# Njia — AI, data and validation disclosure

**Final documentation checkpoint: 27 September 2026 · Dhruzzz · Kenya · ONLINE.** The deployed root at https://gomycode-2026.vercel.app is the new CV-to-AI coach. The old skills/learning interface remains at `/classic`.

## Actual runtime AI contribution

The new **`POST /api/advise`** accepts CV text, country, role and `consent`. It rejects advice without consent server-side. After basic contact scrubbing, it sends **CV text to Groq** with target country/role, historical market scope and top skill IDs, the allowed vocabulary and lexicon matches. The actual model verified in new production is **`openai/gpt-oss-20b`**.

Groq produces a personal brief: summary, CV-evidence strengths, gap explanations and first steps, before/after CV rewrite suggestions, exactly seven daily actions with deliverables, interview question/answer guidance and suggested skills. The app calculates market counts, demand percentages, coverage and priority ranking separately; those figures are not model-authored statistics. Confirming skills recalculates market evidence but does not regenerate the original AI brief. Edited CV/target inputs are labelled as stale until rebuilt.

| Component | Method and boundary |
| --- | --- |
| Upload | In-memory PDF/DOCX/UTF-8 TXT parsing; no OCR; browser cap 4,000,000 bytes, backend 5 MiB |
| New CV advice | Groq chat-completions API using consented, basic-contact-scrubbed CV text; actual model `openai/gpt-oss-20b` |
| Keyword extraction | Local vocabulary/alias matching with simple context rules; not LLM inference |
| Historical market | Canonicalized posting counts and top-15 demand-weighted coverage; not proficiency or hiring odds |
| Historical retrieval | scikit-learn TF-IDF/cosine similarity; not live vacancy search |
| New fallback | Labelled curated brief using keyword evidence, historical priorities, seven daily actions and interview guidance; no AI-generated assessment or invented rewrite |
| Classic workflow only | Manual skills, four-week curated plans, optional curriculum-only Groq/Ollama wording, fixed quizzes and Markdown export |

## Consent, credentials and fallback

- The root checkbox explicitly consents to sending CV text, with basic contact redaction, to the AI provider. Uploads also require permission for server parsing. Optional preview parses only, then clears consent so the user agrees again before AI advice. Direct upload-to-brief proceeds from parsing to advice under the checked consent.
- The advisor uses a server-held `GROQ_API_KEY`. Model precedence is `NJIA_ADVISOR_MODEL`, then `GROQ_MODEL`, then `openai/gpt-oss-20b`. No key value belongs in shared documents or browser code.
- The advisor makes at most one Groq request per assessment, with a 45-second total deadline and no retries/redirects. Missing credentials, provider errors/timeouts or invalid output return a labelled curated result. Provider configuration alone is not proof of successful inference; the result exposes mode/model.
- **`NJIA_AI_PROVIDER=offline` is a classic-plan setting, not a global AI disable switch.** The new advisor independently uses the Groq key. Without that key it falls back, but `/api/advise` still requires consent.
- For **`/classic` only**, `/api/plan` checks remote opt-in with `use_ai`/`ai_consent` and sends allowlisted structured curriculum, not CV text. Old “CV never goes to AI” statements apply to classic extraction/plan processing only and are false for the new endpoint.
- Classic local Ollama defaults to `qwen2.5:3b` and permits loopback endpoints. It was mock-tested only, not installed/live-tested, and is not used by the new advisor. NVIDIA Brev was not used.

## Privacy and exported content

Uploads and pasted text reach the hosting server on the public app; this is **not on-device processing**. Parsing/advice use request memory with no application-level CV persistence or prompt logging. Browser state is in memory, without accounts, analytics, localStorage/sessionStorage or a user database. These statements do not establish hosting-provider or Groq retention policies, nor guarantee secure erasure. Browser cancellation may leave an already received server request running.

Scrubbing removes common email addresses, phone-like numbers, links and explicitly labelled identity lines. It can miss names, employers, addresses and other personal details, or remove unrelated numbers. **Basic redaction is not full anonymization.** Review/remove details before consent; document previews themselves may contain personal information.

The new download is **`njia-career-brief.html`**. It excludes **CV-evidence quote sections and before/after rewrite sections by default**; the user can explicitly include them. The complete raw CV is not attached, but summaries, action items and other personalised advice may still reveal CV details even with excerpts excluded. Review the file before sharing. Downloads persist independently of session reset; “Share Njia” shares only the public app URL. Classic Markdown export has its own content rules and is not the new root download.

## Validation is not a factual guarantee

The advisor validates JSON shape/types/lengths, seven-day ordering, allowed skills and source-quote presence using normalized text matching. It filters some rewrites introducing unsupported numbers or lexicon-recognized tools, and checks some employment-promise patterns. These are partial safeguards, not verification of all factual claims or semantic faithfulness.

**An observed rewrite introduced “real-time sales monitoring,” an unsupported embellishment.** Every rewrite and other generated claim requires human review before use. The prompt requests fact preservation, but neither it nor passing assertions guarantees factual advice. CV evidence is self-reported; absence from a CV does not establish lack of ability. No certification, hiring outcome or placement guarantee is offered.

## Data and evaluation

The bundled corpus contains **18,371 historical 2023 tech/data postings** from ten African/MENA countries, including Kenya. Prepared documentation attributes it to [lukebarousse/data_jobs](https://huggingface.co/datasets/lukebarousse/data_jobs) and identifies Apache-2.0; provenance and licensing were not independently verified. This is not a licensing determination for the application code.

Skills are lowercased, aliases canonicalized and duplicates removed per posting. Fewer than 50 local postings for a role triggers a labelled ten-country role sample. Demand is the proportion of sample postings mentioning a skill; coverage weights selected skills among the top 15 by their posting mentions. The historical, tech/data-focused and geographically uneven sample is neither current vacancies nor a representative survey of the Kenyan labour market.

**Latest evidence reported by the main workflow:**

- **48 new-production acceptance assertions passed.**
- **9 recording assertions passed.**
- **57 total acceptance/recording assertions (48 + 9).**
- **73 backend tests passed, separately.**
- Real new-production Groq inference verified with **`openai/gpt-oss-20b`**; the updated exact-90-second demo records the real public app.

No tests were rerun for this documentation-only update. These counts are not independent model-quality, fairness or user-outcome studies. Earlier 38-check production evidence and four-week plan timings concern the older classic flow and must not be presented as current root verification. Browser mobile/emulation evidence does not establish physical-phone performance or adoption.

The earlier extraction-only synthetic evaluation had 20 developer-authored examples, 41 true positives, 2 false positives, 1 false negative, precision 0.9535, recall 0.9762 and 17/20 exact skill-set matches. Its zero inference calls/cost applies only to that keyword-extraction evaluation. It excludes hosted coaching and total operating costs; no general latency or factual-accuracy benchmark is claimed. Genuine user feedback and employment outcomes remain unestablished.

## Development, presentation and recording tools

Development used **OpenCode**, main agent label **`github-copilot/gpt-6-astra`**, plus coding/review agents in the same harness whose underlying identities were not independently established. Assistance covered application code, documentation and review. The lightweight application stack uses Python/FastAPI, static HTML/CSS/JavaScript, HTTPX, Pydantic, document parsers and scikit-learn; checks use unittest and Playwright/Chromium. UI visuals are code-native.

The **final eight-page deck was generated locally with python-pptx and Playwright**. Gemini was not used for inference; NVIDIA Brev was not used. No credential values are disclosed. The published captioned video is exactly **90.000 seconds**, showing real public-app interaction and real Groq output; no fabricated responses or synthetic voice are used. The [voiceover script](VOICEOVER.md) is ready as supporting material; it is not a claim that narration is present in the published recording.

## Public handoff

- Live: https://gomycode-2026.vercel.app
- Source: https://github.com/Eeshan-Vaghjiani/njia
- PDF: https://github.com/Eeshan-Vaghjiani/njia/blob/main/presentation/Njia-Dhruzzz.pdf
- PPTX: https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/Njia-Dhruzzz.pptx
- Demo: https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/njia-demo-90s.webm

Source, presentation and demo are published. The official project form **has not been submitted**. See the [final checklist](FINAL_CHECKLIST.md) for human review and submission.
