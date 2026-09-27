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

Njia helps Kenyan tech and data job seekers turn a CV into a practical next move from a mobile browser. With explicit consent, it sends basic-contact-redacted CV text to Groq’s openai/gpt-oss-20b and builds a personal brief: evidence-linked strengths, three priorities, draft CV rewrites, seven days of concrete actions and an interview question. Historical evidence from 18,371 postings is calculated separately from AI prose, with visible sample sizes and editable skill suggestions. Users can keep a downloadable HTML brief; CV excerpts and rewrite sections are excluded by default. The live public coach passed 48 acceptance assertions plus nine recording assertions, separately from 73 backend tests. Njia makes career advice actionable without presenting coverage as hiring odds: redaction is partial, generated claims require review, and provider failures return a labelled curated brief.

### 9. Problem solved

A Kenyan job seeker may have useful experience but struggle to explain it in a CV, identify the most relevant evidence gap, or decide what to practise next. Generic course lists leave the connection between past work, a target role and tomorrow’s action to the learner. Njia brings those decisions into one mobile-browser journey: inspect the experience already present, compare it with visible historical role demand, and leave with a focused week of work and interview preparation. This is a prototype problem hypothesis; genuine user feedback and employment outcomes have not yet been established.

### 10. Solution and key features

- **CV to personal brief:** PDF/DOCX/TXT upload or pasted experience, optional preview/edit, and explicit consent before `/api/advise` sends basic-contact-scrubbed CV text to Groq.
- **Useful coaching:** personalised summary, evidence-linked strengths, three priorities with first steps, before/after CV draft rewrites, seven daily actions with deliverables, and interview question/answer guidance.
- **Visible market evidence:** deterministic counts and demand-weighted coverage from historical 2023 postings; sample sizes and broader regional fallback are labelled. These are not live vacancies or hiring odds.
- **Human skill review:** edit suggested skills and recalculate market evidence. This does not regenerate the original AI brief; stale CV/target advice is labelled.
- **Portable follow-through:** copy the checklist, track progress for the session and download an HTML brief. CV-evidence and before/after sections are excluded by default, with explicit inclusion available; other advice may still reveal experience details.
- **Resilience:** labelled curated advisor fallback if Groq is unavailable or output is invalid. The older `/classic` offers manual skills, four-week curated learning, fixed practice checks and Markdown export.
- **Honest limits:** basic redaction is not anonymization. Generated rewrites require review; an observed response invented “real-time sales monitoring.” Validation does not guarantee factual accuracy.
- **Build and reuse:** the team’s application work includes the coach UI (`static/coach.*`), advisor/validation (`njia/advisor.py`), market engine and checks. It uses existing open-source libraries and the attributed historical corpus; the sample CV is labelled fictional. The published demo uses real provider output. Physical-phone user research, refreshed vacancy data and employment-outcome validation are future work.

### 11. Technologies used

Python; FastAPI; Uvicorn; Pydantic; HTML/CSS/JavaScript; HTTPX; python-dotenv; python-multipart; pypdf; Python ZIP/XML parsing for DOCX; scikit-learn TF-IDF/cosine retrieval; unittest; Playwright/Chromium; Vercel hosting. New runtime coaching uses Groq’s chat-completions API with actual production model `openai/gpt-oss-20b`. The final eight-page presentation was generated locally with python-pptx and Playwright. OpenCode assisted development. The bundled historical dataset is attributed to `lukebarousse/data_jobs`.

### 12. Source code URL

https://github.com/Eeshan-Vaghjiani/njia

### 13. Presentation URL

https://github.com/Eeshan-Vaghjiani/njia/blob/main/presentation/Njia-Dhruzzz.pdf

Use this viewable GitHub PDF link in the form. Editable companion: https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/Njia-Dhruzzz.pptx. The published presentation has eight pages and was generated locally with python-pptx + Playwright.

### 14. 90-second demo video URL

https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/njia-demo-90s.webm

Updated recording of the real public coach and actual Groq output, exactly **90.000 seconds**, captioned; no fabricated responses or synthetic voice. The release asset name is unchanged.

### 15. Project next step

Run consented usability sessions with Kenyan job seekers on physical phones: can they identify one useful next action, correct a skill suggestion and take away a brief they understand? Use that feedback to improve mobile input and privacy wording, and evaluate rewrite faithfulness on a broader, reviewed CV set, including the observed unsupported “real-time sales monitoring” embellishment. Refresh historical demand data with documented provenance and measure completion of the seven-day actions before making claims about employment impact.

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

**Click Mobile — Mobile-First Impact Award:** Njia turns a Kenyan job seeker’s CV into a focused week of career actions through a mobile-first browser interface, including a take-away brief without requiring an account. See `static/coach.css` for the responsive interface and `scripts/coach_acceptance.py` for browser acceptance checks; physical-phone usability and adoption are the next validation step. Dhruzzz is a Kenya/ONLINE team, matching the published Kenya-only scope, which states no onsite-only restriction; organizer participation records determine final eligibility.

**Brightest GmbH — Skills & Employability Award:** Njia connects evidence in a CV to role-relevant priorities, seven days of practical deliverables and an interview question, making learning progress easier to demonstrate. The published demo and `njia/advisor.py` show this workflow, while neither AI advice nor classic practice checks certify competence or prove hiring outcomes. We are a Kenya/ONLINE team; the published award description states no Kenya exclusion, subject to confirmed participation.

**Artefact — Data & AI Award:** Njia combines 18,371 historical postings with consented CV-to-Groq coaching to turn market data and personal experience into actionable priorities. See `njia/engine.py`, `njia/advisor.py` and the published demo: statistics are calculated separately from actual `openai/gpt-oss-20b` prose, and the 57 public acceptance/recording assertions demonstrate prototype behaviour rather than measured societal outcomes. The award accepts all participating countries, including our Kenya/ONLINE team, subject to organizer confirmation.

**Thunders — Engineering Excellence Award:** Njia demonstrates engineering care through server-enforced CV-to-AI consent, bounded document parsing, structured-output validation, labelled fallback, stale-state handling and excerpt-controlled HTML export. See `tests/test_advisor.py`, `njia/uploads.py` and `static/coach.js`: 73 backend tests passed separately from 48 acceptance plus nine recording assertions, with real production Groq output in the published demo. We are a Kenya/ONLINE team; no Kenya exclusion is stated in the published award description, with final eligibility determined by organizers.

### 19. AI/tool disclosure — list models, agents, datasets, APIs and generated assets used. Explain your chosen stack, access constraints, actual AI contribution and fallback. State honestly if no AI was used. Brev is optional; explain its use only if used. Do not include voucher codes, passwords or API keys.

Njia uses Python/FastAPI and static JavaScript for a lightweight mobile-browser experience, with deterministic historical-market calculations and local TF-IDF/cosine retrieval. The **new deployed root calls `/api/advise`, which requires consent and sends basic-contact-scrubbed CV text to Groq**, together with country/role, historical scope/top skills and vocabulary context. Actual new-production inference used **`openai/gpt-oss-20b`** to generate a personal summary, evidence strengths, gap explanations, draft rewrites, seven-day actions and interview guidance. Access requires a server-held Groq key and network/provider availability; missing credentials, provider failures or invalid output return a labelled curated brief.

**Product AI example:** labelled fictional sample CV + Kenya + target role → consented Groq assessment against CV and historical skill context → evidence-linked strengths, draft CV changes and a seven-day action brief. The model helps personalise prose; market statistics are computed by the application. The recorded output is real inference, not simulated advice.

Basic redaction is not full anonymization: identifying details can remain. Uploads are parsed in hosting-server request memory, not on-device; application-level non-persistence is not a claim about provider retention. The HTML brief excludes CV-evidence quotes and before/after sections by default, with optional inclusion, but other personalised prose can still reveal experience details. Validation checks structure, quotations and some unsupported numbers/tools, **not all factual accuracy**: an observed rewrite invented **“real-time sales monitoring,”** so human review is required. Market figures are calculated separately; coverage is not hiring probability.

The **older `/classic` only** offers manual skills, deterministic four-week plans and fixed quizzes; its optional `/api/plan` sends structured curriculum without CV text. The old no-CV-to-model boundary does not apply to the new advisor. Classic `NJIA_AI_PROVIDER=offline` does not disable the new advisor’s independent Groq path. Classic Ollama `qwen2.5:3b` was mock-tested only, not live-used; NVIDIA Brev was not used.

The dataset is attributed to `lukebarousse/data_jobs`: 18,371 historical 2023 postings across ten African/MENA countries. Prepared documentation identifies Apache-2.0, without independent provenance/licence verification. Synthetic inputs were used for validation. Results report **48 acceptance + 9 recording assertions = 57**, separately from **73 backend tests**; these are not an independent factuality, fairness or user-outcome evaluation.

**Build assistance:** development used **OpenCode**, main agent label **`github-copilot/gpt-6-astra`**, plus coding/review agents whose underlying model identities were not independently established. Assistance covered code, documentation and review; backend tests and browser checks exercised consent, validation, fallback and export behaviour, while factual faithfulness remains a known limit. UI visuals are code-native HTML/CSS. The **final eight-page presentation was generated locally with python-pptx and Playwright**; Gemini was not used for inference. The exact-90-second captioned Playwright demo records the real public coach and real Groq output, with no fabricated responses or synthetic voice. No credentials are included in public materials.

## Optional evidence fields

These appear before final confirmation in the current form and do not change the 20 required questions.

**Project cover / screenshot / logo URL — optional**

https://raw.githubusercontent.com/Eeshan-Vaghjiani/njia/main/docs/images/coach-desktop.png

**Live demo URL — optional**

https://gomycode-2026.vercel.app

**Testing, results and known limitations — optional**

- Backend suite: **73 tests passed** (`tests/`; run instructions in `README.md`), counted separately from browser assertions.
- Public coach: **48 acceptance + 9 recording assertions = 57**, with genuine Groq `openai/gpt-oss-20b` responses observed; evidence: `scripts/coach_acceptance.py`, published 90-second demo and `docs/AI_DISCLOSURE.md`.
- Provider errors/invalid output trigger labelled curated fallback (`njia/advisor.py`), but validation missed an observed rewrite inventing “real-time sales monitoring.” Physical-phone usability and employment outcomes have not been established.

**Responsible AI and data — optional**

Njia uses historical 2023 postings attributed to `lukebarousse/data_jobs`; prepared source documentation identifies Apache-2.0, without independent provenance/licence verification, and demonstration CVs are labelled synthetic. Explicit consent is required before basic-contact-scrubbed CV text is sent to Groq; CVs are processed in server request memory without application-level storage, which does not establish hosting/provider retention. Basic redaction is not anonymization, and generated claims require human review because validation does not guarantee factual accuracy. The historical sample is not current or representative, and coverage is not hiring probability; employment outcomes have not been established.

### 20. Final confirmation

Exact required checkbox statement:

> I confirm that our functional prototype, source code, presentation, 90-second demo video, project card details and AI/tool disclosure are complete, accessible and final.

**Pending human review and submission.** Open the published source, presentation and video signed out and review the answers before confirming. Enter the leader contact information privately, submit once before **19:30 EAT**, and save the confirmation receipt. **The form has not been submitted.**
