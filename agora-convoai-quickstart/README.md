# Agora ConvoAI Quickstart

Beginner-friendly skill to run Agora's official voice agent demo end-to-end.

## Quick Start

```bash
cd agora-convoai-quickstart
chmod +x bin/*.sh

# First time (login + project + env + deps + hotfix)
./bin/bootstrap.sh

# Daily run
./bin/run.sh
```

Open:
- `http://localhost:3000`
- `http://localhost:8000/docs`

## What This Skill Automates

- Clone official sample: `AgoraIO-Conversational-AI/agent-quickstart-python`
- Install dependencies (`bun install`)
- Create/select Agora project with `rtc + rtm + convoai`
- Write `server/.env.local` via `agora project env write --with-secrets --overwrite`
- Apply two stability hotfixes (empty `agent_id`, RTM subscribe retry)
- Start dev with proxy env unset to avoid SOCKS runtime crash

## Config

| Variable | Description | Default |
|---|---|---|
| `AGORA_DEMO_WORKSPACE` | Demo checkout directory | `<skill>/workspace` |
| `AGORA_PROJECT_NAME` | Project name to create/use | `agora-quickstart-<timestamp>` |

## Full Reference

See [SKILL.md](./SKILL.md).
