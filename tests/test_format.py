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
    tiles: state.tiles.map((t) => [t.id, t.x, t.y, t.w, t.h]),
    legend: state.legend, num: state.num, title: state.title, intro: state.intro, notes: state.notes,
    wm_id: state.wmId, wm_text: state.wmText, series: state.series, warnings,
    hero: state.hero, zones: Array.from(state.zones),
    rooms: Object.fromEntries(Object.entries(state.rooms).map(([r, v]) => [r, { start: v.start, group: v.group, texts: v.texts }])),
    play: state.play && Object.fromEntries(Object.entries(state.play).map(([k, v]) => [k, [...v].sort((a, b) => a - b)])),
  };
}
"""


def as_ref_state(js: dict) -> dict:
    out = {k: v for k, v in js.items() if k != "warnings"}
    out["legend"] = {int(k): v for k, v in out["legend"].items()}
    out["items"] = [tuple(i) for i in out["items"]]
    out["tiles"] = [tuple(t) for t in out["tiles"]]
    out["rooms"] = {int(k): v for k, v in out["rooms"].items()}
    return out


def normalized(st: dict) -> dict:
    st = dict(st)
    st["legend"] = {int(k): v for k, v in st["legend"].items()}
    st["items"] = [tuple(i) for i in st["items"]]
    st["tiles"] = [tuple(t) for t in st["tiles"]]
    st.setdefault("series", "")  # links made before the series field existed have none
    st.setdefault("hero", False)  # ... and before hero view existed
    st.setdefault("zones", [0] * ref.SQUARES)
    st.setdefault("rooms", {})
    st.setdefault("play", None)
    st["rooms"] = {int(k): v for k, v in st["rooms"].items()}
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


def test_a_stored_grey_legend_label_is_ignored(page):
    st = ref.blank()
    st["legend"] = {1: "not rock", 2: "any trap"}
    js = page.evaluate(DECODE_JS, ref.encode(st))
    assert js["legend"] == {"2": "any trap"}
    payload = page.evaluate(
        "async (p) => { const { state } = await QMG.decodeHash(p); return QMG.encodeState(state); }",
        ref.encode(st),
    )
    assert ref.decode(payload)["legend"] == {2: "any trap"}


TILE = 100  # the room tile's permanent id


def test_tiles_decode_with_their_own_sizes(page):
    st = ref.blank()
    st["tiles"] = [(TILE, 4, 10, 2, 3), (TILE, 0, 0, 26, 19)]
    js = page.evaluate(DECODE_JS, ref.encode(st))
    assert js["tiles"] == [[TILE, 4, 10, 2, 3], [TILE, 0, 0, 26, 19]]
    assert js["warnings"] == []


def test_tiles_that_do_not_fit_or_are_not_tiles_are_skipped_with_a_warning(page):
    st = ref.blank()
    st["tiles"] = [
        (TILE, 4, 10, 2, 3),
        (TILE, 25, 5, 2, 1),  # runs off the right edge
        (TILE, 5, 18, 1, 2),  # runs off the bottom edge
        (TILE, 5, 5, 0, 1),  # zero width
        (40, 5, 5, 1, 1),  # a goblin is not a tile
        (200, 5, 5, 1, 1),  # unknown id
    ]
    js = page.evaluate(DECODE_JS, ref.encode(st))
    assert js["tiles"] == [[TILE, 4, 10, 2, 3]]
    assert any("room tile" in w and "skipped" in w for w in js["warnings"])


def test_a_tile_id_used_as_a_piece_is_skipped(page):
    st = ref.blank()
    st["items"] = [(TILE, 5, 5, 0), (40, 6, 5, 0)]
    js = page.evaluate(DECODE_JS, ref.encode(st))
    assert js["items"] == [[40, 6, 5, 0]]


def test_too_many_tiles_is_refused(page):
    body = bytearray(ref.encode_body(ref.blank()))
    head = 1 + (ref.SQUARES + 1) // 2 + 1  # flags, highlights, empty item count
    body[head : head + 1] = ref.varint(300)
    with pytest.raises(Exception, match="too many"):
        page.evaluate("(p) => QMG.decodeHash(p)", ref.raw_payload(bytes(body)))


def test_links_made_before_the_series_field_existed_still_decode_with_no_series(page):
    st = ref.blank()
    st["title"] = "An old quest"
    old_body = ref.encode_body(st)[:-1]  # drop the trailing (empty) series string
    js = page.evaluate(DECODE_JS, ref.raw_payload(old_body))
    assert js["title"] == "An old quest" and js["series"] == "" and js["warnings"] == []


def test_the_series_roundtrips_and_is_filtered_and_limited(page):
    st = ref.blank()
    st["series"] = "The Order of the Oth"
    assert page.evaluate(DECODE_JS, ref.encode(st))["series"] == "The Order of the Oth"
    st["series"] = "<b>" + "s" * 400 + "</b>"
    js = page.evaluate(DECODE_JS, ref.encode(st))
    assert len(js["series"]) == 160 and "<" not in js["series"]
    assert any("series" in w and "shortened" in w for w in js["warnings"])


def test_the_js_encoder_writes_the_series_in_the_spec_position(page):
    payload = page.evaluate(
        "async () => { QMG.app.state.series = 'Oth'; return QMG.encodeState(QMG.app.state); }"
    )
    assert ref.decode(payload)["series"] == "Oth"


# ---------------------------------------------------------------- hero view data (FORMAT.md 4.7, 4.8)
def hero_state() -> dict:
    st = ref.blank()
    st["hero"] = True
    st["rooms"] = {
        0: {
            "start": True,
            "group": 0,
            "texts": ["Read aloud A", "Treasure A", "Traps A", "Secret A"],
        },
        10: {"start": False, "group": 1, "texts": ["K", "", "", ""]},
        11: {"start": False, "group": 1, "texts": ["L", "", "", ""]},
        26: {"start": False, "group": 0, "texts": ["", "Zone 1 purse", "", ""]},
    }
    st["play"] = {"rev": [0, 10], "t": [10], "tr": [], "sd": [26]}
    return st


ZONE_LAYER = bytes(
    ref.SQUARES
)  # an empty zone layer (one byte per square), which starts the hero section


def body_of(payload: str) -> bytes:
    data = base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4))
    return zlib.decompress(data[1:], -15)


def test_hero_data_decodes_to_what_the_reference_encoded(page):
    st = hero_state()
    js = page.evaluate(DECODE_JS, ref.encode(st))
    assert as_ref_state(js) == normalized(st)
    assert js["warnings"] == []


def test_hero_data_roundtrips_through_the_js_encoder(page):
    st = hero_state()
    payload = page.evaluate(
        "async (p) => { const { state } = await QMG.decodeHash(p); return QMG.encodeState(state); }",
        ref.encode(st),
    )
    assert normalized(ref.decode(payload)) == normalized(st)


def test_states_without_hero_data_encode_exactly_as_before(page):
    st = ref.blank()
    st["title"] = "Plain quest"
    st["series"] = "Oth"
    payload = page.evaluate(
        "async (p) => { const { state } = await QMG.decodeHash(p); return QMG.encodeState(state); }",
        ref.encode(st),
    )
    assert body_of(payload) == ref.encode_body(
        st
    )  # no trailing hero bytes, links stay as short as before


def test_no_play_state_and_an_explicit_empty_one_are_different_and_both_survive(page):
    for play in (None, {"rev": [], "t": [], "tr": [], "sd": []}):
        st = hero_state()
        st["play"] = play
        payload = page.evaluate(
            "async (p) => { const { state } = await QMG.decodeHash(p); return QMG.encodeState(state); }",
            ref.encode(st),
        )
        assert ref.decode(payload)["play"] == play


def test_a_truncated_play_state_is_refused(page):
    body = ref.encode_body(hero_state())
    with pytest.raises(Exception, match="truncated"):
        page.evaluate("(p) => QMG.decodeHash(p)", ref.raw_payload(body[:-3]))


def test_too_many_room_records_are_refused(page):
    st = ref.blank()
    body = ref.encode_body(st) + ZONE_LAYER + ref.varint(57)
    with pytest.raises(Exception, match="corrupt"):
        page.evaluate("(p) => QMG.decodeHash(p)", ref.raw_payload(body))


def test_room_records_for_unknown_regions_are_skipped_with_a_warning(page):
    empty = b"".join(ref.string("") for _ in range(4))
    good = bytes([5, 1, 0]) + ref.string("ok") + b"".join(ref.string("") for _ in range(3))
    bad = bytes([60, 1, 0]) + empty  # there are only 56 regions
    body = ref.encode_body(ref.blank()) + ZONE_LAYER + ref.varint(2) + good + bad
    js = page.evaluate(DECODE_JS, ref.raw_payload(body))
    assert list(js["rooms"]) == ["5"]
    assert any("room" in w and "skipped" in w for w in js["warnings"])


def test_room_texts_are_limited_to_600_characters_and_filtered(page):
    st = ref.blank()
    st["rooms"] = {
        3: {"start": False, "group": 0, "texts": ["<b>" + "x" * 700 + "</b>", "ok", "", ""]}
    }
    js = page.evaluate(DECODE_JS, ref.encode(st))
    text = js["rooms"]["3"]["texts"][0]
    assert len(text) == 600 and "<" not in text
    assert js["rooms"]["3"]["texts"][1] == "ok"
    assert any("shortened" in w for w in js["warnings"])
    assert any("removed" in w for w in js["warnings"])


def test_a_duplicate_room_record_keeps_the_last_one(page):
    st = ref.blank()
    one = bytes([4, 0, 0]) + ref.string("first") + b"".join(ref.string("") for _ in range(3))
    two = bytes([4, 1, 0]) + ref.string("second") + b"".join(ref.string("") for _ in range(3))
    body = ref.encode_body(st) + ZONE_LAYER + ref.varint(2) + one + two
    js = page.evaluate(DECODE_JS, ref.raw_payload(body))
    assert js["rooms"]["4"]["texts"][0] == "second" and js["rooms"]["4"]["start"] is True


def test_a_full_set_of_room_texts_fits_in_a_link(page):
    st = ref.blank()
    words = (
        "the door grinds open and dust hangs in the torchlight above the old stone floor ".split()
    )
    st["rooms"] = {
        region: {
            "start": False,
            "group": 0,
            "texts": [
                " ".join(words[(region + k + i) % len(words)] for i in range(120))[:600]
                for k in range(4)
            ],
        }
        for region in range(ref.REGIONS)
    }
    payload = ref.encode(st)
    js = page.evaluate(DECODE_JS, payload)
    assert len(js["rooms"]) == 56 and js["warnings"] == []
    again = page.evaluate(
        "async (p) => { const { state } = await QMG.decodeHash(p); return QMG.encodeState(state); }",
        payload,
    )
    assert ref.decode(again)["rooms"] == st["rooms"]


def test_a_zone_layer_alone_is_enough_to_write_the_hero_section_and_roundtrips(page):
    st = ref.blank()
    st["zones"][100] = 4
    payload = page.evaluate(
        "async (p) => { const { state } = await QMG.decodeHash(p); return QMG.encodeState(state); }",
        ref.encode(st),
    )
    assert body_of(payload) == ref.encode_body(st)
    assert ref.decode(payload)["zones"][100] == 4


def test_zones_can_share_a_square_with_stone_and_other_highlights(page):
    st = ref.blank()
    st["hl"][7] = 1  # solid stone
    st["hl"][8] = 2  # a trap highlight
    st["zones"][7] = 2
    st["zones"][8] = 3
    js = page.evaluate(DECODE_JS, ref.encode(st))
    assert js["hl"][7] == 1 and js["hl"][8] == 2
    assert js["zones"][7] == 2 and js["zones"][8] == 3


def test_a_truncated_zone_layer_is_refused(page):
    st = ref.blank()
    st["zones"][5] = 1
    body = ref.encode_body(st)
    with pytest.raises(Exception, match="truncated"):
        page.evaluate("(p) => QMG.decodeHash(p)", ref.raw_payload(body[:-100]))


def many_zones_state():
    st = ref.blank()
    st["zones"][100] = 4
    st["zones"][101] = 17
    st["zones"][102] = 30
    st["legend"] = {6: "Zone one name", 22: "Seventeenth", 35: "Thirtieth"}
    st["rooms"] = {
        3: {"start": True, "group": 0, "texts": ["D", "", "", ""]},
        42: {"start": False, "group": 2, "texts": ["Z17 reads", "chest", "", "door"]},
        55: {"start": False, "group": 2, "texts": ["Z30", "", "", ""]},
    }
    st["play"] = {"rev": [3, 42], "t": [42], "tr": [], "sd": [55]}
    return st


def test_a_quest_with_thirty_zones_decodes_to_what_the_reference_encoded(page):
    st = many_zones_state()
    js = page.evaluate(DECODE_JS, ref.encode(st))
    assert as_ref_state(js) == normalized(st)
    assert js["warnings"] == []


def test_a_quest_with_thirty_zones_roundtrips_through_the_js_encoder(page):
    st = many_zones_state()
    payload = page.evaluate(
        "async (p) => { const { state } = await QMG.decodeHash(p); return QMG.encodeState(state); }",
        ref.encode(st),
    )
    assert normalized(ref.decode(payload)) == normalized(st)
    assert body_of(payload) == ref.encode_body(st)


def test_a_zone_name_beyond_the_tenth_is_stored_in_the_legend(page):
    st = ref.blank()
    st["legend"] = {16: "Zone 11", 35: "Zone 30"}
    assert as_ref_state(page.evaluate(DECODE_JS, ref.encode(st)))["legend"] == st["legend"]


def test_a_zone_above_thirty_is_read_as_no_zone(page):
    st = ref.blank()
    st["zones"][7] = 31
    st["zones"][8] = 30
    js = page.evaluate(DECODE_JS, ref.encode(st))
    assert js["zones"][7] == 0 and js["zones"][8] == 30


def test_a_region_record_beyond_the_fifty_sixth_is_refused(page):
    with pytest.raises(Exception, match="corrupt"):
        too_many = ref.encode_body(ref.blank()) + ZONE_LAYER + ref.varint(57)
        page.evaluate("(p) => QMG.decodeHash(p)", ref.raw_payload(too_many))


def test_the_play_state_is_28_bytes_and_covers_all_56_regions(page):
    st = ref.blank()
    st["play"] = {"rev": [0, 55], "t": [], "tr": [], "sd": [30]}
    without_play = {**st, "play": None, "zones": [1] + [0] * (ref.SQUARES - 1)}  # same sections
    assert len(ref.encode_body(st)) - len(ref.encode_body(without_play)) == 28
    js = page.evaluate(DECODE_JS, ref.encode(st))
    assert js["play"] == {"rev": [0, 55], "t": [], "tr": [], "sd": [30]}
