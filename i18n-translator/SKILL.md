---
name: i18n-translator
description: AI-powered multi-language website translation with text extraction, Gemini translation, and language switcher.
version: 1.1.0
author: Vivi
tags: [i18n, translation, html, multilingual]
platforms: [all]
dependencies:
  - python3
  - pip (google-generativeai)
---

# i18n-translator Skill

Transforms Chinese HTML/web content into multiple languages with one command.

## Features

- AI translation via Gemini 2.5 Flash
- 6 built-in languages (extensible to any language)
- Batch processing (100+ texts per minute)
- Incremental updates (only translates new/changed content)
- Offline language switcher (no server required)
- Dry-run preview mode

## Quick Start

```bash
pip install google-generativeai
export GEMINI_API_KEY="your-key"  # Get from https://aistudio.google.com/app/apikey

# All languages
./translate-all.sh ~/project

# Selected languages
./auto-translate.sh ~/project "en-US,ja-JP,ko-KR"
```

## Command Reference

### Shell Scripts

| Script | Usage | Description |
|--------|-------|-------------|
| `translate-all.sh` | `./translate-all.sh <dir> [out]` | Translate to all 6 languages |
| `auto-translate.sh` | `./auto-translate.sh <dir> [langs] [out]` | Translate to selected languages |

### Python Commands

| Command | Usage | Description |
|---------|-------|-------------|
| `extract` | `python3 main.py extract --root <dir> --lang zh-CN --write` | Extract text, replace with tokens |
| `apply` | `python3 main.py apply --root <dir> --lang en-US --out-dir <out>` | Generate translated version |
| `embed-switch` | `python3 main.py embed-switch --html <file> --root <dir> --langs zh-CN,en-US` | Add language switcher |
| `translate` | `python3 translate.py --root <dir> --targets "en-US,ja-JP"` | AI-translate dictionaries |

### Common Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Preview without writing files |
| `--batch-size N` | Texts per API call (default: 20) |
| `--ext .html` | File extensions to scan (repeatable) |

## Configuration

| Env Variable | Required | Description |
|-------------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Gemini API key |

## Workflow

```
Source HTML (Chinese)
  -> extract --write
Tokenized HTML + i18n/zh-CN.json
  -> translate.py
i18n/en-US.json, i18n/ja-JP.json, ...
  -> apply --out-dir
Translated HTML versions
```

> **Warning:** `extract --write` modifies source files in-place (Chinese text -> tokens). Always backup first.

## Output Structure

```
project/
├── index.html          # Tokenized (after extract)
├── i18n/
│   ├── zh-CN.json      # Chinese dictionary
│   ├── en-US.json      # English dictionary
│   └── ja-JP.json      # Japanese dictionary

project__multilang__en-US/
└── index.html          # English version

project__multilang__ja-JP/
└── index.html          # Japanese version
```

## Supported Languages

| Code | Language |
|------|----------|
| `en-US` | English |
| `ja-JP` | Japanese |
| `ko-KR` | Korean |
| `es-ES` | Spanish |
| `fr-FR` | French |
| `de-DE` | German |

Custom languages: `python3 translate.py --root <dir> --target th-TH`

## Cost Estimation (Gemini 2.5 Flash)

- ~1.5 tokens per Chinese character
- 1000 chars x 3 languages ~ $0.01

## Troubleshooting

**API key error?**
`echo $GEMINI_API_KEY` — ensure it's set. Get one at https://aistudio.google.com/app/apikey

**Output dir already exists?**
The tool auto-removes existing output. If issues persist, delete manually.

**HTML attributes not translated?**
`data-*`, `aria-label`, `title`, `placeholder` attributes need manual replacement via `sed`. See `examples/` for patterns.

**Rate limited?**
Reduce batch size: `python3 translate.py --root <dir> --targets en-US --batch-size 5`
