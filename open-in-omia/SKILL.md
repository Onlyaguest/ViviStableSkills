---
name: open-in-omia
description: Open local review artifacts in Xiaoer Omia when users ask to open, preview, inspect, or review a file.
metadata:
  version: 1.0.0
  author: Vivi
  tags: [productivity, viewer, local-first, macos]
  platforms: [macos]
  dependencies: [Xiaoer Omia, bash]
---

# Open in Omia

Use Xiaoer Omia as the quiet local review surface. Keep editing in the agent or a dedicated editor.

## Features

- Open common local artifacts in Omia by bundle identifier
- Support HTML, Markdown, PDF, Office, images, media, data, archives, code, and 3D files
- Validate file existence and extension before launch
- Open one primary artifact by default to reduce window noise
- Never change macOS global file associations
- Never silently fall back to another application

## Workflow

1. Resolve the requested local artifact.
2. If several artifacts exist and the user did not request all of them, choose the primary final deliverable only.
3. Do not use this skill for an external URL, source-code editing, or when the user names another app.
4. Run:

```bash
bin/open-in-omia.sh "/absolute/path/to/artifact"
```

5. Report only the opened file or the concrete blocker.

## Command Reference

| Command | Purpose |
|---|---|
| `bin/open-in-omia.sh FILE...` | Open supported local files in Omia |
| `bin/open-in-omia.sh --check FILE...` | Validate without launching Omia |
| `bin/open-in-omia.sh --force FILE...` | Try an unlisted format when explicitly requested |
| `bin/open-in-omia.sh --help` | Show usage |

## Output States

```text
READY        /absolute/path
OPENED       /absolute/path
MISSING      /absolute/path
UNSUPPORTED  /absolute/path
OPEN_FAILED  /absolute/path
APP_MISSING  Xiaoer Omia (com.jane.xiaoeromon)
```

Treat `OPENED` as successful handoff to the review surface, not as user acceptance of the artifact.

## Boundaries

- Never edit, convert, move, or overwrite a file while opening it.
- Never change the user's default applications.
- Never use `--force` unless the user explicitly asks to try an unlisted format.
- If Omia is missing, direct the user to the official download page in README.md.

## Troubleshooting

**Omia is reported missing:** Install it, launch it once, then retry.

**A supported-looking file is rejected:** Run with `--check`, inspect the extension, and use `--force` only with user approval.

**A Codex file link opens internally:** Ask the agent to “open this in Omia”; the skill calls macOS directly instead of relying on link handling.
