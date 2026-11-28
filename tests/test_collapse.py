"""The cards in the right-hand panel can be folded away."""

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
