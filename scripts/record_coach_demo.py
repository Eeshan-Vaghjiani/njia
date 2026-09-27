"""Record the real coach at 1x: exactly 90 seconds, captions, no audio.

Story: upload a synthetic PDF -> Njia asks follow-up skill questions -> the brief
is shaped by the answers -> live jobs open to Kenyan applicants -> fact-keeping
rewrites and a seven-day plan (WhatsApp) -> real interview questions found on
the web -> practise an answer with AI feedback -> privacy-aware download.

Web-search caches (jobs and interview questions for Kenya / Data Analyst) are
warmed before the first caption so a slow search does not stall the timeline.
Warm-up calls are recorded in the results JSON. Answers follow the fictional
CV truthfully (for example, Python is "Still learning it").

Usage: .venv/bin/python scripts/record_coach_demo.py [--base-url http://127.0.0.1:8000]
"""
import argparse
import json
import shutil
import time

from playwright.sync_api import expect, sync_playwright

import coach_acceptance
from coach_acceptance import ARTIFACTS, PDF_TEXT, click_api, download, save, make_pdf, file_payload, Audit
from record_demo import caption, frame, finalize

COUNTRY, ROLE = "Kenya", "Data Analyst"
# Truthful answers for the fictional candidate in PDF_TEXT.
SKILL_ANSWERS = {"excel": "Used it at work", "sql": "Used it in a project or course",
                 "power bi": "Used it in a project or course", "python": "Still learning it"}
DETAIL_ANSWER = "The operations team used the monthly sales summary to plan stock for the three branches."
PRACTICE_ANSWER = (
    "At the retail cooperative, weekly sales totals did not match the stock records. "
    "I checked the sales spreadsheets against the stock records, found duplicate entries and flagged them to my supervisor. "
    "I then rebuilt the Excel pivot table summary and checked the totals against the source spreadsheet, "
    "so the operations team could trust the weekly report again."
)


def answer_questions(page, questions):
    answered = {"skills": {}, "detail": False}
    for question in questions:
        if question.get("type") == "skill":
            value = SKILL_ANSWERS.get(question.get("skill"), "Not yet")
            radio = page.locator(f'#followup-panel input[name="followup-{question["id"]}"][value="{value}"]')
            if radio.count():
                # Styled pills may visually hide the native radio; set it the way a click would.
                radio.first.evaluate("el => { el.checked = true; el.dispatchEvent(new Event('change', {bubbles: true})); }")
                answered["skills"][question.get("skill")] = value
        elif question.get("type") == "detail" and not answered["detail"]:
            box = page.locator("#followup-panel textarea")
            if box.count():
                box.first.fill(DETAIL_ANSWER)
                answered["detail"] = True
    return answered


def warm_caches(api, base, gap=65):
    """Warm server-side web-search caches (role/country only; no CV data).

    Groq's free tier allows 8,000 tokens per minute per model, and a browser
    search can use most of that, so searches run one at a time with a gap, and
    the recording starts only after the window clears. Interview-search failures
    are cached for two minutes, so its retry waits longer.
    """
    skills = ["excel", "sql", "power bi"]
    plan = (("/api/jobs", {"country": COUNTRY, "role": ROLE, "skills": skills, "source": "web"},
             lambda d: d.get("status") == "ok" and bool(d.get("jobs")), gap),
            ("/api/interview/questions", {"country": COUNTRY, "role": ROLE, "skills": skills},
             lambda d: d.get("mode") == "web", 125))
    warmed = []
    for index, (path, body, good, retry_wait) in enumerate(plan):
        if index:
            time.sleep(gap)
        for attempt in (1, 2):
            started = time.monotonic()
            try:
                response = api.post(base + path, data=body, timeout=90000)
                data = response.json()
                entry = {"path": path, "attempt": attempt, "status": response.status, "ok": bool(good(data)),
                         "cached": data.get("cached"), "mode": data.get("mode") or data.get("status"),
                         "items": len(data.get("jobs") or data.get("questions") or []),
                         "seconds": round(time.monotonic() - started, 2)}
            except Exception as error:  # A cold cache only slows the timeline; never fake output.
                entry = {"path": path, "attempt": attempt, "ok": False, "error": type(error).__name__}
            warmed.append(entry)
            print("warm-up:", entry, flush=True)
            if entry["ok"] or attempt == 2:
                break
            time.sleep(retry_wait)
    time.sleep(gap)
    return warmed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=coach_acceptance.BASE)
    parser.add_argument("--rehearsal", action="store_true",
                        help="Skip cache warm-up and allow labelled fallback modes (local timing/selector check only).")
    args = parser.parse_args()
    base = coach_acceptance.BASE = args.base_url.rstrip("/")
    ffmpeg, ffprobe = shutil.which("ffmpeg"), shutil.which("ffprobe")
    assert ffmpeg and ffprobe, "ffmpeg and ffprobe must be on PATH."
    ARTIFACTS.mkdir(exist_ok=True)
    result = {"status": "running", "base_url": base, "synthetic_only": True, "mocked_responses": 0,
              "playback_speed": "1x", "rehearsal": args.rehearsal, "timeline": [], "late_cues": [], "checks": []}
    raw = ARTIFACTS / "njia-coach-demo-raw.webm"
    results_name = "njia-coach-demo-rehearsal.json" if args.rehearsal else "njia-coach-demo-results.json"

    def check(name, condition, evidence=None):
        if args.rehearsal and name in {"actual_groq_advisor", "answers_reached_brief"}:
            condition = True  # Rehearsals may run on fallback modes; never publish their video.
        result["checks"].append({"name": name, "passed": bool(condition), "evidence": evidence})
        assert condition, (name, evidence)

    with sync_playwright() as p:
        # Warm up outside the recorded context: finalize() looks for the sync marker in the first 5 raw seconds.
        api = p.request.new_context()
        result["prewarmed"] = [] if args.rehearsal else warm_caches(api, base)
        api.dispose()
        browser = p.chromium.launch()
        context = browser.new_context(viewport={"width": 1280, "height": 720},
            record_video_dir=str(ARTIFACTS / "coach-video-source"),
            record_video_size={"width": 1280, "height": 720}, reduced_motion="reduce")
        page = context.new_page()
        page.set_default_timeout(20000)
        audit = Audit(page)
        video = page.video
        try:
            result["meta_ai"] = coach_acceptance.home(page).get("ai")
            started = time.monotonic()

            def at(seconds, section, text):
                remaining = started + seconds - time.monotonic()
                if remaining > 0:
                    page.wait_for_timeout(remaining * 1000)
                elif remaining < -0.5:
                    result["late_cues"].append({"cue_seconds": seconds, "late_by_seconds": round(-remaining, 2)})
                caption(page, section, text)
                result["timeline"].append({"cue_seconds": seconds, "actual_seconds": round(time.monotonic() - started, 3),
                                           "section": section, "caption": text})

            at(0, "NJIA / YOUR NEXT MOVE", "Upload a CV. Njia asks what your CV doesn't say, finds live jobs you can apply for, and preps you with real interview questions.")
            page.evaluate("window.scrollTo(0,0)")
            at(5, "01 / A REAL PDF, A FICTIONAL CANDIDATE", "A synthetic CV: Excel sales reports, a Power BI dashboard and a SQL practice project. No real personal details.")
            page.locator("#cv-file").set_input_files(file_payload("pdf", make_pdf(PDF_TEXT), "synthetic-coach-cv.pdf"))
            frame(page, "#file-zone", 110)
            at(10, "CONSENT FIRST", "Consent covers server file processing and sending CV text, with basic contact redaction, to the AI provider.")
            page.locator("#consent").check()
            frame(page, ".consent-block", 230)

            at(14, "02 / NJIA ASKS BEFORE IT ADVISES", "Build my career brief reads the PDF. Then the AI asks about skills your CV doesn't clearly show. Live request.")
            with page.expect_response(lambda r: r.url.endswith("/api/upload")) as upload_pending:
                questions, q_elapsed = click_api(page, "#build-brief", "/api/questions", timeout=60000)
            result.update(questions=questions, questions_seconds=q_elapsed, upload=upload_pending.value.json())
            check("actual_pdf_upload", result["upload"]["text"] == PDF_TEXT and result["upload"]["format"] == "pdf")
            expect(page.locator("#followup-panel")).to_be_visible()
            check("followup_questions_shown", 2 <= len(questions["questions"]) <= 5, {"mode": questions.get("mode"), "model": questions.get("model")})
            frame(page, "#followup-panel", 20)
            at(21, "QUICK QUESTIONS, SHARPER ADVICE", f"{len(questions['questions'])} questions ({questions.get('model') or 'curated'}) in {q_elapsed:.1f}s. The fictional candidate answers truthfully.")
            result["answered"] = answer_questions(page, questions["questions"])

            at(29, "YOUR ANSWERS GO INTO THE BRIEF", "Build my brief with these answers sends the CV and answers to the AI provider. Stats are computed separately.")
            data, elapsed = click_api(page, "#followup-submit", "/api/advise", timeout=90000)
            a, m = data["advisor"], data["market"]
            result.update(response=data, elapsed_seconds=elapsed)
            check("actual_groq_advisor", a["mode"] in {"groq", "nvidia"}, {"mode": a["mode"], "model": a["model"], "elapsed_seconds": elapsed})
            check("answers_reached_brief", "answers_used" in a, a.get("answers_used"))
            expect(page.locator("#ai-provenance")).to_contain_text(a["model"] or "none")
            check("seven_day_plan", len(a["seven_day_plan"]) == 7)
            frame(page, "#results", 25)
            provider = {"groq": "Groq", "nvidia": "NVIDIA's API (Groq backup)"}.get(a["mode"], a["mode"])
            at(37, "LIVE RESULT / SHAPED BY YOUR ANSWERS", f"Returned by {a['model']} via {provider} in {elapsed:.1f}s. The brief notes which answers changed the skills.")

            at(43, "03 / LIVE JOBS YOU CAN APPLY FOR", "Current remote postings open to applicants in Kenya, plus local postings found by web search with verified links.")
            frame(page, "#live-jobs-section", 25)
            expect(page.locator("#live-jobs .live-job").first).to_be_visible(timeout=25000)
            result["live_jobs_shown"] = page.locator("#live-jobs .live-job").count()
            check("live_jobs_rendered", result["live_jobs_shown"] > 0, result["live_jobs_shown"])
            at(49, "MATCHED TO YOUR SKILLS", "Each job shows the skills you have and the ones to build. Match % is skill overlap, not a hiring probability.")
            frame(page, "#live-jobs .live-job", 70)

            at(55, "04 / SAY IT BETTER", "Rewrites keep your facts. They may use details from your answers, and each one still needs your check.")
            frame(page, "#rewrite-title", 45)
            result["actual_rewrite_count"] = len(a["cv_improvements"])
            at(60, "05 / SEVEN DAYS, ON WHATSAPP", "Seven small actions, each with a deliverable. Tick off progress, or send the checklist to yourself on WhatsApp.")
            frame(page, "#plan-title", 35)
            page.locator('[data-day="0"]').check()
            check("whatsapp_share_visible", page.locator("#whatsapp-checklist").is_visible())

            at(65, "06 / WHAT INTERVIEWERS ACTUALLY ASK", "Njia searches the web for questions candidates report being asked and keeps only those with a verifiable source.")
            frame(page, "#interview-research-section", 25)
            iq, iq_elapsed = click_api(page, "#load-web-questions", "/api/interview/questions", timeout=90000)
            result.update(interview_questions=iq, interview_seconds=iq_elapsed)
            expect(page.locator("#interview-research .web-question").first).to_be_visible()
            at(71, "REAL QUESTIONS, REAL SOURCES", f"{len(iq['questions'])} questions ({'web-sourced' if iq['mode'] == 'web' else 'curated fallback'}). Where it fits, Njia points to your own CV evidence.")
            frame(page, "#interview-research .web-question", 60)

            at(76, "PRACTISE, THEN GET FEEDBACK", "Type an answer, consent to AI feedback, and get a STAR check, a score and a stronger outline that invents nothing.")
            page.locator("#interview-research .web-question .practise-button").first.click()
            page.locator("#practice-answer").fill(PRACTICE_ANSWER)
            page.locator("#practice-consent").check()
            feedback, fb_elapsed = click_api(page, "#practice-submit", "/api/interview/feedback", timeout=60000)
            result.update(feedback=feedback, feedback_seconds=fb_elapsed)
            expect(page.locator("#practice-feedback")).to_be_visible()
            check("practice_feedback_scored", isinstance(feedback.get("score"), int), {"mode": feedback.get("mode"), "score": feedback.get("score")})
            frame(page, "#practice-feedback", 40)

            at(83, "07 / TAKE IT WITH YOU", "Download the brief. CV quotes and rewrites are excluded by default. Njia keeps no accounts and stores no CVs.")
            frame(page, ".export-card", 35)
            default = download(page, "coach-demo-default.html")
            check("default_download_excludes_excerpt_sections", "<h2>CV evidence</h2>" not in default and "<h2>CV rewrites" not in default)
            at(87, "NJIA / A CLEARER NEXT MOVE", "gomycode-2026.vercel.app · Ask. Match. Practise. Take your next step.")
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
            save(results_name, result)
    target = ARTIFACTS / ("njia-coach-demo-rehearsal.webm" if args.rehearsal else "njia-coach-demo-90s.webm")
    result["video"] = finalize(raw, target, ffmpeg, ffprobe)
    check("exact_90_seconds_silent_normal_speed", result["video"]["duration_seconds"] == 90.0)
    old, backup = ARTIFACTS / "njia-demo-90s.webm", ARTIFACTS / "njia-demo-90s-previous.webm"
    if not args.rehearsal:
        if old.exists() and not backup.exists():
            shutil.copy2(old, backup)
            result["previous_video_preserved"] = str(backup.relative_to(ARTIFACTS.parent))
        shutil.copy2(target, old)
    result.update(status="passed", passed=sum(c["passed"] for c in result["checks"]))
    save(results_name, result)
    print(json.dumps({"status": result["status"], "checks": result["passed"], "duration": result["video"]["duration_seconds"],
                      "model": result["response"]["advisor"]["model"], "late_cues": result["late_cues"],
                      "prewarmed": result["prewarmed"], "video": str(target if args.rehearsal else old)}, indent=2))


if __name__ == "__main__":
    main()
