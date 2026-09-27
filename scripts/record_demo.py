"""Record a live, silent, captioned 90-second demo; no fabricated app results.

Run after upload_browser_test.py. Requires ffmpeg/ffprobe on PATH. The raw
Playwright WebM is retained; only startup/tail footage is trimmed, at 1x speed.
Caption overlays are added with page.evaluate; all application actions use UI.
"""
import argparse
import json
import shutil
import subprocess
import time
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

from upload_browser_test import (ARTIFACTS, BASE_URL, SYNTHETIC, Audit,
                                 click_response, file_payload, make_pdf,
                                 ready, reserve_ai_call, save_json)


def caption(page, section, text):
    page.evaluate("""({section, text}) => {
      let box = document.getElementById('demo-caption');
      if (!box) {
        box = document.createElement('aside'); box.id = 'demo-caption';
        box.setAttribute('aria-label', 'Demo narration overlay');
        Object.assign(box.style, {position:'fixed', left:'20px', right:'20px',
          bottom:'20px', height:'100px', boxSizing:'border-box', padding:'15px 24px',
          background:'#102e29', color:'#ffffff', borderTop:'3px solid #d9edaa',
          borderRadius:'10px', boxShadow:'0 6px 30px #0003', zIndex:'2147483647',
          pointerEvents:'none', fontFamily:'Segoe UI, sans-serif'});
        const heading = document.createElement('div'); heading.id='demo-section';
        Object.assign(heading.style, {color:'#d9edaa', fontSize:'12px',
          fontWeight:'700', letterSpacing:'1.3px', marginBottom:'6px'});
        const copy = document.createElement('div'); copy.id='demo-copy';
        Object.assign(copy.style, {fontSize:'19px', lineHeight:'1.35'});
        box.append(heading, copy); document.body.append(box);
        // Two-pixel sync marker inside the overlay enables frame-accurate trim.
        const marker = document.createElement('div'); marker.id='demo-sync';
        Object.assign(marker.style, {position:'fixed', left:'22px', top:'690px',
          width:'2px', height:'2px', background:'rgb(1,254,127)',
          zIndex:'2147483647', pointerEvents:'none'});
        document.body.append(marker);
      }
      document.getElementById('demo-section').textContent=section;
      document.getElementById('demo-copy').textContent=text;
    }""", {"section": section, "text": text})


def frame(page, selector, top=90):
    page.locator(selector).first.evaluate(
        "(el, top) => window.scrollTo({top:window.scrollY+el.getBoundingClientRect().top-top, behavior:'instant'})", top)


def probe(path, ffprobe):
    return json.loads(subprocess.check_output([
        ffprobe, "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)
    ], text=True))


def finalize(raw, target, ffmpeg, ffprobe):
    # Read the first five seconds at 25fps, finding the actual caption start.
    # Scale-free rgb conversion before cropping avoids chroma subsampling loss.
    pixels = subprocess.check_output([
        ffmpeg, "-v", "error", "-i", str(raw), "-t", "5", "-vf",
        "fps=25,format=rgb24,crop=2:2:22:690", "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"
    ])
    first = None
    for index in range(len(pixels) // 12):
        tile = pixels[index * 12:(index + 1) * 12]
        r, g, b = (sum(tile[channel::3]) / 4 for channel in range(3))
        if g > 175 and g - r > 90 and g - b > 45:
            first = index / 25
            break
    assert first is not None, "Could not find caption sync marker in raw video."
    raw_meta = probe(raw, ffprobe)
    assert float(raw_meta["format"]["duration"]) >= first + 90, "Raw recording is too short; never pad or fake footage."
    subprocess.run([
        ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(raw),
        "-vf", f"trim=start={first}:duration=90,setpts=PTS-STARTPTS,fps=25",
        "-frames:v", "2250", "-an", "-c:v", "libvpx-vp9", "-crf", "28",
        "-b:v", "0", "-deadline", "good", "-cpu-used", "4", str(target)
    ], check=True)
    meta = probe(target, ffprobe)
    duration = float(meta["format"]["duration"])
    stream = next(s for s in meta["streams"] if s["codec_type"] == "video")
    assert abs(duration - 90) <= .04, duration
    assert (stream["width"], stream["height"]) == (1280, 720)
    assert not any(s["codec_type"] == "audio" for s in meta["streams"])
    return {"duration_seconds": duration, "trim_start_seconds": first,
            "raw_duration_seconds": float(raw_meta["format"]["duration"]),
            "viewport": "1280x720", "fps": 25, "frames": 2250,
            "audio": "none; silent with visible narration captions", "probe": meta}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=BASE_URL)
    args = parser.parse_args()
    ffmpeg, ffprobe = shutil.which("ffmpeg"), shutil.which("ffprobe")
    assert ffmpeg and ffprobe, "ffmpeg and ffprobe must be available on PATH."
    ARTIFACTS.mkdir(exist_ok=True)
    result = {"status": "running", "base_url": args.base_url, "synthetic_only": True,
              "mocked_requests": 0, "playback_speed": "1x", "timeline": []}
    raw = ARTIFACTS / "njia-demo-raw.webm"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={"width": 1280, "height": 720},
            record_video_dir=str(ARTIFACTS / "demo-video-source"),
            record_video_size={"width": 1280, "height": 720}, reduced_motion="reduce")
        page = context.new_page()
        page.set_default_timeout(10000)
        audit = Audit(page)
        video = page.video
        try:
            result["provider"] = ready(page, args.base_url)["ai"]
            started = time.monotonic()

            def at(seconds, section, text):
                remaining = started + seconds - time.monotonic()
                assert remaining > -1.0, f"Missed {seconds}s cue by {-remaining:.2f}s; retain raw and report failure."
                if remaining > 0:
                    page.wait_for_timeout(remaining * 1000)
                caption(page, section, text)
                result["timeline"].append({"cue": seconds, "actual": round(time.monotonic() - started, 3), "section": section, "caption": text})

            at(0, "NJIA / THE PROBLEM · 00–12s", "Which skill should I learn next? Turn a skills summary into a market-grounded next step.")
            at(6, "EVIDENCE BEFORE ADVICE", "Historical 2023 tech/data postings across 10 African & MENA countries. This demo uses synthetic data only.")
            frame(page, ".dataset-strip", 130)

            at(12, "01 / UPLOAD → PREVIEW → REVIEW · 12–30s", "Choose a synthetic PDF. File processing requires consent; uploading creates an editable text preview.")
            frame(page, ".upload-card", 55)
            page.locator("#cv-file").set_input_files(file_payload())
            page.locator("#upload-consent").check()
            frame(page, ".upload-card", 55)
            page.wait_for_timeout(1200)
            result["preview"] = click_response(page, "#upload", "/api/upload")
            expect(page.locator("#cv")).to_have_value(SYNTHETIC)
            expect(page.locator("#consent")).not_to_be_checked()
            frame(page, "#cv", 240)
            at(20, "REVIEW FIRST. EXTRACT SECOND.", "Review the actual preview, then give separate consent to find skills. CV text is never sent to Groq.")
            page.locator("#cv").fill(SYNTHETIC + " Reviewed synthetic summary.")
            page.locator("#consent").check()
            frame(page, "#cv", 70)
            page.screenshot(path=str(ARTIFACTS / "njia-demo-upload.png"))
            page.wait_for_timeout(1200)
            result["extraction"] = click_response(page, "#extract", "/api/extract")
            expect(page.locator("#skill-count")).to_have_text("3")
            frame(page, "#skill-chips", 360)
            at(26, "CONFIRM YOUR SKILLS", "SQL, Excel and Power BI were found by server-side keyword matching. Review the chips before analysis.")

            at(30, "02 / YOUR SKILL GAP · 30–45s", "Find my path counts demand in the selected market. Coverage describes skill mentions, not hiring odds.")
            result["analysis"] = click_response(page, "#analyze", "/api/analyze")
            frame(page, "#overview", 40)
            page.wait_for_timeout(2500)
            at(36, "COUNTS, GAPS & HISTORICAL EXAMPLES", "The chart shows requested skills. Historical job examples use TF-IDF and cosine similarity, not generative AI.")
            frame(page, "#overview .panel-card", 50)
            at(41, "CURATED IS THE DEFAULT", "Leave remote-AI consent unchecked: the app builds a four-week curated plan without a language model.")
            page.locator('[data-tab="plan"]').click()
            expect(page.locator("#ai-consent")).not_to_be_checked()
            result["curated_plan"] = click_response(page, "#generate-plan", "/api/plan")
            assert result["curated_plan"]["mode"] == "curated"
            expect(page.locator("#plan .tiny-badge")).to_have_text("Curated plan")
            frame(page, "#plan", 45)

            at(45, "03 / OPTIONAL AI COACHING · 45–64s", "The current result is labelled Curated plan. Now explicitly opt in to share structured curriculum with Groq.")
            page.locator("#new-plan").click()
            frame(page, "#plan", 35)
            expect(page.locator("#ai-consent")).not_to_be_checked()
            page.wait_for_timeout(1500)
            page.locator("#ai-consent").check()
            frame(page, "#plan", 35)
            at(49, "LIVE REQUEST / GROQ", "Generate coaching through the actual API. Only skills and curriculum are shared; the CV is excluded.")
            reserve_ai_call("record_demo")
            ai_start = time.monotonic()
            result["ai_plan"] = click_response(page, "#generate-plan", "/api/plan", timeout=12000)
            result["ai_elapsed_seconds"] = round(time.monotonic() - ai_start, 3)
            assert result["ai_plan"]["mode"] == "groq", result["ai_plan"]["note"]
            expect(page.locator("#plan .tiny-badge")).to_have_text("AI coaching · Groq")
            frame(page, "#plan", 35)
            at(55, "AI COACHING · GROQ / VERIFIED RESPONSE", "The returned plan is labelled AI coaching · Groq. Review the suggestions; demand figures and links stay grounded.")
            page.screenshot(path=str(ARTIFACTS / "njia-demo-ai.png"))
            at(59, "SMALL STEPS. TANGIBLE EVIDENCE.", "Each week includes practice, a resource and a deliverable. Mark progress for this session only.")
            page.locator('[data-week="1"]').check()
            expect(page.locator("#progress")).to_have_text("1")
            frame(page, "#plan .week-card", 45)

            at(64, "04 / PRACTICE & EVIDENCE · 64–80s", "Try SQL fundamentals: three fixed questions, graded by an answer key. This is practice, not certification.")
            page.locator('[data-tab="practice"]').click()
            page.locator("#practice-skill").select_option("sql")
            result["assessment"] = click_response(page, "#start-practice", "/api/assessment/sql")
            frame(page, "#practice-form", 50)
            for i, answer in enumerate((1, 2, 0)):
                page.locator(f'input[name="q{i}"][value="{answer}"]').check()
                frame(page, f'input[name="q{i}"][value="{answer}"]', 320)
                page.wait_for_timeout(1100)
            at(71, "SELF-REVIEW, THEN CHECK", "Add a reflection for a mentor. It stays in page memory and is not AI-graded or sent with the answers.")
            page.locator("#reflection").fill("I would check duplicates and NULL values before trusting a sales total.")
            frame(page, "#reflection", 280)
            page.wait_for_timeout(1000)
            result["grade"] = click_response(page, '#practice-form button[type="submit"]', "/api/assessment/grade")
            assert result["grade"]["correct"] == 3
            frame(page, "#practice .panel-card", 40)
            at(76, "TAKE YOUR EVIDENCE WITH YOU", "See the real answer-key feedback, then download a local report with your plan, practice and limitations.")
            frame(page, "#practice .feedback", 90)
            with page.expect_download() as pending:
                page.get_by_role("button", name="Download my evidence report").click()
            pending.value.save_as(str(ARTIFACTS / "njia-demo-evidence.md"))
            frame(page, "#practice .feedback", 90)

            at(80, "LIMITATIONS & NEXT STEPS · 80–90s", "Not live vacancies or hiring odds. Keyword matching can miss context. Next: practise, build a project, consult a mentor.")
            # Exercise two real failure states rather than drawing error messages.
            page.locator("#cv-file").set_input_files(file_payload("rtf", b"{\\rtf1 synthetic}"))
            page.locator("#upload").click()
            expect(page.locator("#upload-status")).to_contain_text("Choose a PDF, DOCX or TXT")
            frame(page, ".upload-card", 35)
            at(83, "FILE LIMITS / ACTIONABLE FEEDBACK", "PDF, DOCX or UTF-8 TXT only, up to 4 MB. The real form rejects this unsupported file before sending it.")
            page.wait_for_timeout(1000)
            page.locator("#cv-file").set_input_files(file_payload("pdf", make_pdf(image_only=True), "synthetic-scan.pdf"))
            page.locator("#upload-consent").check()
            result["scan_failure"] = click_response(page, "#upload", "/api/upload", status=422)
            expect(page.locator("#upload-status")).to_contain_text("OCR")
            frame(page, ".upload-card", 25)
            at(86, "SCANS NEED OCR / YOUR NEXT STEP", "The API cannot read an image-only PDF: use OCR or paste text. Review your evidence, then discuss it with a mentor.")
            page.wait_for_timeout(max(0, started + 91 - time.monotonic()) * 1000)
            assert not audit.errors, audit.errors
            assert sum(r.get("json", {}).get("use_ai") is True for r in audit.requests if r["path"] == "/api/plan") == 1
            result["status"] = "recorded"
        except Exception as error:
            result["status"], result["error"] = "failed", str(error)
            page.screenshot(path=str(ARTIFACTS / "njia-demo-failure.png"))
            raise
        finally:
            result.update(requests=audit.requests, responses=audit.responses, javascript_errors=audit.errors)
            context.close()
            video.save_as(str(raw))
            video.delete()
            browser.close()
            save_json("njia-demo-results.json", result)
    result["video"] = finalize(raw, ARTIFACTS / "njia-demo-90s.webm", ffmpeg, ffprobe)
    result["status"] = "passed"
    save_json("njia-demo-results.json", result)
    print(json.dumps({"status": result["status"], "video": "artifacts/njia-demo-90s.webm", "duration": result["video"]["duration_seconds"], "ai_mode": result["ai_plan"]["mode"]}, indent=2))


if __name__ == "__main__":
    main()
