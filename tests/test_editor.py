"""End-to-end editor behavior in the built page."""

from __future__ import annotations

import io

import reference as ref
from conftest import (
    cell_center,
    click_cell,
    items,
    open_link,
    pick_piece,
    piece_id,
    settle,
)
from PIL import Image


def state(page, expr):
    return page.evaluate(f"QMG.app.state.{expr}")


def place(page, slug, x, y):
    pick_piece(page, slug)
    click_cell(page, x, y)


def test_placing_pieces_appends_them_on_top(page):
    place(page, "goblin", 5, 5)
    place(page, "orc", 5, 5)
    got = items(page)
    assert [i["id"] for i in got] == [piece_id(page, "goblin"), piece_id(page, "orc")]


def test_exact_duplicates_are_refused(page):
    place(page, "goblin", 5, 5)
    click_cell(page, 5, 5)
    assert len(items(page)) == 1


def test_multi_square_pieces_cover_their_whole_footprint_and_clamp_to_the_board(page):
    place(page, "table", 25, 18)  # 3x2 anchored off the board edge
    got = items(page)[0]
    assert (got["x"], got["y"]) == (23, 17)


def test_rotation_with_r_while_placing_and_when_selected(page):
    pick_piece(page, "table")
    page.keyboard.press("r")
    click_cell(page, 10, 10)
    assert items(page)[0]["r"] == 1
    page.click('#tools button[data-kind="select"]')
    click_cell(page, 10, 10)
    page.keyboard.press("r")
    assert items(page)[0]["r"] == 2


def test_door_tool_picks_the_nearest_edge(page):
    pick_piece(page, "door")
    click_cell(page, 4, 4, fy=0.05)
    click_cell(page, 6, 4, fx=0.95)
    click_cell(page, 8, 4, fy=0.95)
    click_cell(page, 10, 4, fx=0.05)
    assert [i["r"] for i in items(page)] == [0, 1, 2, 3]


def test_doors_may_sit_on_the_outer_edge(page):
    pick_piece(page, "door")
    click_cell(page, 0, 0, fy=0.05)
    assert items(page) == [{"id": piece_id(page, "door"), "x": 0, "y": 0, "r": 0}]


def test_drag_to_move_keeps_rotation_and_position_in_the_stack(page):
    place(page, "table", 5, 5)
    place(page, "goblin", 12, 12)
    page.click('#tools button[data-kind="select"]')
    x1, y1 = cell_center(page, 6, 5)
    x2, y2 = cell_center(page, 10, 8)
    page.mouse.move(x1, y1)
    page.mouse.down()
    page.mouse.move(x2, y2, steps=5)
    page.mouse.up()
    got = items(page)
    assert got[0]["id"] == piece_id(page, "table")  # still first in the list
    assert (got[0]["x"], got[0]["y"]) == (9, 8)  # grabbed at offset (1, 0)


def test_arrow_keys_nudge_the_selected_piece(page):
    place(page, "goblin", 5, 5)
    page.click('#tools button[data-kind="select"]')
    click_cell(page, 5, 5)
    page.keyboard.press("ArrowRight")
    page.keyboard.press("ArrowDown")
    assert (items(page)[0]["x"], items(page)[0]["y"]) == (6, 6)


def test_delete_removes_the_selected_piece(page):
    place(page, "goblin", 5, 5)
    page.click('#tools button[data-kind="select"]')
    click_cell(page, 5, 5)
    page.keyboard.press("Delete")
    assert items(page) == []


def test_eraser_removes_the_top_piece(page):
    place(page, "goblin", 5, 5)
    place(page, "orc", 5, 5)
    page.click('#tools button[data-kind="erase"]')
    click_cell(page, 5, 5)
    assert [i["id"] for i in items(page)] == [piece_id(page, "goblin")]


def test_clicking_a_stacked_square_again_cycles_down_the_stack(page):
    place(page, "goblin", 5, 5)
    place(page, "orc", 5, 5)
    page.click('#tools button[data-kind="select"]')
    click_cell(page, 5, 5)
    assert state(page, "items") is not None
    first = page.evaluate("QMG.app.selected")
    click_cell(page, 5, 5)
    second = page.evaluate("QMG.app.selected")
    assert first != second


def pin(page, x, y):
    page.evaluate("window.scrollTo(0, 0)")
    click_cell(page, x, y)


def test_the_whats_here_panel_names_the_room_of_the_pinned_square(page):
    pin(page, 2, 2)  # inside room A (x 1-4, y 1-3)
    text = page.locator("#inspector").inner_text()
    assert "Room: A" in text
    pin(page, 11, 8)  # inside room K (x 10-15, y 7-12)
    assert "Room: K" in page.locator("#inspector").inner_text()


def test_the_whats_here_panel_names_no_room_for_a_corridor_square(page):
    pin(page, 0, 0)
    assert "Room" not in page.locator("#inspector").inner_text().replace("Room tiles", "")


def test_inspector_lists_the_stack_top_first_and_can_reorder(page):
    place(page, "goblin", 5, 5)
    place(page, "orc", 5, 5)
    box = cell_center(page, 5, 5)
    page.mouse.move(*box)
    names = page.locator("#inspector .stack .name").all_inner_texts()
    assert names == ["Orc", "Goblin"]
    assert "Square F6" in page.locator("#inspector").inner_text()
    page.locator("#inspector .stack li").first.get_by_role("button", name="Back").click()
    assert [i["id"] for i in items(page)] == [piece_id(page, "orc"), piece_id(page, "goblin")]


def test_inspector_buttons_move_rotate_and_remove(page):
    place(page, "stairs", 5, 5)
    page.click('#tools button[data-kind="select"]')
    click_cell(page, 5, 5)
    li = page.locator("#inspector .stack li").first
    li.get_by_role("button", name="←").click()
    assert items(page)[0]["x"] == 4
    li.get_by_role("button", name="Remove").click()
    assert items(page) == []


def test_highlight_painting_by_dragging(page):
    page.click('#tools button[data-kind="highlight"][data-value="2"]')
    x1, y1 = cell_center(page, 3, 3)
    x2, y2 = cell_center(page, 6, 3)
    page.mouse.move(x1, y1)
    page.mouse.down()
    page.mouse.move(x2, y2, steps=8)
    page.mouse.up()
    hl = page.evaluate("Array.from(QMG.app.state.hl)")
    assert [hl[3 * 26 + x] for x in range(3, 7)] == [2, 2, 2, 2]
    page.click('#tools button[data-kind="highlight"][data-value="0"]')
    click_cell(page, 3, 3)
    assert page.evaluate("QMG.app.state.hl[3 * 26 + 3]") == 0


def paint(page, value, x, y):
    page.click(f'#tools button[data-kind="highlight"][data-value="{value}"]')
    page.evaluate("window.scrollTo(0, 0)")
    click_cell(page, x, y)


def test_legend_lists_only_used_colors_with_fixed_grey_and_default_orange(page):
    assert page.locator("#legend li").count() == 0
    paint(page, 1, 3, 3)
    paint(page, 2, 4, 3)
    assert page.locator("#legend li").all_inner_texts() == ["Solid stone", "Trap"]


def test_grey_has_no_editable_legend_but_the_others_do(page):
    assert page.locator('#legend-edit input[data-color="1"]').count() == 0
    assert page.locator("#legend-edit input").count() == 4 + 10  # the four colors and the ten zones
    page.fill('#legend-edit input[data-color="3"]', "secret room")
    assert page.locator("#legend li").count() == 0  # cyan is not used yet
    paint(page, 3, 5, 5)
    assert "secret room" in page.locator("#legend").inner_text()
    page.fill('#legend-edit input[data-color="2"]', "pit or spear trap")
    paint(page, 2, 6, 5)
    assert "pit or spear trap" in page.locator("#legend").inner_text()
    settle(page)


def test_undo_redo_buttons_and_shortcuts(page):
    place(page, "goblin", 5, 5)
    place(page, "orc", 6, 5)
    assert len(items(page)) == 2
    page.click("#undo")
    assert len(items(page)) == 1
    page.click("#redo")
    assert len(items(page)) == 2
    page.keyboard.press("Control+z")
    assert len(items(page)) == 1
    page.keyboard.press("Control+y")
    assert len(items(page)) == 2
    assert page.locator("#redo").is_disabled()


def test_typing_is_one_undo_step_per_pause(page):
    page.fill("#qtitle", "Hello")
    page.wait_for_timeout(900)
    page.fill("#qtitle", "Hello world")
    page.wait_for_timeout(900)
    page.click("#undo")
    assert state(page, "title") == "Hello"
    assert page.input_value("#qtitle") == "Hello"


def test_browser_back_and_forward_step_through_edits(page):
    place(page, "goblin", 5, 5)
    settle(page)
    place(page, "orc", 6, 5)
    settle(page)
    page.go_back()
    page.wait_for_timeout(300)
    assert len(items(page)) == 1
    page.go_forward()
    page.wait_for_timeout(300)
    assert len(items(page)) == 2


def test_quest_text_fields_store_filtered_text_in_the_link(page, site):
    page.fill("#qnum", "12345678901234")
    page.fill("#qtitle", "The <Vault> of % Doom")
    page.fill("#qintro", "Hello **heroes**")
    page.fill("#notes", "# Secret\n- one")
    page.select_option("#wm-select", label="Orc")
    page.fill("#wm-text", "and a goblin")
    page.wait_for_timeout(500)
    settle(page)
    assert state(page, "num") == "1234567890"
    assert state(page, "title") == "The Vault of  Doom"
    payload = page.evaluate("location.hash").lstrip("#")
    open_link(page, site, payload)
    assert page.input_value("#qtitle") == "The Vault of  Doom"
    assert page.input_value("#notes") == "# Secret\n- one"
    assert page.locator("#wm-select").evaluate("e => e.selectedOptions[0].textContent") == "Orc"
    assert page.input_value("#wm-text") == "and a goblin"
    assert page.locator("#sheet-notes h3").inner_text() == "Secret"
    assert "Quest 1234567890: The Vault of Doom" in page.title()


def test_theme_is_stored_in_the_link_and_printing_is_always_light(page, site):
    page.select_option("#theme", label="Dark")
    settle(page)
    assert page.evaluate("document.documentElement.dataset.theme") == "dark"
    dark_bg = page.evaluate("getComputedStyle(document.body).backgroundColor")
    payload = page.evaluate("location.hash").lstrip("#")
    open_link(page, site, payload)
    assert page.evaluate("document.documentElement.dataset.theme") == "dark"
    assert page.evaluate("getComputedStyle(document.body).backgroundColor") == dark_bg
    page.emulate_media(media="print")
    assert page.evaluate("getComputedStyle(document.body).backgroundColor") == "rgb(255, 255, 255)"
    assert page.locator("#topbar").is_hidden()
    assert page.locator("#tools").is_hidden()


def test_theme_change_is_not_an_undo_step(page):
    page.select_option("#theme", label="Dark")
    assert page.locator("#undo").is_disabled()


def test_new_map_clears_everything_but_can_be_undone(page):
    place(page, "goblin", 5, 5)
    page.once("dialog", lambda d: d.accept())
    page.click("#clear")
    assert items(page) == []
    page.click("#undo")
    assert len(items(page)) == 1


def test_long_links_show_a_warning_but_do_not_block(page):
    import random

    random.seed(1)
    text = " ".join(
        "".join(random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(6)) for _ in range(1200)
    )
    page.fill("#notes", text[:9000])
    page.wait_for_timeout(500)
    settle(page)
    assert "warn" in page.locator("#linkinfo").get_attribute("class")
    assert "cut links" in page.locator("#linkinfo").inner_text()
    assert page.locator("#copy").is_enabled()


def test_print_sheet_has_title_wandering_monster_intro_and_notes(page):
    page.fill("#qnum", "3")
    page.fill("#qtitle", "The Vault")
    page.select_option("#wm-select", label="Orc")
    page.fill("#qintro", "Hello **heroes**")
    page.fill("#notes", "- secret")
    assert page.locator("#print-title").inner_text() == "Quest 3: The Vault"
    assert page.locator("#print-wm").inner_text() == "Wandering monster: Orc"
    assert page.locator("#print-intro strong").inner_text() == "heroes"
    assert page.locator("#print-notes li").inner_text() == "secret"


def test_no_wandering_monster_when_both_blank(page):
    assert page.locator("#print-wm").inner_text() == ""


def test_unsupported_browsers_get_a_message_with_minimum_versions(browser, site):
    ctx = browser.new_context()
    pg = ctx.new_page()
    pg.add_init_script("delete window.CompressionStream; delete window.DecompressionStream;")
    pg.goto(site)
    pg.wait_for_function("window.QMG !== undefined")
    box = pg.locator("#unsupported")
    assert box.is_visible()
    assert "Chrome 103" in box.inner_text() and "Safari 16.4" in box.inner_text()
    assert pg.locator("#app").is_hidden()
    ctx.close()


def test_footer_carries_the_notice_and_license(page):
    text = page.locator("#footer").inner_text()
    assert "Unofficial" in text and "Hasbro" in text and "MIT License" in text


def test_every_catalog_piece_has_a_palette_button_and_a_rendered_sprite(page):
    count = page.evaluate("QMG.CATALOG.length")
    tiles = page.evaluate("QMG.CATALOG.filter((c) => c.tile).length")
    assert page.locator('#tools button[data-kind="piece"]').count() == count - tiles
    assert page.locator('#tools button[data-kind="tile"]').count() == tiles
    assert page.locator('#sprites symbol[id^="icon-"]').count() == count


def test_all_pieces_render_on_the_board(page):
    page.evaluate(
        """() => { QMG.CATALOG.forEach((c, i) => QMG.app.state.items.push({ id: c.id, x: i % 20, y: Math.floor(i / 20) * 4, r: 0 })); }"""
    )
    open_state = page.evaluate("QMG.CATALOG.length")
    page.keyboard.press("Escape")
    page.click('#tools button[data-kind="erase"]')
    page.click('#tools button[data-kind="select"]')
    assert open_state > 30


def tiles(page):
    return page.evaluate("QMG.app.state.tiles.map((t) => ({...t}))")


def pick_tile(page):
    page.click('#tools button[data-kind="tile"]')
    page.evaluate("window.scrollTo(0, 0)")


def drag_cells(page, x1, y1, x2, y2):
    a = cell_center(page, x1, y1)
    b = cell_center(page, x2, y2)
    page.mouse.move(*a)
    page.mouse.down()
    page.mouse.move(*b, steps=6)
    page.mouse.up()


def test_dragging_with_the_tile_tool_draws_a_rectangle_of_that_size(page):
    pick_tile(page)
    drag_cells(page, 6, 4, 3, 7)  # drag up and to the left: still a 4x4 rectangle
    got = tiles(page)
    assert len(got) == 1
    assert (got[0]["x"], got[0]["y"], got[0]["w"], got[0]["h"]) == (3, 4, 4, 4)
    assert page.locator("#layer-tiles use").count() == 16


def test_a_plain_click_with_the_tile_tool_makes_a_1x1_tile(page):
    pick_tile(page)
    click_cell(page, 9, 9)
    assert [(t["w"], t["h"]) for t in tiles(page)] == [(1, 1)]


def test_tiles_are_drawn_below_pieces_even_when_placed_later(page):
    place(page, "goblin", 5, 5)
    pick_tile(page)
    drag_cells(page, 4, 4, 7, 7)
    html = page.evaluate("document.querySelector('#board').innerHTML")
    assert html.index('id="layer-tiles"') < html.index('id="layer-items"')
    assert [i["id"] for i in items(page)] == [piece_id(page, "goblin")]  # piece list untouched


def test_the_inspector_lists_pieces_then_tiles_and_resizes_a_tile(page):
    pick_tile(page)
    drag_cells(page, 4, 4, 5, 5)
    page.click('#tools button[data-kind="select"]')
    click_cell(page, 4, 4)
    panel = page.locator("#inspector")
    assert "room tiles (under the pieces)" in panel.inner_text().lower()
    panel.get_by_label("Width").fill("5")
    panel.get_by_label("Width").dispatch_event("change")
    panel.get_by_label("Height").fill("3")
    panel.get_by_label("Height").dispatch_event("change")
    assert [(t["w"], t["h"]) for t in tiles(page)] == [(5, 3)]


def test_resizing_is_limited_to_the_board(page):
    pick_tile(page)
    click_cell(page, 24, 17)
    page.click('#tools button[data-kind="select"]')
    click_cell(page, 24, 17)
    box = page.locator("#inspector")
    box.get_by_label("Width").fill("9")
    box.get_by_label("Width").dispatch_event("change")
    assert tiles(page)[0]["w"] == 2  # only two columns remain from x=24


def test_selecting_moving_and_deleting_a_tile(page):
    pick_tile(page)
    drag_cells(page, 4, 4, 5, 5)
    page.click('#tools button[data-kind="select"]')
    a = cell_center(page, 4, 4)
    b = cell_center(page, 8, 7)
    page.mouse.move(*a)
    page.mouse.down()
    page.mouse.move(*b, steps=5)
    page.mouse.up()
    assert (tiles(page)[0]["x"], tiles(page)[0]["y"]) == (8, 7)
    page.keyboard.press("ArrowLeft")
    assert tiles(page)[0]["x"] == 7
    page.keyboard.press("Delete")
    assert tiles(page) == []


def test_the_eraser_removes_a_tile_only_when_no_piece_is_there(page):
    place(page, "goblin", 5, 5)
    pick_tile(page)
    drag_cells(page, 4, 4, 6, 6)
    page.click('#tools button[data-kind="erase"]')
    click_cell(page, 5, 5)
    assert items(page) == [] and len(tiles(page)) == 1
    click_cell(page, 5, 5)
    assert tiles(page) == []


def test_tiles_are_in_the_link_and_in_undo_history(page, site):
    pick_tile(page)
    drag_cells(page, 4, 4, 6, 5)
    settle(page)
    payload = page.evaluate("location.hash").lstrip("#")
    import reference as ref

    assert ref.decode(payload)["tiles"] == [(100, 4, 4, 3, 2)]
    open_link(page, site, payload)
    assert [(t["w"], t["h"]) for t in tiles(page)] == [(3, 2)]
    page.click('#tools button[data-kind="tile"]')
    click_cell(page, 12, 12)
    assert len(tiles(page)) == 2
    page.click("#undo")
    assert len(tiles(page)) == 1


def test_tiles_do_not_change_the_statistics(page):
    pick_tile(page)
    drag_cells(page, 1, 1, 12, 8)  # covers several printed rooms
    text = page.locator("#stats").inner_text()
    assert "Monsters\n0" in text and "(22)" in text  # still all 22 printed rooms


def test_the_quest_sheet_sits_below_the_legend_and_starts_with_a_hint(page):
    order = page.evaluate(
        "[...document.querySelector('#stage').children].map((e) => e.id || e.className)"
    )
    assert order.index("legend") + 1 == order.index("quest-sheet")
    assert page.locator("#sheet-empty").is_visible()
    assert page.locator("#sheet-intro-section").is_hidden()
    assert page.locator("#sheet-notes-section").is_hidden()


def test_the_quest_sheet_updates_on_every_keystroke(page):
    page.locator("#qtitle").press_sequentially("Crypt", delay=20)
    assert page.locator("#sheet-title").inner_text() == "Crypt"
    page.fill("#qnum", "7")
    assert page.locator("#sheet-title").inner_text() == "Quest 7: Crypt"
    page.locator("#qintro").press_sequentially("Hello **bold", delay=10)
    assert page.locator("#sheet-intro").inner_text() == "Hello **bold"  # not closed yet: literal
    page.locator("#qintro").press_sequentially("** world", delay=10)
    assert page.locator("#sheet-intro strong").inner_text() == "bold"
    assert page.locator("#sheet-empty").is_hidden()


def test_the_quest_sheet_renders_notes_and_the_wandering_monster(page):
    page.fill("#notes", "# Secrets\n- one\n- two\n\n| A | B |\n|---|---|\n| 1 | 2 |")
    assert page.locator("#sheet-notes h3").inner_text() == "Secrets"
    assert page.locator("#sheet-notes li").count() == 2
    assert page.locator("#sheet-notes td").count() == 2
    assert "secret" in page.locator("#sheet-notes-section summary").inner_text().lower()
    page.select_option("#wm-select", label="Orc")
    assert page.locator("#sheet-wm").inner_text() == "Wandering monster: Orc"
    page.fill("#wm-text", "and a rat")
    assert page.locator("#sheet-wm").inner_text() == "Wandering monster: Orc \u2013 and a rat"
    page.select_option("#wm-select", label="(none)")
    page.fill("#wm-text", "")
    assert page.locator("#sheet-wm").is_hidden()


def test_the_quest_sheet_is_not_printed_but_the_print_sheet_is(page):
    page.fill("#qtitle", "Crypt")
    page.emulate_media(media="print")
    assert page.locator("#quest-sheet").is_hidden()
    assert page.locator("#print-title").inner_text() == "Crypt"


def test_a_new_piece_starts_unrotated_even_after_rotating_a_different_one(page):
    pick_piece(page, "table")
    page.keyboard.press("r")
    click_cell(page, 10, 10)
    assert items(page)[0]["r"] == 1  # the table was placed turned
    pick_piece(page, "goblin")
    click_cell(page, 3, 3)
    assert [i["r"] for i in items(page)] == [1, 0]  # the goblin starts upright


def test_picking_the_same_piece_again_keeps_its_rotation(page):
    pick_piece(page, "table")
    page.keyboard.press("r")
    pick_piece(page, "table")
    click_cell(page, 10, 10)
    assert items(page)[0]["r"] == 1


def test_the_secret_door_tile_rotates_like_a_piece_while_the_hidden_door_snaps_to_an_edge(page):
    pick_piece(page, "secret-door")
    page.keyboard.press("r")
    page.keyboard.press("r")
    click_cell(page, 6, 6, fy=0.05)  # near the north edge: a secret door tile ignores that
    pick_piece(page, "hidden-door")
    click_cell(page, 8, 6, fx=0.95)  # near the east edge: a hidden door snaps to it
    got = items(page)
    assert (got[0]["id"], got[0]["r"]) == (piece_id(page, "secret-door"), 2)
    assert (got[1]["id"], got[1]["r"]) == (piece_id(page, "hidden-door"), 1)


def test_the_series_shows_above_the_title_on_the_sheet_print_page_and_tab(page, site):
    assert page.locator("#sheet-series").is_hidden()
    page.fill("#series", "The Order of the Oth")
    page.fill("#qtitle", "The Stone Tablets")
    assert page.locator("#sheet-series").inner_text().lower() == "the order of the oth"
    order = page.evaluate(
        "[...document.querySelector('#quest-sheet').children].map((e) => e.id).slice(0, 2)"
    )
    assert order == ["sheet-series", "sheet-title"]
    assert page.locator("#print-series").inner_text() == "The Order of the Oth"
    assert page.title().startswith("The Order of the Oth: The Stone Tablets")
    page.wait_for_timeout(500)
    settle(page)
    payload = page.evaluate("location.hash").lstrip("#")
    open_link(page, site, payload)
    assert page.input_value("#series") == "The Order of the Oth"


def test_clearing_the_series_hides_it_again(page):
    page.fill("#series", "A series")
    page.fill("#series", "")
    assert page.locator("#sheet-series").is_hidden() and page.locator("#print-series").is_hidden()


def active_tool(page):
    return page.evaluate("QMG.app.tool.kind")


def test_escape_returns_from_a_placement_tool_to_the_select_tool(page):
    pick_piece(page, "goblin")
    assert active_tool(page) == "piece"
    page.keyboard.press("Escape")
    assert active_tool(page) == "select"
    assert page.locator('#tools button[data-kind="select"]').get_attribute("aria-pressed") == "true"
    click_cell(page, 5, 5)  # no longer places anything
    assert items(page) == []


def test_escape_leaves_the_highlight_and_tile_tools_too(page):
    page.click('#tools button[data-kind="highlight"][data-value="2"]')
    page.keyboard.press("Escape")
    assert active_tool(page) == "select"
    pick_tile(page)
    page.keyboard.press("Escape")
    assert active_tool(page) == "select"


def test_escape_cancels_a_tile_that_is_being_dragged_out(page):
    pick_tile(page)
    a = cell_center(page, 4, 4)
    b = cell_center(page, 8, 7)
    page.mouse.move(*a)
    page.mouse.down()
    page.mouse.move(*b, steps=4)
    page.keyboard.press("Escape")
    page.mouse.up()
    assert tiles(page) == [] and active_tool(page) == "select"


def test_the_deselect_button_does_what_escape_does_without_a_keyboard(page):
    place(page, "goblin", 5, 5)  # leaves the Place tool active and the goblin selected
    assert page.evaluate("QMG.app.selected") >= 0
    page.click("#deselect")
    assert active_tool(page) == "select"
    assert page.evaluate("QMG.app.selected") == -1 and page.evaluate("QMG.app.pinned") is None
    assert page.locator('#tools button[data-kind="select"]').get_attribute("aria-pressed") == "true"
    click_cell(page, 6, 6)  # the Place tool is gone: nothing more is placed
    assert len(items(page)) == 1


def test_the_deselect_button_sits_with_the_select_and_eraser_buttons(page):
    names = page.locator("#tools .tgrid").first.locator("button").all_inner_texts()
    assert [n.strip() for n in names] == ["Select", "Eraser", "Deselect"]


def test_the_deselect_button_is_not_a_tool_that_stays_pressed(page):
    page.click("#deselect")
    assert page.locator("#deselect").get_attribute("aria-pressed") in (None, "false")


def test_escape_deselects_and_unpins_in_the_select_tool(page):
    place(page, "goblin", 5, 5)
    page.keyboard.press("Escape")  # back to Select
    click_cell(page, 5, 5)
    assert page.evaluate("QMG.app.selected") >= 0 and page.evaluate("QMG.app.pinned") is not None
    page.keyboard.press("Escape")
    assert page.evaluate("QMG.app.selected") == -1 and page.evaluate("QMG.app.pinned") is None
    assert active_tool(page) == "select"


def key_lines(page, selector="#sheet-key"):
    return page.evaluate(
        """(sel) => [...document.querySelectorAll(sel + ' h4, ' + sel + ' li')].map((e) => e.textContent.trim())""",
        selector,
    )


def test_the_piece_key_is_hidden_until_something_is_placed(page):
    assert page.locator("#sheet-key-section").is_hidden()
    assert page.locator("#print-key-section").is_hidden()


def test_the_piece_key_lists_used_pieces_grouped_like_the_palette_with_counts(page):
    place(page, "goblin", 5, 5)
    place(page, "goblin", 6, 5)
    place(page, "orc", 7, 5)
    place(page, "table", 10, 10)
    assert key_lines(page) == ["Furniture", "Table", "Monsters", "Goblin \u00d72", "Orc"]
    assert key_lines(page, "#print-key") == key_lines(page)
    assert (
        page.locator('#sheet-key li:has-text("Goblin") use').get_attribute("href") == "#icon-goblin"
    )


def test_the_piece_key_includes_room_tiles_and_combines_numbered_markers(page):
    place(page, "marker-3", 2, 2)
    place(page, "marker-1", 3, 2)
    pick_tile(page)
    drag_cells(page, 8, 8, 9, 9)
    lines = key_lines(page)
    assert "Room tiles" in lines and "Room tile" in lines
    assert lines[-2:] == ["Markers", "Markers 1, 3"]


def test_the_piece_key_follows_edits_and_undo(page):
    place(page, "goblin", 5, 5)
    assert key_lines(page) == ["Monsters", "Goblin"]
    page.click('#tools button[data-kind="erase"]')
    click_cell(page, 5, 5)
    assert page.locator("#sheet-key-section").is_hidden()
    page.click("#undo")
    assert key_lines(page) == ["Monsters", "Goblin"]


def test_grey_has_its_own_solid_stone_areas_section_above_doors_and_walls(page):
    headings = [h.lower() for h in page.locator("#tools h2, #tools summary").all_inner_texts()]
    assert headings[:2] == ["tools", "highlight"]
    assert headings[2].startswith("solid stone areas")
    assert headings[3] == "hero view zones"
    assert headings[4] == "doors & walls"
    highlight_grid = page.locator("#tools h2, #tools summary", has_text="Highlight").locator(
        "xpath=following-sibling::div[1]"
    )
    assert "Grey" not in highlight_grid.inner_text()
    solid_grid = page.locator("#tools h2, #tools summary", has_text="Solid stone areas").locator(
        "xpath=following-sibling::div[1]"
    )
    assert solid_grid.inner_text().split() == ["Grey", "Clear"]
    solid_grid.get_by_role("button", name="Grey").click()
    click_cell(page, 3, 3)
    assert page.evaluate("QMG.app.state.hl[3 * 26 + 3]") == 1  # still the grey highlight, value 1


def panel_square(page):
    return page.locator("#inspector .square").inner_text()


def test_the_panel_follows_the_selected_piece_when_it_moves(page):
    place(page, "goblin", 5, 5)  # placing selects the new piece
    assert panel_square(page) == "Square F6"
    page.click('#inspector button[title="Move right"]')
    assert panel_square(page) == "Square G6"  # the panel followed the piece
    assert "Goblin" in page.locator("#inspector").inner_text()
    page.keyboard.press("ArrowDown")
    assert panel_square(page) == "Square G7"
    assert "Goblin" in page.locator("#inspector").inner_text()


def test_the_panel_follows_a_dragged_piece(page):
    place(page, "goblin", 5, 5)
    page.click('#tools button[data-kind="select"]')
    cx, cy = cell_center(page, 5, 5)
    nx, ny = cell_center(page, 8, 5)
    page.mouse.move(cx, cy)
    page.mouse.down()
    page.mouse.move(nx, ny, steps=6)
    page.mouse.up()
    assert panel_square(page) == "Square I6"
    assert "Goblin" in page.locator("#inspector").inner_text()


def ghost_count(page):
    return page.locator("#layer-overlay .ghost").count()


def test_the_hover_preview_shows_for_a_mouse(page):
    pick_piece(page, "goblin")
    cx, cy = cell_center(page, 5, 5)
    page.mouse.move(cx, cy)
    assert ghost_count(page) == 1


def test_a_touch_pointer_never_shows_the_hover_ghost(page):
    """A touch pointer has no hover. A pointermove of type touch (with no pointerleave, as can
    happen on a real phone) must not draw the transparent preview or the square highlight."""
    pick_piece(page, "goblin")
    cx, cy = cell_center(page, 5, 5)
    page.evaluate(
        """([x, y]) => document.querySelector('#board').dispatchEvent(
            new PointerEvent('pointermove', {pointerType: 'touch', clientX: x, clientY: y, bubbles: true}))""",
        [cx, cy],
    )
    assert ghost_count(page) == 0
    assert page.locator("#layer-overlay .hover").count() == 0
    # the same position as a mouse does show the preview, so the check above is not vacuous
    page.mouse.move(cx, cy)
    assert ghost_count(page) == 1


def test_tapping_an_identical_piece_again_selects_it_instead_of_clearing(page):
    place(page, "marker-a", 5, 5)
    assert state(page, "items.length") == 1
    click_cell(page, 5, 5)  # the same marker on the same square is refused as a duplicate
    assert state(page, "items.length") == 1
    assert (
        page.evaluate("QMG.app.selected") == 0
    )  # but the existing one is selected, not deselected
    assert panel_square(page) == "Square F6"
    assert "Marker A" in page.locator("#inspector").inner_text()


def test_placing_moves_a_pinned_panel_to_the_new_piece(page):
    page.click('#tools button[data-kind="select"]')
    click_cell(page, 3, 3)  # pin a different square with the Select tool
    assert panel_square(page) == "Square D4"
    place(page, "marker-a", 8, 8)
    assert panel_square(page) == "Square I9"  # the panel moved to the piece just placed
    assert "Marker A" in page.locator("#inspector").inner_text()
    pick_piece(page, "marker-b")
    click_cell(page, 10, 8)
    assert panel_square(page) == "Square K9"


def test_drawing_a_tile_moves_a_pinned_panel_to_the_tile(page):
    page.click('#tools button[data-kind="select"]')
    click_cell(page, 3, 3)
    assert panel_square(page) == "Square D4"
    pick_tile(page)
    drag_cells(page, 8, 8, 9, 9)
    assert panel_square(page) == "Square I9"


# ---------------------------------------------------------------- print: zones and room colors
CORRIDOR = (226, 217, 198)  # the plain board color rooms print in without their tints


def zoned_map(page, site):
    st = ref.blank()
    st["zones"][100] = 2  # a zone square (F4 .. any corridor or room square will do)
    st["hl"][101] = 1  # solid stone: a highlight that must always print
    open_link(page, site, ref.encode(st))


def room_tint(page):
    """The color actually painted at the middle of an empty square of room E (what a printer gets)."""
    x, y = cell_center(page, 18, 2)
    png = page.screenshot(clip={"x": x - 2, "y": y - 2, "width": 4, "height": 4})
    return Image.open(io.BytesIO(png)).convert("RGB").getpixel((1, 1))


def test_the_print_options_for_zones_and_room_colors_are_on_by_default(page):
    assert page.locator("#po-zones").is_checked()
    assert page.locator("#po-rooms").is_checked()


def test_there_is_no_print_option_for_highlights(page):
    labels = page.locator(".printopts").inner_text().lower()
    assert "zone" in labels and "room" in labels and "highlight" not in labels


def test_the_print_options_show_on_screen_but_are_not_printed(page):
    assert page.locator(".printopts").is_visible()
    page.emulate_media(media="print")
    assert page.locator(".printopts").is_hidden()


def test_zones_print_unless_their_option_is_off_and_the_zone_legend_goes_with_them(page, site):
    zoned_map(page, site)
    assert page.locator("#legend li.legend-zone").count() == 1
    page.emulate_media(media="print")
    assert (
        page.evaluate("getComputedStyle(document.querySelector('#layer-zones')).display") != "none"
    )
    assert page.locator("#legend li.legend-zone").is_visible()
    page.emulate_media(media="screen")
    page.uncheck("#po-zones")
    page.emulate_media(media="print")
    assert (
        page.evaluate("getComputedStyle(document.querySelector('#layer-zones')).display") == "none"
    )
    assert page.locator("#legend li.legend-zone").is_hidden()


def test_zones_still_show_on_screen_when_their_print_option_is_off(page, site):
    zoned_map(page, site)
    page.uncheck("#po-zones")
    assert (
        page.evaluate("getComputedStyle(document.querySelector('#layer-zones')).display") != "none"
    )


def test_room_tints_print_unless_their_option_is_off(page):
    page.emulate_media(media="print")
    assert room_tint(page) != CORRIDOR
    page.emulate_media(media="screen")
    page.uncheck("#po-rooms")
    assert room_tint(page) != CORRIDOR  # the screen keeps its colors
    page.emulate_media(media="print")
    assert room_tint(page) == CORRIDOR


def test_highlights_print_whatever_the_other_options_say(page, site):
    zoned_map(page, site)
    page.uncheck("#po-zones")
    page.uncheck("#po-rooms")
    page.emulate_media(media="print")
    assert page.evaluate("getComputedStyle(document.querySelector('#layer-hl')).display") != "none"
    assert page.evaluate("document.querySelectorAll('#layer-hl *').length") > 0


def test_legend_swatches_keep_their_colors_when_printed(page, site):
    """Browsers drop background colors on paper unless the element asks for them to be kept."""
    zoned_map(page, site)  # solid stone is in the legend, and so is a zone
    page.emulate_media(media="print")
    swatches = page.locator("#legend .swatch")
    assert swatches.count() >= 2
    kept = swatches.evaluate_all("els => els.map((e) => getComputedStyle(e).printColorAdjust)")
    assert set(kept) == {"exact"}


# ---------------------------------------------------------------- the What's here panel keeps its size
def crowded_map(page, site, pieces=("goblin", "orc", "skeleton", "zombie")):
    st = ref.blank()
    for slug in pieces:
        st["items"].append((piece_id(page, slug), 5, 5, 0))
    st["hl"][9 * 26 + 8] = 3  # a highlight on an empty square at I10
    st["tiles"].append((piece_id(page, "room-tile"), 12, 15, 2, 2))
    open_link(page, site, ref.encode(st))


def hover(page, x, y):
    page.evaluate("window.scrollTo(0, 0)")
    page.mouse.move(*cell_center(page, x, y))
    page.wait_for_timeout(60)


def card_box(page):
    return page.locator("#inspector-card").bounding_box()


def test_the_whats_here_card_keeps_its_size_whatever_is_under_the_mouse(page, site):
    page.set_viewport_size({"width": 1400, "height": 1000})
    crowded_map(page, site)
    hover(page, 0, 0)  # a bare corridor square
    first = card_box(page)
    for x, y in [(5, 5), (8, 9), (12, 15), (2, 2), (0, 0)]:  # a stack, a highlight, a tile, a room
        hover(page, x, y)
        box = card_box(page)
        assert (box["height"], box["y"]) == (first["height"], first["y"]), (x, y)


def test_pinning_a_square_does_not_resize_the_whats_here_card(page, site):
    page.set_viewport_size({"width": 1400, "height": 1000})
    crowded_map(page, site)
    hover(page, 0, 0)
    first = card_box(page)
    click_cell(page, 5, 5)  # pins the stack
    assert card_box(page)["height"] == first["height"]
    page.keyboard.press("Escape")
    assert card_box(page)["height"] == first["height"]


def test_the_cards_below_do_not_move_while_the_mouse_moves_over_the_map(page, site):
    page.set_viewport_size({"width": 1400, "height": 1000})
    crowded_map(page, site)
    below = page.locator("#side > .card").nth(1)
    hover(page, 0, 0)
    y = below.bounding_box()["y"]
    for x, yy in [(5, 5), (12, 15), (8, 9)]:
        hover(page, x, yy)
        assert below.bounding_box()["y"] == y


def test_the_pieces_list_scrolls_inside_the_card_and_fits_two_pieces_without_scrolling(page, site):
    page.set_viewport_size({"width": 1400, "height": 1000})
    crowded_map(page, site)
    hover(page, 5, 5)  # four pieces
    here = page.locator("#inspector .here")
    assert here.evaluate("e => e.scrollHeight > e.clientHeight")  # four do not fit: it scrolls
    crowded_map(page, site, pieces=("goblin", "orc"))
    hover(page, 5, 5)  # two pieces
    assert here.evaluate("e => e.scrollHeight <= e.clientHeight + 1")
