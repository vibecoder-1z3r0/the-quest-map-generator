"""Authoring hero view data in the editor: the room and zone card, groups, counters, Copy hero link."""

from __future__ import annotations

import pytest
import reference as ref
from conftest import click_cell, open_link

K, N, Z1 = 10, 13, 26


@pytest.fixture(autouse=True)
def quick(page):
    page.set_default_timeout(4000)


def pin(page, x, y):
    page.click('#tools button[data-kind="select"]')
    page.evaluate("window.scrollTo(0, 0)")
    click_cell(page, x, y)


def rooms(page):
    return page.evaluate("JSON.parse(JSON.stringify(QMG.app.state.rooms))")


def card_title(page):
    return page.locator("#hero-card summary").inner_text().lower()


def test_the_card_starts_collapsed_with_a_room_chooser(page):
    assert page.locator("#hero-card").is_visible()
    assert page.evaluate("document.querySelector('#hero-card details').open") is False
    chips = page.locator("#hero-chooser button[data-region]")
    letters = chips.evaluate_all("els => els.map(e => e.textContent.trim())")
    assert (
        letters[0] == "A" and letters[-1] == "V" and len(letters) == 22
    )  # the board's rooms, no zones yet


def test_pinning_a_room_square_opens_the_card_for_that_room(page):
    pin(page, 12, 8)  # room K
    assert page.evaluate("document.querySelector('#hero-card details').open") is True
    assert "room k" in card_title(page)
    for i in range(4):
        assert page.locator(f"#hero-text-{i}").is_visible()


def test_pinning_a_plain_corridor_square_says_to_choose_a_room_or_zone(page):
    pin(page, 12, 8)
    pin(page, 0, 0)  # plain corridor
    assert not page.locator("#hero-text-0").is_visible()
    assert "choose" in page.locator("#hero-card").inner_text().lower()


def test_hovering_never_changes_the_card(page):
    pin(page, 12, 8)
    page.mouse.move(*__import__("conftest").cell_center(page, 2, 2))  # hover room A
    assert "room k" in card_title(page)


def test_the_chooser_switches_rooms_without_pinning_a_square(page):
    page.click("#hero-card summary")  # open the collapsed card
    page.click('#hero-chooser button[data-region="13"]')
    assert "room n" in card_title(page)
    assert page.evaluate("QMG.app.pinned") is None


def test_typing_a_text_stores_it_counts_it_and_stops_at_600(page):
    pin(page, 12, 8)
    page.fill("#hero-text-0", "The door grinds open.")
    assert rooms(page)[str(K)]["texts"][0] == "The door grinds open."
    assert "21/600" in page.locator("#hero-card").inner_text()
    page.fill("#hero-text-1", "x" * 700)
    assert len(rooms(page)[str(K)]["texts"][1]) == 600


def test_each_of_the_four_texts_goes_to_its_own_slot(page):
    pin(page, 12, 8)
    for i, text in enumerate(["read", "treasure", "traps", "secret"]):
        page.fill(f"#hero-text-{i}", text)
    assert rooms(page)[str(K)]["texts"] == ["read", "treasure", "traps", "secret"]


def test_revealed_at_the_start_is_a_checkbox_and_an_empty_default_record_is_dropped(page):
    pin(page, 12, 8)
    page.check("#hero-start")
    assert rooms(page)[str(K)]["start"] is True
    page.uncheck("#hero-start")
    assert (
        rooms(page) == {}
    )  # nothing left to say about the room, so no record (and a shorter link)


def test_group_chips_link_rooms_so_they_reveal_together(page):
    pin(page, 12, 8)  # room K
    page.click('#hero-group button[data-region="13"]')  # room N
    groups = page.evaluate("[QMG.app.state.rooms[10].group, QMG.app.state.rooms[13].group]")
    assert groups[0] == groups[1] and groups[0] > 0
    assert page.evaluate("QMG.hero.groupMembers(QMG.app.state, 10)") == [K, N]
    assert (
        page.locator('#hero-group button[data-region="13"]').get_attribute("aria-pressed") == "true"
    )
    page.click('#hero-group button[data-region="13"]')  # unlink again
    assert rooms(page) == {}


def test_a_third_room_joins_the_same_group(page):
    pin(page, 12, 8)
    page.click('#hero-group button[data-region="13"]')
    page.click('#hero-group button[data-region="0"]')
    assert sorted(page.evaluate("QMG.hero.groupMembers(QMG.app.state, 10)")) == [0, K, N]


def test_painted_zones_appear_in_the_chooser_and_get_a_card_like_a_room(page):
    page.click('#tools button[data-kind="zone"][data-value="1"]')
    page.evaluate("window.scrollTo(0, 0)")
    click_cell(page, 3, 0)
    names = page.locator("#hero-chooser button[data-region]").evaluate_all(
        "els => els.map(e => e.textContent.trim())"
    )
    assert "Zone 1" in names
    page.fill('#legend-edit input[data-color="6"]', "North hallway")
    pin(page, 3, 0)
    assert "north hallway" in card_title(page)
    page.fill("#hero-text-0", "A cold hallway.")
    assert rooms(page)[str(Z1)]["texts"][0] == "A cold hallway."


def test_the_card_shows_the_total_room_text_and_updates_the_link(page):
    pin(page, 12, 8)
    page.fill("#hero-text-0", "12345")
    pin(page, 2, 2)
    page.fill("#hero-text-2", "abc")
    assert "8 characters" in page.locator("#hero-total").inner_text()
    page.wait_for_timeout(450)
    decoded = ref.decode(page.evaluate("location.hash").lstrip("#"))
    assert decoded["rooms"][K]["texts"][0] == "12345" and decoded["rooms"][0]["texts"][2] == "abc"


def test_hero_texts_are_undoable_as_one_step_per_pause(page):
    pin(page, 12, 8)
    page.fill("#hero-text-0", "first")
    page.wait_for_timeout(900)  # a pause: one undo step
    page.fill("#hero-text-0", "second")
    page.wait_for_timeout(900)
    page.click("#undo")
    assert rooms(page)[str(K)]["texts"][0] == "first"
    page.click("#undo")
    assert rooms(page) == {}


def test_the_map_marks_regions_that_have_text_and_grouped_ones(page):
    pin(page, 12, 8)
    page.fill("#hero-text-0", "text")
    page.click('#hero-group button[data-region="13"]')
    page.click('#tools button[data-kind="select"]')
    assert page.locator('#layer-overlay .hero-dot[data-region="10"]').count() == 1
    assert page.locator("#layer-overlay .hero-group").count() == 2


def test_a_hero_link_opened_in_the_editor_fills_the_card(page, site):
    st = ref.blank()
    st["rooms"] = {K: {"start": True, "group": 0, "texts": ["Opened", "", "", ""]}}
    open_link(page, site, ref.encode(st))
    pin(page, 12, 8)
    assert page.input_value("#hero-text-0") == "Opened"
    assert page.is_checked("#hero-start")


def test_copy_hero_link_copies_a_link_in_hero_view_with_no_play_state(page, site):
    st = ref.blank()
    st["rooms"] = {K: {"start": True, "group": 0, "texts": ["x", "", "", ""]}}
    st["play"] = {"rev": [0], "t": [], "tr": [], "sd": []}
    open_link(page, site, ref.encode(st))
    page.evaluate(
        "Object.defineProperty(navigator, 'clipboard', { value: { writeText: async (t) => { window.__copied = t; } } })"
    )
    page.click("#copy-hero")
    page.wait_for_function("window.__copied !== undefined")
    copied = page.evaluate("window.__copied")
    decoded = ref.decode(copied.split("#", 1)[1])
    assert decoded["hero"] is True and decoded["play"] is None
    assert decoded["rooms"][K]["texts"][0] == "x"
    assert page.evaluate("QMG.app.state.play !== null")  # the editor's own link is untouched


def test_copy_hero_link_is_not_offered_inside_hero_view(page, site):
    st = ref.blank()
    st["hero"] = True
    open_link(page, site, ref.encode(st))
    page.wait_for_selector("body.hero")
    assert not page.locator("#copy-hero").is_visible()
