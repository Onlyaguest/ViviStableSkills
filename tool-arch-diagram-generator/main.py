from __future__ import annotations

import argparse
import html
import os
import sys
from pathlib import Path


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


MERMAID_STARTERS = (
    "sequenceDiagram",
    "flowchart",
    "graph",
    "classDiagram",
    "stateDiagram",
    "stateDiagram-v2",
    "erDiagram",
    "gantt",
    "journey",
    "mindmap",
    "timeline",
    "sankey-beta",
    "quadrantChart",
    "requirementDiagram",
    "c4context",
    "c4container",
    "c4component",
    "c4dynamic",
    "c4deployment",
    "pie",
    "gitGraph",
)


def _is_mermaid_start(line: str) -> bool:
    stripped = line.strip()
    lower = stripped.lower()
    for starter in MERMAID_STARTERS:
        if lower.startswith(starter.lower()):
            return True
    return False


def _extract_fenced_mermaid(text: str) -> list[str]:
    blocks: list[str] = []
    in_block = False
    buf: list[str] = []
    for line in text.splitlines():
        if not in_block:
            if line.strip().startswith("```mermaid"):
                in_block = True
                buf = []
            continue
        if line.strip().startswith("```"):
            content = "\n".join(buf).strip()
            if content:
                blocks.append(content)
            in_block = False
            continue
        buf.append(line)
    return blocks


def _extract_unfenced_mermaid(text: str) -> list[str]:
    lines = text.splitlines()
    blocks: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if _is_mermaid_start(line):
            buf = [line.strip()]
            i += 1
            while i < len(lines):
                nxt = lines[i]
                if not nxt.strip():
                    # look ahead to decide if block ends
                    j = i + 1
                    while j < len(lines) and not lines[j].strip():
                        j += 1
                    if j >= len(lines):
                        i = j
                        break
                    if lines[j] == lines[j].lstrip() and not lines[j].lstrip().startswith("%%"):
                        i = j
                        break
                    buf.append("")
                    i += 1
                    continue
                if nxt == nxt.lstrip() and not nxt.lstrip().startswith("%%"):
                    break
                buf.append(nxt)
                i += 1
            content = "\n".join(buf).strip()
            if content:
                blocks.append(content)
            continue
        i += 1
    return blocks


def _extract_mermaid_blocks(text: str) -> list[str]:
    fenced = _extract_fenced_mermaid(text)
    if fenced:
        return fenced
    return _extract_unfenced_mermaid(text)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise
    except Exception as exc:
        raise RuntimeError(f"Failed to read file: {path} ({exc})")


def _load_mermaid_js(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise
    except Exception as exc:
        raise RuntimeError(f"Failed to read Mermaid JS: {path} ({exc})")


def _build_html(title: str, mermaid_js: str, diagrams: list[str]) -> str:
    escaped_title = html.escape(title)
    blocks = []
    for idx, d in enumerate(diagrams, start=1):
        blocks.append(
            "\n".join(
                [
                    f"<section class=\"card\">",
                    f"  <h2>Diagram {idx}</h2>",
                    f"  <div class=\"mermaid\">\n{html.escape(d)}\n  </div>",
                    "</section>",
                ]
            )
        )

    return "\n".join(
        [
            "<!doctype html>",
            "<html lang=\"en\">",
            "<head>",
            "  <meta charset=\"utf-8\">",
            "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">",
            f"  <title>{escaped_title}</title>",
            "  <style>",
            "    :root {",
            "      color-scheme: light;",
            "      --bg: #f5f2ea;",
            "      --card: #ffffff;",
            "      --ink: #1b1b1b;",
            "      --muted: #666666;",
            "      --border: #e0dacb;",
            "    }",
            "    body {",
            "      margin: 0;",
            "      font-family: 'Iowan Old Style', 'Palatino Linotype', 'Book Antiqua', Palatino, serif;",
            "      color: var(--ink);",
            "      background: var(--bg);",
            "    }",
            "    header {",
            "      padding: 24px 28px 8px 28px;",
            "    }",
            "    header h1 {",
            "      margin: 0;",
            "      font-size: 24px;",
            "    }",
            "    header p {",
            "      margin: 6px 0 0 0;",
            "      color: var(--muted);",
            "      font-size: 14px;",
            "    }",
            "    main {",
            "      padding: 12px 20px 28px 20px;",
            "      display: grid;",
            "      grid-template-columns: 1fr;",
            "      gap: 16px;",
            "    }",
            "    .card {",
            "      background: var(--card);",
            "      border: 1px solid var(--border);",
            "      border-radius: 12px;",
            "      padding: 16px;",
            "      box-shadow: 0 6px 18px rgba(40, 30, 10, 0.08);",
            "    }",
            "    .card h2 {",
            "      margin: 0 0 8px 0;",
            "      font-size: 16px;",
            "      color: var(--muted);",
            "      letter-spacing: 0.02em;",
            "      text-transform: uppercase;",
            "    }",
            "    .mermaid {",
            "      overflow-x: auto;",
            "    }",
            "  </style>",
            "</head>",
            "<body>",
            "  <header>",
            f"    <h1>{escaped_title}</h1>",
            "    <p>Generated by tool-arch-diagram-generator (offline)</p>",
            "  </header>",
            "  <main>",
            "\n".join(blocks),
            "  </main>",
            "  <script>",
            mermaid_js,
            "  </script>",
            "  <script>",
            "    mermaid.initialize({ startOnLoad: true, theme: 'neutral' });",
            "  </script>",
            "</body>",
            "</html>",
        ]
    )


def main() -> int:
    tool_dir = Path(__file__).resolve().parent
    _load_dotenv_if_present(tool_dir / ".env")

    parser = argparse.ArgumentParser(
        description="Generate offline HTML architecture diagrams from Mermaid in Markdown"
    )
    parser.add_argument("--input", required=True, help="path to markdown file")
    parser.add_argument(
        "--output",
        default="./dist",
        help="output directory or html file path",
    )
    parser.add_argument(
        "--title",
        default="Architecture Diagrams",
        help="HTML title",
    )
    parser.add_argument(
        "--mermaid-js",
        default=os.getenv("MERMAID_JS_PATH"),
        help="path to mermaid.min.js (offline)",
    )
    parser.add_argument("--dry-run", action="store_true", help="show detected diagrams")

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        _eprint(f"Input file not found: {input_path}")
        return 2

    try:
        raw = _read_text(input_path)
    except Exception as exc:
        _eprint(str(exc))
        return 1

    diagrams = _extract_mermaid_blocks(raw)
    if not diagrams:
        _eprint("No Mermaid diagrams found. Use ```mermaid blocks for reliability.")
        return 1

    if args.dry_run:
        print(f"Found {len(diagrams)} diagram(s)")
        for idx, d in enumerate(diagrams, start=1):
            first_line = d.splitlines()[0] if d.splitlines() else ""
            print(f"- {idx}: {first_line}")
        return 0

    mermaid_js_path = Path(args.mermaid_js) if args.mermaid_js else None
    if mermaid_js_path is None:
        fallback = tool_dir / "mermaid.min.js"
        if fallback.exists():
            mermaid_js_path = fallback
    if not mermaid_js_path:
        _eprint("Missing Mermaid JS. Set MERMAID_JS_PATH or --mermaid-js.")
        return 2
    if not mermaid_js_path.exists():
        _eprint(f"Mermaid JS not found: {mermaid_js_path}")
        return 2

    try:
        mermaid_js = _load_mermaid_js(mermaid_js_path)
    except Exception as exc:
        _eprint(str(exc))
        return 1

    html_text = _build_html(args.title, mermaid_js, diagrams)

    output_path = Path(args.output)
    if output_path.suffix.lower() in {".html", ".htm"}:
        output_file = output_path
        output_file.parent.mkdir(parents=True, exist_ok=True)
    else:
        output_path.mkdir(parents=True, exist_ok=True)
        output_file = output_path / "index.html"

    try:
        output_file.write_text(html_text, encoding="utf-8")
    except Exception as exc:
        _eprint(f"Failed to write output: {output_file} ({exc})")
        return 1

    print(f"OK: {output_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
