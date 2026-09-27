# Njia: 90-second voiceover

## Is voiceover required?

**Neither current official source explicitly requires voiceover, audio, or spoken narration.** They require a **90-second demo video**, showing the prototype working, with a link the jury can open. The guide asks for the problem, product, proof and next step. Its example timing (0–15 / 15–65 / 65–80 / 80–90 seconds) is explicitly “a suggested structure, not an extra scoring rule.” Adding narration is an editorial recommendation for clarity, not a stated submission requirement; silence is not explicitly approved or prohibited.

Sources checked read-only on **27 September 2026**:
- [Official onboarding: submission checklist and suggested structure](https://hackathon.gomycode.com/onboarding#submit); [FAQ: video duration and access](https://hackathon.gomycode.com/onboarding#help).
- [Linked official submission form](https://docs.google.com/forms/d/e/1FAIpQLSebmyKeBPv2mrmy4T_wI2_z9SBjjSTZ-O-_ewiWs6PBEikRjw/viewform): required “90-second demo video URL” and final confirmation; no audio instruction.

## Recording evidence

[Recorder](../scripts/record_coach_demo.py) and [published results](https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/njia-coach-demo-results.json) establish the cues below. The final [video](https://github.com/Eeshan-Vaghjiani/njia/releases/download/demo-v1/njia-demo-90s.webm) is **90.000 seconds**, 1×, 25 fps, 2,250 frames, with visible captions and **no audio stream**. Logged cue execution is within 0.019 seconds of the scheduled times; finalization trims startup footage at the caption sync marker. This recording uses a synthetic CV, zero mocked responses, and one real `openai/gpt-oss-20b` request through Groq, taking 2.26 seconds including PDF processing. Its market result uses 391 historical Kenyan postings and 39.6% demand-weighted coverage.

## Narration — 177 words

Read only the quoted paragraphs. Start each at its cue, pause when finished, and rehearse against the video; the word count alone does not guarantee the spoken duration. “GPT OSS twenty B” is the spoken model name. The closing next step is a proposal, not a completed test.

### 00:00–00:06 · Introduction
> We're team Dhruzzz, joining online from Kenya. Njia helps jobseekers choose their next step.

### 00:06–00:12 · Problem and PDF
> Unsure what to improve? Start with a fictional candidate's PDF CV.

### 00:12–00:18 · Consent
> Review consent for server processing and sharing CV text with the AI provider.

### 00:18–00:25 · Real AI request
> Build my career brief makes a real AI request using that CV.

### 00:25–00:31 · Returned result
> Groq runs GPT OSS twenty B. We didn't use Brev.

### 00:31–00:37 · Strengths and evidence
> Open each strength to see supporting CV evidence. These suggestions need your review.

### 00:37–00:43 · Historical market evidence
> Market evidence uses historical Kenyan postings from 2023, not predictions of hiring success.

### 00:43–00:49 · Priorities
> Three priorities turn skill demand into practical first steps, rather than live vacancies.

### 00:49–00:56 · Draft rewrite
> Compare the original bullet with an AI draft. Verify every claim before using it.

### 00:56–01:02 · Seven day plan
> The seven day plan gives you small actions and concrete work to keep.

### 01:02–01:08 · Progress
> Track your progress as you practise and build evidence throughout the week.

### 01:08–01:15 · Interview practice
> Practise a tailored interview question, with guidance for explaining your real experience.

### 01:15–01:21 · Skill review
> Review your skills, then confirm them to recalculate the historical market evidence.

### 01:21–01:27 · Export
> Export your HTML brief. CV quotes and rewrites require opting in.

### 01:27–01:30 · Next step
> Next: test with jobseekers.

## Practical recording and mix

Record your microphone while watching the video muted, using headphones to avoid feedback. Place the voice track at 00:00 and align each section to its cue. The source has no audio to mute; in an editor, keep any added desktop audio or music muted so speech stays clear. Retain the visible captions, use a comfortable voice level without clipping, and export a separate narrated copy at exactly 90 seconds and 1× speed. Check the rendered duration, cue alignment and audible ending, then test the hosted link signed out.

Word count: **177**, whitespace-delimited words in the quoted narration only; headings and recording notes excluded.
