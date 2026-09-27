"""Record the real public coach at 1x: exactly 90 seconds, captions, no audio."""
import json
import shutil
import time

from playwright.sync_api import expect, sync_playwright

from coach_acceptance import (ARTIFACTS, BASE, PDF_TEXT, home, click_api,
                              download, reserve, save, make_pdf, file_payload, Audit)
from record_demo import caption, frame, finalize


def main():
    ffmpeg, ffprobe = shutil.which("ffmpeg"), shutil.which("ffprobe")
    assert ffmpeg and ffprobe
    result = {"status": "running", "base_url": BASE, "synthetic_only": True,
              "mocked_responses": 0, "playback_speed": "1x", "timeline": [], "checks": []}
    raw = ARTIFACTS / "njia-coach-demo-raw.webm"

    def check(name, condition, evidence=None):
        result["checks"].append({"name": name, "passed": bool(condition), "evidence": evidence})
        assert condition, (name, evidence)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={"width": 1280, "height": 720},
            record_video_dir=str(ARTIFACTS / "coach-video-source"),
            record_video_size={"width": 1280, "height": 720}, reduced_motion="reduce")
        page = context.new_page()
        page.set_default_timeout(12000)
        audit = Audit(page)
        video = page.video
        try:
            result["meta_ai"] = home(page).get("ai")
            started = time.monotonic()

            def at(seconds, section, text):
                remaining = started + seconds - time.monotonic()
                assert remaining > -1.0, f"Missed {seconds}s cue by {-remaining:.2f}s; raw retained."
                if remaining > 0:
                    page.wait_for_timeout(remaining * 1000)
                caption(page, section, text)
                result["timeline"].append({"cue_seconds": seconds, "actual_seconds": round(time.monotonic() - started, 3),
                                           "section": section, "caption": text})

            at(0, "NJIA / YOUR NEXT MOVE", "A sharper CV. A focused week. Career advice grounded in your experience and historical Kenyan market evidence.")
            page.evaluate("window.scrollTo(0,0)")
            at(6, "01 / A REAL PDF, A FICTIONAL CANDIDATE", "Upload a synthetic CV: Excel sales reports, a Power BI dashboard and a SQL practice project. No real personal details.")
            page.locator("#cv-file").set_input_files(file_payload("pdf", make_pdf(PDF_TEXT), "synthetic-coach-cv.pdf"))
            frame(page, "#file-zone", 110)
            at(12, "REVIEW THE CONSENT", "Consent permits server file processing and sending CV text to the AI provider with basic contact redaction.")
            page.locator("#consent").check()
            frame(page, ".consent-block", 230)
            at(18, "02 / ONE CLICK → YOUR CAREER BRIEF", "Build my career brief reads the PDF and calls the real public /api/advise endpoint. This is a live request.")
            reserve("record_coach_demo_pdf")
            with page.expect_response(lambda r: r.url.endswith("/api/upload")) as upload_pending:
                data, elapsed = click_api(page, "#build-brief", "/api/advise", timeout=90000)
            result.update(response=data, elapsed_seconds=elapsed, upload=upload_pending.value.json())
            a, m = data["advisor"], data["market"]
            check("actual_pdf_upload", result["upload"]["text"] == PDF_TEXT and result["upload"]["format"] == "pdf")
            check("actual_groq_advisor", a["mode"] == "groq", {"model": a["model"], "elapsed_seconds": elapsed})
            expect(page.locator("#ai-provenance")).to_contain_text(a["model"])
            check("seven_day_plan", len(a["seven_day_plan"]) == 7)
            frame(page, "#results", 25)
            at(25, "LIVE RESULT / GROQ", f"Returned by {a['model']} in {elapsed:.2f}s, including PDF processing. The mode and model are visible in the brief.")
            page.screenshot(path=str(ARTIFACTS / "coach-demo-groq.png"))
            if a["strengths"]:
                page.locator("#strengths summary").first.click()
                frame(page, "#summary-card", 35)
            at(31, "EVIDENCE FOR YOUR STRENGTHS", "Open a strength to inspect the CV evidence behind it. Suggested skills still need your review; they are not verified proficiency.")
            frame(page, "#strengths", 130)
            at(37, "03 / THREE PRIORITIES. ONE DIRECTION.", f"The actual response uses {m['sample_size']} historical postings and {m['coverage']}% demand-weighted coverage. This is not a hiring probability.")
            frame(page, "#market-title", 45)
            at(43, "MAKE THE FIRST MOVE SMALL", "Each priority pairs market demand with a practical first step. These are historical examples, not live vacancies.")
            frame(page, "#priority-cards", 45)
            if a["cv_improvements"]:
                at(49, "04 / BEFORE → SUGGESTED REWRITE", "Compare the original CV bullet with the returned rewrite. Check every fact; add a metric only when you can verify it.")
            else:
                at(49, "04 / HONEST CV FEEDBACK", "No grounded rewrite was returned for this request. The app says so: clarify a real task, tool and outcome without inventing achievements.")
            frame(page, "#rewrite-title", 45)
            result["actual_rewrite_count"] = len(a["cv_improvements"])
            page.screenshot(path=str(ARTIFACTS / "coach-demo-rewrites.png"))
            at(56, "05 / YOUR NEXT SEVEN DAYS", "Seven small actions, each with something tangible to keep. Mark progress for this session as you work through the plan.")
            frame(page, "#plan-title", 35)
            page.locator('[data-day="0"]').check()
            at(62, "FROM ADVICE TO SOMETHING YOU CAN SHOW", "Continue through the week: practise, save your work and explain what you learned. The checklist is yours to take away.")
            frame(page, '#seven-day-plan li:nth-child(4)', 65)
            at(68, "06 / PRACTISE YOUR INTERVIEW ANSWER", "One tailored question, plus what a good answer includes. Use your real experience to practise a clear explanation.")
            page.locator("#interview-guidance summary").click()
            frame(page, "#interview-section", 40)
            at(75, "REVIEW YOUR SKILLS", "Keep skills you can support. Confirming recalculates historical market evidence without generating another AI brief.")
            frame(page, "#skill-review", 45)
            confirmed, _ = click_api(page, "#confirm-skills", "/api/analyze")
            result["confirmed_market"] = confirmed
            expect(page.locator("#skill-status")).to_contain_text("Skills confirmed")
            at(81, "07 / DOWNLOAD YOUR CAREER BRIEF", "The HTML download excludes CV evidence quotes and before/after rewrites by default. Include them only by checking the opt-in.")
            frame(page, ".export-card", 35)
            expect(page.locator("#include-excerpts")).not_to_be_checked()
            default = download(page, "coach-demo-default.html")
            check("default_download_excludes_excerpt_sections", "<h2>CV evidence</h2>" not in default and "<h2>CV rewrites" not in default)
            page.wait_for_timeout(1200)
            page.locator("#include-excerpts").check()
            included = download(page, "coach-demo-with-excerpts.html")
            check("optin_download_includes_rewrite_section", "<h2>CV rewrites" in included)
            at(87, "NJIA / A CLEARER NEXT MOVE", "gomycode-2026.vercel.app · Review your brief. Build evidence. Take your next step.")
            page.wait_for_timeout(max(0, started + 91 - time.monotonic()) * 1000)
            check("single_recording_advice_call", audit.count("/api/advise") == 1)
            check("no_javascript_errors", not audit.errors, audit.errors)
            check("all_observed_api_success", all(r["status"] == 200 for r in audit.responses), audit.responses)
            result["status"] = "recorded"
        except Exception as error:
            result.update(status="failed", error=f"{type(error).__name__}: {error}")
            page.screenshot(path=str(ARTIFACTS / "coach-demo-failure.png"))
            raise
        finally:
            result.update(requests=audit.requests, responses=audit.responses, javascript_errors=audit.errors)
            context.close()
            video.save_as(str(raw))
            video.delete()
            browser.close()
            save("njia-coach-demo-results.json", result)
    target = ARTIFACTS / "njia-coach-demo-90s.webm"
    result["video"] = finalize(raw, target, ffmpeg, ffprobe)
    check("exact_90_seconds_silent_normal_speed", result["video"]["duration_seconds"] == 90.0)
    old = ARTIFACTS / "njia-demo-90s.webm"
    backup = ARTIFACTS / "njia-demo-90s-previous.webm"
    if old.exists():
        assert not backup.exists(), "Backup exists; preserve it and inspect before replacing."
        shutil.copy2(old, backup)
        result["previous_video_preserved"] = str(backup.relative_to(ARTIFACTS.parent))
    shutil.copy2(target, old)
    result.update(status="passed", passed=sum(c["passed"] for c in result["checks"]))
    save("njia-coach-demo-results.json", result)
    print(json.dumps({"status": result["status"], "checks": result["passed"], "duration": result["video"]["duration_seconds"],
                      "model": result["response"]["advisor"]["model"], "elapsed_seconds": result["elapsed_seconds"],
                      "video": str(target), "old_preserved": result.get("previous_video_preserved")}, indent=2))


if __name__ == "__main__":
    main()
