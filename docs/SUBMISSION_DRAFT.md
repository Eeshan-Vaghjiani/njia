# Njia — final 20-field submission draft

**Dhruzzz · Kenya · ONLINE · 27 September 2026.** Copy-ready answers; leader contact information is supplied privately. **The form has not been submitted.** Deadline: **27 September 2026, 19:30 EAT**.

[Official project form](https://docs.google.com/forms/d/e/1FAIpQLSebmyKeBPv2mrmy4T_wI2_z9SBjjSTZ-O-_ewiWs6PBEikRjw/viewform)

**Handoff:** latest features are live at the same URL with NVIDIA configured. The regenerated eight-page PDF/PPTX, corrected exact-90.000-second video, recording JSON, NVIDIA JSON and voiceover are **published at the same URLs**. Latest evidence: **126 backend tests passed offline** (main-workflow report), **19 successful public-recording checks**, and a **separate actual local NVIDIA fallback test**. The older **57 public assertions (48 + 9)** are historical, not the current recording count. Four optional evidence answers follow field 19.

### 1. Country

Kenya

### 2. Hackerspace / ONLINE

ONLINE

### 3. Team name

Dhruzzz

### 4. Team leader full name

Eeshan Vaghjiani

### 5. Team leader email

Enter privately in the official form, matching Final Team Confirmation.

### 6. Project title

Njia

### 7. Team members — full name of each member, one per line

```text
Eeshan Vaghjiani
Bhavin Mepani
Dhruvin Bhudia
```

### 8. Project summary — maximum 150 words

Njia helps Kenyan tech and data job seekers turn a CV into a practical next move from a mobile browser. With consent, AI reads basic-contact-redacted CV text and asks follow-up questions. Answers shape evidence-linked strengths, priorities informed by 18,371 historical postings, draft rewrites requiring human review, and a seven-day plan. Njia shows remote jobs open to the selected country and local jobs found through web search, with source links and matched or missing skills. It finds source-linked interview questions and gives separately consented practice feedback. Groq powers coaching and web research; NVIDIA provides a configured coaching backup. Web searches receive role, country and skill names, never CV text. Unavailable AI has labelled fallbacks. Basic redaction is not anonymization; generated claims need checking, and skill overlap is not hiring probability.

### 9. Problem solved

A Kenyan job seeker may have useful experience but struggle to explain it in a CV, identify relevant evidence gaps, find openings they are eligible for, or prepare for interviews. Generic course lists and job boards leave the connection between past work, a target role, today's vacancies and tomorrow's action to the learner. Njia brings those decisions into one mobile-browser journey: it asks what the CV does not show, compares experience with visible historical role demand, matches it to live postings by stated eligibility, and offers a focused week of work, source-linked interview questions and practice feedback. This is a prototype problem hypothesis; genuine user feedback and employment outcomes remain unestablished.

### 10. Solution and key features

- **Ask before advising:** consented CV upload (PDF/DOCX/TXT) or pasted experience leads to 3–5 follow-up questions. Skill options are server-fixed; a detail question quotes the CV. Answers are optional, self-reported and used in the brief; Skip remains available.
- **Personal brief:** summary, strengths with exact CV quotes, three priorities, draft rewrites, seven daily actions with deliverables and interview guidance. Skill answers add/remove suggested skills in code. Rewrites using detail answers are labelled “Uses your answer — verify”; all generated claims require human review.
- **Live jobs:** Himalayas remote postings filtered by country/worldwide eligibility, plus local Groq web-search results whose URLs appear in tool evidence. Cards show posting date, eligibility and matched/missing skills. The latest recording rendered eight remote and three local cards; the source headline separately reported 111 remote matches. Verify listings before applying; skill overlap is not hiring probability.
- **Interview research and practice:** source-linked web questions, browser-computed CV-evidence hints, and separately consented practice feedback with a 1–5 score, STAR checklist and draft outline. Partial number/tool checks do not guarantee factual faithfulness.
- **Visible market evidence:** deterministic counts and demand-weighted coverage from 18,371 historical 2023 postings. Below 50 local role postings, a broader ten-country sample is labelled. These figures are separate from live vacancies and AI-authored prose.
- **Review and follow-through:** edit skills to recalculate evidence and job matches, track session progress, copy or send the checklist to WhatsApp, and download HTML. CV quotes and rewrite sections are excluded by default. Skill review does not regenerate the brief; edited CV/target inputs mark it stale.
- **Bounded fallback:** configured NVIDIA can serve JSON coaching if Groq credentials are absent or supported provider errors occur. Brief failover also covers invalid assessments; questions/feedback feature-validation failures go directly to curated/checklist output. Web research has no NVIDIA fallback. Labelled curated outputs and independent job-source failures preserve partial use.
- **Known factual limit:** the latest successful recording's rewrite added unsupported **“support inventory decisions”**, despite an explicit personal synthetic-data dashboard answer. Earlier output invented “real-time sales monitoring” and an unstated practice-outline purpose. Passing checks do not establish factual accuracy.
- **Build and reuse:** team application work includes `static/coach.*`, follow-up UI, jobs/interview UI, `njia/questions.py`, `njia/advisor.py`, `njia/jobs.py`, `njia/interview.py`, the shared client, market engine and checks. Existing libraries, attributed historical data and Himalayas are reused; demonstration CVs are labelled fictional.

### 11. Technologies used

Python; FastAPI; Uvicorn; Pydantic; HTML/CSS/JavaScript; HTTPX; python-dotenv; python-multipart; pypdf; Python ZIP/XML DOCX parsing; scikit-learn TF-IDF/cosine retrieval; unittest; Playwright/Chromium; Vercel. Groq **`openai/gpt-oss-20b`** in JSON mode powers questions, briefs and practice feedback; **`openai/gpt-oss-120b` with `browser_search` (Exa)** powers local-job and interview research. NVIDIA API Catalog **`openai/gpt-oss-20b`** is the configured JSON coaching backup. Remote jobs use Himalayas. The eight-page deck was regenerated locally with python-pptx and Playwright. OpenCode assisted development. Historical data is attributed to `lukebarousse/data_jobs`.

### 12. Source code URL

https://github.com/Eeshan-Vaghjiani/njia

### 13. Presentation URL

https://github.com/Eeshan-Vaghjiani/njia/blob/main/presentation/Njia-Dhruzzz.pdf

Viewable PDF for the form; regenerated eight-page deck published at the same URL. Editable companion: https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/Njia-Dhruzzz.pptx

### 14. 90-second demo video URL

https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/njia-demo-90s.mp4

Final delivery: **MP4, H.264, 1280×720, 25 fps, faststart, approximately 4.2 MB**, converted from the latest corrected real public-app recording: **90.000 seconds**, silent captions, 1×, **19 checks passed**, zero late cues, JavaScript errors or mocked responses. Two narration captions were corrected in postproduction to require factual review; no app/model output content was edited. Real Groq output; NVIDIA fallback was tested separately locally, not shown in the video. WebM is retained only as an optional source.

### 15. Project next step

Run consented usability sessions with Kenyan job seekers on physical phones: can they answer follow-ups, identify a useful next action, find a posting they are genuinely eligible for, and practise an answer? Improve input, wording and privacy copy from feedback. Evaluate rewrite and practice-outline faithfulness on a broader human-reviewed CV set, including the latest unsupported “support inventory decisions” claim. Measure source relevance/freshness, add Kenyan boards with official feeds, and evaluate paid inference and caching to reduce observed quota and search-latency failures. Measure seven-day action completion and applications started before claiming employment impact.

### 16. Partner awards — which prizes is your team applying for?

Select all four:

- **Click Mobile — Mobile-First Impact Award:** Kenya only; **KSh 50,000 total cash contribution**, allocation TBC.
- **Brightest GmbH — Skills & Employability Award:** fully paid Brightest vouchers plus discounted voucher pricing for one winning team; quantity, discount and redemption terms TBC.
- **Artefact — Data & AI Award:** approximately US$1,040 gift voucher; one winning team; all participating countries; redemption terms TBC.
- **Thunders — Engineering Excellence Award:** one Mac mini for one team.

Click Mobile is the team's priority. Country podium consideration is automatic for eligible entries; do not select “Country podium only” alongside partner awards. No award/payment is guaranteed.

### 17. Primary prize application — choose the award that best fits your project

**Click Mobile — Mobile-First Impact Award (Kenya only)**

### 18. Award application — explain your project’s fit and eligibility

**Click Mobile:** Njia connects CV context, live listings, interview practice and weekly actions through a mobile-first browser interface, with WhatsApp sharing and no account or app installation. See `static/coach.css`, `static/followup.css`, `static/jobs.css` and the demo: the latest recording ran at 1280×720 with no JavaScript errors; earlier mobile-browser evidence is separate, with no new mobile acceptance run or physical-phone study claimed. Dhruzzz is Kenya/ONLINE, matching the published Kenya-only scope with no stated onsite restriction; organizer records determine eligibility.

**Brightest GmbH:** Njia links CV evidence to role-relevant priorities, matched/missing job skills and sourced interview practice, helping learners build and demonstrate job-relevant skills. See `njia/jobs.py`, `njia/interview.py` and the demo; neither advice nor practice scores certify competence or prove employment outcomes. The published scope states no Kenya exclusion, subject to confirmed participation.

**Artefact:** Njia turns historical postings and live-source data into actionable priorities, with statistics computed separately from model prose and source URLs checked against search-tool evidence. See `njia/engine.py`, `njia/jobs.py` and `njia/interview.py`; **126 offline backend tests and 19 latest recording checks** demonstrate prototype behaviour, not measured societal outcomes. The award accepts all participating countries, including Kenya, subject to organizer confirmation.

**Thunders:** Njia demonstrates server-enforced consent, bounded parsing, structured-output validation, URL grounding, independent job-source failure handling, process caching, separate search-model quotas and bounded Groq-to-NVIDIA failover. See `njia/groq_client.py`, `njia/advisor.py` and `tests/`: **126 backend tests passed offline**, **19 public-recording checks passed**, and a separate local forced-fallback test returned validated NVIDIA questions and a seven-day brief; recording-session search/timing failures are also disclosed. The published award description states no Kenya exclusion, with final eligibility determined by organizers.

### 19. AI/tool disclosure — models, agents, datasets, APIs, assets, access and fallback

Njia uses Python/FastAPI and static JavaScript for a lightweight mobile browser, deterministic historical-market calculations and local TF-IDF/cosine retrieval. **Groq `openai/gpt-oss-20b`** generates consented CV follow-ups (`/api/questions`), a brief from scrubbed CV text and optional answers (`/api/advise`), and separately consented practice feedback (`/api/interview/feedback`). The model writes draft advice, not market statistics; skill-answer options and skill-list adjustments are handled in code. **Groq `openai/gpt-oss-120b` with `browser_search` (Exa)** researches local jobs and interview questions, receiving role, country and top market skill names, **never CV text**. Source URLs must appear in tool evidence. Himalayas supplies remote jobs without AI.

**NVIDIA backup is configured in production.** Missing Groq credentials or supported provider errors can trigger one NVIDIA API Catalog request using default `openai/gpt-oss-20b`, labelled `nvidia`, under the same consent and feature validation. The brief also fails over on invalid assessments; questions/feedback feature-validation failures instead return curated questions/checklist feedback directly. Web research has no NVIDIA fallback. A separate actual local test forced Groq unavailable: **five validated questions in 11.564 s** and a **validated seven-day brief in 16.637 s**, one NVIDIA request each. The video uses Groq, not NVIDIA; the local test did not exercise feedback or establish production failover. **NVIDIA Brev was not used.**

Hosted inference requires network access and server-held credentials. Configured NVIDIA can serve JSON coaching without a Groq key; Groq is required for web research. Groq free-tier token limits and NVIDIA trial rate limits constrain access. Process caches and separate search-model quotas reduce repeated work without guaranteeing availability; labelled curated/checklist outputs and independent job sources preserve partial use.

**Actual session:** initial cache warming returned local jobs but curated interview fallback and stopped before recording/coaching. Three recording attempts then failed on interview timing or local-card availability. The final successful take had no failed checks, late cues or JavaScript errors; fallback allowance was enabled but unused. The session's **27 application POSTs** include warm-up and cache hits, not 27 upstream inference calls. One separately observed browser search consumed **93,301 tokens**; exact full-session tokens and monetary cost were unavailable. The final interview response took **0.390 s from cache**, not a fresh-search benchmark. See `artifacts/recording-handoff.md` and `docs/AI_DISCLOSURE.md`.

**Product example:** fictional CV + Kenya + Data Analyst → four follow-ups → truthful answers (Python still learning; dashboard a personal synthetic-data project) → Groq brief and seven-day plan → eight remote and three local job cards → eight interview questions from three source URLs → separately consented practice feedback scored 4/5. Statistics and match percentages are application-calculated.

**Human review:** basic redaction is not anonymization. Parsing is in hosting-server memory, not on-device; no application-level CV persistence does not establish provider retention. HTML exports exclude quote/rewrite sections by default, but other prose may reveal CV details. Validation checks structure, quotes, source URLs and some numbers/tools, **not all factual accuracy**. The latest rewrite added **“support inventory decisions”** despite the explicit personal-project answer. Earlier output invented “real-time sales monitoring” and an unstated practice-outline purpose. Every draft, including “Uses your answer — verify,” needs human factual review. Source links establish search provenance, not exact quotation; listing eligibility is third-party information, and coverage/match percentages are not hiring probability.

**Classic only:** `/classic` offers manual skills, curated four-week plans and fixed quizzes; optional `/api/plan` sends structured curriculum without CV text. That old boundary does not apply to the coach. `NJIA_AI_PROVIDER=offline` does not disable independent Groq/NVIDIA coaching. Classic Ollama `qwen2.5:3b` was mock-tested only, not live-used.

**Data and evaluation:** 18,371 historical 2023 postings across ten African/MENA countries, attributed to `lukebarousse/data_jobs`; prepared documentation identifies Apache-2.0 without independent provenance/licence verification. Himalayas is credited with job-page links; other source pages are linked for users to check. Synthetic inputs were used. **126 backend tests passed offline**, separately from **19 latest recording checks**, the local NVIDIA test and **older 57 public assertions (48 + 9)**. These are not independent factuality, fairness or user-outcome studies.

**Build assistance and assets:** OpenCode assisted code, tests, docs, review, recorder and deck tooling. Earlier development and this documentation update used main agent label **`github-copilot/gpt-6-astra`**. The feature-build workflow reports **`github-copilot/claude-opus-5.5`** coordinating parallel coding/review subagents whose underlying identities were not independently established. UI visuals are code-native. The **eight-page deck** was regenerated locally with **python-pptx and Playwright**; Gemini was not used for inference. The captioned Playwright video records the real public coach and Groq responses, with zero mocked responses, no synthetic voice and no audio stream. Credential values are excluded from public materials.

**Caption-only postproduction:** PNG overlays with a lossless VP9 re-encode corrected the narration rectangle at **53.240–57.280 s** and **76.360–83.440 s** (ends exclusive), replacing overclaims with explicit factual-review instructions. The old captions are absent from the final video. The [recording JSON](https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/njia-coach-demo-results.json) discloses `caption_corrections`, including identical decoded pixels outside the caption rectangle in every frame and identical frame hashes outside the correction windows; these checks apply to the corrected WebM source before H.264 MP4 conversion. No app/model output content was edited or fabricated, no new API calls or recording run occurred, and final MP4 delivery remains **90.000 s, 1×, no audio**. Exact corrected wording is in `docs/AI_DISCLOSURE.md` and `docs/VOICEOVER.md`.

## Optional evidence fields

**Project cover / screenshot / logo URL**

https://raw.githubusercontent.com/Eeshan-Vaghjiani/njia/main/docs/images/coach-desktop.png

**Live demo URL**

https://gomycode-2026.vercel.app

**Testing, results and known limitations**

- **126 backend tests passed offline**, reported by main; run instructions in `README.md`.
- **19 latest public-recording checks passed**, no failed checks, late cues, JavaScript errors or mocked responses; exact 90.000 s, 1×. Groq 20b: four questions **1.271 s including upload**, brief **1.450 s**, feedback **0.844 s**, score **4/5**. **8 remote + 3 local cards; 8 web interview questions / 3 source URLs** on Groq 120b. Evidence: [published recording JSON](https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/njia-coach-demo-results.json) and the video URL above; JSON also discloses the two caption-only corrections.
- **Local NVIDIA proof:** forced Groq unavailability; five validated questions **11.564 s**, seven-day validated brief **16.637 s**, one request each, `openai/gpt-oss-20b`; [published NVIDIA JSON](https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/nvidia-fallback-results.json). Not in the video; not production-failover proof. No Brev.
- Older **57 public assertions (48 + 9)** are separate historical evidence; no new mobile acceptance run.
- Initial cache warm-up and three recording attempts failed before the final success. **27 session application POSTs** include warming/cache hits; final interview response **0.390 s was cached**. One separate search used **93,301 tokens**; full-session cost is unavailable. Latest rewrite's unsupported **“support inventory decisions”** requires human correction. Physical-phone usability and employment outcomes remain unestablished.

**Responsible AI and data**

Historical 2023 data is attributed to `lukebarousse/data_jobs` (Apache-2.0 per prepared documentation, not independently verified); live Himalayas postings are attributed, and demonstration CVs are synthetic. Explicit consent precedes sending scrubbed CV text to Groq or NVIDIA; practice answers need separate consent. Web research receives only role, country and skill names, never CV text; source URLs must appear in tool evidence. Basic redaction is not anonymization. The latest unsupported “support inventory decisions” rewrite illustrates why generated claims require human review. Coverage and match % are not hiring probability; employment outcomes are unestablished.

### 20. Final confirmation

Exact required checkbox statement:

> I confirm that our functional prototype, source code, presentation, 90-second demo video, project card details and AI/tool disclosure are complete, accessible and final.

**Pending human review and submission.** Open the published deck/video at the same URLs signed out, review all answers, enter leader contact information privately, submit once before **19:30 EAT**, and save the receipt. **The form has not been submitted.**
