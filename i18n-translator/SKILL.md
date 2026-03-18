---
name: i18n-translator
description: AI-powered multi-language website translation. Automatically extracts text, translates to 6+ languages (English, Japanese, Korean, Spanish, French, German), generates language-specific versions, and adds language switcher. Supports incremental updates and batch processing.
version: 1.0.0
author: Vivi
repository: https://github.com/Onlyaguest/ViviStableSkills
---

# i18n-translator

AI-powered multi-language website translation tool.

## What It Does

Transforms any Chinese website/HTML into multiple languages with one command:

```bash
./translate-all.sh ~/my-website
```

**Result:**
- 🇺🇸 English version
- 🇯🇵 Japanese version
- 🇰🇷 Korean version
- 🇪🇸 Spanish version
- 🇫🇷 French version
- 🇩🇪 German version
- 🌐 Language switcher (top-right corner)

## Quick Start

### 1. Install

```bash
# Clone this skill
git clone https://github.com/Onlyaguest/ViviStableSkills.git
cd ViviStableSkills/i18n-translator

# Install dependencies
pip install google-generativeai
```

### 2. Set API Key

```bash
export GEMINI_API_KEY="your-api-key"
```

Get your key from: https://aistudio.google.com/app/apikey

### 3. Translate

```bash
# Translate to all languages
./translate-all.sh /path/to/your/website

# Or choose specific languages
./auto-translate.sh /path/to/your/website "en-US,ja-JP,ko-KR"
```

## Use Cases

### Case 1: Technical Documentation

**Before:**
```
~/docs/
├── index.html (Chinese)
└── guide.html (Chinese)
```

**Command:**
```bash
./auto-translate.sh ~/docs "en-US,ja-JP"
```

**After:**
```
~/docs__multilang__en-US/  (English)
~/docs__multilang__ja-JP/  (Japanese)
```

### Case 2: Product Landing Page

**Before:**
```
~/product/index.html (Chinese)
```

**Command:**
```bash
./translate-all.sh ~/product
```

**After:**
- 6 language versions
- Language switcher in top-right corner
- Users can switch languages without page reload

### Case 3: Data Reports

**Before:**
```
~/reports/Q4-2026.html (Chinese)
```

**Command:**
```bash
./auto-translate.sh ~/reports/Q4-2026.html "en-US,ja-JP,ko-KR"
```

**After:**
- English, Japanese, Korean versions
- Perfect for international teams

## Features

### ✨ Core Features

- **AI Translation** - Powered by Gemini 2.5 Flash
- **Batch Processing** - Translates 100+ texts in seconds
- **Incremental Updates** - Only translates new/changed content
- **Language Switcher** - Auto-generated UI component
- **6+ Languages** - English, Japanese, Korean, Spanish, French, German
- **Zero Config** - Works out of the box

### 🎯 Smart Features

- **Context-Aware** - Preserves HTML structure
- **Token-Based** - Consistent translations across pages
- **Logging** - Tracks API usage and costs
- **Error Handling** - Graceful fallbacks
- **Dry Run** - Preview before applying

## Supported Languages

| Code | Language | Use Case |
|------|----------|----------|
| `en-US` | English | Global |
| `ja-JP` | Japanese | Asia |
| `ko-KR` | Korean | Asia |
| `es-ES` | Spanish | Europe/Americas |
| `fr-FR` | French | Europe |
| `de-DE` | German | Europe |

## Advanced Usage

### Incremental Translation

```bash
# First time: translates everything
./auto-translate.sh ~/project "en-US,ja-JP"

# After editing Chinese content
./auto-translate.sh ~/project "en-US,ja-JP"
# → Only translates new/changed content!
```

### Custom Batch Size

```bash
python3 translate.py \
  --root ~/project \
  --targets "en-US,ja-JP" \
  --batch-size 10
```

### Add Language Switcher

```bash
python3 main.py embed-switch \
  --html ~/output/index.html \
  --root ~/project \
  --langs "zh-CN,en-US,ja-JP,ko-KR"
```

## Troubleshooting

### HTML Attributes Not Translated

**Problem:** Attributes like `data-num="第一层"` remain in Chinese.

**Solution:**

```bash
# Manual replacement (recommended for <10 attributes)
cd ~/project__multilang__en-US
sed -i '' 's/data-num="第一层"/data-num="Layer 1"/g' index.html
sed -i '' 's/data-num="第二层"/data-num="Layer 2"/g' index.html
```

**Common untranslated attributes:**
- `data-*` attributes
- `aria-label`
- `title`
- `placeholder`

### Translation Quality Issues

**Solution:** Edit the dictionary file:

```bash
vim ~/project/i18n/en-US.json
```

Then regenerate:

```bash
python3 main.py apply \
  --root ~/project \
  --lang en-US \
  --out-dir ~/output
```

### API Rate Limits

**Solution:** Reduce batch size:

```bash
python3 translate.py \
  --root ~/project \
  --targets "en-US" \
  --batch-size 5
```

## File Structure

```
your-project/
├── index.html              # Original (tokenized)
├── i18n/
│   ├── zh-CN.json         # Chinese dictionary
│   ├── en-US.json         # English dictionary
│   ├── ja-JP.json         # Japanese dictionary
│   └── logs/
│       └── translate-*.json  # Translation logs

your-project__multilang__en-US/
├── index.html              # English version
└── i18n/
    └── en-US.json

your-project__multilang__ja-JP/
├── index.html              # Japanese version
└── i18n/
    └── ja-JP.json
```

## Performance

- **Extraction**: ~1000 files/second
- **Translation**: ~100 texts/minute (API-dependent)
- **Generation**: ~1000 files/second

## Cost Estimation

Using Gemini 2.5 Flash:
- ~1.5 tokens per Chinese character
- ~$0.075 per 1M input tokens
- ~$0.30 per 1M output tokens

**Example:**
- 1000 Chinese characters
- Translate to 3 languages
- Cost: ~$0.01

## Integration Examples

### For Claude Code

```bash
# In your Claude Code project
git clone https://github.com/Onlyaguest/ViviStableSkills.git skills
cd skills/i18n-translator

# Translate your docs
./translate-all.sh ../../docs
```

### For OpenClaw

```bash
# Add to workspace skills
cd ~/.openclaw/workspace/skills
git clone https://github.com/Onlyaguest/ViviStableSkills.git vivi-skills
ln -s vivi-skills/i18n-translator .

# Use in agent
cd ~/.openclaw/workspace/skills/i18n-translator
./translate-all.sh ~/project
```

### For Other AI Agents

```bash
# Clone to your agent's workspace
cd /path/to/agent/workspace
git clone https://github.com/Onlyaguest/ViviStableSkills.git

# Use directly
cd ViviStableSkills/i18n-translator
./translate-all.sh /path/to/content
```

## Real-World Examples

### Example 1: Hermes Swarm Analysis

**Input:** Technical article (418 texts)
**Command:** `./auto-translate.sh ~/article "en-US,ja-JP,ko-KR"`
**Time:** ~3 minutes
**Cost:** ~$0.05
**Result:** 3 language versions + switcher

### Example 2: E2E Latency Optimization

**Input:** Technical guide (69 texts)
**Command:** `./auto-translate.sh ~/guide "en-US"`
**Time:** ~30 seconds
**Cost:** ~$0.01
**Result:** English version with perfect formatting

### Example 3: AI Consulting Guide

**Input:** Business document (150 texts)
**Command:** `./translate-all.sh ~/guide`
**Time:** ~2 minutes
**Cost:** ~$0.03
**Result:** 6 language versions

## Best Practices

1. **Backup First** - Use git or backup before translating
2. **Preview Changes** - Use `--dry-run` to preview
3. **Incremental Updates** - Re-run after editing Chinese content
4. **Manual Review** - Check translations for accuracy
5. **Attribute Check** - Look for untranslated HTML attributes
6. **Batch Size** - Adjust based on API limits
7. **Cost Tracking** - Monitor logs for API usage

## FAQ

**Q: Can I translate from English to other languages?**
A: Yes! The tool auto-detects source language. Just run the same commands.

**Q: Does it work with React/Vue/Angular?**
A: Yes, but you need to build the static HTML first.

**Q: Can I customize the language switcher?**
A: Yes, edit the CSS in the generated HTML.

**Q: What about SEO?**
A: Each language version is a separate HTML file, perfect for SEO.

**Q: Can I use other AI models?**
A: Currently supports Gemini. PRs welcome for other models!

## Contributing

Found a bug? Have a feature request?

1. Fork the repo
2. Create a branch
3. Submit a PR

## License

MIT

## Support

- GitHub Issues: https://github.com/Onlyaguest/ViviStableSkills/issues
- Documentation: See README.md in this directory

---

**Made with ❤️ by Vivi**

*Tested in production with 100+ websites*
