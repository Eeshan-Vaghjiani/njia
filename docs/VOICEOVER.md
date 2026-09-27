# Njia: 90-second voiceover

## Is voiceover required?

Neither recorded official source explicitly requires audio or spoken narration. They require a **90-second demo video** accessible to the jury; the problem/product/proof/next-step timing is a suggested structure. Narration is an editorial aid, not a stated submission requirement.

Sources checked on **27 September 2026**: [official onboarding](https://hackathon.gomycode.com/onboarding#submit), [FAQ](https://hackathon.gomycode.com/onboarding#help), and [submission form](https://docs.google.com/forms/d/e/1FAIpQLSebmyKeBPv2mrmy4T_wI2_z9SBjjSTZ-O-_ewiWs6PBEikRjw/viewform).

## Latest recording evidence and cue source

The cues below follow the inspected [recorder timeline](../scripts/record_coach_demo.py), its live [coach HTML](../static/coach.html), and [successful results JSON](https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/njia-coach-demo-results.json), including its `caption_corrections` disclosure. Final delivery is the corrected [MP4 video](https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/njia-demo-90s.mp4): **H.264, faststart, 6,303,031 bytes**, 90.000 seconds, 1280×720, **1×, 25 fps, 2,250 frames**, with **real user-provided human narration, AAC 48 kHz stereo audio and visible captions**. At the user's request, the existing release asset was replaced at this same URL. The historical WebM remains silent and is retained only as an optional source. The latest eight-page PDF/PPTX, recording JSON, NVIDIA JSON and voiceover are also published.

**19 checks passed**, zero late cues, zero JavaScript errors, zero mocked responses. Real Groq `openai/gpt-oss-20b` returned **four follow-ups in 1.271 s including PDF upload**, the **brief in 1.450 s**, and **feedback in 0.844 s**, scoring **4/5**. The screen shows **8 remote + 3 local job cards**, and **8 web interview questions from 3 source URLs**, researched with Groq `openai/gpt-oss-120b`. This is separate from the older **57 public assertions (48 + 9)** and main-reported **126 offline backend tests**.

The recording does **not** show NVIDIA fallback. A separate [actual local test](https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/nvidia-fallback-results.json), with Groq forced unavailable, returned five validated NVIDIA 20b questions in **11.564 s** and a validated seven-day brief in **16.637 s**. NVIDIA is configured in production, but local success is not production-failover proof. **Brev was not used.**

Initial cache warming failed on interview research; three recording attempts then failed on search timing/local-card availability before the successful final take. The session used **27 application POSTs**, including warming; the final take skipped new warming and its **0.390 s interview response was cached**. Endpoint counts are not upstream provider-call counts. One separately observed search used **93,301 tokens**; exact full-session cost is unavailable. See [session disclosure](AI_DISCLOSURE.md#data-and-evaluation).

**Factual-review caveat:** the latest rewrite added unsupported “support inventory decisions” despite a personal synthetic-data project answer. The published video now explicitly calls for factual review. Its two overclaiming captions were replaced in postproduction, only within the narration rectangle (`x=20, y=600, width=1240, height=100`):

- **53.240–57.280 s** (end exclusive): “Draft rewrites need factual review. Verify every claim against your CV and answers; AI can add unsupported details.”
- **76.360–83.440 s** (end exclusive): “AI feedback suggests structure. Verify every fact; it can add unsupported details.”

The old captions are no longer present. Offline PNG overlays and a lossless VP9 re-encode preserved app/model output pixels outside that rectangle in **every frame**, with identical decoded frame hashes outside correction windows, as recorded in JSON `caption_corrections`; those checks apply to the corrected WebM source before H.264 MP4 conversion. No app/model output content was fabricated or edited and no new API calls or recording run were made. The subsequent human-narration mix copied the MP4 video stream unchanged, hash-verified, retaining **90.000 seconds and 1×**. Original recording check counts are unchanged. The script below uses the planned cues; the supplied recording's wording and semantic alignment have not been verified by listening in the development workflow.

## Narration — 170 words

This is the prepared 170-word script and intended cue guide, not a verified transcript of the supplied human recording. Its original reading guidance was to start each quoted paragraph at its cue and pause when finished; word count alone does not guarantee duration. “Groq” is the provider; the model name can be read as “GPT OSS twenty B.”

### 00:00–00:05 · Introduction
> We're Dhruzzz from Kenya, joining online. Njia helps jobseekers choose their next move.

### 00:05–00:10 · Fictional PDF
> Start with a fictional PDF showing Excel, SQL and dashboard experience.

### 00:10–00:14 · Consent
> Consent covers server processing and sharing redacted CV text with AI.

### 00:14–00:21 · Follow-up request
> Njia asks about skills the CV doesn't clearly show.

### 00:21–00:29 · Answer follow-ups
> Four questions arrive through Groq. Answer truthfully: this dashboard was a personal project.

### 00:29–00:37 · Build the brief
> Those answers shape the brief. Market statistics are calculated separately. The model doesn't write those numbers.

### 00:37–00:43 · Result
> Review the returned brief, evidence strengths and suggested skills.

### 00:43–00:49 · Live jobs
> Explore eight remote and three local listings. Check each source.

### 00:49–00:53 · Match
> Match measures skill overlap, not hiring probability.

### 00:53–00:57 · Draft rewrite
> Rewrites are drafts. Check every claim before using them.

### 00:57–01:02 · Weekly actions
> Follow seven daily actions, track progress, or share through WhatsApp.

### 01:02–01:11 · Interview research
> Interview research started earlier. Cached results help here; fresh searches take longer. Web searches never receive CV text.

### 01:11–01:16 · Sources
> Eight questions link to three sources. Read their context.

### 01:16–01:23 · Practice feedback
> Practise with separate consent. Groq returns STAR feedback and four out of five.

### 01:23–01:27 · Download
> Download excludes quotes and rewrites by default.

### 01:27–01:30 · Next step
> Next: test with Kenyan jobseekers.

## Recording and mix

The user explicitly supplied human audio and requested that the same submitted video URL be updated. The main workflow completed the mix with [scripts/add_voiceover.py](../scripts/add_voiceover.py) and replaced the existing `njia-demo-90s.mp4` release asset using `--clobber`.

- Narration duration: **85.421083 seconds**, starting at **0**, normal speed, with original pauses retained and silence padding to **90.000 seconds**.
- Audio processing: **70 Hz high-pass**, **loudnorm** loudness normalization, **AAC 192 kb/s, 48 kHz stereo**. This is a real human voice, not synthetic narration.
- Video: **H.264, 1280×720, 25 fps**, copied unchanged from the corrected MP4; video-stream hash preservation verified.
- Published MP4: **6,303,031 bytes**; SHA-256: `00929c0452f1d06ec17b109e23902d8805111c4a2df00a2a1a03f0eb06e6a2d9`.
- Public evidence: [narration-results.json](https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/narration-results.json). Main-workflow verification covers technical playback only; it does not establish a listening review, semantic cue alignment or an audible-ending review.

The user reports this video URL was submitted; form receipt not verified by the development workflow.

Word count covers whitespace-delimited words in the quoted narration only, excluding headings and notes.
