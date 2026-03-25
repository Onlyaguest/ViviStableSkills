---
name: pomodoro
description: AI-powered Pomodoro timer with auto-completion, local logging, and macOS notifications.
version: 1.1.0
author: Vivi
tags: [productivity, timer, focus]
platforms: [macos]
dependencies:
  - python3
  - bash
---

# Pomodoro Timer Skill

Manages focus sessions with timer, auto-completion, JSON logging, and optional Roam/dashboard sync.

## Features

- Auto-completion after set duration
- Local JSON session logging
- macOS system notifications
- Energy cost tracking (-15 complete, -8 interrupted)
- Optional: Roam Research sync
- Optional: Live dashboard deployment

## Quick Start

```bash
cd pomodoro && chmod +x bin/*.sh

# Start 25-minute session
./bin/pomodoro.sh start "write code" 25

# Complete early with note
./bin/pomodoro.sh done "finished ahead of schedule"
```

## Command Reference

| Command | Description | Example |
|---------|-------------|---------|
| `start <task> [min]` | Start new pomodoro | `start "coding" 25` |
| `done [note]` | Complete current session | `done "all tests pass"` |
| `interrupt [note]` | Stop current session | `interrupt "urgent call"` |
| `status` | Show current session | `status` |
| `today` | View today's sessions | `today` |

## Configuration

All configuration is via environment variables (all optional):

| Variable | Description | Default |
|----------|-------------|---------|
| `POMODORO_DATA_DIR` | Session data directory | `<skill>/data/` |
| `ROAM_GRAPH` | Roam Research graph name for sync | _(disabled)_ |
| `POMODORO_SITE_DIR` | Dashboard HTML output directory | _(required for dashboard)_ |
| `POMODORO_GIT_DIR` | Dashboard git repo root | _(required for dashboard)_ |

## Data Format

### sessions.json

```json
{
  "sessions": [
    {
      "id": "20260324-211211",
      "date": "2026-03-24",
      "startTime": "21:12",
      "endTime": "21:35",
      "duration": 25,
      "actualDuration": 23,
      "task": "write code",
      "status": "complete",
      "note": "finished",
      "energy": -15
    }
  ]
}
```

## File Structure

```
pomodoro/
├── bin/
│   ├── pomodoro.sh      # Main timer script
│   └── dashboard.sh     # Dashboard deployment (optional)
├── assets/
│   └── index.html       # Dashboard template
├── examples/
│   └── integration.sh   # Integration examples
├── data/                # Auto-created on first run
│   ├── current.json     # Running session state
│   └── sessions.json    # All sessions log
├── SKILL.md
└── README.md
```

## Dashboard

Deploy a live stats page:

```bash
export POMODORO_SITE_DIR=~/my-site/pomodoro
export POMODORO_GIT_DIR=~/my-site
./bin/dashboard.sh
```

The dashboard (`assets/index.html`) reads `sessions.json` and shows today's count, total time, and recent sessions.

## Troubleshooting

**Notifications not showing?**
Check: System Preferences > Notifications > Terminal > Allow.

**Auto-completion not working?**
Verify the background process: `ps aux | grep pomodoro.sh`

**Roam sync not working?**
Ensure `ROAM_GRAPH` is set and `bb` (Babashka) is installed: `brew install borkdude/brew/babashka`
