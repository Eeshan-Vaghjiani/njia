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
                prompt = question.get("question", "").lower()
                detail = ("This was a personal practice dashboard built with synthetic retail data, not used by a real business."
                          if "dashboard" in prompt or "power bi" in prompt else
                          "This was a personal SQL practice project, not used by a real business."
                          if "sql" in prompt else DETAIL_ANSWER)
                box.first.fill(detail)
                answered["detail"] = True
                answered["detail_answer"] = detail
    return answered


def warm_caches(api, base, gap=65, attempts=1):
    """Warm server-side web-search caches (role/country only; no CV data).

    Searches use the separate search model (default gpt-oss-120b). A search can
    use 50-100K tokens against the documented 200K/day free-tier allowance.
    Spacing helps minute limits, not daily exhaustion. No retry by default;
    explicitly allow a second attempt only with sufficient provider quota.
    Interview-search failures are cached for two minutes, so retries wait longer.
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
        for attempt in range(1, attempts + 1):
            started = time.monotonic()
            try:
                response = api.post(base + path, data=body, timeout=90000)
                data = response.json()
                entry = {"path": path, "attempt": attempt, "status": response.status, "ok": response.ok and bool(good(data)),
                         "cached": data.get("cached"), "mode": data.get("mode") or data.get("status"),
                         "items": len(data.get("jobs") or data.get("questions") or []),
                         "seconds": round(time.monotonic() - started, 2)}
            except Exception as error:  # A cold cache only slows the timeline; never fake output.
                entry = {"path": path, "attempt": attempt, "ok": False, "error": type(error).__name__}
            warmed.append(entry)
            print("warm-up:", entry, flush=True)
            if entry["ok"] or attempt == attempts:
                break
            time.sleep(retry_wait)
        if not entry["ok"]:
            return warmed  # Stop before spending quota on the next search or recording.
    time.sleep(gap)
    return warmed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=coach_acceptance.BASE)
    parser.add_argument("--rehearsal", action="store_true",
                        help="Skip cache warm-up and allow labelled fallback modes (local timing/selector check only).")
    parser.add_argument("--warm-attempts", type=int, choices=(1, 2), default=1,
                        help="Attempts per warm-up endpoint (default: 1; retries consume search quota).")
    parser.add_argument("--allow-web-fallback", action="store_true",
                        help="Record honestly labelled curated interview questions if web research is unavailable; AI coaching still required.")
    parser.add_argument("--skip-warmup", action="store_true",
                        help="Skip extra search calls after an analyzed warm-up attempt; UI requests still use real APIs.")
    args = parser.parse_args()
    base = coach_acceptance.BASE = args.base_url.rstrip("/")
    ffmpeg, ffprobe = shutil.which("ffmpeg"), shutil.which("ffprobe")
    assert ffmpeg and ffprobe, "ffmpeg and ffprobe must be on PATH."
    ARTIFACTS.mkdir(exist_ok=True)
    result = {"status": "running", "base_url": base, "synthetic_only": True, "mocked_responses": 0,
              "playback_speed": "1x", "rehearsal": args.rehearsal, "allow_web_fallback": args.allow_web_fallback,
              "warmup_skipped": args.skip_warmup, "timeline": [], "late_cues": [], "checks": []}
    raw = ARTIFACTS / ("njia-coach-demo-rehearsal-raw.webm" if args.rehearsal else "njia-coach-demo-raw.webm")
    results_name = "njia-coach-demo-rehearsal.json" if args.rehearsal else "njia-coach-demo-results.json"
    stamp = time.strftime("%Y%m%d-%H%M%S")
    for previous in (ARTIFACTS / results_name, raw, ARTIFACTS / "coach-demo-failure.png"):
        if previous.exists():
            shutil.copy2(previous, previous.with_name(f"{previous.stem}-{stamp}{previous.suffix}"))

    def check(name, condition, evidence=None):
        if args.rehearsal and name in {"actual_ai_advisor", "actual_ai_questions", "actual_ai_feedback",
                                      "web_interview_questions", "answers_reached_brief"}:
            result["checks"].append({"name": name, "passed": bool(condition), "required": False, "evidence": evidence})
            return  # Keep observed failures visible; rehearsals are never publication evidence.
        result["checks"].append({"name": name, "passed": bool(condition), "evidence": evidence})
        assert condition, (name, evidence)

    with sync_playwright() as p:
        # Launch first so missing Chromium does not waste public search quota.
        browser = p.chromium.launch()
        # Warm up outside the recorded context; none of this wait belongs in the video.
        api = p.request.new_context()
        result["prewarmed"] = [] if args.rehearsal or args.skip_warmup else warm_caches(api, base, attempts=args.warm_attempts)
        api.dispose()
        if not (args.rehearsal or args.skip_warmup or args.allow_web_fallback) and (len(result["prewarmed"]) < 2 or not result["prewarmed"][-1]["ok"]):
            result.update(status="failed", error="Cache warm-up failed; recording not started. Check quota before rerunning.")
            save(results_name, result)
            browser.close()
            raise RuntimeError(result["error"])
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
                if not args.rehearsal:
                    assert remaining >= -1, f"Missed {seconds}s cue by {-remaining:.2f}s; retain raw, do not publish a truncated story."
                caption(page, section, text)
                result["timeline"].append({"cue_seconds": seconds, "actual_seconds": round(time.monotonic() - started, 3),
                                           "section": section, "caption": text})

            at(0, "NJIA / YOUR NEXT MOVE", "Upload a CV. Answer follow-ups, explore live jobs, then practise interview answers with feedback. Provider fallbacks are labelled.")
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
            check("actual_ai_questions", questions.get("mode") in {"groq", "nvidia"}, questions.get("mode"))
            frame(page, "#followup-panel", 20)
            at(21, "QUICK QUESTIONS, SHARPER ADVICE", f"{len(questions['questions'])} questions ({questions.get('model') or 'curated'}) in {q_elapsed:.1f}s. The fictional candidate answers truthfully.")
            result["answered"] = answer_questions(page, questions["questions"])

            at(29, "YOUR ANSWERS GO INTO THE BRIEF", "Build my brief with these answers sends the CV and answers to the AI provider. Stats are computed separately.")
            data, elapsed = click_api(page, "#followup-submit", "/api/advise", timeout=135000)
            a, m = data["advisor"], data["market"]
            result.update(response=data, elapsed_seconds=elapsed)
            check("actual_ai_advisor", a["mode"] in {"groq", "nvidia"}, {"mode": a["mode"], "model": a["model"], "elapsed_seconds": elapsed})
            check("answers_reached_brief", bool(a.get("answers_used")), a.get("answers_used"))
            expect(page.locator("#ai-provenance")).to_contain_text(a["model"] or "none")
            check("seven_day_plan", len(a["seven_day_plan"]) == 7)
            frame(page, "#results", 25)
            provider = {"groq": "Groq", "nvidia": "NVIDIA API Catalog (Groq backup)"}.get(a["mode"], a["mode"])
            at(37, "LIVE RESULT / SHAPED BY YOUR ANSWERS", f"Returned by {a['model']} via {provider} in {elapsed:.1f}s. The brief notes which answers changed the skills.")
            research_started = time.monotonic()
            research = []

            def research_response(response):
                if response.url.endswith("/api/interview/questions"):
                    research.append((response.json(), time.monotonic() - research_started, response.status))

            page.on("response", research_response)
            page.locator("#load-web-questions").click()
            frame(page, "#results", 25)

            at(43, "03 / LIVE JOBS YOU CAN APPLY FOR", "Remote postings open to applicants in Kenya. Local web search runs separately; check its live status and verify each listing.")
            frame(page, "#live-jobs-section", 25)
            expect(page.locator("#live-jobs .live-job").first).to_be_visible(timeout=25000)
            result["live_jobs_shown"] = page.locator("#live-jobs .live-job").count()
            check("live_jobs_rendered", result["live_jobs_shown"] > 0, result["live_jobs_shown"])
            if not args.rehearsal:
                expect(page.locator('#live-jobs .live-job[data-kind="remote"]').first).to_be_visible()
                if not args.allow_web_fallback:
                    expect(page.locator('#live-jobs .live-job[data-kind="local"]').first).to_be_visible()
            result["live_jobs_by_kind"] = {kind: page.locator(f'#live-jobs .live-job[data-kind="{kind}"]').count()
                                           for kind in ("remote", "local")}
            result["live_jobs_status_text"] = page.locator("#live-jobs").inner_text()
            at(49, "MATCHED TO YOUR SKILLS", "Each job shows the skills you have and the ones to build. Match % is skill overlap, not a hiring probability.")
            frame(page, '#live-jobs .live-job[data-kind="local"]' if result["live_jobs_by_kind"]["local"] else "#live-jobs .live-job", 70)

            at(53, "04 / SAY IT BETTER", "Draft rewrites need factual review. Verify every claim against your CV and answers; AI can add unsupported details.")
            frame(page, "#rewrite-title", 45)
            result["actual_rewrite_count"] = len(a["cv_improvements"])
            at(57, "05 / SEVEN DAYS, ON WHATSAPP", "Seven small actions, each with a deliverable. Tick off progress, or send the checklist to yourself on WhatsApp.")
            frame(page, "#plan-title", 35)
            page.locator('[data-day="0"]').check()
            check("whatsapp_share_visible", page.locator("#whatsapp-checklist").is_visible())

            at(62, "06 / INTERVIEW PREPARATION", "Research started after the brief, while we explored jobs. If unavailable, Njia shows a labelled curated bank instead.")
            frame(page, "#interview-research-section", 25)
            while not research and time.monotonic() - research_started < 80:
                page.wait_for_timeout(100)
            assert research, "Interview research did not return within 80 seconds."
            iq, iq_elapsed, iq_status = research[0]
            check("interview_request_success", iq_status == 200, iq_status)
            result.update(interview_questions=iq, interview_seconds=iq_elapsed)
            if args.allow_web_fallback and iq.get("mode") == "curated":
                check("curated_interview_fallback_labelled", "not web-sourced" in page.locator("#interview-research").inner_text().lower(), iq.get("note"))
            else:
                check("web_interview_questions", iq.get("mode") == "web" and bool(iq.get("sources")), iq.get("mode"))
            expect(page.locator("#interview-research .web-question").first).to_be_visible()
            at(71, "WEB-SOURCED QUESTIONS" if iq["mode"] == "web" else "CURATED FALLBACK / NOT WEB-SOURCED",
               f"{len(iq['questions'])} questions. " + ("Source links let you check the context." if iq["mode"] == "web" else "Web research did not return usable sources. These are Njia's curated practice questions."))
            frame(page, "#interview-research .web-question", 60)

            at(76, "PRACTISE, THEN GET FEEDBACK", "AI feedback suggests structure. Verify every fact; it can add unsupported details.")
            practice_index = next((i for i, q in enumerate(iq["questions"]) if q.get("category") == "behavioural"), 0)
            result["practised_question"] = iq["questions"][practice_index]["question"]
            page.locator("#interview-research .web-question .practise-button").nth(practice_index).click()
            page.locator("#practice-answer").fill(PRACTICE_ANSWER)
            page.locator("#practice-consent").check()
            feedback, fb_elapsed = click_api(page, "#practice-submit", "/api/interview/feedback", timeout=70000)
            result.update(feedback=feedback, feedback_seconds=fb_elapsed)
            check("actual_ai_feedback", feedback.get("mode") in {"groq", "nvidia"}, feedback.get("mode"))
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
            check("single_questions_and_feedback_calls", audit.count("/api/questions") == audit.count("/api/interview/feedback") == 1)
            check("single_interview_search_call", audit.count("/api/interview/questions") == 1)
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
    try:
        result["video"] = finalize(raw, target, ffmpeg, ffprobe)
    except Exception as error:
        result.update(status="failed", error=f"{type(error).__name__}: {error}")
        save(results_name, result)
        raise
    check("exact_90_seconds_silent_normal_speed", result["video"]["duration_seconds"] == 90.0)
    old, backup = ARTIFACTS / "njia-demo-90s.webm", ARTIFACTS / "njia-demo-90s-previous.webm"
    if not args.rehearsal:
        if old.exists() and not backup.exists():
            shutil.copy2(old, backup)
            result["previous_video_preserved"] = str(backup.relative_to(ARTIFACTS.parent))
        shutil.copy2(target, old)
    result.update(status="rehearsed" if args.rehearsal else "passed", passed=sum(c["passed"] for c in result["checks"]))
    save(results_name, result)
    print(json.dumps({"status": result["status"], "checks": result["passed"], "duration": result["video"]["duration_seconds"],
                      "model": result["response"]["advisor"]["model"], "late_cues": result["late_cues"],
                      "prewarmed": result["prewarmed"], "video": str(target if args.rehearsal else old)}, indent=2))


if __name__ == "__main__":
    main()
