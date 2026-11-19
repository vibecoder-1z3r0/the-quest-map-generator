"""End-to-end editor behavior in the built page."""

from __future__ import annotations

from conftest import (
    cell_center,
    click_cell,
    items,
    open_link,
    pick_piece,
    piece_id,
    settle,
)


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
    click_cell(page, x, y)


def test_legend_lists_only_used_colors_with_fixed_grey_and_default_orange(page):
    assert page.locator("#legend li").count() == 0
    paint(page, 1, 3, 3)
    paint(page, 2, 4, 3)
    assert page.locator("#legend li").all_inner_texts() == ["Solid rock", "Trap"]


def test_grey_has_no_editable_legend_but_the_others_do(page):
    assert page.locator('#legend-edit input[data-color="1"]').count() == 0
    assert page.locator("#legend-edit input").count() == 4
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
    assert "secret" in page.locator("#sheet-notes-section > h3").inner_text().lower()
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
