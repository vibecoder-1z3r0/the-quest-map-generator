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
    "board",
    "stats",
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


ROOM_COLORS = [
    "#f0d9b5",
    "#ecbcb4",
    "#bddbd1",
    "#cdd3ec",
    "#efe2a6",
    "#d3e6ae",
    "#f3cba8",
    "#bcd9e9",
]
CORRIDOR_COLOR = "#e2d9c6"
SOLID_COLOR = "#5b554e"
WALL_COLOR = "#3b2a1a"


def load_board() -> list[str]:
    """Parse src/board.txt into 19 strings of 26 characters and validate it."""
    path = SRC / "board.txt"
    rows = [
        line.rstrip("\n")
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("//")
    ]
    if len(rows) != ROWS:
        raise BuildError(f"board.txt: expected {ROWS} rows, found {len(rows)}")
    for n, row in enumerate(rows, 1):
        if len(row) != COLS:
            raise BuildError(f"board.txt: row {n} has {len(row)} columns, expected {COLS}")
        for ch in row:
            if not (ch in ".#" or "A" <= ch <= "Z"):
                raise BuildError(f"board.txt: row {n} has unknown character {ch!r}")
    for letter in sorted({ch for row in rows for ch in row if ch.isalpha()}):
        cells = {(x, y) for y, row in enumerate(rows) for x, ch in enumerate(row) if ch == letter}
        seen, stack = set(), [next(iter(cells))]
        while stack:
            x, y = stack.pop()
            if (x, y) in seen:
                continue
            seen.add((x, y))
            stack += [c for c in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)) if c in cells]
        if seen != cells:
            raise BuildError(f"board.txt: room {letter} is not one connected area")
    return rows


def room_colors(rows: list[str]) -> dict[str, str]:
    """Greedy colouring so rooms that share a wall get different tints."""
    letters = sorted({ch for row in rows for ch in row if ch.isalpha()})
    touching: dict[str, set[str]] = {k: set() for k in letters}
    for y in range(ROWS):
        for x in range(COLS):
            for nx, ny in ((x + 1, y), (x, y + 1)):
                if nx < COLS and ny < ROWS:
                    a, b = rows[y][x], rows[ny][nx]
                    if a != b and a.isalpha() and b.isalpha():
                        touching[a].add(b)
                        touching[b].add(a)
    colors: dict[str, str] = {}
    for letter in letters:
        used = {colors[o] for o in touching[letter] if o in colors}
        colors[letter] = next((c for c in ROOM_COLORS if c not in used), ROOM_COLORS[0])
    return colors


def board_svg(rows: list[str]) -> str:
    colors = room_colors(rows)
    w, h = COLS * CELL, ROWS * CELL
    tiles, walls = [], []
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            fill = CORRIDOR_COLOR if ch == "." else SOLID_COLOR if ch == "#" else colors[ch]
            tiles.append(
                f'<rect x="{x * CELL}" y="{y * CELL}" '
                f'width="{CELL}" height="{CELL}" fill="{fill}"/>'
            )
            for nx, ny, edge in (
                (x + 1, y, f"M{(x + 1) * CELL} {y * CELL}v{CELL}"),
                (x, y + 1, f"M{x * CELL} {(y + 1) * CELL}h{CELL}"),
            ):
                if nx < COLS and ny < ROWS:
                    other = rows[ny][nx]
                    if other != ch:
                        walls.append(edge)
    grid = "".join(f"M{i * CELL} 0V{h}" for i in range(1, COLS)) + "".join(
        f"M0 {j * CELL}H{w}" for j in range(1, ROWS)
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">'
        "<title>Board</title><desc>Generated from src/board.txt.</desc>"
        + "".join(tiles)
        + f'<path d="{grid}" stroke="#000" stroke-opacity=".13" stroke-width="1" fill="none"/>'
        + f'<path d="{"".join(walls)}" stroke="{WALL_COLOR}" stroke-width="5" '
        + 'stroke-linecap="square" fill="none"/>'
        + f'<rect x="3" y="3" width="{w - 6}" height="{h - 6}" fill="none" '
        + f'stroke="{WALL_COLOR}" stroke-width="6"/>'
        + "</svg>"
    )


def build_board(rows: list[str]) -> str:
    vb = f"0 0 {COLS * CELL} {ROWS * CELL}"
    custom = CUSTOM / "board.svg"
    if custom.is_file():
        root = validate_svg(custom, vb)
        print(f"board art: {custom.relative_to(ROOT)} (custom); room map from src/board.txt")
    else:
        tmp = ET.fromstring(board_svg(rows))
        root = tmp
        print("board art: generated from src/board.txt")
    return f'<symbol id="board-art" viewBox="{vb}">{inner_xml(root)}</symbol>'


def check_catalog(catalog: list[dict], sets: list[dict]) -> None:
    set_ids = [s["id"] for s in sets]
    if len(set(set_ids)) != len(set_ids):
        raise BuildError("sets.json: duplicate set ids")
    for p in catalog:
        if p.get("set") not in set_ids:
            raise BuildError(
                f"catalog.json: '{p['slug']}' has unknown or missing set {p.get('set')!r}"
            )
    ids = [p["id"] for p in catalog]
    slugs = [p["slug"] for p in catalog]
    if len(set(ids)) != len(ids):
        raise BuildError("catalog.json: duplicate ids")
    if len(set(slugs)) != len(slugs):
        raise BuildError("catalog.json: duplicate slugs")
    for p in catalog:
        if not 1 <= p["id"] <= 255:
            raise BuildError(f"catalog.json: id {p['id']} out of range 1..255")
        if p.get("tile") and (p["w"], p["h"]) != (1, 1):
            raise BuildError(f"catalog.json: tile '{p['slug']}' must be a 1x1 icon")


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
        sets = json.loads((SRC / "sets.json").read_text(encoding="utf-8"))
        check_catalog(catalog, sets)
        board_rows = load_board()
        sprites = build_sprites(catalog) + "\n" + build_board(board_rows)
        js = bundle_js().replace("/*@CATALOG@*/ []", json.dumps(catalog, separators=(",", ":")))
        js = js.replace("/*@BOARD@*/ []", json.dumps(board_rows))
        js = js.replace("/*@SETS@*/ []", json.dumps(sets, separators=(",", ":")))
        if any(m in js for m in ("/*@CATALOG@*/", "/*@BOARD@*/", "/*@SETS@*/")):
            raise BuildError("catalog, board or sets placeholder not replaced")
        unset = [
            p["name"]
            for p in catalog
            if p.get("monster") and p.get("bp") is None and not p.get("bp_varies")
        ]
        if unset:
            print(f"note: no body point (BP) value yet for: {', '.join(unset)}")
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
