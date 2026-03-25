---
name: github-repo-sync
description: Sync a plain-text list of GitHub repositories to local disk with optional macOS scheduled execution.
version: 1.0.0
author: Vivi
tags: [git, sync, automation, github]
platforms: [macos, linux]
dependencies:
  - python3
  - git
---

# github-repo-sync Skill

Maintain a `repos.txt` file, run one command to clone or update all listed repositories.

## Features

- Clone missing repos, fast-forward pull existing ones
- Plain-text repo list (owner/repo, HTTPS, or SSH formats)
- Safe sync: skips dirty worktrees, detached HEAD, missing upstream
- macOS launchd integration for scheduled sync
- Dry-run preview for all operations
- Zero external Python dependencies

## Quick Start

```bash
cp .env.example .env
vim repos.txt        # Add your repos
python3 main.py run
```

## Command Reference

### run

```bash
python3 main.py run [--repo-list FILE] [--root-dir DIR] [--only OWNER/REPO] [--dry-run]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--repo-list` | Path to repo list file | `repos.txt` |
| `--root-dir` | Local root for synced repos | `~/Code/github-sync` |
| `--only` | Limit to specific repos (repeatable) | _(all)_ |
| `--dry-run` | Preview without executing | `false` |
| `--git-bin` | Git executable path | `git` |

### install-launch-agent (macOS only)

```bash
python3 main.py install-launch-agent [--interval-minutes N] [--label LABEL] [--dry-run]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--interval-minutes` | Sync interval | `60` |
| `--label` | launchd label | `com.example.github-repo-sync` |
| `--dry-run` | Preview plist only | `false` |

### uninstall-launch-agent

```bash
python3 main.py uninstall-launch-agent [--label LABEL] [--dry-run]
```

## Configuration

All via `.env` or environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `REPO_LIST_FILE` | Repo list path | `repos.txt` |
| `SYNC_ROOT_DIR` | Local sync root | `~/Code/github-sync` |
| `GIT_BIN` | Git executable | `git` |
| `SCHEDULE_INTERVAL_MINUTES` | Launchd interval (min) | `60` |
| `LAUNCH_AGENT_LABEL` | Launchd label | `com.example.github-repo-sync` |

## Sync Strategy

| Scenario | Action |
|----------|--------|
| Directory missing | `git clone` |
| Clean worktree + has upstream | `git fetch --all --prune` + `git pull --ff-only` |
| Dirty worktree | Skip pull (protect local changes) |
| Detached HEAD | Skip pull |
| No upstream on current branch | Skip pull |
| Not a git repo | Skip entirely |

## File Structure

```
github-repo-sync/
├── main.py           # CLI entry point
├── repos.txt         # Repo list (user-maintained)
├── .env.example      # Configuration template
├── logs/             # launchd logs (auto-created)
├── SKILL.md
└── README.md
```

## Troubleshooting

**Private repos failing?**
Ensure your SSH key or Git credential helper is configured for the repo host.

**Repos showing "skipped"?**
Expected when: local changes exist, detached HEAD, or no upstream set. This protects your work.

**Want a different list file?**
Set `REPO_LIST_FILE` in `.env` or pass `--repo-list /path/to/file.txt`.
