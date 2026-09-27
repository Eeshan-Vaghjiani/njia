# Final submission checklist — Dhruzzz / Kenya / ONLINE

**27 September 2026 · Submission pending.** The final answers are in [SUBMISSION_DRAFT.md](SUBMISSION_DRAFT.md). Deadline: **today, 19:30 EAT / 16:30 UTC**. A source push or release upload is not a form submission.

## Final decisions and prepared material

| Item | Final handoff |
| --- | --- |
| Team | **Dhruzzz · Kenya · ONLINE** |
| Leader | **Eeshan Vaghjiani**; email entered privately in the form |
| Full roster | **Eeshan Vaghjiani; Bhavin Mepani; Dhruvin Bhudia** |
| Project | **Njia** |
| Primary award | **Click Mobile — Mobile-First Impact Award** |
| Partner selections | **Click Mobile, Brightest GmbH, Artefact, Thunders**; each has a 2–3-sentence fit explanation in the draft |
| Cash-prize scope | Click Mobile: **KSh 50,000 total**, Kenya only, allocation TBC; published wording does not exclude ONLINE or impose onsite attendance |
| Current product | CV-to-AI coach at the deployed root with **follow-up questions, live eligible jobs, web-sourced interview questions and practice feedback** (added 27 September); older skills/four-week-plan interface at `/classic` |
| AI | `/api/questions`, `/api/advise` and `/api/interview/feedback` require consent and use `openai/gpt-oss-20b`; `/api/jobs` (web) and `/api/interview/questions` use `openai/gpt-oss-120b` + Groq `browser_search` with role/country/skill names only; remote jobs come from the Himalayas API |
| Brief | Follow-up answers, summary, evidence strengths, priorities, before/after suggestions, seven-day actions, interview guidance, live jobs, interview practice, WhatsApp checklist and downloadable HTML |
| Export privacy | CV-evidence and before/after sections excluded by default; explicit inclusion available; other personalised advice may reveal CV details |
| Accuracy limit | Observed unsupported **“real-time sales monitoring”** rewrite; generated claims require review, with no overall factual guarantee |
| Latest reported checks | **48 acceptance + 9 recording assertions = 57**, separately from **73 backend tests** |
| Presentation | Published **8 pages**, generated locally with **python-pptx + Playwright** |
| Demo | Updated **exactly 90.000-second**, captioned recording of real public-app interaction and real Groq output |
| Voiceover | [Ready script](VOICEOVER.md); the published demo is captioned, and narration is not explicitly mandatory in the official requirements |
| Publication status | **Source, presentation and demo published; official form not submitted** |

## Final links

| Form use | URL |
| --- | --- |
| Source — field 12 | https://github.com/Eeshan-Vaghjiani/njia |
| Presentation — field 13, viewable PDF | https://github.com/Eeshan-Vaghjiani/njia/blob/main/presentation/Njia-Dhruzzz.pdf |
| Video — field 14 | https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/njia-demo-90s.webm |
| Editable presentation companion | https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/Njia-Dhruzzz.pptx |
| Live prototype | https://gomycode-2026.vercel.app |
| Release page | https://github.com/Eeshan-Vaghjiani/njia/releases/tag/demo-v1 |

Open these published links signed out during the final review.

## Form coverage

The draft contains all **20 required fields**, in order: country; ONLINE; team; leader name; leader email instruction; project title; full roster; summary **≤150 words**; problem; features; technologies; source; presentation; video; next step; partner selections; **Click Mobile primary**; four award explanations; AI/tool disclosure; final confirmation.

The form requests URLs rather than file uploads. A hosted PDF can be the presentation URL. It now also offers **four optional fields**: screenshot/cover/logo URL, live demo URL, testing/results/limitations, and responsible AI/data; suggested answers are in the draft. No separate member-contact list, project-card upload or Docker field is required. Do not select “Country podium only” alongside partner awards. Eligibility remains subject to organizer participation records; prize preference does not guarantee an award.

## Sources

- [Official onboarding, submission and awards](https://hackathon.gomycode.com/onboarding)
- [Official project form](https://docs.google.com/forms/d/e/1FAIpQLSebmyKeBPv2mrmy4T_wI2_z9SBjjSTZ-O-_ewiWs6PBEikRjw/viewform)
- [Recorded requirements](HACKATHON_REQUIREMENTS.md), [final draft](SUBMISSION_DRAFT.md), [current AI disclosure](AI_DISCLOSURE.md)

## Last steps — deploy, record, review and submit

- [ ] **Deploy (Eeshan):** `git pull && vercel deploy --prod`; confirm `https://gomycode-2026.vercel.app/static/jobs.js` returns 200. No new environment variables are required (`NJIA_SEARCH_MODEL` defaults to `openai/gpt-oss-120b`). Optional but recommended: move the production Groq organisation to a paid tier — one web search can use ~90K tokens against a free-tier limit of 200K tokens per day per model.
- [ ] **Record:** `cd scripts && ../.venv/bin/python record_coach_demo.py`, then replace the release asset under the same URL: `gh release upload demo-v1 artifacts/njia-demo-90s.webm artifacts/njia-coach-demo-results.json --clobber`.
- [ ] **Human final review:** open source/PDF/video signed out, verify the eight-page deck/exact-90-second coach recording, and review all 20 required answers plus the optional evidence. Confirm roster/registration details, enter the leader contact information privately, retain Click Mobile as primary with all four partner selections, and check the final confirmation when the deliverables are accessible and final.
- [ ] **Human form submission:** submit the [official form](https://docs.google.com/forms/d/e/1FAIpQLSebmyKeBPv2mrmy4T_wI2_z9SBjjSTZ-O-_ewiWs6PBEikRjw/viewform) once before **19:30 EAT** and save the receipt. **Not submitted at this handoff.**
