# Njia — Your CV. A better next move.

**[Live app](https://gomycode-2026.vercel.app) · [Source](https://github.com/Eeshan-Vaghjiani/njia) · [Presentation PDF](https://github.com/Eeshan-Vaghjiani/njia/blob/main/presentation/Njia-Dhruzzz.pdf) · [90-second demo](https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/njia-demo-90s.webm)**

A mobile-first career coach for Kenyan tech and data job seekers. Njia asks what your CV doesn't say, turns your experience into evidence-linked strengths and a practical week, matches you to **live jobs you can apply for**, and preps you with **real interview questions found on the web**.

**Team Dhruzzz · Kenya · ONLINE**
Eeshan Vaghjiani (lead), Bhavin Mepani and Dhruvin Bhudia. Primary award: **Click Mobile — Mobile-First Impact Award**.

## The problem

Job seekers can struggle to explain their experience, identify useful skill gaps, find openings they are actually eligible for and prepare for real interviews. Generic advice rarely connects their CV, a target role, today's vacancies and tomorrow's action. Njia brings these decisions into one browser journey.

## How it works

1. **Give context.** Choose a country and target role. Upload PDF/DOCX/TXT, paste experience, or try the labelled fictional sample, then consent to AI processing.
2. **Njia asks before it advises.** Groq reads the redacted CV and asks 3–5 quick follow-up questions: skills the CV doesn't clearly show (*Used it at work / in a project or course / still learning / not yet*) and one detail question about an outcome. Answering is optional; **Skip** always works.
3. **A brief shaped by your answers.** Strengths with exact CV quotes, three priorities, draft rewrites (which may use facts you supplied, labelled *Uses your answer — verify*), seven daily actions and interview guidance. Answers add or remove suggested skills.
4. **Live jobs you can apply for.** Remote postings from the [Himalayas](https://himalayas.app) jobs API whose location restrictions include your country (or are worldwide), plus local postings found by Groq's built-in web search and kept only when their link appears in the search tool's results. Each job shows eligibility, posting date, matched and missing skills and a skill-overlap %, and links to the source to apply.
5. **Real interview questions, then practise.** Groq web search finds questions candidates report being asked for the role, each with its source link. Practise an answer (separate consent) and get a 1–5 score, a STAR checklist, strengths, improvements and a stronger outline that must not add numbers or tools you didn't mention.
6. **Take it with you.** Review skills and recalculate historical market evidence, send the seven-day checklist to WhatsApp, copy it, or download an HTML brief. CV-evidence quotes and rewrite sections are excluded by default.

**Try it:** open the live app → choose the sample → consent → *Build my career brief* → answer the quick questions → explore priorities, live jobs and interview practice. If a provider is unavailable or its output fails validation, Njia returns a clearly labelled curated brief, curated questions or checklist feedback instead.

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
# Optional backup for questions, brief and feedback if Groq fails (free key from build.nvidia.com):
NVIDIA_API_KEY=your_server_side_nvapi_key
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

- **Consented CV text goes to Groq** (follow-up questions and the brief). If Groq fails and `NVIDIA_API_KEY` is configured, the same request goes once to the same open-weight model (`openai/gpt-oss-20b`) on the NVIDIA API Catalog, and the brief is labelled `nvidia`. Basic contact scrubbing is best effort, not anonymization; names, employers and other identifying details may remain. Remove sensitive details before consenting. Practice answers go to the AI provider only with their own consent checkbox.
- **Web searches never receive CV text.** Live-job and interview-question searches send only the role, country and top market skill names to Groq's built-in browser search (powered by Exa). Results are cached in server memory per role/country (Himalayas 1 h, web jobs 12 h, interview questions 24 h), because one browser search can use ~90K Groq tokens.
- **Live postings are third-party listings.** Njia shows only postings open to your country according to the listing, links to the source (Himalayas credited as required) and drops web results whose link can't be found in the search results. It does not verify employers, deadlines or eligibility beyond the listing. A found source proves the search returned that page, not that every word is quoted exactly. Confirm each posting on the source site before applying. Match % is skill overlap with the skills Njia can detect in the posting, not a hiring probability.
- Uploads are parsed on the hosting server. The app uses request/browser memory with **no application-level CV storage**, accounts, analytics or user database. This does not describe hosting/Groq retention or guarantee secure erasure. Downloads remain on the user’s device.
- **Review every generated claim.** Validation cannot eliminate hallucinations; an observed rewrite invented “real-time sales monitoring”, and an observed practice outline added an unstated purpose. Suggestions are drafts, with no factual, qualification or employment guarantee.
- Market figures come from **18,371 historical 2023 tech/data postings across ten African/MENA countries**, not live vacancies or a representative labour-market survey. Below 50 local role postings, Njia labels a broader ten-country sample. Coverage measures top-15 skill demand, not proficiency or hiring odds. Live jobs never change these historical figures.
- Prepared data documentation attributes the corpus to [lukebarousse/data_jobs](https://huggingface.co/datasets/lukebarousse/data_jobs) and identifies Apache-2.0; provenance/licensing were not independently verified.
- Browser uploads are capped at 4,000,000 bytes; the parser accepts 5 MiB. Scanned PDFs need external OCR or pasted text.

## Stack and documentation

Python/FastAPI, static HTML/CSS/JavaScript, Groq (`openai/gpt-oss-20b`, JSON mode and built-in `browser_search`), the NVIDIA API Catalog as an optional backup running the same `openai/gpt-oss-20b`, the Himalayas public jobs API, scikit-learn historical retrieval, unittest and Playwright; hosted on Vercel. OpenCode assisted coding, documentation and review. The eight-page deck was generated locally with python-pptx and Playwright. See the disclosure for actual AI use and boundaries.

- [Deployment](docs/DEPLOYMENT.md) · [AI and data disclosure](docs/AI_DISCLOSURE.md)
- [Submission answers](docs/SUBMISSION_DRAFT.md) · [Final checklist](docs/FINAL_CHECKLIST.md) · [Official requirements](docs/HACKATHON_REQUIREMENTS.md)
- [Ready voiceover script](docs/VOICEOVER.md) · [Release assets](https://github.com/Eeshan-Vaghjiani/njia/releases/tag/demo-v1)

**Submission status:** source, presentation and demo are published; the official form has **not been submitted**.
