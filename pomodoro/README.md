# Pomodoro Timer Skill

AI-powered Pomodoro timer with auto-completion, Roam Research integration, and live dashboard.

## Quick Start

```bash
# Install
git clone https://github.com/Onlyaguest/ViviStableSkills.git
cd ViviStableSkills/pomodoro
chmod +x bin/*.sh

# Start a 25-minute session
./bin/pomodoro.sh start "写代码" 25

# Check status
./bin/pomodoro.sh status

# View today's sessions
./bin/pomodoro.sh today

# Update dashboard
./bin/dashboard.sh
```

## Features

- ⏰ **Auto-Completion** - Timer finishes automatically
- 📝 **Local Logging** - JSON session data
- 📚 **Roam Integration** - Syncs with #番茄钟 tag
- 📊 **Live Dashboard** - Vercel-hosted stats
- 🔔 **Notifications** - macOS system alerts
- ⚡ **Energy Tracking** - Records focus cost

## Commands

| Command | Description |
|---------|-------------|
| `start <task> [min]` | Start new pomodoro |
| `done [note]` | Complete current session |
| `interrupt [note]` | Stop current session |
| `status` | Check current session |
| `today` | View today's sessions |

## Configuration

Edit paths in `bin/pomodoro.sh` and `bin/dashboard.sh`:

```bash
# Your skill location
BASE_DIR="$HOME/.openclaw/workspace/skills/pomodoro"

# Your Vercel site
SITE_DIR="$HOME/MyOpenClawWebsite/sites/pomodoro"
```

## Requirements

- macOS (for notifications)
- Babashka (optional, for Roam sync)
- Git (for dashboard deployment)

## Documentation

See [SKILL.md](./SKILL.md) for complete documentation.

## Examples

```bash
# Deep work session
./bin/pomodoro.sh start "系统设计" 25

# Quick task
./bin/pomodoro.sh start "回复邮件" 10

# Interrupted session
./bin/pomodoro.sh start "写文档" 25
./bin/pomodoro.sh interrupt "紧急会议"
```

## Data Format

Sessions are stored in `data/sessions.json`:

```json
{
  "sessions": [
    {
      "id": "20260324-211211",
      "date": "2026-03-24",
      "task": "写代码",
      "duration": 25,
      "actualDuration": 25,
      "status": "complete",
      "energy": -15
    }
  ]
}
```

## Dashboard

Live dashboard shows:
- Today's pomodoro count
- Total time tracked
- Recent sessions
- Energy cost

Deploy with: `./bin/dashboard.sh`

## Integration

Works with:
- OpenClaw
- Claude Code
- Cursor
- Any AI agent with shell access

## License

MIT

## Support

- Full docs: [SKILL.md](./SKILL.md)
- Issues: https://github.com/Onlyaguest/ViviStableSkills/issues

---

**Made with ❤️ by Vivi**
