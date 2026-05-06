#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
WORKSPACE_DIR="${AGORA_DEMO_WORKSPACE:-$SKILL_DIR/workspace}"
DEMO_DIR="$WORKSPACE_DIR/agent-quickstart-python"

if [[ ! -d "$DEMO_DIR" ]]; then
  echo "Demo not found. Run ./bin/bootstrap.sh first."
  exit 1
fi

cd "$DEMO_DIR"
if [[ ! -f server/.env.local ]]; then
  echo "Missing server/.env.local. Run ./bin/bootstrap.sh first."
  exit 1
fi

echo "Starting dev server..."
echo "Frontend: http://localhost:3000"
echo "Backend : http://localhost:8000/docs"

env -u all_proxy -u http_proxy -u https_proxy -u ALL_PROXY -u HTTP_PROXY -u HTTPS_PROXY \
  bun run dev
