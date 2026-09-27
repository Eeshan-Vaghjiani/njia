# Njia — judging evidence

**Dhruzzz · Kenya · ONLINE · evidence checkpoint: 27 September 2026**

The [published rubric](HACKATHON_REQUIREMENTS.md#7-published-judging-rubric-and-njia-evidence) totals **100 points: 20 / 20 / 20 / 15 / 15 / 10**. The weights below are available points, not predicted scores.

## What is established at this checkpoint

| Evidence | Status and source | Boundary |
| --- | --- | --- |
| Core skills → analysis → plan → practice → export | Recorded passing desktop/mobile checks in [browser-results.json](../artifacts/browser-results.json), documented on 27 September 2026 in [LOCAL_TEST_RESULTS.md](LOCAL_TEST_RESULTS.md) | Earlier core flow; not a verification of the new upload/Groq frontend integration |
| PDF, DOCX and UTF-8 TXT input | Browser upload and memory-based backend implemented, with editable preview and skill review/manual entry; [uploads.py](../njia/uploads.py), [test_uploads.py](../tests/test_uploads.py) | Backend up to **5 MiB**; frontend **4,000,000 bytes** for Vercel request headroom; no OCR; preview is not anonymized; fresh browser checks ongoing |
| Groq hosted coaching | Main workflow live-tested actual **`openai/gpt-oss-20b` on 2026-09-27**, returning a **four-week plan in 2.27 seconds**; mocked boundaries also covered in [test_hosted_ai.py](../tests/test_hosted_ai.py) | One observed integration run, not a model-quality or aggregate latency/cost benchmark |
| Default and failure operation | Curated plans, manual skills and explicit small-sample fallback implemented; core and provider tests cover these paths | A real live-provider failure demonstration is still to be recorded |
| Extraction measurements | Existing [evaluation.json](../artifacts/evaluation.json), recorded in the 27 September verification notes | Small developer-authored synthetic set; no independent real-CV validation |
| Async state handling | [race-results.json](../artifacts/race-results.json): five passing delayed-response checks | Applies to the recorded earlier browser state, not automatically every later change |
| Unit/API test suite | Main workflow reports **57 unittest methods passing** at the 2026-09-27 checkpoint | Not rerun for this documentation-only pass. Main workflow will supply final build/timestamp/results |
| Kenyan user value | Intended user and a working synthetic Kenya example | No real Kenyan user feedback, adoption, hiring outcomes or testimonials documented yet |

README, disclosure and demo now reflect this checkpoint. **Earlier pitch decks are obsolete.** Fresh post-upload browser checks and demo recording are ongoing, not complete. The outline is ready, but real Felo export is blocked by a missing key. Public deployment awaits Vercel authentication; source publication/access and final deliverable links remain pending.

The default remains `NJIA_AI_PROVIDER=offline` unless configured. The account model list did not offer the original `llama-3.3-70b-versatile`, so Groq's default changed to `openai/gpt-oss-20b`. Remote opt-in is enforced server-side by `/api/plan` using `use_ai`/`ai_consent`; curated plans need no AI consent. Only allowlisted structured curriculum goes to Groq, not CV text, identities, country/role or demand statistics.

## Rubric-to-evidence map

| Criterion | Weight | Evidence to put in front of the jury | Honest gap / most useful improvement |
| --- | ---: | --- | --- |
| **Problem + user value** | **20** | A Kenyan tech/data learner chooses a role, confirms skills and leaves with a concrete weekly activity and evidence report. Show the actual task rather than asserting a broad unemployment solution. | Obtain real Kenyan learner/job-seeker feedback now: can they identify the next useful learning action, and is it relevant? No user quotes or outcome claims exist yet. |
| **Functional execution** | **20** | Recorded core end-to-end flow; API calculations; practice scoring; report export; implemented browser upload/preview, tested parsing and curated fallback. | Finish fresh checks and record upload → editable preview → confirmed skills → plan → report. Backend tests alone do not prove that browser journey. |
| **Quality of AI use** | **20** | Deterministic evidence and TF-IDF retrieval; optional Groq rewrite of structured curriculum; preserved statistics/resources and validated output. Main workflow observed a live `openai/gpt-oss-20b` four-week plan in 2.27 seconds on 2026-09-27. | Capture the actual provider/model-labelled result for the jury, review advice for relevance and unsupported claims, and record complete curated fallback. One successful call is not a quality evaluation. Do not call rule extraction or fixed quiz grading LLM work. |
| **Testing + reliability** | **15** | 57 unittest methods reported passing; first-stage synthetic extraction artifact, parser/provider boundaries, earlier pre-upload browser checks and five asynchronous regressions. | Main workflow will finalize suite timestamp/build reference and ongoing post-upload browser checks. Extraction timing is not whole-app or hosted latency; Groq's single 2.27-second observation is not a benchmark, and provider cost is unmeasured. |
| **Experience + demo** | **15** | Existing Chromium checks at desktop 1440 × 1100 and mobile 390 × 844, visible progress, editable skills and downloaded report. | Rehearse the new phone-width journey, file picker, preview, provider notice and fallback. Produce the required accessible 90-second video and a concise current deck. |
| **Responsible AI + data** | **10** | Consent and manual route; in-memory file processing; curriculum-only Groq payload; editable suggestions; historical-data labels; explicit sample fallback; report excludes raw CV. | Verify deployment-aware privacy wording before upload/generation: server processing is not necessarily on-device, previews may contain personal data, and Groq receives structured curriculum. No complete anonymization, fairness, certification or hiring-probability claim. |

## Canonical figures to use everywhere

| Claim | Verified existing value | Meaning |
| --- | --- | --- |
| Corpus | **18,371 postings, 2023, ten African/MENA countries** | Historical tech/data subset, not today's entire labour market |
| Kenya across roles | **1,326 postings** | Corpus scope, not the Data Analyst sample |
| Kenya / Data Analyst | **391 postings** | Canonical sample used in the demo |
| Synthetic profile | **Excel, SQL, Power BI** | Self-reported/confirmed skills, not validated competence |
| Sample coverage | **39.6%** | Share of top-15 demand-weighted skill mentions covered by that profile, not employment probability |
| Small local samples | **Fewer than 50 postings** triggers the role's combined ten-country sample | Broader evidence with less local specificity; must be labelled |
| Extraction evaluation | **20 synthetic examples; 17 exact skill-set matches** | Developer-authored examples, not independent validation |
| Precision / recall | **0.9535 / 0.9762** | Pooled skill-level results: 41 true positives, 2 false positives, 1 false negative |

Counts and sample coverage are corroborated by [LOCAL_TEST_RESULTS.md](LOCAL_TEST_RESULTS.md) and the existing [sample report](../artifacts/njia-skill-evidence.md). Runtime canonicalization, not old aggregate slides, defines the numbers.

The first-stage extraction artifact's **0.97 ms warm median** measures extraction only; it excludes startup, document parsing, requests, rendering, retrieval and generation. Its zero inference calls/cost describe that offline extraction run, not Groq or total operating cost. These are not upload-validation metrics. The known imperfect examples include “excel” as a verb, implied Excel use and retrospective negation. These are concrete reasons to keep skill review editable.

## Highest-value improvements now

### 1. Observe real Kenyan users

Ask available Kenyan learners or job seekers, with consent, to attempt the task: “Choose your target role and find one useful learning action for this week.” Record participant count, date, task completion, confusion, time if measured, and whether they understood the coverage label. Ask what they would actually change or use next.

**Evidence to add:** an anonymized observation table and the resulting product change. Quote only words actually said, with permission; if nobody has participated, state “User validation pending.” A tiny convenience sample is exploratory feedback, not representative research.

### 2. Capture the observed live model and its fallback

The main workflow has reported the successful 2026-09-27 live check: `openai/gpt-oss-20b`, four-week plan, 2.27 seconds. Add the exact timestamp/build reference, actual plan mode and a synthetic-input screenshot or recording; review whether activities fit the chosen skills and hours and avoid fabricated claims. Demonstrate the curated path without AI consent and with the provider unavailable, showing that statistics, links and hours remain intact.

**Evidence to add:** jury-view capture of the observed live result plus a clearly labelled fallback result. A `/api/health` configuration label or mocked result cannot substitute for live evidence. No completed fallback recording is claimed yet.

### 3. Complete the mobile journey

At approximately 390 × 844, try file selection, readable preview editing, skill correction, demand inspection, plan generation, practice and export. Check tap targets, horizontal overflow, keyboard interaction, error recovery and whether long model output obscures the next action. A real phone check is stronger evidence than viewport emulation alone; label which was used.

**Evidence to add:** fresh phone-width screenshots and end-to-end check results from the integrated build. Existing mobile evidence is useful baseline evidence, not proof of new feature integration.

### 4. Make privacy labels precise

Before upload: explain that documents are processed in server memory and preview text may contain personal information. Before hosted coaching: explain that only structured curriculum goes to Groq, not CV text, identities, country/role or demand statistics; remote opt-in is checked server-side. On a public app, “server” means the host, not the user's device; processing is not laptop-only.

**Evidence to add:** screenshots of the final notices and actual-mode label, plus a report showing no raw CV text. Explain that downloads persist as user files and that basic redaction is not comprehensive anonymization. Preserve visible 2023, sample-size and non-certification labels.

## Award positioning

- **Primary: Brightest GmbH — Skills & Employability.** Strongest direct fit: job-relevant learning activities, practice and evidence. No accreditation or hiring-result claim.
- **Partner: Click Mobile.** Kenya/ONLINE team and recorded mobile-browser core flow; strengthen with the final phone-width demonstration. Published KSh 50,000 is the total Kenya contribution, with allocation unannounced.
- **Partner: Artefact.** Clear data-to-action pipeline, measurable prototype checks and one observed live Groq plan; advice quality and societal impact still need evaluation. Explicitly open to all participating countries.
- **Partner: Thunders.** Reliability, bounded parsing, controlled provider output and fallbacks are concrete evidence. Final integrated execution still matters.

These recommendations do not predict a score, eligibility decision or win. Copy-ready, two-to-three-sentence applications for all four awards appear under field 18 in [SUBMISSION_DRAFT.md](SUBMISSION_DRAFT.md).

## Final evidence and deliverable record

| Item | Final value to supply |
| --- | --- |
| Final tested build reference and time | **[FINAL_BUILD_REFERENCE_AND_TEST_TIMESTAMP_WITH_TIMEZONE]** |
| Final test result | **57 unittest methods pass at this checkpoint, per main workflow** — [FINAL_RUN_RESULT_AND_TIMESTAMP_PENDING] |
| Integrated desktop/mobile result | **ONGOING** — [FINAL_BROWSER_RESULT_AND_TIMESTAMP] |
| Live Groq result | **2026-09-27: main workflow observed `openai/gpt-oss-20b`, four-week plan in 2.27 seconds** — [FINAL_CAPTURE_AND_EXACT_TIMESTAMP_PENDING] |
| Real Kenyan user feedback | **PENDING — [ACTUAL PARTICIPANT COUNT, OBSERVATIONS AND DATE]** |
| Source URL | **[FINAL_SOURCE_CODE_URL]** — planned `https://github.com/Eeshan-Vaghjiani/njia`; publication/access pending |
| Final presentation URL | **[FINAL_PRESENTATION_URL]** — outline ready; real Felo export blocked by missing key; old decks obsolete |
| Required 90-second video URL | **[FINAL_90_SECOND_DEMO_VIDEO_URL]** — recording in progress |
| Optional deployed app URL | **[FINAL_LIVE_APP_URL — OPTIONAL]** — pending Vercel authentication |

The source, presentation and 90-second video must be accessible to the jury. Public deployment and Docker are optional; the submission form and its final confirmation are still required by **27 September 2026, 19:30 EAT**.
