#!/usr/bin/env python3
"""Generate scene narration with Cohub CLI and record auditable metadata."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any


DEFAULT_MODEL = "qwen-audio-3.0-tts-plus"
DEFAULT_VOICE = (
    "自然、温暖、清晰的中文声音，像朋友在桌边轻松讲述一次真实的工作流实验；"
    "克制、不播音腔，语速中等，数字和英文产品名读清楚。"
)


def safe_relative(value: str) -> bool:
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and "://" not in value


def duration_seconds(path: Path) -> float | None:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return None
    result = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        return round(float(result.stdout.strip()), 3) if result.returncode == 0 else None
    except ValueError:
        return None


def cost_from(payload: dict[str, Any]) -> float | None:
    billing = payload.get("billing")
    if isinstance(billing, dict) and isinstance(billing.get("amountUsd"), (int, float)):
        return float(billing["amountUsd"])
    return float(payload["cost"]) if isinstance(payload.get("cost"), (int, float)) else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("story")
    parser.add_argument("--space-id", default=os.environ.get("COHUB_SPACE_ID"))
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--voice-prompt", default=DEFAULT_VOICE)
    parser.add_argument("--timeout-ms", type=int, default=180_000)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    story_path = Path(args.story).expanduser().resolve()
    project = story_path.parent
    data = json.loads(story_path.read_text(encoding="utf-8"))
    scenes = data.get("scenes", [])
    jobs: list[tuple[dict[str, Any], Path]] = []
    for scene in scenes:
        text = scene.get("narration")
        audio = scene.get("audio")
        if not text and not audio:
            continue
        if not isinstance(text, str) or not text.strip():
            parser.error(f"scene {scene.get('id')} has audio but no narration")
        if args.model == DEFAULT_MODEL and len(text) > 200:
            parser.error(f"scene {scene.get('id')} narration exceeds Qwen 200-char limit")
        if not isinstance(audio, str) or not safe_relative(audio):
            parser.error(f"scene {scene.get('id')} needs a safe public-relative audio path")
        destination = project / "public" / audio
        jobs.append((scene, destination))

    plan = {
        "model": args.model,
        "spaceId": args.space_id,
        "segments": [
            {"sceneId": scene["id"], "characters": len(scene["narration"]), "output": str(path)}
            for scene, path in jobs
        ],
    }
    if args.dry_run:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0
    if not args.space_id:
        parser.error("--space-id or COHUB_SPACE_ID is required")
    executable = shutil.which("cohub")
    if not executable:
        parser.error("cohub CLI is not installed")

    subprocess.run([executable, "auth", "whoami", "--json"], capture_output=True, check=True)
    results: list[dict[str, Any]] = []
    for scene, destination in jobs:
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() and destination.stat().st_size > 1024 and not args.force:
            results.append(
                {
                    "sceneId": scene["id"],
                    "path": str(destination.relative_to(project)),
                    "status": "reused",
                    "durationSeconds": duration_seconds(destination),
                    "costUsd": 0,
                }
            )
            continue
        command = [
            executable,
            "-s",
            args.space_id,
            "generate",
            scene["narration"],
            "--model",
            args.model,
            "--output",
            str(destination),
            "--timeout-ms",
            str(args.timeout_ms),
            "--json",
            "--meta",
            json.dumps({"voice_prompt": args.voice_prompt}, ensure_ascii=False),
        ]
        environment = os.environ.copy()
        environment["COHUB_CLI_AUTO_UPDATE"] = "0"
        run = subprocess.run(command, capture_output=True, text=True, env=environment, check=False)
        if run.returncode != 0:
            raise RuntimeError(f"Cohub TTS failed for {scene['id']}: {run.stderr.strip()}")
        payload = json.loads(run.stdout)
        if not destination.is_file() or destination.stat().st_size <= 1024:
            raise RuntimeError(f"Cohub did not save usable audio for {scene['id']}")
        results.append(
            {
                "sceneId": scene["id"],
                "path": str(destination.relative_to(project)),
                "status": "generated",
                "durationSeconds": duration_seconds(destination),
                "requestId": payload.get("requestId"),
                "taskRunId": payload.get("taskRunId"),
                "costUsd": cost_from(payload),
            }
        )

    known_costs = [item["costUsd"] for item in results if isinstance(item.get("costUsd"), (int, float))]
    manifest = {
        "createdAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "story": str(story_path),
        "model": args.model,
        "spaceId": args.space_id,
        "voicePrompt": args.voice_prompt,
        "segments": results,
        "knownCostUsd": round(sum(known_costs), 6),
    }
    manifest_path = project / "narration" / "tts-manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "manifest": str(manifest_path), **plan}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
