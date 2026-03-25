---
name: github-issue-manager
description: Create and manage GitHub Issues from the command line with templates and label automation.
version: 1.0.0
author: Vivi
tags: [github, issues, automation, project-management]
platforms: [all]
dependencies:
  - bash
  - curl
  - jq
---

# GitHub Issue Manager Skill

Create structured GitHub Issues from the command line with templates, automatic labeling, and dry-run preview.

## Features

- Issue templates (feature, bug, enhancement)
- Automatic label management (type, priority, phase)
- Dry-run preview before creating
- Custom body text and extra labels
- Works with any GitHub repo (public or private)

## Quick Start

```bash
export GITHUB_TOKEN="ghp_your_token_here"

# Preview an issue (dry run)
./create-issue.sh --repo owner/repo --title "New feature" --type feature --dry-run

# Create for real
./create-issue.sh --repo owner/repo --title "New feature" --type feature --priority high
```

## Command Reference

```bash
./create-issue.sh [options]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--repo OWNER/REPO` | Target repository (required) | — |
| `--title TEXT` | Issue title (required) | — |
| `--type TYPE` | `feature` / `bug` / `enhancement` | `feature` |
| `--priority LEVEL` | `high` / `medium` / `low` | `medium` |
| `--phase N` | Phase number: `1` / `2` / `3` | _(none)_ |
| `--body TEXT` | Custom body (overrides template) | _(from template)_ |
| `--labels L1,L2` | Extra labels, comma-separated | _(none)_ |
| `--template FILE` | Custom JSON template file | _(auto by type)_ |
| `--dry-run` | Preview without creating | `false` |

## Configuration

| Env Variable | Required | Description |
|-------------|----------|-------------|
| `GITHUB_TOKEN` | Yes | GitHub Personal Access Token with `repo` scope |

Get a token at: https://github.com/settings/tokens

## Label Convention

### Type (one required)

| Label | Meaning |
|-------|---------|
| `feature` | New functionality |
| `bug` | Something broken |
| `enhancement` | Improve existing feature |

### Priority (optional)

`priority-high` · `priority-medium` · `priority-low`

### Phase (optional)

`phase-1` · `phase-2` · `phase-3`

## Templates

Templates are in `templates/` as JSON files:

```json
{
  "title": "Replaced by --title",
  "body": "Markdown body with sections",
  "labels": ["type-label"]
}
```

Built-in: `feature.json`, `bug.json`, `enhancement.json`

Create custom templates and pass via `--template path/to/custom.json`.

## File Structure

```
github-issue-manager/
├── create-issue.sh        # CLI entry point
├── templates/
│   ├── feature.json       # Feature request template
│   ├── bug.json           # Bug report template
│   └── enhancement.json   # Enhancement template
├── examples/
│   └── EXAMPLES.md        # Usage examples
├── SKILL.md
└── README.md
```

## Security

- **Never hardcode tokens** in scripts or commit them to git
- Use `GITHUB_TOKEN` environment variable
- Rotate tokens regularly (recommended: every 90 days)
- Use minimum required permissions

## Troubleshooting

**401 Unauthorized?**
Check `echo $GITHUB_TOKEN` — ensure it's set and not expired.

**404 Not Found?**
Verify repo name (`owner/repo`) and that your token has access to the repo.

**jq: command not found?**
Install jq: `brew install jq` (macOS) or `apt install jq` (Linux).

**JSON parse error?**
Use `--dry-run` to inspect the generated JSON before creating.
