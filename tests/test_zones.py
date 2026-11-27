"""Zones: a per-square layer of corridor areas that heroes reveal like a room (docs/HERO_VIEW.md)."""

from __future__ import annotations

import base64

import pytest
import reference as ref
from conftest import click_cell, open_link

ZONES = list(range(1, 11))


@pytest.fixture(autouse=True)
def quick(page):
    page.set_default_timeout(4000)


def paint_zone(page, n, x, y):
    page.click(f'#tools button[data-kind="zone"][data-value="{n}"]')
    page.evaluate("window.scrollTo(0, 0)")
    click_cell(page, x, y)


def paint_highlight(page, value, x, y):
    page.click(f'#tools button[data-kind="highlight"][data-value="{value}"]')
    page.evaluate("window.scrollTo(0, 0)")
    click_cell(page, x, y)


def square(page, x, y):
    return page.evaluate(
        "([x, y]) => [QMG.app.state.hl[y * 26 + x], QMG.app.state.zones[y * 26 + x]]", [x, y]
    )


def headings(page):
    return [h.lower() for h in page.locator("#tools h2").all_inner_texts()]


def test_the_palette_has_a_hero_view_zones_section_with_ten_zones_and_a_clear(page):
    names = headings(page)
    assert names.index("hero view zones") == names.index("solid stone areas") + 1
    assert names.index("doors & walls") == names.index("hero view zones") + 1
    grid = page.locator("#tools h2", has_text="Hero view zones").locator(
        "xpath=following-sibling::div[1]"
    )
    buttons = grid.locator("button")
    assert buttons.count() == 11  # zones 1-10 and Clear
    kinds = buttons.evaluate_all("els => els.map(e => e.dataset.kind)")
    values = [int(v) for v in buttons.evaluate_all("els => els.map(e => e.dataset.value)")]
    assert kinds == ["zone"] * 11 and values == ZONES + [0]
    assert "Zone 1" in buttons.nth(0).inner_text() and "Clear" in buttons.nth(10).inner_text()


def test_zones_are_not_listed_among_the_ordinary_highlight_colors(page):
    grid = page.locator("#tools h2", has_text="Highlight").first.locator(
        "xpath=following-sibling::div[1]"
    )
    values = grid.locator("button").evaluate_all("els => els.map(e => Number(e.dataset.value))")
    assert values == [0, 2, 3, 4, 5]


def test_painting_a_zone_stores_it_in_the_zone_layer_and_clear_erases_it(page):
    paint_zone(page, 1, 3, 9)
    paint_zone(page, 10, 4, 9)
    assert square(page, 3, 9) == [0, 1] and square(page, 4, 9) == [0, 10]
    paint_zone(page, 0, 3, 9)
    assert square(page, 3, 9) == [0, 0]


def test_a_square_can_be_stone_or_a_trap_and_in_a_zone_at_once(page):
    paint_highlight(page, 1, 5, 9)  # solid stone
    paint_highlight(page, 2, 6, 9)  # a trap highlight
    paint_zone(page, 2, 5, 9)
    paint_zone(page, 3, 6, 9)
    assert square(page, 5, 9) == [1, 2] and square(page, 6, 9) == [2, 3]
    paint_highlight(page, 0, 5, 9)  # clearing the highlight leaves the zone alone
    assert square(page, 5, 9) == [0, 2]


def test_zones_are_undoable(page):
    paint_zone(page, 1, 3, 9)
    page.click("#undo")
    assert square(page, 3, 9) == [0, 0]
    page.click("#redo")
    assert square(page, 3, 9) == [0, 1]


def test_a_zone_square_is_drawn_in_its_own_color_in_the_zone_layer(page):
    paint_zone(page, 1, 3, 9)
    paint_zone(page, 2, 4, 9)
    fills = page.locator("#layer-zones rect").evaluate_all(
        "els => els.map(e => e.getAttribute('fill'))"
    )
    assert len(fills) == 2 and len(set(fills)) == 2 and all(f.startswith("#") for f in fills)


def test_whats_here_names_the_zone_and_uses_the_legend_name(page):
    paint_zone(page, 1, 3, 9)
    page.click('#tools button[data-kind="select"]')
    click_cell(page, 3, 9)
    assert "Zone: Zone 1" in page.locator("#inspector").inner_text()
    page.fill('#legend-edit input[data-color="6"]', "North hallway")
    page.evaluate("window.scrollTo(0, 0)")
    click_cell(page, 3, 9)
    assert "Zone: North hallway" in page.locator("#inspector").inner_text()


def test_the_legend_lists_used_zones_by_default_name_or_legend_name(page):
    assert page.locator("#legend li").count() == 0
    paint_zone(page, 1, 3, 9)
    paint_zone(page, 3, 5, 9)
    assert page.locator("#legend li").all_inner_texts() == ["Zone 1", "Zone 3"]
    page.fill('#legend-edit input[data-color="8"]', "West corridor")
    assert page.locator("#legend li").all_inner_texts() == ["Zone 1", "West corridor"]
    paint_highlight(page, 1, 7, 9)
    assert page.locator("#legend li").all_inner_texts() == [
        "Solid stone",
        "Zone 1",
        "West corridor",
    ]


def test_the_legend_editor_names_zones(page):
    inputs = page.locator("#legend-edit input[data-color]")
    colors = [int(c) for c in inputs.evaluate_all("els => els.map(e => e.dataset.color)")]
    assert colors == [2, 3, 4, 5] + list(range(6, 16))  # zone n is named by legend entry 5 + n
    page.fill('#legend-edit input[data-color="10"]', "Long corridor")
    assert page.evaluate("QMG.app.state.legend[10]") == "Long corridor"


def region(page, x, y):
    return page.evaluate("([x, y]) => QMG.hero.regionAt(QMG.app.state, x, y)", [x, y])


def test_regions_are_rooms_by_letter_zones_by_paint_and_nothing_for_plain_corridor(page):
    assert region(page, 1, 1) == 0  # room A
    assert region(page, 10, 8) == 10  # room K
    assert region(page, 0, 0) is None  # corridor, no zone
    paint_zone(page, 1, 0, 0)
    paint_zone(page, 10, 25, 18)
    assert region(page, 0, 0) == 26  # zone 1
    assert region(page, 25, 18) == 35  # zone 10


def test_a_zone_painted_inside_a_room_is_ignored_for_the_region(page):
    paint_zone(page, 1, 10, 8)  # a square of room K
    assert region(page, 10, 8) == 10


def test_region_names(page):
    names = page.evaluate(
        "() => [QMG.hero.regionName(QMG.app.state, 0), QMG.hero.regionName(QMG.app.state, 10),"
        " QMG.hero.regionName(QMG.app.state, 26), QMG.hero.regionName(QMG.app.state, 35)]"
    )
    assert names == ["Room A", "Room K", "Zone 1", "Zone 10"]
    page.fill('#legend-edit input[data-color="6"]', "North hallway")
    assert page.evaluate("QMG.hero.regionName(QMG.app.state, 26)") == "North hallway"


def zone_button_text(page, n):
    return page.locator(f'#tools button[data-kind="zone"][data-value="{n}"]').first.inner_text()


def test_a_zones_palette_button_shows_its_name_once_it_has_one(page):
    assert zone_button_text(page, 1) == "Zone 1"
    page.fill('#legend-edit input[data-color="6"]', "North hallway")
    assert zone_button_text(page, 1) == "North hallway"
    page.fill('#legend-edit input[data-color="6"]', "")
    assert zone_button_text(page, 1) == "Zone 1"


def test_zone_button_names_follow_a_link_that_names_zones(page, site):
    st = ref.blank()
    st["legend"] = {7: "South hallway"}
    open_link(page, site, ref.encode(st))
    assert zone_button_text(page, 2) == "South hallway"


def test_zones_survive_the_link(page, site):
    paint_zone(page, 4, 3, 9)
    page.wait_for_timeout(450)
    payload = page.evaluate("location.hash").lstrip("#")
    assert ref.decode(payload)["zones"][9 * 26 + 3] == 4
    open_link(page, site, payload)
    assert square(page, 3, 9) == [0, 4]


# ---------------------------------------------------------------- adding and removing zones (10 to 30)
def zone_values(page):
    values = page.locator('#tools button[data-kind="zone"]').evaluate_all(
        "els => els.map(e => Number(e.dataset.value))"
    )
    return [v for v in values if v]


def legend_zone_inputs(page):
    return page.locator("#legend-edit input").evaluate_all(
        "els => els.map(e => Number(e.dataset.color)).filter((k) => k >= 6)"
    )


def confirm(page):
    page.wait_for_selector("#confirm-dialog[open]")
    page.click("#confirm-ok")
    page.wait_for_selector("#confirm-dialog:not([open])", state="attached")


def test_a_new_quest_has_ten_zones_and_can_add_but_not_remove(page):
    assert zone_values(page) == ZONES
    assert page.locator("#add-zone").is_enabled()
    assert page.locator("#remove-zone").is_disabled()
    assert legend_zone_inputs(page) == list(range(6, 16))


def test_add_zone_adds_the_next_zone_to_the_palette_and_the_legend_up_to_thirty(page):
    page.click("#add-zone")
    assert zone_values(page) == list(range(1, 12))
    assert (
        "Zone 11" in page.locator('#tools button[data-kind="zone"][data-value="11"]').inner_text()
    )
    assert legend_zone_inputs(page)[-1] == 16
    for _ in range(19):
        page.click("#add-zone")
    assert zone_values(page) == list(range(1, 31))
    assert legend_zone_inputs(page)[-1] == 35
    assert page.locator("#add-zone").is_disabled()


def test_every_zone_has_its_own_color(page):
    for _ in range(20):
        page.click("#add-zone")
    colors = page.locator('#tools button[data-kind="zone"] .swatch').evaluate_all(
        "els => els.map(e => e.style.background)"
    )
    colors = [c for c in colors if c != "transparent"]
    assert len(colors) == 30 and len(set(colors)) == 30


def test_an_added_zone_can_be_painted_and_is_stored_in_a_version_two_link(page):
    page.click("#add-zone")
    paint_zone(page, 11, 3, 9)
    assert square(page, 3, 9) == [0, 11]
    page.evaluate("QMG.syncUrl()")
    page.wait_for_timeout(100)
    payload = page.evaluate("location.hash").lstrip("#")
    data = base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4))
    assert data[0] == 2
    assert ref.decode(payload)["zones"][9 * 26 + 3] == 11


def test_a_link_with_a_zone_above_ten_opens_with_that_many_zones(page, site):
    st = ref.blank()
    st["zones"][100] = 17
    open_link(page, site, ref.encode(st))
    assert zone_values(page) == list(range(1, 18))


def test_an_added_zone_that_is_never_used_is_not_kept_in_the_link(page, site):
    page.click("#add-zone")
    page.click("#add-zone")
    page.evaluate("QMG.syncUrl()")
    page.reload()
    page.wait_for_function("window.QMG !== undefined")
    assert zone_values(page) == ZONES


def test_remove_zone_drops_an_unused_last_zone_without_asking(page):
    page.click("#add-zone")
    page.click("#add-zone")
    page.click("#remove-zone")
    assert zone_values(page) == list(range(1, 12))
    page.click("#remove-zone")
    assert zone_values(page) == ZONES
    assert page.locator("#remove-zone").is_disabled()
    assert not page.locator("#confirm-dialog").is_visible()


def used_zone_twelve(page):
    for _ in range(2):
        page.click("#add-zone")
    paint_zone(page, 12, 3, 9)
    paint_zone(page, 12, 4, 9)
    page.fill('#legend-edit input[data-color="17"]', "The long hall")
    page.evaluate(
        "QMG.app.state.rooms[37] = { start: false, group: 0, texts: ['read', '', '', ''] }"
    )


def test_removing_a_used_zone_asks_then_clears_its_squares_name_and_record(page):
    used_zone_twelve(page)
    page.click("#remove-zone")
    page.wait_for_selector("#confirm-dialog[open]")
    assert "Zone 12" in page.locator("#confirm-message").inner_text()
    assert "2 squares" in page.locator("#confirm-message").inner_text()
    page.click("#confirm-ok")
    page.wait_for_selector("#confirm-dialog:not([open])", state="attached")
    assert zone_values(page) == list(range(1, 12))
    assert square(page, 3, 9) == [0, 0] and square(page, 4, 9) == [0, 0]
    assert page.evaluate("QMG.app.state.legend[17]") in (None, "")
    assert page.evaluate("37 in QMG.app.state.rooms") is False


def test_cancelling_the_removal_of_a_used_zone_keeps_everything(page):
    used_zone_twelve(page)
    page.click("#remove-zone")
    page.wait_for_selector("#confirm-dialog[open]")
    page.click("#confirm-cancel")
    page.wait_for_selector("#confirm-dialog:not([open])", state="attached")
    assert zone_values(page) == list(range(1, 13))
    assert square(page, 3, 9) == [0, 12]


def test_removing_a_used_zone_is_one_undo_step(page):
    used_zone_twelve(page)
    page.wait_for_timeout(800)  # the typed name settles into its own history step
    page.click("#remove-zone")
    confirm(page)
    page.keyboard.press("Control+z")
    assert square(page, 3, 9) == [0, 12]
    assert zone_values(page) == list(range(1, 13))


def test_removing_the_zone_that_is_the_current_tool_returns_to_select(page):
    page.click("#add-zone")
    page.click('#tools button[data-kind="zone"][data-value="11"]')
    page.click("#remove-zone")
    assert page.evaluate("QMG.app.tool.kind") == "select"
