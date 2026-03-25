# GitHub Issue Manager

Create and manage GitHub Issues from the command line with structured templates.

## Quick Start

```bash
export GITHUB_TOKEN="ghp_your_token_here"

# Preview (dry run)
./create-issue.sh --repo owner/repo --title "Add feature X" --type feature --dry-run

# Create issue
./create-issue.sh --repo owner/repo --title "Add feature X" --type feature --priority high
```

## Commands

| Option | Description |
|--------|-------------|
| `--repo OWNER/REPO` | Target repository (required) |
| `--title TEXT` | Issue title (required) |
| `--type TYPE` | `feature` / `bug` / `enhancement` |
| `--priority LEVEL` | `high` / `medium` / `low` |
| `--phase N` | Phase: `1` / `2` / `3` |
| `--body TEXT` | Custom body text |
| `--labels L1,L2` | Extra labels |
| `--template FILE` | Custom template |
| `--dry-run` | Preview without creating |

## Requirements

- `GITHUB_TOKEN` env var ([get one here](https://github.com/settings/tokens))
- `jq` (`brew install jq`)
- `curl`

## Full Documentation

See [SKILL.md](./SKILL.md) for complete reference.
