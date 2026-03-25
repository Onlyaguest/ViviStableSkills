#!/usr/bin/env bash
# Pomodoro Dashboard Generator

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="${POMODORO_DATA_DIR:-$BASE_DIR/data}"
SITE_DIR="${POMODORO_SITE_DIR:?Error: please set POMODORO_SITE_DIR (e.g. ~/my-site/pomodoro)}"
GIT_DIR="${POMODORO_GIT_DIR:?Error: please set POMODORO_GIT_DIR (e.g. ~/my-site)}"

# Ensure directories exist
mkdir -p "$SITE_DIR"

# Copy HTML template and data
cp "$BASE_DIR/assets/index.html" "$SITE_DIR/index.html"
cp "$DATA_DIR/sessions.json" "$SITE_DIR/sessions.json"

# Git commit
cd "$GIT_DIR"
git add "$(basename "$SITE_DIR")/"
git commit -m "pomodoro: dashboard update $(date '+%Y-%m-%d %H:%M')" || true

echo "Ready to push to remote..."
echo "  Branch: $(git branch --show-current)"
echo "  Remote: $(git remote get-url origin 2>/dev/null || echo 'not configured')"
read -p "Confirm push? (y/N) " confirm
if [[ "$confirm" =~ ^[Yy]$ ]]; then
  git push
  echo "Dashboard deployed"
else
  echo "Push skipped (local commit preserved)"
fi
