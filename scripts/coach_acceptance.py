"""Public coach acceptance, synthetic inputs, two real advice calls; no mocks."""
import html
import argparse
import json
import time
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import expect, sync_playwright
from upload_browser_test import make_pdf, file_payload, Audit

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS = ROOT / "artifacts"
BASE = "https://gomycode-2026.vercel.app"
PDF_TEXT = (
    "SYNTHETIC CV - fictional Nairobi candidate. Junior Data Analyst. "
    "Operations Assistant at a fictional retail cooperative, 2024-2025. "
    "Used Excel pivot tables to summarise weekly sales across three branches. "
    "Checked stock records against sales spreadsheets and flagged duplicate entries. "
    "Prepared a monthly sales summary for the operations team. "
    "Built a Power BI dashboard with a synthetic retail dataset. "
    "Used SQL SELECT, JOIN and GROUP BY in a personal sales analysis project. "
    "Documented cleaning steps and checked totals against the source spreadsheet. "
    "Seeking a junior Data Analyst role in Kenya. I want to learn Python; "
    "I have not used Python in a project yet."
)


def save(name, data):
    (ARTIFACTS / name).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def reserve(owner):
    path = ARTIFACTS / "coach-call-budget.json"
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"limit": 3, "attempts": []}
    assert len(data["attempts"]) < 3, "Three live advice attempts already reserved."
    data["attempts"].append({"owner": owner, "unix": time.time(), "url": BASE + "/api/advise"})
    save(path.name, data)


def home(page):
    with page.expect_response(lambda r: urlsplit(r.url).path == "/api/meta") as pending:
        response = page.goto(BASE, wait_until="networkidle")
    assert response.status == 200
    assert pending.value.status == 200
    expect(page.locator("#sample")).to_be_visible()
    return pending.value.json()


def click_api(page, selector, endpoint, timeout=90000):
    started = time.monotonic()
    with page.expect_response(lambda r: urlsplit(r.url).path == endpoint, timeout=timeout) as pending:
        page.locator(selector).click()
    response = pending.value
    data = response.json()
    elapsed = round(time.monotonic() - started, 3)
    assert response.status == 200, (endpoint, response.status, data)
    return data, elapsed


def download(page, name):
    with page.expect_download() as pending:
        page.locator("#download-report").click()
    assert pending.value.suggested_filename == "njia-career-brief.html"
    path = ARTIFACTS / name
    pending.value.save_as(str(path))
    return path.read_text(encoding="utf-8")


def export_content_checks(text, model):
    decoded = html.unescape(text)
    return {x: x in decoded for x in (model, "Seven-day action checklist", "Interview practice", "Method & limitations")}


def verify_saved_downloads():
    """Recheck saved real downloads after assertion correction; zero API calls."""
    path = ARTIFACTS / "coach-acceptance-results.json"
    result = json.loads(path.read_text(encoding="utf-8"))
    result["assertion_correction"] = "Decode HTML entities before checking headings; original assertion incorrectly required &amp; for a literal ampersand. Rechecked original downloads without network calls."
    for label in ("desktop", "mobile"):
        text = (ARTIFACTS / f"coach-{label}-default.html").read_text(encoding="utf-8")
        evidence = export_content_checks(text, result["flows"][label]["response"]["advisor"]["model"])
        check = next(c for c in result["checks"] if c["name"] == label + "_download_has_plan_model_and_limits")
        check.update(passed=all(evidence.values()), evidence=evidence)
    result["passed"] = sum(c["passed"] for c in result["checks"])
    result["failed"] = sum(not c["passed"] for c in result["checks"])
    result["status"] = "passed" if not result["failed"] else "failed"
    save(path.name, result)
    print(json.dumps({k: result[k] for k in ("status", "passed", "failed")}, indent=2))
    return bool(result["failed"])


def main():
    result = {"status": "running", "base_url": BASE, "synthetic_only": True,
              "mocked_responses": 0, "checks": [], "flows": {}, "started_unix": time.time()}

    def check(name, condition, evidence=None):
        result["checks"].append({"name": name, "passed": bool(condition), "evidence": evidence})
        save("coach-acceptance-results.json", result)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for label, viewport in (("desktop", {"width": 1440, "height": 1000}),
                                ("mobile", {"width": 390, "height": 844})):
            context = browser.new_context(viewport=viewport, is_mobile=label == "mobile",
                                          has_touch=label == "mobile", reduced_motion="reduce")
            page = context.new_page()
            page.set_default_timeout(15000)
            audit = Audit(page)
            flow = result["flows"][label] = {}
            try:
                meta = home(page)
                flow["meta_ai"] = meta.get("ai")
                check(label + "_live_coach_loaded", page.locator("#build-brief").is_visible())
                if label == "desktop":
                    payload = file_payload("pdf", make_pdf(PDF_TEXT), "synthetic-coach-cv.pdf")
                    (ARTIFACTS / "coach-synthetic-cv.pdf").write_bytes(payload["buffer"])
                    page.locator("#cv-file").set_input_files(payload)
                    page.locator("#consent").check()
                    preview, elapsed = click_api(page, "#preview-upload", "/api/upload")
                    flow["pdf_preview"] = preview
                    expect(page.locator("#cv-text")).to_have_value(PDF_TEXT)
                    check("desktop_real_pdf_preview", preview["text"] == PDF_TEXT and preview["format"] == "pdf",
                          {"bytes": len(payload["buffer"]), "elapsed_seconds": elapsed})
                    check("desktop_preview_requires_new_ai_consent", not page.locator("#consent").is_checked()
                          and audit.count("/api/advise") == 0)
                page.locator("#sample").click()
                sample = page.locator("#cv-text").input_value()
                check(label + "_sample_and_consent_reset", "SYNTHETIC SAMPLE" in sample
                      and not page.locator("#consent").is_checked())
                page.locator("#build-brief").click()
                expect(page.locator("#error-message")).to_contain_text("consent")
                check(label + "_consent_blocks_network", audit.count("/api/advise") == 0 and audit.count("/api/questions") == 0)
                page.locator("#consent").check()
                questions, _ = click_api(page, "#build-brief", "/api/questions")
                expect(page.locator("#followup-panel")).to_be_visible()
                check(label + "_followup_questions_shown", 2 <= len(questions["questions"]) <= 5
                      and audit.count("/api/advise") == 0, {"mode": questions.get("mode"), "model": questions.get("model")})
                reserve("acceptance_" + label)
                data, elapsed = click_api(page, "#followup-skip", "/api/advise")
                flow.update(response=data, elapsed_seconds=elapsed)
                expect(page.locator("#results")).to_be_visible()
                a, m = data["advisor"], data["market"]
                check(label + "_advisor_and_market", isinstance(a, dict) and isinstance(m, dict))
                expect(page.locator("#ai-provenance")).to_contain_text(a["model"] or "none")
                check(label + "_actual_groq_provenance", a.get("mode") == "groq"
                      and "groq" in page.locator("#ai-provenance").inner_text().lower(),
                      {"mode": a.get("mode"), "model": a.get("model"), "elapsed_seconds": elapsed})
                check(label + "_summary_matches_response", page.locator("#advisor-summary").inner_text() == a["summary"])
                check(label + "_strengths_match_response", page.locator("#strengths details").count() == len(a["strengths"]),
                      {"actual_count": len(a["strengths"])})
                if a["strengths"]:
                    page.locator("#strengths summary").first.click()
                    expect(page.locator("#strengths blockquote").first).to_have_text(a["strengths"][0]["evidence"])
                rewrites = a["cv_improvements"]
                check(label + "_rewrites_or_honest_empty", page.locator("#cv-improvements .rewrite-card").count() == len(rewrites)
                      and (bool(rewrites) or "No grounded rewrite was returned" in page.locator("#cv-improvements").inner_text()),
                      {"actual_count": len(rewrites)})
                check(label + "_seven_real_days", len(a["seven_day_plan"]) == 7
                      and page.locator("#seven-day-plan input").count() == 7
                      and sorted(d["day"] for d in a["seven_day_plan"]) == list(range(1, 8)))
                page.locator('[data-day="0"]').check()
                check(label + "_day_completion", "completed" in page.locator("#seven-day-plan li").first.get_attribute("class"))
                page.locator("#interview-guidance summary").click()
                check(label + "_interview_matches_response", page.locator("#interview-question").inner_text() == a["interview"]["question"]
                      and page.locator("#interview-rubric").inner_text() == a["interview"]["what_good_looks_like"])
                check(label + "_market_391_historical", m.get("sample_size") == 391
                      and "391 historical postings" in page.locator("#market-source").inner_text(),
                      {k: m.get(k) for k in ("sample_size", "coverage", "scope", "local_postings", "fallback")})
                check(label + "_coverage_is_actual_response", f'{m["coverage"]}%' in page.locator("#coverage").inner_text(),
                      {"coverage": m["coverage"]})
                check(label + "_three_priorities", page.locator("#priority-cards .priority-card").count() == 3)
                check(label + "_skill_suggestions_match", page.locator("#skill-chips button").count() == len(a["suggested_skills"]), a["suggested_skills"])
                before_summary = page.locator("#advisor-summary").inner_text()
                market, _ = click_api(page, "#confirm-skills", "/api/analyze")
                flow["confirmed_market"] = market
                expect(page.locator("#skill-status")).to_contain_text("Skills confirmed")
                check(label + "_skill_review_no_new_ai", audit.count("/api/advise") == 1
                      and page.locator("#advisor-summary").inner_text() == before_summary
                      and "confirmed skills" in page.locator("#coverage").inner_text())
                check(label + "_excerpts_default_off", not page.locator("#include-excerpts").is_checked())
                default = download(page, f"coach-{label}-default.html")
                check(label + "_default_html_excludes_excerpt_sections", "<!doctype html>" in default
                      and "<h2>CV evidence</h2>" not in default and "<h2>CV rewrites" not in default
                      and "excluded by your download preference" in default and html.escape(sample, quote=True) not in default)
                page.locator("#include-excerpts").check()
                included = download(page, f"coach-{label}-with-excerpts.html")
                check(label + "_optin_html_includes_actual_excerpts", "<h2>CV rewrites" in included
                      and all(html.escape(s["evidence"], quote=False) in included for s in a["strengths"])
                      and all(html.escape(s["before"], quote=False) in included and html.escape(s["after"], quote=False) in included for s in rewrites))
                content = export_content_checks(default, a["model"])
                check(label + "_download_has_plan_model_and_limits", all(content.values()), content)
                check(label + "_no_horizontal_overflow", page.evaluate("document.documentElement.scrollWidth <= innerWidth"), viewport)
                page.locator("#results").evaluate("el => el.scrollIntoView({block:'start'})")
                page.screenshot(path=str(ARTIFACTS / f"coach-{label}.png"), full_page=True)
            except Exception as error:
                check(label + "_flow_exception", False, f"{type(error).__name__}: {error}")
                page.screenshot(path=str(ARTIFACTS / f"coach-{label}-failure.png"), full_page=True)
            finally:
                flow.update(requests=audit.requests, responses=audit.responses, javascript_errors=audit.errors)
                check(label + "_no_javascript_errors", not audit.errors, audit.errors)
                check(label + "_observed_api_success", all(200 <= r["status"] < 400 for r in audit.responses), audit.responses)
                context.close()
        browser.close()
    result["passed"] = sum(c["passed"] for c in result["checks"])
    result["failed"] = sum(not c["passed"] for c in result["checks"])
    result["status"] = "passed" if not result["failed"] else "failed"
    save("coach-acceptance-results.json", result)
    print(json.dumps({k: result[k] for k in ("status", "passed", "failed")}, indent=2))
    print(json.dumps([c for c in result["checks"] if not c["passed"]], indent=2))
    return bool(result["failed"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-saved-downloads", action="store_true")
    parser.add_argument("--base-url", default=BASE, help="Run against another origin, e.g. http://127.0.0.1:8000")
    args = parser.parse_args()
    BASE = args.base_url.rstrip("/")
    raise SystemExit(verify_saved_downloads() if args.verify_saved_downloads else main())
