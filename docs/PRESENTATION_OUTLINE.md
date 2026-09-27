# Njia — final presentation outline

**8 slides · Dhruzzz · Kenya · ONLINE · 27 September 2026**

**Narrative:** a Kenyan learner moves from uncertain next steps to visible skill evidence and a practical weekly plan.

This outline replaces the older decks, which are **obsolete**. It is presentation copy and direction, not a generated or hosted deck. The required **90-second demo video is a separate deliverable**; no official slide count or separate presentation duration is specified.

**Checkpoint:** outline ready; real Felo presentation export is blocked by a missing API key. Demo recording and fresh post-upload browser checks are ongoing. Public deployment is pending Vercel authentication. The main workflow will finalize deliverable links and test evidence.

## Design direction

- Use one message per slide, generous spacing, strong contrast and large type. Keep screenshots legible, cropped to the action being discussed.
- Use current application captures and simple editable diagrams. Distinguish **Implemented**, **Live-tested**, **Mock-tested** and **Verification ongoing** where relevant.
- Reuse the product's visual identity. Use one accent colour for the learner's next action and a restrained evidence strip for source/date/limitations.
- Keep detailed verification and disclosures in speaker notes or linked evidence. Keep the 2023-data label and the distinction between one live Groq observation and ongoing browser verification visible.

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

**Visual:** three tightly cropped current flow screenshots. Label new upload captures accurately: implementation is complete, fresh browser verification is ongoing.

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
- Earlier pre-upload desktop/mobile and delayed-response checks passed.
- Fresh integrated browser checks and demo recording ongoing.

**Visual:** compact evidence card beside the existing mobile screenshot; caption it as the recorded earlier core build.

**Speaker cue:** First-stage extraction metrics come from a small developer-authored synthetic set, not broad CV accuracy, upload evaluation or a fairness audit. Its 0.97 ms warm median and zero inference calls/cost exclude document parsing, startup, HTTP/browser work, retrieval and generation; they do not describe Groq or total operating cost. Earlier browser checks used Chromium at 1440 × 1100 and 390 × 844, before upload. Main workflow will add **[FINAL_TEST_RUN_TIMESTAMP_AND_RESULT]**. Groq's 2.27 seconds is one observed live-plan latency, not an aggregate benchmark; hosted cost is unmeasured.

## Slide 7 — Keep the learner in control

**On-slide copy**

- Review every suggested skill; manual entry is available.
- Uploads are processed in server memory; previews can contain personal data.
- Remote opt-in is server-checked; curated planning needs no AI consent.
- Hosted coaching receives structured curriculum, not CVs, identities or demand statistics.
- Historical demand and short quizzes do not prove employability.

**Visual:** current privacy notice and actual plan-mode label. Add fresh verified captures when ongoing browser checks finish.

**Speaker cue:** On a public app, documents/text are processed on the hosting server, not the user's laptop or device. Basic redaction is not full anonymization, previews may contain personal data, and downloaded reports persist as user files. The report excludes raw CV text. Attribute the data to `lukebarousse/data_jobs`; the prepared licence statement is not independently verified provenance.

## Slide 8 — A useful next step, then real-world validation

**On-slide copy**

> **Next: Kenyan user feedback · record live/fallback evidence · finish mobile checks**
>
> Primary application: **Brightest — Skills & Employability**
> Partner applications: **Brightest · Click Mobile · Artefact · Thunders**
>
> **[FINAL_SOURCE_CODE_URL]**
> **[FINAL_PRESENTATION_URL]**
> **[FINAL_90_SECOND_DEMO_VIDEO_URL]**

**Visual:** one strong current learning-plan deliverable, with readable links or QR codes generated only from the verified final URLs.

**Speaker cue:** Ask for feedback on whether the plan helps a Kenyan learner choose and complete a useful next task. Award selections are recommendations, not guarantees. The planned source address is `https://github.com/Eeshan-Vaghjiani/njia`; publication and jury access are pending. Optional app link: **[FINAL_LIVE_APP_URL — PENDING VERCEL AUTHENTICATION]**. Real Felo export is blocked by a missing key; the outline is ready and recording is in progress. Main workflow will finalize links.

## Required 90-second demo video

Recording is in progress. Record the real application using a synthetic profile, and finish fresh integrated checks before describing that flow as verified. The video must be hosted with jury-view access; the walkthrough script is not the deliverable. Use the following timing as an editing target, and verify the actual final duration.

| Time | Show | Narration / evidence boundary |
| --- | --- | --- |
| 0–8 s | Title and Kenya/Data Analyst context | “Njia turns your skills into a practical next learning step.” Label historical 2023 data. |
| 8–23 s | Input and review of Excel, SQL, Power BI | Show implemented upload with a synthetic document, editable preview and skill correction. Complete the ongoing browser checks before calling the integrated journey verified. |
| 23–39 s | Analysis and demand evidence | Show **391 postings**, **39.6% coverage**, top skills and the year. State that coverage is not hiring odds. |
| 39–58 s | Four-week plan and one deliverable | Show the actual Groq mode/model label when recording a live result. Main workflow already observed `openai/gpt-oss-20b`, four weeks in 2.27 seconds on 2026-09-27; distinguish this dated observation from any new run. |
| 58–68 s | Curated recovery path | Show an actual verified unavailable-provider result; an edited cut may connect separately recorded states, with clear labels. Never pass off a simulated response as live inference. |
| 68–81 s | Short practice result and report export | Fixed answer-key feedback; no certification. Show the report without raw CV text. |
| 81–90 s | Phone-width result and closing action | Use a fresh integrated mobile capture if verified. End on a practical learning deliverable and the project name. |

If Groq is unavailable during recording, show the actual curated result and distinguish it from the dated successful live check. A failure-path recording remains pending until captured. Reliability evidence can reference mocks when clearly labelled; do not describe them as live provider calls.

## Final presentation checks

- Replace every final URL placeholder; open source, deck/PDF and video with jury-view access. Local files alone are insufficient.
- Keep the canonical **391 / 39.6% / 2023** example consistent. Do not import numbers or stronger claims from obsolete decks.
- Main workflow will finalize the ongoing post-upload browser results and links. Retain the dated 57-method and live Groq observations with their scope; existing screenshots must not imply a newer test run.
- Complete the actual AI/tool/generated-asset inventory in [SUBMISSION_DRAFT.md](SUBMISSION_DRAFT.md). This outline is ready, but real Felo export is blocked by a missing key; no completed current presentation export is claimed.
- Add genuine Kenyan user observations only if collected; otherwise retain “User validation pending.”
- Submit the required links through the official form by **27 September 2026, 19:30 EAT**. See [JUDGING_EVIDENCE.md](JUDGING_EVIDENCE.md) for supporting artifacts and remaining evidence gaps.
