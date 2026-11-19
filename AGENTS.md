# Quest Map Generator — Agent Guide

A browser-only, static HTML5 quest map editor for HeroQuest-style quests. The **entire map and all
quest text live in the URL hash**; nothing is saved, no server, no storage. Any link regenerates the
map. It can be hosted anywhere static.

> Status: first working version on a **placeholder board**. The rebuilt editor, `make` build, lint,
> tests (golden links, hostile-input, visual baselines) and CI are in place. Still to come: the real
> board layout, the open-wall mechanism (the current "Open wall" piece is provisional), verified
> furniture footprints, and the release and Pages setup in the GitHub repository settings.

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
- Commit and push only when asked.

## Architecture and tooling

- Source in `src/`: `index.html` template, `style.css`, JS modules (encoding, rendering, UI,
  markdown), `catalog.json`, `board.svg`, `icons/`. No bundler, no runtime dependencies.
- `make build` inlines CSS, JS, the icon sprite, the board and the catalog into a **single
  `dist/index.html`**. That file is what is tested and what is published.
- Make targets: `build`, `lint`, `test`, `check` (lint + test, what CI runs), `clean`. No `make serve`.
- Lint: ESLint (JS), html-validate (HTML), ruff (Python); Prettier check optional.
- Tests: pytest + Playwright (Python) against `dist/index.html`, served by a throwaway HTTP server in
  a fixture (matches Pages). Prefer DOM/SVG assertions; a few board-only screenshot baselines
  (committed, generated in the CI container, small tolerance); full-page and mobile screenshots are
  CI artifacts only. Unit tests for the encoder, markdown parser and character filter.
- **Golden links**: committed known URLs per format version that must keep decoding to the expected
  map.
- CI (GitHub Actions): `make check` on every PR/push. Merge to `main` deploys `dist/index.html` to
  GitHub Pages only if green. A `v*` tag attaches `dist/index.html` to a GitHub Release. The build
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
- Decode defensively: bounds-check everything, cap total decompressed size at 64 KB, reject oversized
  fields, and show a banner then start blank on any failure.

## Board, pieces and layers

- The board is a **fixed 26×19 background** with rooms and thick wall borders already drawn
  (`src/board.svg`, replaceable). The layout will be supplied by the owner; use a placeholder 26×19
  grid until then. There is no floor painting and no derived walls.
- Everything placed is an item record **`[icon index, x, y, rotation]`**, rotation 0–3. `x, y` is the
  top-left square of the piece's footprint. A rotation swaps width and height.
- Doors and secret doors are 1×1 pieces; the door art sits on the north edge at rotation 0 and
  rotation selects the edge. Doors on outer board edges are allowed.
- Merging two rooms is done with a piece that covers a wall (an "open wall" edge piece and/or
  floor-colored overlay tile). Exact mechanism pending the owner's input.
- **Z-order = list order**; later records draw on top. A new piece is always appended on top. Panel
  buttons (Bring forward, Send back) reorder any piece past any other. Any number of pieces may share
  a square; the editor refuses only an exact duplicate.
- **Highlights**: 4 bits per square, drawn as a translucent tint over whatever is beneath. `0` none,
  `1` grey (solid rock, with a faint hatch), `2` orange, `3` cyan, `4` yellow, `5` bright green; `6–15`
  reserved. Numbers are permanent. Orange is generic (historically traps). Optional per-color legend
  labels are stored in the URL and shown beside the map.
- `catalog.json` gives each piece a **permanent numeric ID (never reused, max 255)**, name, group,
  footprint (default orientation), and icon slug. IDs go in the URL, never filenames.
- Base-game pieces (footprints from memory — **verify**): stairs 2×2, table 3×2 (2×3 rotated),
  tomb 3×2?, bookcase 3×1, cupboard 3×1?, fireplace 3×1, throne 1×1, weapons rack 3×1, alchemist's
  bench 3×2?, sorcerer's table 3×2?, torture rack 3×2?, treasure chest, pit/spear/falling-rock traps,
  rubble (the fallen rock tile, distinct from the falling rock trap), door, secret door. Monsters:
  goblin, orc, abomination, skeleton, zombie, mummy, gargoyle, dread warrior. Heroes: barbarian,
  dwarf, elf, wizard. Editor extras: numbered markers 1–9. Chaos Warrior is out. More can be added
  later.

## Quest text

- Quest number (plain, max 10), quest title (plain, max 160), intro (bold/italics only, max 2,500),
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
- Place, select, **drag-to-move** (keeps rotation and stack position), panel move buttons and arrow
  keys, `R` rotate, `Del` remove, Highlight tool, Eraser. Clicking a stacked square selects the top
  piece, clicking again cycles down.
- In-page **Undo/Redo** with its own history stack (Ctrl+Z / Ctrl+Y); typing is one step per pause.
  Browser back/forward also work. Opening a link starts a fresh stack.
- Touch: pinch-zoom and pan. Print view with the map, intro, notes and wandering monster.
- Footer notice (below) and MIT license line.
- README screenshots are generated by script from the real editor (Playwright, a `make` target) into
  `docs/screenshots/`; never commit screenshots of a superseded UI.

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

- Board layout from the owner; how rooms were merged (open-wall piece vs overlay tile).
- Verify piece footprints and names, minimum browser versions, and the 160-char wandering-monster limit.
- Planned order: (1) `src/` restructure, `Makefile`, lint, CI; (2) new data format + golden links;
  (3) editor (fixed board, stacking, drag, panel, undo/redo); (4) markdown + character allowlist;
  (5) chibi style sample, then full icon set; (6) footer/notice, README, Pages deploy.

## Future development (tabled — do not build yet)

- **Fog of war mode.** Someone sends a link and the recipient reveals parts of the map as they play
  through. Not part of v1; the format and UI should not be bent to accommodate it yet. Questions to
  settle when it is picked up: where the revealed state lives (it should stay in the URL, with no
  storage), how Zargon's secret notes and hidden pieces are kept out of a player-facing link
  (everything in a link is readable by anyone who has it), and how reveals relate to the highlight
  layer.
