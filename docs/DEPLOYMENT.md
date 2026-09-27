# Deploy Njia

## Recommended path: Render Free, Docker

Use the repository-root `render.yaml` to create one **Free Docker web service**.
It serves the frontend and API at one HTTPS origin, keeps the current 5 MiB CV
upload capability, and avoids a serverless bundle-size dependency. No database,
disk, model server, paid service, or API key is required. AI coaching defaults to
the deterministic `offline` provider.

This is a hackathon/demo deployment. Render Free provides 512 MB RAM and 0.1 CPU;
it sleeps after 15 idle minutes and takes approximately a minute to wake. The
workspace shares 750 free instance hours each month. Check memory after loading
the corpus, running several country/role analyses, and previewing a PDF: the
Docker limit test below has not yet run. Disk package size is not runtime RAM.
One Uvicorn worker and one BLAS/OpenMP thread reduce memory and CPU contention.

### Current blockers and verification status

- **Render:** no authenticated Render session/token is available. The owner must
  sign in and connect the public `Eeshan-Vaghjiani/Njia` repository after the main
  workflow publishes it. This packaging task did not create or publish a repo.
- **Local Docker:** Docker 28.4.0 is installed, but `docker info` cannot connect
  to the `dockerDesktopLinuxEngine` named pipe. Start Docker Desktop's Linux
  engine to build/run the image and verify the 512 MB memory budget. Render can
  build remotely without local Docker.
- **Vercel:** installed CLI 56.3.1 meets the documented minimum 48.1.8; the
  previously checked authentication is invalid. The owner must run `vercel login`.
  No authenticated platform build, bundle-size result, or live HTTPS test exists.
- GitHub authentication was reported valid for **Eeshan-Vaghjiani**; it does not
  authenticate Render or Vercel.
- Packaging checks passed: configuration instance validation against the hosted
  Render/Vercel schemas, Docker COPY source existence, Vercel ignore allowlist
  cases, adapter import, health (18,371 postings), root/static responses,
  same-origin HTTPS POST, cross-origin rejection, and a simulated trusted HTTPS
  proxy. These are local Python checks, not a container or deployed-service test.

### Publish with Render

1. After the main workflow publishes the repository, sign in at
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

Vercel runs the ASGI adapter itself, not the Docker command, so Uvicorn flags in
the Dockerfile do not configure Vercel. Verify that the live runtime supplies
the HTTPS scheme and original public Host. If same-origin POST still gets 403,
the application owner must address trusted proxy/origin handling before release.

## Vercel: viable candidate, subject to build and upload checks

### Current requirements and limits (researched 2026-09-27)

- FastAPI becomes one Python function. The **standard Python uncompressed
  bundle limit is now 500 MB**, not the generic 250 MB function limit.
- Large Functions beta supports up to 5 GB with Fluid compute and Active CPU.
  New eligible projects may use this automatically for oversized functions.
  This setup does not rely on that beta: set project environment variable
  `VERCEL_SUPPORT_LARGE_FUNCTIONS=0` to test the standard-size deployment.
- Supported Python versions are 3.12 (current default), 3.13, and 3.14. This
  packaging assessment targets 3.12; confirm it in the build output. Dependencies
  are read from the existing `requirements.txt`.
- Hobby supports 2 GB memory and up to 300 seconds with Fluid compute; this
  function requests 60 seconds. Hobby is free for personal, non-commercial use
  within quotas; do not select a Pro trial or paid team. Quota exhaustion can
  pause the service. Commercial use needs a different hosting/plan decision.
- **Request and response payloads are limited to 4.5 MB.** Njia currently accepts
  files up to `5 * 1024 * 1024` bytes plus multipart overhead. Those requests can
  fail at Vercel with 413 before reaching the app. Before selecting Vercel, the
  frontend owner should reduce the advertised and enforced file limit to
  **4,000,000 bytes (4 MB)**, leaving multipart headroom; align backend validation
  as appropriate. This packaging task did not change those limits. Render is
  preferred if retaining the existing upload promise is required.

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
Inspect the actual build output before declaring Vercel supported.

### Why the Vercel adapter and configuration exist

Zero-config FastAPI discovery supports root `app.py`/`index.py`/`main.py` and
similar files under `src/` or `app/`; the existing `njia.app:app` is outside those
locations. The native custom-module setting is in `pyproject.toml`, which is
outside this task's allowed files.

`api/index.py` therefore exports the existing ASGI app using Vercel's documented
file-based Python function support. `vercel.json` sets `framework: null` (Other)
to prevent a FastAPI preset overriding this route, rewrites requests to that
function, explicitly includes runtime files, and sets duration. This avoids
legacy `builds` configuration. `.vercelignore` uploads only the adapter,
requirements, application modules, three static files, and the public corpus.
No model/CV/private data or development environment belongs in this upload.

### Owner's Vercel steps

1. Run `vercel login`, then `vercel whoami`. Select the owner's **Hobby** scope.
2. Import/link the repository root with Framework **Other**. Leave build/install
   overrides unset. Set `NJIA_AI_PROVIDER=offline` and
   `VERCEL_SUPPORT_LARGE_FUNCTIONS=0`. Keep Fluid compute enabled.
3. Build/preview only after authentication and scope selection. For a CLI
   preflight, `vercel pull --environment=preview` followed by `vercel build`
   retrieves settings and builds locally without publishing. Prefer a Linux
   build environment for native NumPy/SciPy compatibility. Inspect generated
   `.vercel/output/functions` and the builder's bundle report; compressed source
   upload size is not the relevant limit.
4. If the standard bundle fits, the upload limit has been resolved, and the
   runtime checks pass, the main deployment workflow can publish with
   `vercel deploy` for a preview, then `vercel deploy --prod` for production.
   Stop on a size failure or paid-plan prompt rather than automatically upgrading.
5. Verify the production URL is publicly accessible in a signed-out browser;
   preview authentication can otherwise prevent judges from opening it.

## Live smoke checks for either host

- `/` loads, and `/static/app.js` and `/static/styles.css` return successfully.
- `/api/health` reports `ok`, **18,371** postings and the offline provider.
- `/api/meta` supplies country, role, and skill choices.
- Use the browser UI to extract skills, analyze a country/role, and create an
  offline plan. This verifies HTTPS POST origin handling, unlike a bare health
  request. Check that an unrelated Origin is rejected.
- Preview a synthetic TXT/PDF/DOCX with consent; use non-sensitive sample text.
  Check near-limit uploads against the selected host's actual request limit.
- Confirm health still succeeds after exercising analysis and upload parsing,
  and inspect memory/latency. Caches are per-process and are rebuilt on restart.

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
