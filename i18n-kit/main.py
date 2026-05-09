from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tokenize
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, NamedTuple


TOKEN_PREFIX_DEFAULT = "__I18N__"
TOKEN_SUFFIX_DEFAULT = "__"

DEFAULT_EXTS = [".html", ".htm", ".jsx", ".tsx", ".js", ".ts", ".py"]
DEFAULT_EXCLUDE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".idea",
    ".vscode",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "out",
    ".next",
    ".turbo",
    "__pycache__",
}


class ReplaceEdit(NamedTuple):
    start: int
    end: int
    replacement: str


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


def _looks_binary(data: bytes) -> bool:
    return b"\x00" in data


def _read_text_file(path: Path) -> str | None:
    try:
        data = path.read_bytes()
    except Exception as e:
        _eprint(f"[skip] cannot read: {path} ({e})")
        return None
    if _looks_binary(data):
        return None
    for encoding in ("utf-8", "utf-8-sig", "gb18030", "latin-1"):
        try:
            return data.decode(encoding)
        except Exception:
            continue
    _eprint(f"[skip] cannot decode: {path}")
    return None


def _write_text_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _load_json(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        raise RuntimeError(f"Failed to read json: {path} ({e})") from e
    if not isinstance(data, dict):
        raise RuntimeError(f"Invalid json format (expected object): {path}")
    out: dict[str, str] = {}
    for k, v in data.items():
        if isinstance(k, str) and isinstance(v, str):
            out[k] = v
    return out


def _save_json(path: Path, obj: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_ASCII_LETTER_RE = re.compile(r"[A-Za-z]")


def _is_candidate_text(text: str, *, include_ascii: bool, token_prefix: str) -> bool:
    t = text.strip()
    if len(t) < 2:
        return False
    if token_prefix and token_prefix in t:
        return False
    if "http://" in t or "https://" in t:
        return False
    if _CJK_RE.search(t):
        return True
    if include_ascii and _ASCII_LETTER_RE.search(t) and any(ch.isspace() for ch in t):
        return True
    return False


def _token_for_key(prefix: str, key: str, suffix: str) -> str:
    return f"{prefix}{key}{suffix}"


def _key_for_text(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]


def _key_for_path_and_text(rel_path: str, text: str) -> str:
    h = hashlib.sha1()
    h.update(rel_path.encode("utf-8"))
    h.update(b"\n")
    h.update(text.encode("utf-8"))
    return h.hexdigest()[:10]

_NON_KEY_CHARS_RE = re.compile(r"[^a-z0-9]+")


def _try_pinyin_slug(text: str) -> str | None:
    if not _CJK_RE.search(text):
        return None
    try:
        from pypinyin import Style, pinyin  # type: ignore
    except Exception:
        return None

    parts: list[str] = []
    for item in pinyin(text, style=Style.NORMAL, strict=False):
        if not item:
            continue
        syllable = (item[0] or "").strip().lower()
        if not syllable:
            continue
        if _NON_KEY_CHARS_RE.fullmatch(syllable):
            continue
        parts.append(_NON_KEY_CHARS_RE.sub("_", syllable).strip("_"))
    slug = "_".join([p for p in parts if p])
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug or None


def _ascii_slug(text: str) -> str:
    t = text.strip().lower()
    t = _NON_KEY_CHARS_RE.sub("_", t)
    t = re.sub(r"_+", "_", t).strip("_")
    return t


def _key_for_slug_hash(text: str) -> str:
    # Readable key: prefer ASCII words; for Chinese, prefer pinyin if available.
    slug = _ascii_slug(text)
    if not slug or (slug.isdigit() and _CJK_RE.search(text)):
        slug = _try_pinyin_slug(text) or slug

    if not slug:
        slug = "k"
    if not slug[0].isalpha():
        slug = f"k_{slug}"

    slug = slug[:32].rstrip("_")
    return f"{slug}_{_key_for_text(text)}"


def _apply_edits(content: str, edits: list[ReplaceEdit]) -> str:
    if not edits:
        return content
    edits_sorted = sorted(edits, key=lambda e: e.start, reverse=True)
    out = content
    for e in edits_sorted:
        out = out[: e.start] + e.replacement + out[e.end :]
    return out


def _iter_files(root: Path, exts: set[str], exclude_dirs: set[str]) -> Iterator[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        base = Path(dirpath)
        for name in filenames:
            p = base / name
            if p.suffix.lower() in exts:
                yield p


HTML_TEXT_NODE_RE = re.compile(r">(?P<text>[^<]+)<")
HTML_ATTR_RE = re.compile(
    r"""\b(?P<attr>title|placeholder|alt|aria-label)\s*=\s*(?P<q>["'])(?P<val>.*?)(?P=q)""",
    re.IGNORECASE | re.DOTALL,
)
HTML_SCRIPT_STYLE_RE = re.compile(
    r"(?is)<(script|style)\b[^>]*>.*?</\1>"
)


def _spans_to_ignore_in_html(content: str) -> list[tuple[int, int]]:
    return [(m.start(), m.end()) for m in HTML_SCRIPT_STYLE_RE.finditer(content)]


def _is_in_spans(pos: int, spans: list[tuple[int, int]]) -> bool:
    # spans are expected to be few for typical reports.
    for s, e in spans:
        if s <= pos < e:
            return True
    return False


def _extract_from_html_like(
    content: str,
    *,
    include_ascii: bool,
    token_prefix: str,
) -> list[tuple[str, list[ReplaceEdit]]]:
    extracted: list[tuple[str, list[ReplaceEdit]]] = []
    ignore_spans = _spans_to_ignore_in_html(content)

    for m in HTML_TEXT_NODE_RE.finditer(content):
        if _is_in_spans(m.start(), ignore_spans):
            continue
        raw = m.group("text")
        if token_prefix in raw:
            continue
        stripped = raw.strip()
        if not _is_candidate_text(
            stripped, include_ascii=include_ascii, token_prefix=token_prefix
        ):
            continue
        lead_len = len(raw) - len(raw.lstrip())
        trail_len = len(raw) - len(raw.rstrip())
        start = m.start("text") + lead_len
        end = m.end("text") - trail_len
        extracted.append((stripped, [ReplaceEdit(start, end, "")]))

    for m in HTML_ATTR_RE.finditer(content):
        if _is_in_spans(m.start(), ignore_spans):
            continue
        val = m.group("val")
        if token_prefix in val:
            continue
        if not _is_candidate_text(val, include_ascii=include_ascii, token_prefix=token_prefix):
            continue
        extracted.append((val, [ReplaceEdit(m.start("val"), m.end("val"), "")]))

    return extracted


def _line_offsets(text: str) -> list[int]:
    offsets = [0]
    for idx, ch in enumerate(text):
        if ch == "\n":
            offsets.append(idx + 1)
    return offsets


def _pos_to_index(offsets: list[int], line: int, col: int) -> int:
    if line <= 0:
        return 0
    if line - 1 >= len(offsets):
        return offsets[-1]
    return offsets[line - 1] + col


_PY_PREFIX_RE = re.compile(r"^(?P<prefix>[rRuUbBfF]*)")


def _extract_from_python(
    content: str,
    *,
    include_ascii: bool,
    token_prefix: str,
) -> list[tuple[str, list[ReplaceEdit]]]:
    offsets = _line_offsets(content)
    extracted: list[tuple[str, list[ReplaceEdit]]] = []
    reader = tokenize.generate_tokens(iter(content.splitlines(keepends=True)).__next__)
    for tok in reader:
        if tok.type != tokenize.STRING:
            continue
        s = tok.string
        prefix = _PY_PREFIX_RE.match(s).group("prefix") if _PY_PREFIX_RE.match(s) else ""
        if any(ch in prefix.lower() for ch in ("b", "f")):
            continue
        try:
            import ast

            val = ast.literal_eval(s)
        except Exception:
            continue
        if not isinstance(val, str):
            continue
        if token_prefix in val:
            continue
        if not _is_candidate_text(val, include_ascii=include_ascii, token_prefix=token_prefix):
            continue

        start_i = _pos_to_index(offsets, tok.start[0], tok.start[1])
        end_i = _pos_to_index(offsets, tok.end[0], tok.end[1])
        extracted.append((val, [ReplaceEdit(start_i, end_i, "")]))
    return extracted


@dataclass(frozen=True)
class _JsStringLiteral:
    start: int
    end: int
    quote: str
    raw_value: str


def _iter_js_string_literals(content: str) -> Iterator[_JsStringLiteral]:
    i = 0
    n = len(content)
    state = "code"
    quote = ""
    start = -1

    while i < n:
        ch = content[i]
        nxt = content[i + 1] if i + 1 < n else ""

        if state == "code":
            if ch == "/" and nxt == "/":
                state = "sl_comment"
                i += 2
                continue
            if ch == "/" and nxt == "*":
                state = "ml_comment"
                i += 2
                continue
            if ch in ("'", '"'):
                state = "string"
                quote = ch
                start = i
                i += 1
                continue
            if ch == "`":
                state = "template"
                i += 1
                continue
            i += 1
            continue

        if state == "sl_comment":
            if ch == "\n":
                state = "code"
            i += 1
            continue

        if state == "ml_comment":
            if ch == "*" and nxt == "/":
                state = "code"
                i += 2
                continue
            i += 1
            continue

        if state == "template":
            if ch == "\\":
                i += 2
                continue
            if ch == "`":
                state = "code"
                i += 1
                continue
            i += 1
            continue

        if state == "string":
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                end = i + 1
                raw_value = content[start + 1 : i]
                yield _JsStringLiteral(start=start, end=end, quote=quote, raw_value=raw_value)
                state = "code"
                quote = ""
                start = -1
                i = end
                continue
            i += 1
            continue

        i += 1


def _extract_from_js_like(
    content: str,
    *,
    include_ascii: bool,
    token_prefix: str,
) -> list[tuple[str, list[ReplaceEdit]]]:
    extracted: list[tuple[str, list[ReplaceEdit]]]=[]
    for lit in _iter_js_string_literals(content):
        if token_prefix in lit.raw_value:
            continue
        if not _is_candidate_text(
            lit.raw_value, include_ascii=include_ascii, token_prefix=token_prefix
        ):
            continue
        extracted.append((lit.raw_value, [ReplaceEdit(lit.start, lit.end, "")]))
    return extracted


def _replace_python_string_token(original_token: str, token_text: str) -> str | None:
    m = _PY_PREFIX_RE.match(original_token)
    if not m:
        return None
    prefix = m.group("prefix")
    rest = original_token[len(prefix) :]
    if rest.startswith("'''") or rest.startswith('"""'):
        quote = rest[:3]
    elif rest.startswith("'") or rest.startswith('"'):
        quote = rest[:1]
    else:
        return None
    if quote == "'":
        return f"{prefix}'{token_text}'"
    if quote == '"':
        return f'{prefix}"{token_text}"'
    if quote in ("'''", '"""'):
        return f"{prefix}{quote}{token_text}{quote}"
    return None


@dataclass
class ExtractResult:
    file_count: int = 0
    extracted_count: int = 0
    changed_files: int = 0


def extract_and_optionally_tokenize(
    *,
    root: Path,
    lang: str,
    dict_path: Path,
    exts: set[str],
    exclude_dirs: set[str],
    include_ascii: bool,
    key_mode: str,
    token_prefix: str,
    token_suffix: str,
    write: bool,
    dry_run: bool,
    max_file_bytes: int,
) -> ExtractResult:
    existing = _load_json(dict_path)
    merged = dict(existing)

    result = ExtractResult()

    for path in _iter_files(root, exts, exclude_dirs):
        try:
            if path.stat().st_size > max_file_bytes:
                continue
        except Exception:
            continue

        content = _read_text_file(path)
        if content is None:
            continue
        result.file_count += 1

        rel_path = str(path.relative_to(root))
        if path.suffix.lower() in (".html", ".htm", ".jsx", ".tsx"):
            hits = _extract_from_html_like(
                content, include_ascii=include_ascii, token_prefix=token_prefix
            )
        elif path.suffix.lower() == ".py":
            hits = _extract_from_python(
                content, include_ascii=include_ascii, token_prefix=token_prefix
            )
        elif path.suffix.lower() in (".js", ".ts"):
            hits = _extract_from_js_like(
                content, include_ascii=include_ascii, token_prefix=token_prefix
            )
        else:
            hits = []

        if not hits:
            continue

        file_edits: list[ReplaceEdit] = []

        for text, edits in hits:
            if key_mode == "path-text-hash":
                key = _key_for_path_and_text(rel_path, text)
            elif key_mode == "slug-hash":
                key = _key_for_slug_hash(text)
            else:
                key = _key_for_text(text)

            merged.setdefault(key, text)
            result.extracted_count += 1

            token_text = _token_for_key(token_prefix, key, token_suffix)
            if not write:
                continue

            for e in edits:
                if path.suffix.lower() == ".py":
                    original_token = content[e.start : e.end]
                    replaced = _replace_python_string_token(original_token, token_text)
                    if replaced is None:
                        continue
                    file_edits.append(ReplaceEdit(e.start, e.end, replaced))
                elif path.suffix.lower() in (".js", ".ts"):
                    original_literal = content[e.start : e.end]
                    if original_literal.startswith("'") and original_literal.endswith("'"):
                        file_edits.append(
                            ReplaceEdit(e.start, e.end, f"'{token_text}'")
                        )
                    elif original_literal.startswith('"') and original_literal.endswith('"'):
                        file_edits.append(
                            ReplaceEdit(e.start, e.end, f'"{token_text}"')
                        )
                else:
                    file_edits.append(ReplaceEdit(e.start, e.end, token_text))

        if write and file_edits:
            new_content = _apply_edits(content, file_edits)
            if new_content != content:
                result.changed_files += 1
                if not dry_run:
                    _write_text_file(path, new_content)

    if merged != existing and not dry_run:
        _save_json(dict_path, merged)

    return result


@dataclass
class ApplyResult:
    file_count: int = 0
    changed_files: int = 0
    replaced_tokens: int = 0
    missing_keys: int = 0


def _replace_tokens_in_content(
    content: str,
    translations: dict[str, str],
    *,
    token_prefix: str,
    token_suffix: str,
) -> tuple[str, int, int]:
    # NOTE: token_prefix/suffix are configurable, so build regex dynamically.
    token_re = re.compile(
        re.escape(token_prefix)
        + r"(?P<key>[A-Za-z0-9][A-Za-z0-9_.-]*)"
        + re.escape(token_suffix)
    )
    replaced = 0
    missing = 0

    def repl(m: re.Match[str]) -> str:
        nonlocal replaced, missing
        k = m.group("key")
        if k not in translations:
            missing += 1
            return m.group(0)
        replaced += 1
        return translations[k]

    new_content = token_re.sub(repl, content)
    return new_content, replaced, missing


def apply_translations(
    *,
    root: Path,
    lang: str,
    dict_path: Path,
    out_dir: Path | None,
    in_place: bool,
    exts: set[str],
    exclude_dirs: set[str],
    token_prefix: str,
    token_suffix: str,
    dry_run: bool,
    max_file_bytes: int,
) -> ApplyResult:
    translations = _load_json(dict_path)
    if not translations:
        raise RuntimeError(f"Missing or empty dict: {dict_path}")

    if in_place and out_dir is not None:
        raise RuntimeError("Choose one: --in-place or --out-dir")
    if not in_place and out_dir is None:
        raise RuntimeError("Missing output: use --out-dir (recommended) or --in-place")

    if out_dir is not None:
        if out_dir.exists():
            raise RuntimeError(f"Output dir already exists: {out_dir}")
        if not dry_run:
            shutil.copytree(root, out_dir)
        effective_root = out_dir if not dry_run else root
    else:
        effective_root = root

    result = ApplyResult()
    for path in _iter_files(effective_root, exts, exclude_dirs | {"i18n"}):
        try:
            if path.stat().st_size > max_file_bytes:
                continue
        except Exception:
            continue
        content = _read_text_file(path)
        if content is None:
            continue
        result.file_count += 1
        new_content, replaced, missing = _replace_tokens_in_content(
            content,
            translations,
            token_prefix=token_prefix,
            token_suffix=token_suffix,
        )
        if new_content != content:
            result.changed_files += 1
            result.replaced_tokens += replaced
            result.missing_keys += missing
            if not dry_run:
                _write_text_file(path, new_content)

    return result


def _default_dict_path(root: Path, lang: str) -> Path:
    return root / "i18n" / f"{lang}.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="i18n-kit: extract UI texts to tokens + maintain key->text dict + apply language."
    )
    parser.add_argument(
        "--dotenv",
        default=os.getenv("I18N_KIT_DOTENV", ""),
        help="Optional .env file path (default: env I18N_KIT_DOTENV)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not write files (still prints summary).",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_extract = sub.add_parser("extract", help="Extract texts into dict; optionally tokenize files.")
    p_extract.add_argument("--root", default=os.getenv("I18N_KIT_ROOT", "."), help="Project root.")
    p_extract.add_argument("--lang", default=os.getenv("I18N_KIT_LANG", "zh-CN"))
    p_extract.add_argument("--dict", dest="dict_path", default="", help="Dict json path.")
    p_extract.add_argument("--write", action="store_true", help="Rewrite files: text -> token.")
    p_extract.add_argument(
        "--key-mode",
        choices=["slug-hash", "text-hash", "path-text-hash"],
        default=os.getenv("I18N_KIT_KEY_MODE", "slug-hash"),
    )
    p_extract.add_argument("--include-ascii", action="store_true", help="Also extract ASCII texts.")
    p_extract.add_argument("--token-prefix", default=TOKEN_PREFIX_DEFAULT)
    p_extract.add_argument("--token-suffix", default=TOKEN_SUFFIX_DEFAULT)
    p_extract.add_argument(
        "--ext",
        action="append",
        default=[],
        help="File extension to scan (repeatable). Default: html/tsx/js/py.",
    )
    p_extract.add_argument(
        "--exclude-dir",
        action="append",
        default=[],
        help="Directory name to exclude (repeatable).",
    )
    p_extract.add_argument(
        "--max-file-bytes",
        type=int,
        default=int(os.getenv("I18N_KIT_MAX_FILE_BYTES", str(2 * 1024 * 1024))),
        help="Skip files larger than this.",
    )

    p_apply = sub.add_parser("apply", help="Apply a language dict: token -> text.")
    p_apply.add_argument("--root", default=os.getenv("I18N_KIT_ROOT", "."), help="Project root.")
    p_apply.add_argument("--lang", default=os.getenv("I18N_KIT_LANG", "zh-CN"))
    p_apply.add_argument("--dict", dest="dict_path", default="", help="Dict json path.")
    p_apply.add_argument("--out-dir", default="", help="Output dir (copy project and apply).")
    p_apply.add_argument(
        "--in-place",
        action="store_true",
        help="Modify files in place (danger).",
    )
    p_apply.add_argument("--token-prefix", default=TOKEN_PREFIX_DEFAULT)
    p_apply.add_argument("--token-suffix", default=TOKEN_SUFFIX_DEFAULT)
    p_apply.add_argument(
        "--ext",
        action="append",
        default=[],
        help="File extension to scan (repeatable). Default: html/tsx/js/py.",
    )
    p_apply.add_argument(
        "--exclude-dir",
        action="append",
        default=[],
        help="Directory name to exclude (repeatable).",
    )
    p_apply.add_argument(
        "--max-file-bytes",
        type=int,
        default=int(os.getenv("I18N_KIT_MAX_FILE_BYTES", str(2 * 1024 * 1024))),
        help="Skip files larger than this.",
    )

    p_embed = sub.add_parser(
        "embed-switch",
        help="Embed an offline language switcher into a tokenized HTML file (token -> text at runtime).",
    )
    p_embed.add_argument("--html", required=True, help="Path to the tokenized HTML file.")
    p_embed.add_argument("--root", default="", help="Project root (default: html file directory).")
    p_embed.add_argument(
        "--langs",
        default=os.getenv("I18N_KIT_LANGS", "zh-CN,en-US"),
        help="Comma-separated languages to embed, e.g. zh-CN,en-US.",
    )
    p_embed.add_argument(
        "--dict-dir",
        default=os.getenv("I18N_KIT_DICT_DIR", "i18n"),
        help="Directory under root that contains <lang>.json (default: i18n).",
    )
    p_embed.add_argument(
        "--default-lang",
        default=os.getenv("I18N_KIT_DEFAULT_LANG", "zh-CN"),
        help="Default language used on first open.",
    )
    p_embed.add_argument("--token-prefix", default=TOKEN_PREFIX_DEFAULT)
    p_embed.add_argument("--token-suffix", default=TOKEN_SUFFIX_DEFAULT)

    return parser


I18N_SWITCHER_START = "<!-- I18N-KIT:SWITCHER:START -->"
I18N_SWITCHER_END = "<!-- I18N-KIT:SWITCHER:END -->"


def _inject_or_replace_block(
    html: str,
    *,
    start_marker: str,
    end_marker: str,
    block: str,
) -> str:
    start_i = html.find(start_marker)
    end_i = html.find(end_marker)
    if start_i != -1 and end_i != -1 and end_i > start_i:
        end_i = end_i + len(end_marker)
        return html[:start_i] + block + html[end_i:]

    lower = html.lower()
    body_close = lower.rfind("</body>")
    if body_close != -1:
        return html[:body_close] + block + "\n" + html[body_close:]
    return html.rstrip() + "\n" + block + "\n"


def embed_html_language_switcher(
    *,
    html_path: Path,
    root: Path,
    dict_dir: str,
    langs: list[str],
    default_lang: str,
    token_prefix: str,
    token_suffix: str,
    dry_run: bool,
) -> None:
    html = _read_text_file(html_path)
    if html is None:
        raise RuntimeError(f"Cannot read html: {html_path}")

    dicts: dict[str, dict[str, str]] = {}
    for lang in langs:
        lang = lang.strip()
        if not lang:
            continue
        dict_path = root / dict_dir / f"{lang}.json"
        if not dict_path.exists():
            _eprint(f"[warn] missing dict: {dict_path}")
            dicts[lang] = {}
            continue
        dicts[lang] = _load_json(dict_path)

    # Prevent `</script>` from prematurely terminating the script tag.
    dict_json = json.dumps(dicts, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    langs_json = json.dumps(langs, ensure_ascii=False, separators=(",", ":"))

    block = "\n".join(
        [
            I18N_SWITCHER_START,
            '<div id="i18n-kit-switcher" style="position:fixed;top:12px;right:12px;z-index:99999;display:flex;gap:8px;align-items:center;padding:8px 10px;border-radius:12px;background:rgba(0,0,0,0.25);border:1px solid rgba(255,255,255,0.18);backdrop-filter: blur(8px);">',
            '  <span style="font:12px ui-sans-serif,system-ui;-apple-system,Segoe UI,Roboto,Helvetica,Arial;opacity:.85;">Lang</span>',
            '  <select id="i18n-kit-lang" style="font:12px ui-sans-serif,system-ui;-apple-system,Segoe UI,Roboto,Helvetica,Arial;color:inherit;background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.20);border-radius:10px;padding:4px 8px;">',
            "  </select>",
            "</div>",
            f'<script id="i18n-kit-dicts" type="application/json">{dict_json}</script>',
            "<script>",
            "(function(){",
            f'  const STORAGE_KEY = "i18n-kit-lang";',
            f'  const tokenPrefix = {json.dumps(token_prefix)};',
            f'  const tokenSuffix = {json.dumps(token_suffix)};',
            f'  const defaultLang = {json.dumps(default_lang)};',
            f"  const supportedLangs = {langs_json};",
            "  const dictEl = document.getElementById('i18n-kit-dicts');",
            "  const dicts = dictEl ? JSON.parse(dictEl.textContent || '{}') : {};",
            "  function getLang(){",
            "    return localStorage.getItem(STORAGE_KEY) || defaultLang;",
            "  }",
            "  function setLang(lang){",
            "    localStorage.setItem(STORAGE_KEY, lang);",
            "  }",
            "  function applyLang(lang){",
            "    const map = dicts[lang] || {};",
            "    const fallback = dicts[defaultLang] || {};",
            "    const tokenRe = new RegExp(tokenPrefix + '([A-Za-z0-9][A-Za-z0-9_.-]*)' + tokenSuffix, 'g');",
            "    document.documentElement.lang = lang;",
            "    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);",
            "    const textNodes = [];",
            "    while (walker.nextNode()) textNodes.push(walker.currentNode);",
            "    for (const node of textNodes){",
            "      const v = node.nodeValue;",
            "      if (!v || v.indexOf(tokenPrefix) < 0) continue;",
            "      node.nodeValue = v.replace(tokenRe, (m, k) => (k in map ? map[k] : (k in fallback ? fallback[k] : m)));",
            "    }",
            "    const attrs = ['title','placeholder','alt','aria-label'];",
            "    const selector = attrs.map(a => '['+a+']').join(',');",
            "    for (const el of document.querySelectorAll(selector)){",
            "      for (const a of attrs){",
            "        const v = el.getAttribute(a);",
            "        if (!v || v.indexOf(tokenPrefix) < 0) continue;",
            "        el.setAttribute(a, v.replace(tokenRe, (m, k) => (k in map ? map[k] : (k in fallback ? fallback[k] : m))));",
            "      }",
            "    }",
            "  }",
            "  const select = document.getElementById('i18n-kit-lang');",
            "  if (select){",
            "    select.innerHTML = '';",
            "    for (const lang of supportedLangs){",
            "      const opt = document.createElement('option');",
            "      opt.value = lang;",
            "      opt.textContent = lang;",
            "      select.appendChild(opt);",
            "    }",
            "    const initial = getLang();",
            "    if (supportedLangs.includes(initial)) select.value = initial;",
            "    select.addEventListener('change', () => { setLang(select.value); location.reload(); });",
            "  }",
            "  applyLang(getLang());",
            "})();",
            "</script>",
            I18N_SWITCHER_END,
            "",
        ]
    )

    new_html = _inject_or_replace_block(
        html, start_marker=I18N_SWITCHER_START, end_marker=I18N_SWITCHER_END, block=block
    )
    if new_html != html and not dry_run:
        _write_text_file(html_path, new_html)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.dotenv:
        _load_dotenv_if_present(Path(args.dotenv))

    if args.cmd == "extract":
        root = Path(args.root).expanduser().resolve()
        dict_path = Path(args.dict_path).expanduser() if args.dict_path else _default_dict_path(root, args.lang)
        exts = set((args.ext or DEFAULT_EXTS))
        exts = {e if e.startswith(".") else f".{e}" for e in exts}
        exclude_dirs = set(DEFAULT_EXCLUDE_DIRS) | set(args.exclude_dir or [])
        res = extract_and_optionally_tokenize(
            root=root,
            lang=args.lang,
            dict_path=dict_path,
            exts=exts,
            exclude_dirs=exclude_dirs,
            include_ascii=bool(args.include_ascii),
            key_mode=args.key_mode,
            token_prefix=args.token_prefix,
            token_suffix=args.token_suffix,
            write=bool(args.write),
            dry_run=bool(args.dry_run),
            max_file_bytes=int(args.max_file_bytes),
        )
        print(
            f"extract: scanned_files={res.file_count} extracted={res.extracted_count} changed_files={res.changed_files} dict={dict_path}"
        )
        if args.dry_run:
            print("(dry-run) no files written")
        return 0

    if args.cmd == "apply":
        root = Path(args.root).expanduser().resolve()
        dict_path = Path(args.dict_path).expanduser() if args.dict_path else _default_dict_path(root, args.lang)
        out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else None
        exts = set((args.ext or DEFAULT_EXTS))
        exts = {e if e.startswith(".") else f".{e}" for e in exts}
        exclude_dirs = set(DEFAULT_EXCLUDE_DIRS) | set(args.exclude_dir or [])
        res = apply_translations(
            root=root,
            lang=args.lang,
            dict_path=dict_path,
            out_dir=out_dir,
            in_place=bool(args.in_place),
            exts=exts,
            exclude_dirs=exclude_dirs,
            token_prefix=args.token_prefix,
            token_suffix=args.token_suffix,
            dry_run=bool(args.dry_run),
            max_file_bytes=int(args.max_file_bytes),
        )
        print(
            f"apply: scanned_files={res.file_count} changed_files={res.changed_files} replaced_tokens={res.replaced_tokens} missing_keys={res.missing_keys} dict={dict_path}"
        )
        if args.dry_run:
            print("(dry-run) no files written")
        return 0

    if args.cmd == "embed-switch":
        html_path = Path(args.html).expanduser().resolve()
        root = (
            Path(args.root).expanduser().resolve()
            if args.root
            else html_path.parent.resolve()
        )
        langs = [s.strip() for s in str(args.langs).split(",") if s.strip()]
        if not langs:
            raise RuntimeError("No langs provided: --langs zh-CN,en-US")
        embed_html_language_switcher(
            html_path=html_path,
            root=root,
            dict_dir=str(args.dict_dir),
            langs=langs,
            default_lang=str(args.default_lang),
            token_prefix=str(args.token_prefix),
            token_suffix=str(args.token_suffix),
            dry_run=bool(args.dry_run),
        )
        print(f"embed-switch: html={html_path} root={root} langs={','.join(langs)}")
        if args.dry_run:
            print("(dry-run) no files written")
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
