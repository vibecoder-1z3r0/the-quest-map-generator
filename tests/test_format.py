"""The link format: spec conformance, golden links, and defensive decoding."""

from __future__ import annotations

import base64
import json
import re
import zlib
from pathlib import Path

import pytest
import reference as ref
from conftest import ROOT, click_cell, open_link, pick_piece, settle

GOLDEN = json.loads((Path(__file__).parent / "golden/v1.json").read_text(encoding="utf-8"))

DECODE_JS = """
async (payload) => {
  const { state, warnings } = await QMG.decodeHash(payload);
  return {
    theme: state.theme, hl: Array.from(state.hl),
    items: state.items.map((i) => [i.id, i.x, i.y, i.r]),
    legend: state.legend, num: state.num, title: state.title, intro: state.intro, notes: state.notes,
    wm_id: state.wmId, wm_text: state.wmText, warnings,
  };
}
"""


def as_ref_state(js: dict) -> dict:
    out = {k: v for k, v in js.items() if k != "warnings"}
    out["legend"] = {int(k): v for k, v in out["legend"].items()}
    out["items"] = [tuple(i) for i in out["items"]]
    return out


def normalized(st: dict) -> dict:
    st = dict(st)
    st["legend"] = {int(k): v for k, v in st["legend"].items()}
    st["items"] = [tuple(i) for i in st["items"]]
    return st


@pytest.mark.parametrize("case", GOLDEN, ids=[c["name"] for c in GOLDEN])
def test_golden_links_still_decode(page, case):
    js = page.evaluate(DECODE_JS, case["url"])
    assert as_ref_state(js) == normalized(case["state"])
    assert js["warnings"] == []


@pytest.mark.parametrize("case", GOLDEN, ids=[c["name"] for c in GOLDEN])
def test_reference_decoder_reads_what_the_js_encodes(page, case):
    payload = page.evaluate(
        """async (p) => { const { state } = await QMG.decodeHash(p); return QMG.encodeState(state); }""",
        case["url"],
    )
    assert normalized(ref.decode(payload)) == normalized(case["state"])


def test_the_worked_example_in_the_spec_decodes(page):
    spec = (ROOT / "docs/FORMAT.md").read_text(encoding="utf-8")
    url = re.search(r"^#(A[A-Za-z0-9_-]{30,})$", spec, re.M).group(1)
    js = page.evaluate(DECODE_JS, url)
    assert js["num"] == "3" and js["title"] == "Vault"
    assert js["hl"][0] == 1 and js["hl"][1] == 2
    assert js["items"] == [[1, 4, 7, 0], [2, 4, 7, 3]]
    assert js["legend"] == {"2": "trap"}


def test_spec_example_body_length_is_accurate():
    spec = (ROOT / "docs/FORMAT.md").read_text(encoding="utf-8")
    url = re.search(r"^#(A[A-Za-z0-9_-]{30,})$", spec, re.M).group(1)
    data = base64.urlsafe_b64decode(url + "=" * (-len(url) % 4))
    body = zlib.decompress(data[1:], -15)
    assert f"Body ({len(body)} bytes)" in spec


def test_blank_state_has_no_hash(page):
    assert page.evaluate("location.hash") == ""


def test_encode_decode_roundtrip_in_page(page):
    page.evaluate(
        """() => {
          const s = QMG.app.state; s.num = '7'; s.title = 'Round trip';
          s.items.push({ id: 40, x: 3, y: 4, r: 2 }); s.hl[100] = 4; s.legend[4] = 'yellow';
        }"""
    )
    js = page.evaluate(
        """async () => { const p = await QMG.encodeState(QMG.app.state); return (await QMG.decodeHash(p)).state.title; }"""
    )
    assert js == "Round trip"


def error_banner(pg):
    return pg.locator("#banner").inner_text()


def test_garbage_link_shows_banner_and_blank_map(context, site):
    pg = context.new_page()
    pg.goto(site + "#garbage!!")
    pg.wait_for_function("window.QMG !== undefined")
    pg.wait_for_timeout(200)
    assert "Couldn't read a map" in error_banner(pg)
    assert pg.evaluate("QMG.app.state.items.length") == 0


def test_unsupported_version_is_refused(context, site):
    pg = context.new_page()
    url = base64.urlsafe_b64encode(bytes([99, 1, 2, 3])).decode().rstrip("=")
    pg.goto(site + "#" + url)
    pg.wait_for_function("window.QMG !== undefined")
    pg.wait_for_timeout(200)
    assert "unsupported link version 99" in error_banner(pg)


def test_truncated_body_is_refused(page):
    st = ref.blank()
    st["title"] = "A title that makes the body a bit longer than the empty one"
    st["notes"] = "Some secret notes. " * 20
    whole = ref.encode(st)
    short_body = ref.raw_payload(ref.encode_body(st)[:100])
    for payload in (whole[:-6], short_body, ""):
        with pytest.raises(Exception):  # noqa: B017 - any failure is correct, a crash is not
            page.evaluate("(p) => QMG.decodeHash(p)", payload)


def test_decompression_bomb_is_stopped(page):
    bomb = ref.raw_payload(b"\x00" * 5_000_000)
    with pytest.raises(Exception, match="too large"):
        page.evaluate("(p) => QMG.decodeHash(p)", bomb)


def test_absurd_item_count_is_refused(page):
    body = bytearray(ref.encode_body(ref.blank()))
    head = 1 + (ref.SQUARES + 1) // 2
    body[head : head + 1] = ref.varint(5000)
    with pytest.raises(Exception, match="too many"):
        page.evaluate("(p) => QMG.decodeHash(p)", ref.raw_payload(bytes(body)))


def test_pieces_that_do_not_fit_or_are_unknown_are_skipped_with_a_warning(page):
    st = ref.blank()
    goblin = 40
    st["items"] = [
        (goblin, 5, 5, 0),
        (goblin, 25, 18, 0),
        (200, 1, 1, 0),
        (11, 25, 0, 0),
    ]  # 11 = table 3x2
    js = page.evaluate(DECODE_JS, ref.encode(st))
    assert js["items"] == [[goblin, 5, 5, 0], [goblin, 25, 18, 0]]
    assert any("skipped" in w for w in js["warnings"])


def test_non_monster_wandering_id_is_ignored(page):
    st = ref.blank()
    st["wm_id"] = 11  # table
    js = page.evaluate(DECODE_JS, ref.encode(st))
    assert js["wm_id"] == 0
    assert any("wandering monster" in w for w in js["warnings"])


def test_overlong_fields_are_truncated_and_unsafe_characters_removed(page):
    st = ref.blank()
    st["title"] = "<b>" + "x" * 400 + "</b>"
    js = page.evaluate(DECODE_JS, ref.encode(st))
    assert "<" not in js["title"] and ">" not in js["title"]
    assert len(js["title"]) == 160
    assert any("shortened" in w for w in js["warnings"])
    assert any("removed" in w for w in js["warnings"])


def test_unknown_theme_and_highlight_values_survive_reencoding(page):
    st = ref.blank()
    st["theme"] = 7
    st["hl"][10] = 9
    payload = page.evaluate(
        "async (p) => { const { state } = await QMG.decodeHash(p); return QMG.encodeState(state); }",
        ref.encode(st),
    )
    again = ref.decode(payload)
    assert again["theme"] == 7 and again["hl"][10] == 9


def test_editing_updates_the_hash_without_reload_and_it_roundtrips(page, site):
    marker = page.evaluate("window.__marker = 123")
    assert marker == 123
    pick_piece(page, "goblin")
    click_cell(page, 6, 5)
    settle(page)
    assert page.evaluate("window.__marker") == 123  # no page reload
    assert len(page.evaluate("location.hash")) > 1
    payload = page.evaluate("location.hash").lstrip("#")
    assert ref.decode(payload)["items"] == [(40, 6, 5, 0)]
    open_link(page, site, payload)
    assert page.evaluate("QMG.app.state.items.length") == 1
