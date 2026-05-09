from __future__ import annotations

import argparse
import sys


QUESTIONS = [
    ("difference", '跟"直接丢给 AI"有什么明显区别？'),
    ("vertical", "有行业偏向性或场景偏向性吗？"),
    ("learning", "会越用越聪明吗？"),
    ("hard_for_user", "用户自己很难做到吗？"),
    ("moat", "有壁垒吗？"),
]

EXAMPLES = {
    "generic-email-summary": {
        "title": "通用的总结邮件 skill",
        "answers": [False, False, False, False, False],
    },
    "lawyer-email-assistant": {
        "title": "律师邮件助手",
        "answers": [True, True, True, True, True],
    },
    "energy-os": {
        "title": "创业者精力风控系统",
        "answers": [True, True, True, True, True],
    },
    "wechat-reader-v1": {
        "title": "微信文章阅读器（当前版本）",
        "answers": [False, False, False, False, False],
    },
    "wechat-reader-v2": {
        "title": "微信文章阅读器（深化版）",
        "answers": [True, True, True, True, True],
    },
}


def _parse_answers(raw: str) -> list[bool]:
    tokens = [chunk.strip().lower() for chunk in raw.split(",") if chunk.strip()]
    if len(tokens) != len(QUESTIONS):
        raise ValueError(f"Expected {len(QUESTIONS)} answers, got {len(tokens)}")
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
    parsed: list[bool] = []
    for token in tokens:
        if token not in mapping:
            raise ValueError(f"Unsupported answer token: {token}")
        parsed.append(mapping[token])
    return parsed


def _decision(score: int) -> str:
    if score == 5:
        return "立即做"
    if score >= 3:
        return "可以做，但需要深化"
    if score >= 1:
        return "不要做"
    return "绝对不要做"


def _print_template() -> None:
    print("Skills Filter - 5 问快速筛选")
    for idx, (_, text) in enumerate(QUESTIONS, start=1):
        print(f"{idx}. {text}")


def _print_result(title: str, answers: list[bool]) -> None:
    score = sum(1 for value in answers if value)
    print(f"评估对象: {title}")
    print()
    for idx, ((_, text), answer) in enumerate(zip(QUESTIONS, answers), start=1):
        marker = "✅" if answer else "❌"
        print(f"{idx}. {text} {marker}")
    print()
    print(f"评分: {score}/{len(QUESTIONS)}")
    print(f"结论: {_decision(score)}")


def _run_interactive(title: str) -> int:
    answers: list[bool] = []
    print(f"开始评估: {title}")
    print("请输入 y / n")
    for _, text in QUESTIONS:
        while True:
            raw = input(f"- {text} ").strip().lower()
            if raw in {"y", "yes"}:
                answers.append(True)
                break
            if raw in {"n", "no"}:
                answers.append(False)
                break
            print("请输入 y 或 n")
    print()
    _print_result(title, answers)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="skills-filter: 5-question gate for deciding whether a new skill is worth building"
    )
    parser.add_argument("--template", action="store_true", help="print the five questions")
    parser.add_argument("--answers", help="comma-separated answers, e.g. y,n,y,n,y")
    parser.add_argument("--title", default="未命名候选 skill", help="name of the candidate skill")
    parser.add_argument(
        "--example",
        choices=sorted(EXAMPLES.keys()),
        help="run a built-in example evaluation",
    )
    parser.add_argument("--interactive", action="store_true", help="answer the questions interactively")
    args = parser.parse_args()

    if args.template:
        _print_template()
        return 0

    if args.example:
        example = EXAMPLES[args.example]
        _print_result(example["title"], example["answers"])
        return 0

    if args.interactive:
        return _run_interactive(args.title)

    if args.answers:
        try:
            answers = _parse_answers(args.answers)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        _print_result(args.title, answers)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
