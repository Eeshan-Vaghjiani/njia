# Local verification — 27 September 2026

Recorded local environment: Windows, Python 3.13.2, project virtual environment, Chromium 140 through Playwright 1.55.0; app served at `http://127.0.0.1:8000`. Current unit, desktop/mobile browser, race, upload/Groq and video results were supplied by the main workflow on 2026-09-27; this documentation-only pass did not rerun them.

## Completed checks

| Check | Result |
| --- | --- |
| `python -m unittest discover -s tests -v` | **57 test methods passed**, reported by main workflow; includes upload/provider boundary coverage |
| Live Groq plan | Main workflow observed **openai/gpt-oss-20b**, four-week plan in **2.27 seconds**, 2026-09-27; single run, not a benchmark |
| `python scripts/upload_browser_test.py` | Desktop **PDF, DOCX and TXT passed** upload → editable preview → extraction → analysis; live Groq passed |
| Desktop upload errors | **Passed** invalid-file, oversize, scanned-PDF and consent-error handling; scans require external OCR |
| `python scripts/mobile_upload_test.py` | **Passed** current-build Chromium mobile emulation at **390×844, touch=True**: actual synthetic TXT upload with processing consent → preview → extraction → Kenya gap (**39.6%**) → four-week curated plan → Markdown download; **0 model calls, 0 JavaScript errors**, horizontal-overflow assertion passed at analysis |
| Real Groq in-browser | **Passed** with actual model **`openai/gpt-oss-20b`**; distinct from the separately timed live call above |
| Completed demo artifact | `artifacts/njia-demo-90s.webm`: **90.000 seconds exactly, 1280 × 720**, normal-speed actual CV upload and real Groq recording, silent with Playwright captions; no fabricated screenshots/output or synthetic voice |
| Public repository | Creation and public access verified: https://github.com/Eeshan-Vaghjiani/njia |
| `node --check static/app.js` | Earlier recorded pass; not a fresh post-upload check |
| `python scripts/browser_test.py` | Latest rerun on **current build passed** desktop **1440×1100** and mobile **390×844** core flows |
| Browser JavaScript errors / external page requests | **0 / 0** in the current-build run |
| `python scripts/race_test.py` | Latest rerun on **current build passed all 5** delayed-response and state regression checks |
| `python scripts/evaluate.py` | First-stage extraction: 20 synthetic CV examples; 17 exact skill-set matches |

First-stage extraction evaluation: 41 true positives, 2 false positives, 1 false negative; 95.35% precision and 97.62% recall. Warm median/maximum extraction was 0.97/15.47 ms in the recorded run. This small developer-authored set is not independent validation or an upload-parser test. Timing excludes startup, document parsing, HTTP/browser work, retrieval and generation. Its zero inference calls/$0 inference cost apply only to extraction, not Groq or operating costs. Known failures include ambiguity (“excel” as a verb), implied software skills, and retrospective negation. Users must review extracted skills.

## Current core end-to-end evidence

The sample Kenya / Data Analyst profile confirms Excel, SQL, and Power BI. The dataset has 391 Kenya Data Analyst postings; those three skills cover 39.6% of demand-weighted mentions among the top 15 skills. The walkthrough generates a four-week plan, completes a SQL practice check, and downloads a Markdown report containing the analysis, plan, and practice feedback without raw CV text.

Local artifacts:

- `artifacts/desktop-welcome.png`
- `artifacts/desktop-analysis.png`
- `artifacts/mobile-analysis.png`
- `artifacts/njia-skill-evidence.md`
- `artifacts/evaluation.json`
- `artifacts/browser-results.json`
- `artifacts/race-results.json`
- `artifacts/mobile-upload-results.json`
- `artifacts/mobile-upload-plan.png`

`artifacts/` is Git-ignored, so these are local paths, not public repository links. Selected JSON evidence is planned for the [demo-v1 release](https://github.com/Eeshan-Vaghjiani/njia/releases/tag/demo-v1); only assets actually attached there are publicly downloadable.

## Dedicated mobile TXT upload evidence

The current-build **PASS** covers an actual synthetic TXT file through the upload endpoint in Chromium mobile emulation (**390×844, touch=True**), processing consent, text preview, extraction of three skills, Kenya analysis showing **39.6%** coverage, four curated weeks and a download named `njia-skill-evidence.md`. The JSON records **0 model calls** and an empty JavaScript-error list. The script asserts no horizontal overflow at the analysis step and captures the plan in `artifacts/mobile-upload-plan.png`.

This check does not verify PDF/DOCX uploads on mobile, physical-phone/native file-picker interaction, preview editing, or mobile upload error recovery. Desktop PDF/DOCX/TXT and error-path results remain separate evidence.

With the local server running and Playwright/Chromium installed as described in the [README](../README.md#checks-and-recorded-results), run from the project root:

```powershell
.\.venv\Scripts\python.exe scripts/mobile_upload_test.py
```

On Linux, use `.venv/bin/python scripts/mobile_upload_test.py`. The script defaults to `http://127.0.0.1:8000`; `NJIA_TEST_URL` can select another running instance. A rerun overwrites the mobile JSON and screenshot artifacts.

## Current verification and remaining deliverables

PDF/DOCX/UTF-8 TXT upload is implemented through the browser and memory-based backend, with an editable preview and reviewable/manual skills. The backend accepts up to **5 MiB**; the frontend caps files at **4,000,000 bytes** to leave room under Vercel's request limit. Scanned PDFs need external OCR. Application-server processing means the hosting server on a public app, not the user's laptop; preview text may contain personal data.

**Current desktop/mobile core, all five race checks, desktop upload, dedicated mobile TXT upload and real Groq browser checks passed; the demo recording is complete.** Mobile PDF/DOCX and physical-phone upload remain unverified. Genuine user feedback remains pending. No exact build reference or time-of-day was supplied.

Public repository: https://github.com/Eeshan-Vaghjiani/njia (anonymous access verified). Published video: https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/njia-demo-90s.webm; [release page](https://github.com/Eeshan-Vaghjiani/njia/releases/tag/demo-v1). Anonymous direct-asset HEAD returned **200**, **3,498,819 bytes**. Deployment awaits Vercel login; instructions have been provided. The presentation outline is ready, but no current deck has been generated: Felo export needs an API key. Submission remains pending.

## Model boundary

The default remains `NJIA_AI_PROVIDER=offline` unless configured: extraction is lexicon-based, retrieval is TF-IDF/cosine, demand is arithmetic, and the plan is curated. Optional Groq is implemented and live-tested as recorded above. The account model list did not offer the original `llama-3.3-70b-versatile`, so the default changed to `openai/gpt-oss-20b`. `/api/plan` checks `use_ai` and `ai_consent` server-side; curated plans remain available without consent. Only allowlisted structured curriculum goes to Groq, not CV text, identities, country/role or demand statistics. The 2.27-second observation is not an aggregate latency or model-quality evaluation; no hosted cost measurement is claimed.

The optional local Ollama integration has mocked success/failure/malformed-output tests, but no live Ollama model was installed or tested. Runtime labels and downloaded reports disclose which path actually ran.

These checks do not establish broad CV accuracy, fairness, certification, production readiness, or live labour-market coverage.
