# Acceptance checklist

## Source

- Source title and location recorded.
- Facts, numbers, quotes, and limitations trace to the source.
- Images are original, licensed, generated-and-labeled, or clearly marked placeholders.
- Author tone is recognizable without fabricated first-person experiences.

## Project

- Work is isolated in a new directory.
- `story.json` passes `scripts/validate_story.py`.
- `npm install`, typecheck, and bundle succeed.
- Preview and render commands are documented.

## Visuals

- Hook, middle evidence, result, and closing stills were rendered and inspected.
- No clipped text, unreadable labels, accidental overlaps, or broken images.
- Animation explains state, progression, quantity, or causality.
- The visual system is coherent across scenes.

## Video

- MP4 exists and has the expected duration, dimensions, frame rate, and codec.
- Audio stream exists when narration was requested.
- Audio is neither silent nor clipped according to `volumedetect` and listening/STT evidence.
- The final narration line is present.

## Failure handling

- If source access fails, finish a clearly labeled structural draft and report the blocked facts/assets.
- If source images fail, use code illustrations or explicit placeholders; do not invent screenshots.
- If TTS fails or truncates, preserve the silent video and narration script, then retry only with a materially different supported request shape.
- If one TTS segment fails, do not mix unrelated voices silently. Either regenerate the complete set consistently or disclose the mismatch.
- If Remotion's first Headless Chrome download stalls but a trusted local Chrome is already installed, set `REMOTION_BROWSER_EXECUTABLE` for `npm run stills` instead of repeatedly restarting the download.
- Never overwrite the user's prior video; keep silent/draft/final variants separately.
