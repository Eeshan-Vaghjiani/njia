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
| AI | Consented questions/brief/feedback: Groq `openai/gpt-oss-20b`, with NVIDIA API Catalog backup configured in production. Web jobs/interview research: Groq `openai/gpt-oss-120b` + `browser_search`, role/country/market skill names only, no NVIDIA search fallback. Remote jobs: Himalayas API. No Brev |
| Brief | Follow-up answers, summary, evidence strengths, priorities, before/after suggestions, seven-day actions, interview guidance, live jobs, interview practice, WhatsApp checklist and downloadable HTML |
| Export privacy | CV-evidence and before/after sections excluded by default; explicit inclusion available; other personalised advice may reveal CV details |
| Accuracy limit | Latest rewrite added unsupported **“support inventory decisions”** despite a personal synthetic-data project answer. Human review required; passing checks do not prove factual faithfulness |
| Latest reported checks | **126 backend tests passed offline**; **19 latest public-recording checks**, zero late cues/JavaScript errors. Older **57 public assertions (48 + 9)** are separate historical evidence |
| NVIDIA evidence | Separate local forced-Groq-unavailable test: **5 validated questions / 11.564 s**, **7-day validated brief / 16.637 s**, actual `openai/gpt-oss-20b`, one NVIDIA request each; not shown in video or proof of production failover |
| Presentation | Regenerated **8 pages**, locally with **python-pptx + Playwright**; PDF/PPTX published at same URLs |
| Demo | Final **MP4: H.264, 1280×720, 25 fps, faststart, approximately 4.2 MB, 90.000 seconds**, silent captioned public-app recording, 1×, 19 checks passed; real Groq output, zero mocked responses. Converted from the latest caption-corrected recording with no app/model output content edits. WebM retained only as an optional source; pixel-preservation checks apply to that source |
| Voiceover | [Ready script](VOICEOVER.md); the published demo is captioned, and narration is not explicitly mandatory in the official requirements |
| Publication status | **Latest app deployed; PDF/PPTX, corrected video, recording JSON, NVIDIA JSON and voiceover published at same URLs; official form not submitted** |

## Final links

| Form use | URL |
| --- | --- |
| Source — field 12 | https://github.com/Eeshan-Vaghjiani/njia |
| Presentation — field 13, viewable PDF | https://github.com/Eeshan-Vaghjiani/njia/blob/main/presentation/Njia-Dhruzzz.pdf |
| Video MP4 — field 14 | https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/njia-demo-90s.mp4 |
| Editable presentation companion | https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/Njia-Dhruzzz.pptx |
| Live prototype | https://gomycode-2026.vercel.app |
| Release page | https://github.com/Eeshan-Vaghjiani/njia/releases/tag/demo-v1 |
| Recording evidence and caption-correction disclosure | https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/njia-coach-demo-results.json |
| Separate local NVIDIA evidence | https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/nvidia-fallback-results.json |
| Voiceover release asset | https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/VOICEOVER.md |

Open these published links signed out during the final review.

## Form coverage

The draft contains all **20 required fields**, in order: country; ONLINE; team; leader name; leader email instruction; project title; full roster; summary **≤150 words**; problem; features; technologies; source; presentation; video; next step; partner selections; **Click Mobile primary**; four award explanations; AI/tool disclosure; final confirmation.

The form requests URLs rather than file uploads. A hosted PDF can be the presentation URL. It now also offers **four optional fields**: screenshot/cover/logo URL, live demo URL, testing/results/limitations, and responsible AI/data; suggested answers are in the draft. No separate member-contact list, project-card upload or Docker field is required. Do not select “Country podium only” alongside partner awards. Eligibility remains subject to organizer participation records; prize preference does not guarantee an award.

## Sources

- [Official onboarding, submission and awards](https://hackathon.gomycode.com/onboarding)
- [Official project form](https://docs.google.com/forms/d/e/1FAIpQLSebmyKeBPv2mrmy4T_wI2_z9SBjjSTZ-O-_ewiWs6PBEikRjw/viewform)
- [Recorded requirements](HACKATHON_REQUIREMENTS.md), [final draft](SUBMISSION_DRAFT.md), [current AI disclosure](AI_DISCLOSURE.md)

## Evidence review

- [Latest recording JSON](https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/njia-coach-demo-results.json): four Groq 20b questions **1.271 s including upload**, brief **1.450 s**, feedback **0.844 s**, score **4/5**; **8 remote + 3 local cards**, **8 web interview questions / 3 source URLs** on Groq 120b. `caption_corrections` records the two caption-only postproduction overlays; no new API calls or recording run.
- [Local NVIDIA JSON](https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/nvidia-fallback-results.json): two real validated fallback responses with Groq forced unavailable; no feedback inference in this test.
- [Session disclosure](AI_DISCLOSURE.md#data-and-evaluation): initial cache warming returned jobs but curated interview fallback, then three recording attempts failed on search timing/local-card availability before the final success. **27 application POSTs** across the session; the final **0.390 s interview response was cached**. A separately observed search used **93,301 tokens**; exact session provider token use/cost is unknown. The successful run had no failed checks; this does not describe all attempts as flawless.
- Provider scope: brief fallback covers provider errors and invalid assessments; questions/feedback fail over on shared-client provider errors, while later feature-validation failures go directly to curated/checklist output. Missing Groq credentials still permit configured NVIDIA coaching.

## Last steps — review and submit

- [x] **Deploy:** latest features live at https://gomycode-2026.vercel.app, NVIDIA key configured (main-workflow report).
- [x] **Record and regenerate:** new exact-90-second video passed 19 checks; eight-page deck regenerated.
- [x] **Publication:** latest PDF/PPTX, corrected video, recording JSON, NVIDIA JSON and voiceover uploaded at the same public URLs. No additional recording is needed.
- [ ] **Human final review:** open source/PDF/video signed out, verify the eight-page deck/exact-90-second coach recording, and review all 20 required answers plus the optional evidence. Confirm roster/registration details, enter the leader contact information privately, retain Click Mobile as primary with all four partner selections, and check the final confirmation when the deliverables are accessible and final.
- [ ] **Human form submission:** submit the [official form](https://docs.google.com/forms/d/e/1FAIpQLSebmyKeBPv2mrmy4T_wI2_z9SBjjSTZ-O-_ewiWs6PBEikRjw/viewform) once before **19:30 EAT** and save the receipt. **Not submitted at this handoff.**
