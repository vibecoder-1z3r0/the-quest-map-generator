#!/usr/bin/env python3
"""Regenerate the README screenshots in docs/screenshots/ from the real built editor.

The showcase is the owner's quest #1, stored as a link in docs/showcase/quest-1.txt. Pass
--sample to use the built-in invented sample quest instead (handy for experiments).

Run via `make screenshots`. Screenshots are produced by driving dist/index.html, so they always
match what the tool actually does. Never commit screenshots of a superseded UI.
"""

from __future__ import annotations

import functools
import http.server
import json
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))
import reference as ref  # noqa: E402

OUT = ROOT / "docs/screenshots"
CATALOG = {p["slug"]: p["id"] for p in json.loads((ROOT / "src/catalog.json").read_text())}
MARGIN, CELL = 22, 32


def board_rows() -> list[str]:
    lines = (ROOT / "src/board.txt").read_text(encoding="utf-8").splitlines()
    return [ln for ln in lines if ln.strip() and not ln.startswith("//")]


def showcase() -> dict:
    """A small quest on the real board: unused rooms are greyed out, as in the printed quests."""
    st = ref.blank()
    rows = board_rows()
    in_play = set("TLMQKR")
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch.isalpha() and ch not in in_play:
                st["hl"][y * 26 + x] = 1
    put = lambda slug, x, y, r=0: st["items"].append((CATALOG[slug], x, y, r))  # noqa: E731
    put("stairs", 1, 16)
    for x, y in ((3, 16), (4, 16), (3, 17), (4, 17)):
        put(["barbarian", "dwarf", "elf", "wizard"][(x - 3) + 2 * (y - 16)], x, y)
    put("door", 2, 14, 0)
    put("table", 2, 11, 0)
    put("goblin", 1, 10)
    put("goblin", 4, 12)
    put("treasure-chest", 1, 13)
    st["tiles"] = [(CATALOG["room-tile"], 4, 10, 3, 3)]  # a room tile merging rooms L and M
    put("mummy", 6, 11)
    put("door", 8, 14, 0)
    put("pit-trap", 6, 15)
    put("spear-trap", 7, 15)
    put("orc", 5, 17)
    put("door", 7, 13, 1)
    put("tomb", 12, 8, 1)
    put("abomination", 14, 10)
    put("hidden-door", 8, 15, 1)
    put("secret-door", 7, 13)
    put("weapons-rack", 11, 14, 1)
    put("orc", 0, 9)
    put("dread-warlock", 10, 15)
    put("marker-1", 6, 12)
    put("marker-2", 13, 11)
    for x in (6, 7):
        st["hl"][15 * 26 + x] = 2
    st["hl"][12 * 26 + 13] = 4
    st["legend"] = {4: "secret room"}
    st["series"] = "The Order of the Oth"
    st["num"] = "1"
    st["title"] = "The Dusty Crypt"
    st["wm_id"] = CATALOG["goblin"]
    st["wm_text"] = "1 extra goblin"
    st["intro"] = (
        "The heroes descend into an old crypt.\nTorches flicker on the walls.\n\n"
        "**Beware**: something *moves* in the dark."
    )
    st["notes"] = (
        "# Zargon's secrets\n- The chest holds **150 gold**\n- Pit and spear traps in room Q\n"
        "- A secret door hides the tomb room\n\n## Monsters\n| Monster | Where |\n|---|---|\n"
        "| 2 Goblins | Room L |\n| Mummy | Room M |"
    )
    return st


def first_cell(link: str, piece_id: int) -> tuple[int, int]:
    """Where the first piece with this id sits, so the screenshot can pin and show that square."""
    for item_id, x, y, _rotation in ref.decode(link)["items"]:
        if item_id == piece_id:
            return x, y
    return 12, 9


# Hero view needs hero text, which the owner's quest does not have yet. The screenshots keep the
# zones and room records the quest already has, and only add invented zones (if it has none) and
# invented room texts (where a room has none). Sample text only, not part of the quest.
HERO_DEMO_JS = """
async ([rows]) => {
  const st = QMG.app.state;
  const zoneOf = (x, y) => {
    if (rows[y][x] !== '.') return 0;
    if (y === 0 || ([12, 13].includes(x) && y >= 1 && y <= 5)) return 1;
    if (y === 18 || ([12, 13].includes(x) && y >= 13 && y <= 17)) return 2;
    if (y === 9) return 3;
    if (x === 0) return 4;
    if (x === 25) return 5;
    return 6;
  };
  const room = (start, a, b, c, d) => ({ start, group: 0, texts: [a, b, c, d] });
  if (!st.zones.some(Boolean)) {
    for (let y = 0; y < 19; y++) {
      for (let x = 0; x < 26; x++) st.zones[y * 26 + x] = zoneOf(x, y);
    }
    st.legend[9] = 'West corridor';
    st.rooms[29] = room(
      true,
      'A cold draught runs down the long corridor. Torches gutter in iron brackets.',
      '', '', '',
    );
  }
  if (!Object.values(st.rooms).some((r) => r.start)) st.rooms[8] = room(true, '', '', '', '');
  const texts = {
    10: [
      'The door grinds open. Dust hangs in the torchlight above an old stone tomb.',
      'Beneath the tomb lid: 84 gold coins.',
      'A pressure plate is set into the floor.',
      'Nothing but cold stone.',
    ],
    18: [
      'A fire crackles in a stone hearth. Goblins snarl and reach for their weapons!',
      'A small chest holds a silver ring.',
      'The flagstones look sound.',
      'You find a hidden catch behind a loose brick.',
    ],
  };
  for (const [region, t] of Object.entries(texts)) {
    const rec = st.rooms[region] ?? room(false, '', '', '', '');
    if (!rec.texts.some(Boolean)) rec.texts = t;
    st.rooms[region] = rec;
  }
  const editor = await QMG.encodeState(st);
  st.hero = true;
  const hero = await QMG.encodeState(st);
  st.hero = false;
  return { editor, hero };
}
"""


def center(box, x, y):
    scale = box["width"] / (26 * CELL + 2 * MARGIN)
    return (
        box["x"] + (MARGIN + x * CELL + CELL / 2) * scale,
        box["y"] + (MARGIN + y * CELL + CELL / 2) * scale,
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    handler = functools.partial(Quiet, directory=str(ROOT / "dist"))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_address[1]}/index.html"
    use_sample = "--sample" in sys.argv
    link = (
        ref.encode(showcase())
        if use_sample
        else (ROOT / "docs/showcase/quest-1.txt").read_text().strip()
    )
    pin = (4, 12) if use_sample else first_cell(link, CATALOG["goblin"])
    with sync_playwright() as pw:
        browser = pw.chromium.launch()

        def open_page(hash_: str = "", **ctx):
            ctx.setdefault("viewport", {"width": 1280, "height": 820})
            context = browser.new_context(device_scale_factor=2, **ctx)
            page = context.new_page()
            page.goto(url + hash_)
            page.wait_for_function("window.QMG !== undefined")
            page.reload()
            page.wait_for_timeout(250)
            return context, page

        ctx, page = open_page()
        page.screenshot(path=str(OUT / "01-empty-board.png"))
        ctx.close()

        ctx, page = open_page("#" + link)
        page.click('#tools button[data-kind="select"]')
        box = page.locator("#board").bounding_box()
        page.mouse.click(*center(box, *pin))
        page.mouse.move(*center(box, *pin))
        page.screenshot(path=str(OUT / "02-quest-in-progress.png"))
        page.locator("#side").screenshot(path=str(OUT / "03-quest-text.png"))
        page.locator("#stage").screenshot(path=str(OUT / "07-live-quest-sheet.png"))
        page.select_option("#theme", label="Dark")
        page.wait_for_timeout(150)
        page.screenshot(path=str(OUT / "04-dark-mode.png"))
        page.emulate_media(media="print")
        page.screenshot(path=str(OUT / "05-print-view.png"), full_page=True)
        ctx.close()

        ctx, page = open_page(
            "#" + link,
            viewport={"width": 390, "height": 760},
            has_touch=True,
        )
        page.screenshot(path=str(OUT / "06-phone.png"))
        ctx.close()

        # Hero view: the same quest with hero data, as a hero link and in the editor.
        rows = [
            ln
            for ln in (ROOT / "src/board.txt").read_text().splitlines()
            if ln and not ln.startswith("//")
        ]
        ctx, page = open_page("#" + link)
        demo = page.evaluate(HERO_DEMO_JS, [rows])
        ctx.close()

        ctx, page = open_page("#" + demo["hero"])
        page.screenshot(path=str(OUT / "11-hero-start.png"))
        page.mouse.click(*center(page.locator("#board").bounding_box(), 12, 9))  # room K
        page.click("#hero-reveal")
        page.click("#confirm-ok")
        page.click("#hero-search-t")
        page.wait_for_timeout(150)
        page.screenshot(path=str(OUT / "12-hero-revealed.png"))
        ctx.close()

        ctx, page = open_page(
            "#" + demo["hero"], viewport={"width": 390, "height": 760}, has_touch=True
        )
        page.screenshot(path=str(OUT / "13-hero-phone.png"))
        ctx.close()

        ctx, page = open_page("#" + demo["editor"])
        page.click('#tools button[data-kind="select"]')
        page.mouse.click(*center(page.locator("#board").bounding_box(), 12, 8))  # pins room K
        page.wait_for_timeout(150)
        page.locator("#side").screenshot(path=str(OUT / "14-hero-authoring.png"))
        ctx.close()
        browser.close()
    server.shutdown()
    print("wrote", ", ".join(sorted(p.name for p in OUT.glob("*.png"))))


if __name__ == "__main__":
    main()
