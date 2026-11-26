"""The hero view in the browser: fog, tapping rooms, reveal and search, confirmations, play state."""

from __future__ import annotations

import pytest
import reference as ref
from conftest import ROOT, click_cell, open_link  # noqa: F401

A, F, K, N, Z1 = 0, 5, 10, 13, 26
GOBLIN, CHEST, PIT_TRAP, MARKER_1, DOOR, SECRET_DOOR = 40, 30, 31, 80, 1, 4
READ = "The door grinds open."


@pytest.fixture(autouse=True)
def quick(page):
    page.set_default_timeout(4000)


def hero_state(**changes) -> dict:
    st = ref.blank()
    st["hero"] = True
    st["series"] = "The Order"
    st["num"] = "1"
    st["title"] = "Test quest"
    st["intro"] = "Long ago a **wizard** lived here."
    st["notes"] = "TOP SECRET NOTES"
    st["wm_id"] = GOBLIN
    st["legend"] = {6: "SECRET ZONE NAME"}
    for x in (3, 4):
        st["hl"][x] = 6  # zone 1 on (3, 0) and (4, 0)
    st["rooms"] = {
        A: {
            "start": False,
            "group": 0,
            "texts": [READ, "A purse: 84 gold.", "A pressure plate.", "Hollow wall."],
        },
        F: {"start": True, "group": 0, "texts": ["The start room.", "", "", ""]},
        K: {"start": False, "group": 1, "texts": ["K reads", "", "", ""]},
        N: {"start": False, "group": 1, "texts": ["N reads", "", "", ""]},
        Z1: {"start": False, "group": 0, "texts": ["A cold hallway.", "", "", ""]},
    }
    st["items"] = [
        (GOBLIN, 2, 2, 0),  # in room A
        (CHEST, 3, 2, 0),  # in room A
        (GOBLIN, 10, 0, 0),  # in plain corridor
        (GOBLIN, 3, 0, 0),  # on a zone square
        (MARKER_1, 4, 2, 0),  # a marker, never shown
        (PIT_TRAP, 4, 3, 0),  # a trap, never shown
        (SECRET_DOOR, 1, 1, 0),  # in room A, found only by its secret-door search
        (DOOR, 1, 2, 3),  # west wall of room A
    ]
    st.update(changes)
    return st


def open_hero(page, site, st=None):
    open_link(page, site, ref.encode(st or hero_state()))
    page.wait_for_selector("body.hero")


def visible_pieces(page):
    return page.locator("#layer-items use").count()


def panel(page):
    return page.locator("#hero-panel").inner_text()


def confirm(page):
    page.wait_for_selector("#confirm-dialog[open]")
    page.click("#confirm-ok")
    page.wait_for_selector("#confirm-dialog:not([open])", state="attached")


def tap(page, x, y):
    page.evaluate("window.scrollTo(0, 0)")
    click_cell(page, x, y)


def revealed(page, region):
    return page.evaluate("(r) => QMG.hero.isRevealed(QMG.app.state, r)", region)


def played(page):
    """The play state stored in the link right now, decoded by the reference implementation."""
    page.wait_for_timeout(450)  # the link is updated a moment after an action
    return ref.decode(page.evaluate("location.hash").lstrip("#"))["play"]


def test_a_hero_link_opens_in_hero_view_with_hero_controls_only(page, site):
    open_hero(page, site)
    assert page.locator("#hero-badge").is_visible()
    assert page.locator("#to-zargon").is_visible() and page.locator("#reset-game").is_visible()
    for hidden in ("#tools", "#undo", "#redo", "#clear", "#to-hero", "#inspector-card"):
        assert not page.locator(hidden).is_visible(), hidden


def test_the_hero_view_shows_the_quest_text_the_wandering_monster_but_never_the_notes(page, site):
    open_hero(page, site)
    text = page.inner_text("body")
    assert "test quest" in text.lower() and "Long ago a wizard lived here." in text
    assert "Wandering monster: Goblin" in text
    assert "TOP SECRET NOTES" not in text


def test_hidden_regions_are_covered_by_one_flat_fog_and_plain_corridor_is_not(page, site):
    open_hero(page, site)
    fog = page.locator("#layer-fog path").get_attribute("d")
    assert "M32 32" in fog  # room A's first square is fogged
    assert "M0 0" not in fog  # plain corridor is not
    assert page.locator("#layer-fog path").count() == 1  # a single shape, so there are no seams
    assert page.locator("#layer-fog path").get_attribute("fill") == "#2b2118"


def test_only_what_the_heroes_can_see_is_drawn(page, site):
    open_hero(page, site)
    # visible at the start: the goblin in plain corridor and the door (its corridor side is visible)
    assert visible_pieces(page) == 2
    tap(page, 2, 2)
    page.click("#hero-reveal")
    confirm(page)
    # room A revealed: its goblin and chest, but never the marker, the trap or the unsearched secret door
    assert visible_pieces(page) == 4


def test_tapping_a_hidden_room_offers_reveal_and_cancel_keeps_it_hidden(page, site):
    open_hero(page, site)
    tap(page, 2, 2)
    assert "room a" in panel(page).lower() and READ not in panel(page)
    page.click("#hero-reveal")
    page.wait_for_selector("#confirm-dialog[open]")
    page.click("#confirm-cancel")
    assert not revealed(page, A) and READ not in panel(page)


def test_confirming_the_reveal_shows_the_read_aloud_text_and_the_three_search_buttons(page, site):
    open_hero(page, site)
    tap(page, 2, 2)
    page.click("#hero-reveal")
    confirm(page)
    assert revealed(page, A)
    assert READ in panel(page)
    for kind in ("t", "tr", "sd"):
        assert page.locator(f"#hero-search-{kind}").is_visible()
    assert "A purse" not in panel(page)  # the treasure text only comes with the search


def test_searches_show_their_text_and_the_result_stays(page, site):
    open_hero(page, site)
    tap(page, 2, 2)
    page.click("#hero-reveal")
    confirm(page)
    page.click("#hero-search-t")
    assert "A purse: 84 gold." in panel(page)
    page.click("#hero-search-tr")
    assert "A pressure plate." in panel(page)
    tap(page, 12, 0)  # tap elsewhere and come back: results are still there
    tap(page, 2, 2)
    assert "A purse: 84 gold." in panel(page) and "A pressure plate." in panel(page)
    assert played(page)["t"] == [A] and played(page)["tr"] == [A]


def test_the_secret_door_search_finds_the_secret_door_but_a_trap_search_never_shows_traps(
    page, site
):
    open_hero(page, site)
    tap(page, 2, 2)
    page.click("#hero-reveal")
    confirm(page)
    before = visible_pieces(page)
    page.click("#hero-search-tr")
    assert visible_pieces(page) == before  # traps are never drawn
    page.click("#hero-search-sd")
    assert "Hollow wall." in panel(page)
    assert visible_pieces(page) == before + 1  # the secret door tile appears


def test_a_region_without_texts_still_has_all_search_buttons_and_says_so_politely(page, site):
    st = hero_state()
    del st["rooms"][A]
    open_hero(page, site, st)
    tap(page, 2, 2)
    page.click("#hero-reveal")
    confirm(page)
    assert all(page.locator(f"#hero-search-{k}").is_visible() for k in ("t", "tr", "sd"))
    page.click("#hero-search-t")
    assert "You find nothing." in panel(page)


def test_revealing_one_room_of_a_group_reveals_the_others(page, site):
    open_hero(page, site)
    tap(page, 12, 8)  # room K
    page.click("#hero-reveal")
    confirm(page)
    assert revealed(page, K) and revealed(page, N)
    assert "K reads" in panel(page) and "N reads" in panel(page)


def test_a_hallway_is_called_hallway_and_its_zone_name_never_appears(page, site):
    open_hero(page, site)
    tap(page, 3, 0)
    assert "hallway" in panel(page).lower()
    page.click("#hero-reveal")
    confirm(page)
    assert "A cold hallway." in panel(page)
    assert "SECRET ZONE NAME" not in page.inner_text("body")


def test_hide_again_and_reset_game_each_ask_first(page, site):
    open_hero(page, site)
    tap(page, 2, 2)
    page.click("#hero-reveal")
    confirm(page)
    assert revealed(page, A) and revealed(page, F)  # F is revealed at the start
    page.click("#hero-hide")
    confirm(page)
    assert not revealed(page, A) and revealed(page, F)
    tap(page, 2, 2)
    page.click("#hero-reveal")
    confirm(page)
    page.click("#reset-game")
    page.wait_for_selector("#confirm-dialog[open]")
    page.click("#confirm-cancel")
    assert revealed(page, A)
    page.click("#reset-game")
    confirm(page)
    assert not revealed(page, A) and revealed(page, F)
    assert played(page) is None  # a reset game goes back to a link with no play state


def test_play_does_not_touch_the_browser_history_and_has_no_undo(page, site):
    open_hero(page, site)
    length = page.evaluate("history.length")
    tap(page, 2, 2)
    page.click("#hero-reveal")
    confirm(page)
    page.click("#hero-search-t")
    page.keyboard.press("Control+z")
    assert page.evaluate("history.length") == length
    assert revealed(page, A)  # Ctrl+Z did nothing
    assert played(page)["rev"] == [A, F]


def test_the_play_state_survives_a_reload_of_the_same_link(page, site):
    open_hero(page, site)
    tap(page, 2, 2)
    page.click("#hero-reveal")
    confirm(page)
    page.wait_for_timeout(450)
    payload = page.evaluate("location.hash").lstrip("#")
    open_link(page, site, payload)
    page.wait_for_selector("body.hero")
    assert revealed(page, A)


def test_zargon_view_asks_first_with_a_warning_and_then_shows_everything(page, site):
    open_hero(page, site)
    page.click("#to-zargon")
    page.wait_for_selector("#confirm-dialog[open]")
    assert "secret" in page.inner_text("#confirm-message").lower()
    page.click("#confirm-cancel")
    assert page.evaluate("document.body.classList.contains('hero')")
    page.click("#to-zargon")
    confirm(page)
    assert not page.evaluate("document.body.classList.contains('hero')")
    assert page.locator("#tools").is_visible() and "TOP SECRET NOTES" in page.inner_text("body")
    page.wait_for_timeout(450)
    assert ref.decode(page.evaluate("location.hash").lstrip("#"))["hero"] is False


def test_the_zargon_view_can_switch_to_hero_view_keeping_the_play_state(page, site):
    st = hero_state(hero=False)
    st["play"] = {"rev": [A], "t": [], "tr": [], "sd": []}
    open_link(page, site, ref.encode(st))
    page.click("#to-hero")
    page.wait_for_selector("body.hero")
    assert revealed(page, A) and not revealed(page, F)
    assert not page.locator("#tools").is_visible()


def test_the_hero_panel_sits_right_after_the_map_in_the_single_column_layout(page, site):
    page.set_viewport_size({"width": 390, "height": 844})
    open_hero(page, site)
    board = page.locator("#board").bounding_box()
    hero_panel = page.locator("#hero-panel").bounding_box()
    assert hero_panel["y"] >= board["y"] + board["height"] - 2
    assert hero_panel["y"] < board["y"] + board["height"] + 120
