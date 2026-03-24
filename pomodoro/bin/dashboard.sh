#!/usr/bin/env bash
# Pomodoro Dashboard Generator - 生成看板并部署到 Vercel

set -euo pipefail

BASE_DIR="$HOME/.openclaw/workspace/skills/pomodoro"
DATA_DIR="$BASE_DIR/data"
SITE_DIR="$HOME/MyOpenClawWebsite/sites/pomodoro"
GIT_DIR="$HOME/MyOpenClawWebsite"

# 确保目录存在
mkdir -p "$SITE_DIR"

# 复制 HTML 模板（静态 HTML 通过 JS 读取 JSON）
cp "$BASE_DIR/assets/index.html" "$SITE_DIR/index.html"

# 复制 JSON 数据（供前端读取）
cp "$DATA_DIR/sessions.json" "$SITE_DIR/sessions.json"

# Git 提交并推送
cd "$GIT_DIR"
git add sites/pomodoro/
git commit -m "🍅 Pomodoro dashboard update $(date '+%Y-%m-%d %H:%M')" || true
git push origin main

echo "✅ Dashboard deployed: https://your-site.vercel.app/sites/pomodoro/"
