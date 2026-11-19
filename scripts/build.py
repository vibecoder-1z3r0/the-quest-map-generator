#!/usr/bin/env python3
"""Combine src/ into a single dist/index.html.

Inlines the CSS, the JS modules, the piece icons (as an SVG sprite), the board and the catalog.
Icons come from icons-custom/ when present, else src/icons/. A missing or malformed icon fails
the build. Prints a table of which file is used for every piece.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
CUSTOM = ROOT / "icons-custom"
DIST = ROOT / "dist"
CELL = 32
COLS, ROWS = 26, 19
SVG_NS = "http://www.w3.org/2000/svg"

# Dependency order. Modules share one flat scope after bundling, so top-level names must be unique.
JS_ORDER = [
    "constants",
    "catalog",
    "text",
    "markdown",
    "format",
    "state",
    "render",
    "ui",
    "main",
]

FORBIDDEN_TAGS = {"script", "foreignObject", "iframe", "object", "embed", "image"}


class BuildError(Exception):
    pass


def local(tag: str) -> str:
    return tag.split("}", 1)[-1]


def validate_svg(path: Path, view_box: str) -> ET.Element:
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        raise BuildError(f"{path}: not well-formed XML ({exc})") from exc
    if local(root.tag) != "svg":
        raise BuildError(f"{path}: root element must be <svg>")
    vb = " ".join(root.get("viewBox", "").split())
    if vb != view_box:
        raise BuildError(f"{path}: viewBox must be '{view_box}', found '{vb}'")
    for el in root.iter():
        if local(el.tag) in FORBIDDEN_TAGS:
            raise BuildError(f"{path}: <{local(el.tag)}> is not allowed")
        for name, value in el.attrib.items():
            n = local(name)
            if n.lower().startswith("on"):
                raise BuildError(f"{path}: event handler attribute '{n}' is not allowed")
            if n == "href" and not value.startswith("#"):
                raise BuildError(f"{path}: external reference '{value}' is not allowed")
            if "url(" in value and not re.fullmatch(r".*url\(#[\w-]+\).*", value):
                raise BuildError(f"{path}: external url() reference in '{value}'")
    return root


def inner_xml(root: ET.Element) -> str:
    ET.register_namespace("", SVG_NS)
    parts = []
    if root.text and root.text.strip():
        parts.append(root.text)
    for child in root:
        parts.append(ET.tostring(child, encoding="unicode"))
    xml = "".join(parts)
    return xml.replace(f' xmlns="{SVG_NS}"', "").replace("ns0:", "")


def find_icon(slug: str, folder: str) -> tuple[Path, str]:
    for cand in (CUSTOM / f"{slug}.svg", CUSTOM / folder / f"{slug}.svg"):
        if cand.is_file():
            return cand, "custom"
    default = SRC / "icons" / folder / f"{slug}.svg"
    if default.is_file():
        return default, "default"
    raise BuildError(f"missing icon for '{slug}': expected {default.relative_to(ROOT)}")


def build_sprites(catalog: list[dict]) -> str:
    rows = []
    symbols = []
    for piece in catalog:
        slug, folder = piece["slug"], piece["folder"]
        w, h = piece["w"], piece["h"]
        path, origin = find_icon(slug, folder)
        vb = f"0 0 {w * CELL} {h * CELL}"
        root = validate_svg(path, vb)
        symbols.append(
            f'<symbol id="icon-{slug}" viewBox="{vb}" overflow="visible">{inner_xml(root)}</symbol>'
        )
        rows.append((piece["id"], slug, f"{w}x{h}", origin, str(path.relative_to(ROOT))))
    print(f"{'id':>4}  {'slug':<18} {'size':<5} {'source':<8} file")
    for pid, slug, size, origin, rel in rows:
        print(f"{pid:>4}  {slug:<18} {size:<5} {origin:<8} {rel}")
    return "\n".join(symbols)


def build_board() -> str:
    vb = f"0 0 {COLS * CELL} {ROWS * CELL}"
    custom = CUSTOM / "board.svg"
    path = custom if custom.is_file() else SRC / "board.svg"
    root = validate_svg(path, vb)
    print(f"board: {path.relative_to(ROOT)} ({'custom' if path == custom else 'default'})")
    return f'<symbol id="board-art" viewBox="{vb}">{inner_xml(root)}</symbol>'


def check_catalog(catalog: list[dict]) -> None:
    ids = [p["id"] for p in catalog]
    slugs = [p["slug"] for p in catalog]
    if len(set(ids)) != len(ids):
        raise BuildError("catalog.json: duplicate ids")
    if len(set(slugs)) != len(slugs):
        raise BuildError("catalog.json: duplicate slugs")
    for p in catalog:
        if not 1 <= p["id"] <= 255:
            raise BuildError(f"catalog.json: id {p['id']} out of range 1..255")


def bundle_js() -> str:
    seen: dict[str, str] = {}
    out = []
    decl = re.compile(
        r"^(?:export\s+)?(?:async\s+)?(?:function\*?|const|let|class)\s+([A-Za-z_$][\w$]*)", re.M
    )
    for name in JS_ORDER:
        path = SRC / "js" / f"{name}.js"
        if not path.is_file():
            raise BuildError(f"missing module {path.relative_to(ROOT)}")
        code = path.read_text(encoding="utf-8")
        for ident in decl.findall(code):
            if ident in seen:
                raise BuildError(f"top-level name '{ident}' declared in {seen[ident]} and {name}")
            seen[ident] = name
        code = re.sub(r"^import\b[^;]*;[ \t]*\n?", "", code, flags=re.M)
        code = re.sub(
            r"^export\s+(?=(?:async\s+)?(?:function|const|let|class)\b)", "", code, flags=re.M
        )
        if re.search(r"^export\b", code, flags=re.M):
            raise BuildError(f"{name}.js: unsupported export form")
        out.append(f"// ---- {name}.js ----\n{code.strip()}\n")
    return "\n".join(out)


def version_string() -> str:
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except Exception:
        sha = "unknown"
    try:
        tag = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except Exception:
        tag = "dev"
    return f"{tag} ({sha})"


def main() -> int:
    try:
        catalog = json.loads((SRC / "catalog.json").read_text(encoding="utf-8"))
        check_catalog(catalog)
        sprites = build_sprites(catalog) + "\n" + build_board()
        js = bundle_js().replace("/*@CATALOG@*/ []", json.dumps(catalog, separators=(",", ":")))
        if "/*@CATALOG@*/" in js:
            raise BuildError("catalog placeholder not replaced")
        css = (SRC / "style.css").read_text(encoding="utf-8")
        html = (SRC / "index.html").read_text(encoding="utf-8")
        for marker in ("/*@CSS@*/", "/*@JS@*/", "<!--@SPRITES@-->"):
            if marker not in html:
                raise BuildError(f"index.html is missing {marker}")
        if "</script" in js.lower():
            raise BuildError("JS must not contain a closing script tag")
        html = (
            html.replace("/*@CSS@*/", css)
            .replace("<!--@SPRITES@-->", sprites)
            .replace("@VERSION@", version_string())
            .replace("/*@JS@*/", js)
        )
        DIST.mkdir(exist_ok=True)
        (DIST / "index.html").write_text(html, encoding="utf-8")
        print(f"\nwrote dist/index.html ({len(html) / 1024:.1f} KiB)")
        return 0
    except BuildError as exc:
        print(f"build failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
