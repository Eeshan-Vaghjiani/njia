# Deploy Njia

## Live deployment: Vercel

**Live app: https://gomycode-2026.vercel.app**

- **Project:** `eeshans-projects-0934fb87/gomycode-2026`.
- **2026-09-27, reported by main workflow:** anonymous
  `https://gomycode-2026.vercel.app/api/health` returned **HTTP 200**,
  **18,371 postings**, and configured Groq model **`openai/gpt-oss-20b`**.
- **CLI source deployment succeeded.** The automatic GitHub connection failed;
  automatic deployment is not configured. Publish source updates using the CLI.
- **Public browser verification PASS: 38/38 checks**, fresh anonymous Chromium
  contexts, **2026-09-27T10:25:42.307Z–2026-09-27T10:26:00.536Z**.
  `artifacts/deployed-results.json` records production PDF upload, preview editing,
  consent-gated extraction, Kenya gap (**391 / 39.6%**), curated planning with AI
  unchecked, one real Groq plan (**`mode=groq`, `openai/gpt-oss-20b`, four weeks,
  1.831 s**), SQL **3/3** and report download. Fresh touch-mobile **390×844** TXT
  upload through gap analysis passed without horizontal overflow. Zero JavaScript
  errors, console errors, failed requests or HTTP 403s were observed. See
  [LOCAL_TEST_RESULTS.md](LOCAL_TEST_RESULTS.md) for limits and prior local evidence.

### Active Services configuration and resolved build issues

Initial deployment encountered ambiguous service discovery. `vercel.json` now
declares the service explicitly and sends all paths to it:

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
    {
      "source": "/(.*)",
      "destination": { "type": "service", "service": "njia" }
    }
  ]
}
```

Vercel uses **`pyproject.toml`**, not `requirements.txt`, for this deployment's
dependencies. Explicit pinned direct dependencies were required; the project
declares Python `>=3.12,<3.14` and pins FastAPI `0.115.11`, Uvicorn `0.34.0`,
HTTPX `0.28.1`, scikit-learn `1.6.1`, python-dotenv `1.1.1`, python-multipart
`0.0.32`, and pypdf `6.19.0`. `[tool.vercel]` also identifies `njia.app:app`.
Keep these dependencies current when changing runtime requirements.

The initial `.vercelignore` allowlist dropped runtime files. It was replaced
with explicit exclusions for secrets (`.env`, `.env.*`), `private`, `.venv`,
Git/agent metadata, caches, development files, artifacts/decks and unused data.
The application modules, static assets, public corpus and `pyproject.toml`
remain available to the build. Keep secret values in Vercel's server environment.
**`api/index.py` is a legacy adapter and is not used by Services.**

### Configured server environment

| Variable | Configuration |
| --- | --- |
| `GROQ_API_KEY` | Sensitive server-held value configured in Vercel; never copy its value into docs or browser code |
| `NJIA_AI_PROVIDER` | `groq` |
| `GROQ_MODEL` | `openai/gpt-oss-20b` |
| `NJIA_PUBLIC_ORIGINS` | `https://gomycode-2026.vercel.app` |
| `OPENBLAS_NUM_THREADS` | `1` |

Remote coaching still requires explicit `use_ai`/`ai_consent`. Curated plans
remain available without AI consent; the returned plan identifies the mode
that actually ran.

### Publish a source update

From the linked repository root, check the account/project and deploy:

```powershell
vercel whoami
vercel deploy --prod
```

Confirm the target is `eeshans-projects-0934fb87/gomycode-2026`, inspect the build
result, then verify the production health URL and browser flows below. A GitHub
push alone does not deploy this project while the GitHub connection is absent.

## Alternative packaging: Render Free, Docker

Use the repository-root `render.yaml` to create one **Free Docker web service**.
It serves the frontend and API at one HTTPS origin, supports the backend's 5 MiB
upload limit (the frontend still caps files at 4,000,000 bytes), and avoids a
serverless bundle-size dependency. No database,
disk, model server, paid service, or API key is required. AI coaching defaults to
the deterministic `offline` provider.

This is a hackathon/demo deployment. Render Free provides 512 MB RAM and 0.1 CPU;
it sleeps after 15 idle minutes and takes approximately a minute to wake. The
workspace shares 750 free instance hours each month. Check memory after loading
the corpus, running several country/role analyses, and previewing a PDF: the
Docker limit test below has not yet run. Disk package size is not runtime RAM.
One Uvicorn worker and one BLAS/OpenMP thread reduce memory and CPU contention.

### Earlier alternative-packaging verification status

- **Render:** no authenticated Render session/token was available at the packaging
  checkpoint. To use this alternative, sign in and connect the now-public
  `Eeshan-Vaghjiani/njia` repository. No Render deployment is claimed.
- **Local Docker:** Docker 28.4.0 is installed, but `docker info` cannot connect
  to the `dockerDesktopLinuxEngine` named pipe. Start Docker Desktop's Linux
  engine to build/run the image and verify the 512 MB memory budget. Render can
  build remotely without local Docker.
- **Vercel:** installed CLI 56.3.1 meets the documented minimum 48.1.8. The earlier
  authentication blocker is resolved; CLI source deployment and anonymous health
  succeeded as recorded above. An actual deployed-bundle size is not recorded here.
- GitHub authentication was reported valid for **Eeshan-Vaghjiani**; it does not
  authenticate Render or Vercel.
- Earlier packaging checks passed: configuration instance validation against the
  hosted Render/Vercel schemas, Docker COPY source existence, then-current Vercel
  ignore allowlist cases, adapter import, health (18,371 postings), root/static responses,
  same-origin HTTPS POST, cross-origin rejection, and a simulated trusted HTTPS
  proxy. These are local Python checks, not a container or deployed-service test;
  the old Vercel adapter/allowlist checks do not validate the current Services config.

### Publish with Render

1. Sign in at
   <https://dashboard.render.com/> and select **New > Blueprint**. Connect Njia
   and use the root `render.yaml`. The repository/branch are inferred from the
   Blueprint rather than hardcoded.
2. Confirm the proposed service is **Free**, runtime **Docker**, region
   **Frankfurt**, and health path `/api/health`. Keep `NJIA_AI_PROVIDER=offline`.
   The Blueprint explicitly sets `plan: free` because omitting a plan can select
   paid compute. Auto-deploys are off; use manual deploys for later updates.
3. For the no-paid-plan path, use a workspace without a payment method and avoid
   paid add-ons/trials. Render documents suspension at bandwidth exhaustion and
   disabled builds at build-minute exhaustion when no payment method is present.
   A workspace with a payment method can incur usage charges even for Free
   compute. If signup demands a paid plan/payment arrangement, stop and resolve
   that with the owner instead of accepting it automatically.
4. Apply the Blueprint and wait for `/api/health` to report `status: ok`. The
   build installs requirements, copies the explicit runtime allowlist, and runs
   as non-root UID 10001. Render supplies `PORT`; the command binds `0.0.0.0` and
   expands `${PORT:-10000}` at runtime.
5. Open the assigned `https://...onrender.com` URL and complete the smoke checks
   below. Warm the service shortly before a demo to allow for idle startup.

### Local Docker verification (once the daemon is running)

Run from the repository root:

```powershell
docker build --tag njia:local .
docker run --rm --name njia-local --memory=512m --cpus=0.1 -e PORT=8080 -p 127.0.0.1:8080:8080 njira:local
```

In another terminal, visit <http://127.0.0.1:8080>, check
<http://127.0.0.1:8080/api/health>, exercise analysis and uploads, and run
`docker stats --no-stream njia-local`. This deliberately tests a nondefault PORT
and the Free compute budget. If the process is killed or approaches the memory
limit under expected usage, free-tier suitability remains unresolved; do not
silently switch to paid compute. Stop with `docker stop njira-local`.

## HTTPS origin and proxy headers

`njia/app.py` compares POST `Origin` with `request.base_url`. If TLS terminates
at a proxy but ASGI sees `http://`, ordinary browser POST requests can receive
403 even though GET `/api/health` succeeds. The frontend and API must stay on
the same public origin; this app does not enable cross-origin APIs.

The Docker command enables Uvicorn proxy headers. Render's Blueprint sets
`FORWARDED_ALLOW_IPS=*` so its ingress's `X-Forwarded-Proto: https` is honored.
This setting is appropriate only behind a trusted proxy that controls forwarded
headers and preserves the public Host. For a directly exposed container, retain
the Docker default (loopback only), or explicitly specify the actual proxy IPs.
Do not fix an origin failure by disabling the application's origin check.

Vercel Services runs `njia.app:app`, not the Docker command, so Uvicorn flags in
the Dockerfile do not configure Vercel. The deployed server explicitly sets
`NJIA_PUBLIC_ORIGINS=https://gomycode-2026.vercel.app`. Production same-origin
HTTPS POST flows passed with zero HTTP 403s in the recorded run. Rejection of
unrelated origins was not tested in that production run; local rejection checks
remain separate evidence.

## Vercel limits and earlier size assessment

### Current requirements and limits (researched 2026-09-27)

- FastAPI becomes one Python function. The **standard Python uncompressed
  bundle limit is now 500 MB**, not the generic 250 MB function limit.
- Large Functions beta supports up to 5 GB with Fluid compute and Active CPU.
  New eligible projects may use this automatically for oversized functions.
  The earlier assessment proposed `VERCEL_SUPPORT_LARGE_FUNCTIONS=0` to test
  standard-size deployment; that variable is not in the confirmed live settings above.
- Supported Python versions are 3.12 (current default), 3.13, and 3.14. The
  earlier packaging assessment targeted 3.12. The current project declares
  `>=3.12,<3.14`; verify the actual interpreter in build output. Vercel reads the
  explicit pinned dependencies in `pyproject.toml` for the current deployment.
- Hobby supports 2 GB memory and up to 300 seconds with Fluid compute; the
  current Services configuration does not specify a duration override.
  Hobby is free for personal, non-commercial use
  within quotas; do not select a Pro trial or paid team. Quota exhaustion can
  pause the service. Commercial use needs a different hosting/plan decision.
- **Request and response payloads are limited to 4.5 MB.** The backend accepts
  files up to `5 * 1024 * 1024` bytes (**5 MiB**) plus multipart overhead, but
  the frontend now caps files at **4,000,000 bytes (4 MB)** for multipart
  headroom. Larger direct requests can fail at Vercel with 413 before reaching
  the app. Production synthetic desktop PDF and mobile TXT uploads passed;
  near-limit uploads and production DOCX remain unverified.

### Size assessment

A binary-wheel-only download of the existing requirements for CPython 3.12,
Linux x86_64, manylinux2014/manylinux_2_17 resolved successfully. Summing the
**uncompressed ZIP entries**, including the wheels' shared libraries, produced:

| Input | Uncompressed size |
| --- | ---: |
| NumPy 2.2.6 | 55.11 MiB |
| SciPy 1.16.3 | 112.91 MiB |
| scikit-learn 1.6.1 | 39.55 MiB |
| All 24 resolved dependency wheels combined | **220.51 MiB** |
| Public corpus, 18,371 rows | **3.34 MiB** |

Thus dependencies plus corpus are approximately **223.85 MiB** before app/static
files, generated bytecode, installed-package changes, and Vercel runtime layers.
This has headroom against 500 MB, but little against the old 250 MB limit.
The wheel check used a restricted compatibility target; Vercel's newer Linux
target and unpinned transitive dependencies may resolve different versions.
It is an estimate, not a deployed-bundle measurement or an import test of Linux
native extensions. Never use the Windows `.venv` size as the Linux bundle result.
CLI source deployment has since succeeded; these figures remain the earlier
wheel estimate, not a measurement of the deployed Services bundle.

## Live smoke checks for either host

**Vercel PASS:** homepage, static JS/CSS, sample TXT download, health and metadata;
desktop PDF/edited preview/consent/extraction/analysis; four curated weeks with
`use_ai=false` and `ai_consent=false`; one opted-in Groq response; SQL grading and
report download; fresh mobile TXT/preview/extraction/analysis. All observed HTTP
responses succeeded. The 1.831-second Groq result is one observation, not a benchmark.

**Still unverified in production:** DOCX, near-limit uploads, unrelated-Origin
rejection, provider-failure fallback, mobile plan/download and physical phones;
post-flow health and runtime memory were not measured by this run. Prior local
tests cover some of these paths separately. No Render smoke run is claimed.

The main workflow is publishing `deployed-results.json` and production screenshots
to the existing [demo-v1 release](https://github.com/Eeshan-Vaghjiani/njia/releases/tag/demo-v1).
Only attached assets are publicly downloadable; `artifacts/` paths are local.

## Packaging boundary

Docker copies only `requirements.txt`, six named `njia/*.py` modules, three
named static files, and `data/africa_jobs_subset.jsonl`. Its deny-by-default
context also excludes `.env`, `.venv`, VCS metadata, private datasets, user CVs,
pitch decks, screenshots and other artifacts. Update both the explicit copy
list and ignore rules if legitimate runtime assets are added later. Environment
secrets, if ever needed, belong in host settings rather than the image.

## Official references

- [Vercel FastAPI](https://vercel.com/docs/frameworks/backend/fastapi)
- [Vercel Python runtime](https://vercel.com/docs/functions/runtimes/python)
- [Vercel file-based Python functions](https://vercel.com/docs/functions/runtimes/python/api-directory)
- [Vercel function limits](https://vercel.com/docs/functions/limitations)
- [Vercel configuration](https://vercel.com/docs/project-configuration/vercel-json)
- [Vercel Hobby](https://vercel.com/docs/plans/hobby)
- [Render Free limits and billing behavior](https://render.com/docs/free)
- [Render Blueprint specification](https://render.com/docs/blueprint-spec)
