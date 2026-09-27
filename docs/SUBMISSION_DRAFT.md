# Njia — submission draft

**Team Dhruzzz · Kenya · ONLINE · 27 September 2026**

Form wording and deadline follow [HACKATHON_REQUIREMENTS.md](HACKATHON_REQUIREMENTS.md). This is a draft, not a submitted entry. Submit once through the [official project form](https://docs.google.com/forms/d/e/1FAIpQLSebmyKeBPv2mrmy4T_wI2_z9SBjjSTZ-O-_ewiWs6PBEikRjw/viewform) by **27 September 2026, 19:30 EAT**.

Current evidence supplied by the team/main workflow on **2026-09-27**: **57 unit tests pass**. Latest current-build browser checks passed desktop **1440×1100** and mobile **390×844**, with no JavaScript errors or external page requests; all **five race checks passed**. Desktop PDF/DOCX/TXT upload/preview/extraction/analysis and error handling passed, as did real Groq **`openai/gpt-oss-20b`**. Dedicated mobile **TXT** upload also passed at **390×844, touch=True**, through consent, preview, extraction, Kenya gap (**39.6%**), four-week curated plan and Markdown download, with **0 model calls, 0 JavaScript errors** and no horizontal overflow at the analysis assertion. This is Chromium mobile emulation; mobile PDF/DOCX and physical-phone upload remain unverified. Public source and the **90.000-second, 1280 × 720** silent captioned actual-app upload/Groq video are published with anonymous access verified. Deployment awaits Vercel login; instructions have been provided. No current deck is generated: Felo needs an API key. Genuine user feedback remains pending.

Mobile evidence: `artifacts/mobile-upload-results.json` and `artifacts/mobile-upload-plan.png`. With the local server running and Playwright installed, run `.\.venv\Scripts\python.exe scripts/mobile_upload_test.py` from the project root; see [local test results](LOCAL_TEST_RESULTS.md). `artifacts/` is Git-ignored, so these paths are local. Selected JSON evidence is planned for the [demo-v1 release](https://github.com/Eeshan-Vaghjiani/njia/releases/tag/demo-v1); only attached assets are publicly downloadable.

## Exact form fields, in order

### 1. Country

Kenya

### 2. Hackerspace / ONLINE

ONLINE

### 3. Team name

Dhruzzz

### 4. Team leader full name

Supply privately in the official form from the confirmed team records; identity details are not included in this public draft.

### 5. Team leader email

Supply directly in the form from the separately held submission contacts, matching Final Team Confirmation. No contact value is included in this document.

### 6. Project title

Njia

### 7. Team members — full name of each member, one per line

Supply the confirmed roster privately in the official form, one full name per line. Member identity/contact details are not included in this public draft.

### 8. Project summary — maximum 150 words

Njia helps Kenyan tech and data job seekers turn existing skills into a practical next learning step. Users upload PDF, DOCX or TXT documents, review editable text and skill suggestions, or enter skills manually. They compare confirmed skills with historical demand, build a four-week plan, try short practice checks and download an evidence report. The browser prototype uses 18,371 postings from 2023 across ten African and MENA countries, with visible sample sizes and broader-sample fallback. Documents are processed in app-server memory. Optional, explicitly opted-in Groq coaching rewrites structured curriculum while preserving calculated statistics and curated resources. Actual document upload, preview, extraction and analysis passed desktop browser checks; real Groq coaching also passed in-browser with openai/gpt-oss-20b. Curated plans remain available without AI consent. Coverage describes advertised skill mentions, not hiring odds or certified competence.

### 9. Problem solved

A Kenyan learner targeting a tech or data role needs to decide what to learn next and how to demonstrate progress. Job requirements and learning resources can be difficult to translate into a focused learning plan that fits the time available. Njia connects a user's confirmed skills to visible demand evidence and a concrete weekly activity, practice check and take-away report. This is the problem hypothesis behind the prototype; real Kenyan user feedback and employment outcomes have not yet been established.

### 10. Solution and key features

- **Reviewable skills:** upload a document, paste experience or select skills manually; keyword/alias suggestions can be corrected before analysis.
- **Document input:** PDF, DOCX and UTF-8 TXT browser uploads produce an editable-text preview through `/api/upload`, with processing consent and in-memory parsing. The backend accepts up to **5 MiB**; the frontend caps files at **4,000,000 bytes** to leave room under Vercel's request limit. Actual desktop upload/preview/extract/analyze checks and invalid-file, oversize, scanned-PDF and consent-error cases passed. Scanned PDFs require external OCR. Public-app processing occurs on the hosting server, not the user's laptop; previews may contain personal data.
- **Explainable gaps:** canonicalized historical posting counts, top-15 demand-weighted coverage, sample sizes and explicit broader-sample fallback below 50 local postings.
- **Relevant examples:** TF-IDF/cosine retrieval of historical postings, labelled as 2023 examples rather than live vacancies.
- **Actionable learning:** a four-week curated plan with hours, exercises, resources and deliverables. Optional Groq wording enhancement is implemented, mock-tested and live-tested by the main workflow on 2026-09-27: **`openai/gpt-oss-20b`, four weeks in 2.27 seconds** in one observed run. `/api/plan` enforces remote opt-in using `use_ai`/`ai_consent`; curated plans need no AI consent.
- **Practice and evidence:** fixed three-question checks for supported skills and a downloadable Markdown report. These do not certify proficiency.
- **Recovery paths:** manual skills when extraction is unsuitable; complete curated coaching when the model is unavailable or its response fails validation.

### 11. Technologies used

Python; FastAPI; Uvicorn; Pydantic; HTML/CSS/JavaScript; scikit-learn TF-IDF and cosine similarity; HTTPX; python-dotenv; python-multipart; pypdf; Python ZIP/XML parsing for DOCX; unittest; Playwright/Chromium. Bundled JSONL data is attributed to `lukebarousse/data_jobs`. Optional hosted coaching uses Groq's chat-completions API with default and live-tested model `openai/gpt-oss-20b`. The original `llama-3.3-70b-versatile` was unavailable in the account model list, prompting the default change. Optional local Ollama defaults to `qwen2.5:3b` and remains mock-tested only. Inference defaults to offline unless configured.

### 12. Source code URL

https://github.com/Eeshan-Vaghjiani/njia

Public repository creation and anonymous access verified by the main workflow on 2026-09-27.

### 13. Presentation URL

**[FINAL_PRESENTATION_URL — PENDING FINAL DECK/PDF AND JURY-ACCESS CHECK]**

The [presentation outline](PRESENTATION_OUTLINE.md) is ready. **Real Felo export is blocked by a missing API key**; no completed current deck/export is claimed. Older decks are obsolete and must not be submitted as the current presentation.

### 14. 90-second demo video URL

https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/njia-demo-90s.webm

View/download the published video from the [demo-v1 release page](https://github.com/Eeshan-Vaghjiani/njia/releases/tag/demo-v1). `artifacts/njia-demo-90s.webm` is **exactly 90.000 seconds, 1280 × 720**, normal-speed actual CV upload and real Groq recording, silent with Playwright captions; no fabricated screenshots/output or synthetic voice. Anonymous direct-asset HEAD returned **200**, **3,498,819 bytes**.

### 15. Project next step

Complete the presentation once Felo access is available, finish Vercel login for deployment, and extend the passing emulated mobile TXT check to PDF/DOCX and physical phones. Conduct short, consented usability sessions with Kenyan learners or job seekers to measure whether they can identify a useful next learning task, understand coverage, and finish the flow. Use actual feedback to refine privacy labels, curriculum and mobile interaction, then expand evaluation beyond synthetic examples and refresh the historical data with documented provenance.

### 16. Partner awards — which prizes is your team applying for?

Recommended selections, using the exact checkbox wording:

- **Brightest GmbH — Skills & Employability Award (Brightest Award) | Job-relevant skills and qualifications | Fully paid Brightest vouchers + discounted Brightest voucher pricing, both for ONE WINNING TEAM ONLY; quantity, discount rate and redemption terms TBC**
- **Click Mobile — Mobile-First Impact Award | Mobile-first solutions for Kenyan users, businesses or communities | Total KSh 50,000 cash prize; KENYA ONLY; allocation TBC**
- **Artefact — Data & AI Award | Data into actionable insights or useful AI solutions with measurable business or societal impact | Approx. US$1,040 gift voucher; one winning team; ALL PARTICIPATING COUNTRIES; redemption terms TBC**
- **Thunders — Engineering Excellence Award | Strong, reliable technical prototype | One Mac mini; one team**

These are fit recommendations, not eligibility approvals or award guarantees. Kenya/ONLINE and the privately held roster are user-supplied; organizer registration/attendance records remain authoritative. Click Mobile's KSh 50,000 is the total Kenya contribution, with allocation unannounced. Country podium consideration is automatic for eligible entries; do not also select the podium-only checkbox.

### 17. Primary prize application — choose the award that best fits your project

**Brightest GmbH — Skills & Employability Award**

### 18. Award application — explain your project’s fit and eligibility

**Brightest GmbH — Skills & Employability Award:** Njia supports job-relevant learning through visible skill gaps, four-week activities, short practice checks and an exportable evidence report, making this our strongest thematic fit. The existing Kenya/Data Analyst walkthrough demonstrates that learning workflow, but does not establish accredited qualifications or improved hiring outcomes. We are a Kenya/ONLINE team; the published award lists no Kenya exclusion, subject to organizer confirmation of eligibility.

**Click Mobile — Mobile-First Impact Award:** Njia targets a practical Kenyan learner need through a browser-based path from skills to learning actions; current-build Chromium checks passed the core journey and a dedicated TXT upload → preview/consent → extraction → Kenya gap (39.6%) → curated plan → download flow at 390×844 with touch emulation, zero model calls/JavaScript errors and no horizontal overflow at analysis. Our Kenya/ONLINE team matches the published Kenya-only scope; mobile PDF/DOCX and physical-phone upload remain unverified. We claim a mobile-browser prototype, not measured adoption or proven employment impact.

**Artefact — Data & AI Award:** Njia converts 2023 posting data into explainable skill-demand analysis, historical retrieval and learning actions; the canonical Kenya/Data Analyst sample contains 391 postings and gives the example profile 39.6% demand-weighted coverage. The first-stage extraction evaluation records 17 exact matches across 20 developer-authored synthetic examples; separately, a live Groq `openai/gpt-oss-20b` call returned a four-week plan in 2.27 seconds on 2026-09-27—prototype observations, not societal-outcome evidence or broad performance benchmarks. The award explicitly accepts all participating countries, including Kenya, subject to the team's confirmed participation.

**Thunders — Engineering Excellence Award:** Njia demonstrates engineering care through canonicalized calculations, sample fallback, bounded document parsing, server-enforced remote-AI opt-in, provider-output validation and curated-plan fallback. Evidence includes 57 passing unit tests, current-build desktop/mobile core and all five race checks, desktop PDF/DOCX/TXT upload/error checks, dedicated touch-emulated mobile TXT upload through curated plan/download, and real Groq coaching in-browser. We are a Kenya/ONLINE team; no Kenya exclusion is stated in the published award description, with final eligibility determined by organizers.

### 19. AI/tool disclosure — list models, agents, datasets, APIs and generated assets used. Explain your chosen stack, access constraints, actual AI contribution and fallback. State honestly if no AI was used. Brev is optional; explain its use only if used. Do not include voucher codes, passwords or API keys.

Njia uses a lightweight Python/FastAPI and static-JavaScript stack so the core workflow can run without inference credentials. Skill extraction uses vocabulary/alias rules; demand is calculated from canonicalized posting rows; related examples use scikit-learn TF-IDF/cosine retrieval; practice checks use fixed answer keys. These components are not generative-model inference.

Optional Groq hosted coaching is implemented and mock-tested. On **2026-09-27**, the main workflow successfully live-tested actual model **`openai/gpt-oss-20b`**, receiving a four-week plan in **2.27 seconds**. The account model list did not offer the original `llama-3.3-70b-versatile`, so the default changed to `openai/gpt-oss-20b`. This is a single integration observation, not an aggregate latency, cost or model-quality evaluation. Access requires a server-held API key, network connectivity and provider availability. The default remains `NJIA_AI_PROVIDER=offline` unless configured. `/api/plan` checks `use_ai`/`ai_consent` server-side before remote generation; curated planning is available without AI consent. Only allowlisted structured curriculum fields are sent to Groq, not raw CV text, identity fields, country/role or demand statistics. Validated output can rewrite titles, tasks and deliverables; calculated statistics, skill targets, hours and curated links remain controlled by application logic. Missing credentials, connection errors, rate limits or invalid output return the complete curated plan. Validation does not guarantee that generated advice is correct.

PDF/DOCX/TXT documents and pasted text are processed in app-server memory; on a public app this means the hosting server, not the user's device. Previews may contain personal information. The first-stage synthetic evaluation's extraction timings and zero inference calls/cost exclude document parsing, HTTP/browser work, retrieval and generation, and do not describe Groq or total operating costs.

Optional local Ollama defaults to `qwen2.5:3b`; its integration is mock-tested but not live-verified. NVIDIA Brev was not used. The bundled source is attributed to `lukebarousse/data_jobs`: 18,371 historical 2023 postings from ten African/MENA countries. Prepared documentation identifies Apache-2.0; provenance and licensing have not been independently verified. The small extraction evaluation uses 20 developer-authored synthetic examples and is not a real-user or fairness study.

AI coding assistance used **OpenCode**, main agent **`github-copilot/gpt-6-astra`**, plus parallel coding/review agents in the same harness; their underlying model identities were not independently established. Assistance covered application code, documentation and review. UI visuals are code-native HTML/CSS. The silent, captioned Playwright demo records actual CV upload and real Groq output at normal speed, with no fabricated screenshots/output or synthetic voice. Felo presentation generation is blocked by a missing API key. Development assistance is distinct from runtime Groq coaching.

### 20. Final confirmation

Exact required checkbox statement:

> I confirm that our functional prototype, source code, presentation, 90-second demo video, project card details and AI/tool disclosure are complete, accessible and final.

**Pending.** Source and video access are verified; complete the presentation and remaining required deliverables before confirming.

## Final handoff

- Required URLs: source, final presentation and **90-second video**, each opened successfully with jury-view access.
- Optional live app: **[FINAL_LIVE_APP_URL — OPTIONAL; PENDING VERCEL AUTHENTICATION]**. A local prototype with run instructions and recorded demo is permitted.
- Current desktop/mobile core, all five race checks, desktop upload, dedicated touch-emulated mobile TXT upload and real browser Groq passed. The 90.000-second video is published and anonymously accessible. Mobile PDF/DOCX and physical-phone upload remain unverified.
- Use the dated evidence in [JUDGING_EVIDENCE.md](JUDGING_EVIDENCE.md): 57 unit tests passed at this checkpoint, as supplied by the main workflow.
- Submit the official form by the Kenya deadline and retain the receipt separately. No submission completion is claimed in this draft.
