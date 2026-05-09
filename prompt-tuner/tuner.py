from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PROMPT_FILE = ROOT / "prompt.txt"
CASES_FILE = ROOT / "cases.yaml"
ENV_FILE = ROOT / ".env"
VERSION_PREFIX = "# Version:"


def eprint(message: str) -> None:
    print(message, file=sys.stderr)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Regression test runner for system prompts using a golden dataset."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate local files only; no API calls",
    )
    parser.add_argument(
        "--provider",
        choices=("openai", "gemini"),
        help="override provider from .env",
    )
    parser.add_argument(
        "--model",
        help="override model name from .env",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="run only the first N cases",
    )
    return parser.parse_args()


def parse_cases_fallback(raw_text: str) -> list[dict[str, str]]:
    cases: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw_line in raw_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("- input:"):
            if current:
                if "input" not in current or "expected" not in current:
                    raise RuntimeError("Invalid cases.yaml: each case needs input and expected")
                cases.append(current)
            value = line.split(":", 1)[1].strip().strip("'").strip('"')
            current = {"input": value}
            continue
        if line.startswith("expected:"):
            if current is None:
                raise RuntimeError("Invalid cases.yaml: expected appeared before input")
            value = line.split(":", 1)[1].strip().strip("'").strip('"')
            current["expected"] = value
    if current:
        if "input" not in current or "expected" not in current:
            raise RuntimeError("Invalid cases.yaml: each case needs input and expected")
        cases.append(current)
    return cases


def load_resources(use_fallback_parser: bool = False) -> tuple[str, list[dict[str, str]]]:
    try:
        prompt_text = PROMPT_FILE.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        raise RuntimeError(f"Missing file: {PROMPT_FILE}")
    except Exception as exc:
        raise RuntimeError(f"Failed to read {PROMPT_FILE}: {exc}")

    try:
        raw_text = CASES_FILE.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise RuntimeError(f"Missing file: {CASES_FILE}")
    except Exception as exc:
        raise RuntimeError(f"Failed to read {CASES_FILE}: {exc}")

    if use_fallback_parser:
        raw_cases = parse_cases_fallback(raw_text)
    else:
        try:
            import yaml
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                f"Missing dependency for full parsing: {exc.name}. Run `pip install -r requirements.txt`."
            )
        try:
            raw_cases = yaml.safe_load(raw_text)
        except Exception as exc:
            raise RuntimeError(f"Failed to parse {CASES_FILE}: {exc}")

        if not isinstance(raw_cases, list):
            raise RuntimeError("cases.yaml must contain a top-level list")

    cases: list[dict[str, str]] = []
    for index, case in enumerate(raw_cases, start=1):
        if not isinstance(case, dict):
            raise RuntimeError(f"Case #{index} must be a mapping")
        if "input" not in case or "expected" not in case:
            raise RuntimeError(f"Case #{index} must include both input and expected")
        cases.append(
            {
                "input": str(case["input"]),
                "expected": str(case["expected"]).strip(),
            }
        )

    return prompt_text, cases


def check_local_files() -> int:
    try:
        prompt_text, cases = load_resources(use_fallback_parser=True)
    except RuntimeError as exc:
        eprint(f"❌ {exc}")
        return 1

    if not prompt_text.startswith(VERSION_PREFIX):
        eprint("❌ prompt.txt must start with a version header like '# Version: X.Y.Z (YYYY-MM-DD)'")
        return 1

    if not cases:
        eprint("❌ cases.yaml must contain at least one test case")
        return 1

    print("✅ Local prompt-tuner structure check passed")
    print(f"Prompt file: {PROMPT_FILE.name}")
    print(f"Cases file: {CASES_FILE.name}")
    print(f"Cases count: {len(cases)}")
    print(f"Version header: {prompt_text.splitlines()[0]}")
    return 0


def resolve_runtime(args: argparse.Namespace) -> tuple[str, str, str]:
    try:
        from dotenv import load_dotenv
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            f"Missing dependency for runtime config: {exc.name}. Run `pip install -r requirements.txt`."
        )
    load_dotenv(ENV_FILE)
    provider = (args.provider or os.getenv("PROVIDER") or "gemini").strip().lower()
    if provider not in {"openai", "gemini"}:
        raise RuntimeError(f"Unsupported provider: {provider}")
    model = (args.model or os.getenv(f"{provider.upper()}_MODEL") or "").strip()
    api_key = (os.getenv(f"{provider.upper()}_API_KEY") or "").strip()
    if not model:
        raise RuntimeError(f"Missing model configuration: {provider.upper()}_MODEL")
    if not api_key:
        raise RuntimeError(f"Missing API key: {provider.upper()}_API_KEY")
    return provider, model, api_key


def call_gemini(system_prompt: str, text: str, model: str, api_key: str) -> str:
    import requests

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": f"{system_prompt}\n\n用户原始输入:\n{text}"}],
            }
        ],
        "generationConfig": {
            "temperature": 0.5,
            "maxOutputTokens": 800,
        },
    }
    response = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=90)
    response.raise_for_status()
    data = response.json()
    if "candidates" in data and data["candidates"]:
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    return f"🔴 API Error: {json.dumps(data, ensure_ascii=False)}"


def call_openai(system_prompt: str, text: str, model: str, api_key: str) -> str:
    import requests

    url = "https://api.openai.com/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
        "temperature": 0.0,
        "max_tokens": 800,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    response = requests.post(url, headers=headers, json=payload, timeout=90)
    response.raise_for_status()
    data = response.json()
    if "choices" in data and data["choices"]:
        return data["choices"][0]["message"]["content"].strip()
    return f"🔴 API Error: {json.dumps(data, ensure_ascii=False)}"


def run_inference(provider: str, model: str, api_key: str, system_prompt: str, text: str) -> str:
    if provider == "gemini":
        return call_gemini(system_prompt, text, model, api_key)
    if provider == "openai":
        return call_openai(system_prompt, text, model, api_key)
    raise RuntimeError(f"Unsupported provider: {provider}")


def run_regression(args: argparse.Namespace) -> int:
    try:
        system_prompt, cases = load_resources()
        provider, model, api_key = resolve_runtime(args)
    except RuntimeError as exc:
        eprint(f"❌ {exc}")
        return 1

    selected_cases = cases[: args.limit] if args.limit and args.limit > 0 else cases
    print(f"🔹 Tuning with Provider: {provider} | Model: {model}")
    print(f"🔹 Cases: {len(selected_cases)}\n")
    print(f"{'INPUT':<30} | {'EXPECTED':<30} | {'ACTUAL':<30} | STATUS")
    print("-" * 110)

    success_count = 0
    padding = 30

    for index, case in enumerate(selected_cases, start=1):
        inp = case["input"]
        expected = case["expected"]
        try:
            actual = run_inference(provider, model, api_key, system_prompt, inp)
            if len(selected_cases) > 5 and index < len(selected_cases):
                time.sleep(1)
        except Exception as exc:
            actual = f"💥 Request Error: {exc}"

        status = "✅" if actual == expected else "⚠️"
        if status == "✅":
            success_count += 1

        disp_inp = (inp[: padding - 3] + "...") if len(inp) > padding else inp
        disp_exp = (expected[: padding - 3] + "...") if len(expected) > padding else expected
        disp_act = (actual[: padding - 3] + "...") if len(actual) > padding else actual

        print(f"{disp_inp:<30} | {disp_exp:<30} | {disp_act:<30} | {status}")
        if status != "✅":
            print(f"  -> Raw Actual: {actual}")

    print("-" * 110)
    print(f"🏁 Result: {success_count}/{len(selected_cases)} passed.")
    return 0 if success_count == len(selected_cases) else 2


def main() -> int:
    args = parse_args()
    if args.check:
        return check_local_files()
    return run_regression(args)


if __name__ == "__main__":
    raise SystemExit(main())
