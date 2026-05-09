from __future__ import annotations

import argparse
import csv
import datetime as dt
import html
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


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


def _parse_int(raw: str | None, *, default: int) -> int:
    if raw is None:
        return default
    s = str(raw).strip()
    if not s:
        return default
    try:
        return int(s)
    except ValueError:
        return default


def _parse_bool(raw: str | None, *, default: bool) -> bool:
    if raw is None:
        return default
    s = str(raw).strip().lower()
    if not s:
        return default
    if s in ("1", "true", "yes", "y", "on"):
        return True
    if s in ("0", "false", "no", "n", "off"):
        return False
    return default


def _now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def _slugify(raw: str) -> str:
    s = raw.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "report"


def _safe_relpath(path: Path) -> str:
    return str(path).replace("\\", "/")


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {path}: {e}") from e


def _sniff_delimiter(path: Path) -> str:
    try:
        sample = path.read_text(encoding="utf-8", errors="replace")[:4096]
    except Exception:
        return ","
    if "\t" in sample and sample.count("\t") >= sample.count(","):
        return "\t"
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=[",", "\t", ";", "|"])
        return dialect.delimiter
    except Exception:
        return "," if "," in sample else "\t" if "\t" in sample else ","


def _read_table_from_path(path: Path, *, max_rows: int) -> tuple[list[str], list[list[str]]]:
    if not path.exists():
        raise FileNotFoundError(str(path))

    suffix = path.suffix.lower()
    if suffix == ".csv" or suffix == ".tsv":
        delimiter = "\t" if suffix == ".tsv" else _sniff_delimiter(path)
        with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
            reader = csv.reader(f, delimiter=delimiter)
            try:
                header = next(reader)
            except StopIteration:
                return [], []
            columns = [str(x) for x in header]
            body: list[list[str]] = []
            for row in reader:
                if not row or not any(str(c).strip() for c in row):
                    continue
                body.append([str(c) for c in row])
                if len(body) >= max_rows:
                    break
        return columns, body

    if suffix == ".json":
        data = _read_json(path)
        if isinstance(data, list) and (not data or isinstance(data[0], dict)):
            cols: list[str] = []
            seen = set()
            for item in data:
                if not isinstance(item, dict):
                    continue
                for k in item.keys():
                    if k not in seen:
                        seen.add(k)
                        cols.append(str(k))
            body: list[list[str]] = []
            for item in data[:max_rows]:
                if not isinstance(item, dict):
                    continue
                body.append([str(item.get(c, "")) for c in cols])
            return cols, body

        if isinstance(data, list) and (not data or isinstance(data[0], list)):
            body2 = [[str(c) for c in r] for r in data[:max_rows] if isinstance(r, list)]
            cols2 = [f"c{i+1}" for i in range(max((len(r) for r in body2), default=0))]
            return cols2, body2

        raise ValueError(f"Unsupported table JSON structure: {path}")

    raise ValueError(f"Unsupported table file type: {path}")


def _hash_color(name: str) -> str:
    h = 0
    for ch in name:
        h = (h * 131 + ord(ch)) % 360
    return f"hsl({h}, 72%, 60%)"


def _svg_bar_chart(items: list[tuple[str, float]], *, width: int = 980) -> str:
    margin_left = 180
    margin_right = 18
    margin_top = 18
    margin_bottom = 18
    row_h = 24

    if not items:
        return "<div class='muted'>No chart data.</div>"

    max_v = max((v for _, v in items), default=1.0)
    max_v = max(max_v, 1e-9)

    height = margin_top + margin_bottom + row_h * len(items)
    inner_w = width - margin_left - margin_right

    def w_scale(v: float) -> float:
        return inner_w * (v / max_v)

    parts: list[str] = [
        f"<svg viewBox='0 0 {width} {height}' xmlns='http://www.w3.org/2000/svg' role='img'>"
    ]
    for idx, (label, value) in enumerate(items):
        y = margin_top + idx * row_h
        bar_w = max(0.0, w_scale(value))
        parts.append(
            f"<text x='{margin_left - 10}' y='{y + 16}' text-anchor='end' class='svg-label'>{html.escape(label)}</text>"
        )
        parts.append(
            f"<rect x='{margin_left}' y='{y + 6}' width='{bar_w:.2f}' height='10' rx='5' fill='rgba(96,165,250,.92)'/>"
        )
        parts.append(
            f"<text x='{width - margin_right}' y='{y + 16}' text-anchor='end' class='svg-value'>{value:g}</text>"
        )
    parts.append("</svg>")
    return "".join(parts)


def _downsample_points(points: list[tuple[str, float]], *, max_points: int) -> list[tuple[str, float]]:
    if max_points <= 0 or len(points) <= max_points:
        return points
    step = (len(points) - 1) / (max_points - 1)
    out: list[tuple[str, float]] = []
    for i in range(max_points):
        idx = int(round(i * step))
        out.append(points[min(idx, len(points) - 1)])
    return out


def _svg_line_chart(
    series: list[tuple[str, list[tuple[str, float]]]],
    *,
    width: int = 980,
    height: int = 360,
    max_points: int,
) -> str:
    if not series:
        return "<div class='muted'>No chart data.</div>"

    margin = {"l": 46, "r": 16, "t": 16, "b": 34}
    inner_w = width - margin["l"] - margin["r"]
    inner_h = height - margin["t"] - margin["b"]

    cleaned: list[tuple[str, list[tuple[str, float]]]] = []
    all_y: list[float] = []
    all_x_labels: list[str] = []
    for name, pts in series:
        pts2 = _downsample_points([(str(x), float(y)) for x, y in pts], max_points=max_points)
        if pts2:
            all_x_labels = all_x_labels or [x for x, _ in pts2]
            all_y.extend([y for _, y in pts2])
        cleaned.append((name, pts2))

    if not all_y or not all_x_labels:
        return "<div class='muted'>No chart data.</div>"

    y_min = min(all_y)
    y_max = max(all_y)
    if y_min == y_max:
        y_min -= 1
        y_max += 1

    def x_scale(i: int, n: int) -> float:
        if n <= 1:
            return margin["l"] + inner_w / 2
        return margin["l"] + inner_w * (i / (n - 1))

    def y_scale(v: float) -> float:
        t = (v - y_min) / (y_max - y_min)
        return margin["t"] + inner_h * (1 - t)

    parts: list[str] = [
        f"<svg viewBox='0 0 {width} {height}' xmlns='http://www.w3.org/2000/svg' role='img'>",
        f"<rect x='0' y='0' width='{width}' height='{height}' fill='rgba(15,23,42,0.0)'/>",
    ]

    ticks = 4
    for i in range(ticks + 1):
        v = y_min + (y_max - y_min) * (i / ticks)
        y = y_scale(v)
        parts.append(
            f"<line x1='{margin['l']}' y1='{y:.2f}' x2='{width - margin['r']}' y2='{y:.2f}' stroke='rgba(148,163,184,.22)' stroke-width='1'/>"
        )
        parts.append(
            f"<text x='{margin['l'] - 8}' y='{y + 4:.2f}' text-anchor='end' class='svg-tick'>{v:g}</text>"
        )

    n = len(all_x_labels)
    label_every = max(1, n // 6)
    for i, xlab in enumerate(all_x_labels):
        if i % label_every != 0 and i != n - 1:
            continue
        x = x_scale(i, n)
        parts.append(
            f"<text x='{x:.2f}' y='{height - 10}' text-anchor='middle' class='svg-tick'>{html.escape(xlab)}</text>"
        )

    for name, pts in cleaned:
        if not pts:
            continue
        color = _hash_color(name)
        points_attr = " ".join(
            f"{x_scale(i, len(pts)):.2f},{y_scale(y):.2f}" for i, (_, y) in enumerate(pts)
        )
        parts.append(
            f"<polyline fill='none' stroke='{color}' stroke-width='2.2' points='{points_attr}'/>"
        )

    parts.append("</svg>")
    parts.append("<div class='legend'>")
    for name, _ in cleaned:
        parts.append(
            f"<span class='key'><span class='dot' style='background:{_hash_color(name)}'></span>{html.escape(name)}</span>"
        )
    parts.append("</div>")
    return "".join(parts)


def _md_to_html(md: str) -> str:
    lines = md.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    in_code = False
    in_list = False

    def flush_list() -> None:
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    def inline(s: str) -> str:
        esc = html.escape(s)
        esc = re.sub(r"`([^`]+)`", r"<code>\1</code>", esc)
        esc = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", esc)
        esc = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", esc)

        def link_repl(m: re.Match[str]) -> str:
            text = m.group(1)
            url = m.group(2)
            url_esc = html.escape(url, quote=True)
            return f"<a href='{url_esc}' target='_blank' rel='noreferrer'>{text}</a>"

        esc = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link_repl, esc)
        return esc

    for raw in lines:
        line = raw.rstrip("\n")
        if line.strip().startswith("```"):
            flush_list()
            if not in_code:
                in_code = True
                out.append("<pre><code>")
            else:
                in_code = False
                out.append("</code></pre>")
            continue

        if in_code:
            out.append(html.escape(line) + "\n")
            continue

        if not line.strip():
            flush_list()
            continue

        if line.startswith("#"):
            flush_list()
            m = re.match(r"^(#{1,4})\s+(.*)$", line)
            if m:
                lvl = len(m.group(1))
                content = inline(m.group(2))
                out.append(f"<h{lvl}>{content}</h{lvl}>")
                continue

        if re.match(r"^\s*-\s+", line):
            if not in_list:
                out.append("<ul>")
                in_list = True
            item = re.sub(r"^\s*-\s+", "", line)
            out.append(f"<li>{inline(item)}</li>")
            continue

        flush_list()
        out.append(f"<p>{inline(line)}</p>")

    flush_list()
    if in_code:
        out.append("</code></pre>")
    return "".join(out)


@dataclass(frozen=True)
class Report:
    slug: str
    title: str
    subtitle: str
    tags: list[str]
    updated_at: str
    blocks: list[dict[str, Any]]
    src_path: Path


def _parse_float(raw: str) -> float | None:
    s = str(raw).strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _parse_dt(raw: str) -> dt.datetime | None:
    s = str(raw).strip()
    if not s:
        return None
    s2 = s.replace("Z", "+00:00")
    try:
        return dt.datetime.fromisoformat(s2)
    except Exception:
        pass
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M:%S", "%Y/%m/%d %H:%M", "%Y-%m-%d"):
        try:
            return dt.datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


@dataclass(frozen=True)
class _CsvColStat:
    non_empty: int
    numeric_ok: int
    dt_ok: int
    uniques: set[str]


@dataclass(frozen=True)
class _CsvProfile:
    columns: list[str]
    rows_scanned: int
    col_stats: dict[str, _CsvColStat]


def _profile_csv(path: Path, *, max_rows: int, max_unique: int) -> _CsvProfile:
    delimiter = "\t" if path.suffix.lower() == ".tsv" else _sniff_delimiter(path)
    with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        columns = [c for c in (reader.fieldnames or []) if c]
        stats: dict[str, dict[str, Any]] = {
            c: {"non_empty": 0, "numeric_ok": 0, "dt_ok": 0, "uniques": set()} for c in columns
        }
        scanned = 0
        for row in reader:
            scanned += 1
            for c in columns:
                v = (row.get(c) or "").strip()
                if not v:
                    continue
                st = stats[c]
                st["non_empty"] += 1
                if _parse_float(v) is not None:
                    st["numeric_ok"] += 1
                if _parse_dt(v) is not None:
                    st["dt_ok"] += 1
                if len(st["uniques"]) <= max_unique:
                    st["uniques"].add(v)
            if scanned >= max_rows:
                break
    col_stats = {
        c: _CsvColStat(
            non_empty=int(stats[c]["non_empty"]),
            numeric_ok=int(stats[c]["numeric_ok"]),
            dt_ok=int(stats[c]["dt_ok"]),
            uniques=set(stats[c]["uniques"]),
        )
        for c in columns
    }
    return _CsvProfile(columns=columns, rows_scanned=scanned, col_stats=col_stats)


def _choose_best_columns(profile: _CsvProfile, *, max_unique: int) -> tuple[str | None, str | None, str | None]:
    dt_cols: list[tuple[float, str]] = []
    num_cols: list[tuple[float, str]] = []
    cat_cols: list[tuple[int, str]] = []

    for c in profile.columns:
        st = profile.col_stats.get(c)
        if not st or st.non_empty <= 0:
            continue
        dt_ratio = st.dt_ok / st.non_empty if st.non_empty else 0.0
        num_ratio = st.numeric_ok / st.non_empty if st.non_empty else 0.0
        if dt_ratio >= 0.7:
            dt_cols.append((dt_ratio, c))
        if num_ratio >= 0.7:
            num_cols.append((num_ratio, c))
        uniq = len(st.uniques)
        if 2 <= uniq <= max_unique:
            cat_cols.append((uniq, c))

    dt_col = max(dt_cols, default=(0.0, None))[1]
    num_col = max(num_cols, default=(0.0, None))[1]
    cat_col = min(cat_cols, default=(10**9, None))[1]
    return dt_col, num_col, cat_col


def _auto_blocks_from_csv(
    path: Path,
    *,
    max_table_rows: int,
    profile_rows: int,
    max_unique_categories: int,
    max_chart_points: int,
) -> list[dict[str, Any]]:
    profile = _profile_csv(path, max_rows=profile_rows, max_unique=max_unique_categories)
    dt_col, num_col, cat_col = _choose_best_columns(profile, max_unique=max_unique_categories)

    md_lines = [
        f"**Source**: `{path.name}`",
        f"**Columns**: {', '.join([f'`{c}`' for c in profile.columns])}" if profile.columns else "**Columns**: (none)",
        f"**Profiled rows**: {profile.rows_scanned} (limit `{profile_rows}`)",
        f"**Preview rows**: {max_table_rows} (limit `{max_table_rows}`)",
    ]
    if dt_col and num_col:
        md_lines.append(f"**Detected**: time column `{dt_col}`, numeric column `{num_col}`")
    elif num_col and cat_col:
        md_lines.append(f"**Detected**: numeric column `{num_col}`, category column `{cat_col}`")

    blocks: list[dict[str, Any]] = [
        {"type": "markdown", "content": "\n".join(["# CSV Auto Report", "", *md_lines])},
        {"type": "table", "title": "Data preview", "path": path.name},
    ]

    if dt_col and num_col:
        delimiter = "\t" if path.suffix.lower() == ".tsv" else _sniff_delimiter(path)
        sums_by_x: dict[str, float] = {}
        counts_by_x: dict[str, int] = {}
        with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            scanned = 0
            for row in reader:
                scanned += 1
                x_raw = (row.get(dt_col) or "").strip()
                y_raw = (row.get(num_col) or "").strip()
                d = _parse_dt(x_raw)
                y = _parse_float(y_raw)
                if d is None or y is None:
                    continue
                x = d.date().isoformat() if len(x_raw) <= 10 else d.isoformat(timespec="seconds")
                sums_by_x[x] = sums_by_x.get(x, 0.0) + y
                counts_by_x[x] = counts_by_x.get(x, 0) + 1
                if scanned >= profile_rows:
                    break
        pts = [{"x": x, "y": sums_by_x[x] / counts_by_x[x]} for x in sorted(sums_by_x.keys())]
        blocks.append(
            {
                "type": "chart",
                "title": f"{num_col} over time",
                "kind": "line",
                "series": [{"name": num_col, "points": pts}],
            }
        )

    if num_col and cat_col:
        delimiter = "\t" if path.suffix.lower() == ".tsv" else _sniff_delimiter(path)
        sums: dict[str, float] = {}
        counts: dict[str, int] = {}
        with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            scanned = 0
            for row in reader:
                scanned += 1
                cval = (row.get(cat_col) or "").strip()
                y = _parse_float((row.get(num_col) or "").strip())
                if not cval or y is None:
                    continue
                sums[cval] = sums.get(cval, 0.0) + y
                counts[cval] = counts.get(cval, 0) + 1
                if scanned >= profile_rows:
                    break
        items: list[tuple[str, float]] = []
        for k, s in sums.items():
            n = counts.get(k, 0)
            if n > 0:
                items.append((k, s / n))
        items.sort(key=lambda x: x[1], reverse=True)
        data = [{"label": k, "value": v} for k, v in items[:max_unique_categories]]
        if data:
            blocks.append({"type": "chart", "title": f"Avg {num_col} by {cat_col}", "kind": "bar", "data": data})

    return blocks


def _load_report_from_json(path: Path) -> Report | None:
    raw = _read_json(path)
    if not isinstance(raw, dict):
        _eprint(f"Skip non-object report JSON: {path}")
        return None

    slug = str(raw.get("slug") or path.stem)
    slug2 = _slugify(slug)
    title = str(raw.get("title") or slug2)
    subtitle = str(raw.get("subtitle") or "")
    tags = raw.get("tags") or []
    tags2 = [str(x) for x in tags] if isinstance(tags, list) else []
    updated_at = str(raw.get("updated_at") or "")
    if not updated_at:
        updated_at = dt.datetime.fromtimestamp(path.stat().st_mtime, tz=dt.timezone.utc).date().isoformat()

    blocks = raw.get("blocks") or []
    blocks2: list[dict[str, Any]] = blocks if isinstance(blocks, list) else []

    return Report(
        slug=slug2,
        title=title,
        subtitle=subtitle,
        tags=tags2,
        updated_at=updated_at,
        blocks=blocks2,
        src_path=path,
    )


def _load_report_from_csv(
    path: Path,
    *,
    max_table_rows: int,
    profile_rows: int,
    max_unique_categories: int,
    max_chart_points: int,
) -> Report:
    title = path.stem.replace("_", " ").replace("-", " ").strip() or path.stem
    slug = _slugify(path.stem)
    updated_at = dt.datetime.fromtimestamp(path.stat().st_mtime, tz=dt.timezone.utc).date().isoformat()
    blocks = _auto_blocks_from_csv(
        path,
        max_table_rows=max_table_rows,
        profile_rows=profile_rows,
        max_unique_categories=max_unique_categories,
        max_chart_points=max_chart_points,
    )
    return Report(
        slug=slug,
        title=title,
        subtitle=f"Auto from {path.name}",
        tags=["csv", "auto"],
        updated_at=updated_at,
        blocks=blocks,
        src_path=path,
    )


def _extract_body_html(raw: str) -> str:
    m = re.search(r"<body[^>]*>(.*)</body>", raw, flags=re.IGNORECASE | re.DOTALL)
    if m:
        return m.group(1).strip()
    return raw.strip()


def _load_report_from_html(path: Path) -> Report:
    title = path.stem.replace("_", " ").replace("-", " ").strip() or path.stem
    slug = _slugify(path.stem)
    updated_at = dt.datetime.fromtimestamp(path.stat().st_mtime, tz=dt.timezone.utc).date().isoformat()
    raw = path.read_text(encoding="utf-8", errors="replace")
    blocks = [{"type": "html", "content": _extract_body_html(raw)}]
    return Report(
        slug=slug,
        title=title,
        subtitle=f"From {path.name}",
        tags=["html"],
        updated_at=updated_at,
        blocks=blocks,
        src_path=path,
    )


def _load_report_from_markdown(path: Path) -> Report:
    title = path.stem.replace("_", " ").replace("-", " ").strip() or path.stem
    slug = _slugify(path.stem)
    updated_at = dt.datetime.fromtimestamp(path.stat().st_mtime, tz=dt.timezone.utc).date().isoformat()
    raw = path.read_text(encoding="utf-8", errors="replace")
    blocks = [{"type": "markdown", "content": raw}]
    return Report(
        slug=slug,
        title=title,
        subtitle=f"From {path.name}",
        tags=["markdown"],
        updated_at=updated_at,
        blocks=blocks,
        src_path=path,
    )


def _load_reports(
    reports_dir: Path,
    *,
    auto_from_csv: bool,
    max_table_rows: int,
    profile_rows: int,
    max_unique_categories: int,
    max_chart_points: int,
) -> list[Report]:
    if not reports_dir.exists():
        return []

    reports: list[Report] = []
    json_stems: set[str] = set()
    for path in sorted(reports_dir.glob("*.json")):
        if path.name.startswith("_"):
            continue
        json_stems.add(path.stem.lower())
        r = _load_report_from_json(path)
        if r:
            reports.append(r)

    if auto_from_csv:
        for suffix in (".csv", ".tsv"):
            for path in sorted(reports_dir.glob(f"*{suffix}")):
                if path.name.startswith("_"):
                    continue
                if path.stem.lower() in json_stems:
                    continue
                try:
                    reports.append(
                        _load_report_from_csv(
                            path,
                            max_table_rows=max_table_rows,
                            profile_rows=profile_rows,
                            max_unique_categories=max_unique_categories,
                            max_chart_points=max_chart_points,
                        )
                    )
                except Exception as e:
                    _eprint(f"Failed to auto-load CSV report: {path}: {e}")

    for suffix, loader in ((".html", _load_report_from_html), (".md", _load_report_from_markdown)):
        for path in sorted(reports_dir.glob(f"*{suffix}")):
            if path.name.startswith("_"):
                continue
            if path.stem.lower() in json_stems:
                continue
            try:
                reports.append(loader(path))
            except Exception as e:
                _eprint(f"Failed to load report: {path}: {e}")

    reports.sort(key=lambda r: (r.updated_at, r.title), reverse=True)
    return reports


def _page_template(*, site_title: str, site_subtitle: str, page_title: str, body_html: str, extra_head: str = "") -> str:
    st = html.escape(site_title)
    ss = html.escape(site_subtitle)
    t = html.escape(page_title)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{t}</title>
  <style>
    :root {{
      --bg: #070b18;
      --card: rgba(255,255,255,0.04);
      --border: rgba(148,163,184,0.18);
      --text: rgba(226,232,240,0.92);
      --muted: rgba(148,163,184,0.82);
      --accent: #60a5fa;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--text);
      background: radial-gradient(1200px 800px at 10% -10%, rgba(96,165,250,0.25), transparent 55%),
                  radial-gradient(1200px 800px at 110% 20%, rgba(167,139,250,0.22), transparent 55%),
                  var(--bg);
      font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
      line-height: 1.5;
    }}
    a {{ color: var(--accent); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .wrap {{ max-width: 1100px; margin: 0 auto; padding: 26px 18px 42px; }}
    .topbar {{ display:flex; align-items:center; justify-content:space-between; gap: 10px; margin-bottom: 18px; }}
    .brand {{ display:flex; align-items:center; gap: 10px; }}
    .logo {{
      width: 36px; height: 36px; border-radius: 12px;
      background: linear-gradient(135deg, rgba(96,165,250,0.95), rgba(167,139,250,0.95));
      box-shadow: 0 18px 50px rgba(0,0,0,0.55);
    }}
    .brand h1 {{ margin: 0; font-size: 16px; }}
    .muted {{ color: var(--muted); }}
    .grid {{ display:grid; grid-template-columns: 1fr; gap: 14px; }}
    @media (min-width: 980px) {{ .grid {{ grid-template-columns: 1fr 1fr; }} }}
    .card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 16px;
      box-shadow: 0 18px 50px rgba(0,0,0,0.42);
      backdrop-filter: blur(10px);
    }}
    .card h2 {{ margin: 0 0 6px 0; font-size: 16px; }}
    .card p {{ margin: 8px 0; }}
    .meta {{ font-size: 12px; color: rgba(148,163,184,0.85); display:flex; gap:10px; flex-wrap:wrap; }}
    .tag {{
      display:inline-flex; align-items:center; gap:6px;
      padding: 2px 10px; border-radius: 999px;
      border: 1px solid rgba(148,163,184,0.22);
      background: rgba(255,255,255,0.03);
      font-size: 12px; color: rgba(148,163,184,0.92);
    }}
    .content h1, .content h2, .content h3, .content h4 {{ margin: 14px 0 8px; }}
    .content pre {{
      overflow: auto;
      background: rgba(2,6,23,0.6);
      border: 1px solid rgba(148,163,184,0.18);
      padding: 12px;
      border-radius: 14px;
    }}
    .content code {{
      background: rgba(2,6,23,0.6);
      border: 1px solid rgba(148,163,184,0.12);
      padding: 1px 6px;
      border-radius: 8px;
      color: rgba(226,232,240,0.92);
    }}
    .content ul {{ margin: 6px 0 10px 18px; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      overflow: hidden;
      border-radius: 14px;
      border: 1px solid rgba(148,163,184,0.16);
    }}
    th, td {{ padding: 10px 10px; font-size: 13px; border-bottom: 1px solid rgba(148,163,184,0.12); text-align: left; vertical-align: top; }}
    th {{ color: rgba(226,232,240,0.95); background: rgba(255,255,255,0.03); }}
    .figure {{ margin: 10px 0; }}
    .figure img {{ width: 100%; height: auto; border-radius: 14px; border: 1px solid rgba(148,163,184,0.16); }}
    .figure .cap {{ margin-top: 6px; font-size: 12px; color: rgba(148,163,184,0.85); }}
    .svg-label {{ font: 11px sans-serif; fill: rgba(226,232,240,0.88); }}
    .svg-value {{ font: 11px sans-serif; fill: rgba(148,163,184,0.92); }}
    .svg-tick {{ font: 11px sans-serif; fill: rgba(148,163,184,0.92); }}
    .legend {{ display:flex; gap: 12px; flex-wrap:wrap; margin-top: 10px; font-size: 12px; color: rgba(148,163,184,0.9); }}
    .key {{ display:inline-flex; align-items:center; gap: 6px; }}
    .dot {{ width: 10px; height: 10px; border-radius: 999px; display:inline-block; }}
    .foot {{ margin-top: 18px; font-size: 12px; color: rgba(148,163,184,0.75); }}
  </style>
  {extra_head}
</head>
<body>
  <div class="wrap">
    <div class="topbar">
      <div class="brand">
        <div class="logo" aria-hidden="true"></div>
        <div>
          <h1>{st}</h1>
          <div class="muted" style="font-size:12px;">{ss}</div>
        </div>
      </div>
      <div class="muted" style="font-size:12px;">Generated at {_now_iso()}</div>
    </div>
    {body_html}
  </div>
</body>
</html>
"""


def _render_index(*, site_title: str, site_subtitle: str, reports: list[Report]) -> str:
    if not reports:
        body = """
<div class="card">
  <h2>No reports yet</h2>
  <p class="muted">把 <code>reports/*.json</code> 或 <code>reports/*.csv</code> 放进来（CSV 自动报告需开启 <code>AUTO_REPORT_FROM_CSV=1</code>）。</p>
  <p class="muted">最小命令：<code>python main.py build --use-examples</code></p>
</div>
"""
        return _page_template(site_title=site_title, site_subtitle=site_subtitle, page_title=site_title, body_html=body)

    cards: list[str] = ['<div class="grid">']
    for r in reports:
        tags_html = "".join([f"<span class='tag'>{html.escape(t)}</span>" for t in r.tags])
        subtitle_html = f"<p class='muted'>{html.escape(r.subtitle)}</p>" if r.subtitle else ""
        cards.append(
            f"""
<a class="card" href="r/{html.escape(r.slug)}/" style="display:block;">
  <h2>{html.escape(r.title)}</h2>
  {subtitle_html}
  <div class="meta">
    <span>Updated: {html.escape(r.updated_at)}</span>
    {tags_html}
  </div>
</a>
""".strip()
        )
    cards.append("</div>")
    return _page_template(site_title=site_title, site_subtitle=site_subtitle, page_title=site_title, body_html="".join(cards))


def _render_block(block: dict[str, Any], *, report: Report, tool_dir: Path, max_table_rows: int, max_chart_points: int) -> str:
    btype = str(block.get("type") or "").strip().lower()
    title = str(block.get("title") or "").strip()
    title_html = f"<h3>{html.escape(title)}</h3>" if title else ""

    if btype == "markdown":
        content = str(block.get("content") or "")
        return f"<section class='card content'>{title_html}{_md_to_html(content)}</section>"

    if btype == "html":
        content2 = str(block.get("content") or "")
        return f"<section class='card content'>{title_html}{content2}</section>"

    if btype == "image":
        src = str(block.get("src") or "").strip()
        if not src:
            return f"<section class='card'><h3>Image</h3><div class='muted'>Missing src</div></section>"
        caption = str(block.get("caption") or "").strip()
        cap_html = f"<div class='cap'>{html.escape(caption)}</div>" if caption else ""
        safe_src = html.escape(src)
        return (
            f"<section class='card'>{title_html}<div class='figure'>"
            f"<img src='../assets/{safe_src}' alt='{safe_src}'/>"
            f"{cap_html}</div></section>"
        )

    if btype == "table":
        columns: list[str] = []
        rows: list[list[str]] = []

        path_raw = str(block.get("path") or "").strip()
        if path_raw:
            base = report.src_path.parent
            path = (base / path_raw).resolve()
            try:
                columns, rows = _read_table_from_path(path, max_rows=max_table_rows)
            except Exception as e:
                return (
                    f"<section class='card'>{title_html}<div class='muted'>Failed to load table: "
                    f"{html.escape(str(e))}</div></section>"
                )
        else:
            columns_raw = block.get("columns") or []
            rows_raw = block.get("rows") or []
            if isinstance(columns_raw, list):
                columns = [str(c) for c in columns_raw]
            if isinstance(rows_raw, list):
                for r in rows_raw[:max_table_rows]:
                    if isinstance(r, list):
                        rows.append([str(c) for c in r])
                    elif isinstance(r, dict):
                        rows.append([str(r.get(c, "")) for c in columns])

        if not columns:
            return f"<section class='card'>{title_html}<div class='muted'>Empty table.</div></section>"

        thead = "<tr>" + "".join([f"<th>{html.escape(c)}</th>" for c in columns]) + "</tr>"
        tbody_rows: list[str] = []
        for r in rows:
            padded = list(r) + [""] * max(0, len(columns) - len(r))
            tbody_rows.append("<tr>" + "".join([f"<td>{html.escape(c)}</td>" for c in padded[: len(columns)]]) + "</tr>")
        tbody = "".join(tbody_rows) if tbody_rows else "<tr><td class='muted' colspan='999'>No rows</td></tr>"
        return f"<section class='card'>{title_html}<table><thead>{thead}</thead><tbody>{tbody}</tbody></table></section>"

    if btype == "chart":
        kind = str(block.get("kind") or "").strip().lower()
        if kind == "bar":
            data = block.get("data") or []
            items: list[tuple[str, float]] = []
            if isinstance(data, list):
                for it in data:
                    if isinstance(it, dict) and "label" in it and "value" in it:
                        try:
                            items.append((str(it["label"]), float(it["value"])))
                        except Exception:
                            continue
            svg = _svg_bar_chart(items)
            return f"<section class='card'>{title_html}{svg}</section>"

        if kind == "line":
            raw_series = block.get("series") or []
            series: list[tuple[str, list[tuple[str, float]]]] = []
            if isinstance(raw_series, list):
                for s in raw_series:
                    if not isinstance(s, dict):
                        continue
                    name = str(s.get("name") or "series")
                    pts = s.get("points") or []
                    out_pts: list[tuple[str, float]] = []
                    if isinstance(pts, list):
                        for p in pts:
                            if isinstance(p, dict) and "x" in p and "y" in p:
                                try:
                                    out_pts.append((str(p["x"]), float(p["y"])))
                                except Exception:
                                    continue
                    series.append((name, out_pts))
            svg2 = _svg_line_chart(series, max_points=max_chart_points)
            return f"<section class='card'>{title_html}{svg2}</section>"

        return f"<section class='card'>{title_html}<div class='muted'>Unknown chart kind: {html.escape(kind)}</div></section>"

    return f"<section class='card'>{title_html}<div class='muted'>Unknown block type: {html.escape(btype)}</div></section>"


def _render_report(
    report: Report,
    *,
    site_title: str,
    site_subtitle: str,
    tool_dir: Path,
    max_table_rows: int,
    max_chart_points: int,
) -> str:
    tags_html = "".join([f"<span class='tag'>{html.escape(t)}</span>" for t in report.tags])
    subtitle_html = f"<p class='muted'>{html.escape(report.subtitle)}</p>" if report.subtitle else ""
    header = f"""
<div class="card">
  <div class="meta"><a href="../index.html">← Back</a></div>
  <h2 style="margin:8px 0 6px;">{html.escape(report.title)}</h2>
  {subtitle_html}
  <div class="meta"><span>Updated: {html.escape(report.updated_at)}</span>{tags_html}</div>
</div>
""".strip()

    blocks_html = []
    for b in report.blocks:
        if not isinstance(b, dict):
            continue
        blocks_html.append(
            _render_block(b, report=report, tool_dir=tool_dir, max_table_rows=max_table_rows, max_chart_points=max_chart_points)
        )

    body = header + "".join(blocks_html) + "<div class='foot muted'>Tip: 在本工具里改 JSON / assets 后重新 build。</div>"
    return _page_template(site_title=site_title, site_subtitle=site_subtitle, page_title=report.title, body_html=body)


def _copy_tree(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    for path in src.rglob("*"):
        if path.is_dir():
            continue
        rel = path.relative_to(src)
        out = dst / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, out)


def build_site(
    *,
    tool_dir: Path,
    reports_dir: Path,
    assets_dir: Path,
    out_dir: Path,
    max_table_rows: int,
    max_chart_points: int,
    site_title: str,
    site_subtitle: str,
    auto_from_csv: bool,
    auto_profile_rows: int,
    auto_max_unique_categories: int,
    dry_run: bool,
) -> int:
    reports = _load_reports(
        reports_dir,
        auto_from_csv=auto_from_csv,
        max_table_rows=max_table_rows,
        profile_rows=auto_profile_rows,
        max_unique_categories=auto_max_unique_categories,
        max_chart_points=max_chart_points,
    )

    out_root = out_dir
    out_assets = out_root / "assets"
    out_reports = out_root / "r"

    if dry_run:
        print(f"[dry-run] would write: {out_root}")
        print(f"[dry-run] reports: {len(reports)} from {reports_dir}")
        print(f"[dry-run] assets: {assets_dir if assets_dir.exists() else '(missing)'}")
        return 0

    out_assets.mkdir(parents=True, exist_ok=True)
    out_reports.mkdir(parents=True, exist_ok=True)

    # fresh assets
    if out_assets.exists():
        for p in out_assets.iterdir():
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink()
    # fresh report pages (avoid stale slugs)
    if out_reports.exists():
        for p in out_reports.iterdir():
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink()
    _copy_tree(assets_dir, out_assets)

    index_html = _render_index(site_title=site_title, site_subtitle=site_subtitle, reports=reports)
    (out_root / "index.html").write_text(index_html, encoding="utf-8")

    for r in reports:
        page_dir = out_reports / r.slug
        page_dir.mkdir(parents=True, exist_ok=True)
        page_html = _render_report(
            r,
            site_title=site_title,
            site_subtitle=site_subtitle,
            tool_dir=tool_dir,
            max_table_rows=max_table_rows,
            max_chart_points=max_chart_points,
        )
        (page_dir / "index.html").write_text(page_html, encoding="utf-8")

    return 0


def _find_repo_root(start: Path) -> Path | None:
    cur = start.resolve()
    for _ in range(25):
        if (cur / ".git").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return None


def _run_git(args: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _ensure_worktree(*, repo_root: Path, worktree_dir: Path, branch: str) -> tuple[bool, str]:
    if (worktree_dir / ".git").exists():
        return True, "worktree exists"

    worktree_dir.parent.mkdir(parents=True, exist_ok=True)

    has_branch = _run_git(["show-ref", "--verify", f"refs/heads/{branch}"], cwd=repo_root).returncode == 0
    if has_branch:
        r = _run_git(["worktree", "add", str(worktree_dir), branch], cwd=repo_root)
    else:
        r = _run_git(["worktree", "add", "-b", branch, str(worktree_dir)], cwd=repo_root)
    if r.returncode != 0:
        return False, (r.stderr.strip() or r.stdout.strip() or "git worktree add failed")
    return True, "worktree created"


def _sync_dir(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for child in dst.iterdir():
        if child.name == ".git":
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()
    _copy_tree(src, dst)


def _ensure_repo_checkout(*, repo_dir: Path, repo_url: str, branch: str) -> tuple[bool, str]:
    if repo_dir.exists() and not (repo_dir / ".git").exists():
        return False, f"repo dir exists but is not a git repo: {repo_dir}"

    if not repo_dir.exists():
        repo_dir.parent.mkdir(parents=True, exist_ok=True)
        r = _run_git(["clone", repo_url, str(repo_dir)], cwd=repo_dir.parent)
        if r.returncode != 0:
            return False, (r.stderr.strip() or r.stdout.strip() or "git clone failed")

    # ensure origin URL (best-effort)
    _run_git(["remote", "set-url", "origin", repo_url], cwd=repo_dir)

    co = _run_git(["checkout", branch], cwd=repo_dir)
    if co.returncode != 0:
        co2 = _run_git(["checkout", "-b", branch], cwd=repo_dir)
        if co2.returncode != 0:
            return False, (co2.stderr.strip() or co2.stdout.strip() or "git checkout failed")
    return True, "repo ready"


@dataclass(frozen=True)
class PublishConfig:
    mode: str  # "branch" | "repo"

    # branch mode
    remote: str
    branch: str
    worktree_dir: Path

    # repo mode
    repo_url: str
    repo_branch: str
    repo_dir: Path


def publish_site_branch(
    *,
    tool_dir: Path,
    out_dir: Path,
    remote: str,
    branch: str,
    worktree_dir: Path,
    message: str,
    push: bool,
    dry_run: bool,
) -> int:
    repo_root = _find_repo_root(tool_dir)
    if not repo_root:
        _eprint("Failed to find repo root (missing .git).")
        return 2

    out_root = out_dir
    if not out_root.exists():
        _eprint(f"Missing build output: {out_root} (run: python main.py build)")
        return 2

    ok, info = _ensure_worktree(repo_root=repo_root, worktree_dir=worktree_dir, branch=branch)
    if not ok:
        _eprint(f"Failed to prepare worktree: {info}")
        return 2

    if dry_run:
        print(f"[dry-run] repo_root: {repo_root}")
        print(f"[dry-run] sync {out_root} -> {worktree_dir} ({info})")
        print(f"[dry-run] git commit/push: {remote} {branch}")
        return 0

    _sync_dir(out_root, worktree_dir)

    status = _run_git(["status", "--porcelain"], cwd=worktree_dir)
    if status.returncode != 0:
        _eprint(status.stderr.strip() or "git status failed")
        return 2

    if not status.stdout.strip():
        print("No changes to publish.")
        return 0

    add = _run_git(["add", "-A"], cwd=worktree_dir)
    if add.returncode != 0:
        _eprint(add.stderr.strip() or "git add failed")
        return 2

    commit = _run_git(["commit", "-m", message], cwd=worktree_dir)
    if commit.returncode != 0:
        # allow "nothing to commit" edge cases
        msg = (commit.stderr + commit.stdout).strip()
        if "nothing to commit" not in msg.lower():
            _eprint(msg or "git commit failed")
            return 2

    if push:
        p = _run_git(["push", remote, f"HEAD:{branch}"], cwd=worktree_dir)
        if p.returncode != 0:
            _eprint(p.stderr.strip() or p.stdout.strip() or "git push failed")
            return 2
        print(f"Pushed to {remote}/{branch}")
    else:
        print("Committed (no-push).")

    return 0


def publish_site_repo(
    *,
    out_dir: Path,
    repo_url: str,
    repo_branch: str,
    repo_dir: Path,
    message: str,
    push: bool,
    dry_run: bool,
) -> int:
    out_root = out_dir
    if not out_root.exists():
        _eprint(f"Missing build output: {out_root} (run: python main.py build)")
        return 2

    if not repo_url.strip():
        _eprint("Missing config: PUBLISH_REPO_URL (see .env.example)")
        return 2

    if dry_run:
        print(f"[dry-run] sync {out_root} -> {repo_dir} (repo={repo_url} branch={repo_branch})")
        return 0

    ok, info = _ensure_repo_checkout(repo_dir=repo_dir, repo_url=repo_url, branch=repo_branch)
    if not ok:
        _eprint(f"Failed to prepare publish repo: {info}")
        return 2

    _sync_dir(out_root, repo_dir)

    status = _run_git(["status", "--porcelain"], cwd=repo_dir)
    if status.returncode != 0:
        _eprint(status.stderr.strip() or "git status failed")
        return 2

    if not status.stdout.strip():
        print("No changes to publish.")
        return 0

    add = _run_git(["add", "-A"], cwd=repo_dir)
    if add.returncode != 0:
        _eprint(add.stderr.strip() or "git add failed")
        return 2

    commit = _run_git(["commit", "-m", message], cwd=repo_dir)
    if commit.returncode != 0:
        msg = (commit.stderr + commit.stdout).strip()
        if "nothing to commit" not in msg.lower():
            _eprint(msg or "git commit failed")
            return 2

    if push:
        p = _run_git(["push", "origin", repo_branch], cwd=repo_dir)
        if p.returncode != 0:
            _eprint(p.stderr.strip() or p.stdout.strip() or "git push failed")
            return 2
        print(f"Pushed to origin/{repo_branch}")
    else:
        print("Committed (no-push).")

    return 0


def publish_site_any(
    *,
    tool_dir: Path,
    out_dir: Path,
    publish: PublishConfig,
    message: str,
    push: bool,
    dry_run: bool,
) -> int:
    mode = (publish.mode or "branch").strip().lower()
    if mode == "repo":
        return publish_site_repo(
            out_dir=out_dir,
            repo_url=publish.repo_url,
            repo_branch=publish.repo_branch,
            repo_dir=publish.repo_dir,
            message=message,
            push=push,
            dry_run=dry_run,
        )
    return publish_site_branch(
        tool_dir=tool_dir,
        out_dir=out_dir,
        remote=publish.remote,
        branch=publish.branch,
        worktree_dir=publish.worktree_dir,
        message=message,
        push=push,
        dry_run=dry_run,
    )


def _fingerprint(paths: list[Path]) -> tuple[tuple[str, int, int], ...]:
    files: list[tuple[str, int, int]] = []
    for p in paths:
        if not p.exists():
            continue
        if p.is_file():
            st = p.stat()
            files.append((_safe_relpath(p), int(st.st_mtime), int(st.st_size)))
            continue
        for f in p.rglob("*"):
            if not f.is_file():
                continue
            st = f.stat()
            files.append((_safe_relpath(f), int(st.st_mtime), int(st.st_size)))
    files.sort()
    return tuple(files)


def watch_loop(
    *,
    tool_dir: Path,
    reports_dir: Path,
    assets_dir: Path,
    out_dir: Path,
    max_table_rows: int,
    max_chart_points: int,
    site_title: str,
    site_subtitle: str,
    auto_from_csv: bool,
    auto_profile_rows: int,
    auto_max_unique_categories: int,
    interval_s: float,
    publish: bool,
    publish_cfg: PublishConfig,
    dry_run: bool,
) -> int:
    targets = [reports_dir, assets_dir, tool_dir / ".env"]
    last = None
    print(f"Watching: {reports_dir} {assets_dir} (interval={interval_s}s)")
    while True:
        fp = _fingerprint(targets)
        if fp != last:
            last = fp
            print(f"[{dt.datetime.now().strftime('%H:%M:%S')}] change detected -> build")
            code = build_site(
                tool_dir=tool_dir,
                reports_dir=reports_dir,
                assets_dir=assets_dir,
                out_dir=out_dir,
                max_table_rows=max_table_rows,
                max_chart_points=max_chart_points,
                site_title=site_title,
                site_subtitle=site_subtitle,
                auto_from_csv=auto_from_csv,
                auto_profile_rows=auto_profile_rows,
                auto_max_unique_categories=auto_max_unique_categories,
                dry_run=dry_run,
            )
            if code != 0:
                _eprint(f"build failed (code={code})")
            elif publish:
                msg = f"Publish: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                publish_site_any(tool_dir=tool_dir, out_dir=out_dir, publish=publish_cfg, message=msg, push=True, dry_run=dry_run)
        time.sleep(max(0.2, interval_s))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a static HTML site from report JSON/CSV files.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    def add_common_build_flags(p: argparse.ArgumentParser) -> None:
        p.add_argument("--reports", type=str, default=None, help="reports directory (default from REPORTS_DIR)")
        p.add_argument("--assets", type=str, default=None, help="assets directory (default from ASSETS_DIR)")
        p.add_argument("--out", type=str, default=None, help="output directory (default from OUT_DIR)")
        p.add_argument("--max-table-rows", type=int, default=None, help="limit rows per table")
        p.add_argument("--max-chart-points", type=int, default=None, help="limit points per line series")
        p.add_argument("--auto-csv", action="store_true", help="auto-generate a report page for each CSV/TSV")
        p.add_argument("--no-auto-csv", action="store_true", help="disable CSV/TSV auto reports (override env)")
        p.add_argument("--dry-run", action="store_true", help="do not write files / do not run git")
        p.add_argument("--use-examples", action="store_true", help="build using examples/ instead of reports/assets")

    p_build = sub.add_parser("build", help="build the static site")
    add_common_build_flags(p_build)

    p_pub = sub.add_parser("publish", help="publish built site (branch mode or separate repo mode)")
    p_pub.add_argument("--out", type=str, default=None, help="output directory (default from OUT_DIR)")
    p_pub.add_argument("--mode", type=str, choices=["branch", "repo"], default=None, help="publish mode")
    p_pub.add_argument("--repo-url", type=str, default=None, help="publish repo URL (mode=repo)")
    p_pub.add_argument("--repo-branch", type=str, default=None, help="publish repo branch (mode=repo)")
    p_pub.add_argument("--repo-dir", type=str, default=None, help="local publish repo dir (mode=repo)")
    p_pub.add_argument("--remote", type=str, default=None, help="git remote (default from PUBLISH_REMOTE)")
    p_pub.add_argument("--branch", type=str, default=None, help="git branch (default from PUBLISH_BRANCH)")
    p_pub.add_argument("--worktree", type=str, default=None, help="worktree dir (default from PUBLISH_WORKTREE_DIR)")
    p_pub.add_argument("--message", type=str, default=None, help="commit message")
    p_pub.add_argument("--no-push", action="store_true", help="commit but do not push")
    p_pub.add_argument("--dry-run", action="store_true", help="do not write files / do not run git")

    p_watch = sub.add_parser("watch", help="watch reports/assets and rebuild (optionally publish)")
    add_common_build_flags(p_watch)
    p_watch.add_argument("--interval", type=float, default=2.0, help="poll interval seconds")
    p_watch.add_argument("--publish", action="store_true", help="after build, publish to branch")
    p_watch.add_argument("--publish-mode", type=str, choices=["branch", "repo"], default=None, help="publish mode")
    p_watch.add_argument("--repo-url", type=str, default=None, help="publish repo URL (mode=repo)")
    p_watch.add_argument("--repo-branch", type=str, default=None, help="publish repo branch (mode=repo)")
    p_watch.add_argument("--repo-dir", type=str, default=None, help="local publish repo dir (mode=repo)")
    p_watch.add_argument("--remote", type=str, default=None, help="git remote (default from PUBLISH_REMOTE)")
    p_watch.add_argument("--branch", type=str, default=None, help="git branch (default from PUBLISH_BRANCH)")
    p_watch.add_argument("--worktree", type=str, default=None, help="worktree dir (default from PUBLISH_WORKTREE_DIR)")

    return parser.parse_args()


def main() -> int:
    tool_dir = Path(__file__).resolve().parent
    _load_dotenv_if_present(tool_dir / ".env")

    args = _parse_args()

    reports_dir_default = tool_dir / (os.getenv("REPORTS_DIR") or "reports")
    assets_dir_default = tool_dir / (os.getenv("ASSETS_DIR") or "assets")
    out_dir_default = tool_dir / (os.getenv("OUT_DIR") or "out/site")

    site_title_default = os.getenv("SITE_TITLE") or "Data Showcase"
    site_subtitle_default = os.getenv("SITE_SUBTITLE") or "Static reports for humans"

    max_table_rows_default = _parse_int(os.getenv("MAX_TABLE_ROWS"), default=200)
    max_chart_points_default = _parse_int(os.getenv("MAX_CHART_POINTS"), default=500)

    auto_from_csv_default = _parse_bool(os.getenv("AUTO_REPORT_FROM_CSV"), default=False)
    auto_profile_rows_default = _parse_int(os.getenv("AUTO_REPORT_PROFILE_ROWS"), default=5000)
    auto_max_unique_categories_default = _parse_int(os.getenv("AUTO_REPORT_MAX_UNIQUE_CATEGORIES"), default=20)

    publish_mode_default = (os.getenv("PUBLISH_MODE") or "branch").strip().lower()
    publish_remote_default = os.getenv("PUBLISH_REMOTE") or "origin"
    publish_branch_default = os.getenv("PUBLISH_BRANCH") or "site"
    publish_worktree_default = tool_dir / (os.getenv("PUBLISH_WORKTREE_DIR") or ".publish-worktree")
    publish_repo_url_default = os.getenv("PUBLISH_REPO_URL") or ""
    publish_repo_branch_default = os.getenv("PUBLISH_REPO_BRANCH") or "main"
    publish_repo_dir_default = tool_dir / (os.getenv("PUBLISH_REPO_DIR") or ".publish-repo")

    use_examples = bool(getattr(args, "use_examples", False))
    reports_dir = Path(args.reports) if getattr(args, "reports", None) else reports_dir_default
    assets_dir = Path(args.assets) if getattr(args, "assets", None) else assets_dir_default
    out_dir = Path(args.out) if getattr(args, "out", None) else out_dir_default
    max_table_rows = int(args.max_table_rows) if getattr(args, "max_table_rows", None) else max_table_rows_default
    max_chart_points = (
        int(args.max_chart_points) if getattr(args, "max_chart_points", None) else max_chart_points_default
    )

    auto_from_csv = auto_from_csv_default
    if bool(getattr(args, "auto_csv", False)):
        auto_from_csv = True
    if bool(getattr(args, "no_auto_csv", False)):
        auto_from_csv = False

    if use_examples:
        reports_dir = tool_dir / "examples/reports"
        assets_dir = tool_dir / "examples/assets"
        auto_from_csv = False

    if args.cmd == "build":
        return build_site(
            tool_dir=tool_dir,
            reports_dir=reports_dir,
            assets_dir=assets_dir,
            out_dir=out_dir,
            max_table_rows=max_table_rows,
            max_chart_points=max_chart_points,
            site_title=site_title_default,
            site_subtitle=site_subtitle_default,
            auto_from_csv=auto_from_csv,
            auto_profile_rows=auto_profile_rows_default,
            auto_max_unique_categories=auto_max_unique_categories_default,
            dry_run=bool(args.dry_run),
        )

    if args.cmd == "publish":
        mode = str(args.mode or publish_mode_default)
        remote = str(args.remote or publish_remote_default)
        branch = str(args.branch or publish_branch_default)
        worktree = Path(args.worktree) if args.worktree else publish_worktree_default
        repo_url = str(getattr(args, "repo_url", None) or publish_repo_url_default)
        repo_branch = str(getattr(args, "repo_branch", None) or publish_repo_branch_default)
        repo_dir = Path(getattr(args, "repo_dir", None)) if getattr(args, "repo_dir", None) else publish_repo_dir_default
        message = str(args.message or f"Publish: {_now_iso()}")
        publish_cfg = PublishConfig(
            mode=mode,
            remote=remote,
            branch=branch,
            worktree_dir=worktree,
            repo_url=repo_url,
            repo_branch=repo_branch,
            repo_dir=repo_dir,
        )
        return publish_site_any(
            tool_dir=tool_dir,
            out_dir=out_dir,
            publish=publish_cfg,
            message=message,
            push=not bool(args.no_push),
            dry_run=bool(args.dry_run),
        )

    if args.cmd == "watch":
        mode = str(getattr(args, "publish_mode", None) or publish_mode_default)
        remote = str(getattr(args, "remote", None) or publish_remote_default)
        branch = str(getattr(args, "branch", None) or publish_branch_default)
        worktree = Path(getattr(args, "worktree", None)) if getattr(args, "worktree", None) else publish_worktree_default
        repo_url = str(getattr(args, "repo_url", None) or publish_repo_url_default)
        repo_branch = str(getattr(args, "repo_branch", None) or publish_repo_branch_default)
        repo_dir = Path(getattr(args, "repo_dir", None)) if getattr(args, "repo_dir", None) else publish_repo_dir_default
        publish_cfg = PublishConfig(
            mode=mode,
            remote=remote,
            branch=branch,
            worktree_dir=worktree,
            repo_url=repo_url,
            repo_branch=repo_branch,
            repo_dir=repo_dir,
        )
        return watch_loop(
            tool_dir=tool_dir,
            reports_dir=reports_dir,
            assets_dir=assets_dir,
            out_dir=out_dir,
            max_table_rows=max_table_rows,
            max_chart_points=max_chart_points,
            site_title=site_title_default,
            site_subtitle=site_subtitle_default,
            auto_from_csv=auto_from_csv,
            auto_profile_rows=auto_profile_rows_default,
            auto_max_unique_categories=auto_max_unique_categories_default,
            interval_s=float(getattr(args, "interval", 2.0)),
            publish=bool(getattr(args, "publish", False)),
            publish_cfg=publish_cfg,
            dry_run=bool(getattr(args, "dry_run", False)),
        )

    _eprint(f"Unknown cmd: {args.cmd}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
