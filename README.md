# Quest Map Generator

A browser-only editor for HeroQuest-style quest maps. The **whole quest lives in the link**: the
map, the pieces, the highlights, the quest number, title, intro, Zargon's secret notes and the
wandering monster. Nothing is saved and nothing is sent anywhere. Copy the address bar, send it to
someone, and they see exactly the same quest.

Because it's one static HTML file, it can be hosted anywhere (GitHub Pages, any web server, or just
opened from disk).

> **Status: first working version** on the standard 26 x 19 board with its 22 rooms. See
> [AGENTS.md](./AGENTS.md) for the decisions and plan and [docs/FORMAT.md](./docs/FORMAT.md) for the
> link format.

![A quest in progress, with the What's here panel](docs/screenshots/02-quest-in-progress.png)

## Quests to open in the live editor

The quests of **The Order of the Oth**, each stored entirely in its link:

| # | Quest | Notes |
|---|---|---|
| 1 | [The Stone Tablets of Uganoth](https://vibecoder-1z3r0.github.io/the-quest-map-generator/#Aa1WbW_jxhEmbclnrd59Pjcfimh0CAqeKgm54oACRfvhLkmvAdKekFxQ5B0rckguvNxld5dWVPg39Afk1wazXNm61m1RoAIMc8XZZ2aemXlG8fShTxxF0eT_cqCH-8MmHCb0fTfaxBFEk6j9dGMyCs9RvKHDhg4E0r7ptm_vzKJNRLDtlZPo_rCJjg5ROMSHA8XC2bT7-2n3Dxdn8Yuz-KobNyeXvz2Lr3r9q_jx306Sy07y-DR5fJJcnSVPzpMnneTqNPlFJ3mv232v1532uhcX8ee9eDo8G0zPBsPxX6bvT6fJaJSMx8lknExHyWicXA6TSzZ70ovZxbQ3jOV4Nhgng0kyGCXD8fvDSfx6Gn8wjD_ox0V_sDzvFL1ut9ftPer2B52o34163egi5uPO-NFX0zhmg_6vRsM5m52MZ6fj2elkdjL5Nh4uRr1k8Chh58mon_RZMj7_rjOas958xOaD_rw_mbPx7HF_Nh7N-uezcW92OpifDZPzSdIdJWfT5NEwOWHJaT_pDDrPL76eTr4Zjr5n_R-G51EUP__l2xLhC6cVwlu-legs6By-LLjSrvyp85lWBfBCL4FDrXdo8kbCTvydmwwUrzCDxSIYLxaQcnODGbjSIAJXqUDlwHpwF8BTrRwXSqgCXIlgMTXBZ8ULkYK3LXVTlA5ybQrtHKo5Y59CyW8QDKYCycdOG3LEHXDYcpURwmu9lULZJUjMYLv3DnLkRqK1YCXfo4HF4rOmQunjXULJLaByaHzUCJan9GgaoXxMi8VLWWjTZicUWOQmLemNK9Ei3KDZH1JbM_aVbqBqrIMbVK4xCEI57YEPZHjkJRh0hvIALqV_f1SB4wIsgVIz6BqjyK4Cp6FCytA6-mIPOUHc-dkZKljJVWbnjL3CHTe4hK0h7ko0Gu2SaPW2d1kecoRSywwyrgo0FnJuoDDIHZI5Vwd6gUutcP6PCXXO1giqVGEQFTjDawspV6C0gy1CJmyqb4jdNQCZU7BU-q3U6XWw5wbBGVEUvgptvlZLKnKNBpQ2FZdgGkmxZ7rF9vdr7sod39s1wEa4ACdUiMbjkk-ptYFC3JDjHd8vD97ssTN75GwN8GetrCOT4DBcCWX3ntaMvX2gZe7IJP-paSoirVgz9hJW8LYUFnJhrPPVoGqGlvJFMcht2zbgyNJoXUEuVGbbTPzF42E9apU1wOfIs_aiwh8d1Nw4KlaTwQqe7kpUsNcNOH6NUGtr0VqhVWjmAH48rN46R2w71MdiS7pMtN0xu4Qdl7LlMkXhy0tjpbQTKRIQpIan10TCU8ZewQq49dC6xpDnXeJpSX0tXCAOLTGU0UQZvEHuwbkKNxulULZcIRRGNyqDRmVoFHJXwq7E0AH_BL_jFhLvV1jgQYIg09o8o-Ck1SCR-3bZYilU5rXPBa7KEEZi0Dpt0MILkNo62OpsD7UWytlnjH0EK3j-4YdQ0EgRN5s7hD8FhF0p0hJ2QkoIWA9A0YWMV7zANWMfw6ol7L-3UNs1HJyutrAT1I9BgiQ6h4YC0C11W6GyltiM-pykUEPdkKw4yI2uWmksUeZrgC9rrSDTdMHq-87YYkED4DQY7pxEKrIH1_oaUm4RrBQZ2n8tJD2GIlInHTh_5_KasU9gBU0dQm6lrJXudpUcpuV-4u8jKsQNYe9D1R8UqEAigbU88to-WwO8VPuDt3em0su80VICh1RXW-4gEymuAT7NW2EOL-1102r83iuCpRz1DrN7za6F89zbJs_RwG_-TfmDgv5v4nFI0Dd65bdNOzZ-dUrkmWeIwjiY7smnlxQ07-rBkdgw9kdYwRuV4nE9_IqmmmLQocwLRC15ioCE7TzD-GOKtd_vcNjGIbEgLQoMaVkrXk9prXro3M84OZRcGIrncH3-1F9tPfmFu9WVUNzPXC6KxlAPHS9_dvtqc_vSOZ5e336MOSqLt1_UmAoub9kt_G61WsHD_9gtvID7v79SuHdpZIJ4QGh_STX088SWRuB1K5BeKp8DNRy1C6VQhLXqjqapRNImodZwy9jrA9NUvuqwmDwhW1p0Gea0pbMHOoSK3PYI2gf14T-X2QtHmM1WSLxkCQv-2k5YBKxqt18z9uvokry_MRmaw05548qfAQ) | The quest shown in these screenshots. |
| 2 | [The Parchment of Oaths](https://vibecoder-1z3r0.github.io/the-quest-map-generator/#AeVSsU7EMAzlJKabmJi9sZxu4BNgATEcEsfA6CbuJbo0qRznKjHy5ThpewufQJWhseP3np-9ufm33-bx_ugI3pGNGygKpB4OKC7_3L4QJ8o7wF6IIY8UrY8nMKlECZQzuFQ4gyXjR0dcc6JQH5IiwRG7QJIr3OcJYxK3g1dweCGwPpt0ISYLCM5bSxEGHLUYpdLguZVh1GN81YQsvkcjcI5p0nBuRH8177fbhUMYjeLXZw06td9nFDRp6Br-GzdRk0qnlmUa0MeWq9cxTcR9CTD5b2S7tgHBEyipwpBVwq9UYChZ4KLBolA-LmxmZdtBSHqhFeJB9WtcnY1WWYU9XWYJ47WlxZfJi_NRaZ6KQEcTMu2g49qiW8bTJ17k53ksJVpCO_sQkk6lI0WarVNpofBZRbaa7NCmaW0509VxhyHkve7HXd2OA1vdgOqyuF8) | Work in progress: the start of the quest. |

Or start from [a blank map](https://vibecoder-1z3r0.github.io/the-quest-map-generator/).

## Using it

1. Open the page (it starts as [a blank map](https://vibecoder-1z3r0.github.io/the-quest-map-generator/)). Choose a tool on the left, or pick a piece from the palette.
2. Click the board to place a piece. The address bar updates as you go, with no page reload.
3. Fill in the quest number, title, intro, notes and wandering monster on the right.
4. Copy the link (the **Copy link** button, or straight from the address bar) to share or bookmark
   the quest. Opening any link redraws the map.

### Board and pieces

- The board is the standard fixed board, with its rooms lettered A to V. Quests are made by placing
  pieces on it, not by drawing walls. Grey out the rooms a quest doesn't use.
- Pieces: doors, hidden doors, secret door tiles, wall tiles and double wall tiles, stairs, furniture, treasure chests, traps, monsters, heroes and
  numbered (1-9) and lettered (A-I) markers for pointing at things from your notes.
- Pieces can be **rotated** (`R`), **moved** (drag, arrow keys, or the buttons in the panel) and
  **removed** (`Del` or the Eraser). Several pieces can share a square. New pieces go on top, and
  the panel's *Bring forward* and *Send back* change the order.
- Doors are placed in a square and rotated onto the edge they sit on.
- Hover a square to see everything in it in the **What's here** panel (squares are labeled like
  `E8`). Click to pin the panel.

### Live quest sheet

Below the map and its legend, the quest is shown rendered (title, wandering monster, introduction
and Zargon's notes with their formatting), and it updates as you type in the Quest panel. It isn't
printed; the print page has its own layout.

### Room tiles

To merge rooms (as with a physical room tile laid over them), choose **Room tile** under *Room tiles*
and drag out a rectangle on the board. Tiles can be any size, are always rectangles, and sit
**under every piece**. Select a tile to move it (drag or arrow keys), or use the *What's here*
panel to change its width and height, reorder it among other tiles, or remove it.

### Quest stats

A **Quest stats** card (and the print page) summarises the quest, recalculated as you edit:
monsters on the map, total quest BP, the average BP per *active* room (a room with no grey square)
and per room that has monsters, the highest room, monsters in corridors (counted in the totals only),
and a breakdown by type. The wandering monster is shown separately and never counted. Rooms are
lettered A to V on the board. BP comes from each monster's body points in `src/catalog.json`. The Dread Warlock's body points vary
by quest, so it counts as a monster but its BP is left out, and the card says so.

### Highlights

Paint squares with a highlight color: grey for solid stone, orange for traps (of any kind), cyan,
yellow or bright green. Highlights tint whatever is underneath. Grey is always labeled "Solid stone"
and orange "Trap". Name the other colors in the legend editor ("cyan = secret room"); each used
color is listed beside the map.

### Quest text

- **Series** (optional, for example "The Order of the Oth"), **quest number** and **title**: plain
  text. The series shows above the title on the quest sheet and the print page.
- **Intro**: text for the heroes, with **bold** and *italics* only.
- **Zargon's notes**: your secret notes, with headings, bullet and numbered lists, bold, italics,
  rules and tables.
- **Wandering monster**: pick a monster, type something else, or leave both blank for none.
- A single new line is a line break. Extra blank lines add extra space.
- Only a small, safe set of characters is accepted. Anything else is removed.

### Undo, theme and printing

- **Undo / Redo** buttons (`Ctrl+Z` / `Ctrl+Y`) step through your edits. The browser's back and
  forward buttons work too.
- The editor opens in **light mode**. Switch to **dark mode** (or any later theme) for easier editing. The choice is
  stored in the link, so a shared link opens in the theme it was saved with. Printing never uses a dark
  theme: light themes print as themselves, and dark ones print in light.
- **Print** gives a one-page portrait sheet in the order of the official books: the map, the
  quest title, the introduction, Zargon's notes (if any), the wandering monster, then a compact key
  of the pieces and small quest statistics. Tick or untick **Print** next to a section's title to
  include or leave it out; **Monsters only** trims the key to the monsters. These choices are not
  stored in the link.

### Hero view

Hero view is a second way to look at the same quest, for playing it. The map starts hidden under a flat
fog and the heroes reveal it room by room. Everything is in the link: open a **hero link** and the page
opens in hero view.

![Hero view at the start](docs/screenshots/11-hero-start.png)

- **Playing.** Tap a room or hallway and press **Reveal** (it asks first). A revealed place shows its
  monsters, furniture and doors and its read-aloud text, and offers **Search for treasure**, **traps**
  and **secret doors**. Each search shows the text the author wrote for it, and the result stays. A
  secret-door search also reveals the secret doors that belong to that place. Traps are never drawn, and
  the site never rolls dice or decides whether a trap is sprung; that stays at the table. **Hide this room
  again** and **Reset game** (both ask first) fix a mistake. Your progress is kept in the link, so
  reloading or bookmarking it keeps your place, and there is no undo.
- **Zargon's view.** The **Zargon view** button in hero view asks first and warns that the secret notes
  and everything hidden become visible. In the editor, **Hero view** opens the quest in hero view and
  **Copy hero link** copies a link with nothing revealed.
- **Authoring.** Pin a square with the Select tool and the **Hero view data** card opens for its room (or
  pick a room or zone in the card). Give each room or zone a read-aloud text and treasure, trap and
  secret-door texts (600 characters each), tick *revealed at the start* for the starting place, and link
  rooms that should reveal together. Hallways are made with the **Hero view zones** palette: paint
  corridor squares with a zone and give the zone a name in the legend (heroes never see zone names).
  Any square, even solid stone or a trap highlight, can be in a zone.
- **Rules.** Doors are shown when either side is visible; markers and Zargon's highlight colors are never
  shown; hidden stone looks like any hidden area and shows once its room or zone is revealed.
- **No printing.** Hero view is for a device, so it does not print (print from Zargon's view instead).
- **Honor system.** Anyone with a hero link can read everything in it, including the hidden texts, by
  decoding it. Hero view hides things on screen; it does not protect them.

![The authoring card](docs/screenshots/14-hero-authoring.png)

### Heads up

- **Anyone with the link can read Zargon's secret notes**, because they are stored in the link.
  Only share a link with players if you are happy for them to see everything in it.
- Very long links may be cut off by some chat apps. A warning appears above about 2,000 characters.
- Needs a recent browser (about Chrome 103, Safari 16.4 or Firefox 113). Older browsers show a
  message with the minimum versions.

## Screenshots

These are generated by script (`make screenshots`) from the real editor, so they always match what
the tool does. They show [quest #1 in the live editor](https://vibecoder-1z3r0.github.io/the-quest-map-generator/#Aa1WbW_jxhEmbclnrd59Pjcfimh0CAqeKgm54oACRfvhLkmvAdKekFxQ5B0rckguvNxld5dWVPg39Afk1wazXNm61m1RoAIMc8XZZ2aemXlG8fShTxxF0eT_cqCH-8MmHCb0fTfaxBFEk6j9dGMyCs9RvKHDhg4E0r7ptm_vzKJNRLDtlZPo_rCJjg5ROMSHA8XC2bT7-2n3Dxdn8Yuz-KobNyeXvz2Lr3r9q_jx306Sy07y-DR5fJJcnSVPzpMnneTqNPlFJ3mv232v1532uhcX8ee9eDo8G0zPBsPxX6bvT6fJaJSMx8lknExHyWicXA6TSzZ70ovZxbQ3jOV4Nhgng0kyGCXD8fvDSfx6Gn8wjD_ox0V_sDzvFL1ut9ftPer2B52o34163egi5uPO-NFX0zhmg_6vRsM5m52MZ6fj2elkdjL5Nh4uRr1k8Chh58mon_RZMj7_rjOas958xOaD_rw_mbPx7HF_Nh7N-uezcW92OpifDZPzSdIdJWfT5NEwOWHJaT_pDDrPL76eTr4Zjr5n_R-G51EUP__l2xLhC6cVwlu-legs6By-LLjSrvyp85lWBfBCL4FDrXdo8kbCTvydmwwUrzCDxSIYLxaQcnODGbjSIAJXqUDlwHpwF8BTrRwXSqgCXIlgMTXBZ8ULkYK3LXVTlA5ybQrtHKo5Y59CyW8QDKYCycdOG3LEHXDYcpURwmu9lULZJUjMYLv3DnLkRqK1YCXfo4HF4rOmQunjXULJLaByaHzUCJan9GgaoXxMi8VLWWjTZicUWOQmLemNK9Ei3KDZH1JbM_aVbqBqrIMbVK4xCEI57YEPZHjkJRh0hvIALqV_f1SB4wIsgVIz6BqjyK4Cp6FCytA6-mIPOUHc-dkZKljJVWbnjL3CHTe4hK0h7ko0Gu2SaPW2d1kecoRSywwyrgo0FnJuoDDIHZI5Vwd6gUutcP6PCXXO1giqVGEQFTjDawspV6C0gy1CJmyqb4jdNQCZU7BU-q3U6XWw5wbBGVEUvgptvlZLKnKNBpQ2FZdgGkmxZ7rF9vdr7sod39s1wEa4ACdUiMbjkk-ptYFC3JDjHd8vD97ssTN75GwN8GetrCOT4DBcCWX3ntaMvX2gZe7IJP-paSoirVgz9hJW8LYUFnJhrPPVoGqGlvJFMcht2zbgyNJoXUEuVGbbTPzF42E9apU1wOfIs_aiwh8d1Nw4KlaTwQqe7kpUsNcNOH6NUGtr0VqhVWjmAH48rN46R2w71MdiS7pMtN0xu4Qdl7LlMkXhy0tjpbQTKRIQpIan10TCU8ZewQq49dC6xpDnXeJpSX0tXCAOLTGU0UQZvEHuwbkKNxulULZcIRRGNyqDRmVoFHJXwq7E0AH_BL_jFhLvV1jgQYIg09o8o-Ck1SCR-3bZYilU5rXPBa7KEEZi0Dpt0MILkNo62OpsD7UWytlnjH0EK3j-4YdQ0EgRN5s7hD8FhF0p0hJ2QkoIWA9A0YWMV7zANWMfw6ol7L-3UNs1HJyutrAT1I9BgiQ6h4YC0C11W6GyltiM-pykUEPdkKw4yI2uWmksUeZrgC9rrSDTdMHq-87YYkED4DQY7pxEKrIH1_oaUm4RrBQZ2n8tJD2GIlInHTh_5_KasU9gBU0dQm6lrJXudpUcpuV-4u8jKsQNYe9D1R8UqEAigbU88to-WwO8VPuDt3em0su80VICh1RXW-4gEymuAT7NW2EOL-1102r83iuCpRz1DrN7za6F89zbJs_RwG_-TfmDgv5v4nFI0Dd65bdNOzZ-dUrkmWeIwjiY7smnlxQ07-rBkdgw9kdYwRuV4nE9_IqmmmLQocwLRC15ioCE7TzD-GOKtd_vcNjGIbEgLQoMaVkrXk9prXro3M84OZRcGIrncH3-1F9tPfmFu9WVUNzPXC6KxlAPHS9_dvtqc_vSOZ5e336MOSqLt1_UmAoub9kt_G61WsHD_9gtvID7v79SuHdpZIJ4QGh_STX088SWRuB1K5BeKp8DNRy1C6VQhLXqjqapRNImodZwy9jrA9NUvuqwmDwhW1p0Gea0pbMHOoSK3PYI2gf14T-X2QtHmM1WSLxkCQv-2k5YBKxqt18z9uvokry_MRmaw05548qfAQ).

| | |
|---|---|
| ![Empty board](docs/screenshots/01-empty-board.png) **The empty board** | ![Dark mode](docs/screenshots/04-dark-mode.png) **Dark mode** (stored in the link) |
| ![Quest text](docs/screenshots/03-quest-text.png) **Quest text, previews and legend** | ![Print view](docs/screenshots/05-print-view.png) **Print view** (always light) |
| ![Hero view after revealing a room](docs/screenshots/12-hero-revealed.png) **Hero view**, a room revealed and searched | ![Hero view on a phone](docs/screenshots/13-hero-phone.png) **Hero view on a phone** |

On a phone the map comes first:

![Phone layout](docs/screenshots/06-phone.png)

## Hosting

- Merges to `main` publish the site to GitHub Pages using GitHub's official Pages actions.
- One-time setup: in the repository's **Settings, Pages**, set the source to **GitHub Actions**.
- To try a pull request's build, download the `dist` artifact from its CI run and open the single
  `index.html` in a browser.

## Known limitations

- **Statistics use the board's fixed rooms.** You can merge rooms by laying a room tile over them,
  but the statistics still treat them as the separate rooms printed on the board. Averages and the
  highest room are therefore per printed room, not per merged room.
- Only monsters placed on the map are counted. Reinforcements, summoned monsters and anything
  described only in the notes are not, and the wandering monster is never included.
- Every monster counts at its standard body points; there are no per-monster overrides.
- The board layout is fixed. There is no support for other boards or custom room shapes.

## Building and testing

The source lives in `src/`; `make build` combines it into one `dist/index.html`, which is what is
tested and published. Open `dist/index.html` directly, or use the hosted copy or the file attached
to a release.

First-time setup: `make setup` (Python only: installs the dev tooling and the Playwright
browser; there is no npm or Node).

```
make build   # build dist/index.html
make lint    # deno lint (JS), HTML check, ruff (Python)
make test    # run the Playwright tests against dist/index.html
make screenshots  # regenerate docs/screenshots/
make baselines    # regenerate the visual baselines (tests/baselines/)
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
