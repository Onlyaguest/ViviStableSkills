from __future__ import annotations

import argparse
import os
import plistlib
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


NAME_RE = r"[A-Za-z0-9_.-]+"
HTTPS_RE = re.compile(
    rf"^(?:https?://)?(?:www\.)?github\.com/(?P<owner>{NAME_RE})/(?P<repo>{NAME_RE})(?:\.git)?/?$"
)
SSH_RE = re.compile(
    rf"^git@github\.com:(?P<owner>{NAME_RE})/(?P<repo>{NAME_RE})(?:\.git)?/?$"
)
SHORT_RE = re.compile(rf"^(?P<owner>{NAME_RE})/(?P<repo>{NAME_RE})$")


@dataclass(frozen=True)
class RepoSpec:
    raw: str
    clone_url: str
    owner: str
    repo: str
    dest_dir: Path

    @property
    def slug(self) -> str:
        return f"{self.owner}/{self.repo}"


@dataclass(frozen=True)
class SyncResult:
    repo: str
    action: str
    status: str
    message: str
    dest_dir: Path


def _eprint(message: str) -> None:
    print(message, file=sys.stderr)


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


def _expand_path(raw: str, *, base_dir: Path) -> Path:
    expanded = Path(os.path.expanduser(os.path.expandvars(raw)))
    if expanded.is_absolute():
        return expanded.resolve()
    return (base_dir / expanded).resolve()


def _default_repo_list(tool_dir: Path) -> str:
    return os.getenv("REPO_LIST_FILE", str(tool_dir / "repos.txt"))


def _default_root_dir() -> str:
    return os.getenv("SYNC_ROOT_DIR", "~/Code/github-sync")


def _git_bin() -> str:
    return os.getenv("GIT_BIN", "git")


def _strip_comment(line: str) -> str:
    if "#" not in line:
        return line.strip()
    head, _, _ = line.partition("#")
    return head.strip()


def _parse_repo_target(raw: str) -> tuple[str, str, str]:
    text = raw.strip()
    for pattern in (HTTPS_RE, SSH_RE, SHORT_RE):
        match = pattern.match(text)
        if not match:
            continue
        owner = match.group("owner")
        repo = match.group("repo")
        if pattern is SHORT_RE:
            clone_url = f"https://github.com/{owner}/{repo}.git"
        elif text.startswith("http"):
            clone_url = f"https://github.com/{owner}/{repo}.git"
        else:
            clone_url = f"git@github.com:{owner}/{repo}.git"
        return clone_url, owner, repo
    raise ValueError(
        f"Unsupported repo format: {raw!r}. Use owner/repo, https://github.com/owner/repo(.git), or git@github.com:owner/repo.git"
    )


def _load_repo_specs(repo_list_path: Path, root_dir: Path) -> list[RepoSpec]:
    if not repo_list_path.exists():
        raise FileNotFoundError(f"Repo list file not found: {repo_list_path}")

    specs: list[RepoSpec] = []
    seen: set[str] = set()
    for line in repo_list_path.read_text(encoding="utf-8").splitlines():
        cleaned = _strip_comment(line)
        if not cleaned:
            continue
        clone_url, owner, repo = _parse_repo_target(cleaned)
        slug = f"{owner}/{repo}"
        if slug in seen:
            continue
        seen.add(slug)
        specs.append(
            RepoSpec(
                raw=cleaned,
                clone_url=clone_url,
                owner=owner,
                repo=repo,
                dest_dir=root_dir / owner / repo,
            )
        )
    return specs


def _run_command(args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
    )


def _command_output(result: subprocess.CompletedProcess[str]) -> str:
    pieces = []
    if result.stdout.strip():
        pieces.append(result.stdout.strip())
    if result.stderr.strip():
        pieces.append(result.stderr.strip())
    return "\n".join(pieces).strip()


def _last_line(text: str, fallback: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[-1] if lines else fallback


def _git_is_repo(repo_dir: Path, git_bin: str) -> bool:
    result = _run_command([git_bin, "-C", str(repo_dir), "rev-parse", "--is-inside-work-tree"])
    return result.returncode == 0 and result.stdout.strip() == "true"


def _git_current_branch(repo_dir: Path, git_bin: str) -> str:
    result = _run_command([git_bin, "-C", str(repo_dir), "branch", "--show-current"])
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def _git_is_dirty(repo_dir: Path, git_bin: str) -> bool:
    result = _run_command([git_bin, "-C", str(repo_dir), "status", "--porcelain"])
    return result.returncode == 0 and bool(result.stdout.strip())


def _git_has_upstream(repo_dir: Path, git_bin: str) -> bool:
    result = _run_command(
        [git_bin, "-C", str(repo_dir), "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"]
    )
    return result.returncode == 0 and bool(result.stdout.strip())


def _sync_repo(spec: RepoSpec, *, git_bin: str, dry_run: bool) -> SyncResult:
    if not spec.dest_dir.exists():
        if dry_run:
            return SyncResult(
                repo=spec.slug,
                action="clone",
                status="planned",
                message=f"Would clone {spec.clone_url}",
                dest_dir=spec.dest_dir,
            )
        spec.dest_dir.parent.mkdir(parents=True, exist_ok=True)
        result = _run_command([git_bin, "clone", spec.clone_url, str(spec.dest_dir)])
        if result.returncode != 0:
            return SyncResult(
                repo=spec.slug,
                action="clone",
                status="failed",
                message=_last_line(_command_output(result), "git clone failed"),
                dest_dir=spec.dest_dir,
            )
        return SyncResult(
            repo=spec.slug,
            action="clone",
            status="ok",
            message="Cloned successfully",
            dest_dir=spec.dest_dir,
        )

    if not _git_is_repo(spec.dest_dir, git_bin):
        return SyncResult(
            repo=spec.slug,
            action="inspect",
            status="skipped",
            message="Destination exists but is not a git repository",
            dest_dir=spec.dest_dir,
        )

    if dry_run:
        return SyncResult(
            repo=spec.slug,
            action="pull",
            status="planned",
            message="Would fetch and fast-forward pull if the worktree is clean",
            dest_dir=spec.dest_dir,
        )

    fetch_result = _run_command([git_bin, "-C", str(spec.dest_dir), "fetch", "--all", "--prune"])
    if fetch_result.returncode != 0:
        return SyncResult(
            repo=spec.slug,
            action="fetch",
            status="failed",
            message=_last_line(_command_output(fetch_result), "git fetch failed"),
            dest_dir=spec.dest_dir,
        )

    if _git_is_dirty(spec.dest_dir, git_bin):
        return SyncResult(
            repo=spec.slug,
            action="pull",
            status="skipped",
            message="Skipped because the worktree has local changes",
            dest_dir=spec.dest_dir,
        )

    branch = _git_current_branch(spec.dest_dir, git_bin)
    if not branch:
        return SyncResult(
            repo=spec.slug,
            action="pull",
            status="skipped",
            message="Skipped because HEAD is detached",
            dest_dir=spec.dest_dir,
        )

    if not _git_has_upstream(spec.dest_dir, git_bin):
        return SyncResult(
            repo=spec.slug,
            action="pull",
            status="skipped",
            message=f"Skipped because branch {branch} has no upstream",
            dest_dir=spec.dest_dir,
        )

    pull_result = _run_command([git_bin, "-C", str(spec.dest_dir), "pull", "--ff-only"])
    if pull_result.returncode != 0:
        return SyncResult(
            repo=spec.slug,
            action="pull",
            status="failed",
            message=_last_line(_command_output(pull_result), "git pull failed"),
            dest_dir=spec.dest_dir,
        )

    return SyncResult(
        repo=spec.slug,
        action="pull",
        status="ok",
        message=_last_line(_command_output(pull_result), "Updated successfully"),
        dest_dir=spec.dest_dir,
    )


def _iter_selected(specs: Iterable[RepoSpec], only: set[str]) -> list[RepoSpec]:
    if not only:
        return list(specs)
    selected = [spec for spec in specs if spec.slug in only]
    missing = sorted(only - {spec.slug for spec in selected})
    if missing:
        raise ValueError(f"Repos not found in repo list: {', '.join(missing)}")
    return selected


def _print_results(results: list[SyncResult]) -> None:
    for result in results:
        print(
            f"[{result.status.upper():7}] {result.repo} | {result.action:<6} | {result.dest_dir}"
        )
        print(f"           {result.message}")

    counts: dict[str, int] = {}
    for result in results:
        counts[result.status] = counts.get(result.status, 0) + 1
    summary = ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))
    print(f"\nSummary: {summary}")


def _user_launch_domain() -> str:
    return f"gui/{os.getuid()}"


def _launch_agent_path(label: str) -> Path:
    return Path.home() / "Library" / "LaunchAgents" / f"{label}.plist"


def _launch_agent_payload(
    *,
    label: str,
    python_bin: Path,
    tool_dir: Path,
    interval_minutes: int,
    repo_list_arg: str | None,
    root_dir_arg: str | None,
) -> dict[str, object]:
    program_arguments = [str(python_bin), str(tool_dir / "main.py"), "run"]
    if repo_list_arg:
        program_arguments.extend(["--repo-list", repo_list_arg])
    if root_dir_arg:
        program_arguments.extend(["--root-dir", root_dir_arg])

    logs_dir = tool_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    return {
        "Label": label,
        "ProgramArguments": program_arguments,
        "RunAtLoad": True,
        "StartInterval": interval_minutes * 60,
        "WorkingDirectory": str(tool_dir),
        "StandardOutPath": str(logs_dir / "launchd.stdout.log"),
        "StandardErrorPath": str(logs_dir / "launchd.stderr.log"),
    }


def _run_launchctl(args: list[str], *, check: bool) -> None:
    result = _run_command(["launchctl", *args])
    if check and result.returncode != 0:
        raise RuntimeError(_command_output(result) or f"launchctl {' '.join(args)} failed")


def _install_launch_agent(
    *,
    tool_dir: Path,
    label: str,
    interval_minutes: int,
    python_bin: Path,
    repo_list_arg: str | None,
    root_dir_arg: str | None,
    dry_run: bool,
) -> None:
    if sys.platform != "darwin":
        raise RuntimeError("launchd installation is only supported on macOS")
    if interval_minutes <= 0:
        raise ValueError("--interval-minutes must be greater than 0")

    agent_path = _launch_agent_path(label)
    payload = _launch_agent_payload(
        label=label,
        python_bin=python_bin,
        tool_dir=tool_dir,
        interval_minutes=interval_minutes,
        repo_list_arg=repo_list_arg,
        root_dir_arg=root_dir_arg,
    )

    if dry_run:
        print(f"Would write LaunchAgent to: {agent_path}")
        print(plistlib.dumps(payload).decode("utf-8"))
        return

    agent_path.parent.mkdir(parents=True, exist_ok=True)
    agent_path.write_bytes(plistlib.dumps(payload))

    _run_launchctl(["bootout", _user_launch_domain(), str(agent_path)], check=False)
    _run_launchctl(["bootstrap", _user_launch_domain(), str(agent_path)], check=True)

    print(f"LaunchAgent installed: {agent_path}")
    print(f"Interval: every {interval_minutes} minute(s)")


def _uninstall_launch_agent(*, label: str, dry_run: bool) -> None:
    if sys.platform != "darwin":
        raise RuntimeError("launchd uninstallation is only supported on macOS")

    agent_path = _launch_agent_path(label)
    if dry_run:
        print(f"Would unload and remove: {agent_path}")
        return

    if agent_path.exists():
        _run_launchctl(["bootout", _user_launch_domain(), str(agent_path)], check=False)
        agent_path.unlink()
        print(f"LaunchAgent removed: {agent_path}")
    else:
        print(f"LaunchAgent not found: {agent_path}")


def _run_sync(args: argparse.Namespace, tool_dir: Path) -> int:
    repo_list_path = _expand_path(args.repo_list, base_dir=tool_dir)
    root_dir = _expand_path(args.root_dir, base_dir=tool_dir)

    try:
        specs = _load_repo_specs(repo_list_path, root_dir)
        selected = _iter_selected(specs, set(args.only))
    except (FileNotFoundError, ValueError) as exc:
        _eprint(str(exc))
        return 2

    if not selected:
        _eprint(f"No repositories found in {repo_list_path}")
        return 2

    results = [_sync_repo(spec, git_bin=args.git_bin, dry_run=args.dry_run) for spec in selected]
    _print_results(results)

    failed = any(result.status == "failed" for result in results)
    return 1 if failed else 0


def build_parser(tool_dir: Path) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sync a plain-text list of GitHub repositories to local disk."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Clone missing repos or pull updates")
    run_parser.add_argument(
        "--repo-list",
        default=_default_repo_list(tool_dir),
        help="path to the repo list file (default: %(default)s)",
    )
    run_parser.add_argument(
        "--root-dir",
        default=_default_root_dir(),
        help="local root directory for synced repos (default: %(default)s)",
    )
    run_parser.add_argument(
        "--git-bin",
        default=_git_bin(),
        help="git executable to use (default: %(default)s)",
    )
    run_parser.add_argument(
        "--only",
        action="append",
        default=[],
        metavar="OWNER/REPO",
        help="limit the sync to one or more repo slugs from repos.txt",
    )
    run_parser.add_argument("--dry-run", action="store_true", help="show planned actions only")

    install_parser = subparsers.add_parser(
        "install-launch-agent",
        help="Install or refresh a macOS LaunchAgent for scheduled sync",
    )
    install_parser.add_argument(
        "--interval-minutes",
        type=int,
        default=int(os.getenv("SCHEDULE_INTERVAL_MINUTES", "60")),
        help="sync interval in minutes (default: %(default)s)",
    )
    install_parser.add_argument(
        "--label",
        default=os.getenv("LAUNCH_AGENT_LABEL", "com.example.github-repo-sync"),
        help="launchd label (default: %(default)s)",
    )
    install_parser.add_argument(
        "--repo-list",
        help="optional repo list path to bake into the scheduled command",
    )
    install_parser.add_argument(
        "--root-dir",
        help="optional root dir path to bake into the scheduled command",
    )
    install_parser.add_argument("--dry-run", action="store_true", help="preview the plist only")

    uninstall_parser = subparsers.add_parser(
        "uninstall-launch-agent",
        help="Remove the macOS LaunchAgent",
    )
    uninstall_parser.add_argument(
        "--label",
        default=os.getenv("LAUNCH_AGENT_LABEL", "com.example.github-repo-sync"),
        help="launchd label (default: %(default)s)",
    )
    uninstall_parser.add_argument("--dry-run", action="store_true", help="preview removal only")

    return parser


def main() -> int:
    tool_dir = Path(__file__).resolve().parent
    _load_dotenv_if_present(tool_dir / ".env")
    parser = build_parser(tool_dir)
    args = parser.parse_args()

    if args.command == "run":
        return _run_sync(args, tool_dir)

    if args.command == "install-launch-agent":
        try:
            _install_launch_agent(
                tool_dir=tool_dir,
                label=args.label,
                interval_minutes=args.interval_minutes,
                python_bin=Path(sys.executable).resolve(),
                repo_list_arg=str(_expand_path(args.repo_list, base_dir=tool_dir))
                if args.repo_list
                else None,
                root_dir_arg=str(_expand_path(args.root_dir, base_dir=tool_dir))
                if args.root_dir
                else None,
                dry_run=args.dry_run,
            )
        except (RuntimeError, ValueError) as exc:
            _eprint(str(exc))
            return 2
        return 0

    if args.command == "uninstall-launch-agent":
        try:
            _uninstall_launch_agent(label=args.label, dry_run=args.dry_run)
        except RuntimeError as exc:
            _eprint(str(exc))
            return 2
        return 0

    _eprint(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
