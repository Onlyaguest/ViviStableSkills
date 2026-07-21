#!/usr/bin/env bash

set -euo pipefail

APP_ID="com.jane.xiaoeromon"
CHECK_ONLY=0
FORCE=0

usage() {
  printf 'Usage: %s [--check] [--force] FILE [FILE ...]\n' "$0" >&2
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --check) CHECK_ONLY=1; shift ;;
    --force) FORCE=1; shift ;;
    --) shift; break ;;
    -h|--help) usage; exit 0 ;;
    -*) printf 'UNKNOWN_OPTION\t%s\n' "$1" >&2; usage; exit 64 ;;
    *) break ;;
  esac
done

if [ "$#" -eq 0 ]; then
  usage
  exit 64
fi

if ! open -Ra "Xiaoer Omia" >/dev/null 2>&1; then
  printf 'APP_MISSING\tXiaoer Omia (%s)\n' "$APP_ID" >&2
  exit 69
fi

is_supported_extension() {
  case "$1" in
    md|markdown|txt|text|html|htm|pdf|ai|doc|docx|ppt|pptx|xls|xlsx|xlsm|\
    png|jpg|jpeg|gif|webp|svg|bmp|tif|tiff|ico|heic|heif|psd|cdr|\
    cr2|cr3|crw|nef|nrw|arw|srf|sr2|dng|orf|rw2|raw|raf|pef|srw|rwl|x3f|3fr|fff|iiq|erf|mrw|dcr|kdc|\
    mp4|mov|webm|m4v|wav|mp3|m4a|aac|flac|ogg|epub|zip|tar|gz|tgz|xmind|\
    glb|gltf|obj|stl|ply|json|jsonl|ndjson|csv|tsv|xml|yaml|yml|toml|ini|conf|cfg|env|log|properties|plist|\
    graphql|gql|proto|diff|patch|js|mjs|cjs|jsx|ts|tsx|py|rb|rs|go|java|kt|kts|c|h|cpp|cc|cxx|hpp|cs|php|\
    swift|m|mm|css|scss|sass|less|sh|bash|zsh|fish|sql|lua|r|pl|pm|dart|vue|svelte|scala|clj)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

status=0

for input_path in "$@"; do
  if [ ! -f "$input_path" ]; then
    printf 'MISSING\t%s\n' "$input_path"
    status=66
    continue
  fi

  directory=$(cd "$(dirname "$input_path")" && pwd -P)
  absolute_path="$directory/$(basename "$input_path")"
  extension=${absolute_path##*.}
  extension=$(printf '%s' "$extension" | tr '[:upper:]' '[:lower:]')

  if [ "$FORCE" -ne 1 ] && ! is_supported_extension "$extension"; then
    printf 'UNSUPPORTED\t%s\n' "$absolute_path"
    status=65
    continue
  fi

  if [ "$CHECK_ONLY" -eq 1 ]; then
    printf 'READY\t%s\n' "$absolute_path"
    continue
  fi

  if open -b "$APP_ID" "$absolute_path"; then
    printf 'OPENED\t%s\n' "$absolute_path"
  else
    printf 'OPEN_FAILED\t%s\n' "$absolute_path"
    status=70
  fi
done

exit "$status"
