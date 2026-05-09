from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path


DEFAULT_TASKS = {
    "archive": "tasks/quick-archive/main.py",
    "card-merge": "tasks/card-merge/main.py",
    "template": "tasks/template-workflow/main.py",
    "clean": "tasks/vault-workflow/main.py",
    "inbox-clean": "tasks/inbox-clean/main.py",
    "merge": "tasks/merge-notes/main.py",
    "merge-ai": "tasks/merge-ai/main.py",
    "name-stager": "tasks/name-stager/main.py",
    "note-fixer": "tasks/note-fixer/main.py",
    "project-fixer": "tasks/project-fixer/main.py",
    "solution-fixer": "tasks/solution-fixer/main.py",
    "scan": "tasks/vault-move-planner/main.py",
    "prettify": "tasks/who-link-prettifier/main.py",
    "split": "tasks/card-pack-splitter/main.py",
    "share-outline": "tasks/share-outline-builder/main.py",
}

LINTER_TASKS = {
    "meeting": "tasks/meeting-sum-linter/main.py",
    "who": "tasks/who-linter/main.py",
    "card": "tasks/card-linter/main.py",
    "daily": "tasks/daily-linter/main.py",
}

FIXER_TASKS = {
    "meeting": "tasks/meeting-sum-fixer/main.py",
    "who": "tasks/who-fixer/main.py",
    "card": "tasks/card-fixer/main.py",
    "daily": "tasks/daily-fixer/main.py",
}

SPECIAL_COMMANDS = {"move"}
ORDERED_TYPES = ["meeting", "who", "card", "daily"]
NORMALIZE_TASKS = {
    "meeting": "tasks/gemini-meeting-sum-normalizer/main.py",
    "who": "tasks/gemini-person-who-normalizer/main.py",
    "card": "tasks/gemini-import-cleaner/main.py",
}
NORMALIZE_TYPES = ["who", "meeting", "card"]
MEETING_NAME_RE = re.compile(r"^\d{4}-\d{2}-\d{2} Meeting-.+\.md$")


def _eprint(msg: str) -> None:
    print(msg, file=sys.stderr)


def _load_dotenv_if_present(dotenv_path: Path) -> None:
    if not dotenv_path.exists():
        return
    try:
        raw = dotenv_path.read_text(encoding="utf-8")
    except Exception:
        return
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("export "):
            stripped = stripped[len("export ") :].strip()
        if "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key and key not in os.environ:
            os.environ[key] = value


def _parse_task_map(raw: str | None) -> dict[str, str]:
    mapping = dict(DEFAULT_TASKS)
    if not raw:
        return mapping
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if ":" not in chunk:
            continue
        key, value = chunk.split(":", 1)
        key = key.strip()
        value = value.strip()
        if key and value:
            mapping[key] = value
    return mapping


def _resolve_repo_root(raw: str | None) -> Path:
    if not raw:
        raise ValueError("Missing config: REPO_ROOT")
    return Path(raw).expanduser().resolve()


def _resolve_task_path(repo_root: Path, raw: str) -> Path:
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = repo_root / path
    return path


def _run_command(cmd: list[str]) -> int:
    print("==> " + " ".join(cmd))
    proc = subprocess.run(cmd, env=os.environ.copy())
    return proc.returncode


def _list_commands(tasks: dict[str, str]) -> None:
    print("Commands:")
    for name in sorted(tasks.keys()):
        print(f"- {name}")
    print("- check")
    print("- lint")
    print("- fix")
    print("- normalize")
    print("- meeting-archive")
    print("- daily-rollover")
    print("- docs-sync")
    print("- move")
    print("- run")


def _validate_task_map(repo_root: Path, task_map: dict[str, str]) -> list[str]:
    missing: list[str] = []
    for name, raw in sorted(task_map.items()):
        task_main = _resolve_task_path(repo_root, raw)
        if not task_main.exists():
            missing.append(f"{name}: {task_main}")
    return missing


def _run_check(task_map: dict[str, str]) -> int:
    repo_root_raw = os.getenv("REPO_ROOT")
    if not repo_root_raw:
        _eprint("Missing config: REPO_ROOT")
        return 2
    try:
        repo_root = _resolve_repo_root(repo_root_raw)
    except ValueError as exc:
        _eprint(str(exc))
        return 2
    if not repo_root.exists():
        _eprint(f"REPO_ROOT not found: {repo_root}")
        return 2

    check_map = dict(task_map)
    check_map.update(LINTER_TASKS)
    check_map.update(FIXER_TASKS)
    check_map.update(NORMALIZE_TASKS)

    missing = _validate_task_map(repo_root, check_map)
    if missing:
        _eprint("Missing task entrypoints:")
        for item in missing:
            _eprint(f"- {item}")
        return 2

    print(f"OK: REPO_ROOT -> {repo_root}")
    print(f"OK: mapped entrypoints -> {len(check_map)}")

    vault_root_raw = os.getenv("VAULT_ROOT")
    if not vault_root_raw:
        print("WARN: VAULT_ROOT not set; dispatch validation passed, vault-dependent flows were not checked")
        return 0

    vault_root = Path(vault_root_raw).expanduser().resolve()
    if not vault_root.exists():
        _eprint(f"VAULT_ROOT not found: {vault_root}")
        return 2

    print(f"OK: VAULT_ROOT -> {vault_root}")
    moc_path_raw = os.getenv("MOC_TOOL_GUIDE", "3_Atlas/MOC-系统工具与协议总览.md")
    moc_path = Path(moc_path_raw).expanduser()
    if not moc_path.is_absolute():
        moc_path = vault_root / moc_path
    moc_path = moc_path.resolve()
    if moc_path.exists():
        print(f"OK: MOC_TOOL_GUIDE -> {moc_path}")
    else:
        print(f"WARN: MOC_TOOL_GUIDE not found -> {moc_path}")
    return 0


def _ensure_vault_root_arg(args: list[str], vault_root: str | None) -> list[str]:
    if not vault_root:
        return args
    if "--vault-root" in args:
        return args
    return args + ["--vault-root", vault_root]


def _run_group(
    repo_root: Path,
    task_map: dict[str, str],
    types: list[str],
    extra_args: list[str],
    vault_root: str | None,
    dry_run: bool,
) -> int:
    python = sys.executable
    for name in types:
        task_path = task_map.get(name)
        if not task_path:
            _eprint(f"Unknown task type: {name}")
            return 2
        task_main = _resolve_task_path(repo_root, task_path)
        if not task_main.exists():
            _eprint(f"Task not found: {task_main}")
            return 2
        args = list(extra_args)
        args = _ensure_vault_root_arg(args, vault_root)
        if dry_run and "--dry-run" not in args:
            args.append("--dry-run")
        code = _run_command([python, str(task_main)] + args)
        if code != 0:
            return code
    return 0


def _delete_pack_files(
    vault_root: Path,
    draft_dir: str,
    pack_glob: str,
    dry_run: bool,
) -> int:
    pack_dir = Path(draft_dir).expanduser()
    if not pack_dir.is_absolute():
        pack_dir = vault_root / pack_dir
    pack_dir = pack_dir.resolve()
    if not pack_dir.exists():
        _eprint(f"Draft dir not found: {pack_dir}")
        return 2
    deleted = 0
    for path in pack_dir.rglob(pack_glob):
        if not path.is_file():
            continue
        if dry_run:
            print(f"DRY-RUN: delete {path}")
            continue
        path.unlink()
        deleted += 1
    if not dry_run:
        print(f"Deleted packs: {deleted}")
    return 0


def _parse_date(value: str | None) -> date:
    if not value:
        return date.today()
    return datetime.strptime(value, "%Y-%m-%d").date()


def _resolve_daily_output_dir(vault_root: Path) -> Path:
    output_dir_value = os.getenv("DAILY_OUTPUT_DIR", "")
    if not output_dir_value:
        return vault_root
    output_dir = Path(output_dir_value).expanduser()
    if not output_dir.is_absolute():
        output_dir = vault_root / output_dir
    return output_dir.resolve()


def _collect_meeting_candidates(draft_path: Path) -> list[str]:
    if not draft_path.exists():
        return []
    return [
        path.name
        for path in draft_path.rglob("*.md")
        if path.is_file() and MEETING_NAME_RE.match(path.name)
    ]


def _extract_prepared_block(lines: list[str]) -> list[str] | None:
    header = "###### 排好的任务 (Prepared Work)"
    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        if line.strip() == header:
            start_idx = i
            continue
        if start_idx is not None and i > start_idx and line.strip() == "---":
            end_idx = i
            break
    if start_idx is None:
        return None
    if end_idx is None:
        end_idx = len(lines)
    return lines[start_idx:end_idx]


def _replace_prepared_block(lines: list[str], new_block: list[str]) -> tuple[list[str], bool]:
    header = "###### 排好的任务 (Prepared Work)"
    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        if line.strip() == header:
            start_idx = i
            continue
        if start_idx is not None and i > start_idx and line.strip() == "---":
            end_idx = i
            break
    if start_idx is None:
        return lines, False
    if end_idx is None:
        end_idx = len(lines)
    return lines[:start_idx] + new_block + lines[end_idx:], True


def _update_frontmatter_key(lines: list[str], key: str, value: str) -> tuple[list[str], bool]:
    if not lines or lines[0].strip() != "---":
        return lines, False
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return lines, False
    fm_lines = list(lines[1:end_idx])
    key_prefix = f"{key}:"
    updated = False
    for i, line in enumerate(fm_lines):
        if line.startswith(key_prefix):
            fm_lines[i] = f"{key}: {value}"
            updated = True
            break
    if not updated:
        fm_lines.append(f"{key}: {value}")
        updated = True
    new_lines = ["---", *fm_lines, "---", *lines[end_idx + 1 :]]
    return new_lines, updated


def _upsert_section(
    lines: list[str],
    header: str,
    block_lines: list[str],
    before_header: str | None = None,
) -> tuple[list[str], bool]:
    start_idx = None
    for i, line in enumerate(lines):
        if line.strip() == header:
            start_idx = i
            break
    if start_idx is None:
        insert_at = len(lines)
        if before_header:
            for i, line in enumerate(lines):
                if line.strip() == before_header:
                    insert_at = i
                    break
        new_lines = lines[:insert_at] + block_lines + lines[insert_at:]
        return new_lines, True

    end_idx = len(lines)
    for i in range(start_idx + 1, len(lines)):
        if lines[i].startswith("## "):
            end_idx = i
            break
    new_lines = lines[:start_idx] + block_lines + lines[end_idx:]
    return new_lines, True


def _update_moc_tool_guide(
    vault_root: Path,
    moc_path_raw: str,
    dry_run: bool,
) -> int:
    moc_path = Path(moc_path_raw).expanduser()
    if not moc_path.is_absolute():
        moc_path = vault_root / moc_path
    moc_path = moc_path.resolve()
    if not moc_path.exists():
        _eprint(f"MOC not found: {moc_path}")
        return 2

    text = moc_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    today = datetime.now().date().isoformat()
    lines, _ = _update_frontmatter_key(lines, "updated", today)

    block = [
        "## 统一入口（笔记工具）",
        "默认只记一个入口：`note-hub`。",
        "",
        "```bash",
        "# 会议归档触发器：拆分 → 合并 → 补全 → 归档 → 删除 Gemini pack",
        "python tasks/note-hub/main.py meeting-archive",
        "",
        "# 文档同步（README/AGENTS/RELEASE_NOTES/MOC）",
        "python tasks/note-hub/main.py docs-sync --summary \"docs sync\"",
        "",
        "# 全流程清洗（拆分/合并/扫描/补全/复扫/移动）",
        "python tasks/note-hub/main.py clean -- --apply",
        "",
        "# 仅清理 Inbox",
        "python tasks/note-hub/main.py inbox-clean",
        "",
        "# 仅生成移动计划 / 仅按计划移动",
        "python tasks/note-hub/main.py scan",
        "python tasks/note-hub/main.py move",
        "```",
        "",
    ]

    lines, _ = _upsert_section(lines, block[0], block, "## 工具索引（Tasks）")

    new_text = "\n".join(lines).rstrip("\n") + "\n"
    if new_text == text:
        return 0
    if dry_run:
        print(f"DRY-RUN: update MOC -> {moc_path}")
        return 0
    moc_path.write_text(new_text, encoding="utf-8")
    print(f"Updated MOC: {moc_path}")
    return 0


def main() -> int:
    tool_dir = Path(__file__).resolve().parent
    _load_dotenv_if_present(tool_dir / ".env")

    parser = argparse.ArgumentParser(description="note-hub: single entrypoint for note tooling")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="list available commands")
    subparsers.add_parser("check", help="validate config and mapped task entrypoints")

    for name in sorted(DEFAULT_TASKS.keys()):
        subparsers.add_parser(name, help=f"run {name}")

    lint_parser = subparsers.add_parser("lint", help="run linter tasks")
    lint_parser.add_argument(
        "--type",
        default="all",
        choices=["all", *ORDERED_TYPES],
        help="note type to lint",
    )
    lint_parser.add_argument("task_args", nargs=argparse.REMAINDER)

    fix_parser = subparsers.add_parser("fix", help="run fixer tasks")
    fix_parser.add_argument(
        "--type",
        default="all",
        choices=["all", *ORDERED_TYPES],
        help="note type to fix",
    )
    fix_parser.add_argument("--dry-run", action="store_true", help="preview only")
    fix_parser.add_argument("task_args", nargs=argparse.REMAINDER)

    normalize_parser = subparsers.add_parser(
        "normalize", help="normalize Gemini imports"
    )
    normalize_parser.add_argument(
        "--type",
        default="who",
        choices=["all", *NORMALIZE_TYPES],
        help="note type to normalize (default: who)",
    )
    normalize_parser.add_argument("task_args", nargs=argparse.REMAINDER)

    subparsers.add_parser("move", help="apply move planner")

    meeting_parser = subparsers.add_parser(
        "meeting-archive", help="process meeting archive workflow"
    )
    meeting_parser.add_argument(
        "--draft-dir",
        default=os.getenv("DRAFT_DIR", "Draft"),
        help="draft directory for Gemini card packs",
    )
    meeting_parser.add_argument(
        "--pack-glob",
        default=os.getenv("MEETING_PACK_GLOB", "Gemini-*.md"),
        help="glob for pack files to delete after archiving",
    )
    meeting_parser.add_argument(
        "--keep-pack",
        action="store_true",
        help="keep Gemini pack files after archive",
    )
    meeting_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="preview only",
    )

    daily_parser = subparsers.add_parser(
        "daily-rollover", help="create today's daily and carry over tasks"
    )
    daily_parser.add_argument(
        "--date",
        help="target date (YYYY-MM-DD), default: today",
    )
    daily_parser.add_argument(
        "--source-date",
        help="source date for prepared tasks (YYYY-MM-DD), default: yesterday",
    )
    daily_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="preview only",
    )

    docs_parser = subparsers.add_parser(
        "docs-sync", help="update README/AGENTS/RELEASE_NOTES and Atlas MOC"
    )
    docs_parser.add_argument("--summary", action="append", default=[], help="summary bullet")
    docs_parser.add_argument("--summary-file", help="path to summary file")
    docs_parser.add_argument(
        "--with-archive",
        action="store_true",
        help="also write quick-archive note",
    )
    docs_parser.add_argument(
        "--skip-moc",
        action="store_true",
        help="skip Atlas MOC update",
    )
    docs_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="preview only",
    )

    run_parser = subparsers.add_parser("run", help="run any task by name")
    run_parser.add_argument("--task", required=True, help="task directory name")
    run_parser.add_argument("task_args", nargs=argparse.REMAINDER)

    args, unknown = parser.parse_known_args()
    if unknown and unknown[0] == "--":
        unknown = unknown[1:]

    task_map = _parse_task_map(os.getenv("HUB_TASKS"))

    if args.command == "list":
        _list_commands(task_map)
        return 0

    if args.command == "check":
        return _run_check(task_map)

    try:
        repo_root = _resolve_repo_root(os.getenv("REPO_ROOT"))
    except ValueError as exc:
        _eprint(str(exc))
        return 2

    if args.command == "lint":
        extra_args = list(args.task_args or [])
        if extra_args and extra_args[0] == "--":
            extra_args = extra_args[1:]
        types = ORDERED_TYPES if args.type == "all" else [args.type]
        return _run_group(
            repo_root,
            LINTER_TASKS,
            types,
            extra_args,
            os.getenv("VAULT_ROOT"),
            False,
        )

    if args.command == "fix":
        extra_args = list(args.task_args or [])
        if extra_args and extra_args[0] == "--":
            extra_args = extra_args[1:]
        types = ORDERED_TYPES if args.type == "all" else [args.type]
        return _run_group(
            repo_root,
            FIXER_TASKS,
            types,
            extra_args,
            os.getenv("VAULT_ROOT"),
            args.dry_run,
        )

    if args.command == "normalize":
        extra_args = list(args.task_args or [])
        if extra_args and extra_args[0] == "--":
            extra_args = extra_args[1:]
        types = NORMALIZE_TYPES if args.type == "all" else [args.type]
        return _run_group(
            repo_root,
            NORMALIZE_TASKS,
            types,
            extra_args,
            os.getenv("VAULT_ROOT"),
            False,
        )

    if args.command == "meeting-archive":
        vault_root = os.getenv("VAULT_ROOT")
        if not vault_root:
            _eprint("Missing config: VAULT_ROOT")
            return 2
        python = sys.executable
        draft_dir = args.draft_dir
        draft_path = Path(draft_dir).expanduser()
        if not draft_path.is_absolute():
            draft_path = Path(vault_root) / draft_path
        draft_path = draft_path.resolve()
        dry_run = bool(args.dry_run)

        steps = [
            (
                [
                    python,
                    str(repo_root / "tasks" / "gemini-pack-link-fixer" / "main.py"),
                    "--vault-root",
                    vault_root,
                    "--input-dir",
                    str(draft_path),
                ]
                + (["--dry-run"] if dry_run else []),
                "Fix Gemini links (Pack)",
            ),
            (
                [
                    python,
                    str(repo_root / "tasks" / "card-pack-splitter" / "main.py"),
                    "--vault-root",
                    vault_root,
                    "--input-dir",
                    str(draft_path),
                    "--output-dir",
                    str(draft_path),
                    "--apply" if not dry_run else "--dry-run",
                ],
                "Split card packs",
            ),
            (
                [
                    python,
                    str(repo_root / "tasks" / "meeting-link-alias-fixer" / "main.py"),
                    "--vault-root",
                    vault_root,
                    "--input-dir",
                    str(draft_path),
                    "--alias-dirs",
                    f"{draft_path},2_Cards",
                    "--recursive",
                ]
                + (["--dry-run"] if dry_run else []),
                "Fix MeetingSum links (Aliases)",
            ),
            (
                [
                    python,
                    str(repo_root / "tasks" / "meeting-source-link-fixer" / "main.py"),
                    "--vault-root",
                    vault_root,
                    "--input-dir",
                    str(draft_path),
                    "--meeting-dir",
                    "4_Source/MeetingSum",
                ]
                + (["--dry-run"] if dry_run else []),
                "Fix Meeting source links",
            ),
            (
                [
                    python,
                    str(repo_root / "tasks" / "wikilink-normalizer" / "main.py"),
                    "--vault-root",
                    vault_root,
                    "--input-dir",
                    str(draft_path),
                    "--recursive",
                ]
                + (["--dry-run"] if dry_run else []),
                "Normalize wikilinks",
            ),
            (
                [
                    python,
                    str(repo_root / "tasks" / "merge-ai" / "main.py"),
                    "--vault-root",
                    vault_root,
                    "--input-dir",
                    str(draft_path),
                    "--inbox-dir",
                    "",
                    "--apply" if not dry_run else "--dry-run",
                ],
                "Merge same-name notes (AI)",
            ),
            (
                [
                    python,
                    str(repo_root / "tasks" / "meeting-sum-fixer" / "main.py"),
                    "--vault-root",
                    vault_root,
                    "--input-dir",
                    str(draft_path),
                    "--recursive",
                ]
                + (["--dry-run"] if dry_run else []),
                "Fix MeetingSum (Draft)",
            ),
            (
                [
                    python,
                    str(repo_root / "tasks" / "who-fixer" / "main.py"),
                    "--vault-root",
                    vault_root,
                    "--input-dir",
                    str(draft_path),
                    "--inbox-dir",
                    "",
                ]
                + (["--dry-run"] if dry_run else []),
                "Fix Who (Draft)",
            ),
            (
                [
                    python,
                    str(repo_root / "tasks" / "card-fixer" / "main.py"),
                    "--vault-root",
                    vault_root,
                    "--input-dir",
                    str(draft_path),
                    "--inbox-dir",
                    "",
                ]
                + (["--dry-run"] if dry_run else []),
                "Fix Card (Draft)",
            ),
            (
                [
                    python,
                    str(repo_root / "tasks" / "solution-fixer" / "main.py"),
                    "--vault-root",
                    vault_root,
                    "--input-dir",
                    str(draft_path),
                    "--inbox-dir",
                    "",
                ]
                + (["--dry-run"] if dry_run else []),
                "Fix Solution (Draft)",
            ),
            (
                [
                    python,
                    str(repo_root / "tasks" / "project-fixer" / "main.py"),
                    "--vault-root",
                    vault_root,
                    "--input-dir",
                    str(draft_path),
                    "--inbox-dir",
                    "",
                ]
                + (["--dry-run"] if dry_run else []),
                "Fix Project (Draft)",
            ),
            (
                [
                    python,
                    str(repo_root / "tasks" / "note-fixer" / "main.py"),
                    "--vault-root",
                    vault_root,
                    "--input-dir",
                    str(draft_path),
                    "--inbox-dir",
                    "",
                ]
                + (["--dry-run"] if dry_run else []),
                "Fix Note (Draft)",
            ),
            (
                [
                    python,
                    str(repo_root / "tasks" / "card-merge" / "main.py"),
                    "--vault-root",
                    vault_root,
                    "--input-dir",
                    str(draft_path),
                    "--inbox-dir",
                    "",
                    "--apply" if not dry_run else "--dry-run",
                ],
                "Merge same-name cards/solutions (Draft)",
            ),
            (
                [
                    python,
                    str(repo_root / "tasks" / "vault-move-planner" / "main.py"),
                    "--vault-root",
                    vault_root,
                    "--draft-dir",
                    str(draft_path),
                ]
                + ([] if dry_run else ["--apply"]),
                "Move (Draft)",
            ),
        ]

        meeting_candidates: list[str] = []
        for cmd, label in steps:
            code = _run_command(cmd)
            if code != 0:
                _eprint(f"{label} failed with code {code}")
                return code
            if label == "Split card packs":
                meeting_candidates = _collect_meeting_candidates(draft_path)

        if meeting_candidates:
            daily_cmd = [
                python,
                str(repo_root / "tasks" / "daily-meeting-linker" / "main.py"),
                "--vault-root",
                vault_root,
                "--meeting-names",
                ",".join(meeting_candidates),
            ]
            if dry_run:
                daily_cmd.append("--dry-run")
            code = _run_command(daily_cmd)
            if code != 0:
                _eprint(f"Daily linker failed with code {code}")
                return code

        if not args.keep_pack:
            return _delete_pack_files(
                Path(vault_root), str(draft_path), args.pack_glob, dry_run
            )
        return 0

    if args.command == "daily-rollover":
        vault_root_raw = os.getenv("VAULT_ROOT")
        if not vault_root_raw:
            _eprint("Missing config: VAULT_ROOT")
            return 2
        vault_root = Path(vault_root_raw).expanduser().resolve()
        if not vault_root.exists():
            _eprint(f"Vault root not found: {vault_root}")
            return 2

        try:
            target_date = _parse_date(args.date)
        except ValueError:
            _eprint("date must be YYYY-MM-DD")
            return 2
        if args.source_date:
            try:
                source_date = _parse_date(args.source_date)
            except ValueError:
                _eprint("source-date must be YYYY-MM-DD")
                return 2
        else:
            source_date = target_date - timedelta(days=1)

        output_dir = _resolve_daily_output_dir(vault_root)
        target_path = output_dir / f"{target_date.isoformat()}.md"
        source_path = output_dir / f"{source_date.isoformat()}.md"

        python = sys.executable
        daily_manager = repo_root / "tasks" / "daily-note-manager" / "main.py"
        if not daily_manager.exists():
            _eprint(f"Task not found: {daily_manager}")
            return 2

        cmd = [
            python,
            str(daily_manager),
            "--vault-root",
            str(vault_root),
            "--date",
            target_date.isoformat(),
        ]
        output_dir_value = os.getenv("DAILY_OUTPUT_DIR", "")
        if output_dir_value:
            cmd.extend(["--output-dir", output_dir_value])
        if args.dry_run:
            cmd.append("--dry-run")
        code = _run_command(cmd)
        if code != 0:
            return code

        if not source_path.exists():
            _eprint(f"Source daily not found: {source_path}")
            return 0
        if not target_path.exists():
            _eprint(f"Target daily not found: {target_path}")
            return 2

        source_lines = source_path.read_text(encoding="utf-8").splitlines()
        target_lines = target_path.read_text(encoding="utf-8").splitlines()
        prepared_block = _extract_prepared_block(source_lines)
        if not prepared_block:
            _eprint(f"Prepared Work section not found: {source_path}")
            return 0

        updated_lines, changed = _replace_prepared_block(target_lines, prepared_block)
        if not changed:
            _eprint(f"Prepared Work section not found: {target_path}")
            return 0

        new_text = "\n".join(updated_lines).rstrip("\n") + "\n"
        if args.dry_run:
            print(f"DRY-RUN: update prepared tasks -> {target_path}")
            return 0
        target_path.write_text(new_text, encoding="utf-8")
        print(f"Updated: {target_path}")
        return 0

    if args.command == "docs-sync":
        python = sys.executable
        quick_archive = repo_root / "tasks" / "quick-archive" / "main.py"
        if not quick_archive.exists():
            _eprint(f"Task not found: {quick_archive}")
            return 2

        summary_items = list(args.summary or [])
        summary_file = args.summary_file
        if not summary_items and not summary_file:
            default_summary = os.getenv("DOCS_SYNC_SUMMARY", "docs sync")
            summary_items = [default_summary]

        cmd = [python, str(quick_archive)]
        for item in summary_items:
            cmd.extend(["--summary", item])
        if summary_file:
            cmd.extend(["--summary-file", summary_file])
        if not args.with_archive:
            cmd.append("--skip-archive")
        if args.dry_run:
            cmd.append("--dry-run")

        code = _run_command(cmd)
        if code != 0:
            return code

        if not args.skip_moc:
            vault_root = os.getenv("VAULT_ROOT")
            if not vault_root:
                _eprint("Missing config: VAULT_ROOT")
                return 2
            moc_path = os.getenv("MOC_TOOL_GUIDE", "3_Atlas/MOC-系统工具与协议总览.md")
            return _update_moc_tool_guide(Path(vault_root), moc_path, args.dry_run)

        return 0

    if args.command == "run":
        task_dir = Path(args.task)
        if not task_dir.is_absolute():
            task_dir = repo_root / "tasks" / task_dir
        task_main = task_dir / "main.py"
        if not task_main.exists():
            _eprint(f"Task not found: {task_main}")
            return 2
        task_args = list(args.task_args)
        if task_args and task_args[0] == "--":
            task_args = task_args[1:]
        cmd = [sys.executable, str(task_main)] + task_args
        return _run_command(cmd)

    if args.command in SPECIAL_COMMANDS:
        task_path = task_map.get("scan") or DEFAULT_TASKS["scan"]
        task_main = _resolve_task_path(repo_root, task_path)
        if not task_main.exists():
            _eprint(f"Task not found: {task_main}")
            return 2
        cmd = [sys.executable, str(task_main), "--apply"] + unknown
        return _run_command(cmd)

    task_path = task_map.get(args.command)
    if not task_path:
        _eprint(f"Unknown command: {args.command}")
        return 2

    task_main = _resolve_task_path(repo_root, task_path)
    if not task_main.exists():
        _eprint(f"Task not found: {task_main}")
        return 2

    cmd = [sys.executable, str(task_main)] + unknown
    return _run_command(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
