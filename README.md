# Njia — Your CV. A better next move.

**[Live app](https://gomycode-2026.vercel.app) · [Source](https://github.com/Eeshan-Vaghjiani/njia) · [Presentation PDF](https://github.com/Eeshan-Vaghjiani/njia/blob/main/presentation/Njia-Dhruzzz.pdf) · [90-second demo](https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/njia-demo-90s.webm)**

A mobile-first career coach for Kenyan tech and data job seekers. Turn experience into evidence-linked strengths, draft CV improvements and a practical week of next steps.

**Team Dhruzzz · Kenya · ONLINE**
Eeshan Vaghjiani (lead), Bhavin Mepani and Dhruvin Bhudia. Primary award: **Click Mobile — Mobile-First Impact Award**.

## The problem

Job seekers can struggle to explain their experience, identify useful skill gaps and decide what to practise next. Generic advice rarely connects their CV, a target role and tomorrow’s action. Njia brings these decisions into one browser journey.

## How it works

1. Choose a country and target role. Upload PDF/DOCX/TXT, paste experience, or try the labelled fictional sample.
2. Review the text and consent to AI processing. Groq builds a personal brief with strengths, three priorities, draft rewrites, seven daily actions and interview guidance.
3. Review suggested skills and recalculate historical market evidence. Changing skills updates the figures; changing CV/target requires rebuilding the AI brief.
4. Copy the checklist or download an HTML brief. CV-evidence quotes and rewrite sections are excluded by default; other personalised advice can still reveal experience details.

**Try it:** open the live app → choose the sample → review and consent → build your brief → inspect the priorities and download. If the provider is unavailable or its output fails validation, Njia returns a clearly labelled curated brief.

## Screenshots

Actual public-app captures using a clearly labelled synthetic CV; cropped for readability.

![Njia coach in a desktop browser](docs/images/coach-desktop.png)

<details>
<summary>View the mobile experience</summary>

<img src="docs/images/coach-mobile.png" alt="Njia coach in a mobile browser" width="320">

</details>

## Quick start

Use **Python 3.12 or 3.13**. The prepared dataset is included.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn njia.app:app --host 127.0.0.1 --port 8000 --no-access-log
```

Open **http://127.0.0.1:8000**. On Linux/macOS, use `python3` to create the environment and `.venv/bin/python` for subsequent commands.

The app loads a root `.env` when present; use `.env.example` as a reference. For AI coaching, set these **server-side**:

```dotenv
GROQ_API_KEY=your_server_side_key
GROQ_MODEL=openai/gpt-oss-20b
```

`NJIA_ADVISOR_MODEL`, if set, overrides the advisor model. Without a Groq key, the coach uses curated fallback and still requires consent. `NJIA_AI_PROVIDER=offline` controls only the older `/classic` planning flow; it does not disable the new advisor. Installation and hosted inference need network access.

## Evidence and tests

**73 backend tests passed**, separately from **57 public-app assertions: 48 acceptance + 9 recording**. The published captioned demo is **90.000 seconds** and shows real public-app interaction and Groq `openai/gpt-oss-20b` output.

Run the backend suite:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

These are engineering checks, not independent model-accuracy or employment-outcome studies. Mobile browser checks are not physical-phone user research. Next: consented Kenyan usability sessions, broader rewrite-faithfulness evaluation and refreshed market data.

## Privacy and limitations

- **Consented CV text goes to Groq.** Basic contact scrubbing is best effort, not anonymization; names, employers and other identifying details may remain. Remove sensitive details before consenting.
- Uploads are parsed on the hosting server. The app uses request/browser memory with **no application-level CV storage**, accounts, analytics or user database. This does not describe hosting/Groq retention or guarantee secure erasure. Downloads remain on the user’s device.
- **Review every generated claim.** Validation cannot eliminate hallucinations; an observed rewrite invented “real-time sales monitoring.” Suggestions are drafts, with no factual, qualification or employment guarantee.
- Evidence comes from **18,371 historical 2023 tech/data postings across ten African/MENA countries**, not live vacancies or a representative labour-market survey. Below 50 local role postings, Njia labels a broader ten-country sample. Coverage measures top-15 skill demand, not proficiency or hiring odds.
- Prepared data documentation attributes the corpus to [lukebarousse/data_jobs](https://huggingface.co/datasets/lukebarousse/data_jobs) and identifies Apache-2.0; provenance/licensing were not independently verified.
- Browser uploads are capped at 4,000,000 bytes; the parser accepts 5 MiB. Scanned PDFs need external OCR or pasted text.

## Stack and documentation

Python/FastAPI, static HTML/CSS/JavaScript, Groq, scikit-learn historical retrieval, unittest and Playwright; hosted on Vercel. OpenCode assisted coding, documentation and review. The eight-page deck was generated locally with python-pptx and Playwright. See the disclosure for actual AI use and boundaries.

- [Deployment](docs/DEPLOYMENT.md) · [AI and data disclosure](docs/AI_DISCLOSURE.md)
- [Submission answers](docs/SUBMISSION_DRAFT.md) · [Final checklist](docs/FINAL_CHECKLIST.md) · [Official requirements](docs/HACKATHON_REQUIREMENTS.md)
- [Ready voiceover script](docs/VOICEOVER.md) · [Release assets](https://github.com/Eeshan-Vaghjiani/njia/releases/tag/demo-v1)

**Submission status:** source, presentation and demo are published; the official form has **not been submitted**.
