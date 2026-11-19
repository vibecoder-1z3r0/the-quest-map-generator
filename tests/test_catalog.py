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
        "dread-warlock",
    }


def test_tiles_are_one_by_one_icons_and_not_in_the_item_groups():
    tiles = [p for p in CATALOG if p.get("tile")]
    assert [p["slug"] for p in tiles] == ["room-tile"]
    assert all(p["w"] == p["h"] == 1 and p["group"] == "Room tiles" for p in tiles)


def test_the_provisional_open_wall_piece_is_gone():
    assert "open-wall" not in {p["slug"] for p in CATALOG}


SETS = json.loads((ROOT / "src/sets.json").read_text(encoding="utf-8"))


def test_every_piece_names_a_known_set():
    set_ids = {s["id"] for s in SETS}
    assert len(set_ids) == len(SETS)
    for piece in CATALOG:
        assert piece.get("set") in set_ids, f"{piece['slug']} has no valid set"


def test_everything_is_tagged_base_for_now_and_all_heroes_share_one_group():
    """The eight added heroes are really expansion heroes, tagged base until their sets are known."""
    assert {s["id"] for s in SETS} == {"base"}
    assert {p["set"] for p in CATALOG} == {"base"}
    heroes = {p["slug"] for p in CATALOG if p["group"] == "Heroes"}
    assert {"barbarian", "dwarf", "elf", "wizard", "bard", "wandering-monk"} <= heroes
    assert len(heroes) == 12


def test_heroes_are_one_by_one_tokens_and_never_monsters():
    for piece in CATALOG:
        if piece["group"] == "Heroes":
            assert (piece["w"], piece["h"]) == (1, 1) and not piece.get("monster")


def test_groups_are_categories_not_sets():
    """Expansion pieces join their natural group (Monsters, Furniture, ...), never a group per set."""
    names = {s["id"].lower() for s in SETS} | {s["name"].lower() for s in SETS}
    for piece in CATALOG:
        assert piece["group"].lower() not in names, f"{piece['slug']}: group is named after a set"


def test_monster_body_points_match_the_owner_supplied_values():
    bp = {p["slug"]: p["bp"] for p in CATALOG if p.get("monster")}
    assert bp == {
        "goblin": 1, "orc": 1, "zombie": 1, "skeleton": 1,
        "abomination": 2, "mummy": 2,
        "gargoyle": 3, "dread-warrior": 3,
        "dread-warlock": None,  # not set yet: shown as n/a in the statistics, never guessed
    }  # fmt: skip
