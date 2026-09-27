# Local verification — 27 September 2026

Earlier local verification environment: Windows, Python 3.13.2, project virtual environment, Chromium 140 through Playwright 1.55.0; app served on loopback at `http://127.0.0.1:8000`. Current unit/live-Groq results below were supplied by the main workflow on 2026-09-27 and were not rerun in this documentation-only pass. No Brev use or completed deployment/submission is claimed.

## Completed checks

| Check | Result |
| --- | --- |
| `python -m unittest discover -s tests -v` | **57 test methods passed**, reported by main workflow; includes upload/provider boundary coverage |
| Live Groq plan | Main workflow observed **openai/gpt-oss-20b**, four-week plan in **2.27 seconds**, 2026-09-27; single run, not a benchmark |
| `node --check static/app.js` | Earlier recorded pass; not a fresh post-upload check |
| `python scripts/browser_test.py` | Earlier pre-upload desktop 1440×1100 and mobile 390×844 flows passed |
| Browser errors / external page requests | 0 / 0 in that earlier browser run |
| `python scripts/race_test.py` | 5 earlier pre-upload delayed-response and state regression checks passed |
| `python scripts/evaluate.py` | First-stage extraction: 20 synthetic CV examples; 17 exact skill-set matches |

First-stage extraction evaluation: 41 true positives, 2 false positives, 1 false negative; 95.35% precision and 97.62% recall. Warm median/maximum extraction was 0.97/15.47 ms in the recorded run. This small developer-authored set is not independent validation or an upload-parser test. Timing excludes startup, document parsing, HTTP/browser work, retrieval and generation. Its zero inference calls/$0 inference cost apply only to extraction, not Groq or operating costs. Known failures include ambiguity (“excel” as a verb), implied software skills, and retrospective negation. Users must review extracted skills.

## Earlier pre-upload end-to-end evidence

The sample Kenya / Data Analyst profile confirms Excel, SQL, and Power BI. The dataset has 391 Kenya Data Analyst postings; those three skills cover 39.6% of demand-weighted mentions among the top 15 skills. The walkthrough generates a four-week plan, completes a SQL practice check, and downloads a Markdown report containing the analysis, plan, and practice feedback without raw CV text.

Local artifacts:

- `artifacts/desktop-welcome.png`
- `artifacts/desktop-analysis.png`
- `artifacts/mobile-analysis.png`
- `artifacts/njia-skill-evidence.md`
- `artifacts/evaluation.json`
- `artifacts/browser-results.json`
- `artifacts/race-results.json`

## Current implementation and pending verification

PDF/DOCX/UTF-8 TXT upload is implemented through the browser and memory-based backend, with an editable preview and reviewable/manual skills. The backend accepts up to **5 MiB**; the frontend caps files at **4,000,000 bytes** to leave room under Vercel's request limit. Scanned PDFs need external OCR. Application-server processing means the hosting server on a public app, not the user's laptop; preview text may contain personal data.

**Fresh post-upload browser tests and demo recording are ongoing.** Earlier browser/race artifacts must not be presented as completed checks of the new integrated flow. The main workflow will supply final build references, test timestamps/results and links later.

Planned repository: https://github.com/Eeshan-Vaghjiani/njia (publication/access pending). Public deployment is pending Vercel authentication. The presentation outline is ready; real Felo export is blocked by a missing key.

## Model boundary

The default remains `NJIA_AI_PROVIDER=offline` unless configured: extraction is lexicon-based, retrieval is TF-IDF/cosine, demand is arithmetic, and the plan is curated. Optional Groq is implemented and live-tested as recorded above. The account model list did not offer the original `llama-3.3-70b-versatile`, so the default changed to `openai/gpt-oss-20b`. `/api/plan` checks `use_ai` and `ai_consent` server-side; curated plans remain available without consent. Only allowlisted structured curriculum goes to Groq, not CV text, identities, country/role or demand statistics. The 2.27-second observation is not an aggregate latency or model-quality evaluation; no hosted cost measurement is claimed.

The optional local Ollama integration has mocked success/failure/malformed-output tests, but no live Ollama model was installed or tested. Runtime labels and downloaded reports disclose which path actually ran.

These checks do not establish broad CV accuracy, fairness, certification, production readiness, or live labour-market coverage.
