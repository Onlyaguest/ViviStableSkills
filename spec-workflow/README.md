# spec-workflow

Stable scaffold for specification-driven project work. It exposes the hidden `.spec-workflow` pattern as a reusable CLI: initialize the workflow directories, generate steering docs, and create a new spec folder from templates.

## Commands

Check bundled templates:

```bash
python3 main.py check
```

Initialize a project:

```bash
python3 main.py init --root /absolute/path/to/project --project-name "Energy OS" --author Developer_Lead
```

Create a feature spec:

```bash
python3 main.py new-spec --root /absolute/path/to/project --name "dashboard sync" --author Developer_Lead
```

## Validation

Minimum validation:

```bash
python3 main.py check
python3 -m py_compile main.py
```

Recommended end-to-end validation:

```bash
python3 main.py init --root /tmp/spec-demo --project-name "Spec Demo" --author Developer_Lead
python3 main.py new-spec --root /tmp/spec-demo --name "dashboard sync" --author Developer_Lead
```

## What it creates

- `.spec-workflow/approvals`
- `.spec-workflow/archive`
- `.spec-workflow/specs`
- `.spec-workflow/steering`
- `.spec-workflow/templates`
- `.spec-workflow/user-templates`
- steering docs: `product.md`, `tech.md`, `structure.md`
- spec docs: `requirements.md`, `design.md`, `tasks.md`
