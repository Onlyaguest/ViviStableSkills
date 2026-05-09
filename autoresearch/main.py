from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path


def _workspace(root: Path) -> Path:
    return root / "autoresearch"


def _parse_questions(raw: str) -> list[str]:
    return [item.strip() for item in raw.split("|") if item.strip()]


def _parse_answers(raw: str) -> list[bool]:
    mapping = {
        "y": True,
        "yes": True,
        "true": True,
        "1": True,
        "n": False,
        "no": False,
        "false": False,
        "0": False,
    }
    values: list[bool] = []
    for token in [part.strip().lower() for part in raw.split(",") if part.strip()]:
        if token not in mapping:
            raise ValueError(f"Unsupported answer token: {token}")
        values.append(mapping[token])
    return values


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_init(root: Path, skill_name: str, prompt_path: str | None, questions: list[str], author: str) -> int:
    ws = _workspace(root)
    ws.mkdir(parents=True, exist_ok=True)
    (ws / "iterations").mkdir(exist_ok=True)
    (ws / "artifacts").mkdir(exist_ok=True)

    checklist = "\n".join([f"- [ ] {question}" for question in questions]) or "- [ ] Add 3-6 yes/no checklist questions"
    _write(
        ws / "README.md",
        (
            f"# autoresearch workspace\n\n"
            f"- skill: {skill_name}\n"
            f"- author: {author}\n"
            f"- created: {datetime.now().isoformat(timespec='seconds')}\n\n"
            f"Use this workspace to iterate on one skill with a stable checklist, baseline score, and changelog.\n"
        ),
    )
    _write(
        ws / "checklist.md",
        (
            f"# Checklist for {skill_name}\n\n"
            "Keep this to 3-6 yes/no questions.\n\n"
            f"{checklist}\n"
        ),
    )
    _write(
        ws / "baseline.md",
        (
            f"# Baseline\n\n"
            f"- skill: {skill_name}\n"
            "- test input: [fill this in]\n"
            "- starting score: [fill this in]\n"
            "- notes: [what currently fails most often]\n"
        ),
    )
    _write(
        ws / "CHANGELOG.md",
        (
            "# Change Log\n\n"
            "| Time | Iteration | Change | Score Before | Score After | Keep? | Notes |\n"
            "|---|---|---|---:|---:|---|---|\n"
        ),
    )
    _write(
        ws / "runbook.md",
        (
            "# Runbook\n\n"
            "1. Lock the test input.\n"
            "2. Score the current output with `score`.\n"
            "3. Make one small change only.\n"
            "4. Score again.\n"
            "5. If score improves, keep it; otherwise revert it.\n"
            "6. Append the result with `log-iteration`.\n"
            "7. Stop after three consecutive runs above 95% or when gains plateau.\n"
        ),
    )
    if prompt_path:
        _write(ws / "source-pointer.txt", prompt_path + "\n")

    print(f"Initialized autoresearch workspace: {ws}")
    return 0


def run_score(answers: list[bool], append: Path | None, skill_name: str) -> int:
    total = len(answers)
    passed = sum(1 for item in answers if item)
    percentage = round((passed / total) * 100, 1) if total else 0.0
    result = {
        "skill": skill_name,
        "passed": passed,
        "total": total,
        "percentage": percentage,
        "answers": answers,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if append:
        append.parent.mkdir(parents=True, exist_ok=True)
        with append.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(result, ensure_ascii=False) + "\n")
    return 0


def run_log_iteration(root: Path, iteration: str, change: str, before: float, after: float, keep: bool, notes: str) -> int:
    ws = _workspace(root)
    changelog = ws / "CHANGELOG.md"
    if not changelog.exists():
        raise FileNotFoundError(f"Missing changelog: {changelog}. Run init first.")
    line = f"| {datetime.now().isoformat(timespec='seconds')} | {iteration} | {change} | {before} | {after} | {'yes' if keep else 'no'} | {notes or '-'} |\n"
    with changelog.open("a", encoding="utf-8") as fh:
        fh.write(line)
    print(f"Logged iteration to {changelog}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="autoresearch: scaffold and record an iterative skill-improvement loop"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="initialize an autoresearch workspace")
    init_parser.add_argument("--root", required=True, help="target project root")
    init_parser.add_argument("--skill-name", required=True, help="skill under improvement")
    init_parser.add_argument("--author", default="unknown", help="workspace author")
    init_parser.add_argument("--prompt-path", help="optional original skill or prompt path")
    init_parser.add_argument(
        "--questions",
        default="",
        help="pipe-separated yes/no checklist questions",
    )

    score_parser = subparsers.add_parser("score", help="score one run against yes/no answers")
    score_parser.add_argument("--answers", required=True, help="comma-separated answers, e.g. y,y,n,y")
    score_parser.add_argument("--skill-name", default="unnamed-skill", help="skill under evaluation")
    score_parser.add_argument("--append", help="optional JSONL file to append result to")

    log_parser = subparsers.add_parser("log-iteration", help="append one iteration result to changelog")
    log_parser.add_argument("--root", required=True, help="target project root")
    log_parser.add_argument("--iteration", required=True, help="iteration label")
    log_parser.add_argument("--change", required=True, help="what changed this round")
    log_parser.add_argument("--before", required=True, type=float, help="score before the change")
    log_parser.add_argument("--after", required=True, type=float, help="score after the change")
    log_parser.add_argument("--keep", action="store_true", help="mark this change as kept")
    log_parser.add_argument("--notes", default="", help="optional notes")

    args = parser.parse_args()

    if args.command == "init":
        questions = _parse_questions(args.questions)
        return run_init(
            Path(args.root).expanduser().resolve(),
            args.skill_name,
            args.prompt_path,
            questions,
            args.author,
        )

    if args.command == "score":
        answers = _parse_answers(args.answers)
        append = Path(args.append).expanduser().resolve() if args.append else None
        return run_score(answers, append, args.skill_name)

    if args.command == "log-iteration":
        return run_log_iteration(
            Path(args.root).expanduser().resolve(),
            args.iteration,
            args.change,
            args.before,
            args.after,
            args.keep,
            args.notes,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
