# Verification and media scripts

Run from the repository root using the project's Python environment.

## Current submitted coach

- `coach_acceptance.py`: current public coach acceptance checks; real provider calls require configured server access.
- `record_coach_demo.py`: records the current 90-second captioned demo. Imports shared recording/upload helpers below.
- `build_final_deck.py`: regenerates the eight-slide presentation and PDF; requires local presentation dependencies.
- `build_readme_images.py`: crops real synthetic-profile captures for README illustrations; requires Pillow.
- `configure_vercel_env.py`: copies approved runtime secrets via stdin to an authenticated Vercel CLI; never commit `.env`.

The standard backend suite is `python -m unittest discover -s tests -v`.
See each script for its configured URL, network-call budget, and output paths before rerunning.

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
