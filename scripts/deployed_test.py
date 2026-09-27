"""Anonymous public Chromium verification; NJIA_TEST_URL overrides the HTTPS URL.

Run with .venv\\Scripts\\python.exe -B scripts/deployed_test.py.
Only synthetic inputs are used. The results file reserves the single remote-AI
attempt before transmission, so rerunning this script cannot silently retry it.
No application imports, dotenv loading, credentials, or authenticated storage.
"""
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import expect, sync_playwright

# Existing standalone helpers adapted from tests/test_uploads.py; no app import.
from upload_browser_test import SYNTHETIC, file_payload

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS = ROOT / "artifacts"
RESULTS = ARTIFACTS / "deployed-results.json"
BASE = os.environ.get("NJIA_TEST_URL", "https://gomycode-2026.vercel.app").rstrip("/")
EXPECTED_MODEL = "openai/gpt-oss-20b"


def utc():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def main():
    assert urlsplit(BASE).scheme == "https", "NJIA_TEST_URL must use public HTTPS"
    assert ARTIFACTS.is_dir(), "Expected existing artifacts directory"
    prior = json.loads(RESULTS.read_text(encoding="utf-8")) if RESULTS.exists() else {}
    reservations = prior.get("remote_ai_reservations", [])
    result = {
        "status": "running", "started_utc": utc(), "base_url": BASE,
        "browser": "Chromium", "anonymous_fresh_contexts": True,
        "synthetic_only": True, "mocked_responses": 0,
        "remote_ai_limit": 1, "remote_ai_reservations": reservations,
        "remote_ai_requests_this_run": 0, "checks": [], "failures": [],
        "requests": [], "responses": [], "javascript_errors": [],
        "console_errors": [], "request_failures": [], "screenshots": [],
        "verification_limits": [
            "Groq execution is evidenced by the public API mode/model and rendered UI; no provider logs or secrets accessed.",
            "One remote plan attempt maximum, including reruns retaining this results file; no retries.",
            "Chromium desktop 1440x1100 and mobile touch 390x844; synthetic PDF/TXT only.",
            "Historical dataset coverage is not proficiency or hiring probability.",
        ],
    }

    def save():
        RESULTS.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    def check(name, condition, evidence=None):
        entry = {"name": name, "status": "passed" if condition else "failed", "utc": utc()}
        if evidence is not None:
            entry["evidence"] = evidence
        result["checks"].append(entry)
        if not condition:
            result["failures"].append(entry)
        return condition

    def phase(name, fn, page=None):
        try:
            fn()
        except Exception as error:
            check(name, False, f"{type(error).__name__}: {error}")
            if page is not None:
                screenshot(page, f"public-{name}-failure.png")
        save()

    def screenshot(page, name):
        try:
            page.screenshot(path=str(ARTIFACTS / name), full_page=True)
            result["screenshots"].append({"path": f"artifacts/{name}", "utc": utc()})
        except Exception as error:
            check("screenshot", False, str(error))

    def attach(context, label):
        def request(req):
            if not req.url.startswith(("http:", "https:")):
                return
            entry = {"context": label, "utc": utc(), "method": req.method,
                     "url": req.url, "origin": req.headers.get("origin")}
            if "application/json" in req.headers.get("content-type", ""):
                entry["json"] = req.post_data_json
            result["requests"].append(entry)

        def response(res):
            result["responses"].append({"context": label, "utc": utc(),
                                        "method": res.request.method, "url": res.url,
                                        "status": res.status})

        def guard(route):
            req = route.request
            if req.method == "POST" and urlsplit(req.url).path == "/api/plan":
                body = req.post_data_json
                if body.get("use_ai") or body.get("ai_consent"):
                    if reservations:
                        check("remote_ai_budget", False, "Additional remote plan request blocked before transmission")
                        route.abort()
                        return
                    reservations.append({"utc": utc(), "base_url": BASE, "state": "reserved_before_send"})
                    result["remote_ai_requests_this_run"] += 1
                    save()
            route.continue_()

        context.route("**/api/plan", guard)
        context.on("request", request)
        context.on("response", response)
        context.on("requestfailed", lambda req: result["request_failures"].append(
            {"context": label, "utc": utc(), "url": req.url, "error": req.failure}))
        page = context.new_page()
        page.on("pageerror", lambda err: result["javascript_errors"].append(
            {"context": label, "utc": utc(), "error": str(err)}))
        page.on("console", lambda msg: result["console_errors"].append(
            {"context": label, "utc": utc(), "error": msg.text}) if msg.type == "error" else None)
        page.set_default_timeout(20000)
        return page

    def click_api(page, selector, endpoint, timeout=30000):
        with page.expect_response(lambda r: urlsplit(r.url).path == endpoint, timeout=timeout) as pending:
            page.locator(selector).click()
        response = pending.value
        assert response.status == 200, f"{endpoint}: HTTP {response.status}: {response.text()[:600]}"
        return response.json()

    def count(endpoint):
        return sum(urlsplit(r["url"]).path == endpoint for r in result["requests"])

    def last_body(endpoint):
        return [r["json"] for r in result["requests"] if urlsplit(r["url"]).path == endpoint][-1]

    def home(page, label):
        with page.expect_response(lambda r: urlsplit(r.url).path == "/api/meta") as pending:
            response = page.goto(BASE, wait_until="networkidle")
        meta_response = pending.value
        meta = meta_response.json()
        expect(page.locator("#upload")).to_be_enabled()
        check(f"{label}_homepage_meta", response.status == 200 and meta_response.status == 200, {
            "homepage_status": response.status, "meta_status": meta_response.status,
            "title": page.title(), "ai": meta.get("ai"), "postings": meta.get("postings"),
            "countries": len(meta.get("countries", [])),
        })
        check(f"{label}_provider", meta["ai"].get("provider") == "groq"
              and meta["ai"].get("configured") is True
              and meta["ai"].get("model") == EXPECTED_MODEL, meta["ai"])
        expect(page).to_have_title("Njia — Your skills. Your next step.")
        expect(page.locator('meta[name="description"]')).to_have_attribute("content", "Find your next career step with job-market evidence. No CV storage. CV never sent to AI.")
        expect(page.locator('meta[name="viewport"]')).to_have_attribute("content", "width=device-width,initial-scale=1")
        expect(page.locator("#cv")).to_have_value("")
        expect(page.locator("#skill-count")).to_have_text("0")
        expect(page.locator("#country")).to_have_value("Kenya")
        expect(page.locator("#role")).to_have_value("Data Analyst")
        check(f"{label}_fresh_session", page.evaluate("localStorage.length + sessionStorage.length") == 0)

    def upload_gap(page, extension, label):
        payload = file_payload(extension)
        page.locator("#cv-file").set_input_files(payload)
        expect(page.locator("#upload-consent")).not_to_be_checked()
        before = count("/api/upload")
        page.locator("#upload").click()
        expect(page.locator("#upload-status")).to_contain_text("agree")
        check(f"{label}_upload_consent_gate", count("/api/upload") == before)
        page.locator("#upload-consent").check()
        extract_before = count("/api/extract")
        preview = click_api(page, "#upload", "/api/upload")
        expect(page.locator("#cv")).to_have_value(SYNTHETIC)
        expect(page.locator("#consent")).not_to_be_checked()
        expect(page.locator("#skill-count")).to_have_text("0")
        check(f"{label}_actual_{extension}_upload", preview["text"] == SYNTHETIC
              and preview["format"] == extension and count("/api/extract") == extract_before,
              {"status": 200, "bytes": len(payload["buffer"]), "format": preview["format"],
               "characters": preview["characters"], "filename": preview["filename"]})
        page.locator("#extract").click()
        expect(page.locator("#status")).to_contain_text("review")
        check(f"{label}_extraction_consent_gate", count("/api/extract") == extract_before)
        reviewed = SYNTHETIC + " Reviewed synthetic summary."
        page.locator("#cv").fill(reviewed)
        page.locator("#consent").check()
        extracted = click_api(page, "#extract", "/api/extract")
        expect(page.locator("#skill-count")).to_have_text("3")
        check(f"{label}_reviewed_extraction", set(extracted["skills"]) == {"sql", "excel", "power bi"}
              and last_body("/api/extract") == {"text": reviewed, "consent": True}, extracted)
        analysis = click_api(page, "#analyze", "/api/analyze")
        expect(page.locator("#overview")).to_be_visible()
        expect(page.locator(".score-ring strong")).to_have_text("39.6%")
        check(f"{label}_kenya_gap", analysis["coverage"] == 39.6 and analysis["sample_size"] > 0
              and analysis["country"] == "Kenya" and bool(analysis["gaps"]),
              {k: analysis.get(k) for k in ("country", "role", "coverage", "scope", "sample_size", "local_postings", "fallback", "matched_count", "gaps")})
        check(f"{label}_layout", page.evaluate("document.documentElement.scrollWidth <= innerWidth"), page.viewport_size)

    def curated(page):
        page.locator('[data-tab="plan"]').click()
        expect(page.locator("#ai-consent")).not_to_be_checked()
        plan = click_api(page, "#generate-plan", "/api/plan")
        expect(page.locator("#plan .tiny-badge")).to_have_text("Curated plan")
        expect(page.locator(".week-card")).to_have_count(4)
        body = last_body("/api/plan")
        check("curated_default", plan["mode"] == "curated" and plan["model"] is None
              and body["use_ai"] is False and body["ai_consent"] is False,
              {"status": 200, "mode": plan["mode"], "model": plan["model"], "weeks": len(plan["weeks"]), "request": body})

    def remote(page):
        assert not reservations, "Remote attempt already reserved in deployed-results.json; no retry permitted"
        page.locator("#new-plan").click()
        expect(page.locator("#ai-consent")).not_to_be_checked()
        page.locator("#ai-consent").check()
        start = time.monotonic()
        plan = click_api(page, "#generate-plan", "/api/plan", timeout=90000)
        body = last_body("/api/plan")
        evidence = {"status": 200, "mode": plan.get("mode"), "model": plan.get("model"),
                    "note": plan.get("note"), "weeks": len(plan.get("weeks", [])),
                    "elapsed_seconds": round(time.monotonic() - start, 3), "request": body,
                    "first_week": plan.get("weeks", [None])[0]}
        result["remote_plan"] = evidence
        reservations[-1].update(state="response_received", mode=plan.get("mode"), model=plan.get("model"))
        check("actual_groq_plan", plan.get("mode") == "groq" and plan.get("model") == EXPECTED_MODEL
              and len(plan.get("weeks", [])) == 4, evidence)
        check("remote_separate_consent_structured_only", body.get("use_ai") is True
              and body.get("ai_consent") is True
              and set(body) == {"country", "role", "skills", "hours", "use_ai", "ai_consent"}, body)
        page.locator("#plan").scroll_into_view_if_needed()
        screenshot(page, "public-ai.png")
        expect(page.locator("#plan .tiny-badge")).to_have_text("AI coaching · Groq")

    def practice(page):
        page.locator('[data-tab="practice"]').click()
        page.locator("#practice-skill").select_option("sql")
        assessment = click_api(page, "#start-practice", "/api/assessment/sql")
        expect(page.locator("#practice-form")).to_be_visible()
        for index, answer in enumerate([1, 2, 0]):
            page.locator(f'input[name="q{index}"][value="{answer}"]').check()
        reflection = "Synthetic reflection: check duplicates and NULL values before summing sales."
        page.locator("#reflection").fill(reflection)
        grade = click_api(page, '#practice-form button[type="submit"]', "/api/assessment/grade")
        expect(page.locator("#practice")).to_contain_text("SQL · 3/3 correct")
        check("sql_grading", assessment["skill"] == "sql" and grade["correct"] == grade["total"] == 3,
              {"status": 200, "grade": grade, "request": last_body("/api/assessment/grade")})
        check("reflection_not_transmitted", last_body("/api/assessment/grade") == {"skill": "sql", "answers": [1, 2, 0]})
        with page.expect_download() as pending:
            page.locator("#practice [data-download]").click()
        download = pending.value
        assert download.failure() is None, download.failure()
        data = Path(download.path()).read_bytes()
        text = data.decode("utf-8")
        checks = {"filename": download.suggested_filename == "njia-skill-evidence.md",
                  "grade": "3/3 correct" in text, "plan": "Four-week learning plan" in text,
                  "coverage": "39.6%" in text, "reflection": reflection in text,
                  "no_raw_cv": SYNTHETIC not in text, "limitations": "Methods and limitations" in text,
                  "model": EXPECTED_MODEL in text}
        check("evidence_download", all(checks.values()), {"filename": download.suggested_filename,
              "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "content_checks": checks})
        screenshot(page, "public-practice.png")

    save()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            desktop = browser.new_context(viewport={"width": 1440, "height": 1100}, reduced_motion="reduce")
            page = attach(desktop, "desktop")
            phase("desktop-home", lambda: home(page, "desktop"), page)

            def public_paths():
                for path, mime in (("/api/health", "application/json"), ("/static/styles.css", "text/css"),
                                   ("/static/app.js", "javascript"), ("/static/sample-cv.txt", "text/plain")):
                    response = desktop.request.get(BASE + path)
                    entry = {"context": "anonymous_request", "utc": utc(), "method": "GET", "url": response.url,
                             "status": response.status, "content_type": response.headers.get("content-type", "")}
                    result["responses"].append(entry)
                    check(f"public_path_{path}", response.status == 200 and mime in entry["content_type"], entry)
                    if path == "/api/health" and response.status == 200:
                        check("health_payload", response.json().get("status") == "ok", response.json())
                    if path.endswith("sample-cv.txt") and response.status == 200:
                        check("synthetic_sample_download", "SQL" in response.text() and "Excel" in response.text(),
                              {"bytes": len(response.body()), "sample": response.text()})
                expect(page.locator('link[rel="stylesheet"]')).to_have_attribute("href", "/static/styles.css")
                expect(page.locator("script[src]")).to_have_attribute("src", "/static/app.js")
                expect(page.locator(".sample-download")).to_have_attribute("href", "/static/sample-cv.txt")
                check("declared_upload_limits", page.locator("#cv").get_attribute("maxlength") == "15000"
                      and "4,000,000" in page.locator("#upload-help").inner_text(),
                      {"ui_max_file_bytes": 4000000, "preview_max_characters": 15000,
                       "boundary_uploads_tested": False, "help": page.locator("#upload-help").inner_text()})

            phase("public-paths", public_paths, page)
            phase("desktop-pdf", lambda: upload_gap(page, "pdf", "desktop"), page)
            phase("curated-plan", lambda: curated(page), page)
            phase("remote-ai", lambda: remote(page), page)
            phase("sql-practice-download", lambda: practice(page), page)
            mobile = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True,
                                         has_touch=True, reduced_motion="reduce")
            phone = attach(mobile, "mobile")
            phase("mobile-home", lambda: home(phone, "mobile"), phone)
            phase("mobile-txt", lambda: upload_gap(phone, "txt", "mobile"), phone)
            screenshot(phone, "public-mobile.png")
            mobile.close()
            desktop.close()
        finally:
            browser.close()
            origin = urlsplit(BASE)
            external = [r for r in result["requests"] if (urlsplit(r["url"]).scheme, urlsplit(r["url"]).netloc) != (origin.scheme, origin.netloc)]
            wrong_origin = [r for r in result["requests"] if r["method"] == "POST" and r.get("origin") != f"{origin.scheme}://{origin.netloc}"]
            check("https_same_origin_requests", not external and not wrong_origin,
                  {"external_requests": external, "incorrect_post_origins": wrong_origin})
            check("no_http_403", not any(r["status"] == 403 for r in result["responses"]))
            check("all_observed_http_success", all(200 <= r["status"] < 400 for r in result["responses"]))
            check("no_javascript_errors", not result["javascript_errors"], result["javascript_errors"])
            check("no_console_errors", not result["console_errors"], result["console_errors"])
            check("no_failed_requests", not result["request_failures"], result["request_failures"])
            check("remote_call_count", result["remote_ai_requests_this_run"] == 1 and len(reservations) == 1,
                  {"actual_this_run": result["remote_ai_requests_this_run"], "reserved_total": len(reservations), "limit": 1})
            result["finished_utc"] = utc()
            result["status"] = "failed" if result["failures"] else "passed"
            save()
    print(json.dumps({"status": result["status"], "checks": len(result["checks"]),
                      "failures": result["failures"], "remote_plan": result.get("remote_plan"),
                      "evidence": str(RESULTS)}, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
