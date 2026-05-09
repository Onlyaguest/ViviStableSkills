---
name: i18n-kit
description: Add offline multilingual support to static HTML, small web projects, or reports by extracting text into tokens, maintaining language dictionaries, applying translated outputs, and optionally embedding a local language switcher. Use when the user asks for bilingual support, tokenizing Chinese copy, offline language switching, or i18n for reports and lightweight sites.
version: 1.0.0
author: Vivi
tags: [i18n, translation, html, multilingual, offline]
platforms: [all]
dependencies:
  - python3
  - pypinyin
---

# i18n-kit

Offline-first i18n workflow for small sites and reports. It extracts UI copy into tokens, maintains dictionaries, applies translated outputs, and can inject a local language switcher into a single HTML file.

## Use this skill when

- The user says "帮我做中英双语"
- The user wants an offline language switcher for a report page
- The project is static HTML or a small frontend, not a large framework-first app
- The user wants to tokenize Chinese UI text before translating

## Workflow

1. Run `extract --dry-run` first to preview what text will be captured.
2. Run `extract --write` only after preview looks correct.
3. Prepare target dictionaries manually or with AI translation.
4. Use `apply` to generate language-specific outputs.
5. Use `embed-switch` when one HTML file should switch languages locally.

## Commands

Minimum validation:

```bash
python3 main.py --dry-run extract --root examples/site --lang zh-CN --ext .html
```

Generate tokens and dictionary:

```bash
python3 main.py extract --root /absolute/path/to/project --lang zh-CN --ext .html --write
```

Apply a target language:

```bash
python3 main.py apply --root /absolute/path/to/project --lang en-US --out-dir /absolute/path/to/project__en
```

Embed offline switcher:

```bash
python3 main.py embed-switch --html /absolute/path/to/project/report.html --root /absolute/path/to/project --langs zh-CN,en-US
```

## Inputs and outputs

- Input: static HTML / JSX / TSX / JS / TS / Python templates with UI text
- Output: tokenized source files, `i18n/<lang>.json` dictionaries, translated output directories, or a single HTML file with local language switching

## Validation

Minimum validation command:

```bash
python3 main.py --dry-run extract --root examples/site --lang zh-CN --ext .html
```

This validates the core offline extraction path without requiring any API key.

## Constraints

- Always preview with `--dry-run` before `--write`
- Best fit is reports and small static projects
- For large React apps, framework-native i18n may still be better
- AI translation is optional; extraction and offline switching should work without API access
