# i18n-kit

Offline-first i18n toolkit for reports and small web projects. It supports:

- extracting UI text into `__I18N__...__` tokens
- building `i18n/<lang>.json` dictionaries
- generating translated output directories
- embedding an offline language switcher into a single HTML file

## Visual Guide

Open `guide.html` for a quick visual overview of:

- when this skill should trigger
- the no-API validation flow
- the extract / apply / embed-switch workflow
- the review checklist

## Quick Start

```bash
# Local validation without API
python3 main.py --dry-run extract --root examples/site --lang zh-CN --ext .html

# Then tokenize for real
python3 main.py extract --root /path/to/project --lang zh-CN --ext .html --write
```

## Optional AI Translation

`translate.py`, `auto-translate.sh`, and `translate-all.sh` are included for AI-assisted dictionary generation. They are optional and can be added after the offline extraction flow is confirmed.
