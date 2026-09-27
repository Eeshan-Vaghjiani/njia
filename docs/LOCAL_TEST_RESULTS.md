# Local and production verification — 27 September 2026

Recorded local environment: Windows, Python 3.13.2, project virtual environment, Chromium 140 through Playwright 1.55.0; app served at `http://127.0.0.1:8000`. Current unit, desktop/mobile browser, race, upload/Groq and video results were supplied by the main workflow on 2026-09-27; this documentation-only pass did not rerun them.

## Public deployment checkpoint

Main workflow reports the app live at **https://gomycode-2026.vercel.app** on 2026-09-27. Anonymous `/api/health` returned **HTTP 200**, **18,371 postings**, and configured Groq model **`openai/gpt-oss-20b`**. Vercel project: `eeshans-projects-0934fb87/gomycode-2026`. CLI source deployment succeeded; automatic GitHub connection failed, so automatic deployment is not configured. See [deployment details](DEPLOYMENT.md).

**Public browser verification PASS: 38/38 checks** in `artifacts/deployed-results.json`, **2026-09-27T10:25:42.307Z–2026-09-27T10:26:00.536Z**. Fresh anonymous Chromium desktop **1440×1100** and touch-mobile **390×844** contexts used synthetic inputs and **zero mocked responses**.

| Production check | Recorded result |
| --- | --- |
| Public resources | Homepage, health, metadata, JS/CSS and sample TXT download passed |
| Desktop document flow | Actual PDF upload, preview editing, upload/extraction consent gates and lexicon extraction passed; Excel, Power BI, SQL → Kenya/Data Analyst **391 postings / 39.6%** |
| Curated default | Four weeks, `mode=curated`, AI opt-in unchecked (`use_ai=false`, `ai_consent=false`) |
| Real hosted coaching | Exactly **one** opted-in request; HTTP 200, **`mode=groq`**, **`openai/gpt-oss-20b`**, **four weeks in 1.831 s**; API response and rendered UI evidence, not provider logs or a benchmark |
| Practice/export | SQL **3/3**; downloaded `njia-skill-evidence.md` includes plan, model, coverage, grade, reflection and limitations, excludes raw CV; reflection not sent for grading |
| Fresh mobile flow | Actual TXT upload → edited/reviewed preview → consent-gated extraction → Kenya **391 / 39.6%** gap; no horizontal overflow |
| Observed errors | **0** JavaScript errors, console errors, failed requests and HTTP 403s; same-origin HTTPS requests, all observed HTTP responses successful |

Production captures: `artifacts/public-ai.png`, `artifacts/public-practice.png`, `artifacts/public-mobile.png`. Production scope excludes DOCX, near-limit uploads, unrelated-Origin rejection, provider-failure fallback, mobile plan/download and physical phones. Prior local results below retain their own scope; this documentation update did not rerun checks.

## Completed local checks and published deliverables

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

`artifacts/` is Git-ignored, so these are local paths. The main workflow is publishing JSON evidence and screenshots to the existing [demo-v1 release](https://github.com/Eeshan-Vaghjiani/njia/releases/tag/demo-v1); only attached assets are publicly downloadable.

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

**Local desktop/mobile core, all five race checks, desktop upload, dedicated mobile TXT upload and real Groq browser checks passed; the demo recording is complete.** Production additionally passed the 38 checks above. Mobile PDF/DOCX and physical-phone upload remain unverified. Genuine user feedback remains pending. Production UTC timestamps are recorded above; an exact build reference and local test time-of-day were not supplied.

Public repository: https://github.com/Eeshan-Vaghjiani/njia (anonymous access verified). Published video: https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/njia-demo-90s.webm; [release page](https://github.com/Eeshan-Vaghjiani/njia/releases/tag/demo-v1). Anonymous direct-asset HEAD returned **200**, **3,498,819 bytes**. The [Vercel app](https://gomycode-2026.vercel.app) passed the scoped production browser checks. The presentation remains outline-only: final Felo export is blocked by missing `FELO_API_KEY`. Submission remains pending.

## Model boundary

The default remains `NJIA_AI_PROVIDER=offline` unless configured: extraction is lexicon-based, retrieval is TF-IDF/cosine, demand is arithmetic, and the plan is curated. Production Groq `openai/gpt-oss-20b` passed with actual `mode=groq` above. The account model list did not offer the original `llama-3.3-70b-versatile`, prompting the model change. `/api/plan` checks `use_ai` and `ai_consent` server-side; curated plans remain available without AI consent. Only allowlisted structured curriculum goes to Groq, not CV text, identities, country/role or demand statistics. The earlier 2.27-second and fresh production 1.831-second observations are separate runs, not an aggregate latency or model-quality evaluation; no hosted cost measurement is claimed.

The optional local Ollama integration has mocked success/failure/malformed-output tests, but no live Ollama model was installed or tested. Runtime labels and downloaded reports disclose which path actually ran.

These checks do not establish broad CV accuracy, fairness, certification, production readiness, or live labour-market coverage.
