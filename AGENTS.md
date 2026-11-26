# Quest Map Generator — Agent Guide

A browser-only, static HTML5 quest map editor for HeroQuest-style quests. The **entire map and all
quest text live in the URL hash**; nothing is saved, no server, no storage. Any link regenerates the
map. It can be hosted anywhere static.

> Status: working editor on the **real board layout** (22 rooms) with quest statistics. The `make`
> build, lint, tests (golden links, hostile-input, visual baselines) and CI are in place. Still to
> come: verified furniture footprints, and the release and Pages setup in the GitHub
> repository settings.

## Git conventions

- **Never put a `claude.ai/code/session_...` link anywhere** — commits, PR text, files. Hard rule.
- [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `docs:`, `build:`,
  `ci:`, `test:`, `refactor:`, `chore:`, optional scope, imperative mood.
- Same commit format as the owner's `many-game-show` project. Every commit body ends with:

  ```
  This work was substantially AI-generated with human review and
  direction throughout.

  Vibe-Coder: Vibe-Coder 1.z3r0 <243014891+vibecoder-1z3r0@users.noreply.github.com>
  Co-authored-by: Vibe-Coder 1.z3r0 <243014891+vibecoder-1z3r0@users.noreply.github.com>
  Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
  ```
- Develop on `claude/clever-rubin-2bpoj7`; push with `git push -u origin <branch>`.
- Don't open a PR unless asked. Don't force-push without being told to (`--force-with-lease` only).
- Commit and push only when asked. Every commit includes a fresh `SESSION_LOG.md` (`make session-log`).

## Architecture and tooling

- Source in `src/`: `index.html` template, `style.css`, JS modules (encoding, rendering, UI,
  markdown), `catalog.json`, `board.svg`, `icons/`. No bundler, no runtime dependencies.
- `make build` inlines CSS, JS, the icon sprite, the board and the catalog into a **single
  `dist/index.html`**. That file is what is tested and what is published.
- Make targets: `build` (always rebuilds), `lint`, `test` (both reuse the built page and only rebuild
  it if it is missing or older than the sources), `clean`. There is no umbrella target and no
  `make serve`.
- **No npm, no Node.** All tooling is Python-installable (`pip install -e '.[dev]'`). Lint: `deno lint`
  (the Deno binary from PyPI, configured in `deno.json`) for JS, `scripts/lint_html.py` (strict html5lib
  parse, unique ids, references) for HTML, ruff for Python. Tests use Playwright for Python.
- Tests: pytest + Playwright (Python) against `dist/index.html`, served by a throwaway HTTP server in
  a fixture (matches Pages). Prefer DOM/SVG assertions; a few board-only screenshot baselines
  (committed, generated in the CI container, small tolerance); full-page and mobile screenshots are
  CI artifacts only. Unit tests for the encoder, markdown parser and character filter.
- **Session log**: `scripts/session_timing.py` (from many-game-show) writes `SESSION_LOG.md`, a
  turn-by-turn timing and token report of the session. A **pre-commit hook** (`scripts/hooks/pre-commit`,
  enabled by `make setup` via `core.hooksPath`) runs `make session-log` and stages the result, so every commit
  carries a fresh log. If the hook is not active in a checkout, run `make session-log` before committing. The
  header note lives in `scripts/session_log_header.md`.
- **Golden links**: committed known URLs per format version that must keep decoding to the expected
  map.
- CI (GitHub Actions) runs `make build`, `make lint` and `make test` as separate steps, in that
  order, on every PR/push. A merge to `main` deploys `dist/index.html` to
  GitHub Pages **with GitHub's official `actions/upload-pages-artifact` and `actions/deploy-pages`**,
  only if green. The repository's Pages source must be set to **GitHub Actions**. There are no PR
  previews (the official action replaces the whole site, so it cannot host per-PR folders); every CI
  run uploads the built page as a downloadable `dist` artifact instead. **Only GitHub's own actions
  (`actions/*`) are allowed, plus plain `git` and the preinstalled `gh` CLI; never third-party
  actions** (a test enforces it). A `v*` tag attaches `dist/index.html` to a GitHub Release. The build
  stamps a version/commit string in the footer.
- Browser support: recent evergreen only. Feature-detect `CompressionStream`/`DecompressionStream`
  (`deflate-raw`) and show a banner with minimum versions (about Chrome 103, Safari 16.4, Firefox 113 —
  verify against current compat data before shipping) and disable the editor otherwise. No polyfill.

## URL format

`docs/FORMAT.md` is the normative byte-level spec; keep it and the code in sync.

- Hash (`#...`), not query string, so nothing reaches a server log.
- Payload = `[version byte] + deflateRaw(body)`, base64url. Body holds the highlight layer, the item
  list and the text fields. Version byte allows forward evolution.
- **No normalization**: the link records exactly what was placed.
- The format may change freely until the first tagged release; after that only versioned, additive
  changes, and old links must keep decoding (golden-link tests enforce this).
- Show live link length; warn (message only, never block copying) above about 2,000 characters.
- Decode defensively: bounds-check everything, cap total decompressed size at 256 KB, reject oversized
  fields, and show a banner then start blank on any failure.

## Board, pieces and layers

- The board is a **fixed 26×19 background**. Its single source of truth is **`src/board.txt`**: one
  character per square (`.` corridor, `A`-`Z` a room, `#` solid). The build generates the board art
  (walls wherever neighboring squares differ, tinted rooms) and the room map the statistics use. To
  replace only the art, drop `board.svg` in `icons-custom/`; the room map still comes from
  `board.txt`. The layout was traced from the owner's photo of the board (the photo and official art
  are not in the repo). There is no floor painting. Rooms are lettered A-Z in reading order.
- Everything placed (except room tiles) is an item record **`[icon index, x, y, rotation]`**, rotation 0–3. `x, y` is the
  top-left square of the piece's footprint. A rotation swaps width and height.
- Doors and **hidden doors** are 1×1 edge pieces (catalog `edge: true`); the art sits on the north edge
  at rotation 0 and rotation selects the edge. Doors on outer board edges are allowed. The **secret
  door** is a separate 1×1 rotatable *tile* piece (id 4, not an edge piece), as in the physical game;
  the former "secret door" frame (id 2) was renamed Hidden door and keeps its permanent id.
- Merging two rooms is done by placing a **room tile**, as with the physical game. Tiles are
  **resizable rectangles** stored in their **own `tiles` list** in the link (`[tile id, x, y, width,
  height]`, see `docs/FORMAT.md` section 4.3), never in the piece list. Tile styles are catalog
  entries marked `"tile": true` (1x1 icon repeated across the rectangle; today only "Room tile",
  id 100). Tiles are always drawn **below every piece**; list order only orders tiles among
  themselves. Tools: drag a rectangle with the Room tile tool; width/height fields in the panel. The
  statistics deliberately keep the board's **fixed rooms**, so merged rooms still count as their
  printed rooms (documented limitation in the README). The old provisional "Open wall" piece is gone.
- **Z-order = list order**; later records draw on top. A new piece is always appended on top. Panel
  buttons (Bring forward, Send back) reorder any piece past any other. Any number of pieces may share
  a square; the editor refuses only an exact duplicate.
- **Highlights**: 4 bits per square, drawn as a translucent tint over whatever is beneath. `0` none,
  `1` grey (solid stone, with a faint hatch), `2` orange, `3` cyan, `4` yellow, `5` bright green; `6–15`
  reserved. Numbers are permanent. Orange means a trap of any kind (default legend text "Trap"). Grey is
  always "Solid stone" with no editable legend. In the palette, Grey sits in its own **"Solid stone
  areas"** section directly above "Doors & walls" (the button is still called "Grey"); the Highlight
  section keeps Clear, Orange, Cyan, Yellow and Bright green. Colors 2-15 may carry an optional editable label stored
  in the URL; the legend beside the map lists each color that is used on the map.
- `catalog.json` gives each piece a **permanent numeric ID (never reused, max 255)**, name, group,
  footprint (default orientation), icon slug, and **the set it comes from** (`"set"`, an id from
  `src/sets.json`; everything is currently `base`, "Base game"). Sets are static data, not in the
  link, and every piece must name a known set (the build and tests enforce it). IDs go in the URL,
  never filenames.
- **Expansion pieces go in their natural palette group, never in a group of their own.** A new
  monster belongs in "Monsters", new furniture in "Furniture", and so on; the `set` field records
  where it came from (and drives the tabled palette filter). Never name a group after a set. The
  palette lists a group's pieces in `catalog.json` order, so insert a new piece next to related ones
  (file order is independent of the permanent numeric id); the test suite enforces the group rule.
- Base-game pieces (footprints from memory — **verify**): stairs 2×2, table 3×2 (2×3 rotated),
  tomb 3×2?, bookcase 3×1, cupboard 3×1?, fireplace 3×1, throne 1×1, weapons rack 3×1, alchemist's
  bench 3×2?, sorcerer's table 3×2?, torture rack 3×2?, treasure chest, pit/spear/falling-rock traps,
  rubble (the fallen rock tile, distinct from the falling rock trap), door, hidden door, wall tile
  (1×1, id 5) and double wall tile (2 wide × 1 high, id 6; both from the owner, plain rotatable pieces
  in Doors & walls, id 3 stays retired), secret door
  tile. Monsters:
  goblin, orc, abomination, skeleton, zombie, mummy, gargoyle, dread warrior, dread warlock (the spell
  caster; BP varies by quest). Heroes: barbarian,
  dwarf, elf, wizard; plus the expansion heroes bard, warlock, druid, berzerker, explorer, commander
  of the guardian knights, rogue heir of elethorn and wandering monk. Those eight are **really
  expansion heroes but are tagged `base` for now** (owner's call); re-tag them when the real set
  names are known. "Berzerker" is spelled as the owner wrote it. Editor extras: numbered markers 1–9 (ids 80-88) and lettered markers A–I (ids 89-97, teal). Chaos Warrior is out. More can be added
  later.

## Quest statistics (derived, never stored in the link)

Shown in a "Quest stats" card and on the print page. Every monster counts at its catalog `bp`
(body points; from the owner: Goblin, Orc, Zombie, Skeleton 1; Abomination and Mummy 2; Gargoyle and
Dread Warrior 3, where the Abomination is the Fimir and the Dread Warrior is the Chaos Warrior of the
source tables). `bp: null` means not set yet (a future monster), and the card then shows "n/a" and
names the monsters without a value (never guess a BP). The **Dread Warlock's BP varies by quest**
(`bp: null` with `bp_varies: true`): it counts as a monster, its BP is left out of every BP figure,
and the card notes "BP not included (varies by quest)" instead of going n/a.
- Monsters on the map and total quest BP (corridor monsters included).
- Average BP over **active rooms** (a room with no grey square at all) and over **rooms that contain
  monsters**; highest room BP (ties listed). Empty rooms count as 0 in the active average.
- Monsters standing in corridors are in the totals only, and get their own "In corridors" line.
- The wandering monster is **never counted**; it has its own line (BP shown if a monster is picked).
- Not counted by design: off-map or reinforcement monsters, and per-monster BP overrides.
- A per-type breakdown ("2 Goblins, 1 Mummy").

## Hero view

A second view of the same link for playing a quest (`docs/HERO_VIEW.md` has the full rules and the
decisions behind them; `docs/FORMAT.md` 4.7 and 4.8 the bytes). The view flag is bit 4 of the flags byte.
- **Regions** are the board's rooms (A-Z are regions 0-25) and ten **zones** (regions 26-35). Zones are
  a separate per-square layer (not highlights), painted with the Hero view zones palette, so any square
  can be in a zone; zone names are legend entries 6-15 and are never shown to heroes. `src/js/hero.js`
  holds the pure rules (regions, groups, reveal/hide/search/reset, visibility, secret door ownership,
  merged texts) and is exposed to tests as `QMG.hero`.
- Per region (optional records): revealed at the start, a group (regions with the same group reveal
  together), and four texts of up to 600 characters: read aloud, treasure, traps, secret doors.
- **Play state** (revealed and searched regions) lives in the link, 20 bytes, and replaces the start
  state once present. Play changes the link in place (`replaceState`): no history entries and no undo.
  A quest without hero data keeps exactly the link it always had.
- Hero view hides: markers, trap pieces, Zargon's highlight colors, secret and hidden doors until their
  owner's secret-door search, and everything in a hidden room or zone. One flat opaque fog covers hidden
  squares (solid stone included, shown only once its region is revealed); doors show if either side is
  visible; squares in no region stay visible. Zargon's notes are never shown; the quest text, intro and
  wandering monster are.
- Hero controls: tap a region, **Reveal** / **Hide this room again** / **Reset game** each confirm in a
  dialog; **Zargon view** confirms with a warning. Editor: a collapsible card follows the pinned square
  (never the hover) with a region chooser, groups and counters; **Hero view** and **Copy hero link**
  (always a clean play state) are in the header.
- Hero view **never prints** (it is for a device): in print media it shows only a short note, because the
  print layout holds Zargon's notes and the whole map. Print from Zargon's view.
- It is an honor system: everything in a link is readable by anyone who decodes it.

## Quest text

- Series (optional, plain, max 160; shown above the title on the sheet, print page and tab title; an
  optional *trailing* field in the link so older links still decode), quest number (plain, max 10),
  quest title (plain, max 160), intro (bold/italics only, max 2,500),
  Zargon's secret notes (max 10,000), and a wandering monster (monster picker + free text ≤160;
  both blank means none).
- Notes support a small markdown subset: `#`/`##`/`###` headings, bullets, numbered lists, bold,
  italics, `---` rule, pipe tables, backslash escapes. No raw HTML, images or links; no nested lists.
- A single newline is a line break; extra newlines add vertical space (each beyond the first adds a
  blank line). Applies on screen and in print.
- **Character allowlist**: letters and digits (any script), space, newline, and
  `. , ! ? ' " : ; ( ) [ ] - * # | & \ / + _`. Curly quotes, en/em dashes and the ellipsis are
  normalized to ASCII equivalents; everything else (including `< > `` % = ~ @ $ ^`, control
  characters and invisible/bidi Unicode) is removed. Applied on input, paste and on every decode, to
  all text fields; a banner notes when characters were stripped.
- **Render user text only via `textContent`/DOM nodes, never `innerHTML`.** Use our own tiny parser,
  no markdown library. Tests feed hostile strings (`<script>`, `<img onerror>`, bidi overrides,
  decompression bombs) through links.

## Editor UI

- **Light theme by default, with a dark mode and room for more themes (ids 0-15) for editing.** Printing **never uses a dark
  theme**: each theme declares whether it is print-safe (light); print-safe themes print as
  themselves, others print with the default light theme (enforce in `@media print`). The theme is stored in the URL (theme id in the flags
  byte, `docs/FORMAT.md`); toggling it updates the hash but is not an undo step.
- "What's here" panel: hover shows, click/tap pins. Lists everything in the square top to bottom
  (pieces with footprint, anchor, rotation; the highlight) with Bring forward, Send back, Rotate,
  Move and Remove. Board-style coordinates (column letter + row number), e.g. `E8`.
  **The panel follows the selected piece**: moving it (panel buttons, arrow keys, drag) or rotating it re-pins
  the panel to the piece's new square, so it never loses the piece. Placing a piece selects it and leaves the Place
  tool active (bulk placing needs no trips to the palette). The hover preview and square highlight only show for
  a mouse or pen, never for touch.
- Place, select, **drag-to-move** (keeps rotation and stack position), panel move buttons and arrow
  keys, `R` rotate, `Del` remove, Highlight tool, Eraser. **`Esc` cancels any tool in progress (even a
  tile being dragged out) and returns to the Select tool with nothing selected or pinned.** Clicking a stacked square selects the top
  piece, clicking again cycles down.
- In-page **Undo/Redo** with its own history stack (Ctrl+Z / Ctrl+Y); typing is one step per pause.
  Browser back/forward also work. Opening a link starts a fresh stack.
- Touch: pinch-zoom and pan.
- **Single-column layout** (screens up to 1000px wide, no device sniffing): the map and its highlight legend, then
  the What's here panel, then the palette, then the quest sheet, then the other side cards. The zoom buttons and
  the keyboard shortcut line are hidden at these widths (pinch-zoom and touch cover them).
- **Header**: two rows. Row 1: app name and build (and a HERO VIEW badge in hero view), Theme, the quest
  line (`Series: Quest N - Title`, blank parts dropped, truncated with a tooltip), Copy map link and Copy hero
  link, then Hero view, Undo, Redo, Print and New map on the right (in hero view: Zargon view and Reset game
  instead). Row 2: the link length and the privacy note ("Anyone with the link can read Zargon's secret
  notes"). The keyboard shortcut line sits under the zoom controls above the map.
- **Print view (portrait, one page for a typical quest), in the order of the official books:** the
  map (row/column markings hidden in print), then series and title, the introduction (no heading),
  Zargon's notes (only when there are any), the wandering monster, then a compact piece key and very
  small statistics (about 8pt). Each printable section has a **Print checkbox next to its title**
  (Introduction, Pieces on this map with a "Monsters only" option, Quest stats, Highlight legend,
  Zargon's notes). These choices are not stored in the link (the flags byte has spare bits if that
  is ever wanted).
- Footer notice (below) and MIT license line.
- **Send the owner screenshots whenever the UI changes** (`make screenshots`, then show the relevant
  images in the reply). Don't just regenerate them silently.
- README screenshots are generated by script from the real editor (Playwright, a `make` target) into
  `docs/screenshots/`; never commit screenshots of a superseded UI. The showcase is **the owner's
  quest #1** (the link in `docs/showcase/quest-1.txt`); `scripts/screenshots.py --sample` uses the
  built-in invented sample instead. Tests keep their own fixtures and never depend on the showcase.

## Icons and art

- **Chibi style**, drawn as simple SVG shapes: big head, small body, bold outline, flat fills, few
  palette colors via CSS variables; must print well in black and white.
- One SVG per piece: `src/icons/<group>/<slug>.svg`, filename = slug, `viewBox` = `w*32 × h*32` of the
  default footprint, `<title>`/`<desc>` naming the piece and size, a header comment. Rotation is a
  transform on the `<use>`; each icon is drawn once.
- Users override icons by dropping a same-named file in `icons-custom/` (wins over defaults).
  `make build` prints a table of piece → slug → file → default/custom; a missing or malformed icon
  **fails the build** (no silent fallback).
- Tests: every catalog entry has an icon and vice versa, IDs unique and stable, each `viewBox`
  matches its footprint.
- Do style samples first (Barbarian, Goblin, table) for owner approval before the full set.
  Document the style rules in `src/icons/README.md`.
- The art is AI-generated. Do not copy or trace official artwork. Don't claim stronger rights than
  MIT's permissions.

## Licensing and notice

Repo is MIT. Footer and README carry a notice along these lines:

> Unofficial, free fan-made tool, a labor of love for the HeroQuest community. Not affiliated with,
> endorsed by or sponsored by Hasbro, Inc. or any other owner of the game. HeroQuest and all related
> names, characters, marks and artwork are trademarks or copyrighted works of their respective
> owners, used only for identification; no infringement is intended. All artwork was created with AI
> assistance and is not copied from official art. Released under the MIT License.

## Open items

- Additional room tile styles, if wanted (only the plain "Room tile" exists).
- **Renumber the catalog ids once, right before the first tagged release (owner's decision).** Ids
  are cosmetic (palette and key order come from `catalog.json` file order), so this is optional
  tidying, and it is only allowed in the window before the first `v*` tag, when the format may still
  change freely. Plan: write a one-off script that decodes the owner's quest link, remaps old ids to
  new ones and re-encodes it; then in one commit update `catalog.json`, `tests/catalog_ids.json`, the
  golden links, `tests/reference.py`, `docs/FORMAT.md` examples, `docs/showcase/quest-1.txt` and the
  README links. Save the old link first (it will stop decoding). After the first tag, ids are frozen.
- Re-tag the eight expansion heroes once the real set names are known.
- Verify piece footprints and names, minimum browser versions, and the 160-char wandering-monster limit.
- Planned order: (1) `src/` restructure, `Makefile`, lint, CI; (2) new data format + golden links;
  (3) editor (fixed board, stacking, drag, panel, undo/redo); (4) markdown + character allowlist;
  (5) chibi style sample, then full icon set; (6) footer/notice, README, Pages deploy.

## Future development (tabled — do not build yet)

- **Palette filtering by name and set.** A search box plus checkboxes per set (from `src/sets.json`)
  to filter the piece palette. Deliberately not built yet because it would add noise while there is
  only one set; the per-piece `set` data is already in place for it.
- **Object export / import (JSON) for durable backups.** A file the owner downloads and can load
  back, readable and independent of the compact binary link, so a breaking link-format change
  never strands a quest. Tabled for now: the owner is the only holder of real links and is fine
  remaking a quest after a breaking change, so the link plus a saved copy of it is the backup until
  then. Design when it is picked up:
  - **Buttons:** Export (downloads a `.json` file) and Import (file picker or pasted text) in the top
    bar. Importing replaces the current map after a confirm and is one Undo step. The file is an
    explicit save the owner chooses; the app still stores nothing by itself.
  - **Schema number with explicit migrations** for every older schema, plus **committed example
    exports per schema** checked by tests (like the golden links).
  - **Reference pieces by both permanent id and readable name** and have import trust the id. Names
    can change or be reused (the old "secret door" frame became "Hidden door" and "secret door" now
    means the new slab tile), so a name alone could land on the wrong piece. Never reuse a slug for a
    different piece.
  - **Same safety as the link:** the character filter and limits, a file size cap, unknown pieces
    skipped with a warning, nothing from the file ever executed.
  - Record the board (for example `"board": "standard-26x19"`) in case other boards ever exist.

  ```json
  {
    "format": "quest-map-generator",
    "schema": 1,
    "board": "standard-26x19",
    "theme": "light",
    "series": "The Order of the Oth",
    "number": "1",
    "title": "The Stone Tablets of Uganoth",
    "intro": "Long ago, a powerful wizard named **Uganoth** ...",
    "notes": "",
    "wandering": { "piece": "skeleton", "id": 43, "text": "" },
    "pieces": [
      { "piece": "goblin", "id": 40, "x": 5, "y": 5, "rotation": 0 },
      { "piece": "door", "id": 1, "x": 21, "y": 5, "rotation": 2 }
    ],
    "tiles": [
      { "style": "room-tile", "id": 100, "x": 4, "y": 10, "w": 2, "h": 3 }
    ],
    "highlights": [
      "gg........................",
      "..........................",
      "..........................",
      "..........................",
      "..........................",
      "..........................",
      "..........................",
      "..........................",
      ".....c....................",
      "..........................",
      "..........................",
      "..........................",
      "..........................",
      "..........................",
      "..........................",
      "..........................",
      "..........................",
      "..........................",
      ".........................."
    ],
    "legend": { "cyan": "secret room" }
  }
  ```

  (`highlights` is 19 rows of 26 characters like `board.txt`: `.` none, `g` grey, `o` orange,
  `c` cyan, `y` yellow, `l` bright green.)
