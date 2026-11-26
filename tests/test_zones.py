"""Zones: corridor squares painted with highlight values 6-15 that heroes reveal like a room."""

from __future__ import annotations

from conftest import click_cell

ZONE_VALUES = list(range(6, 16))


def paint(page, value, x, y):
    page.click(f'#tools button[data-kind="highlight"][data-value="{value}"]')
    page.evaluate("window.scrollTo(0, 0)")
    click_cell(page, x, y)


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
    values = [int(v) for v in buttons.evaluate_all("els => els.map(e => e.dataset.value)")]
    assert values == ZONE_VALUES + [0]
    assert "Zone 1" in buttons.nth(0).inner_text() and "Clear" in buttons.nth(10).inner_text()


def test_zones_are_not_listed_among_the_ordinary_highlight_colors(page):
    grid = page.locator("#tools h2", has_text="Highlight").first.locator(
        "xpath=following-sibling::div[1]"
    )
    values = grid.locator("button").evaluate_all("els => els.map(e => Number(e.dataset.value))")
    assert values == [0, 2, 3, 4, 5]


def test_painting_a_zone_stores_its_highlight_value_and_clear_erases_it(page):
    paint(page, 6, 3, 9)
    paint(page, 15, 4, 9)
    assert page.evaluate("[QMG.app.state.hl[9 * 26 + 3], QMG.app.state.hl[9 * 26 + 4]]") == [6, 15]
    paint(page, 0, 3, 9)
    assert page.evaluate("QMG.app.state.hl[9 * 26 + 3]") == 0


def test_a_zone_square_is_drawn_in_its_own_color_not_the_neutral_reserved_tint(page):
    paint(page, 6, 3, 9)
    rect = page.locator("#layer-hl rect").first
    assert rect.get_attribute("stroke-dasharray") is None
    assert rect.get_attribute("fill").startswith("#")
    paint(page, 7, 4, 9)
    fills = page.locator("#layer-hl rect").evaluate_all(
        "els => els.map(e => e.getAttribute('fill'))"
    )
    assert len(set(fills)) == 2  # each zone has its own color


def test_whats_here_names_the_zone_and_uses_the_legend_name(page):
    paint(page, 6, 3, 9)
    page.click('#tools button[data-kind="select"]')
    click_cell(page, 3, 9)
    assert "Zone 1" in page.locator("#inspector").inner_text()
    page.fill('#legend-edit input[data-color="6"]', "North hallway")
    page.evaluate("window.scrollTo(0, 0)")
    click_cell(page, 3, 9)
    assert "North hallway" in page.locator("#inspector").inner_text()


def test_the_legend_lists_used_zones_by_default_name_or_legend_name(page):
    assert page.locator("#legend li").count() == 0
    paint(page, 6, 3, 9)
    paint(page, 8, 5, 9)
    assert page.locator("#legend li").all_inner_texts() == ["Zone 1", "Zone 3"]
    page.fill('#legend-edit input[data-color="8"]', "West corridor")
    assert page.locator("#legend li").all_inner_texts() == ["Zone 1", "West corridor"]


def test_the_legend_editor_names_zones(page):
    inputs = page.locator("#legend-edit input[data-color]")
    colors = [int(c) for c in inputs.evaluate_all("els => els.map(e => e.dataset.color)")]
    assert colors == [2, 3, 4, 5] + ZONE_VALUES
    page.fill('#legend-edit input[data-color="10"]', "Long corridor")
    assert page.evaluate("QMG.app.state.legend[10]") == "Long corridor"


def region(page, x, y):
    return page.evaluate("([x, y]) => QMG.hero.regionAt(QMG.app.state, x, y)", [x, y])


def test_regions_are_rooms_by_letter_zones_by_paint_and_nothing_for_plain_corridor(page):
    assert region(page, 1, 1) == 0  # room A
    assert region(page, 10, 8) == 10  # room K
    assert region(page, 0, 0) is None  # corridor, no zone
    paint(page, 6, 0, 0)
    paint(page, 15, 25, 18)
    assert region(page, 0, 0) == 26  # zone 1
    assert region(page, 25, 18) == 35  # zone 10


def test_a_zone_painted_inside_a_room_is_ignored_for_the_region(page):
    paint(page, 6, 10, 8)  # a square of room K
    assert region(page, 10, 8) == 10


def test_region_names(page):
    names = page.evaluate(
        "() => [QMG.hero.regionName(QMG.app.state, 0), QMG.hero.regionName(QMG.app.state, 10),"
        " QMG.hero.regionName(QMG.app.state, 26), QMG.hero.regionName(QMG.app.state, 35)]"
    )
    assert names == ["Room A", "Room K", "Zone 1", "Zone 10"]
    page.fill('#legend-edit input[data-color="6"]', "North hallway")
    assert page.evaluate("QMG.hero.regionName(QMG.app.state, 26)") == "North hallway"


def zone_button_text(page, value):
    return page.locator(
        f'#tools button[data-kind="highlight"][data-value="{value}"]'
    ).first.inner_text()


def test_a_zones_palette_button_shows_its_name_once_it_has_one(page):
    assert zone_button_text(page, 6) == "Zone 1"
    page.fill('#legend-edit input[data-color="6"]', "North hallway")
    assert zone_button_text(page, 6) == "North hallway"
    page.fill('#legend-edit input[data-color="6"]', "")
    assert zone_button_text(page, 6) == "Zone 1"


def test_zone_button_names_follow_a_link_that_names_zones(page, site):
    import reference as ref
    from conftest import open_link

    st = ref.blank()
    st["legend"] = {7: "South hallway"}
    open_link(page, site, ref.encode(st))
    assert zone_button_text(page, 7) == "South hallway"
