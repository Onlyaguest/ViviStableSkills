#!/usr/bin/env python3
"""Validate the data boundary consumed by the Remotion template."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any


SCENE_TYPES = {"hero", "workflow", "chips", "distribution", "closing"}
SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def safe_public_path(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and "://" not in value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("story")
    parser.add_argument("--min-duration", type=float, default=45)
    parser.add_argument("--max-duration", type=float, default=60)
    parser.add_argument("--check-assets", action="store_true")
    args = parser.parse_args()

    story_path = Path(args.story).expanduser().resolve()
    try:
        data = json.loads(story_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        parser.error(str(error))

    errors: list[str] = []
    meta = data.get("meta")
    if not isinstance(meta, dict):
        errors.append("meta must be an object")
    else:
        for field in ("title", "sourceTitle"):
            if not isinstance(meta.get(field), str) or not meta[field].strip():
                errors.append(f"meta.{field} is required")

    scenes = data.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        errors.append("scenes must be a non-empty array")
        scenes = []

    ids: set[str] = set()
    total = 0.0
    for index, scene in enumerate(scenes, start=1):
        prefix = f"scenes[{index - 1}]"
        if not isinstance(scene, dict):
            errors.append(f"{prefix} must be an object")
            continue
        scene_id = scene.get("id")
        if not isinstance(scene_id, str) or not SAFE_ID.fullmatch(scene_id):
            errors.append(f"{prefix}.id must match {SAFE_ID.pattern}")
        elif scene_id in ids:
            errors.append(f"duplicate scene id: {scene_id}")
        else:
            ids.add(scene_id)

        scene_type = scene.get("type")
        if scene_type not in SCENE_TYPES:
            errors.append(f"{prefix}.type must be one of {sorted(SCENE_TYPES)}")
        for field in ("kicker", "title"):
            if not isinstance(scene.get(field), str) or not scene[field].strip():
                errors.append(f"{prefix}.{field} is required")
        duration = scene.get("durationSeconds")
        if not isinstance(duration, (int, float)) or duration <= 0:
            errors.append(f"{prefix}.durationSeconds must be positive")
        else:
            total += float(duration)

        narration = scene.get("narration")
        if narration is not None:
            if not isinstance(narration, str) or not narration.strip():
                errors.append(f"{prefix}.narration must be a non-empty string")
            elif len(narration) > 200:
                errors.append(f"{prefix}.narration is {len(narration)} chars; Qwen limit is 200")

        for field in ("image", "audio"):
            value = scene.get(field)
            if value is None:
                continue
            if not safe_public_path(value):
                errors.append(f"{prefix}.{field} must be a safe public-relative path")
            elif args.check_assets and not (story_path.parent / "public" / value).is_file():
                errors.append(f"missing public asset: {value}")

        if scene_type in {"workflow", "distribution"} and not isinstance(scene.get("steps"), list):
            errors.append(f"{prefix}.steps must be an array")
        if scene_type == "chips" and not isinstance(scene.get("chips"), list):
            errors.append(f"{prefix}.chips must be an array")
        if scene_type == "distribution" and not isinstance(scene.get("total"), (int, float)):
            errors.append(f"{prefix}.total must be numeric")

    if not args.min_duration <= total <= args.max_duration:
        errors.append(
            f"total duration {total:g}s is outside {args.min_duration:g}–{args.max_duration:g}s"
        )

    summary = {"story": str(story_path), "scenes": len(scenes), "durationSeconds": total}
    if errors:
        print(json.dumps({**summary, "ok": False, "errors": errors}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps({**summary, "ok": True}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
