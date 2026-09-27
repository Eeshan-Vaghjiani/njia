# Njia — final 20-field submission draft

**Dhruzzz · Kenya · ONLINE · 27 September 2026.** Copy-ready answers below; leader contact information is supplied privately in the official form. **The form has not been submitted.** Deadline: **27 September 2026, 19:30 EAT**.

[Official project form](https://docs.google.com/forms/d/e/1FAIpQLSebmyKeBPv2mrmy4T_wI2_z9SBjjSTZ-O-_ewiWs6PBEikRjw/viewform)

**Handoff:** source, eight-page presentation and exact-90.000-second captioned public-app demo are published. Evidence records **48 acceptance + 9 recording assertions = 57**, separately from **73 backend tests**, and real production **`openai/gpt-oss-20b`**. The live form retains 20 required questions and now includes four optional evidence fields; suggested answers follow field 19 below.

### 1. Country

Kenya

### 2. Hackerspace / ONLINE

ONLINE

### 3. Team name

Dhruzzz

### 4. Team leader full name

Eeshan Vaghjiani

### 5. Team leader email

Enter privately in the official form, matching Final Team Confirmation. No email address is published here.

### 6. Project title

Njia

### 7. Team members — full name of each member, one per line

```text
Eeshan Vaghjiani
Bhavin Mepani
Dhruvin Bhudia
```

### 8. Project summary — maximum 150 words

Njia helps Kenyan tech and data job seekers turn a CV into a practical next move from a mobile browser. With explicit consent, Groq's openai/gpt-oss-20b reads the basic-contact-redacted CV and first asks a few follow-up questions about skills the CV doesn't clearly show. The answers shape a personal brief: evidence-linked strengths, three priorities from 18,371 historical postings, fact-preserving CV rewrites, a seven-day plan and interview guidance. Njia then lists live jobs the user can apply for: remote postings open to their country, plus local postings found by web search and kept only when the link appears in the search results, each with matched and missing skills. It finds interview questions candidates report online, with sources, and gives AI feedback on practice answers. Web searches receive only role, country and skill names, never CV text. Every AI step has a labelled fallback; match percentages are skill overlap, not hiring odds.

### 9. Problem solved

A Kenyan job seeker may have useful experience but struggle to explain it in a CV, identify the most relevant evidence gap, find openings they are actually eligible for, or prepare for the questions interviewers really ask. Generic course lists and job boards leave the connection between past work, a target role, today's vacancies and tomorrow's action to the learner. Njia brings those decisions into one mobile-browser journey: it asks about what the CV doesn't show, compares the experience with visible historical role demand, matches it to live postings open to the user's country, and leaves them with a focused week of work, real interview questions and practice feedback. This is a prototype problem hypothesis; genuine user feedback and employment outcomes have not yet been established.

### 10. Solution and key features

- **Njia asks before it advises (new):** after consent, `/api/questions` sends basic-contact-scrubbed CV text to Groq, which asks 3–5 follow-up questions: skill questions with fixed server-set options (*used it at work / in a project or course / still learning it / not yet*) and a free-text question about a quoted CV item's outcome. Answers add or remove suggested skills in code and go into the brief; rewrites may use facts from free-text answers, labelled “Uses your answer — verify”. Skip always works; curated questions are used if AI fails.
- **CV to personal brief:** PDF/DOCX/TXT upload or pasted experience, optional preview/edit, explicit consent, then a personalised summary, evidence-linked strengths (exact CV quotes), three priorities with first steps, before/after draft rewrites, seven daily actions with deliverables and interview guidance.
- **Live jobs you can apply for (new):** `/api/jobs` queries the Himalayas public jobs API for remote postings whose location restrictions include the user's country or are worldwide (111 remote Data Analyst results were open to Kenya on 27 September), and Groq's built-in browser search for local postings (for example BrighterMonday, MyJobMag, Fuzu), keeping a web result only when its URL appears in the search tool's results. Cards show eligibility, posting date, matched and missing skills and a skill-overlap %, and link to the source to apply.
- **Real interview questions and practice (new):** `/api/interview/questions` uses Groq browser search to find questions candidates report for the role, each with a source link (unverifiable sources dropped; labelled curated bank as fallback), plus “use your evidence” hints computed in the browser from the user's strengths. `/api/interview/feedback` (separate consent) scores a typed practice answer 1–5 with a STAR checklist, strengths, improvements and a stronger outline that is rejected if it adds numbers or tools the user never mentioned; deterministic checklist fallback.
- **Visible market evidence:** deterministic counts and demand-weighted coverage from historical 2023 postings; sample sizes and broader regional fallback are labelled. These are not live vacancies or hiring odds, and live jobs never change them.
- **Human skill review:** edit suggested skills and recalculate market evidence and job matches. This does not regenerate the original AI brief; stale CV/target advice is labelled.
- **Portable follow-through:** copy the checklist, send it to WhatsApp, track progress for the session and download an HTML brief. CV-evidence and before/after sections are excluded by default, with explicit inclusion available.
- **Resilience:** every AI step has a labelled fallback (curated questions, curated brief, curated interview bank, checklist feedback). If Groq fails a question, brief or feedback call and a key is configured, one request goes to the same `openai/gpt-oss-20b` model on the NVIDIA API Catalog, labelled `nvidia`. Job sources fail independently; web searches are cached per role/country and run on a separate model so they cannot exhaust the brief model's daily token limit.
- **Honest limits:** basic redaction is not anonymization. Generated rewrites and outlines require review; observed responses invented “real-time sales monitoring” and added an unstated purpose to a practice outline. A found source proves the search returned that page, not that every word is quoted exactly. Validation does not guarantee factual accuracy.
- **Build and reuse:** the team's application work includes the coach UI (`static/coach.*`, `static/jobs.*`, `static/interview.*`), follow-up questions (`njia/questions.py`), advisor/validation (`njia/advisor.py`), live jobs (`njia/jobs.py`), interview research and feedback (`njia/interview.py`), the shared Groq client, market engine and checks. It uses existing open-source libraries, the attributed historical corpus and the Himalayas public API; the sample CV is labelled fictional. Physical-phone user research and employment-outcome validation are future work.

### 11. Technologies used

Python; FastAPI; Uvicorn; Pydantic; HTML/CSS/JavaScript; HTTPX; python-dotenv; python-multipart; pypdf; Python ZIP/XML parsing for DOCX; scikit-learn TF-IDF/cosine retrieval; unittest; Playwright/Chromium; Vercel hosting. Runtime AI uses Groq's chat-completions API: `openai/gpt-oss-20b` (JSON mode) for follow-up questions, the career brief and practice feedback, and `openai/gpt-oss-120b` with Groq's built-in `browser_search` tool (powered by Exa) for live local jobs and interview-question research. The NVIDIA API Catalog's `openai/gpt-oss-20b` endpoint is an optional backup for the JSON calls when Groq fails. Live remote jobs come from the Himalayas public jobs API (credited and linked as its terms require). The eight-page presentation was generated locally with python-pptx and Playwright. OpenCode assisted development. The bundled historical dataset is attributed to `lukebarousse/data_jobs`.

### 12. Source code URL

https://github.com/Eeshan-Vaghjiani/njia

### 13. Presentation URL

https://github.com/Eeshan-Vaghjiani/njia/blob/main/presentation/Njia-Dhruzzz.pdf

Use this viewable GitHub PDF link in the form. Editable companion: https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/Njia-Dhruzzz.pptx. The published presentation has eight pages and was generated locally with python-pptx + Playwright.

### 14. 90-second demo video URL

https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/njia-demo-90s.webm

Updated recording of the real public coach and actual Groq output, exactly **90.000 seconds**, captioned; no fabricated responses or synthetic voice. The release asset name is unchanged.

### 15. Project next step

Run consented usability sessions with Kenyan job seekers on physical phones: can they answer the follow-up questions, identify one useful next action, find a live posting they are genuinely eligible for, and practise an answer they can use? Use that feedback to improve mobile input, question wording and privacy copy, and evaluate rewrite and practice-outline faithfulness on a broader, reviewed CV set, including the observed unsupported “real-time sales monitoring” embellishment. Measure how often web-found postings and interview sources are relevant and still open, add Kenyan job boards with official feeds, and move to a paid inference tier with caching so learners don't hit free-tier rate limits. Then measure seven-day action completion and applications started before making claims about employment impact.

### 16. Partner awards — which prizes is your team applying for?

Select all four, including the primary award:

- **Click Mobile — Mobile-First Impact Award | Mobile-first solutions for Kenyan users, businesses or communities | Total KSh 50,000 cash prize; KENYA ONLY; allocation TBC**
- **Brightest GmbH — Skills & Employability Award (Brightest Award) | Job-relevant skills and qualifications | Fully paid Brightest vouchers + discounted Brightest voucher pricing, both for ONE WINNING TEAM ONLY; quantity, discount rate and redemption terms TBC**
- **Artefact — Data & AI Award | Data into actionable insights or useful AI solutions with measurable business or societal impact | Approx. US$1,040 gift voucher; one winning team; ALL PARTICIPATING COUNTRIES; redemption terms TBC**
- **Thunders — Engineering Excellence Award | Strong, reliable technical prototype | One Mac mini; one team**

Click Mobile is the team’s priority, aligned with its Kenyan mobile-first focus and cash-prize preference. KSh 50,000 is the published total contribution, with allocation unannounced; no award or payment is guaranteed. Country podium consideration is automatic for eligible entries; do not select the podium-only checkbox with partner awards.

### 17. Primary prize application — choose the award that best fits your project

**Click Mobile — Mobile-First Impact Award (Kenya only)**

### 18. Award application — explain your project’s fit and eligibility

**Click Mobile — Mobile-First Impact Award:** Njia turns a Kenyan job seeker's CV into follow-up questions, live jobs they can apply for, interview practice and a week of actions through a mobile-first browser interface, with a WhatsApp checklist share and no account or app install. See `static/coach.css`, `static/followup.css` and `static/jobs.css` for the responsive interface and the 90-second demo; the integrated flow was browser-checked at 360, 390 and 1280 px widths with no horizontal overflow or JavaScript errors, and physical-phone usability is the next validation step. Dhruzzz is a Kenya/ONLINE team, matching the published Kenya-only scope, which states no onsite-only restriction; organizer participation records determine final eligibility.

**Brightest GmbH — Skills & Employability Award:** Njia connects evidence in a CV to role-relevant priorities, live postings the learner can actually apply for (with matched and missing skills), real interview questions with sources and scored practice answers, making job-relevant skills easier to build and demonstrate. See `njia/jobs.py`, `njia/interview.py` and the published demo; neither AI advice nor practice scores certify competence or prove hiring outcomes. We are a Kenya/ONLINE team; the published award description states no Kenya exclusion, subject to confirmed participation.

**Artefact — Data & AI Award:** Njia turns data into actionable insight: 18,371 historical postings drive deterministic priorities, live Himalayas postings are filtered by stated eligibility and scored by skill overlap, and Groq web research is accepted only when its sources appear in the search tool's own results. See `njia/engine.py`, `njia/jobs.py` and `njia/interview.py`: statistics are computed by the application separately from model prose, and 126 backend tests plus the recorded public demo show prototype behaviour rather than measured societal outcomes. The award accepts all participating countries, including our Kenya/ONLINE team, subject to organizer confirmation.

**Thunders — Engineering Excellence Award:** Njia demonstrates engineering care through server-enforced consent, bounded document parsing, strict structured-output validation, URL grounding against tool evidence, per-source failure isolation, TTL caching with shared in-flight requests, a separate search model that protects the brief model's daily token limit, Groq-to-NVIDIA failover on the same open-weight model, and a labelled fallback at every AI step. See `njia/groq_client.py`, `njia/jobs.py`, `njia/advisor.py` and `tests/`: 126 backend tests pass (73 original plus 43 for the new features), with real production Groq output in the published demo. We are a Kenya/ONLINE team; no Kenya exclusion is stated in the published award description, with final eligibility determined by organizers.

### 19. AI/tool disclosure — list models, agents, datasets, APIs and generated assets used. Explain your chosen stack, access constraints, actual AI contribution and fallback. State honestly if no AI was used. Brev is optional; explain its use only if used. Do not include voucher codes, passwords or API keys.

Njia uses Python/FastAPI and static JavaScript for a lightweight mobile-browser experience, with deterministic historical-market calculations and local TF-IDF/cosine retrieval. **Runtime AI uses Groq in five places.** (1) **`/api/questions`** requires consent and sends basic-contact-scrubbed CV text, country/role and historical top skills to **`openai/gpt-oss-20b`**, which proposes 3–5 follow-up questions; skill-answer options are fixed by the server. (2) **`/api/advise`** requires consent and sends the scrubbed CV plus any answers to **`openai/gpt-oss-20b`**, which writes the summary, evidence strengths, gap explanations, draft rewrites, seven-day actions and interview guidance; skill answers are applied to suggested skills in code. (3) **`/api/jobs`** (web source) and (4) **`/api/interview/questions`** call **`openai/gpt-oss-120b`** with Groq's built-in **`browser_search`** tool (powered by Exa), sending only role, country and top market skill names — **never CV text**. Results are kept only when their URL appears in the tool's own search results, and are cached per role/country. (5) **`/api/interview/feedback`** sends a separately consented, scrubbed practice answer to **`openai/gpt-oss-20b`** for a score, STAR checklist and stronger outline. Remote live jobs come from the Himalayas public jobs API with no AI involved. **Backup provider:** if Groq fails call (1), (2) or (5) and `NVIDIA_API_KEY` is configured, the same request goes once to the same `openai/gpt-oss-20b` model on the NVIDIA API Catalog (a rate-limited trial service), with identical validation, and the result is labelled `nvidia`; the consent text names this backup. Web searches never use the backup. Access requires a server-held Groq key and network/provider availability; the free tier limits tokens per minute and per day, so searches use a separate model. Missing credentials, rate limits, provider failures or invalid output return labelled curated questions, a curated brief, a curated interview bank or checklist feedback.

**Product AI example:** labelled fictional sample CV + Kenya + Data Analyst → the AI asks about skills the CV doesn't show (e.g. Python, Tableau) and one outcome → the candidate answers truthfully (Python: still learning; one outcome detail) → consented Groq brief with evidence-linked strengths, draft rewrites (any that use the supplied outcome are labelled for verification) and a seven-day plan → live postings open to Kenya with matched/missing skills → source-linked interview questions → a practice answer scored with a STAR checklist. Market statistics and job-match percentages are computed by the application, not the model.

Basic redaction is not full anonymization: identifying details can remain. Uploads are parsed in hosting-server request memory, not on-device; application-level non-persistence is not a claim about provider retention. The HTML brief excludes CV-evidence quotes and before/after sections by default, with optional inclusion, but other personalised prose can still reveal experience details. Validation checks structure, quotations, source URLs against tool evidence and some unsupported numbers/tools, **not all factual accuracy**: an observed rewrite invented **“real-time sales monitoring,”** and an observed practice outline added an unstated purpose, so human review is required. A source link proves the search returned that page, not that the question is quoted exactly. Live postings are third-party listings; eligibility comes from each listing's stated location restrictions. Coverage and match % are not hiring probability.

The **older `/classic` only** offers manual skills, deterministic four-week plans and fixed quizzes; its optional `/api/plan` sends structured curriculum without CV text. The old no-CV-to-model boundary does not apply to the new advisor. Classic `NJIA_AI_PROVIDER=offline` does not disable the new advisor’s independent Groq path. Classic Ollama `qwen2.5:3b` was mock-tested only, not live-used; NVIDIA Brev was not used.

The dataset is attributed to `lukebarousse/data_jobs`: 18,371 historical 2023 postings across ten African/MENA countries. Prepared documentation identifies Apache-2.0, without independent provenance/licence verification. Live remote postings come from the Himalayas public jobs API, credited with links back to each Himalayas job page as its terms require; web-found postings and interview sources are third-party pages linked for the user to check. Synthetic inputs were used for validation. **126 backend tests** pass; these are not an independent factuality, fairness or user-outcome evaluation.

**Build assistance:** earlier development used **OpenCode**, main agent label **`github-copilot/gpt-6-astra`**, plus coding/review agents whose underlying model identities were not independently established. Today's features (follow-up questions, live jobs, interview research and feedback, WhatsApp share, updated recorder and deck builder) were built with **OpenCode** at the team's direction, using main agent model **`github-copilot/claude-opus-5.5`**, which coordinated parallel coding subagents in the same harness whose underlying model identities were not independently established. Assistance covered code, tests, documentation and review; factual faithfulness remains a known limit. UI visuals are code-native HTML/CSS. The **eight-page presentation was generated locally with python-pptx and Playwright**; Gemini was not used for inference. The captioned Playwright demo records the real public coach and real Groq output, with no fabricated responses or synthetic voice. No credentials are included in public materials.

## Optional evidence fields

These appear before final confirmation in the current form and do not change the 20 required questions.

**Project cover / screenshot / logo URL — optional**

https://raw.githubusercontent.com/Eeshan-Vaghjiani/njia/main/docs/images/coach-desktop.png

**Live demo URL — optional**

https://gomycode-2026.vercel.app

**Testing, results and known limitations — optional**

- Backend suite: **126 tests passed** (73 original + 53 for follow-up questions, live jobs, interview research/feedback, the shared Groq client and the NVIDIA backup; `tests/`, run instructions in `README.md`), counted separately from browser checks.
- Live checks on 27 September: Himalayas returned **111 remote Data Analyst results open to Kenya**; Groq web search returned source-verified BrighterMonday, MyJobMag and Fuzu postings, and 7/7 source-verified interview questions from three sites; follow-up questions took 1.3–1.8 s and practice feedback 1.2 s. Evidence: `scripts/record_coach_demo.py`, the published 90-second demo and `docs/AI_DISCLOSURE.md`.
- Limits: web searches take about 20–40 s and can hit Groq free-tier rate limits (labelled fallback, cached results, retry button); a source link proves the search returned that page, not exact quotation; an observed rewrite invented “real-time sales monitoring” and an observed practice outline added an unstated purpose. Physical-phone usability and employment outcomes have not been established.

**Responsible AI and data — optional**

Njia uses historical 2023 postings attributed to `lukebarousse/data_jobs` (Apache-2.0 per prepared documentation, not independently verified), live postings from the Himalayas public API with the required attribution, and labelled synthetic demonstration CVs. Explicit consent is required before basic-contact-scrubbed CV text is sent to Groq, practice answers need their own consent, and web searches receive only role, country and skill names — never CV text — with results kept only when their links appear in the search tool's results. Basic redaction is not anonymization, generated claims require human review, and match % and coverage are not hiring probability; employment outcomes have not been established.

### 20. Final confirmation

Exact required checkbox statement:

> I confirm that our functional prototype, source code, presentation, 90-second demo video, project card details and AI/tool disclosure are complete, accessible and final.

**Pending human review and submission.** Open the published source, presentation and video signed out and review the answers before confirming. Enter the leader contact information privately, submit once before **19:30 EAT**, and save the confirmation receipt. **The form has not been submitted.**
