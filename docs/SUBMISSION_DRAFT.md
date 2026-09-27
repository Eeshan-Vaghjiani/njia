# Njia — submission draft

**Team Dhruzzz · Kenya · ONLINE · 27 September 2026**

Form wording and deadline follow [HACKATHON_REQUIREMENTS.md](HACKATHON_REQUIREMENTS.md). This is a draft, not a submitted entry. Submit once through the [official project form](https://docs.google.com/forms/d/e/1FAIpQLSebmyKeBPv2mrmy4T_wI2_z9SBjjSTZ-O-_ewiWs6PBEikRjw/viewform) by **27 September 2026, 19:30 EAT**.

Current status supplied by the team/main workflow on **2026-09-27**: PDF/DOCX/TXT browser upload and in-memory backend are implemented, with editable preview, skill review and manual entry. **57 unittest methods pass. Groq live-tested:** actual model **`openai/gpt-oss-20b`**, four-week plan in **2.27 seconds** in one observed run. Earlier browser/race evidence predates upload; fresh browser tests and demo recording are ongoing. Public deployment awaits Vercel authentication. The outline is ready, but real Felo presentation export is blocked by a missing key. Earlier pitch decks are obsolete. Final links and test evidence will be supplied by the main workflow.

## Exact form fields, in order

### 1. Country

Kenya

### 2. Hackerspace / ONLINE

ONLINE

### 3. Team name

Dhruzzz

### 4. Team leader full name

Eeshan Vaghjiani

### 5. Team leader email

Supply directly in the form from the separately held submission contacts, matching Final Team Confirmation. No contact value is included in this document.

### 6. Project title

Njia

### 7. Team members — full name of each member, one per line

```text
Eeshan Vaghjiani
Bhavin Mepani
Dhruvin Bhudia
```

### 8. Project summary — maximum 150 words

Njia helps Kenyan tech and data job seekers turn existing skills into a practical next learning step. Users upload PDF, DOCX or TXT documents, review editable text and skill suggestions, or enter skills manually. They compare confirmed skills with historical demand, build a four-week plan, try short practice checks and download an evidence report. The prototype uses 18,371 postings from 2023 across ten African and MENA countries, with visible sample sizes and broader-sample fallback. Documents are processed in app-server memory. Optional, explicitly opted-in Groq coaching rewrites structured curriculum while preserving calculated statistics and curated resources; a live openai/gpt-oss-20b call returned a four-week plan in 2.27 seconds. Curated plans remain available without AI consent. Coverage describes advertised skill mentions, not hiring odds or certified competence. Fresh integrated browser checks are ongoing.

### 9. Problem solved

A Kenyan learner targeting a tech or data role needs to decide what to learn next and how to demonstrate progress. Job requirements and learning resources can be difficult to translate into a focused learning plan that fits the time available. Njia connects a user's confirmed skills to visible demand evidence and a concrete weekly activity, practice check and take-away report. This is the problem hypothesis behind the prototype; real Kenyan user feedback and employment outcomes have not yet been established.

### 10. Solution and key features

- **Reviewable skills:** upload a document, paste experience or select skills manually; keyword/alias suggestions can be corrected before analysis.
- **Document input:** PDF, DOCX and UTF-8 TXT browser uploads produce an editable-text preview through `/api/upload`, with processing consent and in-memory parsing. The backend accepts up to **5 MiB**; the frontend caps files at **4,000,000 bytes** to leave room under Vercel's request limit. Scanned PDFs require external OCR. Fresh browser verification is ongoing. Public-app processing occurs on the hosting server, not the user's laptop; previews may contain personal data.
- **Explainable gaps:** canonicalized historical posting counts, top-15 demand-weighted coverage, sample sizes and explicit broader-sample fallback below 50 local postings.
- **Relevant examples:** TF-IDF/cosine retrieval of historical postings, labelled as 2023 examples rather than live vacancies.
- **Actionable learning:** a four-week curated plan with hours, exercises, resources and deliverables. Optional Groq wording enhancement is implemented, mock-tested and live-tested by the main workflow on 2026-09-27: **`openai/gpt-oss-20b`, four weeks in 2.27 seconds** in one observed run. `/api/plan` enforces remote opt-in using `use_ai`/`ai_consent`; curated plans need no AI consent.
- **Practice and evidence:** fixed three-question checks for supported skills and a downloadable Markdown report. These do not certify proficiency.
- **Recovery paths:** manual skills when extraction is unsuitable; complete curated coaching when the model is unavailable or its response fails validation.

### 11. Technologies used

Python; FastAPI; Uvicorn; Pydantic; HTML/CSS/JavaScript; scikit-learn TF-IDF and cosine similarity; HTTPX; python-dotenv; python-multipart; pypdf; Python ZIP/XML parsing for DOCX; unittest; Playwright/Chromium. Bundled JSONL data is attributed to `lukebarousse/data_jobs`. Optional hosted coaching uses Groq's chat-completions API with default and live-tested model `openai/gpt-oss-20b`. The original `llama-3.3-70b-versatile` was unavailable in the account model list, prompting the default change. Optional local Ollama defaults to `qwen2.5:3b` and remains mock-tested only. Inference defaults to offline unless configured.

### 12. Source code URL

**[FINAL_SOURCE_CODE_URL — PENDING CREATION AND JURY-ACCESS CHECK]**

Planned repository: `https://github.com/Eeshan-Vaghjiani/njia`. Publication and jury access remain pending; the main workflow will finalize this link.

### 13. Presentation URL

**[FINAL_PRESENTATION_URL — PENDING FINAL DECK/PDF AND JURY-ACCESS CHECK]**

The [presentation outline](PRESENTATION_OUTLINE.md) is ready. **Real Felo export is blocked by a missing API key**; no completed current deck/export is claimed. Older decks are obsolete and must not be submitted as the current presentation.

### 14. 90-second demo video URL

**[FINAL_90_SECOND_DEMO_VIDEO_URL — PENDING RECORDING, HOSTING AND JURY-ACCESS CHECK]**

A jury-accessible **90-second recorded demo is required**, alongside the source and presentation URLs. Recording is **in progress**; a script or local walkthrough does not satisfy this field.

### 15. Project next step

Finish the ongoing post-upload desktop/mobile checks and demo recording, capture the live Groq result and curated fallback, and finalize jury-accessible source, presentation and video links. Conduct short, consented usability sessions with Kenyan learners or job seekers to measure whether they can identify a useful next learning task, understand coverage, and finish the flow; record actual observations rather than assumed demand. Use that feedback to refine privacy labels, curriculum and mobile interaction, then expand evaluation beyond synthetic examples and refresh the historical data with documented provenance.

### 16. Partner awards — which prizes is your team applying for?

Recommended selections, using the exact checkbox wording:

- **Brightest GmbH — Skills & Employability Award (Brightest Award) | Job-relevant skills and qualifications | Fully paid Brightest vouchers + discounted Brightest voucher pricing, both for ONE WINNING TEAM ONLY; quantity, discount rate and redemption terms TBC**
- **Click Mobile — Mobile-First Impact Award | Mobile-first solutions for Kenyan users, businesses or communities | Total KSh 50,000 cash prize; KENYA ONLY; allocation TBC**
- **Artefact — Data & AI Award | Data into actionable insights or useful AI solutions with measurable business or societal impact | Approx. US$1,040 gift voucher; one winning team; ALL PARTICIPATING COUNTRIES; redemption terms TBC**
- **Thunders — Engineering Excellence Award | Strong, reliable technical prototype | One Mac mini; one team**

These are fit recommendations, not eligibility approvals or award guarantees. Kenya/ONLINE and the roster above are user-supplied; organizer registration/attendance records remain authoritative. Click Mobile's KSh 50,000 is the total Kenya contribution, with allocation unannounced. Country podium consideration is automatic for eligible entries; do not also select the podium-only checkbox.

### 17. Primary prize application — choose the award that best fits your project

**Brightest GmbH — Skills & Employability Award**

### 18. Award application — explain your project’s fit and eligibility

**Brightest GmbH — Skills & Employability Award:** Njia supports job-relevant learning through visible skill gaps, four-week activities, short practice checks and an exportable evidence report, making this our strongest thematic fit. The existing Kenya/Data Analyst walkthrough demonstrates that learning workflow, but does not establish accredited qualifications or improved hiring outcomes. We are a Kenya/ONLINE team; the published award lists no Kenya exclusion, subject to organizer confirmation of eligibility.

**Click Mobile — Mobile-First Impact Award:** Njia targets a practical Kenyan learner need through a browser-based path from skills to learning actions, and recorded Chromium checks cover the core journey at 390 × 844. Our team participates from Kenya/ONLINE, matching the published Kenya-only scope; the newly integrated upload and hosted-coaching journey still needs a fresh mobile demonstration. We claim a mobile-browser prototype, not measured adoption or proven employment impact.

**Artefact — Data & AI Award:** Njia converts 2023 posting data into explainable skill-demand analysis, historical retrieval and learning actions; the canonical Kenya/Data Analyst sample contains 391 postings and gives the example profile 39.6% demand-weighted coverage. The first-stage extraction evaluation records 17 exact matches across 20 developer-authored synthetic examples; separately, a live Groq `openai/gpt-oss-20b` call returned a four-week plan in 2.27 seconds on 2026-09-27—prototype observations, not societal-outcome evidence or broad performance benchmarks. The award explicitly accepts all participating countries, including Kenya, subject to the team's confirmed participation.

**Thunders — Engineering Excellence Award:** Njia demonstrates engineering care through canonicalized calculations, explicit sample fallback, bounded document parsing, server-enforced remote-AI opt-in, provider-output validation and complete curated-plan fallback. Main workflow reports 57 unittest methods passing and a successful live Groq plan; recorded pre-upload desktop/mobile and delayed-response checks provide baseline evidence while fresh integrated browser checks remain ongoing. We are a Kenya/ONLINE team, and no Kenya exclusion is stated in the published award description; final eligibility remains with organizers.

### 19. AI/tool disclosure — list models, agents, datasets, APIs and generated assets used. Explain your chosen stack, access constraints, actual AI contribution and fallback. State honestly if no AI was used. Brev is optional; explain its use only if used. Do not include voucher codes, passwords or API keys.

Njia uses a lightweight Python/FastAPI and static-JavaScript stack so the core workflow can run without inference credentials. Skill extraction uses vocabulary/alias rules; demand is calculated from canonicalized posting rows; related examples use scikit-learn TF-IDF/cosine retrieval; practice checks use fixed answer keys. These components are not generative-model inference.

Optional Groq hosted coaching is implemented and mock-tested. On **2026-09-27**, the main workflow successfully live-tested actual model **`openai/gpt-oss-20b`**, receiving a four-week plan in **2.27 seconds**. The account model list did not offer the original `llama-3.3-70b-versatile`, so the default changed to `openai/gpt-oss-20b`. This is a single integration observation, not an aggregate latency, cost or model-quality evaluation. Access requires a server-held API key, network connectivity and provider availability. The default remains `NJIA_AI_PROVIDER=offline` unless configured. `/api/plan` checks `use_ai`/`ai_consent` server-side before remote generation; curated planning is available without AI consent. Only allowlisted structured curriculum fields are sent to Groq, not raw CV text, identity fields, country/role or demand statistics. Validated output can rewrite titles, tasks and deliverables; calculated statistics, skill targets, hours and curated links remain controlled by application logic. Missing credentials, connection errors, rate limits or invalid output return the complete curated plan. Validation does not guarantee that generated advice is correct.

PDF/DOCX/TXT documents and pasted text are processed in app-server memory; on a public app this means the hosting server, not the user's device. Previews may contain personal information. The first-stage synthetic evaluation's extraction timings and zero inference calls/cost exclude document parsing, HTTP/browser work, retrieval and generation, and do not describe Groq or total operating costs.

Optional local Ollama defaults to `qwen2.5:3b`; its integration is mock-tested but not live-verified. NVIDIA Brev was not used. The bundled source is attributed to `lukebarousse/data_jobs`: 18,371 historical 2023 postings from ten African/MENA countries. Prepared documentation identifies Apache-2.0; provenance and licensing have not been independently verified. The small extraction evaluation uses 20 developer-authored synthetic examples and is not a real-user or fairness study.

AI coding assistance was used for code and documentation. This documentation pass used OpenCode with `github-copilot/gpt-6-astra`; development assistance is distinct from runtime AI. No slides or visual assets were generated in this pass. **[BEFORE SUBMITTING: complete the inventory of other development agents/models and any generated assets actually included in the final build, deck or video; replace this note with verified details.]**

### 20. Final confirmation

Exact required checkbox statement:

> I confirm that our functional prototype, source code, presentation, 90-second demo video, project card details and AI/tool disclosure are complete, accessible and final.

**Pending.** Select only after replacing the final URL placeholders, completing the disclosure inventory, checking jury access and aligning the claims with the demonstrated final build.

## Final handoff

- Required URLs: source, final presentation and **90-second video**, each opened successfully with jury-view access.
- Optional live app: **[FINAL_LIVE_APP_URL — OPTIONAL; PENDING VERCEL AUTHENTICATION]**. A local prototype with run instructions and recorded demo is permitted.
- Complete ongoing integrated desktop/mobile checks and demo recording. Preserve the dated live-model observation above and add final evidence references without describing earlier browser results as post-upload verification.
- Use the dated evidence in [JUDGING_EVIDENCE.md](JUDGING_EVIDENCE.md); derive any final test total from the final run rather than freezing a changing count here.
- Submit the official form by the Kenya deadline and retain the receipt separately. No submission completion is claimed in this draft.
