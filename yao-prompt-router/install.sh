#!/usr/bin/env bash
# yao-prompt-router installer
#
# One-liner install:
#   curl -fsSL https://raw.githubusercontent.com/Onlyaguest/ViviStableSkills/main/yao-prompt-router/install.sh | bash
#
# Or clone and run locally:
#   ./install.sh

set -euo pipefail

SKILLS_DIR="${HOME}/.claude/skills"
TMP_DIR=$(mktemp -d)

# Detect if running locally (cloned repo) or via curl pipe
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" 2>/dev/null)" 2>/dev/null && pwd 2>/dev/null || echo "")"

cleanup() { rm -rf "$TMP_DIR"; }
trap cleanup EXIT

REPO_RAW="https://raw.githubusercontent.com/Onlyaguest/ViviStableSkills/main/yao-prompt-router"
PROMPTS_ZIP="https://github.com/yaojingang/yao-open-prompts/archive/refs/heads/main.zip"

echo ""
echo "  yao-prompt-router installer"
echo "  102 Chinese AI prompt templates, one smart entry point."
echo ""

# --- Step 1: Download yao-open-prompts ---
echo "[1/3] Downloading prompt templates from yao-open-prompts..."
curl -fsSL -o "$TMP_DIR/yao-prompts.zip" "$PROMPTS_ZIP"

echo "[2/3] Installing 9 prompt categories to $SKILLS_DIR..."
unzip -qo "$TMP_DIR/yao-prompts.zip" -d "$TMP_DIR/prompts"

PROMPTS_ROOT="$TMP_DIR/prompts/yao-open-prompts-main/prompts"
if [ ! -d "$PROMPTS_ROOT" ]; then
  echo "Error: prompts directory not found. Check network connection."
  exit 1
fi

installed=0
for dir in "$PROMPTS_ROOT"/*/; do
  name=$(basename "$dir")
  target="$SKILLS_DIR/yao-${name}"
  mkdir -p "$target"
  cp -r "$dir"* "$target/"
  installed=$((installed + 1))
done
echo "  -> $installed prompt categories installed."

# --- Step 2: Install router skill ---
echo "[3/3] Installing yao-prompt-router skill..."

ROUTER_DIR="$SKILLS_DIR/yao-prompt-router"
mkdir -p "$ROUTER_DIR"

if [ -n "$SCRIPT_DIR" ] && [ -f "$SCRIPT_DIR/SKILL.md" ]; then
  # Local install (cloned repo)
  cp "$SCRIPT_DIR/SKILL.md" "$ROUTER_DIR/SKILL.md"
  [ -f "$SCRIPT_DIR/prompt-index.json" ] && cp "$SCRIPT_DIR/prompt-index.json" "$ROUTER_DIR/"
  echo "  -> Installed from local files."
else
  # Remote install (curl pipe) - download individual files directly
  curl -fsSL -o "$ROUTER_DIR/SKILL.md" "$REPO_RAW/SKILL.md"
  curl -fsSL -o "$ROUTER_DIR/prompt-index.json" "$REPO_RAW/prompt-index.json" 2>/dev/null || true
  echo "  -> Installed from GitHub."
fi

# --- Done ---
echo ""
echo "  Done! Installed:"
ls -1d "$SKILLS_DIR"/yao-* 2>/dev/null | while read -r d; do
  echo "    $(basename "$d")"
done
echo ""
echo "  Restart Claude Code, then try:"
echo "    '帮我写一篇小红书种草文案'"
echo "    '优化一下这个标题'"
echo "    '帮我做个GEO优化方案'"
echo ""
