---
name: github-issue-manager
description: Create and manage GitHub Issues from the command line with templates and label automation.
version: 1.1.0
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

## Issue Lifecycle & Closing Workflow

### Issue Type Classification

Issues fall into two categories based on their nature and who handles closure:

#### Functional Issues (功能类)

Issues that require implementation work by the development team.

**Types:**
- `feature` - New functionality to be implemented
- `bug` - Broken functionality to be fixed
- `enhancement` - Improvements to existing features

**Closing responsibility:** Development team (e.g., ems-crew)  
**Closing timing:** After implementation is complete and tested  
**State reason:** `completed`

**Examples:**
- "Add AI classification for Roam blocks"
- "Fix database write issue"
- "Improve Dashboard UI/UX"

#### Administrative Issues (管理类)

Issues that don't require implementation, closed for coordination/management reasons.

**Types:**
- `duplicate` - Already covered by another issue
- `invalid` - Not a valid issue or request
- `wontfix` - Decided not to implement
- `documentation` - Documentation-only changes

**Closing responsibility:** Project coordinator (e.g., 元虾虾)  
**Closing timing:** Immediately when identified  
**State reason:** `not_planned`

**Examples:**
- "Issue #10 (duplicate of Issue #9)"
- "Invalid feature request"
- "Out of scope for current phase"

### Closing Workflow

#### For Functional Issues (by development team)

```bash
# Close when implementation is complete
curl -X PATCH \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/OWNER/REPO/issues/NUMBER \
  -d '{"state": "closed", "state_reason": "completed"}'
```

**Best practices:**
- Close only after implementation + testing + verification
- Reference the closing commit in a comment
- Update the issue with final status before closing

#### For Administrative Issues (by coordinator)

```bash
# Close duplicate/invalid/wontfix issues
curl -X PATCH \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/OWNER/REPO/issues/NUMBER \
  -d '{"state": "closed", "state_reason": "not_planned"}'
```

**Best practices:**
- Add a comment explaining why (e.g., "Duplicate of #9")
- Close immediately to keep the issue list clean
- Link to the related issue if applicable

### When to Close Issues

| Scenario | Who Closes | When | State Reason |
|----------|------------|------|--------------|
| Feature implemented & tested | Dev team | After verification | `completed` |
| Bug fixed & verified | Dev team | After testing | `completed` |
| Enhancement deployed | Dev team | After deployment | `completed` |
| Duplicate identified | Coordinator | Immediately | `not_planned` |
| Invalid request | Coordinator | Immediately | `not_planned` |
| Won't implement | Coordinator | After decision | `not_planned` |
| Documentation only | Either | After merge | `completed` |

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
