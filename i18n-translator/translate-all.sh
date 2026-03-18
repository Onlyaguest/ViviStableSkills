#!/bin/bash
# Translate to ALL supported languages at once
# Usage: ./translate-all.sh <input-file-or-dir> [output-dir]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INPUT="${1:?Usage: $0 <input-file-or-dir> [output-dir]}"
OUTPUT="${2:-${INPUT}__all-langs}"

# All supported languages
ALL_LANGS="en-US,ja-JP,ko-KR,es-ES,fr-FR,de-DE"

echo "🌍 Translating to ALL languages: $ALL_LANGS"
echo ""

"$SCRIPT_DIR/auto-translate.sh" "$INPUT" "$ALL_LANGS" "$OUTPUT"
