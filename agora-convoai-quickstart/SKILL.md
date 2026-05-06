---
name: agora-convoai-quickstart
description: Run Agora official Conversational AI quickstart from zero to working state with one bootstrap script and one run script.
version: 1.0.0
author: Vivi
tags: [agora, conversational-ai, voice-agent, quickstart]
platforms: [macos, linux]
dependencies:
  - bash
  - git
  - node
  - npm
  - bun
  - python3
  - agoraio-cli
---

# Agora ConvoAI Quickstart Skill

Minimal workflow for Codex / Claude Code to get a working local voice agent demo.

## Features

- Official sample-first flow
- CLI-based login/project/env setup
- Auto-apply known hotfixes for stability
- Proxy-safe run command
- Works without manual env file editing

## Quick Start

```bash
cd agora-convoai-quickstart
chmod +x bin/*.sh
./bin/bootstrap.sh
./bin/run.sh
```

## Command Reference

| Command | Purpose |
|---|---|
| `./bin/bootstrap.sh` | One-time setup: clone sample, install deps, project/env setup, hotfix apply |
| `./bin/run.sh` | Start local backend + frontend |

## Behavior Rules For Agent

- Always run `bootstrap.sh` before first run.
- If unauthenticated, execute `agora login --no-browser` and wait for OAuth completion.
- Do not ask user to manually edit `server/.env.local`.
- Start app only via `./bin/run.sh`.

## Troubleshooting

1. `socksio` proxy error in backend
- Use `./bin/run.sh` (it unsets proxy vars before startup).

2. UI exits right after click
- Check `/api/v2/startAgent` response includes non-empty `agent_id`.
- Re-run `./bin/bootstrap.sh` to reapply hotfix files.

3. Login/project issues
- `agora whoami --json`
- `agora project doctor --json`

## File Structure

```
agora-convoai-quickstart/
├── SKILL.md
├── README.md
├── .gitignore
├── bin/
│   ├── bootstrap.sh
│   └── run.sh
└── patches/
    ├── server/src/agent.py
    └── web/src/hooks/useAgoraConnection.ts
```
