---
name: obsidian-note-hub
description: Unified entrypoint for Obsidian note operations such as cleanup, merge, lint/fix, meeting archive, daily rollover, and docs sync. Use when the user wants one command surface over an existing notes-tools repo instead of calling many atomic scripts by hand.
version: 1.0.0
author: Vivi
tags: [obsidian, notes, workflow, archive, orchestrator]
platforms: [all]
dependencies:
  - python3
---

# obsidian-note-hub

One front door for a mature note-ops tool family. This skill dispatches into an existing notes-tools repo and gives humans or agents a stable command surface for common Obsidian maintenance workflows.

## Use this skill when

- The user says "帮我处理笔记库" but does not want 10 separate scripts
- The repo already has many note tools and needs a stable orchestrator entrypoint
- The team wants one trigger surface for archive / cleanup / merge / lint / fix flows
- An agent needs to validate mappings before running a vault-changing command

## Workflow

1. Run `python3 main.py list` to inspect the public command surface.
2. Run `python3 main.py check` after setting `REPO_ROOT` and `VAULT_ROOT`.
3. Start with dry-run flows when a command can change vault contents.
4. Only then run the real dispatch command against the notes-tools repo.

## Commands

Inspect available commands:

```bash
python3 main.py list
```

Validate config and dispatch map:

```bash
REPO_ROOT=/absolute/path/to/MyNotesTools \
VAULT_ROOT=/absolute/path/to/ObsidianVault \
python3 main.py check
```

Safe dry-run examples:

```bash
REPO_ROOT=/absolute/path/to/MyNotesTools \
VAULT_ROOT=/absolute/path/to/ObsidianVault \
python3 main.py meeting-archive --dry-run
```

```bash
REPO_ROOT=/absolute/path/to/MyNotesTools \
VAULT_ROOT=/absolute/path/to/ObsidianVault \
python3 main.py docs-sync --summary "docs sync" --dry-run --skip-moc
```

## Inputs and outputs

- Input: `.env` config, existing notes-tools repo, existing Obsidian vault
- Output: dispatched runs of downstream note tools, or config / mapping validation output in terminal

## Validation

Minimum validation commands:

```bash
python3 main.py list
```

```bash
REPO_ROOT=/absolute/path/to/MyNotesTools VAULT_ROOT=/absolute/path/to/ObsidianVault python3 main.py check
```

## Constraints

- This is an orchestrator, not a fully bundled copy of every downstream note tool
- Real commands depend on the target notes-tools repo staying intact
- Prefer dry-run variants before any vault-mutating workflow
- `docs-sync` may need `--skip-moc` if the target vault does not have the Atlas MOC file
