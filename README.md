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
| 1 | [The Stone Tablets of Uganoth](https://vibecoder-1z3r0.github.io/the-quest-map-generator/#AdVXW28bRRj1Jt4kXt_TtPCA8LhCaBrSikIlJAQP5VaQgFpQhLhrdne8u8p6x8zOxjXKT-mP5XwzY8eFFHhAQqySeMfzXc_5Lm0wvu4JWq3W6F850MvVYeYPI_o-bM2CFmuNWu4JAxLy761gRocZHciIuwnd7VYM92TWqey1rg6z1s6h5Q_B5kCxiGgcvjcO3z8-CB4cBLfCoNk7eQcvne6t4Mave_ykzW_s8xt7_NYBv3nEb7b5rX3-Upu_HIYvd8JxJzw-Dr7qBOP-QW980OsPvxy_Oh7zwYAPh3w05OMBHwz5SZ-fRJObnSA6Hnf6QTmc9Ia8N-K9Ae8PX-2Pgkfj4LV-8Fo3yLq9s6N21gnDTtg5DLu9dqsbtjph6zgQw_bw8LtxEES97uuD_jSa7A0n-_gZTfZGPwb900GH9w55dMQHXd6N-PDop_ZgGnWmg2ja6067o2k0nNzoToaDSfdoMuxM9nvTgz4_GvFwwA_G_LDP9yK-3-XtXvv-8ffj0Q_9wc9R95f-Eci6_8qTXLKvjaokeyLiUpqaqTn7JhOVMvmz9ueqypjI1BkTbKlWUs-bkq2K34ROWSUWMmWnp1749JQlQl_gK5NrKZmokkJWhtXWuPHGE1UZUVQFzBp4rmWivc-FyIqEqSqBcK6aLDdsrnSmjJHVNIo-Y7m4kEzLRBbkZKU0eRIGkcWiSsnEIxWXRVWfsRIC8dp6mEuhS1nXrC7FWmrE-3mzkKUN-Aw2a4YgpbZhIx6R0KtuYIYsnp4-LDOlXXpFhXiFTnK6gXQt2YXU601u96LoO9WwRVMbfF-ZRkuoGGUNb9Cwls-QhtGFRD6iLO39iygA8MgN4o2uSHDBYHAhKUW4wRdrNicbW0crTZTl0KqB2gdyJTSkY03g5VIrCe_A1cpu09wkyXJVpiwVVSZ1DcOaZVoKwENIVxt8ETSCnT4bUe3EuiCqICcRoBZLcAxRxM5iydKiTtQFwXuPMRKnYIn8uFTJuZdHhHgrsszS4PKtVUksL-G6UnohSgRbUuypcrat_lKYfCXWNYzPCuPNgSYXjbVLPkuFhLPighxD_Gzjrd51Vu84g70vVFUbEvEOvYrn3XoC4U-uqZktmOQ_0c2CQMsg_JDdBQYFgC00yCM2iE1fU5YUoF27uoEjSGqlFhAHmS4Tq7hbKzulgqC_kiJ1ipV8agCPNkRWk8Lz7VUOTNaoUCPOJbq5rtEWhap8NXvju-1qpedSuhK1sdQ5KRNsW2TPgGlZOizRnJZe6ivEVCSSDAEFkZwTCLdRkogFt2RaLaXPc5t4klNdg0sHHFgBQim1lEa7CGsc5eU0m6qSpcNKgnPVIAL8Sl2haHOGhH0F_MH8Cv659Ysf4YcQiFb6DgVX1grtJWy5xDIH-nb6GY9V7sPgKByj8Ic9YKWC2Vila8ihFes7UfQhTN1_802WUUsRNrOthU-9hVVegPhVgf71tq4xRQqpwHSUKKGPYNT8sxJyVSNwvcBUKKge_QwCs6hsCkA56GKIOmBTqnOahYotGxorGMIatNvZmMtyjiL7Zgm1VJFCra4qI5YZNQA0tTAGpAtXs7FS5xgJaJq6LFKg9Sci6dWTSJW0wfw5ZeT-MXJvlj5kN8rc7HbLZNMtVx1_FRF6n2yvPevXDigPIhlzOKLD7yDdh9V64-25rrRzXivEK7DVFjE2UYp6h8ZnczeY_WV93rghv7YToaYcsUrTq5m9BMyEfd3M5xgxb72Afj9B_5b558LcJGgLfWHXjWsbuztR5qlFiMLYiK7Jpx0pCOa5ebAzbKLoE_Dx2K3rLR92RxOn0s-h1A6IZSkgJ8m2sQjLp4lc2gXPNuvYJ-ZHS4UywSxzw-s27VVrem57nByWotAUz0Z9etuqOk8kIGK1KCphe25eZAAGMe9u_-jyg9nlF7PLh8ZgOl1-JOeyquXl10uZFKK8jC7Zu3fv3mV_-QGhBzi8zdwn_X5LwW-TSgtCRTK31hv610qdo8XO3bi0g_M-o_Kj4qGEMr9kzU5v4ZOGVXUPHqNHG9yJzMVmTVl4Ylp7KRLBzk6vqRei3FUMorpuWvw16XaM-E7FWIn9AENoVm1VoMnlYmnWQPqN1gl5f6wxjjcb5rHJW__v5-Cf37TpT0iP_yLwj7t5sc7f3BwevuAGz_7-f3Gz9-fH3wRH7j9lvwM) | The quest shown in these screenshots. |
| 2 | [The Parchment of Oaths](https://vibecoder-1z3r0.github.io/the-quest-map-generator/#Ab1V33PbRBDW2ZJiy7Ikpzg0L-2mhSlYcobSGR54Iy0tmcIkM01hys85S2dLY_nOczrFDeMn_lP-E_Yk2dQlYdoH2MS5W61u97tvv3WIoS0YaCPVDv82-_d1Kjdo0qBDbnQGRksfBPzRJ8kWBBkMjozAqNMRHdlxcFuXfS-nznC0dbR97zzrkT3HsrtW17E823ZJ2G-RsEW6xHIMy7AJWOZ9kzzuoG-18GmfdPYtaz-098Pe_l2ze6dNhmZ72GoNTTIkbdsdWB8a5DYJD4PwsBcetsODLnneI55LvD7p9W3XtXzXclz3LBgH3tj3I28QDvqfBX7P7RJ_zz-1QqcdOiTqtkK3HbassL0Xmpb3kR0etMPb5rjXibyOFThhsDcYmmD17mT9W6dB8NCPHC_q-WG_F9le1PFDO-h_7MPhAG517_rdV237xxb5yfJ-HrZ_6Xq_esFvA6SIfH5wkTI4pzJOF4wrEFM4oyot_jC_YVKwIgI6VUxCsWQ8yfgMYlFylbOigFSUsoCExdkyZVLHFKZ6oQRncEEnOVOFTvdyRrlQaQSnkNJLBklWxOKSSZYAhTRLEsZhQZd4mCpdhs6rY5Tjb5xpTFSqbEpjBXMuVvi4qAr9E_Ox4zQ1lKQx5tevValFtX1MFY3FYlLlfy4rUCuEzqqoZAua8Sqm3aVYMTktc1hlv1OZbK4BecYAi2IalmDBV6KERVkouMSHJabKeFMt3lSLIBfosE2KB4gfnyOzPMGqSmbssoaw3F6p4WWVqTTjWOakVDBhKypZBBOpr5g27ZkK2cAv6raUPGE0qXnIBXZlwjBTTR1Cy0s5R5DVmSKliVhtrlywLeMpzfPi-E_rKYzhjMc1urpinVigHCqCM1SAEDKCZY6UA95EXmnMM2CvY7ZUFb4Ndy9raJ88kXr5gUokZg7TbIbEfYqrRB41KViNQ_UOzUWZwD3N8tvi2U16dK86WaPQaJPq_GqnBhI5Gu2eG42c9cn5-rvz9VcK-zVfP2FTxgu2frFEYdN87azhy_F4DP-64EuP0PkCPw-bdVMmRiHHFC-mQU1FnouVZmc0qknAMkj1aIREj54yikR-m81SxfU7JyJXEbwoFwvBN3CPYZs5wW7wBwo5YVrGHBsEis6xRY8ASV8IVONEJFcoZRRl1eWELugMJYQ6V7o65tUd5Ow14itllUKDrSfsDYTwdRHTJas4xh7QJc6pLI7x5s6zjUZQM1hUZ5aNSirlJUgoqj9B5Pqrpu6y1lIz8UyLHkFXQsaKhZ6iacaTm8YcFS6RR5RAPR5vzNUFzhVgAin0FCQwuYIC52tZXT7OhT7dzLdm89gZGx9oUGcywe-4JnKmUmtrxo71urZxg-1ETPO_i2x3rTaa0XevidTLu0X20AxCmv-Mzsb-PvO2vVvEMwz_-siu_c-RzjVG-vXl_wI) | Work in progress: the start of the quest. |

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
  shown; hidden stone looks like any hidden area and shows once its room or zone is revealed. A hallway that
  is in no zone is treated as solid stone: it stays fogged, and tapping it and pressing Reveal says "Nothing
  to reveal. This is solid stone." So paint every hallway the heroes can walk into a zone. Tapping a
  hallway highlights only that square, so the shape of a zone never shows.
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
the tool does. They show [quest #1 in the live editor](https://vibecoder-1z3r0.github.io/the-quest-map-generator/#AdVXW28bRRj1Jt4kXt_TtPCA8LhCaBrSikIlJAQP5VaQgFpQhLhrdne8u8p6x8zOxjXKT-mP5XwzY8eFFHhAQqySeMfzXc_5Lm0wvu4JWq3W6F850MvVYeYPI_o-bM2CFmuNWu4JAxLy761gRocZHciIuwnd7VYM92TWqey1rg6z1s6h5Q_B5kCxiGgcvjcO3z8-CB4cBLfCoNk7eQcvne6t4Mave_ykzW_s8xt7_NYBv3nEb7b5rX3-Upu_HIYvd8JxJzw-Dr7qBOP-QW980OsPvxy_Oh7zwYAPh3w05OMBHwz5SZ-fRJObnSA6Hnf6QTmc9Ia8N-K9Ae8PX-2Pgkfj4LV-8Fo3yLq9s6N21gnDTtg5DLu9dqsbtjph6zgQw_bw8LtxEES97uuD_jSa7A0n-_gZTfZGPwb900GH9w55dMQHXd6N-PDop_ZgGnWmg2ja6067o2k0nNzoToaDSfdoMuxM9nvTgz4_GvFwwA_G_LDP9yK-3-XtXvv-8ffj0Q_9wc9R95f-Eci6_8qTXLKvjaokeyLiUpqaqTn7JhOVMvmz9ueqypjI1BkTbKlWUs-bkq2K34ROWSUWMmWnp1749JQlQl_gK5NrKZmokkJWhtXWuPHGE1UZUVQFzBp4rmWivc-FyIqEqSqBcK6aLDdsrnSmjJHVNIo-Y7m4kEzLRBbkZKU0eRIGkcWiSsnEIxWXRVWfsRIC8dp6mEuhS1nXrC7FWmrE-3mzkKUN-Aw2a4YgpbZhIx6R0KtuYIYsnp4-LDOlXXpFhXiFTnK6gXQt2YXU601u96LoO9WwRVMbfF-ZRkuoGGUNb9Cwls-QhtGFRD6iLO39iygA8MgN4o2uSHDBYHAhKUW4wRdrNicbW0crTZTl0KqB2gdyJTSkY03g5VIrCe_A1cpu09wkyXJVpiwVVSZ1DcOaZVoKwENIVxt8ETSCnT4bUe3EuiCqICcRoBZLcAxRxM5iydKiTtQFwXuPMRKnYIn8uFTJuZdHhHgrsszS4PKtVUksL-G6UnohSgRbUuypcrat_lKYfCXWNYzPCuPNgSYXjbVLPkuFhLPighxD_Gzjrd51Vu84g70vVFUbEvEOvYrn3XoC4U-uqZktmOQ_0c2CQMsg_JDdBQYFgC00yCM2iE1fU5YUoF27uoEjSGqlFhAHmS4Tq7hbKzulgqC_kiJ1ipV8agCPNkRWk8Lz7VUOTNaoUCPOJbq5rtEWhap8NXvju-1qpedSuhK1sdQ5KRNsW2TPgGlZOizRnJZe6ivEVCSSDAEFkZwTCLdRkogFt2RaLaXPc5t4klNdg0sHHFgBQim1lEa7CGsc5eU0m6qSpcNKgnPVIAL8Sl2haHOGhH0F_MH8Cv659Ysf4YcQiFb6DgVX1grtJWy5xDIH-nb6GY9V7sPgKByj8Ic9YKWC2Vila8ihFes7UfQhTN1_802WUUsRNrOthU-9hVVegPhVgf71tq4xRQqpwHSUKKGPYNT8sxJyVSNwvcBUKKge_QwCs6hsCkA56GKIOmBTqnOahYotGxorGMIatNvZmMtyjiL7Zgm1VJFCra4qI5YZNQA0tTAGpAtXs7FS5xgJaJq6LFKg9Sci6dWTSJW0wfw5ZeT-MXJvlj5kN8rc7HbLZNMtVx1_FRF6n2yvPevXDigPIhlzOKLD7yDdh9V64-25rrRzXivEK7DVFjE2UYp6h8ZnczeY_WV93rghv7YToaYcsUrTq5m9BMyEfd3M5xgxb72Afj9B_5b558LcJGgLfWHXjWsbuztR5qlFiMLYiK7Jpx0pCOa5ebAzbKLoE_Dx2K3rLR92RxOn0s-h1A6IZSkgJ8m2sQjLp4lc2gXPNuvYJ-ZHS4UywSxzw-s27VVrem57nByWotAUz0Z9etuqOk8kIGK1KCphe25eZAAGMe9u_-jyg9nlF7PLh8ZgOl1-JOeyquXl10uZFKK8jC7Zu3fv3mV_-QGhBzi8zdwn_X5LwW-TSgtCRTK31hv610qdo8XO3bi0g_M-o_Kj4qGEMr9kzU5v4ZOGVXUPHqNHG9yJzMVmTVl4Ylp7KRLBzk6vqRei3FUMorpuWvw16XaM-E7FWIn9AENoVm1VoMnlYmnWQPqN1gl5f6wxjjcb5rHJW__v5-Cf37TpT0iP_yLwj7t5sc7f3BwevuAGz_7-f3Gz9-fH3wRH7j9lvwM).

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

### Quest simulator (developer tool)

`scripts/simulate.py` gives a rough idea of how hard a quest is for 2, 3 or 4 heroes. It reads a quest
link (a URL, the part after `#`, or a file that holds one) and plays the fights many times with the
base-game dice, then prints how often the heroes survive, how many body points they have left, and
which rooms cost the most. It is a fights-only Monte Carlo: no movement, line of sight, doors,
treasure or equipment, and special rules written in the quest text are not modeled. Only the stat
blocks in Zargon's notes (`**Name**` followed by a `|BP|MP|Attack|Defense|Special|` table) and the
potions of healing named there are read. Use it to compare quests and spot a room that decides
everything, not to predict a table's result. It is not part of the page and does not change a link.

```
.venv/bin/python scripts/simulate.py docs/showcase/quest-1.txt
.venv/bin/python scripts/simulate.py "<link>" --runs 5000 --heroes 3,4 --caster-damage 0
```

A stat block goes to the only monster piece of its type (for example the one Abomination); use
`--boss "Lumeloth=Abomination"` when that is not clear. The printed assumptions say what was guessed.

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
