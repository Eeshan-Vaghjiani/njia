# Njia — Your CV. A better next move.

Njia is a mobile-first career-coaching prototype for Kenyan tech and data job seekers. The **deployed root is the new CV-to-AI coach**: upload or paste experience, consent to remote processing, and receive a personal career brief with evidence-linked strengths, priorities, draft CV rewrites, seven days of actions and interview practice.

**Team Dhruzzz · Kenya · ONLINE**
**Leader:** Eeshan Vaghjiani · **Members:** Eeshan Vaghjiani, Bhavin Mepani, Dhruvin Bhudia

## Live app and submission assets

- **Live coach:** https://gomycode-2026.vercel.app
- **Source:** https://github.com/Eeshan-Vaghjiani/njia
- **Final presentation, 8 pages — PDF:** https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/Njia-Dhruzzz.pdf
- **Editable PPTX:** https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/Njia-Dhruzzz.pptx
- **90-second demo:** https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/njia-demo-90s.webm
- **Release page:** https://github.com/Eeshan-Vaghjiani/njia/releases/tag/demo-v1

**27 September 2026 handoff:** the new production coach was verified with **48 acceptance assertions + 9 recording assertions = 57 total**, separately from **72 passing unit tests**, as reported by the main workflow. The updated demo is exactly **90.000 seconds**, captioned, and records the real public app and real Groq output. The final eight-page presentation was generated locally with **python-pptx and Playwright**. Release asset uploading is in progress in the main workflow; the final source push is pending. These URLs are the final handoff locations, not a fresh claim that all updated uploads have completed. Submission remains pending.

## What works today

1. **Bring your experience.** Choose a country and target role, then upload PDF, DOCX or UTF-8 TXT, paste 10–15,000 characters, or try the labelled fictional sample. Browser uploads are capped at 4,000,000 bytes; the parser accepts up to 5 MiB. Scanned PDFs require external OCR or pasted text.
2. **Review and consent.** Optional “Preview & edit text first” parses the document on the server without an AI advice request, then requires consent again before coaching. Building directly from an upload parses the file and proceeds to advice under the checked consent.
3. **Build a personal brief.** `/api/advise` sends basic-contact-scrubbed CV text to Groq after server-enforced consent. The actual production model is **`openai/gpt-oss-20b`**. The brief includes a summary, CV-evidence strengths, three market-ranked priorities and first steps, before/after rewrite suggestions, a seven-day checklist, and an interview question with answer guidance.
4. **Check the evidence.** Review suggested skills and confirm edits to recalculate historical market figures. Confirmation updates market evidence only; it does not regenerate the AI brief. Changes to CV or target are labelled as stale until the brief is rebuilt.
5. **Keep a useful next step.** Copy the action checklist or download `njia-career-brief.html`. CV-evidence quotes and the entire before/after rewrite sections are **excluded by default**, with an explicit checkbox to include them. Other personalised advice can still reveal experience details; review before sharing. “Share Njia” shares only the public app link.

If Groq credentials are missing, the provider fails, or output fails validation, the advisor returns a labelled curated brief with keyword evidence, priorities, seven daily actions and interview guidance; it does not fabricate an AI response. Manual skills, curated four-week plans, fixed practice checks and Markdown evidence export remain available in the **older `/classic` experience**.

## CV privacy and AI boundaries

**The new coach sends consented CV text to AI.** `/api/advise` requires `consent=true`, applies basic contact redaction, then sends the resulting CV text, country, role, historical scope/top-skill context, allowed skill IDs and lexicon matches to Groq. Email/phone/link and labelled-identity scrubbing is **not full anonymization**; names, employers or other identifying details may remain. Remove personal details before consenting.

Uploads and pasted text reach the FastAPI server. Parsing and advice processing use request memory without application-level CV persistence; on the public app this is the hosting server, not on-device processing. The browser uses in-memory state, with no account, analytics or user database. This does not guarantee secure erasure or describe hosting/Groq retention policies. Cancelling a browser request may not stop server processing already underway. Downloads persist as user files.

The earlier “CV never goes to a model” boundary applies **only to `/classic` extraction and its `/api/plan` curriculum-rewriting path**, not `/api/advise`. Classic `/api/plan` sends only allowlisted structured curriculum after remote opt-in; it does not send CV text. Its `NJIA_AI_PROVIDER=offline` setting is **not a global off switch for the new advisor**, which independently uses the Groq key.

**Review every generated claim and rewrite.** Validation checks output shape, source quotations, skill vocabulary and some unsupported numbers/tools, but does not guarantee factual accuracy. An observed rewrite invented **“real-time sales monitoring”**. Passing checks do not establish that this or other semantic hallucinations are eliminated. Advice is a draft, not verified qualifications or an employment guarantee.

## Run locally

Python 3.11+ is recommended. The prepared dataset is included.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\start.ps1
```

Open **http://127.0.0.1:8000**. If script execution is blocked:

```powershell
.\.venv\Scripts\python.exe -m uvicorn njia.app:app --host 127.0.0.1 --port 8000 --no-access-log
```

### Linux

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn njia.app:app --host 127.0.0.1 --port 8000 --no-access-log
```

For new-coach AI, configure **`GROQ_API_KEY` on the server** and `GROQ_MODEL=openai/gpt-oss-20b`; `NJIA_ADVISOR_MODEL`, if set, overrides that model for the advisor. The app loads a root `.env` if present. Never put credentials in frontend code or shared files. Installation and hosted inference need network access. With no Groq key, the new advisor returns curated fallback after consent; `/classic` also offers manual skills without submitting a CV.

Classic optional plan rewriting uses `NJIA_AI_PROVIDER=groq` or `ollama`; its default is `offline`. Local Ollama defaults to `qwen2.5:3b`, requires a separately installed service/model, and was mock-tested only, not live-tested. The new advisor does not use Ollama.

## Historical evidence and limitations

The corpus contains **18,371 postings from 2023** across Kenya, Nigeria, Tunisia, Morocco, Algeria, Senegal, Côte d’Ivoire, Saudi Arabia, Egypt and South Africa. It is a historical tech/data sample, not live vacancies or a representative labour-market survey.

- Skills are canonicalized, aliases mapped and duplicates removed within each posting.
- Below **50 local postings** for a role, the engine uses that role across the ten-country sample and labels the broader scope.
- Demand is the percentage of selected-scope postings mentioning each skill.
- Coverage is `100 × mentions of selected skills among the top 15 / all mentions of those top 15 skills`. It measures neither proficiency nor hiring probability.
- Related historical examples use local TF-IDF and cosine similarity. Counts, percentages and ranking are calculated by the application, separately from generated prose.

Prepared data documentation attributes the source to [lukebarousse/data_jobs](https://huggingface.co/datasets/lukebarousse/data_jobs) and identifies Apache-2.0. Provenance and licensing were not independently verified; this is not a licence determination for Njia's code. Genuine user feedback and employment outcomes have not been established.

## Validation and tool disclosure

The latest main-workflow report distinguishes **57 production/recording assertions (48 + 9)** from **72 unit tests**. Earlier 38-check production and four-week-plan recordings describe the older classic workflow, not the current root acceptance run. No tests were rerun in this documentation-only update.

The earlier extraction-only evaluation used 20 developer-authored synthetic CV examples: 41 true positives, 2 false positives, 1 false negative; precision 0.9535, recall 0.9762, and 17/20 exact skill-set matches. Its zero model calls/cost applies only to keyword extraction, not the new coach. These checks are not independent real-user, fairness or model-quality validation; mobile browser evidence is not a physical-phone study.

Development used **OpenCode**, main agent label `github-copilot/gpt-6-astra`, plus coding/review agents in the same harness whose underlying identities were not independently established. UI visuals are code-native HTML/CSS. The final deck was generated locally with **python-pptx + Playwright**, **not Felo or Gemini**. Gemini access was rejected with **HTTP 403 (suspended key)**; Gemini was never used for inference. NVIDIA Brev was not used. The captioned demo records real public-app behaviour and real Groq output, without fabricated responses or synthetic voice.

## Project map

- `njia/app.py`: API, `/` coach and `/classic` routes.
- `njia/advisor.py`: consented-CV Groq assessment, validation and curated fallback.
- `njia/engine.py`: corpus, keyword extraction, demand and historical retrieval.
- `njia/uploads.py`: in-memory document parsing.
- `njia/coaching.py`, `njia/assessment.py`: classic plans and fixed practice checks.
- `static/coach.html`, `static/coach.js`, `static/coach.css`: new root interface.
- `tests/`, `scripts/`, `artifacts/`: checks and local evidence; `artifacts/` is Git-ignored.
- [20-field submission draft](docs/SUBMISSION_DRAFT.md), [AI disclosure](docs/AI_DISCLOSURE.md), [final checklist](docs/FINAL_CHECKLIST.md).

Earlier planning documents and classic-flow evidence may describe superseded features. Use this README and the three final documents above for current submission claims. The source and live URLs are unchanged; final source publication is pending in the main workflow.
