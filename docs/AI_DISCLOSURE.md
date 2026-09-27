# Njia — AI, data, and validation disclosure

This disclosure describes the implemented FastAPI/static-JavaScript prototype at the 2026-09-27 checkpoint. Earlier plans and pitch decks are not evidence of shipped features. Public deployment is pending Vercel authentication.

## Runtime methods

| Component | Implemented method | Important boundary |
| --- | --- | --- |
| Document input | In-memory PDF/DOCX/UTF-8 TXT parsing with editable preview | Backend up to 5 MiB; frontend 4,000,000 bytes to accommodate Vercel's request limit; no OCR; preview may contain personal data |
| Experience-text extraction | Server-side vocabulary/alias matching with regular-expression boundaries and simple context rules | No language model; suggestions must be reviewed; manual skills available |
| Skill normalization | Lowercasing, explicit alias-to-canonical mapping, and per-posting deduplication | No learned ontology, embedding model, or unrestricted semantic matching |
| Demand and coverage | Counts from historical posting rows; demand-weighted coverage of the top 15 skills | Not proficiency, employability, or hiring probability |
| Historical retrieval | scikit-learn TF-IDF plus cosine similarity over canonical skill tokens | Classical information retrieval, not generative AI or live vacancy search |
| Default learning plan | Curated exercises and links, ordered by highest-demand gaps, with a fourth-week project | No generative model used |
| Optional hosted plan wording | Groq; default `openai/gpt-oss-20b` | Explicit opt-in; live four-week plan observed by main workflow on 2026-09-27 in 2.27 seconds |
| Optional local plan wording | Ollama; configured model defaults to `qwen2.5:3b` | Mock-tested; not installed or live-tested for this build |
| Practice check | Three fixed questions per supported skill and deterministic answer-key scoring | No AI grading, independent verification, or certification |
| Reflection and report | Browser-memory reflection and user-initiated Markdown export | Reflection is not graded; downloads persist as user files |

Supported practice skills are SQL, R, Python, Excel, Power BI, and Docker. A perfect result on three questions does not establish professional competence.

## Optional AI: exact scope

The default `NJIA_AI_PROVIDER=offline` requires no inference service or API key. Groq hosted coaching is implemented but requires configuration and explicit remote-AI opt-in. NVIDIA Brev is not used.

With `NJIA_AI_PROVIDER=groq`, a server-held `GROQ_API_KEY` and an available model, `/api/plan` checks `use_ai` and `ai_consent` server-side before remote generation. Curated plans remain available without AI consent. The main workflow live-tested **`openai/gpt-oss-20b` on 2026-09-27**, receiving a four-week plan in **2.27 seconds**. The original `llama-3.3-70b-versatile` was unavailable in the account's model list, so the default changed to `openai/gpt-oss-20b`. This single successful integration check does not establish typical latency, cost or advice quality.

Setting `NJIA_AI_PROVIDER=ollama` enables a request to the configured local Ollama `/api/chat` endpoint. Only `http`/`https` URLs whose hostname is `localhost`, `127.0.0.1`, or `::1` are accepted. The default URL is `http://127.0.0.1:11434`, and the default model is `qwen2.5:3b`. Njia does not install Ollama or download a model.

Only allowlisted structured curriculum is sent for hosted rewriting: **no raw CV/document text, identities, browser reflections, country/role or demand statistics are sent to Groq**. Raw CV text and browser reflections are not supplied to Ollama either. The model is asked to rewrite titles, three tasks per week, and deliverables. Returned JSON must contain four weeks and correctly typed, length-bounded fields. The code retains the original demand figures, resource links, hours, and targets.

The prompt asks the model not to invent URLs, statistics, employment promises, or spending instructions. Shape/type validation does not guarantee that generated prose obeys every instruction or is accurate. Users should review the wording. Missing credentials, connection errors, rate limits, invalid output, or disallowed Ollama endpoints return the full curated plan. The returned plan's mode indicates whether rewriting succeeded; provider configuration alone does not establish availability.

Mocked tests cover provider output, failure, privacy and validation boundaries, including remote Ollama endpoint rejection. These are distinct from the main workflow's observed live Groq result. Ollama remains mock-tested only; no model-quality evaluation is claimed.

## Data, provenance, and canonicalization

The runtime corpus is `data/africa_jobs_subset.jsonl`, containing **18,371 postings from 2023** for ten African/MENA countries. Preparation selects those countries and rows with non-null skill fields. The source is attributed to [lukebarousse/data_jobs](https://huggingface.co/datasets/lukebarousse/data_jobs).

`data/prepare_data.py` and `data/africa_skill_demand.json` identify the source licence as **Apache-2.0**. This statement reflects the **prepared documentation; source provenance and licensing were not independently verified** during this work. It is not a separate licensing determination for all underlying posting content or Njia's code.

The engine canonicalizes posting skills at load time: lowercases names, maps known aliases such as `powerbi` to `power bi`, and removes duplicates within each posting. The extraction vocabulary is built from those canonicalized rows. Display labels such as “Power BI” are separate from canonical IDs. Runtime counts therefore need not match older, uncanonicalized aggregates in planning materials.

For each selected role, fewer than 50 local postings triggers an explicitly labelled fallback to that role across the combined ten-country sample. It is not a global or fully representative Africa-wide dataset. Demand counts each posting once per skill; coverage weights the user's confirmed top-15 skills by those counts. Retrieval uses the same scope and returns up to three distinct matching historical examples.

Limitations include stale 2023 observations, a tech/data focus, unequal sample sizes, selection based on recorded skills, and broader geography when fallback applies. Postings describe advertised requirements rather than verified worker capabilities or actual hiring outcomes. They do not capture all informal or transferable skills. English-oriented skill tokens and a few multilingual negation cues are not a validated multilingual CV-understanding system.

## Personal information and persistence

- Pasted text and document uploads are processed only after processing consent; manual skill selection avoids submitting CV text entirely. Remote-AI opt-in is separately enforced server-side; curated plans need no AI consent.
- The browser sends raw pasted text/documents to the FastAPI app server. Processing and upload parsing occur in request memory, without application-level persistence. On a local run the server is on the user's computer; on a public app it is the hosting server, **not on-device or laptop-only processing**. This is not a promise about hosting-provider infrastructure or logging.
- Upload returns an editable preview before skill review. PDF, DOCX and UTF-8 TXT are supported; the backend allows up to 5 MiB and the browser caps files at 4,000,000 bytes to leave room under Vercel's request limit. Scanned PDFs need external OCR. The preview is not anonymized and may expose personal details to the person viewing the page.
- Basic redaction removes common email addresses, phone-like numbers, URLs, and identity lines explicitly labelled with terms such as `Name:` or `Address:` before matching. It can miss unlabelled names, addresses, and other sensitive details, or mistake ordinary numbers for phone numbers. **This is not comprehensive anonymization.**
- The frontend uses in-memory state, not localStorage or sessionStorage. CV text stays in the page until cleared or the page is closed/reloaded; the application does not promise secure memory erasure.
- The reflection remains in the browser. Only the selected skill and three answer indices are sent for grading.
- **Clear text** leaves confirmed skills in place. **Reset this session** clears skills and results. Neither removes a previously downloaded file.
- User-triggered Markdown reports contain self-reported skills, market analysis, any plan, practice feedback, and any submitted reflection. They exclude raw CV text. Review the report before sharing.
- `start.ps1` binds to `127.0.0.1` and disables access logs. The app adds no-store and other response headers and rejects POST requests with a mismatched Origin. These are local prototype protections, not a security certification.
- Hosted inference occurs only through configured, opted-in Groq coaching; the default remains offline. No application analytics or automatic publishing is part of the workflow. Clicking an external course or source link opens that third-party site; dependency and optional model downloads also need network access.

## Evaluation and known failure cases

**57 unittest methods passed**, reported by the main workflow at the 2026-09-27 checkpoint, not rerun in this documentation-only pass. Coverage includes calculations, extraction, retrieval, curated plans, upload parsing/validation, hosted-provider privacy and output boundaries, mocked Ollama responses, assessment scoring, and HTTP behavior. Final test timestamps/results will be updated by the main workflow.

The identity-swap check substitutes four names on explicitly labelled identity lines and compares extraction/coverage. This is a narrow regression check, **not an independent bias or fairness audit**.

The first-stage `artifacts/evaluation.json`, generated by `scripts/evaluate.py`, records:

| Metric | Result |
| --- | ---: |
| Synthetic developer-authored CV examples | 20 |
| True positives | 41 |
| False positives | 2 |
| False negatives | 1 |
| Precision | 0.9535 |
| Recall | 0.9762 |
| Exact skill-set matches | 17/20 |
| Warm median / maximum extraction time | 0.97 ms / 15.47 ms |
| Inference API calls / cost | 0 / $0 |

The three imperfect cases expose actual limits: treating the verb “excel” as the Excel skill, missing Excel when only implied by spreadsheet work, and counting Python despite retrospective negation. Simple negation rules can also omit genuine skills in more complex sentences.

These first-stage metrics cover a small, developer-authored synthetic extraction set, not independent real-world CV or upload-parser validation. Precision and recall pool skill-level counts; exact match compares each complete predicted skill set. Timing measures warm extraction after vocabulary initialization, excluding startup, document parsing, HTTP, browser rendering, demand/retrieval work, and optional model generation. Zero inference calls/cost refers to this extraction evaluation, not Groq or total hardware/operating costs.

**Earlier pre-upload browser verification passed.** `scripts/browser_test.py` exercised Chromium at 1440×1100 and 390×844 through extraction, analysis, learning plans, practice grading, report export, reset, sample fallback, and session isolation, recording no JavaScript errors or external page requests in that run. `scripts/race_test.py` passed five earlier delayed-response/state checks. The recorded `artifacts/browser-results.json` and `artifacts/race-results.json` are baseline local development evidence, not verification of later upload/hosted-coaching changes. **Fresh browser tests and demo recording are ongoing; completion is not claimed.**

## Development assistance and scope of claims

AI coding assistance was used in preparing the prototype and its documentation. Development-time assistance is separate from runtime AI: the default app does not call a generative model. Generated code and prose do not establish correctness; the specific tests and artifacts above define the checks reported here.

`GAME_PLAN.md`, `STRATEGY.md`, research notes, and existing decks remain earlier planning materials and do not describe current capabilities reliably. Groq is now implemented and live-tested as scoped above; NVIDIA Brev is not used. The repository is planned at https://github.com/Eeshan-Vaghjiani/njia; publication/access and deployment remain pending, with Vercel authentication blocking public deployment. The presentation outline is ready, but real Felo export is blocked by a missing key. Demo recording is in progress. The main workflow will finalize links and test evidence; no completed submission is claimed.
