#!/usr/bin/env bash
set -euo pipefail

# Resolve paths relative to this script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Load .env if present
if [ -f "$SKILL_DIR/.env" ]; then
    set -a
    source "$SKILL_DIR/.env"
    set +a
fi

exec python3 "$SKILL_DIR/main.py" archive "$@"
