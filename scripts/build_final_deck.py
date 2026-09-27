"""Local-only Njia deck builder. No API calls, credentials, or remote assets.

Build:    python scripts/build_final_deck.py
PDF:      .venv/Scripts/python.exe scripts/build_final_deck.py --render-only
Validate: python scripts/build_final_deck.py --validate
Only writes inside presentation/. PPTX and HTML share the same design objects.
"""
from pathlib import Path
import argparse
import collections
import html
import json
import math

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "presentation"
STEM = "Njia-Dhruzzz"
NAVY = "14283F"
IVORY = "F7F4EC"
ORANGE = "F27B43"
INK = "1B2D40"
MUTED = "586777"
PALE = "D4DEE6"
LINE = "DDDCD5"
WHITE = "FFFFFF"
LIGHT = "FFF0E5"
GREEN = "246855"
SLIDES = []


def box(s, x, y, w, h, fill, radius=0, stroke=None):
    s["items"].append(dict(kind="box", x=x, y=y, w=w, h=h,
                           fill=fill, radius=radius, stroke=stroke))


def text(s, value, x, y, w, h, size=27, color=None, bold=False,
         serif=False, align="left", link=None):
    s["items"].append(dict(kind="text", text=value, x=x, y=y, w=w, h=h,
                           size=size, color=color or s["fg"], bold=bold,
                           serif=serif, align=align, link=link))


def slide(kicker, title, subtitle=None, dark=False, notes=""):
    n = len(SLIDES) + 1
    s = dict(items=[], dark=dark, bg=NAVY if dark else IVORY,
             fg=IVORY if dark else INK, notes=notes, title=title)
    SLIDES.append(s)
    box(s, 72, 54, 38, 5, ORANGE)
    text(s, kicker.upper(), 129, 40, 1320, 31, 19, ORANGE if dark else MUTED, True)
    text(s, title, 72, 109, 1456, 150, 65, bold=True, serif=True)
    if subtitle:
        text(s, subtitle, 75, 275, 1440, 70, 26, PALE if dark else MUTED)
    box(s, 72, 838, 1456, 1, "385065" if dark else LINE)
    text(s, "NJIA  /  DHRUZZZ  /  KENYA · ONLINE", 74, 853, 1100, 25, 16,
         PALE if dark else MUTED)
    text(s, f"{n:02d} / 08", 1400, 851, 128, 28, 18,
         PALE if dark else MUTED, align="right")
    return s


def label(s, value, x, y, w=600, color=ORANGE):
    text(s, value.upper(), x, y, w, 32, 19, color, True)


def build_content():
    acceptance = json.loads((ROOT / "artifacts/coach-acceptance-results.json").read_text(encoding="utf-8"))
    recording = json.loads((ROOT / "artifacts/njia-coach-demo-results.json").read_text(encoding="utf-8"))
    assert acceptance["passed"] == 48 and recording["passed"] == 9
    assert all(c["passed"] for c in acceptance["checks"] + recording["checks"])
    assert recording["video"]["duration_seconds"] == 90
    assert not recording["javascript_errors"]
    for flow in acceptance["flows"].values():
        assert not flow["javascript_errors"]
        assert flow["response"]["advisor"]["mode"] == "groq"
        assert flow["response"]["advisor"]["model"] == "openai/gpt-oss-20b"
    (OUT / "production-evidence.json").write_text(json.dumps({
        "backend_tests_passed": 72, "backend_count_source": "Main implementation owner confirmation",
        "public_acceptance_assertions": 48, "recording_assertions": 9, "public_total": 57,
        "provider": "Groq", "model": "openai/gpt-oss-20b",
        "observed_seconds": {"desktop": 2.259, "mobile": 1.318, "recording_with_pdf": 2.260},
        "javascript_errors": 0, "sample_size": 391, "coverage": 39.6,
        "video_seconds": 90, "source_artifacts": ["artifacts/coach-acceptance-results.json", "artifacts/njia-coach-demo-results.json"],
        "factual_limit": "Observed unsupported real-time sales monitoring in a rewrite; human factual review required."
    }, indent=2), encoding="utf-8")
    rows = [json.loads(line) for line in
            (ROOT / "data/africa_jobs_subset.jsonl").read_text(encoding="utf-8").splitlines() if line]
    ke = [r for r in rows if r["job_country"] == "Kenya"]
    da = [r for r in ke if r["job_title_short"] == "Data Analyst"]
    countries = len({r["job_country"] for r in rows})
    assert (len(rows), countries, len(ke), len(da)) == (18371, 10, 1326, 391)
    counts = collections.Counter(skill for r in da for skill in set(r["skills"]))
    skills = ["sql", "python", "r", "excel", "spss"]
    demand = sorted([(skill, round(counts[skill] / len(da) * 100, 1)) for skill in skills], key=lambda item: -item[1])

    s = slide("01  /  The Kenyan learner", "A CV tells your past.\nNjia helps choose your next step.", dark=True,
              notes="Njia means path in Swahili. We are Dhruzzz, a Kenya ONLINE team. Wanjiru is an illustrative persona, not an interviewed user. The working production advisor connects CV evidence to historical country-and-role demand, suggested CV rewrites and a seven-day plan. Public desktop, mobile and recording runs used real Groq inference; the evidence is summarized on slide 6.")
    text(s, "AI career guidance grounded in your CV\nand the skills your target market asks for.", 76, 295, 920, 105, 34, PALE)
    label(s, "THE LEARNER'S THREE QUESTIONS", 76, 461)
    for y, n, heading, sub in [
        (518, "01", "What can I already show?", "Find strengths backed by actual CV excerpts."),
        (612, "02", "What should I work on first?", "Prioritize skills using Kenya + target-role data."),
        (706, "03", "What can I do this week?", "Leave with clearer CV bullets and concrete practice.")]:
        text(s, n, 76, y, 55, 45, 27, ORANGE, True)
        text(s, heading, 148, y, 790, 42, 29, IVORY, True)
        text(s, sub, 148, y + 42, 800, 39, 23, PALE)
    box(s, 1050, 300, 478, 481, "203A52", 18)
    text(s, "W", 1092, 328, 130, 120, 90, ORANGE, serif=True)
    label(s, "ILLUSTRATIVE PERSONA", 1095, 465, 380, PALE)
    text(s, "Wanjiru\nNairobi · aspiring data analyst", 1095, 511, 388, 112, 31, IVORY, True)
    text(s, "Has project experience.\nNeeds a credible CV and\na focused learning plan.", 1095, 649, 389, 107, 26, PALE)

    s = slide("02  /  The product upgrade", "From a vague bullet to a useful next move.",
              "One assessment: evidence-grounded strengths, demand priorities, suggested rewrites and interview practice.",
              notes="This is a hand-authored illustration of the intended assessment output, not a captured model response. Both bullets use the same facts: cleaned sales data in Excel and built weekly charts. There is no invented business impact, percentage or credential. The SQL recommendation is an illustrative gap when SQL is not evidenced in the CV; absence of CV evidence does not mean absence of ability. The current upgrade adds a tailored seven-day action plan and interview question.")
    for x, w, fill in [(74, 660, WHITE), (774, 754, NAVY)]:
        box(s, x, 375, w, 242, fill, 14)
    label(s, "BEFORE / SUPPLIED CV FACTS", 104, 400, 580, MUTED)
    text(s, '“Cleaned sales data in Excel\nand made weekly charts.”', 104, 451, 580, 113, 37, INK, serif=True)
    label(s, "AFTER / HUMAN-REVIEWED EXAMPLE", 808, 400, 680)
    text(s, '“Prepared weekly sales charts in Excel\nusing cleaned sales data.”', 808, 451, 677, 113, 36, IVORY, serif=True)
    for x, heading, detail in [
        (74, "01 / Strength", "Excel data preparation, supported\nby the learner's own CV excerpt."),
        (571, "02 / Priority", "If SQL is not evidenced, start with\na JOIN and a checked summary."),
        (1068, "03 / Action", "A seven-day plan plus a tailored\ninterview question and rubric.")]:
        box(s, x, 653, 455, 4, ORANGE)
        text(s, heading, x, 680, 455, 43, 28, INK, True)
        text(s, detail, x, 732, 455, 72, 24, MUTED)
    text(s, "CV rewrites checked for numbers/tools, still require human factual review. Example below is illustrative.", 76, 336, 1440, 28, 18, MUTED)

    s = slide("03  /  Local data, visible denominators", "Better priorities start with local context.",
              "Historical skill mentions inform the advice; the language model does not invent demand figures.",
              notes="The chart is recalculated directly from data/africa_jobs_subset.jsonl. The full subset has 18,371 postings across ten countries, including 1,326 Kenyan postings across roles. The denominator for this chart is 391 Kenya Data Analyst postings. A posting may mention several skills, so the bars are not parts of a total. Source: Hugging Face lukebarousse/data_jobs, Apache-2.0, 2023. This is a historical job-posting sample, not live hiring demand or a representative census of Kenya's labor market.")
    for x, big, caption in [(76, "18,371", "2023 postings in the subset"),
                             (573, "10", "countries represented"),
                             (1070, "1,326", "Kenya postings · all roles")]:
        text(s, big, x, 364, 450, 82, 68, INK, True, True)
        text(s, caption, x, 453, 455, 35, 23, MUTED)
    label(s, "KENYA / DATA ANALYST / n = 391", 76, 530, 850, INK)
    for i, (skill, pct) in enumerate(demand):
        y = 580 + i * 40
        text(s, {"sql": "SQL", "python": "Python", "r": "R", "excel": "Excel", "spss": "SPSS"}[skill],
             76, y - 2, 132, 35, 24, INK, True)
        box(s, 217, y + 1, 575, 23, "E7E6DF", 3)
        box(s, 217, y + 1, 575 * pct / 50, 23, ORANGE if skill == "sql" else NAVY, 3)
        text(s, f"{pct:.1f}%", 810, y - 4, 110, 36, 24, INK, True)
    box(s, 985, 527, 543, 242, LIGHT, 12)
    text(s, "A direction, not a prediction.", 1017, 555, 480, 84, 37, INK, True, True)
    text(s, "Share of sampled posts mentioning each skill.\nMultiple skills can appear in one posting.\n2023 sample; not current vacancies.", 1017, 653, 477, 93, 23, MUTED)
    text(s, "Source: Hugging Face · lukebarousse/data_jobs · Apache-2.0 · 2023", 76, 795, 1400, 26, 17, MUTED,
         link="https://huggingface.co/datasets/lukebarousse/data_jobs")

    s = slide("04  /  AI architecture & relevance", "Ground the facts. Personalize the next step.",
              "AI interprets experience and writes tailored guidance; deterministic code supplies the market evidence.", dark=True,
              notes="Public production desktop, mobile and recording runs confirmed Groq, openai/gpt-oss-20b. User opts in before CV text is sent to the external AI provider, after basic PII redaction. Redaction is best-effort rather than full anonymization. There is no application database persistence of the CV; this does not make a provider-retention claim. The advisor validates output shape, supported skill IDs and source quotes, and checks newly introduced numbers/tools in rewrites. These checks do not prove semantic factuality: the recorded rewrite added unsupported real-time sales monitoring. Human factual review remains necessary. Rules-based guidance is the fallback when the model is unavailable or output is rejected.")
    steps = [
        ("01", "CV + consent", "Country + target role\nBasic PII redaction\nOpt-in before AI transfer"),
        ("02", "Grounding", "CV evidence excerpts\nAllowed skill vocabulary\nFixed 2023 demand data"),
        ("03", "AI advisor", "Groq-hosted inference\nopenai/gpt-oss-20b\nStructured JSON output"),
        ("04", "Checked advice", "Schema + quote checks\nRewrite number/tool checks\nStrengths → plan → practice")]
    for i, (n, heading, detail) in enumerate(steps):
        x = 76 + i * 370
        box(s, x, 379, 344, 270, "203A52", 12)
        text(s, n, x + 25, 402, 285, 64, 44, ORANGE, True, True)
        text(s, heading, x + 25, 477, 294, 45, 31, IVORY, True)
        text(s, detail, x + 25, 535, 297, 102, 23, PALE)
        if i < 3:
            text(s, "→", x + 344, 480, 28, 50, 27, ORANGE, True, align="center")
    box(s, 76, 681, 1452, 118, "29435B", 10)
    label(s, "RESILIENT BY DESIGN", 105, 701, 380)
    text(s, "Model unavailable or output rejected → rules-based guidance", 520, 698, 975, 37, 26, IVORY, True)
    text(s, "Best-effort PII redaction · CV text sent to AI only with opt-in · no application database persistence",
         105, 751, 1385, 30, 21, PALE)

    s = slide("05  /  Phone-first workflow", "A career next step, from a phone browser.",
              "Public desktop + 390 × 844 mobile-browser checks passed. Editable panels below illustrate the journey.",
              notes="These phone panels are code-native illustrations, not screenshots. The new public mobile flow passed at 390 by 844 with real Groq output, no horizontal overflow and no JavaScript errors. The flow covers consent, CV strengths, historical market priorities, a seven-day plan, an interview question and a downloadable HTML brief. The real sample returned 39.6% demand-weighted coverage over 391 Kenya Data Analyst postings; this is not hiring probability. Desktop returned three rewrites; mobile returned an honest empty rewrite list. No app install is required.")
    for i, (heading, subtitle) in enumerate([("01 / Give context", "CV + role + permission"),
                                             ("02 / Read the evidence", "Strengths + local priorities"),
                                             ("03 / Take action", "Plan + interview practice")]):
        x = 78 + i * 495
        text(s, heading, x, 361, 455, 40, 30, INK, True)
        text(s, subtitle, x, 407, 455, 35, 23, MUTED)
        px = x + 46
        box(s, px, 462, 354, 343, NAVY, 24)
        box(s, px + 11, 474, 332, 318, WHITE, 16)
        box(s, px + 137, 480, 80, 6, NAVY, 3)
        text(s, "njia", px + 28, 496, 288, 37, 29, INK, True, True)
        if i == 0:
            label(s, "YOUR NEXT ROLE", px + 28, 549, 280, MUTED)
            text(s, "Kenya  /  Data Analyst", px + 28, 586, 295, 33, 23, INK, True)
            box(s, px + 26, 631, 302, 68, IVORY, 6)
            text(s, "Paste or upload your CV", px + 39, 652, 270, 31, 21, MUTED)
            text(s, "Opt in to send CV text to AI", px + 28, 714, 292, 32, 19, MUTED)
            box(s, px + 26, 753, 302, 28, ORANGE, 5)
            text(s, "Assess my CV", px + 30, 755, 294, 25, 18, NAVY, True, align="center")
        elif i == 1:
            label(s, "EVIDENCE IN YOUR CV", px + 28, 549, 295, MUTED)
            text(s, "Excel data preparation", px + 28, 588, 296, 35, 24, INK, True)
            text(s, '“Cleaned sales data in Excel”', px + 28, 632, 290, 61, 21, MUTED)
            box(s, px + 26, 707, 302, 67, LIGHT, 6)
            text(s, "Next: practise a SQL JOIN\nSQL mentioned in 46.5%*", px + 39, 717, 277, 56, 20, INK)
        else:
            label(s, "YOUR SEVEN-DAY PLAN", px + 28, 549, 292, MUTED)
            text(s, "Day 1  /  Review CV evidence\nDay 2  /  Build a SQL exercise\nDay 3  /  Check edge cases", px + 28, 590, 296, 106, 21, INK)
            box(s, px + 26, 709, 302, 66, LIGHT, 6)
            text(s, "Interview practice\nHow do you check duplicates?", px + 38, 718, 283, 56, 18, INK)
    text(s, "*Kenya Data Analyst, 2023; n = 391. Tested sample: 39.6% demand-weighted coverage, not hiring odds. Panels illustrative.", 76, 811, 1440, 24, 16, MUTED)

    s = slide("06  /  Evidence & honest limits", "A working product. Evidence you can inspect.",
              "Real public Groq calls · synthetic CVs · strengths, rewrites, seven-day plans and tailored interview questions.",
              notes="Main implementation owner confirms 72 passing backend unit-test methods. Separately, coach-acceptance-results.json records 48 passing public acceptance assertions and njia-coach-demo-results.json records nine passing recording assertions, totaling 57 new public assertions. No mocked responses. Desktop, mobile and recording used Groq openai/gpt-oss-20b. Observed elapsed times were 2.259 seconds desktop, 1.318 mobile and 2.260 recording including PDF processing; these are individual observations, not a latency benchmark. All three runs recorded no JavaScript errors and all observed API responses succeeded. The sample used 391 Kenya Data Analyst postings and returned 39.6% demand-weighted coverage, not hiring odds. Recording is exactly 90 seconds at normal speed. Semantic factuality is not guaranteed: the recorded rewrite added unsupported real-time sales monitoring, despite number/tool checks. Human review is required. No real-user adoption or employment impact is claimed.")
    box(s, 76, 372, 666, 241, NAVY, 12)
    label(s, "PASSED / TWO DISTINCT TEST LAYERS", 106, 395, 600, PALE)
    text(s, "72", 106, 443, 270, 98, 82, IVORY, True, True)
    text(s, "57", 435, 443, 270, 98, 82, ORANGE, True, True)
    text(s, "backend tests", 110, 549, 290, 36, 25, PALE)
    text(s, "public assertions", 439, 547, 276, 33, 24, PALE)
    text(s, "48 acceptance + 9 recording", 439, 583, 278, 25, 18, PALE)
    box(s, 780, 372, 748, 241, LIGHT, 12)
    label(s, "LIVE GROQ / OBSERVED RESPONSE TIMES", 812, 395, 680, INK)
    text(s, "2.259s desktop  /  1.318s mobile\n2.260s recording, including PDF processing\n0 JavaScript errors across these runs",
         812, 451, 678, 110, 27, INK)
    text(s, "Individual observations, not a performance benchmark.", 812, 580, 678, 27, 20, MUTED)
    for x, head, body in [
        (76, "Data", "2023 sample, uneven country coverage.\nNot live vacancies or hiring probabilities."),
        (573, "Human factual review", "Numbers/tools checked; unsupported\nbusiness-impact claims can still slip through."),
        (1070, "Impact", "No measured employment outcomes\nor real-user adoption claimed.")]:
        text(s, head, x, 667, 452, 43, 30, INK, True, True)
        text(s, body, x, 727, 456, 72, 23, MUTED)

    s = slide("07  /  Adoption plan & award fit", "Start small. Measure a useful next step.",
              "Proposed pilot with Kenyan learners and a training partner — recruitment has not started.",
              notes="This is a proposed pilot, not adoption or a signed partnership. We propose recruiting ten Kenyan learners with one training partner, reviewing outputs with a facilitator and following up after seven days. Measure completion, factual rewrite acceptance, saved practice artifacts, usefulness and mobile friction; do not present target outcomes as achieved. Click Mobile fit is the practical mobile-first Kenyan learner journey, with Dhruzzz participating as Kenya ONLINE. Published Kenya-only scope aligns with the team context; final award eligibility is determined by organizers. Brightest fits skills and employability, and Artefact fits visible use of local data and AI. No award win or organizer endorsement is claimed.")
    for i, (tag, title, desc) in enumerate([
        ("RECRUIT", "10 learners + 1 partner", "Invite Kenyan career starters.\nObserve the mobile CV journey."),
        ("REVIEW", "Human-check the advice", "Check whether rewrites preserve facts\nand priorities are understandable."),
        ("FOLLOW UP", "Return after 7 days", "Count completed practice artifacts.\nAsk what helped and what blocked progress.")]):
        x = 76 + i * 497
        label(s, tag, x, 387, 455, MUTED)
        box(s, x, 433, 452, 4, ORANGE)
        text(s, title, x, 465, 454, 78, 33, INK, True, True)
        text(s, desc, x, 560, 455, 97, 24, MUTED)
    box(s, 76, 687, 1452, 117, NAVY, 12)
    label(s, "CLICK MOBILE / KENYA ONLINE", 108, 708, 570)
    text(s, "Mobile-first guidance for Kenyan learners.", 680, 706, 805, 38, 28, IVORY, True)
    text(s, "Award fit: practical phone-browser access · also aligned with Brightest (employability) and Artefact (Data & AI).",
         108, 757, 1384, 28, 20, PALE)

    s = slide("08  /  Team Dhruzzz", "Turn experience into a clearer path.", dark=True,
              notes="Close with the live product and source repository. Team: Eeshan Vaghjiani, Bhavin Mepani and Dhruvin Bhudia; Kenya ONLINE. The new recorded production demo is verified locally at exactly 90 seconds, normal speed, with captions. Slide 8 links to the expected demo-v1 release asset njia-demo-90s.webm; upload of the updated asset is pending confirmation. Ask for a Kenyan learner or training partner to run the proposed pilot.")
    text(s, "Njia", 76, 281, 680, 133, 109, IVORY, True, True)
    text(s, "Your evidence. Your market. Your next seven days.", 80, 425, 1415, 69, 39, ORANGE, serif=True)
    label(s, "KENYA · ONLINE", 80, 532, 600, PALE)
    text(s, "Eeshan Vaghjiani\nBhavin Mepani\nDhruvin Bhudia", 80, 582, 620, 155, 34, IVORY)
    box(s, 794, 529, 734, 269, "203A52", 12)
    for y, tag, display, url in [
        (552, "LIVE", "gomycode-2026.vercel.app", "https://gomycode-2026.vercel.app"),
        (626, "SOURCE", "github.com/Eeshan-Vaghjiani/njia", "https://github.com/Eeshan-Vaghjiani/njia"),
        (700, "90-SECOND DEMO", "njia-demo-90s.webm · release upload pending", "https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/njia-demo-90s.webm")]:
        label(s, tag, 827, y, 630)
        text(s, display, 827, y + 30, 669, 38, 22 if tag == "90-SECOND DEMO" else 24, IVORY, link=url)
    text(s, "Pilot invitation: Kenyan learners + training partners", 80, 768, 690, 37, 24, PALE)
    return dict(total_postings=len(rows), countries=countries, kenya_postings=len(ke),
                kenya_data_analyst_postings=len(da), chart=dict(demand))


def make_pptx():
    from pptx import Presentation
    from pptx.dml.color import RGBColor
    from pptx.enum.shapes import MSO_SHAPE
    from pptx.enum.text import PP_ALIGN
    from pptx.util import Inches, Pt
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(16), Inches(9)
    prs.core_properties.title = "Njia — Team Dhruzzz"
    prs.core_properties.subject = "Evidence-grounded career guidance for Kenyan learners"
    prs.core_properties.author = "Team Dhruzzz"
    prs.core_properties.keywords = "Njia, Kenya, Dhruzzz, career guidance, historical demand"
    for s in SLIDES:
        page = prs.slides.add_slide(prs.slide_layouts[6])
        page.background.fill.solid()
        page.background.fill.fore_color.rgb = RGBColor.from_string(s["bg"])
        for e in s["items"]:
            geometry = [Inches(e[k] / 100) for k in ("x", "y", "w", "h")]
            if e["kind"] == "box":
                sh = page.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if e["radius"] else MSO_SHAPE.RECTANGLE, *geometry)
                sh.fill.solid()
                sh.fill.fore_color.rgb = RGBColor.from_string(e["fill"])
                sh.line.fill.background()
                if e["radius"]:
                    sh.adjustments[0] = min(.3, e["radius"] / min(e["w"], e["h"]))
            else:
                sh = page.shapes.add_textbox(*geometry)
                tf = sh.text_frame
                tf.clear()
                tf.word_wrap = True
                tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
                for index, line in enumerate(e["text"].split("\n")):
                    p = tf.paragraphs[0] if index == 0 else tf.add_paragraph()
                    p.alignment = {"left": PP_ALIGN.LEFT, "right": PP_ALIGN.RIGHT, "center": PP_ALIGN.CENTER}[e["align"]]
                    p.line_spacing = 1.12
                    p.space_before = p.space_after = Pt(0)
                    r = p.add_run()
                    r.text = line
                    r.font.name = "Georgia" if e["serif"] else "Segoe UI"
                    r.font.size = Pt(e["size"] * .72)
                    r.font.bold = e["bold"]
                    r.font.color.rgb = RGBColor.from_string(e["color"])
                    if e["link"]:
                        r.hyperlink.address = e["link"]
        page.notes_slide.notes_text_frame.text = s["notes"]
    prs.save(OUT / f"{STEM}.pptx")


def make_html():
    fragments = []
    for index, s in enumerate(SLIDES):
        items = []
        for e in s["items"]:
            style = f'left:{e["x"]}px;top:{e["y"]}px;width:{e["w"]}px;height:{e["h"]}px;'
            if e["kind"] == "box":
                style += f'background:#{e["fill"]};border-radius:{e["radius"]}px;'
                items.append(f'<div class="shape" style="{style}"></div>')
            else:
                style += (f'font-size:{e["size"]}px;color:#{e["color"]};'
                          f'font-weight:{700 if e["bold"] else 400};text-align:{e["align"]};'
                          f'font-family:{"Georgia" if e["serif"] else "Segoe UI"};')
                body = html.escape(e["text"]).replace("\n", "<br>")
                if e["link"]:
                    body = f'<a href="{html.escape(e["link"])}">{body}</a>'
                items.append(f'<div class="text" style="{style}">{body}</div>')
        fragments.append(f'<section class="slide" aria-label="Slide {index+1}" style="background:#{s["bg"]}">{"".join(items)}</section>')
    document = '''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=1600"><title>Njia — Team Dhruzzz</title>
<style>@page{size:1600px 900px;margin:0}*{box-sizing:border-box}html,body{margin:0;padding:0}
body{background:#c9cccf}.slide{position:relative;width:1600px;height:900px;overflow:hidden;
break-after:page;page-break-after:always}.slide:last-child{break-after:auto;page-break-after:auto}
.shape,.text{position:absolute}.text{line-height:1.12;white-space:normal;overflow:visible}
a{color:inherit;text-decoration:none} @media print{body{background:white}
*{-webkit-print-color-adjust:exact;print-color-adjust:exact}}@media screen{.slide{margin:0 auto 24px}}</style>
</head><body>''' + "".join(fragments) + "</body></html>"
    (OUT / f"{STEM}.html").write_text(document, encoding="utf-8")


def render():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1600, "height": 900}, device_scale_factor=1)
        page.goto((OUT / f"{STEM}.html").as_uri(), wait_until="load")
        page.evaluate("document.fonts.ready")
        overflow = page.locator(".text").evaluate_all("""els => els.filter(e =>
            e.scrollHeight > e.clientHeight + 2 || e.scrollWidth > e.clientWidth + 2)
            .map(e => ({text:e.innerText, actual:[e.scrollWidth,e.scrollHeight],
            box:[e.clientWidth,e.clientHeight]}))""")
        if overflow:
            raise RuntimeError("Text overflow: " + json.dumps(overflow, ensure_ascii=False))
        for index, section in enumerate(page.locator(".slide").all()):
            section.screenshot(path=str(OUT / f"slide-{index+1:02d}.png"))
        page.emulate_media(media="print")
        page.pdf(path=str(OUT / f"{STEM}.pdf"), prefer_css_page_size=True,
                 print_background=True, display_header_footer=False)
        browser.close()
    print("Rendered 8 slide previews and PDF; HTML text-overflow check passed.")


def validate():
    import fitz
    from PIL import Image, ImageDraw
    from pptx import Presentation
    prs = Presentation(OUT / f"{STEM}.pptx")
    pdf = fitz.open(OUT / f"{STEM}.pdf")
    assert len(prs.slides) == len(pdf) == 8
    slide_text = "\n".join(shape.text for s in prs.slides for shape in s.shapes if shape.has_text_frame)
    pdf_text = "\n".join(p.get_text() for p in pdf)
    for value in ["Dhruzzz", "Eeshan Vaghjiani", "Bhavin Mepani", "Dhruvin Bhudia", "18,371", "1,326", "391", "57", "72", "39.6%", "2.259s", "1.318s", "2.260s"]:
        assert value.casefold() in slide_text.casefold(), value
        assert value.casefold() in pdf_text.casefold(), value
    for slide_index, s in enumerate(prs.slides):
        assert s.notes_slide.notes_text_frame.text.strip()
        for shape in s.shapes:
            assert shape.left >= 0 and shape.top >= 0
            assert shape.left + shape.width <= prs.slide_width + 10
            assert shape.top + shape.height <= prs.slide_height + 10
    for page in pdf:
        assert len(page.get_text()) > 200
        assert math.isclose(page.rect.width / page.rect.height, 16/9, abs_tol=.001)
    sheet = Image.new("RGB", (1280, 4 * 390), "#D4DEE6")
    draw = ImageDraw.Draw(sheet)
    for i, page in enumerate(pdf):
        pix = page.get_pixmap(matrix=fitz.Matrix(.5, .5), alpha=False)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        img.thumbnail((624, 351))
        x, y = (i % 2) * 640 + 8, (i // 2) * 390 + 27
        sheet.paste(img, (x, y))
        draw.text((x, y - 20), f"SLIDE {i+1:02d}", fill="#14283F")
    sheet.save(OUT / "contact-sheet.png")
    result = dict(pptx_slides=len(prs.slides), pdf_pages=len(pdf), aspect_ratio="16:9",
                  pptx_bytes=(OUT / f"{STEM}.pptx").stat().st_size,
                  pdf_bytes=(OUT / f"{STEM}.pdf").stat().st_size,
                  checks=["Slide/page count", "Required content in PPTX and PDF", "PPTX shape bounds",
                          "Speaker notes on all slides", "PDF searchable text", "PDF aspect ratio"],
                  advisor_validation="72 backend tests confirmed by main owner; 48 public acceptance + 9 recording assertions verified from artifacts; human factual review required")
    (OUT / "validation.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--render-only", action="store_true")
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    OUT.mkdir(exist_ok=True)
    if args.render_only:
        render()
        return
    if args.validate:
        validate()
        return
    evidence = build_content()
    assert len(SLIDES) == 8
    make_pptx()
    make_html()
    (OUT / "data-evidence.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    (OUT / "speaker-notes.md").write_text("# Njia — speaker notes\n\n" + "\n\n".join(
        f'## {i+1}. {s["title"].replace(chr(10), " ")}\n\n{s["notes"]}' for i, s in enumerate(SLIDES)), encoding="utf-8")
    (OUT / "README.md").write_text('''# Njia — Team Dhruzzz

Local eight-slide final deck in navy, ivory and orange. The PPTX contains editable text,
shapes, chart bars and phone-flow illustrations; all slides include speaker notes.
The PDF is printed from the matching local HTML with Chromium/Playwright. No network
assets or model calls are required to build these files.

## Deliverables
- `Njia-Dhruzzz.pptx` — editable presentation, 8 slides.
- `Njia-Dhruzzz.pdf` — searchable PDF, 8 pages.
- `Njia-Dhruzzz.html` — matching printable HTML.
- `speaker-notes.md` — presentation narration and supporting qualifications.
- `contact-sheet.png` and `slide-01.png` … `slide-08.png` — visual previews.
- `data-evidence.json` — locally recalculated denominators and chart values.
- `validation.json` — file sizes and structural validation results.

## Current production evidence
72 backend test methods passed (main implementation owner confirmation), distinct from
57 new public assertions: 48 acceptance + 9 recording, verified from the local JSON artifacts.
Real Groq / openai/gpt-oss-20b: 2.259s desktop, 1.318s mobile, 2.260s recording including PDF.
Individual observations, not a performance benchmark. No JavaScript errors in these runs.
Sample: 391 historical Kenya Data Analyst postings, 39.6% demand-weighted coverage, not hiring odds.
See `production-evidence.json` for sources and the precise count breakdown.

CV rewrites checked for numbers/tools, still require human factual review. The recording
contains unsupported “real-time sales monitoring” in a rewrite. The checks do not guarantee
semantic factuality. The deck's before/after example is illustrative and human-reviewed.

## Remaining release update
The new local demo is exactly 90 seconds. Upload/replace `njia-demo-90s.webm` in the
`demo-v1` GitHub release and verify the public asset URL. Slide 8 links to that exact
asset destination and labels the release upload pending. No production-validation update
is outstanding for the results stated in this deck.

Illustrative persona, CV output and phone panels are explicitly labeled. The pilot is a plan,
not adoption. The dataset is a 2023 historical sample, not current vacancies. CV transfer to
AI requires opt-in and basic, best-effort PII redaction; there is no application database
persistence claim beyond the application itself.

## Rebuild locally (from project root)
```powershell
python scripts/build_final_deck.py
.venv/Scripts/python.exe scripts/build_final_deck.py --render-only
python scripts/build_final_deck.py --validate
```
The builder writes only inside `presentation/`. Existing decks in the project root are untouched.
''', encoding="utf-8")
    print("Built editable 8-slide PPTX + matching HTML in presentation/.")
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
