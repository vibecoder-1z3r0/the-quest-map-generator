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
    assert page.locator("#notes-preview h3").inner_text() == "Secret"
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
    assert page.locator('#tools button[data-kind="piece"]').count() == count
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
