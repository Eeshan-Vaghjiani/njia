"""Real Chromium checks. Start the local server on port 8000 first."""
import json
from pathlib import Path

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS = ROOT / "artifacts"


def main():
    ARTIFACTS.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={"width": 1440, "height": 1100}, reduced_motion="reduce")
        page = context.new_page()
        errors, external = [], []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("request", lambda req: external.append(req.url) if not req.url.startswith(("http://127.0.0.1:8000", "data:")) else None)
        page.goto("http://127.0.0.1:8000", wait_until="networkidle")
        expect(page.locator("#analyze")).to_be_enabled()
        page.screenshot(path=str(ARTIFACTS / "desktop-welcome.png"), full_page=True)
        page.locator("#extract").click()
        expect(page.locator("#status")).to_contain_text("agree")
        page.locator("#sample").click()
        page.locator("#extract").click()
        expect(page.locator("#skill-count")).to_have_text("3")
        page.locator("#analyze").click()
        expect(page.locator("#overview")).to_be_visible()
        expect(page.locator(".score-copy")).to_contain_text("3 of the top")
        expect(page.locator(".job-card")).to_have_count(3)
        page.screenshot(path=str(ARTIFACTS / "desktop-analysis.png"), full_page=True)
        page.get_by_role("button", name="Build my learning path").click()
        page.locator("#hours").select_option("3")
        page.locator("#generate-plan").click()
        expect(page.locator(".week-card")).to_have_count(4, timeout=55000)
        page.locator('[data-week="1"]').check()
        expect(page.locator("#progress")).to_have_text("1")
        page.get_by_role("button", name="Try a practice check").click()
        page.locator("#practice-skill").select_option("sql")
        page.locator("#start-practice").click()
        expect(page.locator("#practice-form")).to_be_visible()
        for i, answer in enumerate([1, 2, 0]):
            page.locator(f'input[name="q{i}"][value="{answer}"]').check()
        page.locator('[data-tab="plan"]').click()
        page.locator('[data-tab="practice"]').click()
        for i, answer in enumerate([1, 2, 0]):
            expect(page.locator(f'input[name="q{i}"][value="{answer}"]')).to_be_checked()
        page.locator("#reflection").fill("I would check duplicates and NULL values before trusting a sales total.")
        page.get_by_role("button", name="Check my answers").click()
        expect(page.locator("#practice")).to_contain_text("SQL · 3/3 correct")
        with page.expect_download() as info:
            page.get_by_role("button", name="Download my evidence report").click()
        download = info.value
        download.save_as(str(ARTIFACTS / download.suggested_filename))
        report = (ARTIFACTS / download.suggested_filename).read_text(encoding="utf-8")
        assert "3/3 correct" in report and "Four-week learning plan" in report
        assert "aspiring data analyst in Nairobi" not in report
        # Country changes invalidate the prior plan and practice evidence.
        page.locator("#country").select_option("Côte d'Ivoire")
        expect(page.locator("#welcome")).to_be_visible()
        page.locator("#analyze").click()
        expect(page.locator(".fallback-note")).to_contain_text("10-country")
        page.locator("#reset").click()
        expect(page.locator("#skill-count")).to_have_text("0")
        expect(page.locator("#cv")).to_have_value("")
        # Manual skills and removal; empty profiles also produce a valid path.
        page.locator("#skill-select").select_option("python")
        page.locator("#add-skill").click()
        expect(page.locator("#skill-count")).to_have_text("1")
        page.get_by_role("button", name="Remove Python", exact=True).click()
        page.locator("#analyze").click()
        expect(page.locator(".score-ring strong")).to_have_text("0%")
        # No raw CV browser persistence.
        assert page.evaluate("Object.keys(localStorage).length + Object.keys(sessionStorage).length") == 0
        page.locator("#about-button").click()
        expect(page.locator("#about")).to_be_visible()
        page.keyboard.press("Escape")
        expect(page.locator("#about")).not_to_be_visible()
        # Phone-sized viewport: run primary flow and check overflow.
        page.set_viewport_size({"width": 390, "height": 844})
        page.locator("#sample").click()
        page.locator("#extract").click()
        expect(page.locator("#skill-count")).to_have_text("3")
        page.locator("#analyze").click()
        expect(page.locator("#overview")).to_be_visible()
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), "Mobile horizontal overflow"
        page.screenshot(path=str(ARTIFACTS / "mobile-analysis.png"), full_page=True)
        # A new page does not inherit a previous visitor's data.
        clean = context.new_page()
        clean.goto("http://127.0.0.1:8000", wait_until="networkidle")
        expect(clean.locator("#skill-count")).to_have_text("0")
        expect(clean.locator("#cv")).to_have_value("")
        assert not errors, errors
        assert not external, external
        result = {"status": "passed", "browser": "Chromium", "desktop": "1440x1100", "mobile": "390x844", "javascript_errors": errors, "external_page_requests": external, "flows": ["consent", "sample extraction", "local analysis", "job retrieval", "four-week plan", "progress", "assessment grading", "report download", "small-sample fallback", "stale-result clearing", "manual skills", "empty profile", "reset", "privacy dialog", "mobile layout", "session isolation"]}
        (ARTIFACTS / "browser-results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(json.dumps(result, indent=2))
        browser.close()


if __name__ == "__main__":
    main()
