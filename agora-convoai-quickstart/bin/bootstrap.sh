#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
WORKSPACE_DIR="${AGORA_DEMO_WORKSPACE:-$SKILL_DIR/workspace}"
DEMO_DIR="$WORKSPACE_DIR/agent-quickstart-python"
PROJECT_NAME="${AGORA_PROJECT_NAME:-agora-quickstart-$(date +%m%d-%H%M%S)}"

for cmd in git node npm bun python3 agora; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Missing dependency: $cmd"
    exit 1
  fi
done

mkdir -p "$WORKSPACE_DIR"

AUTH_JSON="$(agora whoami --json || true)"
if [[ "$AUTH_JSON" != *'"authenticated":true'* ]]; then
  echo "Not authenticated. Starting login..."
  agora login --no-browser
fi

if [[ ! -d "$DEMO_DIR/.git" ]]; then
  git clone https://github.com/AgoraIO-Conversational-AI/agent-quickstart-python "$DEMO_DIR"
fi

cd "$DEMO_DIR"
bun install

agora project create "$PROJECT_NAME" --feature rtc --feature rtm --feature convoai --json || true
agora project use "$PROJECT_NAME" --json || true
agora project env write server/.env.local --with-secrets --overwrite --json
agora project doctor --json || true

cp "$SKILL_DIR/patches/server/src/agent.py" "$DEMO_DIR/server/src/agent.py"
cp "$SKILL_DIR/patches/web/src/hooks/useAgoraConnection.ts" "$DEMO_DIR/web/src/hooks/useAgoraConnection.ts"

echo "Bootstrap done."
echo "Demo dir: $DEMO_DIR"
echo "Next: $SCRIPT_DIR/run.sh"
