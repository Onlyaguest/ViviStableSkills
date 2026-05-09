---
name: spec-workflow
description: Initialize and use a specification-driven workflow with steering docs, reusable templates, and per-feature spec folders. Use when a project needs a structured path from product intent to requirements, design, and tasks before coding.
version: 1.0.0
author: Vivi
tags: [spec, workflow, planning, scaffolding]
platforms: [all]
dependencies:
  - python3
---

# spec-workflow

Turn the hidden `.spec-workflow` pattern into a stable public skill. This skill gives projects a predictable place for product steering, technical steering, structure conventions, approvals, archive history, and per-feature specs.

## Use this skill when

- A project keeps reinventing how to go from idea -> requirements -> design -> tasks
- The team wants a visible, repeatable spec workflow before coding starts
- You want a stable scaffold instead of manually copying `.spec-workflow` directories around
- A project needs custom templates but should still start from a default baseline

## Workflow

1. Run `check` to confirm the bundled templates exist.
2. Run `init` in a project root to create `.spec-workflow` and steering docs.
3. Run `new-spec` to create a feature-level spec folder with requirements/design/tasks docs.
4. Override defaults later through `.spec-workflow/user-templates/`.

## Commands

Check the bundle:

```bash
python3 main.py check
```

Initialize a workflow:

```bash
python3 main.py init --root /absolute/path/to/project --project-name "Energy OS" --author Developer_Lead
```

Create a new feature spec:

```bash
python3 main.py new-spec --root /absolute/path/to/project --name "dashboard sync" --author Developer_Lead
```

## Inputs and outputs

- Input: project root, project name, feature name, bundled templates, optional user template overrides
- Output: initialized `.spec-workflow` tree plus generated steering docs and per-feature spec docs

## Validation

Minimum validation commands:

```bash
python3 main.py check
```

```bash
python3 -m py_compile main.py
```

Recommended end-to-end validation:

```bash
python3 main.py init --root /tmp/spec-demo --project-name "Spec Demo" --author Developer_Lead
python3 main.py new-spec --root /tmp/spec-demo --name "dashboard sync" --author Developer_Lead
```

## Constraints

- This is a scaffold and template workflow, not an opinionated project manager
- Template quality still matters; generated docs are starting points, not finished specs
- `new-spec` expects the project to be initialized first
