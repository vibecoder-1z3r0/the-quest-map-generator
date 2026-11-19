# Quest Map Generator

A browser-only editor for HeroQuest-style quest maps. The **whole quest lives in the link**: the
map, the pieces, the highlights, the quest number, title, intro, Zargon's secret notes and the
wandering monster. Nothing is saved and nothing is sent anywhere. Copy the address bar, send it to
someone, and they see exactly the same quest.

Because it's one static HTML file, it can be hosted anywhere (GitHub Pages, any web server, or just
opened from disk).

> **Status: under development.** The editor is being rebuilt around a fixed game board. See
> [AGENTS.md](./AGENTS.md) for the plan and [docs/FORMAT.md](./docs/FORMAT.md) for the link format.
> Screenshots are listed [below](#screenshots) and will be added when the new editor works.

## Using it

1. Open the page. Choose a tool on the left, or pick a piece from the palette.
2. Click the board to place a piece. The address bar updates as you go, with no page reload.
3. Fill in the quest number, title, intro, notes and wandering monster on the right.
4. Copy the link (the **Copy link** button, or straight from the address bar) to share or bookmark
   the quest. Opening any link redraws the map.

### Board and pieces

- The board is the standard fixed board. Quests are made by placing pieces on it, not by drawing
  walls.
- Pieces: doors and secret doors, stairs, furniture, treasure chests, traps, monsters, heroes and
  numbered markers for pointing at things from your notes.
- Pieces can be **rotated** (`R`), **moved** (drag, arrow keys, or the buttons in the panel) and
  **removed** (`Del` or the Eraser). Several pieces can share a square. New pieces go on top, and
  the panel's *Bring forward* and *Send back* change the order.
- Doors are placed in a square and rotated onto the edge they sit on.
- Hover a square to see everything in it in the **What's here** panel (squares are labeled like
  `E8`). Click to pin the panel.

### Highlights

Paint squares with a highlight color: grey for solid rock, orange (traditionally traps), cyan,
yellow or bright green. Highlights tint whatever is underneath. You can give each color a short
label ("orange = pit trap area") that is shown beside the map.

### Quest text

- **Quest number** and **title**: plain text.
- **Intro**: text for the heroes, with **bold** and *italics* only.
- **Zargon's notes**: your secret notes, with headings, bullet and numbered lists, bold, italics,
  rules and tables.
- **Wandering monster**: pick a monster, type something else, or leave both blank for none.
- A single new line is a line break. Extra blank lines add extra space.
- Only a small, safe set of characters is accepted. Anything else is removed.

### Undo, theme and printing

- **Undo / Redo** buttons (`Ctrl+Z` / `Ctrl+Y`) step through your edits. The browser's back and
  forward buttons work too.
- The editor opens in **light mode**. Switch to **dark mode** for easier editing. The choice is
  stored in the link, so a shared link opens in the theme it was saved with. Printing is always
  light, whichever mode you are in.
- **Print** gives a clean page with the map, the intro, the notes and the wandering monster.

### Heads up

- **Anyone with the link can read Zargon's secret notes**, because they are stored in the link.
  Only share a link with players if you are happy for them to see everything in it.
- Very long links may be cut off by some chat apps. A warning appears above about 2,000 characters.
- Needs a recent browser (about Chrome 103, Safari 16.4 or Firefox 113). Older browsers show a
  message with the minimum versions.

## Screenshots

Screenshots will be generated from the real editor, by script, once the rebuilt editor works, so
they always match what the tool actually does. Planned set:

- the empty board
- a quest in progress (pieces, highlights and the *What's here* panel)
- the quest text panels
- the same quest in dark mode
- the print view

## Building and testing

The source lives in `src/`; `make build` combines it into one `dist/index.html`, which is what is
tested and published.

```
make build   # build dist/index.html
make lint    # ESLint, html-validate, ruff
make test    # build, then run the Playwright tests against dist/index.html
make check   # lint + test (what CI runs)
make clean   # remove dist/
```

Every piece's artwork is a separate SVG in `src/icons/`. To use your own, put a same-named file in
`icons-custom/`; the build prints which file it used for each piece.

## Notice

This is an unofficial, free fan-made tool, a labor of love for the HeroQuest community. It is not
affiliated with, endorsed by or sponsored by Hasbro, Inc. or any other owner of the game. HeroQuest
and all related names, characters, marks and artwork are trademarks or copyrighted works of their
respective owners, used only for identification; no infringement is intended. All artwork in this
tool was created with AI assistance and is not copied from official art.

## License

[MIT](./LICENSE)
