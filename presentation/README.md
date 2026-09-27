# Njia — Team Dhruzzz

Local eight-slide final deck in navy, ivory and orange: **Ask. Match. Practise. Your next move.** The PPTX contains
editable text, shapes, chart bars and phone-flow illustrations; all slides include speaker
notes. The PDF is printed from the matching local HTML with Chromium/Playwright. No network
assets or model calls are required to build these files.

## Deliverables
- `Njia-Dhruzzz.pptx` — editable presentation, 8 slides.
- `Njia-Dhruzzz.pdf` — searchable PDF, 8 pages.
- `Njia-Dhruzzz.html` — matching printable HTML.
- `speaker-notes.md` — presentation narration and supporting qualifications.
- `contact-sheet.png` and `slide-01.png` … `slide-08.png` — visual previews.
- `data-evidence.json` — locally recalculated denominators and chart values.
- `production-evidence.json` — every tested or observed figure used in the deck.
- `validation.json` — file sizes and structural validation results.

## Product story
Njia asks before it advises: after the CV it asks a few follow-up questions whose answers
reshape suggested skills and the brief. It matches the learner to live jobs they can apply
for, with a skill-match % (skill overlap, not a hiring probability), and supports interview
practice with source-linked questions from the web and AI feedback on typed answers. Web
searches receive only role, country and skill names — never CV text. JSON coaching calls can
fall back from Groq to the NVIDIA API Catalog on the same `openai/gpt-oss-20b` model, with
actual-provider labels. Web research uses Groq `openai/gpt-oss-120b` browser search and has no
NVIDIA search backup. Provider failures ultimately return labelled curated or deterministic output.

## Unit-test evidence (separate from browser assertions)
126 backend test methods passed (main implementation owner confirmation, 27 september 2026; separate unit-test suite), distinct from
57 public assertions: 48 acceptance + 9 recording.
Those 57 public assertions are earlier-release evidence, not a new acceptance run.
Real Groq / openai/gpt-oss-20b: 2.259s desktop, 1.318s mobile, 2.260s recording including PDF.
Individual observations, not a performance benchmark. 0 JavaScript errors in these runs.
Sample: 391 historical Kenya Data Analyst postings, 39.6% demand-weighted coverage, not hiring odds.
New features: 8 remote + 3 local job cards shown; 8 source-linked interview questions; 19 new recording checks passed.
See `production-evidence.json` for the precise count breakdown and unverified fields.

## New public recording (27 September 2026)
**19 checks passed**, separate from the earlier 57 public assertions and 126 owner-reported unit tests.
Actual provider: **Groq / openai/gpt-oss-20b** for follow-ups, brief and feedback.
Observed: **1.271s PDF + follow-ups; 1.450s brief; 0.844s feedback**. Feedback score: **4/5**.
Rendered **8 remote + 3 local job cards**, plus **8 web-sourced interview questions** via Groq
`openai/gpt-oss-120b`. Exactly **90.000 seconds**, 1×, silent captions, no late cues or JavaScript errors.
No mocked responses. NVIDIA **API Catalog**, not Brev, is the configured same-model backup;
it was not exercised in this recording. Local replacement is ready; main handles release upload.

CV rewrites checked for numbers/tools, still require human factual review. An earlier recording
contained unsupported “real-time sales monitoring”; the latest added unsupported inventory decisions
to a personal synthetic-data dashboard. The checks do not guarantee
semantic factuality. Rewrites that use the learner's own answers are labelled for verification.
The deck's before/after example is illustrative and hand-authored.

## Published demo
The published `demo-v1` recording is exactly 90 seconds. Slide 8 links to it:
https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/njia-demo-90s.mp4

The published recording shows the updated coach journey.

Illustrative persona, CV output and phone panels are explicitly labeled. The pilot is a plan,
not adoption. The priority dataset is a 2023 historical sample, not current vacancies. CV
transfer to AI requires opt-in and basic, best-effort PII redaction; there is no application
database persistence claim beyond the application itself.

## Rebuild locally (from project root)
```bash
.venv/bin/python scripts/build_final_deck.py --all
.venv/bin/python scripts/build_final_deck.py --all --out /tmp/opencode/deck
```
On Windows use `.venv\Scripts\python.exe`. `--all` builds the PPTX/HTML, renders the PDF and
PNG previews with Playwright, then validates. Update `EVIDENCE` in
`scripts/build_final_deck.py` before rebuilding. The builder writes only inside `--out`
(default `presentation/`).
