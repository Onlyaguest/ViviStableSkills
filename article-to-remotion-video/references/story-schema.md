# `story.json` contract

The bundled template treats `story.json` as the single content file. Keep source facts and content decisions here; keep rendering mechanics in React.

## Top-level fields

```json
{
  "meta": {
    "title": "Video title",
    "sourceTitle": "Original article title",
    "sourceUrl": "https://...",
    "authorVoice": "first-person, warm, lightly self-deprecating",
    "fps": 30,
    "width": 1920,
    "height": 1080
  },
  "theme": {
    "background": "#07100F",
    "panel": "#101A18",
    "text": "#F4F0E7",
    "muted": "#9DAAA4",
    "primary": "#F16B42",
    "success": "#57E0BD"
  },
  "scenes": []
}
```

`fps`, `width`, and `height` are optional; the template defaults to 30, 1920, and 1080. Each scene requires `id`, `type`, `durationSeconds`, `kicker`, and `title`.

## Scene types

### `hero`

Use for a hook, problem, or short first-person opening.

```json
{
  "id": "hook",
  "type": "hero",
  "durationSeconds": 8,
  "kicker": "01 / OPEN",
  "title": "The main line",
  "accentTitle": "The emphasized line",
  "body": "One short supporting sentence.",
  "quote": "A source-grounded quote.",
  "image": "assets/original.png",
  "narration": "Narration under 200 Unicode characters.",
  "audio": "audio/01-hook.mp3",
  "audioPlaybackRate": 1
}
```

### `workflow`

Use for an action path, process, or cause-and-effect sequence. `stats` can contain 1–4 evidence cards.

```json
{
  "id": "workflow",
  "type": "workflow",
  "durationSeconds": 13,
  "kicker": "02 / ACTION",
  "title": "A workflow changed",
  "body": "What changed and why.",
  "steps": ["Input", "Confirm", "Run", "Result"],
  "stats": [{"value": "6", "label": "changed"}],
  "image": "assets/source-ui.png",
  "narration": "...",
  "audio": "audio/02-workflow.mp3"
}
```

### `chips`

Use for a bounded collection such as terms, principles, or named items.

```json
{
  "id": "terms",
  "type": "chips",
  "durationSeconds": 11,
  "kicker": "03 / VOCAB",
  "title": "10 terms",
  "body": "Why this collection matters.",
  "chips": ["one", "two"],
  "image": "assets/source-card.png",
  "narration": "...",
  "audio": "audio/03-terms.mp3"
}
```

### `distribution`

Use for a total that breaks into categories.

```json
{
  "id": "result",
  "type": "distribution",
  "durationSeconds": 15,
  "kicker": "04 / RESULT",
  "title": "Files organized",
  "total": 57,
  "totalLabel": "files",
  "steps": ["Button", "App", "Script", "Dialog"],
  "stats": [
    {"value": "48", "label": "images"},
    {"value": "4", "label": "documents"}
  ],
  "footer": "An honest boundary or secondary result.",
  "image": "assets/source-result.png",
  "narration": "...",
  "audio": "audio/04-result.mp3"
}
```

### `closing`

Use for the conclusion and limitations.

```json
{
  "id": "closing",
  "type": "closing",
  "durationSeconds": 8,
  "kicker": "05 / CLOSE",
  "title": "The meaning",
  "accentTitle": "A short final line.",
  "body": "The honest takeaway.",
  "badges": ["Depends on a computer"],
  "image": "assets/source-ending.png",
  "narration": "...",
  "audio": "audio/05-closing.mp3"
}
```

## Invariants

- Scene IDs are unique and filesystem-safe.
- Total duration should match the user's request; default acceptance range is 45–60 seconds.
- `image` and `audio` are project-public-relative paths, not absolute paths or remote URLs.
- Every number and quote used on screen must appear in source notes.
- Keep narration per scene under 200 Unicode characters for Qwen voice-design mode.
- Omit `audio` when producing a silent draft. Do not point to files that do not exist.
