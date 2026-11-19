from __future__ import annotations

import functools
import http.server
import threading
from pathlib import Path

import pytest
from playwright.sync_api import Page, sync_playwright

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
ARTIFACTS = ROOT / "test-artifacts"
MARGIN = 22  # board margin in viewBox units (matches src/js/render.js)
CELL = 32
VIEW_W = 26 * CELL + 2 * MARGIN


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


@pytest.fixture(scope="session")
def site():
    if not (DIST / "index.html").is_file():
        pytest.fail("dist/index.html is missing; run `make build` (or `make test`)")
    handler = functools.partial(QuietHandler, directory=str(DIST))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}/index.html"
    server.shutdown()


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        yield b
        b.close()


@pytest.fixture
def context(browser):
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    yield ctx
    ctx.close()


@pytest.fixture
def page(context, site) -> Page:
    pg = context.new_page()
    pg.errors = []
    pg.on("pageerror", lambda e: pg.errors.append(str(e)))
    pg.goto(site)
    pg.wait_for_function("window.QMG !== undefined")
    yield pg
    assert pg.errors == [], pg.errors


def open_link(pg: Page, site: str, payload: str) -> None:
    pg.goto(site + "#" + payload)
    pg.reload()
    pg.wait_for_function("window.QMG !== undefined")
    pg.wait_for_timeout(150)


def cell_center(pg: Page, x: float, y: float) -> tuple[float, float]:
    box = pg.locator("#board").bounding_box()
    scale = box["width"] / VIEW_W
    return (
        box["x"] + (MARGIN + x * CELL + CELL / 2) * scale,
        box["y"] + (MARGIN + y * CELL + CELL / 2) * scale,
    )


def click_cell(pg: Page, x: int, y: int, fx: float = 0.5, fy: float = 0.5) -> None:
    cx, cy = cell_center(pg, x, y)
    box = pg.locator("#board").bounding_box()
    scale = box["width"] / VIEW_W
    pg.mouse.click(cx + (fx - 0.5) * CELL * scale, cy + (fy - 0.5) * CELL * scale)


def pick_piece(pg: Page, slug: str) -> None:
    pid = pg.evaluate("(s) => QMG.CATALOG.find((c) => c.slug === s).id", slug)
    pg.click(f'#tools button[data-kind="piece"][data-value="{pid}"]')
    pg.evaluate("window.scrollTo(0, 0)")  # clicking a far-down palette button can scroll the page


def settle(pg: Page) -> None:
    """Wait for the debounced URL update to land."""
    pg.evaluate("QMG.syncUrl()")


def items(pg: Page) -> list[dict]:
    return pg.evaluate("QMG.app.state.items.map((i) => ({...i}))")


def piece_id(pg: Page, slug: str) -> int:
    return pg.evaluate("(s) => QMG.CATALOG.find((c) => c.slug === s).id", slug)
