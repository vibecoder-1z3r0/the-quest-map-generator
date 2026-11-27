#!/usr/bin/env python3
"""Regenerate tests/golden/v1.json using the independent reference encoder.

Golden links are committed so that links issued today must keep decoding forever. Only run this
before the first tagged release; afterwards add new files and never change existing entries.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))
import reference as ref  # noqa: E402

catalog = {p["slug"]: p["id"] for p in json.loads((ROOT / "src/catalog.json").read_text())}


def case(name: str, **fields) -> dict:
    st = ref.blank()
    st.update(fields)
    st["items"] = [list(i) for i in st["items"]]
    return {
        "name": name,
        "url": ref.encode({**st, "items": [tuple(i) for i in st["items"]]}),
        "state": st,
    }


def hl_cells(values: dict[int, int]) -> list[int]:
    hl = [0] * ref.SQUARES
    for idx, v in values.items():
        hl[idx] = v
    return hl


CASES = [
    case("blank-light"),
    case("blank-dark", theme=1),
    case(
        "every-rotation",
        items=[
            (catalog["table"], 4, 4, 0),
            (catalog["table"], 10, 4, 1),
            (catalog["table"], 4, 10, 2),
            (catalog["table"], 10, 10, 3),
        ],
    ),
    case(
        "doors-all-edges-and-outer",
        items=[
            (catalog["door"], 0, 0, 0),
            (catalog["door"], 25, 18, 1),
            (catalog["hidden-door"], 12, 9, 2),
            (catalog["door"], 0, 5, 3),
        ],
    ),
    case(
        "highlights",
        hl=hl_cells({0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 493: 1, 25: 6}),
        legend={2: "any trap", 3: "secret room"},
    ),
    case(
        "room-tiles",
        items=[(catalog["goblin"], 5, 5, 0)],
        tiles=[
            (catalog["room-tile"], 4, 10, 2, 3),
            (catalog["room-tile"], 0, 0, 26, 19),
            (catalog["room-tile"], 25, 18, 1, 1),
        ],
    ),
    case(
        "full-quest",
        theme=1,
        items=[
            (catalog["goblin"], 5, 5, 0),
            (catalog["orc"], 5, 5, 0),
            (catalog["stairs"], 1, 1, 0),
        ],
        num="3",
        title="The Underüground Vault",
        intro="Welcome, **heroes**.\n\n\nGood luck.",
        notes="# Secrets\n- Gold: 150\n\n| A | B |\n|---|---|\n| 1 | 2 |",
        wm_id=catalog["orc"],
        wm_text="plus 1 goblin",
    ),
    case("series", series="The Order of the Oth", num="1", title="The Stone Tablets of Uganoth"),
    case("unicode", title="日本語 éèê", notes="Привет - hello"),
    case("hero-view-flag", hero=True, title="Opens in hero view"),
    case(
        "hero-rooms-groups-and-zones",
        hl=hl_cells({26 * 3 + 0: 1, 26 * 5 + 5: 2}),  # stone and a trap highlight can be zoned too
        zones=hl_cells({26 * 3 + 0: 1, 26 * 3 + 1: 1, 26 * 4 + 0: 10, 26 * 5 + 5: 3}),
        legend={6: "North hallway", 15: "Last zone"},
        rooms={
            0: {
                "start": True,
                "group": 0,
                "texts": [
                    "The door grinds open.\nDust hangs in the air.",
                    "84 gold coins.",
                    "",
                    "Hollow wall.",
                ],
            },
            10: {
                "start": False,
                "group": 1,
                "texts": ["Room K read aloud", "", "A pressure plate.", ""],
            },
            11: {"start": False, "group": 1, "texts": ["Room L read aloud", "", "", "日本語 éèê"]},
            26: {"start": False, "group": 0, "texts": ["", "A hallway purse.", "", ""]},
            35: {"start": False, "group": 255, "texts": ["", "", "", ""]},
        },
    ),
    case(
        "hero-play-state",
        hero=True,
        rooms={0: {"start": True, "group": 0, "texts": ["Start room", "", "", ""]}},
        play={"rev": [0, 10, 26], "t": [10], "tr": [], "sd": [0, 35]},
    ),
    case("hero-play-state-all-hidden", hero=True, play={"rev": [], "t": [], "tr": [], "sd": []}),
    # Version 2: more than ten zones (zones 1-30 are regions 26-55, names are legend entries 6-35).
    case(
        "hero-many-zones-v2",
        hero=True,
        zones=[0] * 100 + [4, 17, 30] + [0] * (ref.SQUARES - 103),
        legend={6: "First", 22: "Seventeenth", 35: "Thirtieth"},
        rooms={
            3: {"start": True, "group": 0, "texts": ["Start", "", "", ""]},
            42: {"start": False, "group": 2, "texts": ["Zone 17 reads", "A chest.", "", "A door."]},
            55: {"start": False, "group": 2, "texts": ["Zone 30 reads", "", "", ""]},
        },
        play={"rev": [3, 42], "t": [42], "tr": [], "sd": [55]},
    ),
]

out = ROOT / "tests/golden/v1.json"
existing = json.loads(out.read_text(encoding="utf-8")) if out.exists() else []
known = {c["name"] for c in existing}
added = [c for c in CASES if c["name"] not in known]
# Append-only: links already in the file are what real users hold, so they are never rewritten.
out.write_text(json.dumps(existing + added, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"{out.relative_to(ROOT)}: kept {len(existing)} existing case(s), added {len(added)}")
