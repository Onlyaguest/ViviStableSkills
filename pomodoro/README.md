# Pomodoro Timer

AI-powered Pomodoro timer with auto-completion, local JSON logging, and macOS notifications.

## Quick Start

```bash
chmod +x bin/*.sh

# Start a 25-minute session
./bin/pomodoro.sh start "write code" 25

# Check status
./bin/pomodoro.sh status

# View today's sessions
./bin/pomodoro.sh today
```

## Commands

| Command | Description |
|---------|-------------|
| `start <task> [min]` | Start new pomodoro (default: 25 min) |
| `done [note]` | Complete current session |
| `interrupt [note]` | Stop current session |
| `status` | Check current session |
| `today` | View today's sessions |

## Optional Integrations

| Feature | Requires | Env Var |
|---------|----------|---------|
| Roam Research sync | [Babashka](https://github.com/babashka/babashka) | `ROAM_GRAPH` |
| Dashboard deploy | Git + hosting | `POMODORO_SITE_DIR`, `POMODORO_GIT_DIR` |

## Data

Sessions are stored in `data/sessions.json` (auto-created on first run).

## Full Documentation

See [SKILL.md](./SKILL.md) for complete reference.
