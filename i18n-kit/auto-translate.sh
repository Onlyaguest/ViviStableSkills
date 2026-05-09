#!/bin/bash
# One-click multi-language translation for HTML/web content
# Usage: ./auto-translate.sh <input-file-or-dir> [languages] [output-dir]
#
# Examples:
#   ./auto-translate.sh ~/report.html                    # All languages
#   ./auto-translate.sh ~/report.html en-US              # English only
#   ./auto-translate.sh ~/report.html "en-US,ja-JP"      # English + Japanese
#   ./auto-translate.sh ~/report.html "en-US,ja-JP,ko-KR" ~/output  # Custom output

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INPUT="${1:?Usage: $0 <input-file-or-dir> [languages] [output-dir]}"
LANGUAGES="${2:-en-US,ja-JP,ko-KR}"  # Default: English, Japanese, Korean
OUTPUT="${3:-${INPUT}__multilang}"

echo "🚀 Multi-language translation"
echo "   Input: $INPUT"
echo "   Languages: $LANGUAGES"
echo "   Output: $OUTPUT"
echo ""

# Step 1: Extract Chinese text and generate tokens
echo "📝 Step 1: Extracting Chinese text..."
python3 "$SCRIPT_DIR/main.py" extract \
  --root "$INPUT" \
  --lang zh-CN \
  --write \
  --ext .html

# Step 2: Auto-translate using AI
echo ""
echo "🤖 Step 2: Translating with AI..."
python3 "$SCRIPT_DIR/translate.py" \
  --root "$INPUT" \
  --source zh-CN \
  --targets "$LANGUAGES"

# Step 3: Generate output for each language
echo ""
echo "📦 Step 3: Generating language versions..."

IFS=',' read -ra LANG_ARRAY <<< "$LANGUAGES"
for lang in "${LANG_ARRAY[@]}"; do
  lang=$(echo "$lang" | xargs)  # Trim whitespace
  lang_output="${OUTPUT}__${lang}"
  
  echo "  → Generating $lang version: $lang_output"
  python3 "$SCRIPT_DIR/main.py" apply \
    --root "$INPUT" \
    --lang "$lang" \
    --out-dir "$lang_output"
done

echo ""
echo "✅ Done! Generated versions:"
for lang in "${LANG_ARRAY[@]}"; do
  lang=$(echo "$lang" | xargs)
  echo "  - $lang: ${OUTPUT}__${lang}"
done

echo ""
echo "📋 Next steps:"
echo "  - Review translations in: $INPUT/i18n/"
echo "  - For bilingual switcher in each version:"
for lang in "${LANG_ARRAY[@]}"; do
  lang=$(echo "$lang" | xargs)
  echo "    python3 $SCRIPT_DIR/main.py embed-switch --html ${OUTPUT}__${lang}/index.html --root $INPUT --langs zh-CN,$LANGUAGES"
done
