# Njia — Team Dhruzzz

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
