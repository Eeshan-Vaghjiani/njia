# Njia: 90-second demo

**2026-09-27 checkpoint:** demo recording and fresh post-upload browser checks are in progress. Main workflow reports 57 unittest methods passing and a live Groq four-week plan from `openai/gpt-oss-20b` in 2.27 seconds. Final recording, links and test results will be added later. Planned repository: https://github.com/Eeshan-Vaghjiani/njia; publication/access pending. Public deployment awaits Vercel authentication. The presentation outline is ready; Felo export is blocked by a missing key, and older decks do not represent current capabilities.

## Before the timer

1. Follow the [README setup](../README.md#run-locally), then run `start.ps1` from the project root. Open **http://127.0.0.1:8000**.
2. Check the configured provider and actual returned plan mode. The default is `NJIA_AI_PROVIDER=offline` unless configured. For hosted coaching, main workflow configures Groq with a server-held key and `openai/gpt-oss-20b`; explicitly opt in before generation. Curated plans are available without AI consent. Ollama remains mock-tested only.
3. Use **Reset this session** for a clean start. Keep the browser's download location accessible for the Markdown report. Use a synthetic PDF/DOCX/TXT or the built-in synthetic profile, not a real CV. The backend accepts up to 5 MiB; the frontend caps files at 4,000,000 bytes to leave room under Vercel's request limit.
4. Rehearse the clicks below. Earlier pre-upload Chromium desktop/mobile checks passed; new browser checks are ongoing and must not be described as complete.

This script supports the required 90-second recording; it is not itself the video deliverable. A local walkthrough is possible while public deployment remains pending.

## Timed walkthrough

| Time | Action | Suggested narration |
| --- | --- | --- |
| 0–10 s | Show the landing page and the 2023 dataset strip. | “Njia turns your existing skills into a next learning step using 18,371 historical tech/data postings across ten African and MENA countries.” |
| 10–25 s | With processing consent, upload a synthetic PDF/DOCX/TXT, review/edit its preview, then find and confirm skills. The built-in example is an alternative. | “Documents are processed in app-server memory. I review the preview and every suggested skill, or enter skills manually without submitting a CV.” |
| 25–42 s | Click **Find my path**. Show coverage, demand bars, and sample size; briefly scroll to the historical job examples. | “Coverage measures mentions of my confirmed skills among the top fifteen skills. It is not hiring odds. These related examples use TF-IDF skill similarity, and they are historical postings—not live vacancies.” |
| 42–60 s | Build a four-week plan at **3 hours / week**. If Groq is configured, explicitly opt in and show the actual returned mode/model; otherwise show curated mode. | “The plan turns missing skills into weekly exercises and evidence. Optional Groq coaching receives only structured curriculum, not my CV or demand statistics. Curated planning works without AI consent.” |
| 60–79 s | Click **Try a practice check**. Choose **SQL**, then **Start a practice check**. Select the rehearsed answers below and click **Check my answers**. | “Three fixed questions give immediate answer-key feedback. This is a fundamentals practice check, not a certification or verified proficiency assessment.” |
| 79–90 s | Click **Download my evidence report**. Point to the downloaded `njia-skill-evidence.md` file. | “I can keep the analysis, plan, and practice result as a local Markdown report. The raw CV is excluded. Njia offers a useful next step while showing the data's age and the limits of its scores.” |

### Rehearsal details

- **Try an example** sets Kenya / Data Analyst and checks processing consent for the synthetic text. For manually pasted text or upload, explicitly check consent. Uploaded preview text may contain personal information; parsing is not anonymization. Scanned PDFs need external OCR.
- The sample's expected confirmed skills are **SQL, Excel, Power BI**. The lexicon has limitations; do not generalize this one example into reliable semantic CV understanding.
- To keep the SQL segment within time, the answer-key choices are **LEFT JOIN**, **HAVING**, and **COUNT(DISTINCT customer_id)**. A rehearsed 3/3 demonstrates grading, not the presenter's competence.
- Skip the optional reflection during the timed walkthrough. If used, it stays in browser memory, is not graded or sent to the server, and is included in the downloaded report after the practice check is submitted.
- Read the displayed coverage and sample size rather than relying on numbers from older slides. Canonicalization affects the calculations.
- `/api/plan` enforces `use_ai`/`ai_consent` server-side for remote opt-in. Do not describe a configured provider as a successful model response; show the actual returned mode. If the provider fails, narrate the curated fallback accurately.

## Optional follow-up, outside the 90 seconds

- **Small-sample handling:** choose **Côte d'Ivoire**, keep **Data Analyst**, and click **Find my path** again. Show the explicit below-50-postings notice and combined 10-country scope. Changing the market clears the previous analysis, plan, and practice result.
- **Manual entry:** reset the session, select a skill under **Review your skills**, and click **+**. Text extraction and its consent checkbox are unnecessary for this route. An empty profile can also produce a starting plan.
- **Transparency:** open **How it works** to show the extraction, demand, retrieval, practice, and privacy descriptions.
- **AI choice and recovery:** demonstrate a curated plan without AI consent. If demonstrating provider unavailability, record an actual fallback result and label it separately from the successful live Groq result.
- **Clearing:** **Clear text** removes the pasted text but retains confirmed skills; **Reset this session** clears skills and results. Neither deletes reports already downloaded to disk.

## Evidence and presenter boundaries

- **Unit/API checks:** main workflow reports **57 unittest methods passing** at the 2026-09-27 checkpoint; not rerun for this documentation-only update.
- **First-stage extraction artifact:** 20 synthetic CV examples; precision **0.9535**, recall **0.9762**, exact matches **17/20**, warm median **0.97 ms**. Timing excludes document parsing, HTTP/browser work, retrieval and generation; zero inference calls/cost is only for that extraction run. This is not an upload or hosted-model benchmark, and the examples are developer-authored, not independent validation.
- **Browser checks:** earlier pre-upload `scripts/browser_test.py` passed the core desktop/mobile walkthrough with zero JavaScript errors and zero external page requests in that run. Five earlier asynchronous checks passed in `scripts/race_test.py`. New integrated browser verification and recording are ongoing.
- **AI:** default lexicon/curated mode uses no generative model. Main workflow live-tested Groq **`openai/gpt-oss-20b` on 2026-09-27**, returning four weeks in **2.27 seconds** in one observed run, not a benchmark. The original `llama-3.3-70b-versatile` was unavailable in the account model list; the default changed accordingly. Optional local Ollama `qwen2.5:3b` remains mock-tested only. No NVIDIA Brev is used.
- **Data:** 2023 tech/data postings are not current or representative of all employment. The prepared documentation attributes the source to `lukebarousse/data_jobs` and identifies Apache-2.0; provenance and licensing have not been independently verified.
- **Privacy:** no application-level raw CV persistence; basic redaction is not comprehensive anonymization. On a public app, document/text processing takes place on the hosting server, not the user's laptop. Groq receives only allowlisted structured curriculum, not CV text, identities, country/role or demand statistics. Exported reports contain self-reported skills and any submitted reflection.
- **Earlier materials:** `GAME_PLAN.md`, `STRATEGY.md`, and existing decks are not current capability evidence. Use this script and the updated presentation outline.

If the local engine does not load, check the server terminal and refresh. If extraction is unsuitable, choose skills manually. Curated planning provides a complete path without model availability or AI consent.
