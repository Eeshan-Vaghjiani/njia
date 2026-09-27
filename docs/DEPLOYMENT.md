# Deploy Njia

**Production:** https://gomycode-2026.vercel.app
**Health:** https://gomycode-2026.vercel.app/api/health

**Latest handoff, 27 September 2026:** new follow-up questions, live jobs, interview research and practice feedback are deployed at this same URL; **NVIDIA backup is configured in production** (main-workflow report). The latest eight-page PDF/PPTX, corrected 90-second video, recording JSON, NVIDIA JSON and voiceover are **published at the same URLs**. Deployment and upload are complete; human final review and form submission remain.

## Active Vercel configuration

The project is `eeshans-projects-0934fb87/gomycode-2026`. Production is deployed through the Vercel CLI. **GitHub auto-deploy is not connected**; a source push does not deploy the app.

`vercel.json` declares the Python/FastAPI service explicitly:

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "services": {
    "njia": {
      "root": ".",
      "runtime": "python",
      "framework": "fastapi",
      "entrypoint": "njia.app:app"
    }
  },
  "rewrites": [
    { "source": "/(.*)", "destination": { "type": "service", "service": "njia" } }
  ]
}
```

Vercel reads pinned dependencies from `pyproject.toml`, which specifies Python `>=3.12,<3.14` and the same entrypoint under `[tool.vercel]`. `api/index.py` is a legacy adapter, not the active Services entrypoint. `.vercelignore` excludes secrets and development artifacts while retaining app modules, static assets and `data/africa_jobs_subset.jsonl`.

## Server environment

| Variable | Value / purpose |
| --- | --- |
| `GROQ_API_KEY` | Server-held secret; configure in Vercel environment settings |
| `GROQ_MODEL` | `openai/gpt-oss-20b` |
| `NJIA_ADVISOR_MODEL` | Optional advisor override; otherwise uses `GROQ_MODEL` |
| `NJIA_SEARCH_MODEL` | Optional; web research model, default `openai/gpt-oss-120b` (separate free-tier token bucket) |
| `NVIDIA_API_KEY` | Server-held secret from build.nvidia.com; configured in current production; enables NVIDIA API Catalog backup for questions, brief and feedback |
| `NJIA_FALLBACK_MODEL` | Optional; NVIDIA backup model, default `openai/gpt-oss-20b` |
| `NJIA_AI_PROVIDER` | `groq` for optional classic plan rewriting |
| `NJIA_PUBLIC_ORIGINS` | `https://gomycode-2026.vercel.app` |
| `OPENBLAS_NUM_THREADS` | `1` |

The root questions/advisor require `consent=true` before sending best-effort-contact-scrubbed CV text to Groq or NVIDIA; practice feedback has separate consent. **Without a Groq key, configured NVIDIA can still serve these JSON coaching calls.** The brief tries at most one Groq request (45 s), then one NVIDIA request (30 s) on provider errors or invalid assessments. Questions/feedback use shared-client failover on provider errors, with limits of 20 s / 30 s per provider respectively; their later feature-validation failures return curated/checklist output without trying another provider. With neither provider usable, labelled curated/checklist results remain. `NJIA_AI_PROVIDER=offline` affects classic plans only, not these paths.

Web jobs and interview research require Groq **`openai/gpt-oss-120b`** by default, with no NVIDIA search fallback. Same-model 20b coaching backup means the default NVIDIA model matches the coaching model, not the search model. `NJIA_FALLBACK_MODEL` may override it. NVIDIA API Catalog is not Brev; Brev was not used.

## Publish and verify

From the linked project root:

```powershell
vercel whoami
vercel deploy --prod
```

Confirm the account/project and successful build, then check:

1. `/api/health` reports healthy status and 18,371 postings.
2. `/` loads the coach and its JS/CSS; `/classic` loads the older interface.
3. Sample input, consent, real advice, skill review and HTML download work.
4. Mobile layout remains usable; check the returned mode/model rather than assuming configured credentials prove inference.

Latest evidence is **126 backend tests passed offline** (main report), separately from **19 checks in the new public recording**, with zero failed checks, late cues, JavaScript errors or mocked responses. Groq `openai/gpt-oss-20b` returned four follow-ups in **1.271 s including PDF upload**, the brief in **1.450 s**, and feedback in **0.844 s**, scoring **4/5**. The UI rendered **8 remote + 3 local jobs**, plus **8 web interview questions from 3 source URLs** on `openai/gpt-oss-120b`. See [recording results](https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/njia-coach-demo-results.json). Its `caption_corrections` records two narration-only overlays; app/model output pixels are unchanged in every frame of the corrected WebM source, with no new API calls or recording run. Final delivery is [MP4](https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/njia-demo-90s.mp4), converted from that latest corrected source as `artifacts/njia-demo-90s.mp4`: **H.264, 1280×720, 25 fps, faststart, approximately 4.2 MB, 90.000 s, 1×, silent**, with no app/model output content edits. WebM is retained only as an optional source. The **older 57 public assertions (48 + 9)** remain separate historical evidence; no new mobile acceptance run is claimed.

[Actual local NVIDIA fallback evidence](https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/nvidia-fallback-results.json) forced Groq unavailable and returned **five validated questions in 11.564 s** and a **validated seven-day brief in 16.637 s**, both `mode: "nvidia"`, model `openai/gpt-oss-20b`, one request each. This is not production-failover footage: the successful public video used Groq, and the local test did not exercise feedback. These results do not establish all provider-failure, near-limit-upload or physical-phone behaviour in production.

### Search caches and recording-session cost

Successful job results use process-local role/country caches (Himalayas **1 h**, web jobs **12 h**); interview research has a **24 h** cache, including fallback caching behaviour when Groq is configured. These caches are not durable across process replacement or guaranteed shared across instances. Search-model separation reduces competition for 20b coaching quotas but does not guarantee provider availability.

Initial cache warming returned three local jobs in **15.96 s**, then curated interview fallback in **4.56 s**, stopping before recording/coaching. Three later takes failed: interview searches missed timeline cues after **8.187 s** and **29.626 s**, then local cards did not appear within the assertion window. The final successful take skipped new warm-up, used existing caches and made seven POSTs plus metadata GET, all HTTP 200; fallback allowance was enabled but unused. Its **0.390 s interview response was cached**, not cold-search performance.

The full session made **27 application POSTs**, including initial warming. Cache hits mean endpoint counts are not upstream inference counts; exact full-session token usage and monetary cost were unavailable. One separately observed search used **93,301 tokens**, motivating caches and the separate 120b model. Preserve this context when citing latency or cost; see [session disclosure](AI_DISCLOSURE.md#data-and-evaluation).

Keep frontend and API on the same origin. `NJIA_PUBLIC_ORIGINS` handles the public HTTPS origin; do not disable origin checks to fix proxy mismatches. Vercel Services does not use the Dockerfile’s Uvicorn flags. Browser uploads are limited to **4,000,000 bytes** for headroom below Vercel’s **4.5 MB request limit**; the backend’s **5 MiB** parser limit does not override the host limit.

## Docker packaging

Docker is optional packaging, not the active production deployment. Keep the Dockerfile COPY allowlist and `.dockerignore` aligned with the runtime: `requirements.txt`, the `njia` modules **including `advisor.py`**, both classic and **`coach.html` / `coach.js` / `coach.css`** assets, and the prepared corpus. The image must exclude credentials, private data and development artifacts.

```powershell
docker build --tag njia:local .
docker run --rm --name njia-local -e PORT=8080 -p 127.0.0.1:8080:8080 njia:local
```

Open http://127.0.0.1:8080 and test the coach as above. Supply Groq and/or NVIDIA credentials through the runtime environment for JSON coaching; web research requires Groq. The container runs as UID 10001, uses one worker and honours `PORT`. Forwarded headers should be trusted only from the actual ingress proxy. No successful container-runtime or Render deployment is claimed.

References: [Vercel FastAPI](https://vercel.com/docs/frameworks/backend/fastapi), [Python runtime](https://vercel.com/docs/functions/runtimes/python), [function limits](https://vercel.com/docs/functions/limitations).
