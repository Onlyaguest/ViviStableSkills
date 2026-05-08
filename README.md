# ViviStableSkills

Stable, production-ready skills for AI agents.

## Available Skills

| Skill | Description | Platform |
|-------|------------|----------|
| [pomodoro](./pomodoro/) | AI-powered Pomodoro timer with auto-completion and local logging | macOS |
| [i18n-translator](./i18n-translator/) | Multi-language website translation with AI (Gemini) | all |
| [prompt-cards](./prompt-cards/) | Modular prompt card system with meta prompts, role cards, and workflows | all |
| [github-repo-sync](./github-repo-sync/) | Sync GitHub repos to local disk with scheduled execution | macOS / Linux |
| [github-issue-manager](./github-issue-manager/) | Create GitHub Issues from CLI with templates and labels | all |
| [cleandesktop](./cleandesktop/) | Desktop file organizer - auto-archive by week with CSV logging | macOS / Linux |
| [agora-convoai-quickstart](./agora-convoai-quickstart/) | One-command setup and run for Agora Conversational AI quickstart demo | macOS / Linux |
| [yao-prompt-router](./yao-prompt-router/) | Smart router for 102 Chinese AI prompt templates (yao-open-prompts) | all |

## Quick Start

```bash
git clone https://github.com/Onlyaguest/ViviStableSkills.git
cd ViviStableSkills

# Example: start a pomodoro
cd pomodoro && ./bin/pomodoro.sh start "coding" 25

# Example: translate a website
cd i18n-translator && ./auto-translate.sh ~/my-site "en-US,ja-JP"

# Example: use a prompt card
cd prompt-cards && cat roles/pop-art-web-generator.md

# Example: install yao-prompt-router (standalone, no need to clone this repo)
curl -fsSL https://raw.githubusercontent.com/Onlyaguest/ViviStableSkills/main/yao-prompt-router/install.sh | bash
```

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines on adding new skills.

## License

MIT
