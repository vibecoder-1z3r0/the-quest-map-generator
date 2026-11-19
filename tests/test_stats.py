"""Quest statistics: totals, room averages, highest room, corridors, wandering monster."""

from __future__ import annotations

import pytest
import reference as ref
from conftest import ROOT, click_cell, open_link, pick_piece
from test_visual import catalog_ids


def room_squares(letter):
    rows = [
        ln
        for ln in (ROOT / "src/board.txt").read_text(encoding="utf-8").splitlines()
        if ln.strip() and not ln.startswith("//")
    ]
    return [(x, y) for y, row in enumerate(rows) for x, ch in enumerate(row) if ch == letter]


STATS_JS = """
(bps) => {
  for (const [slug, bp] of Object.entries(bps)) QMG.CATALOG.find((c) => c.slug === slug).bp = bp;
  return QMG.computeStats(QMG.app.state);
}
"""


@pytest.fixture
def quest(page, site):
    """goblins x2 in room A, a mummy in B, an orc in D, an orc in a corridor; E and K partly grey."""
    ids = catalog_ids()
    st = ref.blank()
    st["items"] = [
        (ids["goblin"], 1, 1, 0),
        (ids["goblin"], 2, 1, 0),
        (ids["mummy"], 5, 1, 0),
        (ids["orc"], 14, 1, 0),
        (ids["orc"], 0, 0, 0),
        (ids["table"], 1, 2, 0),  # not a monster
    ]
    st["hl"][room_squares("E")[0][1] * 26 + room_squares("E")[0][0]] = 1
    st["hl"][room_squares("K")[3][1] * 26 + room_squares("K")[3][0]] = 1
    st["wm_id"] = ids["gargoyle"]
    st["wm_text"] = "plus a rat"
    open_link(page, site, ref.encode(st))
    return page


BPS = {"goblin": 1, "orc": 1, "mummy": 2, "gargoyle": 3}


def test_totals_count_every_monster_on_the_map_including_corridors(quest):
    s = quest.evaluate(STATS_JS, BPS)
    assert s["monsters"] == 5
    assert s["bp"] == 1 + 1 + 2 + 1 + 1
    assert s["bpKnown"] is True


def test_corridor_monsters_are_counted_separately_and_not_in_room_figures(quest):
    s = quest.evaluate(STATS_JS, BPS)
    assert s["corridor"] == {"count": 1, "bp": 1}
    assert s["occupiedRooms"] == ["A", "B", "D"]


def test_average_over_rooms_with_monsters(quest):
    s = quest.evaluate(STATS_JS, BPS)
    assert s["averageOccupied"] == pytest.approx((2 + 2 + 1) / 3)


def test_average_over_active_rooms_excludes_any_room_with_grey(quest):
    s = quest.evaluate(STATS_JS, BPS)
    assert "E" not in s["activeRooms"] and "K" not in s["activeRooms"]
    assert len(s["activeRooms"]) == 20
    assert s["averageActive"] == pytest.approx(5 / 20)


def test_highest_room_and_ties(quest):
    s = quest.evaluate(STATS_JS, BPS)
    assert s["highest"] == {"bp": 2, "rooms": ["A", "B"]}


def test_breakdown_by_type(quest):
    s = quest.evaluate(STATS_JS, BPS)
    assert {(t["name"], t["count"], t["bp"]) for t in s["types"]} == {
        ("Goblin", 2, 2),
        ("Mummy", 1, 2),
        ("Orc", 2, 2),
    }


def test_the_wandering_monster_is_never_counted(quest):
    s = quest.evaluate(STATS_JS, BPS)
    assert s["wandering"] == {"monster": "Gargoyle", "bp": 3, "text": "plus a rat"}
    assert s["monsters"] == 5  # unchanged by the wandering monster


def test_missing_bp_values_are_reported_not_guessed(quest):
    s = quest.evaluate(STATS_JS, {"goblin": None, "orc": 1, "mummy": 2})
    assert s["bpKnown"] is False
    assert s["missing"] == ["Goblin"]


def test_no_monsters_gives_zero_totals_and_no_averages(page):
    s = page.evaluate(STATS_JS, BPS)
    assert s["monsters"] == 0 and s["bp"] == 0
    assert s["averageOccupied"] is None and s["highest"] is None
    assert len(s["activeRooms"]) == 22


def test_the_card_shows_na_until_bp_values_exist_and_updates_live(page):
    page.evaluate("QMG.CATALOG.filter((c) => c.monster).forEach((c) => { c.bp = null; })")
    pick_piece(page, "goblin")
    click_cell(page, 2, 2)  # room A
    text = page.locator("#stats").inner_text()
    assert "Monsters\n1" in text and "n/a" in text and "BP is not set yet for: Goblin" in text
    page.evaluate("QMG.CATALOG.find((c) => c.slug === 'goblin').bp = 1")
    click_cell(page, 3, 2)
    text = page.locator("#stats").inner_text()
    assert "Total quest BP\n2" in text
    assert "Highest room BP\n2 (room A)" in text


def test_room_letters_are_labeled_on_the_board(page):
    assert page.locator("#layer-rooms text").count() == 22
    assert page.locator("#layer-rooms text").first.text_content() == "A"
