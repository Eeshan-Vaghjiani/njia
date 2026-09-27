r"""Live Chromium upload/consent checks; no app imports, secrets, or mocked APIs.

Run: .venv\Scripts\python.exe scripts/upload_browser_test.py
The test and recorder share a persistent two-request remote-AI budget.
"""
import argparse
import json
import time
from io import BytesIO
from pathlib import Path
from urllib.parse import urlsplit
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile

from playwright.sync_api import expect, sync_playwright
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject, NumberObject

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS = ROOT / "artifacts"
BASE_URL = "http://127.0.0.1:8000"
SYNTHETIC = (
    "Synthetic demonstration profile. I use SQL to query sales records and Excel "
    "to build pivot tables and monthly reports. I create dashboards in Power BI. "
    "I want to learn Python and R."
)


def make_pdf(text=SYNTHETIC, image_only=False):
    """Real PDF objects, adapted from tests/test_uploads.py without importing app."""
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
            NameObject("/XObject"): DictionaryObject({NameObject("/Im0"): writer._add_object(image)})})
        content = b"q 100 0 0 100 20 20 cm /Im0 Do Q"
    else:
        font = DictionaryObject({NameObject("/Type"): NameObject("/Font"),
                                 NameObject("/Subtype"): NameObject("/Type1"),
                                 NameObject("/BaseFont"): NameObject("/Helvetica")})
        page[NameObject("/Resources")] = DictionaryObject({
            NameObject("/Font"): DictionaryObject({NameObject("/F1"): writer._add_object(font)})})
        safe = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        content = f"BT /F1 12 Tf 40 750 Td ({safe}) Tj ET".encode("ascii")
    stream = DecodedStreamObject()
    stream.set_data(content)
    page[NameObject("/Contents")] = writer._add_object(stream)
    output = BytesIO()
    writer.write(output)
    return output.getvalue()


def make_docx(text=SYNTHETIC):
    output = BytesIO()
    with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
        archive.writestr("_rels/.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        archive.writestr("word/document.xml", f'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>{escape(text)}</w:t></w:r></w:p></w:body></w:document>')
    return output.getvalue()


def file_payload(extension="pdf", content=None, name=None):
    mime = {"pdf": "application/pdf", "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "txt": "text/plain"}
    if content is None:
        content = {"pdf": make_pdf, "docx": make_docx, "txt": lambda: SYNTHETIC.encode()}[extension]()
    return {"name": name or f"synthetic-profile.{extension}", "mimeType": mime.get(extension, "application/octet-stream"), "buffer": content}


def save_json(name, data):
    ARTIFACTS.mkdir(exist_ok=True)
    (ARTIFACTS / name).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def reserve_ai_call(owner):
    """Conservative, persistent budget: a reserved attempt is never refunded."""
    path = ARTIFACTS / "ai-call-budget.json"
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"limit": 2, "attempts": []}
    assert len(data["attempts"]) < 2, "Two-call AI budget exhausted; no automatic retries allowed."
    data["attempts"].append({"owner": owner, "reserved_unix": time.time()})
    save_json(path.name, data)


class Audit:
    def __init__(self, page):
        self.requests, self.responses, self.errors = [], [], []
        page.on("request", self.request)
        page.on("response", self.response)
        page.on("pageerror", lambda error: self.errors.append(str(error)))

    def request(self, request):
        path = urlsplit(request.url).path
        if path.startswith("/api/"):
            entry = {"path": path, "method": request.method}
            if "application/json" in request.headers.get("content-type", ""):
                entry["json"] = request.post_data_json
            self.requests.append(entry)

    def response(self, response):
        if urlsplit(response.url).path.startswith("/api/"):
            self.responses.append({"path": urlsplit(response.url).path, "status": response.status})

    def count(self, path):
        return sum(r["path"] == path for r in self.requests)


def click_response(page, selector, endpoint, status=200, timeout=15000):
    with page.expect_response(lambda r: urlsplit(r.url).path == endpoint, timeout=timeout) as pending:
        page.locator(selector).click()
    response = pending.value
    data = response.json()
    assert response.status == status, (endpoint, response.status, data)
    return data


def ready(page, base_url=BASE_URL):
    with page.expect_response(lambda r: urlsplit(r.url).path == "/api/meta") as pending:
        page.goto(base_url, wait_until="networkidle")
    meta = pending.value.json()
    expect(page.locator("#upload")).to_be_enabled()
    assert meta["ai"]["provider"] == "groq" and meta["ai"]["configured"] is True
    return meta


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=BASE_URL)
    args = parser.parse_args()
    ARTIFACTS.mkdir(exist_ok=True)
    result = {"status": "running", "base_url": args.base_url, "mocked_requests": 0, "synthetic_only": True, "checks": []}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={"width": 1280, "height": 720}, reduced_motion="reduce")
        page = context.new_page()
        audit = Audit(page)
        try:
            result["provider"] = ready(page, args.base_url)["ai"]
            expect(page.locator("#upload-help")).to_contain_text("4,000,000")
            for extension in ("pdf", "docx", "txt"):
                page.locator("#cv-file").set_input_files(file_payload(extension))
                expect(page.locator("#upload-consent")).not_to_be_checked()
                count = audit.count("/api/upload")
                page.locator("#upload").click()
                expect(page.locator("#upload-status")).to_contain_text("agree")
                assert audit.count("/api/upload") == count
                page.locator("#upload-consent").check()
                extracted_before = audit.count("/api/extract")
                preview = click_response(page, "#upload", "/api/upload")
                assert preview["format"] == extension and preview["text"] == SYNTHETIC
                expect(page.locator("#cv")).to_have_value(SYNTHETIC)
                expect(page.locator("#consent")).not_to_be_checked()
                expect(page.locator("#skill-count")).to_have_text("0")
                assert audit.count("/api/extract") == extracted_before
                page.locator("#extract").click()
                expect(page.locator("#status")).to_contain_text("review")
                assert audit.count("/api/extract") == extracted_before
                reviewed = SYNTHETIC + " Reviewed synthetic summary."
                page.locator("#cv").fill(reviewed)
                page.locator("#consent").check()
                extracted = click_response(page, "#extract", "/api/extract")
                assert set(extracted["skills"]) == {"sql", "excel", "power bi"}, extracted
                assert audit.requests[-1]["json"]["text"] == reviewed
                analysis = click_response(page, "#analyze", "/api/analyze")
                expect(page.locator("#overview")).to_be_visible()
                assert analysis["sample_size"] > 0 and analysis["gaps"]
                result["checks"].append({"format": extension, "preview": preview, "extraction": extracted, "analysis": analysis})
                if extension == "pdf":
                    page.locator(".upload-card").scroll_into_view_if_needed()
                    page.screenshot(path=str(ARTIFACTS / "upload-browser-preview.png"), full_page=True)

            count = audit.count("/api/upload")
            for extension, content, expected in (("rtf", b"{\\rtf1 synthetic}", "Choose a PDF, DOCX or TXT"), ("txt", b"x" * 4000001, "4,000,000")):
                page.locator("#cv-file").set_input_files(file_payload(extension, content))
                page.locator("#upload-consent").check()
                page.locator("#upload").click()
                expect(page.locator("#upload-status")).to_contain_text(expected)
                assert audit.count("/api/upload") == count
                result["checks"].append({"case": "unsupported" if extension == "rtf" else "frontend_max_4MB", "network_blocked": True, "message": page.locator("#upload-status").inner_text()})
                page.screenshot(path=str(ARTIFACTS / f"upload-browser-{'unsupported' if extension == 'rtf' else 'oversize'}.png"))

            page.locator("#cv-file").set_input_files(file_payload("pdf", make_pdf(image_only=True), "synthetic-scan.pdf"))
            page.locator("#upload-consent").check()
            scan = click_response(page, "#upload", "/api/upload", status=422)
            expect(page.locator("#upload-status")).to_contain_text("OCR")
            result["checks"].append({"case": "image_only_scan", "status": 422, "response": scan})
            page.screenshot(path=str(ARTIFACTS / "upload-browser-scan-failure.png"))

            # Also check the real API's consent gate and unsupported-format response.
            for consent, filename, expected_status in (("false", "synthetic.txt", 422), ("true", "synthetic.rtf", 415)):
                response = context.request.post(args.base_url + "/api/upload", multipart={"consent": consent, "file": {"name": filename, "mimeType": "text/plain", "buffer": b"SQL synthetic experience"}})
                assert response.status == expected_status, response.text()
                result["checks"].append({"case": "direct_api_upload", "consent": consent, "filename": filename, "status": response.status, "response": response.json()})

            page.locator('[data-tab="plan"]').click()
            expect(page.locator("#ai-consent")).not_to_be_checked()
            curated = click_response(page, "#generate-plan", "/api/plan")
            assert curated["mode"] == "curated" and curated["model"] is None
            assert audit.requests[-1]["json"]["use_ai"] is False
            assert audit.requests[-1]["json"]["ai_consent"] is False
            expect(page.locator("#plan .tiny-badge")).to_have_text("Curated plan")
            result["curated_plan"] = curated
            page.locator("#new-plan").click()
            expect(page.locator("#ai-consent")).not_to_be_checked()
            page.locator("#ai-consent").check()
            reserve_ai_call("upload_browser_test")
            started = time.monotonic()
            ai = click_response(page, "#generate-plan", "/api/plan", timeout=55000)
            result["ai_elapsed_seconds"] = round(time.monotonic() - started, 3)
            result["ai_plan"] = ai
            assert ai["mode"] == "groq", ai["note"]
            assert ai["model"] and len(ai["weeks"]) == 4
            expect(page.locator("#plan .tiny-badge")).to_have_text("AI coaching · Groq")
            plan_request = [r for r in audit.requests if r["path"] == "/api/plan"][-1]["json"]
            assert plan_request["ai_consent"] is True and plan_request["use_ai"] is True
            assert set(plan_request) == {"country", "role", "skills", "hours", "use_ai", "ai_consent"}
            page.locator("#plan").scroll_into_view_if_needed()
            page.screenshot(path=str(ARTIFACTS / "upload-browser-ai.png"), full_page=True)
            assert not audit.errors, audit.errors
            result["status"] = "passed"
        except Exception as error:
            result["status"], result["error"] = "failed", str(error)
            page.screenshot(path=str(ARTIFACTS / "upload-browser-failure.png"), full_page=True)
            raise
        finally:
            result.update(requests=audit.requests, responses=audit.responses, javascript_errors=audit.errors)
            save_json("upload-browser-results.json", result)
            browser.close()
    print(json.dumps({"status": result["status"], "checks": len(result["checks"]), "ai_mode": result["ai_plan"]["mode"], "ai_elapsed_seconds": result["ai_elapsed_seconds"]}, indent=2))


if __name__ == "__main__":
    main()
