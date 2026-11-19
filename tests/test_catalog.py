"""The catalog, its stable ids and its icon files (no browser needed)."""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = json.loads((ROOT / "src/catalog.json").read_text(encoding="utf-8"))
CELL = 32


def test_ids_are_unique_and_fit_one_byte():
    ids = [p["id"] for p in CATALOG]
    assert len(ids) == len(set(ids))
    assert all(1 <= i <= 255 for i in ids)


def test_slugs_are_unique():
    slugs = [p["slug"] for p in CATALOG]
    assert len(slugs) == len(set(slugs))


def test_ids_are_never_reused_or_renumbered():
    """Ids are permanent. New pieces may be added; existing ids must keep their slug."""
    frozen = json.loads((ROOT / "tests/catalog_ids.json").read_text())
    current = {str(p["id"]): p["slug"] for p in CATALOG}
    for pid, slug in frozen.items():
        assert current.get(pid) == slug, f"id {pid} ({slug}) was removed, renumbered or reused"


def test_every_piece_has_an_icon_with_a_matching_viewbox():
    for piece in CATALOG:
        path = ROOT / "src/icons" / piece["folder"] / f"{piece['slug']}.svg"
        assert path.is_file(), f"missing icon {path}"
        root = ET.parse(path).getroot()
        expected = f"0 0 {piece['w'] * CELL} {piece['h'] * CELL}"
        assert " ".join(root.get("viewBox", "").split()) == expected, path


def test_no_orphan_icons():
    known = {(p["folder"], p["slug"]) for p in CATALOG}
    for path in (ROOT / "src/icons").rglob("*.svg"):
        assert (path.parent.name, path.stem) in known, f"{path} is not in catalog.json"


def test_icons_are_safe_svg():
    for path in (ROOT / "src/icons").rglob("*.svg"):
        text = path.read_text(encoding="utf-8").lower()
        for bad in ("<script", "onload", "onclick", "<foreignobject", "http://", "javascript:"):
            if bad == "http://":
                # the xmlns declaration is the only allowed URL
                assert text.replace('xmlns="http://www.w3.org/2000/svg"', "").count(bad) == 0, path
            else:
                assert bad not in text, f"{path} contains {bad}"


def test_edge_pieces_are_one_by_one():
    for piece in CATALOG:
        if piece.get("edge"):
            assert piece["w"] == piece["h"] == 1


def test_monsters_are_one_by_one_and_listed():
    monsters = {p["slug"] for p in CATALOG if p.get("monster")}
    assert monsters == {
        "goblin",
        "orc",
        "abomination",
        "skeleton",
        "zombie",
        "mummy",
        "gargoyle",
        "dread-warrior",
    }
