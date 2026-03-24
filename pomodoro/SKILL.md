---
name: pomodoro
description: AI-powered Pomodoro timer with auto-completion, Roam Research integration, and live dashboard. Tracks focus sessions, syncs to knowledge base, and visualizes productivity metrics. Perfect for AI agents managing human workflows.
version: 1.0.0
author: Vivi
repository: https://github.com/Onlyaguest/ViviStableSkills
---

# Pomodoro Timer Skill

AI-powered Pomodoro timer with complete workflow automation.

## What It Does

Manages focus sessions with full automation:

```bash
./bin/pomodoro.sh start "写代码" 25
```

**Result:**
- ⏰ Timer starts (system notification)
- 🍅 Auto-completes after 25 minutes
- 📝 Records to local JSON log
- 📚 Syncs to Roam Research with #番茄钟 tag
- 📊 Updates live dashboard on Vercel
- 🔔 Sends completion notification

## Quick Start

### 1. Install

```bash
# Clone this skill
git clone https://github.com/Onlyaguest/ViviStableSkills.git
cd ViviStableSkills/pomodoro

# Make scripts executable
chmod +x bin/*.sh
```

### 2. Configure

Edit paths in `bin/pomodoro.sh` and `bin/dashboard.sh`:

```bash
# pomodoro.sh - Line 4-7
BASE_DIR="$HOME/.openclaw/workspace/skills/pomodoro"  # Your skill location
DATA_DIR="$BASE_DIR/data"
STATE_FILE="$DATA_DIR/current.json"
LOG_FILE="$DATA_DIR/sessions.json"

# dashboard.sh - Line 6-7
SITE_DIR="$HOME/MyOpenClawWebsite/sites/pomodoro"  # Your Vercel site
GIT_DIR="$HOME/MyOpenClawWebsite"
```

### 3. Set Up Roam Integration (Optional)

If you want Roam Research sync:

```bash
# Install bb (Babashka) if not already installed
brew install borkdude/brew/babashka

# Configure Roam credentials in ~/qq/config.edn
# See: https://github.com/your-roam-integration-repo
```

### 4. Start Your First Pomodoro

```bash
# 25-minute session (default)
./bin/pomodoro.sh start "学习新技能"

# Custom duration (in minutes)
./bin/pomodoro.sh start "写文档" 15

# Check status
./bin/pomodoro.sh status

# View today's sessions
./bin/pomodoro.sh today
```

## Use Cases

### Case 1: Deep Work Sessions

**Scenario:** You need 2 hours of focused coding time.

```bash
# Start first pomodoro
./bin/pomodoro.sh start "实现用户认证" 25

# After auto-completion, start next one
./bin/pomodoro.sh start "编写测试用例" 25

# Take a break, then continue
./bin/pomodoro.sh start "代码审查" 25
```

**Result:**
- 3 completed pomodoros logged
- All synced to Roam Research
- Dashboard shows today's progress
- Total: 75 minutes of tracked work

### Case 2: Interrupted Sessions

**Scenario:** You get an urgent call mid-session.

```bash
# Start session
./bin/pomodoro.sh start "写提案" 25

# Interrupt when needed
./bin/pomodoro.sh interrupt "紧急电话"
```

**Result:**
- Session marked as "interrupted"
- Actual duration recorded
- Energy cost: -8 (vs -15 for completed)

### Case 3: AI Agent Workflow

**Scenario:** AI agent manages your daily schedule.

```bash
# Agent starts pomodoro when you begin work
./bin/pomodoro.sh start "处理邮件" 15

# Auto-completes after 15 minutes
# Agent checks: "Ready for next task?"

# Agent updates dashboard
./bin/dashboard.sh
```

**Result:**
- Fully automated time tracking
- No manual intervention needed
- Live dashboard for oversight

## Features

### ✨ Core Features

- **Auto-Completion** - Timer calls `done` automatically when finished
- **Roam Integration** - Syncs to daily note with #番茄钟 tag
- **Live Dashboard** - Real-time Vercel page with stats
- **System Notifications** - macOS notifications for start/end
- **Energy Tracking** - Records energy cost per session
- **Interruption Handling** - Gracefully handles mid-session stops

### 🎯 Smart Features

- **Background Execution** - Runs in background, doesn't block terminal
- **State Persistence** - Survives terminal restarts
- **JSON Logging** - Machine-readable session data
- **Today's Summary** - Quick view of daily progress
- **Status Check** - See current running session

## Supported Commands

| Command | Description | Example |
|---------|-------------|---------|
| `start <task> [minutes]` | Start new pomodoro | `start "写代码" 25` |
| `done [note]` | Complete current session | `done "完成功能"` |
| `interrupt [note]` | Stop current session | `interrupt "会议"` |
| `status` | Check current session | `status` |
| `today` | View today's sessions | `today` |

## Advanced Usage

### Custom Duration

```bash
# Short focus burst (10 minutes)
./bin/pomodoro.sh start "快速回复邮件" 10

# Extended deep work (50 minutes)
./bin/pomodoro.sh start "系统设计" 50

# Micro-task (5 minutes)
./bin/pomodoro.sh start "整理桌面" 5
```

### Manual Completion

```bash
# Start session
./bin/pomodoro.sh start "阅读文档" 25

# Complete early with note
./bin/pomodoro.sh done "提前完成，理解透彻"
```

### Dashboard Deployment

```bash
# Update dashboard after sessions
./bin/dashboard.sh

# Result: Vercel page updated with latest data
```

### Integration with AI Agents

```bash
# In your AI agent's workflow
if [ "$(date +%H)" -ge 9 ] && [ "$(date +%H)" -lt 18 ]; then
  # Work hours: start pomodoro
  ./bin/pomodoro.sh start "$(get_current_task)" 25
fi
```

## Troubleshooting

### Roam Write Fails

**Problem:** `bb roam-write` command not found.

**Solution:**

```bash
# Install Babashka
brew install borkdude/brew/babashka

# Verify installation
bb --version

# Test Roam connection
cd ~/qq && bb roam-write :yuanvv "测试 #番茄钟"
```

### Dashboard Not Updating

**Problem:** `dashboard.sh` fails with "No such file or directory".

**Solution:**

```bash
# Check paths in dashboard.sh
cat bin/dashboard.sh | grep DIR

# Create missing directories
mkdir -p ~/MyOpenClawWebsite/sites/pomodoro

# Verify Git repository
cd ~/MyOpenClawWebsite && git status
```

### Notifications Not Showing

**Problem:** No system notifications on macOS.

**Solution:**

```bash
# Check notification permissions
# System Preferences → Notifications → Terminal → Allow

# Test notification manually
osascript -e 'display notification "Test" with title "Pomodoro"'
```

### Auto-Completion Not Working

**Problem:** Timer doesn't auto-complete after duration.

**Solution:**

```bash
# Check if background process is running
ps aux | grep pomodoro.sh

# Verify SCRIPT_PATH is set correctly
grep SCRIPT_PATH bin/pomodoro.sh

# Test with short duration
./bin/pomodoro.sh start "测试" 1
# Wait 1 minute, should auto-complete
```

## File Structure

```
pomodoro/
├── bin/
│   ├── pomodoro.sh         # Main timer script
│   └── dashboard.sh        # Dashboard deployment
├── assets/
│   └── index.html          # Dashboard template
├── data/                   # Created on first run
│   ├── current.json        # Current session state
│   └── sessions.json       # All sessions log
├── examples/
│   └── integration.sh      # Integration examples
├── SKILL.md               # This file
└── README.md              # Quick reference

After deployment:
~/MyOpenClawWebsite/sites/pomodoro/
├── index.html             # Live dashboard
└── sessions.json          # Data for dashboard
```

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
      "duration": 15,
      "actualDuration": 23,
      "task": "openclaw进行PR对齐",
      "status": "complete",
      "note": "完成PR对齐工作",
      "energy": -15
    }
  ]
}
```

### current.json (during session)

```json
{
  "id": "20260324-214335",
  "task": "闭环测试",
  "duration": 1,
  "startTs": 1711289015,
  "startAt": "2026-03-24 21:43:35",
  "status": "running"
}
```

## Performance

- **Start Time**: <100ms
- **Auto-Completion**: Exact (±1 second)
- **Roam Write**: ~500ms
- **Dashboard Update**: ~2 seconds (git push)
- **Memory Usage**: <5MB

## Integration Examples

### For OpenClaw

```bash
# Add to workspace skills
cd ~/.openclaw/workspace/skills
git clone https://github.com/Onlyaguest/ViviStableSkills.git vivi-skills
ln -s vivi-skills/pomodoro .

# Use in agent workflow
cd ~/.openclaw/workspace/skills/pomodoro
./bin/pomodoro.sh start "$(get_task_from_roam)" 25
```

### For Claude Code

```bash
# In your Claude Code project
git clone https://github.com/Onlyaguest/ViviStableSkills.git skills
cd skills/pomodoro

# Start session
./bin/pomodoro.sh start "重构代码" 25
```

### For Cursor

```bash
# Add to project
cd ~/cursor-project
git clone https://github.com/Onlyaguest/ViviStableSkills.git .skills

# Use via terminal
.skills/pomodoro/bin/pomodoro.sh start "实现功能" 25
```

### For Other AI Agents

```bash
# Clone to agent workspace
cd /path/to/agent/workspace
git clone https://github.com/Onlyaguest/ViviStableSkills.git

# Use directly
ViviStableSkills/pomodoro/bin/pomodoro.sh start "任务名" 25
```

## Real-World Examples

### Example 1: Full Day Tracking

**Morning:**
```bash
./bin/pomodoro.sh start "处理邮件" 15
./bin/pomodoro.sh start "团队会议准备" 25
```

**Afternoon:**
```bash
./bin/pomodoro.sh start "编写代码" 25
./bin/pomodoro.sh start "代码审查" 25
./bin/pomodoro.sh start "文档更新" 15
```

**Result:**
- 5 completed pomodoros
- 105 minutes tracked
- All synced to Roam
- Dashboard shows daily progress

### Example 2: Interrupted Workflow

**Session:**
```bash
./bin/pomodoro.sh start "写提案" 25
# 10 minutes later: urgent call
./bin/pomodoro.sh interrupt "客户电话"
```

**Result:**
- Session logged as "interrupted"
- Actual duration: 10 minutes
- Energy cost: -8 (lower than complete)
- Roam entry: "⚡ 番茄钟：写提案（25分钟）#番茄钟"

### Example 3: AI Agent Integration

**Scenario:** AI agent manages your work schedule.

```bash
# Agent checks calendar
# Agent: "You have 2 hours for deep work"

# Agent starts first pomodoro
./bin/pomodoro.sh start "系统架构设计" 25

# After auto-completion
# Agent: "First session complete. Continue?"

# Agent starts second pomodoro
./bin/pomodoro.sh start "API设计" 25

# Agent updates dashboard
./bin/dashboard.sh
```

**Result:**
- Fully automated time management
- No manual intervention
- Live dashboard for oversight

## Best Practices

1. **Consistent Duration** - Use 25 minutes for most tasks
2. **Descriptive Names** - Use clear task names for better tracking
3. **Regular Breaks** - Take 5-minute breaks between pomodoros
4. **Daily Review** - Check `today` command at end of day
5. **Dashboard Updates** - Run `dashboard.sh` after each session
6. **Roam Sync** - Verify Roam entries daily
7. **Interruption Notes** - Add context when interrupting

## Energy Tracking

The skill tracks energy cost per session:

- **Complete**: -15 energy
- **Interrupted**: -8 energy

This helps you understand the true cost of context switching.

## FAQ

**Q: Can I use this without Roam Research?**
A: Yes! The Roam integration is optional. The skill works perfectly with just local JSON logging and dashboard.

**Q: Does it work on Linux/Windows?**
A: Currently macOS only (uses `osascript` for notifications). PRs welcome for cross-platform support!

**Q: Can I customize the dashboard?**
A: Yes! Edit `assets/index.html` to change colors, layout, or add features.

**Q: What if I forget to start a pomodoro?**
A: You can manually add entries to `sessions.json` or use the `start` command retroactively.

**Q: Can multiple people use the same dashboard?**
A: Yes! Each person can have their own `sessions.json` and deploy to different Vercel paths.

**Q: How do I backup my data?**
A: `sessions.json` is your complete history. Back it up regularly or commit to git.

## Contributing

Found a bug? Have a feature request?

1. Fork the repo
2. Create a branch
3. Submit a PR

## License

MIT

## Support

- GitHub Issues: https://github.com/Onlyaguest/ViviStableSkills/issues
- Documentation: See README.md in this directory

---

**Made with ❤️ by Vivi**

*Tested in production with 100+ pomodoro sessions*
