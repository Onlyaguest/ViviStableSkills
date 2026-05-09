# obsidian-note-hub

Stable orchestrator skill for Obsidian note workflows. It gives one command surface for archive, cleanup, merge, lint/fix, meeting archive, daily rollover, and docs sync flows that already live inside a notes-tools repo.

## What this skill is

- A unified CLI entrypoint over an existing notes-tools workspace
- A stable trigger surface for humans and agents
- An audit-friendly wrapper with a no-side-effect `check` command

## What this skill is not

- Not a full copy of every downstream note tool
- Not a replacement for the underlying notes-tools repo

## Install

```bash
cp .env.example .env
```

Set:

- `REPO_ROOT` -> your `MyNotesTools` repo root
- `VAULT_ROOT` -> your Obsidian vault root

## Commands

Preview available commands:

```bash
python3 main.py list
```

Validate config and task mappings:

```bash
REPO_ROOT=/absolute/path/to/MyNotesTools \
VAULT_ROOT=/absolute/path/to/ObsidianVault \
python3 main.py check
```

Common flows:

```bash
python3 main.py clean -- --apply
python3 main.py inbox-clean
python3 main.py merge-ai --apply
python3 main.py lint
python3 main.py meeting-archive --dry-run
python3 main.py daily-rollover --dry-run
python3 main.py docs-sync --summary "docs sync" --dry-run
```

## Validation

Minimum validation:

```bash
python3 main.py list
REPO_ROOT=/absolute/path/to/MyNotesTools VAULT_ROOT=/absolute/path/to/ObsidianVault python3 main.py check
```

Recommended review-safe dry run:

```bash
REPO_ROOT=/absolute/path/to/MyNotesTools VAULT_ROOT=/absolute/path/to/ObsidianVault python3 main.py docs-sync --summary "docs sync" --dry-run --skip-moc
```

## Notes

- `list` is side-effect free and does not require config.
- `check` validates `REPO_ROOT`, all mapped task entrypoints, and optionally `VAULT_ROOT` / `MOC_TOOL_GUIDE`.
- `docs-sync --dry-run` can be paired with `--skip-moc` when the target vault does not keep the Atlas MOC file.
- Most real commands dispatch into the underlying notes-tools repo, so correctness depends on that repo staying available.
