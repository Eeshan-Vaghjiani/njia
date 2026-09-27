# Njia — final presentation outline

**8 slides · Dhruzzz · Kenya · ONLINE · 27 September 2026**

**Narrative:** a Kenyan learner moves from uncertain next steps to visible skill evidence and a practical weekly plan.

This outline replaces the older decks, which are **obsolete**. It is presentation copy and direction, not a generated or hosted deck. The required **90-second demo video is a separate deliverable**; no official slide count or separate presentation duration is specified.

**Checkpoint:** 57 unit tests passed; latest current-build desktop/mobile core and all five race checks passed, as did desktop PDF/DOCX/TXT upload and real Groq. Dedicated mobile TXT upload passed at **390×844, touch=True** in Chromium emulation through consent, preview, extraction, Kenya **39.6%** gap, four-week curated plan and Markdown download, with **0 model calls, 0 JavaScript errors** and no horizontal overflow at the analysis assertion. Mobile PDF/DOCX and physical-phone upload remain unverified. Source and exactly 90-second captioned video are published with anonymous access verified. Genuine user feedback remains pending. No current deck is generated: Felo needs an API key. Deployment awaits Vercel login; instructions have been provided.

## Design direction

- Use one message per slide, generous spacing, strong contrast and large type. Keep screenshots legible, cropped to the action being discussed.
- Use current application captures and simple editable diagrams. Distinguish **Implemented**, **Live-tested**, **Mock-tested** and **Verification ongoing** where relevant.
- Reuse the product's visual identity. Use one accent colour for the learner's next action and a restrained evidence strip for source/date/limitations.
- Keep detailed verification and disclosures in speaker notes or linked evidence. Keep the 2023-data label and distinguish single-run Groq latency from current browser-check results.

## Slide 1 — Your skills. Your market. Your path.

**On-slide copy**

> **Njia**
> Turn your skills into a practical next learning step.
>
> Dhruzzz · Kenya · ONLINE
> Eeshan Vaghjiani · Bhavin Mepani · Dhruvin Bhudia

**Visual:** one clean current product screenshot, with the learning action as the focal point.

**Speaker cue:** “We built Njia for Kenyan tech and data learners deciding what to learn next.” Frame this as the intended audience, not an established user base.

## Slide 2 — What should I learn next?

**On-slide copy**

- A target role is not yet a learning plan.
- Make skill-demand evidence visible and reviewable.
- Leave with one concrete activity and something to show.

**Visual:** three-step diagram: **My skills → Evidence → Next action**.

**Speaker cue:** Explain the problem hypothesis using a clearly labelled synthetic Kenya/Data Analyst example. Real Kenyan user feedback is pending; do not add a fabricated testimonial, survey statistic or unemployment-impact claim.

## Slide 3 — A complete path from skills to practice

**On-slide copy**

> **Confirm skills → Inspect gaps → Plan four weeks → Practice → Export evidence**

- Editable skill suggestions and manual entry.
- Resources, weekly deliverables and fixed practice checks.
- PDF / DOCX / TXT upload → editable preview → reviewed skills.

**Visual:** three tightly cropped current flow screenshots; desktop upload verification passed for all three formats. Use actual captures, not fabricated screenshots/output.

**Speaker cue:** Upload parses in app-server memory and returns text for review before skill extraction. The backend accepts up to **5 MiB**; the frontend caps files at **4,000,000 bytes** for Vercel request headroom. Scanned documents need external OCR. Manual skills remain available. Practice checks are learning feedback, not certification.

## Slide 4 — Evidence you can inspect

**On-slide copy**

> **391** Kenya Data Analyst postings
> **39.6%** example demand-weighted coverage
> **2023** historical data

- Example confirmed skills: Excel, SQL, Power BI.
- Corpus: 18,371 postings across ten African/MENA countries.
- Small local samples trigger an explicit broader-sample fallback.

**Visual:** current Kenya/Data Analyst demand bars with sample size and year visible.

**Speaker cue:** “Coverage is the share of top-15 skill mentions covered by this profile, not a hiring probability.” Counts are canonicalized. Historical retrieval is not live vacancy search; fewer than 50 local postings uses the role's combined ten-country sample.

## Slide 5 — Ground the evidence. Assist the coaching.

**On-slide copy**

| Evidence layer | Optional coaching layer |
| --- | --- |
| Rules + canonical skill counts | Groq curriculum wording |
| TF-IDF historical retrieval | Titles, activities, deliverables |
| Fixed resources and practice keys | Complete curated fallback |

> **Groq live-tested: `openai/gpt-oss-20b` · four-week plan · 2.27 s**
> Main workflow, 2026-09-27 · one observed run, not a benchmark.

**Visual:** browser → FastAPI → deterministic analysis/curated plan, with a separate optional Groq branch. Label that branch **Server-checked opt-in · structured curriculum only · no CV, identities or demand statistics**.

**Speaker cue:** The account model list did not offer the original `llama-3.3-70b-versatile`, so the default changed to the actual live-tested model `openai/gpt-oss-20b`. The app defaults to offline unless configured. `/api/plan` checks `use_ai`/`ai_consent` server-side; curated plans need no AI consent. Only allowlisted structured curriculum is sent, not CV text, identities, country/role or demand statistics. Statistics, targets, hours and resource links remain controlled by the app. Validated model wording still needs review; this live observation is not a quality evaluation. Ollama remains mock-tested only.

## Slide 6 — Reliability with visible limits

**On-slide copy**

- **17 / 20** exact skill sets on developer-authored synthetic examples.
- **0.9535 precision · 0.9762 recall** on that extraction check.
- **57 unittest methods passing**, reported by main workflow on 2026-09-27.
- Current desktop **1440×1100** / mobile **390×844** core checks and all **5** race checks passed.
- Desktop PDF/DOCX/TXT upload and real Groq passed; captioned demo published.
- Dedicated mobile TXT upload → curated plan → download passed (**390×844, touch=True**).

**Visual:** compact evidence card beside the current mobile TXT plan screenshot, local `artifacts/mobile-upload-plan.png`.

**Speaker cue:** The synthetic extraction set is not broad CV validation or a fairness audit. Its 0.97 ms warm median and zero inference calls/cost exclude parsing, startup, browser work, retrieval and generation. Current-build core Chromium checks recorded no JavaScript errors or external page requests. The dedicated mobile TXT check passed actual upload with consent, preview, extraction, Kenya 39.6% analysis, four curated weeks and Markdown download, with zero model calls/JavaScript errors and no horizontal overflow at analysis. This is touch-enabled Chromium emulation, not mobile PDF/DOCX or physical-phone verification. Groq's 2.27 seconds is one observed live-plan latency, not a benchmark; hosted cost is unmeasured.

**Evidence/reproduction:** local `artifacts/mobile-upload-results.json` and `artifacts/mobile-upload-plan.png`; with the local server running and Playwright installed, run `.\.venv\Scripts\python.exe scripts/mobile_upload_test.py` from the project root. See [LOCAL_TEST_RESULTS.md](LOCAL_TEST_RESULTS.md). `artifacts/` is Git-ignored; selected JSON evidence is planned for the [demo-v1 release](https://github.com/Eeshan-Vaghjiani/njia/releases/tag/demo-v1), where only attached assets are publicly downloadable.

## Slide 7 — Keep the learner in control

**On-slide copy**

- Review every suggested skill; manual entry is available.
- Uploads are processed in server memory; previews can contain personal data.
- Remote opt-in is server-checked; curated planning needs no AI consent.
- Hosted coaching receives structured curriculum, not CVs, identities or demand statistics.
- Historical demand and short quizzes do not prove employability.

**Visual:** current privacy notice and actual plan-mode label from verified app captures.

**Speaker cue:** On a public app, documents/text are processed on the hosting server, not the user's laptop or device. Basic redaction is not full anonymization, previews may contain personal data, and downloaded reports persist as user files. The report excludes raw CV text. Attribute the data to `lukebarousse/data_jobs`; the prepared licence statement is not independently verified provenance.

## Slide 8 — A useful next step, then real-world validation

**On-slide copy**

> **Next: Kenyan user feedback · capture provider fallback · extend mobile formats/phone checks**
>
> Primary application: **Brightest — Skills & Employability**
> Partner applications: **Brightest · Click Mobile · Artefact · Thunders**
>
> https://github.com/Eeshan-Vaghjiani/njia
> **[FINAL_PRESENTATION_URL]**
> https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/njia-demo-90s.webm

**Visual:** one strong current learning-plan deliverable, with readable links or QR codes generated only from the verified final URLs.

**Speaker cue:** Ask whether the plan helps a Kenyan learner choose and complete a useful next task. Award selections are recommendations, not guarantees. Source and video anonymous access are verified. Optional app link: **[FINAL_LIVE_APP_URL — PENDING VERCEL AUTHENTICATION]**. Felo export is blocked by a missing key; no current presentation is generated.

## Required 90-second demo video

Published on the [demo-v1 release](https://github.com/Eeshan-Vaghjiani/njia/releases/tag/demo-v1): `artifacts/njia-demo-90s.webm`, **exactly 90.000 seconds, 1280 × 720**. It records actual CV upload and real Groq `openai/gpt-oss-20b` at normal speed, silent with Playwright captions. Anonymous direct-asset HEAD returned **200**, **3,498,819 bytes**. See [DEMO.md](DEMO.md) for the walkthrough. A live provider-failure recording remains pending.

## Final presentation checks

- Add and verify the final presentation URL; source and video anonymous access are already verified.
- Keep the canonical **391 / 39.6% / 2023** example consistent. Do not import numbers or stronger claims from obsolete decks.
- Retain the dated 57-unit, current desktop/mobile core, five-race, desktop upload/Groq and dedicated touch-emulated mobile TXT results with their scope; mobile PDF/DOCX and physical-phone upload remain unverified.
- AI inventory: OpenCode **`github-copilot/gpt-6-astra`** plus parallel coding/review agents; code-native HTML/CSS UI; silent Playwright-captioned actual-app video with real model output, no fabricated screenshots/output. See [AI_DISCLOSURE.md](AI_DISCLOSURE.md). Felo export remains blocked by a missing key.
- Add genuine Kenyan user observations only if collected; otherwise retain “User validation pending.”
- Submit the required links through the official form by **27 September 2026, 19:30 EAT**. See [JUDGING_EVIDENCE.md](JUDGING_EVIDENCE.md) for supporting artifacts and remaining evidence gaps.
