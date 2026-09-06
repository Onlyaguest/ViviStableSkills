#!/usr/bin/env python3
"""Copy the bundled Remotion starter into a new, non-destructive target."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="New or empty destination directory")
    args = parser.parse_args()

    skill_dir = Path(__file__).resolve().parents[1]
    template = skill_dir / "assets" / "remotion-template"
    target = Path(args.target).expanduser().resolve()

    if not template.is_dir():
        parser.error(f"template missing: {template}")
    if target.exists() and not target.is_dir():
        parser.error(f"target is not a directory: {target}")
    if target.exists() and any(target.iterdir()):
        parser.error(f"refusing to overwrite non-empty target: {target}")

    target.mkdir(parents=True, exist_ok=True)
    for source in template.iterdir():
        destination = target / source.name
        if source.is_dir():
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)

    (target / "public" / "assets").mkdir(parents=True, exist_ok=True)
    (target / "public" / "audio").mkdir(parents=True, exist_ok=True)
    (target / "narration" / "transcription").mkdir(parents=True, exist_ok=True)

    print(f"scaffolded: {target}")
    print(f"edit: {target / 'story.json'}")
    print("next: npm install && npm run check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
