# Njia — AI, data and validation disclosure

**Final documentation checkpoint: 27 September 2026 · Dhruzzz · Kenya · ONLINE.** The deployed root at https://gomycode-2026.vercel.app is the new CV-to-AI coach. The old skills/learning interface remains at `/classic`.

## Actual runtime AI contribution

The new **`POST /api/advise`** accepts CV text, country, role and `consent`. It rejects advice without consent server-side. After basic contact scrubbing, it sends **CV text to Groq** with target country/role, historical market scope and top skill IDs, the allowed vocabulary and lexicon matches. The actual model verified in new production is **`openai/gpt-oss-20b`**.

Groq produces a personal brief: summary, CV-evidence strengths, gap explanations and first steps, before/after CV rewrite suggestions, exactly seven daily actions with deliverables, interview question/answer guidance and suggested skills. The app calculates market counts, demand percentages, coverage and priority ranking separately; those figures are not model-authored statistics. Confirming skills recalculates market evidence but does not regenerate the original AI brief. Edited CV/target inputs are labelled as stale until rebuilt.

### Added on 27 September: ask, match, practise

- **Follow-up questions — `POST /api/questions`.** Requires the same consent as the brief. After basic contact scrubbing, CV text, country/role and historical top skills go to `openai/gpt-oss-20b`, which proposes 3–5 questions. Skill questions always use four server-set options; detail questions must quote a phrase that exists in the CV. Output containing contacts, links or percentages is dropped; fewer than two valid questions returns a labelled curated set.
- **Answers in the brief — `POST /api/advise` `answers`.** Up to six self-reported answers are sent with the CV. In code, *used it at work / in a project or course* adds a vocabulary skill to the suggestions and *not yet* removes it. Rewrites may use numbers or tools only if they appear in the original CV quote or in a free-text detail answer, and are then labelled “Uses your answer — verify.” Skill-option answers never license new facts.
- **Live jobs — `POST /api/jobs`.** `source: "remote"` calls the Himalayas public jobs API (no AI) and keeps postings whose location restrictions include the selected country or are worldwide, crediting and linking Himalayas as its terms require. `source: "web"` calls `openai/gpt-oss-120b` with Groq's built-in `browser_search` tool (powered by Exa), sending only role, country, today's date and top market skill names. A web posting is kept only if its URL appears in the tool's search results; social, profile and search pages, expired postings and postings older than 120 days are dropped. Skill match = detected posting skills that are in the user's confirmed list; it is not a hiring probability.
- **Interview research — `POST /api/interview/questions`.** `openai/gpt-oss-120b` with `browser_search` receives only role, country and top market skill names. A question is kept only if its source URL is a page the search returned or opened (the Exa search page itself is excluded); fewer than three such questions returns a labelled curated bank. The user's skills only reorder results. “Use your evidence” hints are computed in the browser from the brief's strengths.
- **Practice feedback — `POST /api/interview/feedback`.** Needs its own consent checkbox. The scrubbed answer (and any matching CV evidence) goes to `openai/gpt-oss-20b` in JSON mode for a 1–5 score, STAR checklist, strengths, improvements and a stronger outline. Feedback is rejected — falling back to deterministic checklist feedback — if its shape or score is invalid, or if the outline adds numbers or tool names absent from the answer and evidence, or makes a hiring promise.
- **Backup provider.** Production now has NVIDIA configured. If Groq is missing or a supported JSON call fails, one request goes to **`openai/gpt-oss-20b` on the NVIDIA API Catalog** (`NJIA_FALLBACK_MODEL` overrides it), using the same prompts and feature validation, labelled `mode: "nvidia"`. The brief fails over on provider errors **or invalid assessments**, with up to 45 s for Groq plus 30 s for NVIDIA. Questions/feedback fail over on **shared-client provider errors** (including malformed completion envelopes); their subsequent feature-validation failures go directly to curated questions/checklist feedback, without another provider attempt. Each questions provider attempt has a 20 s limit; feedback has 30 s per provider. The consent text names the backup. Web searches never use NVIDIA. Its free endpoint is a rate-limited trial service governed by NVIDIA's API Trial Terms; this is not NVIDIA Brev.
- **Rate limits and caching.** Groq's free tier limits tokens per minute and per day per model, and one observed interview search used 93,301 tokens (mostly the text of opened pages). Web research therefore defaults to `NJIA_SEARCH_MODEL=openai/gpt-oss-120b`, separate from the brief model, at temperature 1.0 (at 0.2 the 120b model repeatedly produced unparseable tool calls). Successful searches are cached in process memory per role/country (web jobs 12 h, Himalayas 1 h, interview questions 24 h); identical concurrent job searches share one provider call. Failures fall back with labels and are never presented as AI output.

| Component | Method and boundary |
| --- | --- |
| Upload | In-memory PDF/DOCX/UTF-8 TXT parsing; no OCR; browser cap 4,000,000 bytes, backend 5 MiB |
| Follow-up questions | Groq / NVIDIA `openai/gpt-oss-20b`, consented scrubbed CV; server-fixed options; curated fallback |
| New CV advice | Groq / NVIDIA using consented, basic-contact-scrubbed CV text plus optional answers; default model `openai/gpt-oss-20b` |
| Live remote jobs | Himalayas public API, country/worldwide eligibility from each listing; no AI |
| Live local jobs / interview questions | Groq `openai/gpt-oss-120b` + `browser_search`; role/country/skill names only; URL must appear in tool results |
| Practice feedback | Groq / NVIDIA `openai/gpt-oss-20b`, separately consented answer; partial no-new-numbers/tools check; checklist fallback |
| Keyword extraction | Local vocabulary/alias matching with simple context rules; not LLM inference |
| Historical market | Canonicalized posting counts and top-15 demand-weighted coverage; not proficiency or hiring odds |
| Historical retrieval | scikit-learn TF-IDF/cosine similarity over 2023 postings; separate from live jobs |
| New fallback | Labelled curated brief using keyword evidence, historical priorities, seven daily actions and interview guidance; no AI-generated assessment or invented rewrite |
| Classic workflow only | Manual skills, four-week curated plans, optional curriculum-only Groq/Ollama wording, fixed quizzes and Markdown export |

## Consent, credentials and fallback

- The root checkbox explicitly consents to sending CV text, with basic contact redaction, to the AI provider. Uploads also require permission for server parsing. Optional preview parses only, then clears consent so the user agrees again before AI advice. Direct upload-to-brief proceeds from parsing to advice under the checked consent.
- The advisor uses a server-held `GROQ_API_KEY`. Model precedence is `NJIA_ADVISOR_MODEL`, then `GROQ_MODEL`, then `openai/gpt-oss-20b`. No key value belongs in shared documents or browser code.
- The advisor makes at most one Groq request (45 s) and one NVIDIA request (30 s) per assessment, without same-provider retries or redirects. With neither provider usable, or if backup validation fails, it returns a labelled curated result. Configuration alone is not proof of successful inference; the result exposes mode/model.
- **`NJIA_AI_PROVIDER=offline` is a classic-plan setting, not a global AI disable switch.** The new coach independently uses Groq/NVIDIA credentials. Without a Groq key, configured NVIDIA can still serve questions, advice and feedback; consent remains required.
- For **`/classic` only**, `/api/plan` checks remote opt-in with `use_ai`/`ai_consent` and sends allowlisted structured curriculum, not CV text. Old “CV never goes to AI” statements apply to classic extraction/plan processing only and are false for the new endpoint.
- Classic local Ollama defaults to `qwen2.5:3b` and permits loopback endpoints. It was mock-tested only, not installed/live-tested, and is not used by the new advisor. NVIDIA Brev was not used.

## Privacy and exported content

Uploads and pasted text reach the hosting server on the public app; this is **not on-device processing**. Parsing/advice use request memory with no application-level CV persistence or prompt logging. Browser state is in memory, without accounts, analytics, localStorage/sessionStorage or a user database. These statements do not establish hosting-provider, Groq or NVIDIA retention policies, nor guarantee secure erasure. Browser cancellation may leave an already received server request running.

Scrubbing removes common email addresses, phone-like numbers, links and explicitly labelled identity lines. It can miss names, employers, addresses and other personal details, or remove unrelated numbers. **Basic redaction is not full anonymization.** Review/remove details before consent; document previews themselves may contain personal information.

The new download is **`njia-career-brief.html`**. It excludes **CV-evidence quote sections and before/after rewrite sections by default**; the user can explicitly include them. The complete raw CV is not attached, but summaries, action items and other personalised advice may still reveal CV details even with excerpts excluded. Review the file before sharing. Downloads persist independently of session reset; “Share Njia” shares only the public app URL. Classic Markdown export has its own content rules and is not the new root download.

## Validation is not a factual guarantee

The advisor validates JSON shape/types/lengths, seven-day ordering, allowed skills and source-quote presence using normalized text matching. It filters some rewrites introducing unsupported numbers or lexicon-recognized tools, and checks some employment-promise patterns. These are partial safeguards, not verification of all factual claims or semantic faithfulness.

**The latest successful recording includes an unsupported rewrite: “support inventory decisions.”** The supplied detail explicitly said the dashboard was a personal practice project using synthetic retail data, not used by a real business. The “Uses your answer — verify” label did not prevent the embellishment. Earlier output introduced “real-time sales monitoring” and an unstated purpose in a practice outline. Every rewrite and generated claim requires human review before use. The published video's two overclaiming narration captions have been corrected to explicitly require factual review; the actual app/model outputs remain unchanged. CV evidence is self-reported; absence from a CV does not establish lack of ability. No certification, hiring outcome or placement guarantee is offered.

## Data and evaluation

The bundled corpus contains **18,371 historical 2023 tech/data postings** from ten African/MENA countries, including Kenya. Prepared documentation attributes it to [lukebarousse/data_jobs](https://huggingface.co/datasets/lukebarousse/data_jobs) and identifies Apache-2.0; provenance and licensing were not independently verified. This is not a licensing determination for the application code.

Skills are lowercased, aliases canonicalized and duplicates removed per posting. Fewer than 50 local postings for a role triggers a labelled ten-country role sample. Demand is the proportion of sample postings mentioning a skill; coverage weights selected skills among the top 15 by their posting mentions. The historical, tech/data-focused and geographically uneven sample is neither current vacancies nor a representative survey of the Kenyan labour market.

**Latest evidence, kept separate by scope:**

- **126 backend tests passed offline**, reported by the main workflow; no older test subtotal is presented as current.
- **19 checks passed** in [the latest public recording](https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/njia-coach-demo-results.json), with **zero failed checks, zero late cues, zero JavaScript errors and zero mocked responses**. Real Groq `openai/gpt-oss-20b`: four follow-ups **1.271 s** including PDF upload, brief **1.450 s**, feedback **0.844 s**, score **4/5**. It showed **8 remote + 3 local cards**, and **8 web interview questions from 3 source URLs** on Groq `openai/gpt-oss-120b`. The source headline's 111 remote matches is distinct from the eight cards rendered.
- **Actual local enforced NVIDIA fallback** in [nvidia-fallback-results.json](https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/nvidia-fallback-results.json): Groq forced unavailable; five validated questions in **11.564 s** and a validated seven-day brief in **16.637 s**, both `mode: "nvidia"`, model `openai/gpt-oss-20b`, one NVIDIA request each. This two-request test did not exercise feedback. It is separate from the public video, which used Groq, and does not establish production failover merely because the production key is configured. **No Brev use.**
- **Older public evidence: 57 assertions (48 acceptance + 9 recording)**. This remains historical evidence, not the latest recording count and not added to it. No new mobile acceptance run is claimed.

**Recording session and search cost:** initial cache warming called jobs (three results, **15.96 s**) and interview research (curated fallback, **4.56 s**), then stopped before recording or coaching. Three subsequent recording attempts failed: interview research missed cues after **8.187 s** and **29.626 s**, then no local card appeared within an assertion window. The final take succeeded with all observed HTTP responses 200; its fallback allowance was enabled but unused. It skipped a new warm-up, rather than establishing cold caches: the **0.390 s** interview response was a cached result. The session total was **27 application POSTs** (4 uploads, 4 follow-up, 4 brief, 4 remote-job, 5 web-job, 5 interview-search and 1 feedback), with all nine coaching completions returned through Groq. Search endpoint calls are not upstream inference-call counts because caches can hit. One separately observed browser search used **93,301 tokens**; exact full-session provider token usage and monetary cost were not exposed. This session account was transcribed from local `artifacts/recording-handoff.md` and `artifacts/njia-coach-demo-warmup-failure.json`. A successful final take is not a claim that all attempts were flawless.

No tests were rerun for this documentation-only update. These counts are not independent model-quality, fairness or user-outcome studies. Earlier 38-check production evidence and four-week plan timings concern the older classic flow and must not be presented as current root verification. Browser mobile/emulation evidence does not establish physical-phone performance or adoption.

The earlier extraction-only synthetic evaluation had 20 developer-authored examples, 41 true positives, 2 false positives, 1 false negative, precision 0.9535, recall 0.9762 and 17/20 exact skill-set matches. Its zero inference calls/cost applies only to that keyword-extraction evaluation. It excludes hosted coaching and total operating costs; no general latency or factual-accuracy benchmark is claimed. Genuine user feedback and employment outcomes remain unestablished.

## Development, presentation and recording tools

Development used **OpenCode**: earlier work and this documentation update used main agent label **`github-copilot/gpt-6-astra`**. The feature-build workflow reports **`github-copilot/claude-opus-5.5`** coordinating coding/review subagents whose underlying identities were not independently established. Assistance covered application code, tests, documentation, recording/deck tooling and review. The lightweight application stack uses Python/FastAPI, static HTML/CSS/JavaScript, HTTPX, Pydantic, document parsers and scikit-learn; checks use unittest and Playwright/Chromium. UI visuals are code-native.

The **eight-page deck was regenerated locally with python-pptx and Playwright**. Gemini was not used for inference; NVIDIA Brev was not used. No credential values are disclosed. The published captioned video is exactly **90.000 seconds**, showing real public-app interaction and real Groq output; no mocked responses or synthetic voice are used. It now includes **real user-provided human narration**, at 1×, 25 fps, 2,250 frames. The latest PDF/PPTX, video, evidence JSONs and [voiceover script](https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/VOICEOVER.md) are published at the same URLs. The script remains a prepared cue guide, not a listening-verified transcript of the supplied recording.

**Final video delivery:** [MP4](https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/njia-demo-90s.mp4): **H.264, 1280×720, 25 fps, faststart, 6,303,031 bytes, 90.000 seconds, 1×**, with human narration, visible captions and **AAC 48 kHz stereo**. The user explicitly supplied the human audio and requested replacement at the same submitted URL; the main workflow uploaded the existing release asset with `--clobber`. The historical WebM remains silent and optional.

**Narration postproduction:** [scripts/add_voiceover.py](../scripts/add_voiceover.py) mixed the **85.421083-second** human recording starting at **0**, at normal speed with original pauses retained and silence padding to 90 seconds. Audio processing used a **70 Hz high-pass filter, loudnorm and AAC 192 kb/s**. The corrected MP4's video stream was copied unchanged and hash-verified. Output SHA-256: `00929c0452f1d06ec17b109e23902d8805111c4a2df00a2a1a03f0eb06e6a2d9`. Public evidence: [narration-results.json](https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/narration-results.json). Main-workflow verification was technical playback verification only, not listening or semantic timing review. Original recording counts remain unchanged; this was not a new application recording or inference run.

**Postproduction caption correction:** offline PNG overlays and a lossless VP9 re-encode of the WebM source changed only the narration rectangle (`x=20, y=600, width=1240, height=100`):

- **53.240–57.280 s** (end exclusive): “Draft rewrites need factual review. Verify every claim against your CV and answers; AI can add unsupported details.”
- **76.360–83.440 s** (end exclusive): “AI feedback suggests structure. Verify every fact; it can add unsupported details.”

The old overclaiming captions are no longer present in the final video. The [recording JSON](https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/njia-coach-demo-results.json) records this under `caption_corrections`: decoded frame hashes match outside the correction windows, and decoded pixels outside the caption rectangle match in **every frame** of the corrected WebM source, before H.264 MP4 conversion. No app/model output content was edited or fabricated, no new API requests were made, and duration and speed remain unchanged. This earlier caption-only correction and format conversion preceded the human-narration mix described above; neither was a new recording run.

## Public handoff

- Live: https://gomycode-2026.vercel.app
- Source: https://github.com/Eeshan-Vaghjiani/njia
- PDF: https://github.com/Eeshan-Vaghjiani/njia/blob/main/presentation/Njia-Dhruzzz.pdf
- PPTX: https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/Njia-Dhruzzz.pptx
- Demo MP4: https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/njia-demo-90s.mp4

The latest deployment is live at the same URL with NVIDIA configured. The latest presentation, human-narrated captioned video, recording JSON, NVIDIA JSON, narration JSON and voiceover script are **published at the existing URLs**. The user reports this video URL was submitted; form receipt not verified by the development workflow. See the [final checklist](FINAL_CHECKLIST.md) for review and receipt verification.
