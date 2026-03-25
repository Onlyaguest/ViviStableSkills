# ViviStableSkills

Stable, production-ready skills for AI agents.

## Available Skills

| Skill | Description | Platform |
|-------|------------|----------|
| [pomodoro](./pomodoro/) | AI-powered Pomodoro timer with auto-completion and local logging | macOS |
| [i18n-translator](./i18n-translator/) | Multi-language website translation with AI (Gemini) | all |
| [github-repo-sync](./github-repo-sync/) | Sync GitHub repos to local disk with scheduled execution | macOS / Linux |

## Quick Start

```bash
git clone https://github.com/Onlyaguest/ViviStableSkills.git
cd ViviStableSkills

# Example: start a pomodoro
cd pomodoro && ./bin/pomodoro.sh start "coding" 25

# Example: translate a website
cd i18n-translator && ./auto-translate.sh ~/my-site "en-US,ja-JP"
```

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines on adding new skills.

## License

MIT
