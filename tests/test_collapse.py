"""The cards in the right-hand panel, the groups in the left-hand palette and the sheets in the middle fold."""

from __future__ import annotations

import pytest
import reference as ref
from conftest import click_cell, open_link

CARDS = [  # (the card's heading, something inside it that is hidden when it is folded)
    ("#inspector-card > details > summary", "#inspector"),
    ("#hero-card > details > summary", "#hero-chooser"),
    ("#quest-card > details > summary", "#series"),
    ("#stats-card > details > summary", "#stats"),
    ("#legend-card > details > summary", "#legend-edit"),
]


@pytest.fixture(autouse=True)
def quick(page):
    page.set_default_timeout(4000)


def quest(page, site):
    st = ref.blank()
    st["title"], st["intro"], st["notes"] = "Folding", "Some intro.", "Secret notes."
    open_link(page, site, ref.encode(st))


def is_open(page, summary):
    return page.locator(summary).evaluate("e => e.parentElement.open")


@pytest.mark.parametrize(("summary", "inside"), CARDS)
def test_clicking_a_card_heading_folds_and_unfolds_it(page, site, summary, inside):
    quest(page, site)
    if summary.startswith("#hero-card"):
        page.click(summary)  # the hero data card starts folded
    assert page.locator(inside).is_visible()
    page.click(summary)
    assert page.locator(inside).is_hidden()
    page.click(summary)
    assert page.locator(inside).is_visible()


def test_every_card_starts_open_except_the_hero_data_card(page, site):
    quest(page, site)
    for summary, _ in CARDS:
        assert is_open(page, summary) == (not summary.startswith("#hero-card")), summary


def test_the_pinned_hint_stays_visible_in_the_whats_here_heading_while_it_is_folded(page, site):
    quest(page, site)
    page.evaluate("window.scrollTo(0, 0)")
    click_cell(page, 2, 2)  # pins a square with the Select tool
    page.click("#inspector-card > details > summary")
    assert page.locator("#inspector").is_hidden()
    assert "pinned" in page.locator("#inspector-hint").inner_text()


def test_the_print_checkboxes_in_a_heading_do_not_fold_the_card(page, site):
    quest(page, site)
    for check, summary in [
        ("#po-stats", "#stats-card > details > summary"),
        ("#po-legend", "#legend-card > details > summary"),
    ]:
        page.click(check)
        assert is_open(page, summary), check
        assert not page.locator(check).is_checked()


def test_the_print_checkboxes_still_work_while_their_card_is_folded(page, site):
    quest(page, site)
    page.click("#stats-card > details > summary")
    page.click("#po-stats")  # the checkbox stays in the heading
    assert page.evaluate("document.body.classList.contains('np-stats')")


def test_a_folded_card_keeps_what_was_typed_and_the_link_does_not_change(page, site):
    quest(page, site)
    page.fill("#series", "The Order")
    page.evaluate("QMG.syncUrl()")
    page.wait_for_timeout(100)
    before = page.evaluate("location.hash")
    page.click("#quest-card > details > summary")
    page.click("#quest-card > details > summary")
    assert page.input_value("#series") == "The Order"
    assert page.evaluate("location.hash") == before


def test_the_keyboard_folds_a_card(page, site):
    quest(page, site)
    page.focus("#stats-card > details > summary")
    page.keyboard.press("Enter")
    assert page.locator("#stats").is_hidden()
    page.keyboard.press("Enter")
    assert page.locator("#stats").is_visible()


def test_a_folded_card_does_not_change_what_prints(page, site):
    quest(page, site)
    page.click("#quest-card > details > summary")
    page.click("#stats-card > details > summary")
    page.emulate_media(media="print")
    assert page.locator("#print-intro").is_visible()
    assert "Secret notes." in page.locator("#print-notes").inner_text()


def test_a_card_can_be_folded_on_a_phone_too(page, site):
    page.set_viewport_size({"width": 390, "height": 844})
    quest(page, site)
    page.click("#quest-card > details > summary")
    assert page.locator("#series").is_hidden()


# ---------------------------------------------------------------- the left-hand palette
GROUPS = [
    "Highlight",
    "Solid stone areas",
    "Hero view zones",
    "Doors & walls",
    "Room tiles",
    "Furniture",
    "Treasure & traps",
    "Monsters",
    "Heroes",
    "Markers",
]


def group(page, title):
    return (
        page.locator("#tools details.psec")
        .filter(has=page.locator("summary", has_text=title))
        .first
    )


def test_tools_is_a_plain_heading_that_never_folds(page):
    assert page.locator("#tools h2").first.inner_text().strip().lower() == "tools"
    texts = [t.strip().lower() for t in page.locator("#tools summary").all_inner_texts()]
    assert "tools" not in texts
    assert page.locator('#tools button[data-kind="select"]').is_visible()


def test_every_other_palette_group_is_a_foldable_section_that_starts_open(page):
    texts = [t.strip().lower() for t in page.locator("#tools summary").all_inner_texts()]
    for title in GROUPS:
        assert title.lower() in texts, title
    opened = page.locator("#tools summary").evaluate_all(
        "els => els.map((e) => e.parentElement.open)"
    )
    assert all(opened)


@pytest.mark.parametrize("title", GROUPS)
def test_each_palette_group_folds_on_its_own(page, title):
    target = group(page, title)
    inside = target.locator("button").first
    others = page.locator("#tools details.psec").evaluate_all("els => els.length")
    assert inside.is_visible() and others >= len(GROUPS)
    target.locator("summary").first.click()
    assert inside.is_hidden()
    other = group(page, "Monsters" if title != "Monsters" else "Heroes")
    assert other.locator("button").first.is_visible()  # the rest stay open
    target.locator("summary").first.click()
    assert inside.is_visible()


def test_a_tool_picked_in_a_group_stays_active_while_the_group_is_folded(page):
    page.click('#tools button[data-kind="piece"]:has-text("Goblin")')
    group(page, "Monsters").locator("summary").first.click()
    assert page.evaluate("QMG.app.tool.kind") == "piece"
    group(page, "Monsters").locator("summary").first.click()
    assert (
        page.locator('#tools button[data-kind="piece"]:has-text("Goblin")').first.get_attribute(
            "aria-pressed"
        )
        == "true"
    )


def test_zones_can_be_added_while_their_group_is_folded_and_show_when_it_opens(page):
    group(page, "Hero view zones").locator("summary").first.click()
    page.evaluate("document.querySelector('#add-zone').click()")  # not visible, but still there
    group(page, "Hero view zones").locator("summary").first.click()
    assert page.locator('#tools button[data-kind="zone"][data-value="11"]').is_visible()


def test_folding_a_palette_group_does_not_change_the_link(page, site):
    quest(page, site)
    page.evaluate("QMG.syncUrl()")
    page.wait_for_timeout(100)
    before = page.evaluate("location.hash")
    group(page, "Furniture").locator("summary").first.click()
    assert page.evaluate("location.hash") == before


def test_the_keyboard_folds_a_palette_group(page):
    group(page, "Heroes").locator("summary").first.focus()
    page.keyboard.press("Enter")
    assert group(page, "Heroes").locator("button").first.is_hidden()
    page.keyboard.press("Enter")
    assert group(page, "Heroes").locator("button").first.is_visible()


def test_a_palette_group_can_be_folded_on_a_phone_too(page):
    page.set_viewport_size({"width": 390, "height": 844})
    group(page, "Furniture").locator("summary").first.click()
    assert group(page, "Furniture").locator("button").first.is_hidden()


# ---------------------------------------------------------------- the sheets under the map
def test_the_quest_info_card_cannot_be_folded_and_notes_and_pieces_are_their_own_cards(page, site):
    st = ref.blank()
    st["title"], st["intro"], st["notes"] = "Folding", "An intro.", "Secret notes."
    st["items"].append((page.evaluate("QMG.CATALOG.find((c) => c.slug === 'goblin').id"), 5, 5, 0))
    open_link(page, site, ref.encode(st))
    assert page.locator("#quest-sheet details").count() == 0  # quest info and the introduction
    assert page.locator("#quest-sheet").locator("#sheet-intro").is_visible()
    for card in ("#sheet-notes-section", "#sheet-key-section"):
        assert page.locator(card).evaluate(
            "e => e.tagName === 'ARTICLE' && e.classList.contains('sheet')"
        )
        assert page.locator(f"#quest-sheet {card}").count() == 0  # not inside the quest info card
    order = page.evaluate(
        "[...document.querySelector('#stage').children].map((e) => e.id).filter((i) => i.endsWith('sheet') || i.endsWith('-section'))"
    )
    assert order == ["quest-sheet", "sheet-notes-section", "sheet-key-section"]


@pytest.mark.parametrize(
    ("summary", "inside"),
    [
        ("#sheet-notes-section > details > summary", "#sheet-notes"),
        ("#sheet-key-section > details > summary", "#sheet-key"),
    ],
)
def test_zargons_notes_and_the_pieces_list_fold(page, site, summary, inside):
    st = ref.blank()
    st["notes"] = "Secret notes."
    st["items"].append((page.evaluate("QMG.CATALOG.find((c) => c.slug === 'goblin').id"), 5, 5, 0))
    open_link(page, site, ref.encode(st))
    assert is_open(page, summary)
    assert page.locator(inside).is_visible()
    page.click(summary)
    assert page.locator(inside).is_hidden()
    page.click(summary)
    assert page.locator(inside).is_visible()


def test_the_sheet_print_checkboxes_do_not_fold_their_cards(page, site):
    st = ref.blank()
    st["notes"] = "Secret notes."
    st["items"].append((page.evaluate("QMG.CATALOG.find((c) => c.slug === 'goblin').id"), 5, 5, 0))
    open_link(page, site, ref.encode(st))
    for check, summary in [
        ("#po-notes", "#sheet-notes-section > details > summary"),
        ("#po-key", "#sheet-key-section > details > summary"),
        ("#po-monsters", "#sheet-key-section > details > summary"),
    ]:
        page.click(check)
        assert is_open(page, summary), check
    assert page.evaluate("document.body.classList.contains('np-notes')")
    assert page.evaluate("document.body.classList.contains('np-key')")
    assert page.evaluate("document.body.classList.contains('po-monsters')")


def test_the_notes_and_pieces_cards_appear_only_when_there_is_something_in_them(page):
    assert page.locator("#sheet-notes-section").is_hidden()
    assert page.locator("#sheet-key-section").is_hidden()
    page.fill("#notes", "Beware.")
    assert page.locator("#sheet-notes-section").is_visible()


def test_with_only_notes_typed_there_is_no_empty_quest_info_card(page):
    page.fill("#notes", "Beware.")
    assert page.locator("#quest-sheet").is_hidden()
    assert page.locator("#sheet-empty").is_hidden()
    page.fill("#qtitle", "Crypt")
    assert page.locator("#quest-sheet").is_visible()


def test_the_fold_state_of_the_sheets_does_not_change_what_prints(page, site):
    st = ref.blank()
    st["title"], st["intro"], st["notes"] = "Folding", "An intro.", "Secret notes."
    open_link(page, site, ref.encode(st))
    page.click("#sheet-notes-section > details > summary")
    page.emulate_media(media="print")
    assert "Secret notes." in page.locator("#print-notes").inner_text()
    assert page.locator("#sheet-notes-section").is_hidden()  # the live cards never print
