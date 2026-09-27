"""Current mobile CV upload flow; no model request is needed."""
import json
import os
import re
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parent.parent
BASE = os.getenv("NJIA_TEST_URL", "http://127.0.0.1:8000").rstrip("/")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(BASE, wait_until="networkidle")
        page.locator("#cv-file").set_input_files({"name": "synthetic-mobile-cv.txt", "mimeType": "text/plain", "buffer": b"I use SQL, Excel and Power BI to analyze sales records and build dashboards."})
        page.locator("#upload-consent").check()
        page.locator("#upload").click()
        expect(page.locator("#cv")).to_have_value(re.compile("SQL"))
        page.locator("#consent").check()
        page.locator("#extract").click()
        expect(page.locator("#skill-count")).to_have_text("3")
        page.locator("#analyze").click()
        expect(page.locator(".score-ring strong")).to_have_text("39.6%")
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        page.locator('[data-tab="plan"]').click()
        page.locator("#generate-plan").click()
        expect(page.locator(".week-card")).to_have_count(4)
        expect(page.locator("#plan .tiny-badge")).to_have_text("Curated plan")
        with page.expect_download() as result:
            page.locator("#plan [data-download]").click()
        assert result.value.suggested_filename == "njia-skill-evidence.md"
        assert not errors, errors
        artifacts = ROOT / "artifacts"
        artifacts.mkdir(exist_ok=True)
        page.screenshot(path=str(artifacts / "mobile-upload-plan.png"), full_page=True)
        report = {"status": "passed", "viewport": "390x844", "touch": True, "flow": "TXT file upload, preview, consent, extraction, Kenya gap, curated plan, download", "model_calls": 0, "javascript_errors": errors}
        (artifacts / "mobile-upload-results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps(report, indent=2))
        browser.close()


if __name__ == "__main__":
    main()
