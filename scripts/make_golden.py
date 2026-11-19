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
    case("unicode", title="日本語 éèê", notes="Привет - hello"),
]

out = ROOT / "tests/golden/v1.json"
out.write_text(json.dumps(CASES, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"wrote {out.relative_to(ROOT)} ({len(CASES)} cases)")
