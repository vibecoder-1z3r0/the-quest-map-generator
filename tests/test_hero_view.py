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
        st["zones"][x] = 1  # zone 1 on (3, 0) and (4, 0)
    st["hl"][5] = 1  # (5, 0) is solid stone in a zone-less corridor ...
    st["zones"][5] = 1  # ... but it belongs to zone 1, so it stays hidden with the zone
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


def fogged(page, x, y):
    """Whether the fog covers the middle of square (x, y), asked of the browser's own geometry."""
    return page.evaluate(
        "([x, y]) => { const p = document.querySelector('#layer-fog path');"
        " return p ? p.isPointInFill(new DOMPoint(x * 32 + 16, y * 32 + 16)) : false; }",
        [x, y],
    )


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


def test_the_hero_header_explains_how_to_play(page, site):
    open_hero(page, site)
    hint = page.locator("#hero-hint").inner_text()
    for word in ("Tap", "Reveal", "search"):
        assert word.lower() in hint.lower(), word


def test_the_whole_quest_line_is_in_the_hero_header_on_a_phone_and_not_cut_off(page, site):
    page.set_viewport_size({"width": 390, "height": 844})
    st = hero_state(title="The Stone Tablets of Uganoth and the Long Road Home")
    open_hero(page, site, st)
    line = page.locator("#head-title")
    assert line.inner_text() == "The Order: Quest 1 - " + st["title"]
    assert line.evaluate("e => e.scrollWidth <= e.clientWidth + 1")


def test_the_hero_quest_card_leaves_out_the_title_the_header_already_shows(page, site):
    open_hero(page, site)
    card = page.locator("#hero-quest").inner_text()
    assert "Test quest" not in card and "The Order" not in card
    assert "Long ago a wizard lived here." in card and "Wandering monster: Goblin" in card


def test_hidden_regions_and_plain_corridor_are_covered_by_one_flat_fog(page, site):
    open_hero(page, site)
    assert fogged(page, 1, 1)  # room A is fogged
    assert fogged(
        page, 0, 0
    )  # and so is plain corridor: a square in no room or zone is solid stone
    assert fogged(page, 3, 0)  # and a zone
    assert not fogged(page, 22, 2)  # room F is revealed at the start, so it is not covered
    assert page.locator("#layer-fog path").count() == 1  # a single shape, so there are no seams
    assert page.locator("#layer-fog path").get_attribute("fill") == "#2b2118"


def test_only_what_the_heroes_can_see_is_drawn(page, site):
    open_hero(page, site)
    # nothing is visible at the start: the goblin in plain corridor is solid stone and the door's
    # corridor side is too, so only revealing a room can show things
    assert visible_pieces(page) == 0
    tap(page, 2, 2)
    page.click("#hero-reveal")
    confirm(page)
    # room A revealed: its goblin, chest and the door in its wall, but never the marker, the trap or the
    # unsearched secret door, and still not the goblin in the plain corridor
    assert visible_pieces(page) == 3


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
    page.click("#hero-search-tr")
    assert "You find nothing." in panel(page)
    page.click("#hero-search-t")
    assert "Shuffle the treasure deck and draw the top card." in panel(page)


def test_written_treasure_text_replaces_the_deck_instruction(page, site):
    open_hero(page, site)  # room A has the treasure text "A purse: 84 gold."
    tap(page, 2, 2)
    page.click("#hero-reveal")
    confirm(page)
    page.click("#hero-search-t")
    assert "A purse: 84 gold." in panel(page)
    assert "Shuffle the treasure deck" not in panel(page)


def test_revealing_one_room_of_a_group_reveals_the_others(page, site):
    open_hero(page, site)
    tap(page, 12, 8)  # room K
    page.click("#hero-reveal")
    confirm(page)
    assert revealed(page, K) and revealed(page, N)
    assert "K reads" in panel(page) and "N reads" in panel(page)


def test_a_zone_above_the_tenth_reveals_like_any_other_and_its_play_state_is_kept(page, site):
    st = hero_state()
    st["zones"][3] = 17  # (3, 0) is in zone 17, which is region 42
    st["rooms"][42] = {"start": False, "group": 0, "texts": ["Zone seventeen reads.", "", "", ""]}
    open_hero(page, site, st)
    assert fogged(page, 3, 0)
    tap(page, 3, 0)
    assert "hallway" in panel(page).lower()
    page.click("#hero-reveal")
    confirm(page)
    assert "Zone seventeen reads." in panel(page)
    assert not fogged(page, 3, 0)
    assert 42 in played(page)["rev"]


def test_a_hallway_is_called_hallway_and_its_zone_name_never_appears(page, site):
    open_hero(page, site)
    tap(page, 3, 0)
    assert "hallway" in panel(page).lower()
    page.click("#hero-reveal")
    confirm(page)
    assert "A cold hallway." in panel(page)
    assert "SECRET ZONE NAME" not in page.inner_text("body")


def test_a_revealed_hallway_has_no_treasure_search_but_keeps_the_others(page, site):
    open_hero(page, site)
    tap(page, 3, 0)  # a zone square
    page.click("#hero-reveal")
    confirm(page)
    assert page.locator("#hero-search-t").count() == 0
    assert page.locator("#hero-search-tr").is_visible()
    assert page.locator("#hero-search-sd").is_visible()
    assert "Search for treasure" not in panel(page)


def test_a_revealed_hallway_with_a_treasure_chest_can_be_searched_for_treasure(page, site):
    st = hero_state()
    st["items"].append((CHEST, 3, 0, 0))  # a chest on a square of zone 1
    open_hero(page, site, st)
    tap(page, 3, 0)
    page.click("#hero-reveal")
    confirm(page)
    page.click("#hero-search-t")
    assert "Shuffle the treasure deck and draw the top card." in panel(page)


def test_a_revealed_room_still_has_the_treasure_search(page, site):
    open_hero(page, site)
    tap(page, 2, 2)
    page.click("#hero-reveal")
    confirm(page)
    assert page.locator("#hero-search-t").is_visible()


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


def test_in_the_single_column_layout_reveal_is_above_the_map_and_the_quest_info_below_it(
    page, site
):
    page.set_viewport_size({"width": 390, "height": 844})
    open_hero(page, site)
    tap(page, 2, 2)  # a hidden room, so the card with the Reveal button shows
    board = page.locator("#board").bounding_box()
    region = page.locator("#hero-region").bounding_box()
    quest = page.locator("#hero-quest").bounding_box()
    assert region["y"] + region["height"] <= board["y"] + 2
    assert board["y"] - (region["y"] + region["height"]) < 120
    assert quest["y"] >= board["y"] + board["height"] - 2
    assert page.locator("#hero-reveal").bounding_box()["y"] < board["y"]


def test_on_a_wide_screen_both_hero_cards_stay_in_the_side_column(page, site):
    open_hero(page, site)
    board = page.locator("#board").bounding_box()
    quest = page.locator("#hero-quest").bounding_box()
    region = page.locator("#hero-region").bounding_box()
    assert quest["x"] >= board["x"] + board["width"] - 2
    assert region["x"] >= board["x"] + board["width"] - 2


def test_stone_in_a_zone_is_hidden_until_the_zone_is_revealed(page, site):
    open_hero(page, site)
    assert page.locator("#layer-hl rect").count() == 0  # the stone at (5, 0) is not drawn yet
    tap(page, 3, 0)
    page.click("#hero-reveal")
    confirm(page)
    assert page.locator("#layer-hl rect").count() == 1  # now it shows as stone


def test_hero_view_does_not_print_and_never_prints_zargons_notes(page, site):
    open_hero(page, site)
    page.emulate_media(media="print")
    text = page.inner_text("body")
    assert (
        "TOP SECRET NOTES" not in text
    )  # the print layout holds Zargon's notes; hero view must not print it
    assert "meant for a screen" in text  # a short note says where to print from
    assert not page.locator("#board").is_visible()
    assert not page.locator("#printsheet").is_visible()


def test_the_editor_still_prints_normally(page, site):
    st = hero_state(hero=False)
    open_link(page, site, ref.encode(st))
    page.emulate_media(media="print")
    assert "TOP SECRET NOTES" in page.inner_text("body")
    assert "meant for a screen" not in page.inner_text("body")


def selected_squares(page):
    return page.locator("#layer-overlay .hero-sel").evaluate_all(
        "els => els.map(e => [Number(e.getAttribute('x')) / 32, Number(e.getAttribute('y')) / 32])"
    )


def test_tapping_a_zone_highlights_only_the_tapped_square(page, site):
    open_hero(page, site)
    tap(page, 3, 0)  # zone 1 covers (3, 0) and (4, 0)
    assert selected_squares(page) == [[3, 0]]  # not the whole zone, which would give its shape away


def test_tapping_a_room_highlights_the_room_and_plain_corridor_one_square(page, site):
    open_hero(page, site)
    tap(page, 2, 2)  # room A is 4 x 3 squares
    assert len(selected_squares(page)) == 12
    tap(page, 10, 0)  # plain corridor
    assert selected_squares(page) == [[10, 0]]


def test_a_hallway_in_no_zone_offers_reveal_and_then_says_it_is_solid_stone(page, site):
    open_hero(page, site)
    tap(page, 10, 0)  # plain corridor, in no zone
    assert "hallway" in panel(page).lower()
    page.click("#hero-reveal")
    page.wait_for_selector("#confirm-dialog[open]")
    assert "Nothing to reveal. This is solid stone." in page.inner_text("#confirm-message")
    assert not page.locator("#confirm-cancel").is_visible()  # it is a message, not a question
    page.click("#confirm-ok")
    page.wait_for_selector("#confirm-dialog:not([open])", state="attached")
    assert played(page) is None  # nothing changed
    assert fogged(page, 10, 0)  # and it stays fogged


def test_the_message_dialog_does_not_hide_the_cancel_button_of_later_questions(page, site):
    open_hero(page, site)
    tap(page, 10, 0)
    page.click("#hero-reveal")
    page.click("#confirm-ok")
    tap(page, 2, 2)
    page.click("#hero-reveal")
    page.wait_for_selector("#confirm-dialog[open]")
    assert page.locator("#confirm-cancel").is_visible()
    page.click("#confirm-cancel")


def test_a_found_secret_door_in_the_fog_shows_on_its_own_square(page, site):
    st = hero_state()
    st["items"] = [(SECRET_DOOR, 7, 9, 0)]  # corridor square between rooms H (7) and N (13)
    st["rooms"] = {7: {"start": False, "group": 0, "texts": ["", "", "", "found"]}}
    open_hero(page, site, st)
    assert visible_pieces(page) == 0
    tap(page, 6, 6)  # room H
    page.click("#hero-reveal")
    confirm(page)
    page.click("#hero-search-sd")
    assert visible_pieces(page) == 1
    assert "M224 288" not in page.locator("#layer-fog path").get_attribute(
        "d"
    )  # (7, 9) is not covered


def search_secret_doors_in_a(page, site, secret_text):
    st = hero_state()
    st["rooms"][A]["texts"][3] = secret_text
    open_hero(page, site, st)
    tap(page, 2, 2)
    page.click("#hero-reveal")
    confirm(page)
    page.click("#hero-search-sd")


def test_a_found_secret_door_is_announced_when_the_secret_door_text_is_blank(page, site):
    search_secret_doors_in_a(page, site, "")
    assert "You find a secret door." in panel(page)
    assert "You find nothing." not in panel(page)


def test_the_secret_door_text_replaces_the_announcement_when_there_is_one(page, site):
    search_secret_doors_in_a(page, site, "Hollow wall.")
    assert "Hollow wall." in panel(page)
    assert "You find a secret door." not in panel(page)


def test_a_secret_door_search_that_finds_nothing_still_says_nothing_found(page, site):
    st = hero_state()
    st["items"] = [it for it in st["items"] if it[0] != SECRET_DOOR]
    st["rooms"][A]["texts"][3] = ""
    open_hero(page, site, st)
    tap(page, 2, 2)
    page.click("#hero-reveal")
    confirm(page)
    page.click("#hero-search-sd")
    assert "You find nothing." in panel(page)


def test_several_found_secret_doors_are_counted_in_the_announcement(page, site):
    st = hero_state()
    st["rooms"][A]["texts"][3] = ""
    st["items"].append((SECRET_DOOR, 2, 1, 0))
    open_hero(page, site, st)
    tap(page, 2, 2)
    page.click("#hero-reveal")
    confirm(page)
    page.click("#hero-search-sd")
    assert "You find 2 secret doors." in panel(page)
