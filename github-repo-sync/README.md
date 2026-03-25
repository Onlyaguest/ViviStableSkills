# github-repo-sync

Sync a list of GitHub repositories to local disk. Maintain `repos.txt`, run one command.

## Quick Start

```bash
# Copy config
cp .env.example .env

# Edit repo list
vim repos.txt

# Sync all repos
python3 main.py run

# Preview without executing
python3 main.py run --dry-run
```

## Repo List Format

One repo per line in `repos.txt`:

```txt
owner/repo
https://github.com/owner/repo.git
git@github.com:owner/repo.git
```

## Commands

| Command | Description |
|---------|-------------|
| `run` | Clone missing repos, pull updates for existing |
| `run --dry-run` | Preview planned actions |
| `run --only owner/repo` | Sync specific repos only |
| `install-launch-agent` | Set up macOS scheduled sync |
| `uninstall-launch-agent` | Remove scheduled sync |

## Sync Behavior

- Missing directory: `git clone`
- Existing repo: `git fetch --all --prune` + `git pull --ff-only`
- Dirty worktree: skip pull (protects local changes)
- Detached HEAD / no upstream: skip pull

## Full Documentation

See [SKILL.md](./SKILL.md) for complete reference.
