"""Bounded, in-memory CV uploads. No file storage or skill extraction here."""

from io import BytesIO
import logging
import re
import unicodedata
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from pypdf import PdfReader, apply_configuration
from python_multipart import MultipartParser
from python_multipart.exceptions import MultipartParseError
from python_multipart.multipart import parse_options_header
from starlette.concurrency import run_in_threadpool


MAX_FILE_BYTES = 5 * 1024 * 1024
MAX_TEXT_CHARACTERS = 15000
MAX_REQUEST_BYTES = MAX_FILE_BYTES + 64 * 1024
MAX_ZIP_BYTES = 20 * 1024 * 1024
MAX_XML_BYTES = 2 * 1024 * 1024
WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
CONTENT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
DOCX_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"
NOTE = (
    "Processed in memory on the server; this endpoint does not store or log your file or CV text "
    "or send it to an AI model. This preview is not anonymized and may contain personal information. "
    "Review and edit it before submitting to /api/extract for skill extraction. "
    "Formatting and some document content may be missing; scanned images require OCR."
)

# pypdf diagnostics can contain document fragments. Keep that library's logs
# out of application handlers (including in a deployed server).
_pdf_logger = logging.getLogger("pypdf")
_pdf_logger.addHandler(logging.NullHandler())
_pdf_logger.propagate = False

router = APIRouter()


class UploadPreview(BaseModel):
    text: str
    filename: str
    characters: int
    format: str
    note: str


def fail(status, message):
    raise HTTPException(status, message)


def check_text_size(length):
    if length > MAX_TEXT_CHARACTERS:
        fail(422, "The extracted text exceeds 15,000 characters. Shorten the CV or upload only relevant sections; no truncated preview was returned.")


def display_filename(raw):
    # A display label only, never a filesystem path. Ignore the supplied MIME type.
    name = raw.decode("utf-8", errors="replace").replace("\\", "/").rsplit("/", 1)[-1]
    name = "".join(c for c in name if not unicodedata.category(c).startswith("C")).strip()
    if not name or len(name) > 255:
        fail(422, "Give the file a name of 1–255 characters ending in .pdf, .docx or .txt.")
    return name


class MemoryMultipart:
    """Use streaming callbacks rather than UploadFile's disk-backed spool."""

    def __init__(self):
        self.file = bytearray()
        self.consent = bytearray()
        self.filename = None
        self.seen = set()
        self.complete = False
        self.kind = None

    def on_part_begin(self):
        self.headers = {}
        self.header_name = bytearray()
        self.header_value = bytearray()
        self.header_bytes = 0
        self.kind = None

    def add_header(self, target, data, start, end):
        self.header_bytes += end - start
        if self.header_bytes > 8192:
            fail(400, "Multipart headers are too large. Upload one file and one consent field.")
        target.extend(data[start:end])

    def on_header_field(self, data, start, end):
        self.add_header(self.header_name, data, start, end)

    def on_header_value(self, data, start, end):
        self.add_header(self.header_value, data, start, end)

    def on_header_end(self):
        name = bytes(self.header_name).lower()
        if name in self.headers:
            fail(400, "Duplicate multipart header. Send a fresh upload.")
        self.headers[name] = bytes(self.header_value)
        self.header_name.clear()
        self.header_value.clear()

    def on_headers_finished(self):
        disposition, options = parse_options_header(self.headers.get(b"content-disposition", b""))
        name = options.get(b"name")
        if disposition != b"form-data" or name not in (b"file", b"consent") or name in self.seen:
            fail(422, "Send exactly one file field and one consent boolean field.")
        self.seen.add(name)
        self.kind = name
        if name == b"file":
            self.filename = display_filename(options.get(b"filename", b""))
        elif b"filename" in options:
            fail(422, "Send consent as a boolean form field, not a file.")
        if b"content-transfer-encoding" in self.headers:
            fail(400, "Encoded multipart parts are unsupported. Send the original file bytes.")

    def on_part_data(self, data, start, end):
        target = self.file if self.kind == b"file" else self.consent
        limit = MAX_FILE_BYTES if self.kind == b"file" else 5
        if len(target) + end - start > limit:
            if self.kind == b"file":
                fail(413, "File exceeds 5 MB (5,242,880 bytes). Compress or shorten the CV and upload again.")
            fail(422, "Consent must be a boolean: true or false.")
        target.extend(data[start:end])

    def on_end(self):
        self.complete = True

    def callbacks(self):
        return {name: getattr(self, name) for name in (
            "on_part_begin", "on_header_field", "on_header_value", "on_header_end",
            "on_headers_finished", "on_part_data", "on_end",
        )}


async def read_upload(request):
    media, options = parse_options_header(request.headers.get("content-type", ""))
    boundary = options.get(b"boundary", b"")
    if media != b"multipart/form-data" or not boundary or len(boundary) > 200:
        fail(400, "Use multipart/form-data with a boundary, a file field and a consent boolean field.")
    length = request.headers.get("content-length")
    if length is not None:
        if not length.isascii() or not length.isdecimal():
            fail(400, "Invalid Content-Length header. Send a fresh upload.")
        normalized_length = length.lstrip("0") or "0"
        if len(normalized_length) > 10 or int(normalized_length) > MAX_REQUEST_BYTES:
            fail(413, "Upload request exceeds the 5 MB file limit plus multipart overhead. Shorten the CV.")
    form = MemoryMultipart()
    parser = MultipartParser(boundary, form.callbacks())
    # Parser error messages can include arbitrary submitted bytes.
    parser.logger = logging.Logger("njia.upload.multipart", level=logging.CRITICAL + 1)
    total = 0
    try:
        async for chunk in request.stream():
            total += len(chunk)
            if total > MAX_REQUEST_BYTES:
                fail(413, "Upload request exceeds the 5 MB file limit plus multipart overhead. Shorten the CV.")
            parser.write(chunk)
        parser.finalize()
    except MultipartParseError:
        fail(400, "Malformed multipart upload. Select the file and upload again.")
    if not form.complete:
        fail(400, "Incomplete multipart upload. Select the file and upload again.")
    if form.seen != {b"file", b"consent"}:
        fail(422, "Send exactly one file field and one consent boolean field.")
    consent = bytes(form.consent).lower()
    if consent not in (b"true", b"false"):
        fail(422, "Consent must be a boolean: true or false.")
    if consent != b"true":
        fail(422, "Please consent to in-memory server processing of your CV, or choose skills manually.")
    if not form.file:
        fail(422, "The file is empty. Upload a CV containing readable text.")
    return bytes(form.file), form.filename


class SafeTreeBuilder(ET.TreeBuilder):
    def doctype(self, name, pubid, system):
        fail(422, "DOCX XML contains a prohibited DTD/entity declaration. Re-save as a standard DOCX or UTF-8 TXT.")


def xml_root(data):
    # Parser-level DTD rejection also covers UTF-16 XML (unlike a byte search).
    return ET.fromstring(data, parser=ET.XMLParser(target=SafeTreeBuilder()))


def docx_text(data):
    if not data.startswith(b"PK\x03\x04"):
        fail(422, "This file is not a valid DOCX. Re-save it as DOCX or UTF-8 TXT; renaming an extension is not enough.")
    with ZipFile(BytesIO(data)) as archive:
        entries = archive.infolist()
        names = [entry.filename for entry in entries]
        if len(entries) > 200 or len(set(names)) != len(names):
            fail(422, "DOCX archive has too many or duplicate entries. Re-save a simplified CV.")
        expanded = 0
        for entry in entries:
            expanded += entry.file_size
            if (expanded > MAX_ZIP_BYTES or entry.file_size > MAX_ZIP_BYTES
                    or entry.file_size > max(entry.compress_size, 1) * 100):
                fail(422, "DOCX archive expands too much (possible ZIP bomb). Remove embedded media or export as UTF-8 TXT.")
            if (entry.flag_bits & 1 or entry.compress_type not in (ZIP_STORED, ZIP_DEFLATED)
                    or ".." in entry.filename.replace("\\", "/").split("/")
                    or entry.filename.startswith(("/", "\\"))):
                fail(422, "DOCX archive contains unsafe or encrypted entries. Re-save an unencrypted standard DOCX.")
        if not {"[Content_Types].xml", "_rels/.rels", "word/document.xml"}.issubset(names):
            fail(422, "This ZIP is not a DOCX document. Export your CV as DOCX or UTF-8 TXT.")
        roots = {}
        actual_size = 0
        for entry in entries:
            wanted = entry.filename in ("[Content_Types].xml", "word/document.xml") or bool(
                re.fullmatch(r"word/(?:header\d+|footer\d+|footnotes|endnotes)\.xml", entry.filename)
            )
            buffer = bytearray()
            with archive.open(entry) as source:
                while chunk := source.read(65536):
                    actual_size += len(chunk)
                    if actual_size > MAX_ZIP_BYTES:
                        fail(422, "DOCX archive expands too much. Remove embedded media or export as UTF-8 TXT.")
                    if wanted:
                        if len(buffer) + len(chunk) > MAX_XML_BYTES:
                            fail(422, "DOCX XML is too large. Simplify the document or export as UTF-8 TXT.")
                        buffer.extend(chunk)
            if wanted:
                roots[entry.filename] = xml_root(buffer)
        types = roots.pop("[Content_Types].xml")
        if types.tag != f"{{{CONTENT_NS}}}Types" or not any(
            node.get("PartName") == "/word/document.xml" and node.get("ContentType") == DOCX_TYPE
            for node in types.findall(f"{{{CONTENT_NS}}}Override")
        ):
            fail(422, "Unsupported Word package. Export a standard, macro-free DOCX document.")
        if roots["word/document.xml"].tag != f"{{{WORD_NS}}}document":
            fail(422, "Invalid DOCX document XML. Re-save as a standard DOCX or UTF-8 TXT.")
        pieces = []
        length = 0
        for name in ["word/document.xml", *sorted(n for n in roots if n != "word/document.xml")]:
            for event, node in _xml_events(roots[name]):
                value = ""
                if event == "start" and node.tag == f"{{{WORD_NS}}}t":
                    value = node.text or ""
                elif event == "start" and node.tag in (f"{{{WORD_NS}}}tab", f"{{{WORD_NS}}}br", f"{{{WORD_NS}}}cr"):
                    value = "\t" if node.tag.endswith("tab") else "\n"
                elif event == "end" and node.tag in (f"{{{WORD_NS}}}p", f"{{{WORD_NS}}}tr"):
                    value = "\n"
                length += len(value)
                check_text_size(length)
                pieces.append(value)
        return "".join(pieces)


def _xml_events(root):
    # Iterative traversal avoids Python recursion on attacker-controlled XML.
    stack = [("start", root)]
    while stack:
        event, node = stack.pop()
        yield event, node
        if event == "start":
            stack.append(("end", node))
            stack.extend(("start", child) for child in reversed(node))


def pdf_text(data):
    if not re.match(rb"%PDF-\d\.\d", data) or not data.rstrip().endswith(b"%%EOF"):
        fail(422, "Invalid or incomplete PDF. Re-export a readable PDF or UTF-8 TXT; scanned CVs need OCR first.")
    with apply_configuration(
        maximum_declared_stream_length=8 * 1024 * 1024,
        array_based_stream_maximum_output_length=8 * 1024 * 1024,
        zlib_maximum_output_length=8 * 1024 * 1024,
        lzw_maximum_output_length=8 * 1024 * 1024,
        run_length_maximum_output_length=8 * 1024 * 1024,
        page_tree_maximum_entries=200, page_tree_maximum_depth=20,
        xform_maximum_invocations_per_extraction=200, jbig2dec_binary=None,
    ):
        reader = PdfReader(BytesIO(data), strict=True)
        if reader.is_encrypted:
            fail(422, "Encrypted/password-protected PDFs are unsupported. Export an unencrypted copy and upload again.")
        if len(reader.pages) > 100:
            fail(422, "PDF exceeds 100 pages. Upload only the relevant CV pages.")
        parts = []
        length = 0
        for page in reader.pages:
            visited = 0

            def check_fragment(text, *_):
                nonlocal visited
                visited += len(text)
                check_text_size(length + visited)

            text = page.extract_text(visitor_text=check_fragment)
            length += len(text) + (1 if parts else 0)
            check_text_size(length)
            parts.append(text)
        result = "\n".join(parts)
        if not result.strip():
            fail(422, "PDF contains no extractable text (it may be image-only/scanned). Run OCR first, then upload a searchable PDF or UTF-8 TXT.")
        return result


def preview(data, filename):
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension not in {"pdf", "docx", "txt"}:
        fail(415, "Unsupported format. Upload PDF, DOCX or UTF-8 TXT (not DOC, RTF or an image).")
    try:
        if extension == "pdf":
            text = pdf_text(data)
        elif extension == "docx":
            text = docx_text(data)
        else:
            if data.startswith((b"%PDF-", b"PK\x03\x04", b"{\\rtf")):
                fail(422, "The file content does not match TXT. Export genuine UTF-8 plain text or use the correct PDF/DOCX extension.")
            try:
                text = data.decode("utf-8-sig")
            except UnicodeDecodeError:
                fail(422, "TXT must be UTF-8 encoded. Save it as UTF-8 plain text and upload again.")
            if any(unicodedata.category(c) == "Cc" and c not in "\n\r\t" for c in text):
                fail(422, "TXT contains binary/control data. Export genuine UTF-8 plain text.")
        check_text_size(len(text))
        text = text.strip()
        if not text:
            fail(422, "No readable text was found. Upload a CV containing text; scanned images need OCR first.")
    except HTTPException:
        raise
    except Exception:
        # Never echo or log parser exceptions: they may embed CV content.
        fail(422, f"The {extension.upper()} is corrupt or cannot be safely read. Re-export it or upload UTF-8 TXT. Scanned PDFs need OCR first.")
    return {"text": text, "filename": filename, "characters": len(text), "format": extension, "note": NOTE}


@router.post("/api/upload", response_model=UploadPreview, openapi_extra={
    "requestBody": {"required": True, "content": {"multipart/form-data": {"schema": {
        "type": "object", "required": ["file", "consent"], "properties": {
            "file": {"type": "string", "format": "binary"},
            "consent": {"type": "boolean", "description": "Consent to in-memory server processing; must be true."},
        },
    }}}},
})
async def upload(request: Request):
    data, filename = await read_upload(request)
    return await run_in_threadpool(preview, data, filename)
