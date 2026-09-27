# Njia — judging evidence

**Dhruzzz · Kenya · ONLINE · evidence checkpoint: 27 September 2026**

The [published rubric](HACKATHON_REQUIREMENTS.md#7-published-judging-rubric-and-njia-evidence) totals **100 points: 20 / 20 / 20 / 15 / 15 / 10**. The weights below are available points, not predicted scores.

## What is established at this checkpoint

| Evidence | Status and source | Boundary |
| --- | --- | --- |
| Core skills → analysis → plan → practice → export | Latest current-build `scripts/browser_test.py` passed desktop **1440×1100** and mobile **390×844**, with **zero JavaScript errors or external page requests**; `artifacts/browser-results.json` | Core mobile flow verified; dedicated TXT upload evidence below |
| Dedicated mobile TXT upload | Current-build `scripts/mobile_upload_test.py` **passed** Chromium mobile emulation at **390×844, touch=True**: actual synthetic TXT upload with processing consent → preview → extraction → Kenya gap (**39.6%**) → four-week curated plan → Markdown download; **0 model calls, 0 JavaScript errors**, no horizontal overflow at the analysis assertion; `artifacts/mobile-upload-results.json`, `artifacts/mobile-upload-plan.png` | TXT only; mobile PDF/DOCX, physical-phone/native picker interaction, preview editing and mobile upload error recovery are not verified by this check |
| PDF, DOCX and UTF-8 TXT input | Desktop `scripts/upload_browser_test.py` **passed all three formats** through upload → editable preview → extraction → analysis, plus invalid-file, oversize, scanned-PDF and consent-error handling | Backend up to **5 MiB**; frontend **4,000,000 bytes** for Vercel request headroom; no OCR; preview is not anonymized |
| Groq hosted coaching | Real browser check **passed with `openai/gpt-oss-20b`**; separately, main workflow observed a **four-week plan in 2.27 seconds** on 2026-09-27; mocked boundaries covered in [test_hosted_ai.py](../tests/test_hosted_ai.py) | Integration observations, not a model-quality or aggregate latency/cost benchmark |
| Default and failure operation | Curated plans, manual skills and explicit small-sample fallback implemented; core and provider tests cover these paths | A real live-provider failure demonstration is still to be recorded |
| Extraction measurements | Existing `artifacts/evaluation.json`, recorded in the 27 September verification notes | Small developer-authored synthetic set; no independent real-CV validation |
| Async state handling | Latest current-build `scripts/race_test.py`: **all five passed**; `artifacts/race-results.json` | Delayed-response/state regression checks |
| Unit/API test suite | Main workflow reports **57 unit tests passing** at the 2026-09-27 checkpoint | Not rerun for this documentation-only pass; exact build/time-of-day not supplied |
| Demo recording | Published `artifacts/njia-demo-90s.webm`: **exactly 90.000 seconds, 1280 × 720**, normal-speed actual CV upload and real Groq, silent with Playwright captions | Anonymous asset HEAD **200**, **3,498,819 bytes**; no fabricated screenshots/output or synthetic voice |
| Public source repository | https://github.com/Eeshan-Vaghjiani/njia — creation/anonymous access verified by main workflow | Repository access does not establish a deployed app |
| Kenyan user value | Intended user and a working synthetic Kenya example | No real Kenyan user feedback, adoption, hiring outcomes or testimonials documented yet |

README, submission draft and demo reflect this checkpoint. **Earlier pitch decks are obsolete.** Current core desktop/mobile, all five race checks, desktop upload/error paths, dedicated mobile TXT upload and real Groq passed. Source and video are published with anonymous access verified. Mobile PDF/DOCX and physical-phone upload remain unverified; genuine user feedback remains pending. No current deck is generated: Felo needs an API key. Deployment awaits Vercel login; instructions have been provided.

`artifacts/` is Git-ignored: artifact paths in this document are local evidence, not public repository links. Selected JSON evidence is planned for the [demo-v1 release](https://github.com/Eeshan-Vaghjiani/njia/releases/tag/demo-v1); only assets actually attached there are publicly downloadable.

The default remains `NJIA_AI_PROVIDER=offline` unless configured. The account model list did not offer the original `llama-3.3-70b-versatile`, so Groq's default changed to `openai/gpt-oss-20b`. Remote opt-in is enforced server-side by `/api/plan` using `use_ai`/`ai_consent`; curated plans need no AI consent. Only allowlisted structured curriculum goes to Groq, not CV text, identities, country/role or demand statistics.

## Rubric-to-evidence map

| Criterion | Weight | Evidence to put in front of the jury | Honest gap / most useful improvement |
| --- | ---: | --- | --- |
| **Problem + user value** | **20** | A Kenyan tech/data learner chooses a role, confirms skills and leaves with a concrete weekly activity and evidence report. Show the actual task rather than asserting a broad unemployment solution. | Obtain real Kenyan learner/job-seeker feedback now: can they identify the next useful learning action, and is it relevant? No user quotes or outcome claims exist yet. |
| **Functional execution** | **20** | Desktop PDF/DOCX/TXT upload → preview → extraction → analysis and real Groq passed; current desktop/mobile core, practice and export passed; dedicated touch-emulated mobile TXT upload through curated plan/download passed; actual-app demo published. | Extend mobile upload verification to PDF/DOCX and physical phones. |
| **Quality of AI use** | **20** | Deterministic evidence and TF-IDF retrieval; optional Groq rewrite of structured curriculum; preserved statistics/resources and validated output. Real `openai/gpt-oss-20b` browser check passed; separate live four-week plan observed in 2.27 seconds on 2026-09-27. | Review advice for relevance and unsupported claims, and record complete curated fallback. Successful integration is not a quality evaluation. Do not call rule extraction or fixed quiz grading LLM work. |
| **Testing + reliability** | **15** | 57 unit tests; current desktop/mobile core and all five race checks; desktop upload/error paths, dedicated mobile TXT upload and real browser Groq passed; synthetic extraction artifact. | Exact build/time-of-day not supplied. Extraction timing is not whole-app latency; Groq's single 2.27-second observation is not a benchmark, and provider cost is unmeasured. |
| **Experience + demo** | **15** | Published **90.000-second, 1280 × 720** actual-app upload/Groq video, silent/captioned; anonymous access verified; current desktop/mobile core and touch-emulated mobile TXT upload checks passed. | Complete the Felo deck when its key is available and extend mobile checks to physical phones and other formats. |
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

Counts and sample coverage are corroborated by [LOCAL_TEST_RESULTS.md](LOCAL_TEST_RESULTS.md) and the existing local sample report `artifacts/njia-skill-evidence.md`. Runtime canonicalization, not old aggregate slides, defines the numbers.

The first-stage extraction artifact's **0.97 ms warm median** measures extraction only; it excludes startup, document parsing, requests, rendering, retrieval and generation. Its zero inference calls/cost describe that offline extraction run, not Groq or total operating cost. These are not upload-validation metrics. The known imperfect examples include “excel” as a verb, implied Excel use and retrospective negation. These are concrete reasons to keep skill review editable.

## Highest-value improvements now

### 1. Observe real Kenyan users

Ask available Kenyan learners or job seekers, with consent, to attempt the task: “Choose your target role and find one useful learning action for this week.” Record participant count, date, task completion, confusion, time if measured, and whether they understood the coverage label. Ask what they would actually change or use next.

**Evidence to add:** an anonymized observation table and the resulting product change. Quote only words actually said, with permission; if nobody has participated, state “User validation pending.” A tiny convenience sample is exploratory feedback, not representative research.

### 2. Review the observed live model and capture fallback

The main workflow reports a successful real browser check with `openai/gpt-oss-20b` and a separate 2026-09-27 live observation of a four-week plan in 2.27 seconds. The actual-app captioned demo is complete. Review whether activities fit the chosen skills and hours and avoid fabricated claims. Demonstrate the curated path without AI consent and with the provider unavailable, showing that statistics, links and hours remain intact.

**Evidence to add:** exact build/time-of-day and a clearly labelled provider-failure fallback capture. The real browser success is established; a `/api/health` configuration label or mocked result alone would not establish it. No completed provider-failure fallback recording is claimed yet.

### 3. Extend the passing mobile TXT upload check

`scripts/mobile_upload_test.py` passed the current-build TXT upload flow at **390×844, touch=True** in Chromium mobile emulation, including consent, preview, extraction, **39.6%** Kenya coverage, four curated weeks and Markdown download. The result records zero model calls and JavaScript errors; the horizontal-overflow assertion passed at analysis. Local evidence: `artifacts/mobile-upload-results.json` and `artifacts/mobile-upload-plan.png`.

**Reproduce:** with the local server running and Playwright installed, run `.\.venv\Scripts\python.exe scripts/mobile_upload_test.py` from the project root. See [LOCAL_TEST_RESULTS.md](LOCAL_TEST_RESULTS.md) for scope and setup.

**Evidence to add:** PDF/DOCX upload on mobile, physical-phone/native file-picker interaction, preview editing, keyboard interaction and mobile error recovery. The passing TXT check does not establish those behaviors. This is a browser prototype, not a native app.

### 4. Make privacy labels precise

Before upload: explain that documents are processed in server memory and preview text may contain personal information. Before hosted coaching: explain that only structured curriculum goes to Groq, not CV text, identities, country/role or demand statistics; remote opt-in is checked server-side. On a public app, “server” means the host, not the user's device; processing is not laptop-only.

**Evidence to add:** screenshots of the final notices and actual-mode label, plus a report showing no raw CV text. Explain that downloads persist as user files and that basic redaction is not comprehensive anonymization. Preserve visible 2023, sample-size and non-certification labels.

## Award positioning

- **Primary: Brightest GmbH — Skills & Employability.** Strongest direct fit: job-relevant learning activities, practice and evidence. No accreditation or hiring-result claim.
- **Partner: Click Mobile.** Kenya/ONLINE team, recorded mobile-browser core flow and passing touch-emulated TXT upload through curated plan/download; extend evidence to physical phones and PDF/DOCX. Published KSh 50,000 is the total Kenya contribution, with allocation unannounced.
- **Partner: Artefact.** Clear data-to-action pipeline, measurable prototype checks and one observed live Groq plan; advice quality and societal impact still need evaluation. Explicitly open to all participating countries.
- **Partner: Thunders.** Reliability, bounded parsing, controlled provider output and fallbacks are concrete evidence. Final integrated execution still matters.

These recommendations do not predict a score, eligibility decision or win. Copy-ready, two-to-three-sentence applications for all four awards appear under field 18 in [SUBMISSION_DRAFT.md](SUBMISSION_DRAFT.md).

## Final evidence and deliverable record

| Item | Final value to supply |
| --- | --- |
| Tested build reference and time | Evidence supplied **2026-09-27**; exact build/time-of-day not supplied |
| Unit test result | **57 unit tests passed**, per main workflow |
| Current desktop result | **Passed** actual PDF/DOCX/TXT upload → editable preview → extraction → analysis; invalid-file, oversize, scanned-PDF and consent-error handling |
| Mobile result | **Current-build core flow and dedicated TXT upload passed at 390×844**; upload check used **touch=True** Chromium emulation, consent/preview/extraction → Kenya **39.6%** gap → curated plan → download, **0 model calls/JavaScript errors**, no horizontal overflow at analysis; mobile PDF/DOCX and physical-phone upload unverified |
| Live Groq result | **Real browser check passed: `openai/gpt-oss-20b`**; separate 2026-09-27 observation: four-week plan in 2.27 seconds |
| Real Kenyan user feedback | **PENDING — [ACTUAL PARTICIPANT COUNT, OBSERVATIONS AND DATE]** |
| Source URL | https://github.com/Eeshan-Vaghjiani/njia — public creation/access verified |
| Final presentation URL | **[FINAL_PRESENTATION_URL]** — outline ready; real Felo export blocked by missing key; old decks obsolete |
| Required 90-second video URL | https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/njia-demo-90s.webm — published, exactly **90.000 seconds, 1280 × 720**, silent/captioned actual CV upload and real Groq; anonymous HEAD **200**, **3,498,819 bytes** |
| Video viewing/download page | https://github.com/Eeshan-Vaghjiani/njia/releases/tag/demo-v1 |
| Optional deployed app URL | No deployment; Vercel remains unauthenticated |

The source, presentation and 90-second video must be accessible to the jury. Public deployment and Docker are optional; the submission form and its final confirmation are still required by **27 September 2026, 19:30 EAT**.
