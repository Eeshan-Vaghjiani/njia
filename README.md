# Njia — Your skills. Your market. Your path.

Njia is a career-coaching prototype built with **FastAPI and static JavaScript**. It compares self-reported skills with historical tech/data job postings, suggests a four-week learning path, and offers short practice checks and a downloadable Markdown evidence report.

**Team Dhruzzz · Kenya · ONLINE:** Eeshan Vaghjiani, Bhavin Mepani, Dhruvin Bhudia. Planned repository: https://github.com/Eeshan-Vaghjiani/njia (publication/access pending). Public deployment is pending Vercel authentication; demo recording is in progress. The presentation outline is ready, but Felo export is blocked by a missing API key. Final links and test evidence will be supplied by the main workflow.

The default experience uses local lexicon extraction, deterministic demand calculations, TF-IDF retrieval, and curated learning activities. **No hosted inference API, API key, NVIDIA Brev, or generative model is required.**

## Run locally

Run these commands from the project root with Python available. Python 3.11+ is a practical choice for a new environment.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\start.ps1
```

Open **http://127.0.0.1:8000**. Keep the terminal running; press `Ctrl+C` to stop. Activation is unnecessary: `start.ps1` uses the project's virtual-environment Python, binds to loopback, and disables access logs.

If local PowerShell policy blocks the script, the equivalent direct command is:

```powershell
.\.venv\Scripts\python.exe -m uvicorn njia.app:app --host 127.0.0.1 --port 8000 --no-access-log
```

### Linux

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn njia.app:app --host 127.0.0.1 --port 8000 --no-access-log
```

The prepared dataset is included; no data download or preparation step is needed to run the app. Package installation needs network access. Once installed, the default workflow runs locally; opening a learning-resource or dataset link visits an external website.

## What works today

1. **Choose a market and role.** Options come from the bundled dataset.
2. **Confirm your skills.** Upload a PDF, DOCX or UTF-8 TXT document, review/edit its text preview, then review the suggested skills. Alternatively, paste 10–15,000 characters of experience or select skills manually without submitting a CV. Text/document processing requires consent. The upload backend parses in memory and accepts up to **5 MiB**; the frontend caps files at **4,000,000 bytes** to leave room under Vercel's request limit. Scanned PDFs need external OCR. The synthetic example uses Kenya / Data Analyst. Skill chips can be removed or supplemented.
3. **Inspect your skill gap.** View demand counts, percentages, sample size, demand-weighted coverage, and missing skills among the top 15 for the selected market and role. Empty skill profiles are supported.
4. **See related historical postings.** Local TF-IDF and cosine similarity retrieve up to three distinct examples with overlapping skills. These are 2023 examples, not current vacancies or hiring recommendations.
5. **Create a four-week plan.** Choose hours per week; receive demand-ranked exercises, resource links, and deliverables. Curated plans require no AI consent. Configured Groq coaching can optionally rewrite plan wording after explicit remote-AI opt-in. Week completion is tracked only in the current page session.
6. **Practice and export.** SQL, R, Python, Excel, Power BI, and Docker each have three fixed multiple-choice questions with answer-key feedback. An optional reflection stays in browser memory and is not graded. Download `njia-skill-evidence.md` with the analysis and any generated plan or completed practice result.

Changing the market, role, or confirmed skills clears earlier results. **Clear text** removes the pasted experience while keeping confirmed skills; **Reset this session** clears skills and results as well.

## How the evidence is calculated

- **Canonicalization:** posting skills are lowercased, known aliases are mapped to canonical IDs, and duplicates within each posting are removed. Examples include `PowerBI` → `power bi`, `postgres` → `postgresql`, and `k8s` → `kubernetes`. Extraction matches this vocabulary and aliases with boundaries and simple context/negation rules; it does not infer arbitrary skills or use embeddings.
- **Scope:** when a country/role has fewer than **50** postings, analysis and retrieval use that role's combined **10-country Africa/MENA sample**. The interface shows the local count and expanded scope.
- **Demand:** a skill's percentage is the share of selected-scope postings mentioning it, counting each posting at most once per skill.
- **Coverage:** `100 × mentions of confirmed skills among the top 15 / all mentions of those top 15 skills`. This is neither tested proficiency nor a probability of employment.
- **Retrieval:** TF-IDF vectors represent canonical posting skills, with cosine similarity used for ranking. No LLM or hosted search service is involved.

## Data and limitations

The application loads `data/africa_jobs_subset.jsonl`: **18,371 historical 2023 postings** across Kenya, Nigeria, Tunisia, Morocco, Algeria, Senegal, Côte d'Ivoire, Saudi Arabia, Egypt, and South Africa. Kenya contributes 1,326 postings across roles.

Prepared source documentation in `data/prepare_data.py` and `data/africa_skill_demand.json` attributes the dataset to [lukebarousse/data_jobs on Hugging Face](https://huggingface.co/datasets/lukebarousse/data_jobs) and identifies **Apache-2.0**. This is an attribution/licence statement from the prepared documentation, **not independently verified provenance or licensing**. It does not establish a licence for Njia's application code.

The preparation script filters selected countries and rows with non-null skill fields. The runtime recalculates demand from canonicalized posting rows rather than using the older aggregate JSON. These tech/data postings are not a representative survey of all employers, workers, informal work, or current demand. Expanding a small sample improves sample size but reduces local specificity. Keyword mentions and short quizzes do not establish competence; Njia issues **no certification**.

## Privacy and optional AI

Raw experience text and uploaded documents are sent to the app server and processed in request memory, without application-level persistence or submission to a model. When run locally, that server is on your computer; on a public deployment, it is the hosting server, **not laptop-only or on-device processing**. Document previews may contain personal information. The frontend keeps session state in memory, without localStorage/sessionStorage, accounts, analytics, or a user database. Text remains in the page until cleared; this is not a secure-erasure guarantee or a claim about hosting-provider infrastructure.

Basic redaction removes email addresses, phone-like numbers, links, and explicitly labelled identity lines before extraction. It can miss personal details and remove unrelated numbers; it is **not full anonymization**. Downloaded reports are intentionally saved files and include confirmed skills and any submitted practice reflection, but not raw CV text.

The default `NJIA_AI_PROVIDER=offline` needs no inference credentials. Optional providers are documented in `.env.example`; configure them in the server environment. The app also loads a root `.env` if present.

**Hosted Groq is implemented and live-tested by the main workflow on 2026-09-27:** the actual model `openai/gpt-oss-20b` returned a four-week plan in **2.27 seconds** in one observed run. The account's model list did not offer the original `llama-3.3-70b-versatile`, so the default was changed to `openai/gpt-oss-20b`. This is a single integration observation, not a latency benchmark or quality evaluation. Set `NJIA_AI_PROVIDER=groq`, a server-held `GROQ_API_KEY`, and `GROQ_MODEL=openai/gpt-oss-20b` to configure it.

Remote generation requires explicit opt-in: `/api/plan` checks `use_ai` and `ai_consent` server-side. Curated plans remain available without consent. Only allowlisted structured curriculum is sent to Groq, **not CV text, identities, country/role or demand statistics**. The server-held API key must never be exposed in browser code or public documentation.

For optional local Ollama:

```dotenv
NJIA_AI_PROVIDER=ollama
NJIA_OLLAMA_URL=http://127.0.0.1:11434
NJIA_OLLAMA_MODEL=qwen2.5:3b
```

This requires a separately installed, running Ollama and a downloaded model (`ollama pull qwen2.5:3b`). **Ollama was not installed or live-tested for this build.** Its integration is covered by mocked tests only. No model is downloaded or started by Njia.

Optional models rewrite only plan titles, tasks, and deliverables from structured curriculum. Statistics, skill targets, hours, and resource links remain deterministic. The Ollama endpoint must use a loopback hostname; this restriction does not apply to the separate hosted Groq integration. Missing credentials, connection failures, rate limits or invalid output return the complete curated plan. `NJIA_AI_PROVIDER=offline` restores the default. A configured-provider label does not prove model availability; the returned plan identifies the mode that actually ran.

See [AI disclosure](docs/AI_DISCLOSURE.md) for boundaries and validation details.

## Checks and recorded results

From the project root, run:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe scripts/evaluate.py
```

**57 unittest methods passed**, as reported by the main workflow at the 2026-09-27 checkpoint; this documentation-only update did not rerun them. Coverage includes calculations, extraction, retrieval, plans, upload parsing/validation, hosted-provider privacy and output boundaries, mocked Ollama behavior, practice grading, and HTTP protections. The limited identity-swap test is not a fairness audit.

The first-stage `artifacts/evaluation.json` records:

| Extraction metric | Recorded value |
| --- | ---: |
| Synthetic developer-authored CV examples | 20 |
| True positives / false positives / false negatives | 41 / 2 / 1 |
| Precision | 0.9535 |
| Recall | 0.9762 |
| Exact skill-set matches | 17/20 |
| Warm median extraction time | 0.97 ms |
| Warm maximum extraction time | 15.47 ms |
| Inference API calls / cost | 0 / $0 |

This is a first-stage, small synthetic extraction check, not independent validation, upload-parser evaluation or an end-to-end speed benchmark. Timing excludes corpus startup, document parsing, HTTP/browser work, retrieval, and optional generation. Zero inference calls/cost applies only to that extraction run, not hosted Groq or total operating costs. Re-running `scripts/evaluate.py` overwrites the artifact and may change timing.

For Chromium checks, keep the local server running in a separate terminal:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\python.exe scripts/browser_test.py
```

On Linux, use `.venv/bin/python` for these commands; Chromium may also require Playwright's system dependencies. **Earlier, pre-upload Chromium verification passed** at desktop 1440×1100 and mobile 390×844, with no JavaScript errors or external page requests in that run. It exercised extraction, analysis, plans, progress, practice grading, report downloads, sample fallback, manual/empty skills, reset, and session isolation. Screenshots and results are in `artifacts/`. **Fresh post-upload browser checks and demo recording are ongoing; completion is not yet claimed.**

Five earlier, pre-upload asynchronous regression checks passed, deliberately delivering held responses after newer user actions: clear-during-extraction, competing plans, assessment restart, competing grades, and preserving answers across tabs. These do not establish post-upload regression status. Run them against the local server with:

```powershell
.\.venv\Scripts\python.exe scripts/race_test.py
```

## Project map

- `njia/app.py`: FastAPI endpoints and static frontend serving; local API reference at `/docs`.
- `njia/engine.py`: corpus, canonicalization, extraction, demand, and retrieval.
- `njia/coaching.py`: curated curriculum and optional Groq/Ollama rewriting.
- `njia/uploads.py`: in-memory PDF/DOCX/TXT parsing for editable previews.
- `njia/assessment.py`: fixed practice questions and grading.
- `static/`: HTML, CSS, and JavaScript interface.
- `tests/`, `scripts/`, `artifacts/`: automated checks, evaluation, and recorded outputs.
- [90-second demo](docs/DEMO.md) and [AI disclosure](docs/AI_DISCLOSURE.md).

`GAME_PLAN.md`, `STRATEGY.md`, research notes, and existing pitch decks are earlier planning material, not current capability evidence. Use the current source, these docs, and [presentation outline](docs/PRESENTATION_OUTLINE.md) for claims. Groq is implemented; NVIDIA Brev is not used. Public deployment, final presentation export, final links and submission remain pending.
