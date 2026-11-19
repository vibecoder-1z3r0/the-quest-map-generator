"""Visual checks: board-only baselines (with tolerance) and screenshot artifacts for review."""

from __future__ import annotations

import os

import reference as ref
from conftest import ARTIFACTS, CELL, MARGIN, ROOT, VIEW_W, open_link
from PIL import Image, ImageChops

BASELINES = ROOT / "tests/baselines"
UPDATE = os.environ.get("QMG_UPDATE_BASELINES") == "1"
MAX_DIFF_FRACTION = 0.01  # fraction of pixels allowed to differ noticeably (fonts, antialiasing)
PIXEL_THRESHOLD = 48


def demo_state(catalog: dict[str, int]) -> dict:
    st = ref.blank()
    put = lambda slug, x, y, r=0: st["items"].append((catalog[slug], x, y, r))  # noqa: E731
    put("table", 4, 4)
    put("stairs", 10, 3)
    put("tomb", 14, 6, 1)
    put("bookcase", 3, 9)
    put("fireplace", 8, 12, 2)
    put("throne", 20, 4)
    put("door", 4, 3)
    put("door", 8, 6, 1)
    put("secret-door", 12, 9, 2)
    for i, slug in enumerate(
        ["goblin", "orc", "abomination", "skeleton", "zombie", "mummy", "gargoyle", "dread-warrior"]
    ):
        put(slug, 6 + i, 5 if i < 3 else 7)
    for i, slug in enumerate(["barbarian", "dwarf", "elf", "wizard"]):
        put(slug, 2 + i, 14)
    for i, slug in enumerate(
        ["treasure-chest", "pit-trap", "spear-trap", "falling-rock-trap", "rubble"]
    ):
        put(slug, 18 + i, 10)
    put("alchemists-bench", 18, 13)
    put("sorcerers-table", 21, 15)
    put("torture-rack", 9, 15)
    for n in range(1, 10):
        put(f"marker-{n}", 2 + n, 17)
    for x in range(5):
        for y in range(3):
            st["hl"][y * 26 + 20 + x] = 1
    for i, v in enumerate([2, 3, 4, 5]):
        st["hl"][5 + i] = v
    st["legend"] = {2: "pit trap area"}
    return st


def catalog_ids() -> dict[str, int]:
    import json

    return {p["slug"]: p["id"] for p in json.loads((ROOT / "src/catalog.json").read_text())}


def board_clip(pg):
    box = pg.locator("#board").bounding_box()
    scale = box["width"] / VIEW_W
    return {
        "x": box["x"] + MARGIN * scale,
        "y": box["y"] + MARGIN * scale,
        "width": 26 * CELL * scale,
        "height": 19 * CELL * scale,
    }


def compare(name: str, path_new, tmp_dir=ARTIFACTS):
    baseline = BASELINES / f"{name}.png"
    if UPDATE:
        BASELINES.mkdir(parents=True, exist_ok=True)
        baseline.write_bytes(path_new.read_bytes())
        return
    assert baseline.is_file(), f"no baseline for {name}; run `make baselines`"
    a = Image.open(baseline).convert("RGB")
    b = Image.open(path_new).convert("RGB")
    assert a.size == b.size, f"{name}: size changed {a.size} -> {b.size}"
    diff = ImageChops.difference(a, b).convert("L")
    bad = sum(diff.histogram()[PIXEL_THRESHOLD + 1 :])
    fraction = bad / (a.size[0] * a.size[1])
    if fraction > MAX_DIFF_FRACTION:
        diff.point(lambda p: 255 if p > PIXEL_THRESHOLD else 0).save(tmp_dir / f"{name}-diff.png")
    assert fraction <= MAX_DIFF_FRACTION, f"{name}: {fraction:.2%} of pixels differ"


def test_board_with_every_piece_matches_the_baseline(page, site):
    ARTIFACTS.mkdir(exist_ok=True)
    open_link(page, site, ref.encode(demo_state(catalog_ids())))
    page.mouse.move(0, 0)
    page.evaluate("document.activeElement && document.activeElement.blur()")
    shot = ARTIFACTS / "board-demo.png"
    page.screenshot(path=str(shot), clip=board_clip(page))
    compare("board-demo", shot)


def test_empty_board_matches_the_baseline(page):
    ARTIFACTS.mkdir(exist_ok=True)
    shot = ARTIFACTS / "board-empty.png"
    page.screenshot(path=str(shot), clip=board_clip(page))
    compare("board-empty", shot)


def test_review_screenshots_are_produced(page, site, browser):
    """Not compared: full-page, dark and phone screenshots (plus a print PDF) for human review."""
    ARTIFACTS.mkdir(exist_ok=True)
    link = ref.encode(demo_state(catalog_ids()))
    open_link(page, site, link)
    page.screenshot(path=str(ARTIFACTS / "page-light.png"), full_page=True)
    page.select_option("#theme", label="Dark")
    page.screenshot(path=str(ARTIFACTS / "page-dark.png"), full_page=True)
    page.emulate_media(media="print")
    page.pdf(path=str(ARTIFACTS / "print.pdf"))
    phone = browser.new_context(
        viewport={"width": 390, "height": 844}, device_scale_factor=2, has_touch=True
    )
    pg = phone.new_page()
    pg.goto(site + "#" + link)
    pg.wait_for_function("window.QMG !== undefined")
    pg.screenshot(path=str(ARTIFACTS / "page-phone.png"), full_page=True)
    phone.close()
    for name in ("page-light.png", "page-dark.png", "print.pdf", "page-phone.png"):
        assert (ARTIFACTS / name).stat().st_size > 1000
