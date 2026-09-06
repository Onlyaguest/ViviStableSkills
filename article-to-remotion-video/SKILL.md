---
name: article-to-remotion-video
description: "Turn one article, document, or long-form source into a locally runnable Remotion short video with source-grounded storytelling, reusable visuals, optional Cohub TTS narration, and STT/technical QA. Use when the user asks for 一篇文章出视频、文章转短视频、Remotion 成片、带配音的视频样片, or wants to repeat this workflow on new articles. Do not trigger for ordinary video playback, transcription-only requests, or interactive-web-only work."
metadata:
  version: 1.0.0
  author: Vivi
  tags: [video, remotion, article, tts, stt]
  platforms: [macos, linux]
  dependencies: [python3, nodejs, ffmpeg]
---

# Article to Remotion Video

Produce a real local project and a verifiable MP4. Treat Remotion as the video engine, TTS as an optional narration source, and STT as QA—not as the creative engine.

## Outcome

Unless the user specifies otherwise, deliver:

- a new isolated project directory;
- `story.json`, preserving source facts, tone, and provenance;
- a runnable Remotion project using the bundled template or an adapted version;
- a 16:9, 45–60 second H.264 MP4;
- 4–6 representative still frames;
- optional Cohub TTS narration plus its script and manifest;
- build, media, visual, and narration verification notes;
- exact preview/render commands and output paths.

Do not publish publicly unless the user explicitly asks.

## Workflow

### 1. Read the source faithfully

Use the source-native reader before summarizing:

- Feishu/Lark Doc or Wiki URL: load and follow `lark-doc`; fetch relevant sections and media tokens.
- PDF: load and follow the available PDF skill (`pdf:pdf`) when layout or page evidence matters.
- Word document: load and follow the available document skill (`documents:documents`).
- Public web article: browse the exact page and cite or record the source URL.
- Local Markdown/text: read the file directly.

Create a short source note containing the article title, source location, exact facts/numbers/quotes used, image provenance, and important limitations. Do not invent connective events, successful states, or product capabilities.

### 2. Decide the story before coding

Choose 4–6 beats that form a causal arc, not a table of contents. Prefer:

`problem or hook → action/workflow → evidence or numbers → result → honest boundary`

Keep the author's register. Shorten wording for the screen, but do not turn tentative claims into completed facts.

Read [references/story-schema.md](references/story-schema.md), then create `story.json`. The JSON is the reusable “one file” that drives the template. Default total duration is 45–60 seconds.

### 3. Scaffold an isolated Remotion project

Run:

```bash
python3 scripts/scaffold_project.py <new-output-directory>
```

The command must refuse to overwrite a non-empty target. Copy source images into `public/assets/`, edit only `story.json`, then validate it:

```bash
python3 scripts/validate_story.py <project>/story.json
```

Adapt the React scene implementation only when the article genuinely needs a new visual grammar. Preserve the template's data-driven boundary instead of hard-coding article facts into components.

### 4. Build visuals around meaning

Use code-generated motion for structure: timelines, counters, state changes, paths, comparisons, or accumulation. Reuse source images when they carry evidence. Use a clearly labeled code illustration only when source media is unavailable.

Avoid unrelated particles, decorative motion, and generic stock imagery. A transition should explain a change in state or move the story forward.

### 5. Add narration when requested or already part of the user's established workflow

Read [references/tts-stt.md](references/tts-stt.md) before any Cohub generation.

- Use Cohub TTS, not STT, to create narration.
- Split narration by scene; keep each Qwen voice-design request under 200 Unicode characters.
- Use the same voice description for every segment.
- Do not claim to clone the author unless the user supplied and authorized reference audio.
- Paid/remote generation requires explicit user intent for narration or a confirmation immediately before the call.
- Preserve the narration text and the returned cost/request IDs in a manifest.

Use the bundled helper after `story.json` contains `narration` and predictable `audio` paths:

```bash
python3 scripts/cohub_tts.py <project>/story.json --space-id <cohub-space-id>
```

### 6. Render and verify the actual deliverable

Run, at minimum:

```bash
cd <project>
npm install
npm run typecheck
npm run build
npm run stills
npm run render
```

Then verify the MP4 with `ffprobe`. Check codec, resolution, frame rate, duration, and—when narration is expected—the presence and level of an audio stream.

Visually inspect representative stills from the hook, middle evidence scenes, result, and ending. Check text overflow, image cropping, contrast, and factual numbers.

When narration exists, use the available local STT skill/tool to transcribe the final MP4. Compare the transcript against the narration scripts and confirm that the last scene is present. A successful TTS request is not proof of a complete audio file.

Read [references/qa.md](references/qa.md) for the acceptance checklist and failure handling.

## Optional GSAP companion

GSAP is not the default video engine. Offer or build a GSAP companion only when the user asks for an interactive article, scrolling story, or side-by-side technical comparison. Reuse the same `story.json`, source images, color tokens, and factual boundaries. Do not make the Remotion MP4 depend on a screen recording of the GSAP page unless explicitly requested.

## Tool roles

- Remotion: frame-accurate scene composition, timing, preview, and MP4 rendering.
- Cohub TTS: optional voice generation.
- STT/ASR: final audio completeness and wording verification.
- FFmpeg/ffprobe: media inspection and audio-level checks.
- GSAP: optional interactive web derivative.
- `lark-doc`, `pdf`, `documents`, or web access: source-faithful intake.
- Image generation: optional illustration only when source media cannot carry the scene; label generated material in provenance.

## Handoff

Lead with the output. Link the MP4, project README, `story.json`, stills, narration manifest/transcript, and comparison report if one was requested. State what passed, what remains approximate, any remote generation cost reported by the provider, and whether anything was published.
