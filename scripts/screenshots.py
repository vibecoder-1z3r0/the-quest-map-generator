#!/usr/bin/env python3
"""Regenerate the README screenshots in docs/screenshots/ from the real built editor.

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


def showcase() -> dict:
    st = ref.blank()
    put = lambda slug, x, y, r=0: st["items"].append((CATALOG[slug], x, y, r))  # noqa: E731
    put("stairs", 2, 2)
    put("door", 6, 3, 1)
    put("table", 9, 3)
    put("bookcase", 9, 1)
    put("fireplace", 16, 1, 0)
    put("throne", 19, 3)
    put("goblin", 8, 4)
    put("goblin", 11, 5)
    put("orc", 13, 4)
    put("abomination", 16, 4)
    put("mummy", 21, 6)
    put("treasure-chest", 12, 8)
    put("pit-trap", 5, 8)
    put("spear-trap", 6, 8)
    put("tomb", 15, 10, 1)
    put("secret-door", 14, 9, 2)
    put("sorcerers-table", 20, 11)
    put("weapons-rack", 3, 12)
    put("rubble", 9, 12)
    put("falling-rock-trap", 10, 12)
    put("barbarian", 2, 4)
    put("dwarf", 3, 4)
    put("elf", 2, 5)
    put("wizard", 3, 5)
    for n in (1, 2, 3):
        put(f"marker-{n}", 4 + n * 4, 14)
    for y in range(0, 4):
        for x in range(22, 26):
            st["hl"][y * 26 + x] = 1
    for x in (5, 6, 7):
        st["hl"][8 * 26 + x] = 2
    for x in range(12, 15):
        st["hl"][9 * 26 + x] = 4
    st["legend"] = {2: "pit trap area", 4: "secret room"}
    st["num"] = "1"
    st["title"] = "The Dusty Crypt"
    st["wm_id"] = CATALOG["goblin"]
    st["wm_text"] = "1 extra goblin"
    st["intro"] = (
        "The heroes descend into an old crypt.\nTorches flicker on the walls.\n\n"
        "**Beware**: something *moves* in the dark."
    )
    st["notes"] = (
        "# Zargon's secrets\n- The chest holds **150 gold**\n- The pit trap is at F9\n"
        "- A secret door hides the tomb room\n\n## Monsters\n| Monster | Where |\n|---|---|\n"
        "| 2 Goblins | Near the table |\n| Mummy | Guards the stairs |"
    )
    return st


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
    link = ref.encode(showcase())
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
        page.mouse.click(*center(box, 11, 5))
        page.mouse.move(*center(box, 11, 5))
        page.screenshot(path=str(OUT / "02-quest-in-progress.png"))
        page.locator("#side").screenshot(path=str(OUT / "03-quest-text.png"))
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
        browser.close()
    server.shutdown()
    print("wrote", ", ".join(sorted(p.name for p in OUT.glob("*.png"))))


if __name__ == "__main__":
    main()
