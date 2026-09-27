# Deploy Njia

**Production:** https://gomycode-2026.vercel.app
**Health:** https://gomycode-2026.vercel.app/api/health

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
| `NJIA_AI_PROVIDER` | `groq` for optional classic plan rewriting |
| `NJIA_PUBLIC_ORIGINS` | `https://gomycode-2026.vercel.app` |
| `OPENBLAS_NUM_THREADS` | `1` |

The root advisor requires `consent=true` before sending best-effort-contact-scrubbed CV text to Groq. Missing credentials, provider failures or invalid responses produce a labelled curated brief. `NJIA_AI_PROVIDER=offline` affects classic plans only, not the advisor’s independent Groq path.

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

The published production evidence records **48 acceptance + 9 recording assertions = 57**, including real Groq `openai/gpt-oss-20b` output. **73 backend tests** are separate evidence. These results do not establish all provider-failure, near-limit-upload or physical-phone behaviour in production.

Keep frontend and API on the same origin. `NJIA_PUBLIC_ORIGINS` handles the public HTTPS origin; do not disable origin checks to fix proxy mismatches. Vercel Services does not use the Dockerfile’s Uvicorn flags. Browser uploads are limited to **4,000,000 bytes** for headroom below Vercel’s **4.5 MB request limit**; the backend’s **5 MiB** parser limit does not override the host limit.

## Docker packaging

Docker is optional packaging, not the active production deployment. Keep the Dockerfile COPY allowlist and `.dockerignore` aligned with the runtime: `requirements.txt`, the `njia` modules **including `advisor.py`**, both classic and **`coach.html` / `coach.js` / `coach.css`** assets, and the prepared corpus. The image must exclude credentials, private data and development artifacts.

```powershell
docker build --tag njia:local .
docker run --rm --name njia-local -e PORT=8080 -p 127.0.0.1:8080:8080 njia:local
```

Open http://127.0.0.1:8080 and test the coach as above. Supply a Groq key through the runtime environment if AI inference is needed. The container runs as UID 10001, uses one worker and honours `PORT`. Forwarded headers should be trusted only from the actual ingress proxy. No successful container-runtime or Render deployment is claimed.

References: [Vercel FastAPI](https://vercel.com/docs/frameworks/backend/fastapi), [Python runtime](https://vercel.com/docs/functions/runtimes/python), [function limits](https://vercel.com/docs/functions/limitations).
