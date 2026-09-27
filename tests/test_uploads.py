from io import BytesIO
import logging
import struct
import unittest
from unittest.mock import patch
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

from fastapi.testclient import TestClient
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject, NumberObject

from njia.app import app
from njia import uploads


def make_pdf(text="SQL Python Excel experience", encrypted=False, image_only=False, padding=0):
    """Generate real PDF objects/xref tables without a fixture or extra dependency."""
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    if image_only:
        image = DecodedStreamObject()
        image.set_data(b"\xff\xff\xff")
        image.update({NameObject(k): v for k, v in {
            "/Type": NameObject("/XObject"), "/Subtype": NameObject("/Image"),
            "/Width": NumberObject(1), "/Height": NumberObject(1),
            "/ColorSpace": NameObject("/DeviceRGB"), "/BitsPerComponent": NumberObject(8),
        }.items()})
        page[NameObject("/Resources")] = DictionaryObject({
            NameObject("/XObject"): DictionaryObject({NameObject("/Im0"): writer._add_object(image)}),
        })
        content = b"q 100 0 0 100 20 20 cm /Im0 Do Q"
    else:
        font = DictionaryObject({NameObject("/Type"): NameObject("/Font"),
                                 NameObject("/Subtype"): NameObject("/Type1"),
                                 NameObject("/BaseFont"): NameObject("/Helvetica")})
        page[NameObject("/Resources")] = DictionaryObject({
            NameObject("/Font"): DictionaryObject({NameObject("/F1"): writer._add_object(font)}),
        })
        escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        content = f"BT /F1 12 Tf 40 750 Td ({escaped}) Tj ET".encode("ascii")
    stream = DecodedStreamObject()
    stream.set_data(content)
    page[NameObject("/Contents")] = writer._add_object(stream)
    if padding:
        writer.add_metadata({"/Padding": "x" * padding})
    if encrypted:
        writer.encrypt("secret")
    output = BytesIO()
    writer.write(output)
    return output.getvalue()


def make_docx(text="SQL Python Excel experience", document=None, extras=None, compression=ZIP_DEFLATED):
    if document is None:
        document = (
            f'<w:document xmlns:w="{uploads.WORD_NS}"><w:body>'
            f'<w:p><w:r><w:t>{escape(text)}</w:t></w:r></w:p>'
            '</w:body></w:document>'
        ).encode("utf-8")
    output = BytesIO()
    with ZipFile(output, "w", compression=compression) as archive:
        archive.writestr("[Content_Types].xml", (
            f'<Types xmlns="{uploads.CONTENT_NS}">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            f'<Override PartName="/word/document.xml" ContentType="{uploads.DOCX_TYPE}"/>'
            '</Types>'
        ))
        archive.writestr("_rels/.rels", (
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
            '</Relationships>'
        ))
        archive.writestr("word/document.xml", document)
        for name, value in (extras or {}).items():
            archive.writestr(name, value)
    return output.getvalue()


class UploadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        cls.client.close()

    def upload(self, content, filename="cv.txt", consent="true", mime="application/octet-stream"):
        return self.client.post("/api/upload", files={"file": (filename, content, mime)}, data={"consent": consent})

    def assert_error(self, response, status, hint):
        self.assertEqual(response.status_code, status, response.text)
        self.assertIn(hint.lower(), response.json()["detail"].lower())

    def test_actual_pdf_docx_and_utf8_txt(self):
        text = "SQL Python Excel experience"
        for filename, data in (("cv.pdf", make_pdf(text)), ("cv.docx", make_docx(text)), ("cv.txt", text.encode())):
            with self.subTest(filename=filename):
                response = self.upload(data, filename)
                self.assertEqual(response.status_code, 200, response.text)
                result = response.json()
                self.assertEqual(set(result), {"text", "filename", "characters", "format", "note"})
                self.assertEqual(result["text"], text)
                self.assertEqual(result["characters"], len(text))
                self.assertEqual(result["filename"], filename)
                self.assertEqual(result["format"], filename.split(".")[1])
                self.assertIn("memory on the server", result["note"])
                self.assertIn("not anonymized", result["note"])
                self.assertIn("no-store", response.headers["cache-control"])

    def test_unicode_bom_and_uppercase_extension(self):
        text = "Expérience: SQL, données, Nairobi — résumé"
        result = self.upload(b"\xef\xbb\xbf" + text.encode(), "CV.TXT", mime="application/pdf")
        self.assertEqual(result.status_code, 200, result.text)
        self.assertEqual(result.json()["text"], text)
        self.assertEqual(result.json()["characters"], len(text))
        self.assertEqual(result.json()["format"], "txt")

    def test_preview_keeps_pii_and_does_not_extract_skills(self):
        text = "Name: Amina Diallo\nEmail: amina@example.com\nSQL and Python"
        with patch("njia.engine.extract_skills", side_effect=AssertionError("Unexpected extraction")):
            response = self.upload(text.encode())
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["text"], text)
        self.assertIn("Review and edit", response.json()["note"])

    def test_docx_paragraphs_tables_tabs_and_header(self):
        document = (f'<w:document xmlns:w="{uploads.WORD_NS}"><w:body>'
                    '<w:p><w:r><w:t>Amina</w:t><w:tab/><w:t>SQL</w:t><w:br/><w:t>Python</w:t></w:r></w:p>'
                    '<w:tbl><w:tr><w:tc><w:p><w:r><w:t>Excel</w:t></w:r></w:p></w:tc></w:tr></w:tbl>'
                    '</w:body></w:document>').encode()
        header = f'<w:hdr xmlns:w="{uploads.WORD_NS}"><w:p><w:r><w:t>Contact</w:t></w:r></w:p></w:hdr>'
        response = self.upload(make_docx(document=document, extras={"word/header1.xml": header}), "cv.docx")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["text"], "Amina\tSQL\nPython\nExcel\n\nContact")

    def test_missing_false_and_invalid_consent(self):
        response = self.client.post("/api/upload", files={"file": ("cv.txt", b"SQL experience")})
        self.assert_error(response, 422, "consent")
        self.assert_error(self.upload(b"SQL experience", consent="false"), 422, "server processing")
        for value in ("yes", "1", "", "not-true"):
            with self.subTest(value=value):
                self.assert_error(self.upload(b"SQL experience", consent=value), 422, "boolean")

    def test_no_document_parsing_without_consent(self):
        with patch("njia.uploads.preview", side_effect=AssertionError("Parsed without consent")):
            self.assert_error(self.upload(make_pdf(), "cv.pdf", consent="false"), 422, "consent")

    def test_missing_duplicate_and_unexpected_fields(self):
        cases = [
            [("consent", (None, "true"))],
            [("consent", (None, "true")), ("file", ("cv.txt", b"SQL")), ("file", ("cv.txt", b"SQL"))],
            [("consent", (None, "true")), ("consent", (None, "false")), ("file", ("cv.txt", b"SQL"))],
            [("consent", (None, "true")), ("other", (None, "value")), ("file", ("cv.txt", b"SQL"))],
            [("consent", ("consent.txt", b"true")), ("file", ("cv.txt", b"SQL"))],
        ]
        for parts in cases:
            with self.subTest(parts=parts):
                self.assert_error(self.client.post("/api/upload", files=parts), 422, "consent")

    def test_unsupported_and_mislabelled_files(self):
        for filename in ("cv.doc", "cv.rtf", "cv.png", "cv.zip", "cv"):
            self.assert_error(self.upload(b"SQL experience", filename), 415, "unsupported format")
        for filename, data in (("cv.pdf", b"SQL experience"), ("cv.docx", b"SQL experience"),
                               ("cv.txt", make_pdf()), ("cv.txt", make_docx()), ("cv.txt", b"{\\rtf1 SQL}")):
            self.assert_error(self.upload(data, filename), 422, "UTF-8" if filename == "cv.pdf" else "file")

    def test_txt_invalid_encoding_binary_and_empty(self):
        self.assert_error(self.upload("Résumé".encode("latin1")), 422, "UTF-8")
        self.assert_error(self.upload(b"SQL\x00Python"), 422, "binary")
        for data in (b"", b" \t\r\n ", b"\xef\xbb\xbf"):
            self.assertEqual(self.upload(data).status_code, 422)

    def test_empty_docx(self):
        self.assert_error(self.upload(make_docx(""), "cv.docx"), 422, "no readable text")

    def test_corrupt_encrypted_and_image_only_pdf(self):
        for data in (b"%PDF-1.7\nbroken\n%%EOF", make_pdf()[:-30]):
            self.assert_error(self.upload(data, "cv.pdf"), 422, "re-export")
        self.assert_error(self.upload(make_pdf(encrypted=True), "cv.pdf"), 422, "unencrypted")
        self.assert_error(self.upload(make_pdf(image_only=True), "cv.pdf"), 422, "OCR")

    def test_pdf_page_limit(self):
        writer = PdfWriter()
        for _ in range(101):
            writer.add_blank_page(width=100, height=100)
        output = BytesIO()
        writer.write(output)
        self.assert_error(self.upload(output.getvalue(), "cv.pdf"), 422, "100 pages")

    def test_character_limit_all_formats_without_truncation(self):
        result = self.upload(b"x" * 15000)
        self.assertEqual(result.status_code, 200, result.text)
        self.assertEqual(result.json()["characters"], 15000)
        for filename, data in (("cv.txt", b"x" * 15001), ("cv.pdf", make_pdf("x" * 15001)),
                               ("cv.docx", make_docx("x" * 15001, compression=ZIP_STORED))):
            response = self.upload(data, filename)
            self.assert_error(response, 422, "15,000")
            self.assertNotIn("text", response.json())

    def test_file_size_limit_at_boundary_and_above(self):
        # Exact byte limit passes upload validation and reaches the character check.
        self.assert_error(self.upload(b"x" * uploads.MAX_FILE_BYTES), 422, "15,000")
        self.assert_error(self.upload(b"x" * (uploads.MAX_FILE_BYTES + 1)), 413, "5 MB")

    def test_request_limit_without_content_length(self):
        body = (b'--boundary\r\nContent-Disposition: form-data; name="file"; filename="cv.txt"\r\n\r\n'
                + b"x" * (uploads.MAX_REQUEST_BYTES + 1))
        response = self.client.post("/api/upload", content=(body[i:i + 65536] for i in range(0, len(body), 65536)),
                                    headers={"content-type": "multipart/form-data; boundary=boundary"})
        self.assert_error(response, 413, "5 MB")

    def test_fragmented_upload_file_first_without_content_length(self):
        body = (b'--b\r\nContent-Disposition: form-data; name="file"; filename="cv.txt"\r\n\r\nSQL experience'
                b'\r\n--b\r\nContent-Disposition: form-data; name="consent"\r\n\r\ntrue\r\n--b--\r\n')
        response = self.client.post("/api/upload", content=(body[i:i + 3] for i in range(0, len(body), 3)),
                                    headers={"content-type": "multipart/form-data; boundary=b"})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["text"], "SQL experience")

    def test_request_headers_and_part_header_limits(self):
        for length, status in ((str(uploads.MAX_REQUEST_BYTES + 1), 413), ("-1", 400), ("9" * 5000, 413)):
            response = self.client.post("/api/upload", content=b"", headers={
                "content-type": "multipart/form-data; boundary=b", "content-length": length,
            })
            self.assertEqual(response.status_code, status, response.text)
        body = b'--b\r\nContent-Disposition: form-data; name="' + b"x" * 9000 + b'"\r\n\r\ntrue\r\n--b--\r\n'
        response = self.client.post("/api/upload", content=body, headers={"content-type": "multipart/form-data; boundary=b"})
        self.assertEqual(response.status_code, 400, response.text)

    def test_zip_bomb_and_large_expansion(self):
        self.assert_error(self.upload(make_docx(extras={"word/media/bomb": b"x" * 200000}), "cv.docx"), 422, "ZIP bomb")
        # Many individually permitted entries may still exceed the aggregate limit.
        with patch.object(uploads, "MAX_ZIP_BYTES", 4096):
            self.assert_error(self.upload(make_docx(extras={"one": b"a" * 2500, "two": b"b" * 2500},
                                                    compression=ZIP_STORED), "cv.docx"), 422, "expands too much")

    def test_zip_entry_count_traversal_and_invalid_package(self):
        cases = [(make_docx(extras={str(i): b"" for i in range(201)}), "too many"),
                 (make_docx(extras={"../escape": b"bad"}), "unsafe"),
                 (b"PK\x03\x04broken", "corrupt")]
        plain_zip = BytesIO()
        with ZipFile(plain_zip, "w") as archive:
            archive.writestr("test.txt", "SQL")
        cases.append((plain_zip.getvalue(), "not a DOCX"))
        for data, hint in cases:
            self.assert_error(self.upload(data, "cv.docx"), 422, hint)

    def test_docx_rejects_corrupt_xml_and_entities_including_utf16(self):
        self.assert_error(self.upload(make_docx(document=b"<broken>"), "cv.docx"), 422, "corrupt")
        for encoding in ("utf-8", "utf-16"):
            document = (f'<?xml version="1.0" encoding="{encoding}"?>'
                        '<!DOCTYPE document [<!ENTITY secret "private">]>'
                        f'<w:document xmlns:w="{uploads.WORD_NS}"><w:body>'
                        '<w:p><w:r><w:t>&secret;</w:t></w:r></w:p></w:body></w:document>')
            self.assert_error(self.upload(make_docx(document=document.encode(encoding)), "cv.docx"), 422, "DTD")

    def test_docx_crc_failure(self):
        data = make_docx("UNIQUE_TEXT_SQL", compression=ZIP_STORED).replace(b"UNIQUE_TEXT_SQL", b"BROKEN_TEXT_SQL", 1)
        self.assert_error(self.upload(data, "cv.docx"), 422, "corrupt")

    def test_docx_duplicate_and_encrypted_entries(self):
        output = BytesIO(make_docx())
        with self.assertWarns(UserWarning), ZipFile(output, "a") as archive:
            archive.writestr("word/document.xml", "<duplicate/>")
        self.assert_error(self.upload(output.getvalue(), "cv.docx"), 422, "duplicate")
        data = bytearray(make_docx())
        # Set encryption flags in the real ZIP central directory. No decryption is attempted.
        offset = data.index(b"PK\x01\x02") + 8
        flags = struct.unpack_from("<H", data, offset)[0]
        struct.pack_into("<H", data, offset, flags | 1)
        self.assert_error(self.upload(bytes(data), "cv.docx"), 422, "encrypted")

    def test_docx_xml_size_limit(self):
        with patch.object(uploads, "MAX_XML_BYTES", 1024):
            data = make_docx("x" * 1100, compression=ZIP_STORED)
            self.assert_error(self.upload(data, "cv.docx"), 422, "XML is too large")

    def test_pdf_compressed_stream_limit(self):
        writer = PdfWriter()
        page = writer.add_blank_page(width=100, height=100)
        page[NameObject("/Resources")] = DictionaryObject({NameObject("/Font"): DictionaryObject({
            NameObject("/F1"): DictionaryObject({
                NameObject("/Type"): NameObject("/Font"), NameObject("/Subtype"): NameObject("/Type1"),
                NameObject("/BaseFont"): NameObject("/Helvetica"),
            }),
        })})
        stream = DecodedStreamObject()
        stream.set_data(b" " * (8 * 1024 * 1024 + 1))
        page[NameObject("/Contents")] = writer._add_object(stream.flate_encode())
        output = BytesIO()
        writer.write(output)
        self.assert_error(self.upload(output.getvalue(), "cv.pdf"), 422, "cannot be safely read")

    def test_filename_is_display_only_and_sanitized(self):
        for name in ("../../cv.txt", "C:\\Users\\person\\cv.txt"):
            response = self.upload(b"SQL experience", name)
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(response.json()["filename"], "cv.txt")
        response = self.upload(b"SQL experience", "cv\u202e.txt")
        self.assertEqual(response.json()["filename"], "cv.txt")
        self.assert_error(self.upload(b"SQL", "x" * 256 + ".txt"), 422, "name")

    def test_malformed_incomplete_and_nonmultipart_requests(self):
        self.assert_error(self.client.post("/api/upload", json={"consent": True}), 400, "multipart")
        for body in (b"nonsense", b'--b\r\nContent-Disposition: form-data; name="consent"\r\n\r\ntrue'):
            response = self.client.post("/api/upload", content=body, headers={"content-type": "multipart/form-data; boundary=b"})
            self.assert_error(response, 400, "upload")

    def test_in_memory_above_default_spool_threshold_and_no_cv_logs(self):
        data = make_pdf("PRIVATE_CANARY_SQL", padding=2 * 1024 * 1024)
        with patch("starlette.formparsers.SpooledTemporaryFile", side_effect=AssertionError("Spool used")), \
                patch("tempfile.TemporaryFile", side_effect=AssertionError("Temporary file used")), \
                patch("tempfile.NamedTemporaryFile", side_effect=AssertionError("Named file used")), \
                patch("builtins.open", side_effect=AssertionError("File access used")), \
                self.assertLogs(level=logging.DEBUG) as logs:
            response = self.upload(data, "PRIVATE_CANARY.pdf")
            invalid = self.upload(b"%PDF-1.7\nPRIVATE_CANARY_SQL\n%%EOF", "PRIVATE_CANARY.pdf")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(invalid.status_code, 422)
        self.assertNotIn("PRIVATE_CANARY", "\n".join(logs.output))

    def test_same_origin_and_openapi_contract(self):
        response = self.client.post("/api/upload", files={"file": ("cv.txt", b"SQL")}, data={"consent": "true"},
                                    headers={"origin": "https://elsewhere.example"})
        self.assertEqual(response.status_code, 403)
        schema = self.client.get("/openapi.json").json()["paths"]["/api/upload"]["post"]
        fields = schema["requestBody"]["content"]["multipart/form-data"]["schema"]
        self.assertEqual(fields["required"], ["file", "consent"])
        self.assertEqual(fields["properties"]["consent"]["type"], "boolean")


if __name__ == "__main__":
    unittest.main()
