# Verification and media scripts

Run from the repository root using the project's Python environment.

## Current submitted coach

- `coach_acceptance.py`: public coach acceptance checks, including the follow-up questions step; `--base-url` targets another origin. Real provider calls require configured server access.
- `record_coach_demo.py`: records the 90-second captioned demo (upload → follow-up questions → brief → live jobs → rewrites/WhatsApp → web interview questions → practice feedback → download). It warms the role/country web-search caches one at a time before the first caption (Groq free-tier tokens-per-minute limit) and records the warm-up in its results JSON. `--base-url` targets another origin. Imports shared recording/upload helpers below.
- `build_final_deck.py`: regenerates the eight-slide presentation and PDF from the `EVIDENCE` values at the top of the file; `--all` builds, renders and validates, and `--out DIR` writes a test build elsewhere. Requires python-pptx, PyMuPDF and Playwright.
- `build_readme_images.py`: crops real synthetic-profile captures for README illustrations; requires Pillow.
- `configure_vercel_env.py`: copies approved runtime secrets via stdin to an authenticated Vercel CLI; never commit `.env`.

The standard backend suite is `python -m unittest discover -s tests -v`.
See each script for its configured URL, network-call budget, and output paths before rerunning.

## Updated video + deck rerun (Windows, from repository root)

Latest completed run: 19 recording checks, 90.000s, 8 remote + 3 local cards, 8 web-sourced
questions, Groq coaching and feedback. The final command after analyzed warm-up failures was:
`python scripts/record_coach_demo.py --base-url https://gomycode-2026.vercel.app --warm-attempts 1 --skip-warmup --allow-web-fallback`.
`--allow-web-fallback` permits honestly labelled curated questions and missing local web cards;
remote cards and real AI coaching remain required. `--skip-warmup` avoids extra preparation calls;
it does not mock or bypass the UI API requests. Search starts at 37s in parallel with the jobs/plan
tour; results are shown at 62–71s. See `artifacts/recording-handoff.md` for attempts and exact calls.

Wait for the deployment owner to confirm the updated public release before recording.
Use the project environment, not the system `python`:

```powershell
Get-Command ffmpeg, ffprobe
.\.venv\Scripts\python.exe scripts/record_coach_demo.py --help
# After deployment confirmation:
.\.venv\Scripts\python.exe scripts/record_coach_demo.py --base-url https://gomycode-2026.vercel.app
# After reviewing the recording and updating verified EVIDENCE in the builder:
.\.venv\Scripts\python.exe scripts/build_final_deck.py --all
```

Prerequisites: Playwright + installed Chromium, pypdf, and ffmpeg/ffprobe with VP9 support
for video; python-pptx, PyMuPDF, Pillow and Playwright/Chromium for the full deck build.
The deck reads `data/africa_jobs_subset.jsonl`; screenshots, old acceptance JSON and a video
file are not required inputs. It uses the explicit `EVIDENCE` dictionary rather than
automatically importing recording results. `--render-only` needs the generated HTML;
`--validate` needs the complete generated PPTX/PDF/supporting files. Install any missing
media packages into `.venv`, e.g.:

```powershell
.\.venv\Scripts\python.exe -m pip install python-pptx==1.0.2 PyMuPDF==1.28.2 Pillow==12.3.0
.\.venv\Scripts\python.exe -m playwright install chromium
```

### Time and call budget

- Warm-up makes **two API POSTs** on success: local web jobs, then web interview questions.
  It waits **65 seconds between them and 65 seconds before recording**. Default one attempt
  per endpoint, 90-second client timeout each: **130 seconds + response time**, at most about
  **5m10s** for successful warm-up at those client bounds. Failure stops before recording.
- `--warm-attempts 2` explicitly allows one retry per endpoint. Retry waits are 65 seconds
  for jobs and 125 seconds for questions. Worst client-timeout budget: **11m20s** before
  recording. Do not automatically rerun on quota failures; waiting does not reset daily quota.
- Recording is **91 seconds raw after the first caption**, finalized to **90 seconds at 1x**,
  plus browser startup and local VP9 encoding. Reserve roughly **6–10 minutes** for one default
  attempt including encoding; provider failures may require a later attempt rather than a longer video.
- On-camera requests: upload, follow-up questions, one brief, remote jobs, local web jobs,
  interview questions, feedback (**7 POSTs**, plus metadata GET). Only the three JSON coaching
  requests need new AI completions when the two web caches hit. NVIDIA failover can add one
  provider attempt for each of those three requests. There is no browser-search NVIDIA backup.
- With cold caches, a successful default run normally makes **2 search + 3 coaching provider
  calls** (up to 8 with all JSON calls failing over). Cache misses during recording can add
  2 searches. With explicit warm retries the potential total is **4 warm searches + 2 in-video
  searches + 6 JSON provider attempts = 12**. Internal browser-search tool steps consume further
  tokens; an application request is not a token-budget guarantee.
- Searches default to `openai/gpt-oss-120b`, separate from coaching's `openai/gpt-oss-20b`.
  Code comments report **50–100K tokens/search** and **200K/day/model** on the free tier;
  two cold searches can use most of that allowance. Confirm actual remaining quota with the
  deployment owner. Caches are process-local: remote jobs 1h, web jobs 12h, interview questions
  24h, failed interview search 120s. New serverless instances can miss warmed caches.
- Public cues allow at most 1 second of drift and otherwise fail, retaining raw footage/JSON.
  Key response slots are about **7s** for PDF + follow-ups, **8s** for the brief, **6s** for
  cached interview questions and **7s** for feedback. Backend timeout ceilings (including
  NVIDIA) are longer: follow-ups 40s, brief 75s, feedback 60s; timeouts do not fit this timeline.
- The recorder does **not** use the old `coach-call-budget.json` three-advice reservation
  ledger or the classic two-call ledger. It enforces one brief per recording, not a persistent
  cross-run limit. Coordinate reruns with the owner; each rerun spends quota again.

The public run requires actual Groq/NVIDIA coaching, both remote and local job cards, and
web-sourced interview questions. `--rehearsal --base-url http://127.0.0.1:8000` skips warm-up
and permits labelled coaching fallbacks, but still uses the running app's real providers
and job APIs; it is not an offline mode. Rehearsal footage/results use separate names and
are labelled `rehearsed`. No rehearsal should replace a published video.

Review the output before publication: `artifacts/njia-coach-demo-results.json`, raw video,
`artifacts/njia-coach-demo-90s.webm`, and canonical `artifacts/njia-demo-90s.webm`. The first
successful replacement preserves `artifacts/njia-demo-90s-previous.webm`. Update verified
deck counts/provider/timings and `demo_predates_new_features` only after reviewing the new
run and replacing the published asset. The builder currently labels the carried-over
public measurements and demo as earlier-release evidence.

## Earlier classic workflow

`browser_test.py`, `race_test.py`, `deployed_test.py`, `mobile_upload_test.py`,
`upload_browser_test.py`, and `record_demo.py` were written for the earlier
four-week-plan interface, now available at `/classic`. Their historical results
are distinct from current coach validation; older scripts that navigate `/`
need that navigation changed to `/classic` before reuse. Do not count their
results as new-coach evidence. Upload/recording modules also provide helpers
imported by the current coach scripts and are retained for reproducibility.

`evaluate.py` measures keyword extraction on 20 synthetic examples, not the
generative advisor's accuracy. Recorded evidence is attached to the
[demo release](https://github.com/Eeshan-Vaghjiani/njia/releases/tag/demo-v1).
