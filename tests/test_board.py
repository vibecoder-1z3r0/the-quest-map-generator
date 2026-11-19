"""The board layout file and the generated board (no browser needed)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROWS = [
    ln
    for ln in (ROOT / "src/board.txt").read_text(encoding="utf-8").splitlines()
    if ln.strip() and not ln.startswith("//")
]

# room letter -> (columns, rows, number of squares), from the standard board
EXPECTED = {
    "A": (4, 3, 12), "B": (4, 3, 12), "C": (3, 5, 15), "D": (3, 5, 15), "E": (4, 4, 16),
    "F": (4, 4, 16), "G": (4, 5, 20), "H": (4, 5, 20), "I": (4, 4, 16), "J": (4, 4, 16),
    "K": (6, 5, 30), "L": (4, 4, 16), "M": (2, 3, 6), "N": (2, 3, 6), "O": (4, 4, 15),
    "P": (4, 4, 16), "Q": (4, 5, 20), "R": (3, 5, 15), "S": (4, 5, 20), "T": (4, 4, 16),
    "U": (3, 4, 12), "V": (4, 4, 16),
}  # fmt: skip


def squares(letter):
    return [(x, y) for y, row in enumerate(ROWS) for x, ch in enumerate(row) if ch == letter]


def test_board_is_19_rows_of_26_known_characters():
    assert len(ROWS) == 19
    assert all(len(r) == 26 for r in ROWS)
    assert set("".join(ROWS)) <= set(".#ABCDEFGHIJKLMNOPQRSTUVWXYZ")


def test_the_standard_board_has_22_rooms_with_the_expected_shapes():
    letters = sorted({ch for r in ROWS for ch in r if ch.isalpha()})
    assert letters == sorted(EXPECTED)
    for letter, (w, h, count) in EXPECTED.items():
        cells = squares(letter)
        xs, ys = [c[0] for c in cells], [c[1] for c in cells]
        assert (max(xs) - min(xs) + 1, max(ys) - min(ys) + 1, len(cells)) == (w, h, count), letter


def test_the_outer_ring_is_corridor():
    assert set(ROWS[0]) == {"."} and set(ROWS[-1]) == {"."}
    assert all(r[0] == "." and r[-1] == "." for r in ROWS)


def test_the_generated_board_is_in_the_built_page():
    page = (ROOT / "dist/index.html").read_text(encoding="utf-8")
    assert 'id="board-art"' in page
    assert "Generated from src/board.txt" in page
