# i18n-translator

AI-powered multi-language website translation tool. Extracts Chinese text, translates via Gemini, generates language-specific HTML versions.

## Quick Start

```bash
# Install
pip install google-generativeai
export GEMINI_API_KEY="your-api-key"

# Translate to all 6 languages
./translate-all.sh ~/my-website

# Or pick specific languages
./auto-translate.sh ~/my-website "en-US,ja-JP"
```

## Supported Languages

`en-US` `ja-JP` `ko-KR` `es-ES` `fr-FR` `de-DE`

## How It Works

1. **Extract** — Scans HTML, replaces Chinese text with `__I18N__key__` tokens
2. **Translate** — Sends tokens to Gemini API, generates per-language dictionaries
3. **Apply** — Copies project, replaces tokens with translated text

> **Note:** `extract --write` modifies source files. Back up or use git before running.

## Scripts

| Script | Usage |
|--------|-------|
| `translate-all.sh <dir>` | Translate to all 6 languages |
| `auto-translate.sh <dir> [langs]` | Translate to selected languages |
| `main.py extract` | Extract text to dictionary |
| `main.py apply` | Apply translations to output |
| `main.py embed-switch` | Add language switcher to HTML |
| `translate.py` | AI translation engine |

## Full Documentation

See [SKILL.md](./SKILL.md) for complete reference.
