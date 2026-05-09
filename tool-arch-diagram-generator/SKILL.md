---
name: tool-arch-diagram-generator
description: Generate offline HTML architecture diagrams from Mermaid embedded in Markdown. Use when the user asks to draw an architecture diagram, convert Mermaid to an offline page, build a sequence/flow/class/ER diagram, or turn Markdown Mermaid blocks into a shareable local HTML file.
version: 1.0.0
author: Vivi
tags: [mermaid, architecture, diagram, markdown, html]
platforms: [all]
dependencies:
  - python3
---

# tool-arch-diagram-generator

Turn Markdown Mermaid blocks into a fully offline `index.html` without any CDN dependency.

## Use this skill when

- The user says "帮我画架构图" or "生成 Mermaid 页面"
- The input is Markdown with ```mermaid blocks
- The user wants a local HTML deliverable for sharing or review
- The diagram type is `sequenceDiagram`, `flowchart`, `classDiagram`, `erDiagram`, `gantt`, or similar Mermaid syntax

## Workflow

1. Prepare or edit a Markdown file containing Mermaid.
2. Run `--dry-run` first to confirm blocks are detected.
3. Generate offline HTML.
4. Open the HTML locally to verify rendering.

## Commands

Preview:

```bash
python3 main.py --input /absolute/path/to/diagram.md --dry-run
```

Generate:

```bash
python3 main.py \
  --input /absolute/path/to/diagram.md \
  --output ./dist \
  --title "System Architecture"
```

The skill auto-detects a bundled local `mermaid.min.js`. If needed, override with:

```bash
python3 main.py --input /absolute/path/to/diagram.md --mermaid-js /absolute/path/to/mermaid.min.js
```

## Inputs and outputs

- Input: a Markdown file with Mermaid blocks
- Output: an offline HTML file, usually `./dist/index.html`

## Validation

Minimum validation command:

```bash
python3 main.py --input /absolute/path/to/diagram.md --dry-run
```

Successful generation prints:

```text
OK: /path/to/output/index.html
```

## Constraints

- Prefer fenced ` ```mermaid ` blocks for reliable parsing
- No CDN is used; the local bundled `mermaid.min.js` is the default runtime
- If no Mermaid block is found, the script exits with a readable error
