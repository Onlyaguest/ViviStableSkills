#!/usr/bin/env python3
"""
CleanDesktop v2.1 - Desktop File Organizer
Auto-archive desktop files by week, with type classification and CSV logging.
"""

from __future__ import annotations

import argparse
import csv
import os
import platform
import shutil
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

# ==================== Constants ====================

LOG_FIELDS = [
    "archived_at",
    "original_name",
    "new_name",
    "category_tag",
    "type_tag",
    "week_folder",
    "src_path",
    "dest_path",
    "action",
]

# File type mapping
TYPE_MAPPING = {
    # Images
    "png": "images", "jpg": "images", "jpeg": "images", "gif": "images",
    "bmp": "images", "tiff": "images", "webp": "images", "heic": "images", "svg": "images",
    # Documents
    "txt": "docs", "md": "docs", "pdf": "docs", "doc": "docs", "docx": "docs",
    "rtf": "docs", "pages": "docs",
    # Spreadsheets
    "xlsx": "sheets", "xls": "sheets", "csv": "sheets", "numbers": "sheets",
    # Videos
    "mp4": "videos", "mov": "videos", "avi": "videos", "mkv": "videos", "wmv": "videos",
    # Audio
    "mp3": "audio", "wav": "audio", "aac": "audio", "flac": "audio", "m4a": "audio",
    # Archives
    "zip": "archives", "rar": "archives", "7z": "archives", "tar": "archives", "gz": "archives",
    # Code
    "py": "code", "js": "code", "ts": "code", "html": "code", "css": "code",
    "java": "code", "swift": "code", "go": "code", "rs": "code", "sh": "code",
}

# Category tag options
CATEGORY_OPTIONS = ["work", "personal", "project", "notes", "other"]

# Types that get an extra copy in a type-specific folder
COPY_TYPES = {"images": "images-archive", "docs": "docs-archive", "sheets": "sheets-archive"}

# Files/dirs to always skip
SKIP_NAMES = {".DS_Store", "Thumbs.db", "desktop.ini"}


# ==================== Utilities ====================

def _eprint(msg: str) -> None:
    print(msg, file=sys.stderr)


def _load_dotenv(dotenv_path: Path) -> None:
    """Load .env file (simple key=value parser, no external deps)."""
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
            stripped = stripped[len("export "):].strip()
        if "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key and key not in os.environ:
            os.environ[key] = value


def get_file_type(filename: str) -> str:
    ext = Path(filename).suffix.lower().lstrip(".")
    return TYPE_MAPPING.get(ext, "other")


def get_week_folder(d: date) -> str:
    """Week folder name: 2025.08.21-2025.08.27 (Monday-based)."""
    monday = d - timedelta(days=d.weekday())
    sunday = monday + timedelta(days=6)
    return f"{monday.strftime('%Y.%m.%d')}-{sunday.strftime('%Y.%m.%d')}"


def add_date_prefix(filename: str, d: date) -> str:
    """Add date prefix if not already present."""
    import re
    if re.match(r"^\d{4}\.\d{2}\.\d{2}\s", filename):
        return filename
    return f"{d.strftime('%Y.%m.%d')} {filename}"


def unique_dest(dest_dir: Path, name: str, reserved: set[Path]) -> Path:
    """Generate unique destination path to avoid conflicts."""
    p = Path(name)
    base = p.stem
    suffix = p.suffix
    candidate = dest_dir / name
    if not candidate.exists() and candidate not in reserved:
        return candidate
    i = 1
    while True:
        new_name = f"{base} ({i}){suffix}"
        candidate = dest_dir / new_name
        if not candidate.exists() and candidate not in reserved:
            return candidate
        i += 1


def select_category_interactive() -> str:
    """Interactive category selection via terminal."""
    print("\nSelect file category:")
    for i, cat in enumerate(CATEGORY_OPTIONS, 1):
        print(f"  {i}. {cat}")
    print()
    while True:
        try:
            choice = input(f"Enter number (1-{len(CATEGORY_OPTIONS)}) [default: {len(CATEGORY_OPTIONS)}-other]: ").strip()
            if not choice:
                return "other"
            idx = int(choice)
            if 1 <= idx <= len(CATEGORY_OPTIONS):
                return CATEGORY_OPTIONS[idx - 1]
            print(f"Please enter a number between 1 and {len(CATEGORY_OPTIONS)}")
        except ValueError:
            print("Please enter a valid number")
        except EOFError:
            return "other"


def select_category_gui() -> str:
    """GUI category selection. macOS uses AppleScript, others fall back to terminal."""
    if platform.system() == "Darwin":
        import subprocess
        items = ", ".join(f'"{c}"' for c in CATEGORY_OPTIONS)
        script = f'''
        set categoryList to {{{items}}}
        set selectedCategory to choose from list categoryList with prompt "Select file category:" default items {{"{CATEGORY_OPTIONS[-1]}"}}
        if selectedCategory is false then
            return "{CATEGORY_OPTIONS[-1]}"
        else
            return item 1 of selectedCategory
        end if
        '''
        try:
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0:
                return result.stdout.strip() or "other"
        except Exception:
            pass
    # Fallback to terminal
    return select_category_interactive()


# ==================== Config ====================

@dataclass(frozen=True)
class Config:
    desktop_path: Path
    archive_path: Path
    log_path: Path
    default_category: str


def load_config() -> Config:
    desktop = Path(os.getenv("CLEANDESKTOP_SOURCE", os.getenv("DESKTOP_PATH", "~/Desktop"))).expanduser()
    archive = Path(os.getenv("CLEANDESKTOP_ARCHIVE", os.getenv("ARCHIVE_PATH", "~/Desktop/archive"))).expanduser()
    log_env = os.getenv("CLEANDESKTOP_LOG", os.getenv("LOG_PATH", ""))
    log_path = Path(log_env).expanduser() if log_env else (archive / "archive_log.csv")
    default_category = os.getenv("CLEANDESKTOP_CATEGORY", os.getenv("DEFAULT_CATEGORY", "other"))
    return Config(
        desktop_path=desktop,
        archive_path=archive,
        log_path=log_path,
        default_category=default_category,
    )


# ==================== Logging ====================

def write_log_rows(log_path: Path, rows: list[dict[str, str]]) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not log_path.exists()
    with log_path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        if write_header:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)


# ==================== Commands ====================

def cmd_archive(args: argparse.Namespace) -> int:
    cfg = load_config()

    category = args.category
    if not category:
        if args.gui:
            category = select_category_gui()
        elif sys.stdin.isatty():
            category = select_category_interactive()
        else:
            category = cfg.default_category

    print(f"\nStarting desktop cleanup...")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Category:  {category}")
    print()

    # Scan desktop
    files_to_process: list[Path] = []
    for item in cfg.desktop_path.iterdir():
        if item.is_dir():
            continue
        if item.name.startswith(".") or item.name.startswith("~$"):
            continue
        if item.name in SKIP_NAMES:
            continue
        files_to_process.append(item)

    if not files_to_process:
        print("Desktop is clean - nothing to archive.")
        return 0

    print(f"Found {len(files_to_process)} file(s) to archive")

    # Prepare archive directories
    today = date.today()
    week_folder = get_week_folder(today)
    week_path = cfg.archive_path / "by-week" / week_folder
    week_path.mkdir(parents=True, exist_ok=True)

    for type_folder in COPY_TYPES.values():
        (cfg.archive_path / type_folder).mkdir(parents=True, exist_ok=True)

    # Plan moves
    reserved: set[Path] = set()
    planned: list[tuple[Path, Path, str, str]] = []

    for src in files_to_process:
        new_name = add_date_prefix(src.name, today)
        type_tag = get_file_type(src.name)
        dest = unique_dest(week_path, new_name, reserved)
        reserved.add(dest)
        planned.append((src, dest, new_name, type_tag))

    # Preview
    if args.dry_run or not args.yes:
        print("\nArchive plan:")
        for src, dest, new_name, type_tag in planned:
            print(f"  [{type_tag}] {src.name} -> {new_name}")
        print()

    if args.dry_run:
        print("[dry-run] Preview only, no files moved.")
        return 0

    if not args.yes:
        if not sys.stdin.isatty():
            _eprint("Non-interactive mode. Use --yes to confirm.")
            return 2
        try:
            ans = input("Proceed? [y/N]: ").strip().lower()
            if ans not in ("y", "yes"):
                print("Cancelled.")
                return 1
        except EOFError:
            return 1

    # Execute
    now = datetime.now().astimezone()
    log_rows: list[dict[str, str]] = []
    stats = {"moved": 0, "copied": 0, "errors": 0}
    type_stats: dict[str, int] = {}

    for src, dest, new_name, type_tag in planned:
        try:
            shutil.move(str(src), str(dest))
            stats["moved"] += 1
            type_stats[type_tag] = type_stats.get(type_tag, 0) + 1

            if type_tag in COPY_TYPES:
                type_archive = cfg.archive_path / COPY_TYPES[type_tag]
                copy_dest = unique_dest(type_archive, new_name, set())
                shutil.copy2(str(dest), str(copy_dest))
                stats["copied"] += 1

            log_rows.append({
                "archived_at": now.isoformat(timespec="seconds"),
                "original_name": src.name,
                "new_name": new_name,
                "category_tag": category,
                "type_tag": type_tag,
                "week_folder": week_folder,
                "src_path": str(src),
                "dest_path": str(dest),
                "action": "move",
            })
            print(f"  [ok] {src.name}")

        except Exception as e:
            stats["errors"] += 1
            _eprint(f"  [error] {src.name}: {e}")

    if log_rows:
        try:
            write_log_rows(cfg.log_path, log_rows)
            print(f"\nLog updated: {cfg.log_path}")
        except Exception as e:
            _eprint(f"Failed to write log: {e}")

    print()
    print("=" * 40)
    print("Archive complete!")
    print(f"  Moved:  {stats['moved']}")
    print(f"  Copied: {stats['copied']}")
    if stats["errors"]:
        print(f"  Errors: {stats['errors']}")
    print()
    print("By type:")
    for t, count in sorted(type_stats.items()):
        print(f"  {t}: {count}")
    print("=" * 40)

    return 0 if stats["errors"] == 0 else 1


def cmd_list(args: argparse.Namespace) -> int:
    cfg = load_config()

    if not cfg.log_path.exists():
        _eprint(f"Log file not found: {cfg.log_path}")
        return 1

    rows: list[dict[str, str]] = []
    with cfg.log_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if args.category and r.get("category_tag") != args.category:
                continue
            if args.type and r.get("type_tag") != args.type:
                continue
            if args.week and r.get("week_folder") != args.week:
                continue
            rows.append(r)

    if not rows:
        print("No matching records.")
        return 0

    limit = args.limit or 20
    rows = rows[-limit:]

    cols = ["archived_at", "original_name", "category_tag", "type_tag", "week_folder"]
    print("\t".join(cols))
    for r in rows:
        print("\t".join(r.get(c, "") for c in cols))

    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    cfg = load_config()

    if not cfg.log_path.exists():
        _eprint(f"Log file not found: {cfg.log_path}")
        return 1

    category_stats: dict[str, int] = {}
    type_stats: dict[str, int] = {}
    week_stats: dict[str, int] = {}
    total = 0

    with cfg.log_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            total += 1
            cat = r.get("category_tag", "unknown")
            typ = r.get("type_tag", "unknown")
            week = r.get("week_folder", "unknown")
            category_stats[cat] = category_stats.get(cat, 0) + 1
            type_stats[typ] = type_stats.get(typ, 0) + 1
            week_stats[week] = week_stats.get(week, 0) + 1

    print(f"\nArchive Statistics ({total} files total)")
    print()
    print("By category:")
    for cat, count in sorted(category_stats.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")
    print()
    print("By type:")
    for typ, count in sorted(type_stats.items(), key=lambda x: -x[1]):
        print(f"  {typ}: {count}")
    print()
    print("By week (last 5):")
    for week, count in sorted(week_stats.items(), reverse=True)[:5]:
        print(f"  {week}: {count}")

    return 0


# ==================== Entry Point ====================

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cleandesktop",
        description="Desktop file organizer - auto-archive by week with CSV logging"
    )
    sub = p.add_subparsers(dest="command", required=True)

    pa = sub.add_parser("archive", help="Archive desktop files")
    pa.add_argument("--category", "-c", help=f"Category tag ({'/'.join(CATEGORY_OPTIONS)})")
    pa.add_argument("--dry-run", action="store_true", help="Preview only, no file moves")
    pa.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")
    pa.add_argument("--gui", action="store_true", help="Use GUI dialog for category selection (macOS)")
    pa.set_defaults(func=cmd_archive)

    pl = sub.add_parser("list", help="Query archive log")
    pl.add_argument("--category", "-c", help="Filter by category")
    pl.add_argument("--type", "-t", help="Filter by file type")
    pl.add_argument("--week", "-w", help="Filter by week folder (e.g. 2025.08.21-2025.08.27)")
    pl.add_argument("--limit", "-n", type=int, default=20, help="Max records to show (default: 20)")
    pl.set_defaults(func=cmd_list)

    ps = sub.add_parser("stats", help="Show archive statistics")
    ps.set_defaults(func=cmd_stats)

    return p


def main(argv: list[str] | None = None) -> int:
    tool_dir = Path(__file__).resolve().parent
    _load_dotenv(tool_dir / ".env")

    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return int(args.func(args))
    except RuntimeError as e:
        _eprint(str(e))
        return 2
    except KeyboardInterrupt:
        print("\nInterrupted.")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
