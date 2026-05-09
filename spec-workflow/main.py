from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path


WORKFLOW_DIRS = ["approvals", "archive", "specs", "steering", "templates", "user-templates"]
STEERING_TEMPLATES = {
    "product.md": "product-template.md",
    "tech.md": "tech-template.md",
    "structure.md": "structure-template.md",
}
SPEC_TEMPLATES = {
    "requirements.md": "requirements-template.md",
    "design.md": "design-template.md",
    "tasks.md": "tasks-template.md",
}


def _bundle_dir() -> Path:
    return Path(__file__).resolve().parent / "bundle"


def _workflow_root(root: Path) -> Path:
    return root / ".spec-workflow"


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip()).strip("-").lower()
    return slug or "unnamed-spec"


def _render_template(path: Path, values: dict[str, str]) -> str:
    text = path.read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace(f"{{{{{key}}}}}", value)
    return text


def _write_if_needed(path: Path, content: str, force: bool) -> bool:
    if path.exists() and not force:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def _ensure_bundle() -> tuple[Path, Path]:
    bundle = _bundle_dir()
    templates = bundle / "templates"
    user_templates = bundle / "user-templates"
    if not templates.exists():
        raise FileNotFoundError(f"Missing bundled templates: {templates}")
    return templates, user_templates


def run_check(root: Path | None) -> int:
    templates, user_templates = _ensure_bundle()
    print(f"OK: bundle/templates -> {templates}")
    print(f"OK: bundle/user-templates -> {user_templates}")
    if root is None:
        print("INFO: no --root provided; bundle check only")
        return 0

    workflow = _workflow_root(root)
    print(f"Target root: {root}")
    if not workflow.exists():
        print(f"WARN: workflow not initialized -> {workflow}")
        return 0

    missing = [name for name in WORKFLOW_DIRS if not (workflow / name).exists()]
    if missing:
        print("WARN: missing workflow directories:")
        for name in missing:
            print(f"- {name}")
    else:
        print("OK: workflow directories complete")

    steering_missing = [name for name in STEERING_TEMPLATES if not (workflow / "steering" / name).exists()]
    if steering_missing:
        print("WARN: missing steering docs:")
        for name in steering_missing:
            print(f"- {name}")
    else:
        print("OK: steering docs present")
    return 0


def run_init(root: Path, project_name: str, author: str, force: bool) -> int:
    templates, user_templates = _ensure_bundle()
    workflow = _workflow_root(root)
    created: list[str] = []

    for name in WORKFLOW_DIRS:
        path = workflow / name
        path.mkdir(parents=True, exist_ok=True)
        created.append(f"dir {path}")

    values = {
        "projectName": project_name,
        "featureName": project_name,
        "date": date.today().isoformat(),
        "author": author,
    }
    for out_name, template_name in STEERING_TEMPLATES.items():
        content = _render_template(templates / template_name, values)
        if _write_if_needed(workflow / "steering" / out_name, content, force):
            created.append(f"file {workflow / 'steering' / out_name}")

    for template_name in templates.glob("*.md"):
        target = workflow / "templates" / template_name.name
        if _write_if_needed(target, template_name.read_text(encoding="utf-8"), force):
            created.append(f"file {target}")

    readme = user_templates / "README.md"
    if readme.exists():
        target = workflow / "user-templates" / "README.md"
        if _write_if_needed(target, readme.read_text(encoding="utf-8"), force):
            created.append(f"file {target}")

    print(f"Initialized: {workflow}")
    print(f"Project: {project_name}")
    for item in created:
        print(f"- {item}")
    return 0


def run_new_spec(root: Path, name: str, project_name: str, author: str, force: bool) -> int:
    _ensure_bundle()
    workflow = _workflow_root(root)
    templates_dir = workflow / "user-templates"
    defaults_dir = workflow / "templates"
    if not defaults_dir.exists():
        raise FileNotFoundError(f"Workflow templates not found: {defaults_dir}. Run init first.")

    slug = _slugify(name)
    spec_dir = workflow / "specs" / slug
    values = {
        "projectName": project_name,
        "featureName": name,
        "date": date.today().isoformat(),
        "author": author,
    }
    written: list[str] = []
    for out_name, template_name in SPEC_TEMPLATES.items():
        source = templates_dir / template_name
        if not source.exists():
            source = defaults_dir / template_name
        content = _render_template(source, values)
        if _write_if_needed(spec_dir / out_name, content, force):
            written.append(str(spec_dir / out_name))

    print(f"Created spec: {spec_dir}")
    for item in written:
        print(f"- {item}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="spec-workflow: scaffold and initialize a hidden .spec-workflow into a stable reusable workflow"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser("check", help="validate bundled templates and optionally a target root")
    check_parser.add_argument("--root", help="project root to inspect")

    init_parser = subparsers.add_parser("init", help="initialize .spec-workflow in a target project root")
    init_parser.add_argument("--root", required=True, help="project root")
    init_parser.add_argument("--project-name", required=True, help="project name")
    init_parser.add_argument("--author", default="unknown", help="document author")
    init_parser.add_argument("--force", action="store_true", help="overwrite existing generated files")

    spec_parser = subparsers.add_parser("new-spec", help="create a new spec folder from templates")
    spec_parser.add_argument("--root", required=True, help="project root")
    spec_parser.add_argument("--name", required=True, help="feature/spec name")
    spec_parser.add_argument("--project-name", default="", help="project name override")
    spec_parser.add_argument("--author", default="unknown", help="document author")
    spec_parser.add_argument("--force", action="store_true", help="overwrite existing generated files")

    args = parser.parse_args()

    if args.command == "check":
        root = Path(args.root).expanduser().resolve() if args.root else None
        return run_check(root)

    if args.command == "init":
        return run_init(
            Path(args.root).expanduser().resolve(),
            args.project_name,
            args.author,
            args.force,
        )

    if args.command == "new-spec":
        root = Path(args.root).expanduser().resolve()
        project_name = args.project_name or root.name
        return run_new_spec(root, args.name, project_name, args.author, args.force)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
