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
| 1 | [The Stone Tablets of Uganoth](https://vibecoder-1z3r0.github.io/the-quest-map-generator/#AbVXbW8bxxG-k3iyuHyXZSUfgnAoBMGZIYk4MVCgaD_YTeoGSGsisVGkeV3ezd0ttNxldvfEMNBv6A_ory1mbynRqdqiRXuAoFvuvD4z8wwZj-574iiKhv-TA73cHZbhMKTPk2gZRxANo-ZJYhIK71G8pMOSDmSkuUma21uxaBmR2UblKLo7LKODQxQO8f5AsXA2Sn4zSn57dhI_PYkvkrg-Ov_VSXzR7lzED388Ss9b6cPj9OFRenGSPjpNH7XSi-P0rVb6dpK83U5G7eTsLP6iHY96J93RSbc3-NPo3dEo7ffTwSAdDtJRP-0P0vNees7Gj9oxOxu1e7EcjLuDtDtMu_20N3i3N4xfjOL3evF7nbjsdGenrbKdJO2k_SDpdFtRJ4naSXQW80Fr8OCrURyzbuf9fm_CxkeD8fFgfDwcHw2_iXvTfjvtPkjZadrvpB2WDk6_bfUnrD3ps0m3M-kMJ2wwftgZD_rjzul40B4fdycnvfR0mCb99GSUPuilRyw97qStbuvJ2V9Gw697_e9Y5_veaRTFT955VSF86bRCeMVXEp0FXcDrkivtqr-1PteqBF7qGXDY6C2aopawFT9zk4Pia8xhOg3C0ylk3FxjDq4yiMBVJlA5sN64C8YzrRwXSqgSXIVgMTPB55qXIgMvW-m6rBwU2pTaOVQTxj6Dil8jGMwEko-tNuSIO-Cw4ionCy_0SgplZyAxh9XOOyiQG4nWgpV8hwam08_rNUof7wwqbgGVQ-OjRrA8o1dTC-Vjmk6fyVKbJjuhwCI3WUU3rkKLcI1mt09twdhXuoZ1bR1co3K1QRDKaW94D4a3PAODzlAewKX09wcVOCzADCg1g642iuTW4DSskTK0jj7YQUEmbv1sDRWs4iq3E8ae45YbnMHKEHYVGo12RrB62dss9zlCpWUOOVclGgsFN1Aa5A5JnKs9vMClVjj565A6Z2UEVao0iAqc4RsLGVegtIMVQi5spq8J3QUAiVOwVPqV1NlVkOcGwRlRlr4KTb5WSyryBg0obdZcgqklxZ7rxrbX33BXbfnOLgCWwgVzQoVovF3yKbU2UIprcrzlu9nemz10Zg-cLQD-qJV1JBIcBpVQdu9pwdire1rmFkzyn5l6TaCVC8aewRxeVcJCIYx1vhpUzdBSvigGuW3aBhxJGq3XUAiV2yYTr3g4rAetsgD4AnneKCr8ycGGG0fFqnOYw-W2QgU7XYPjVwgbbS1aK7QKzRyMHw6rly4Qmw71sdiKlAm2W2RnsOVSNlhmKHx5aayUdiJDMgSZ4dkVgXDJ2HOYA7fetN5gyPM28ayivhYuAIeWEMppogxeI_fGuQqatVIoG6wQSqNrlUOtcjQKuatgW2HogF-Y33ILqfcrLPBAQZBrbR5TcNJqkMh9u6ywEir33OcCVlUIIzVonTZo4SlIbR2sdL6DjRbK2ceM_Q7m8OTDD6GkkSJslrcW_hAsbCuRVbAVUkKwdY8pUsj5mpe4YOwTmDeA_fsWarqGg9PrFWwF9WOgIInOoaEAdAPdSqi8ATanPicq1LCpiVYcFEavG2qsUBYLgNcbrSDXpGD1XWessKQBcBoMd04iFdkb1_oKMm4RrBQ52n8sJL2GIlIn7TF_Q3nB2Kcwh3oTQm6orKHuZpXsp-Vu4u8iKsU12d6Fqt9LUAFEMtbgyDf28QLgmdrtvb0xlZ7mjZYSOGR6veIOcpHhAuCzoiHmcGmv6objd54RLOWot5jfcfZGOI-9rYsCDXz0T8ofGPQ_I499gr7R137bNGPjV6dEnnuEKIy96I58ekpB8yYfHJANY7-HObxUGR7Ww69oqikGHso9QWwkzxCQbDuPMP6U4cbvd9hv45BYoBYFhrisIa9LWqvedOFnnBxKLgzFs1efXHrVxpNfuCu9For7mStEWRvqocPlz26eL2-eOcezq5tPsEBl8ebLDWaCyxt2A7-ez-dw_z92A0_h7u_PFO5tGrkgHBCab1I1fT2xlRF41RCkp8onQA1H7UIplGGtuoNpqpC4SagF3DD2Yo80lW-9X0wekBUtuhwL2tL5PR1CRW56BO29_PCvy-yJI8xmQySesoQFr7YVFgHXG7dbMPZBdE7eX5oczX6nvHRV9P99frj30IqWr1-HHwJx682bXx62B4co-vi_P1zunyP6SXTa_Br5Ow) | The quest shown in these screenshots. |
| 2 | [The Parchment of Oaths](https://vibecoder-1z3r0.github.io/the-quest-map-generator/#AeVTz2_TMBSO0zhr03RrCh3sApY4cEiZEPAXsAOgHYa0ceDoxq-ztdSubKeROPKX8-KkEz-FxBUrkvO9Z3_f955tEv045gX5ZxDm7wD5HQhzEcUhHrLFsKjPIJj_EeDinu0eFMXfQfQT6Mbr7N2UHGU0ndBJRo_TNCflbFTmo3IWl3lMyphMCM0iGqWE0eRZQi7GiGmM0RkZLyhdlOminC6eJpMnI7JMRss4XiZkSUZpXtBiQh9F5EFGrsfkMSnP5uXZtDwblacTOj8ib2LyMiEnKbmckuOcHM_IdJbmOT3JaZZjua9ObySwj9xWcgvaM7NhV9xL9zV5D9aAWzG-8WCZ24EWSt-yyjTa1-Ack6axjgmo1E6C7XIeqa690cBu-LoG7zq6T7dcGy9X7AOTfA9MKFeZPVgQjDOphADNtnyHm7nvZPhd2MY1fpXqPHHr1YZXnt1p02LYBaFfPZ9n2aDhLa-Qv1sWqE34veCeV2a7DvyXNphq0TqErIUtVzrkOrgzLdhNU7NWfeFWHMpgtQKGokgDAgU_m4ZtG-fZHoMNUik9qFUHtRWrDQI4UDxH_xjHzmqBqt4q2PcWdvclDX1plZdKo8zbxrM1tNzCiq1tV6Icjmdj7GDf9cfSaAFc9H2oDZ7KGpCpbx1aqxt7hybDHie5MO2hZAf3HZe8rt159CJ62N2OKyvwBgx9ufIy-j8HmfWP-hs) | Work in progress: the start of the quest. |

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
the tool does. They show [quest #1 in the live editor](https://vibecoder-1z3r0.github.io/the-quest-map-generator/#AbVXbW8bxxG-k3iyuHyXZSUfgnAoBMGZIYk4MVCgaD_YTeoGSGsisVGkeV3ezd0ttNxldvfEMNBv6A_ory1mbynRqdqiRXuAoFvuvD4z8wwZj-574iiKhv-TA73cHZbhMKTPk2gZRxANo-ZJYhIK71G8pMOSDmSkuUma21uxaBmR2UblKLo7LKODQxQO8f5AsXA2Sn4zSn57dhI_PYkvkrg-Ov_VSXzR7lzED388Ss9b6cPj9OFRenGSPjpNH7XSi-P0rVb6dpK83U5G7eTsLP6iHY96J93RSbc3-NPo3dEo7ffTwSAdDtJRP-0P0vNees7Gj9oxOxu1e7EcjLuDtDtMu_20N3i3N4xfjOL3evF7nbjsdGenrbKdJO2k_SDpdFtRJ4naSXQW80Fr8OCrURyzbuf9fm_CxkeD8fFgfDwcHw2_iXvTfjvtPkjZadrvpB2WDk6_bfUnrD3ps0m3M-kMJ2wwftgZD_rjzul40B4fdycnvfR0mCb99GSUPuilRyw97qStbuvJ2V9Gw697_e9Y5_veaRTFT955VSF86bRCeMVXEp0FXcDrkivtqr-1PteqBF7qGXDY6C2aopawFT9zk4Pia8xhOg3C0ylk3FxjDq4yiMBVJlA5sN64C8YzrRwXSqgSXIVgMTPB55qXIgMvW-m6rBwU2pTaOVQTxj6Dil8jGMwEko-tNuSIO-Cw4ionCy_0SgplZyAxh9XOOyiQG4nWgpV8hwam08_rNUof7wwqbgGVQ-OjRrA8o1dTC-Vjmk6fyVKbJjuhwCI3WUU3rkKLcI1mt09twdhXuoZ1bR1co3K1QRDKaW94D4a3PAODzlAewKX09wcVOCzADCg1g642iuTW4DSskTK0jj7YQUEmbv1sDRWs4iq3E8ae45YbnMHKEHYVGo12RrB62dss9zlCpWUOOVclGgsFN1Aa5A5JnKs9vMClVjj565A6Z2UEVao0iAqc4RsLGVegtIMVQi5spq8J3QUAiVOwVPqV1NlVkOcGwRlRlr4KTb5WSyryBg0obdZcgqklxZ7rxrbX33BXbfnOLgCWwgVzQoVovF3yKbU2UIprcrzlu9nemz10Zg-cLQD-qJV1JBIcBpVQdu9pwdire1rmFkzyn5l6TaCVC8aewRxeVcJCIYx1vhpUzdBSvigGuW3aBhxJGq3XUAiV2yYTr3g4rAetsgD4AnneKCr8ycGGG0fFqnOYw-W2QgU7XYPjVwgbbS1aK7QKzRyMHw6rly4Qmw71sdiKlAm2W2RnsOVSNlhmKHx5aayUdiJDMgSZ4dkVgXDJ2HOYA7fetN5gyPM28ayivhYuAIeWEMppogxeI_fGuQqatVIoG6wQSqNrlUOtcjQKuatgW2HogF-Y33ILqfcrLPBAQZBrbR5TcNJqkMh9u6ywEir33OcCVlUIIzVonTZo4SlIbR2sdL6DjRbK2ceM_Q7m8OTDD6GkkSJslrcW_hAsbCuRVbAVUkKwdY8pUsj5mpe4YOwTmDeA_fsWarqGg9PrFWwF9WOgIInOoaEAdAPdSqi8ATanPicq1LCpiVYcFEavG2qsUBYLgNcbrSDXpGD1XWessKQBcBoMd04iFdkb1_oKMm4RrBQ52n8sJL2GIlIn7TF_Q3nB2Kcwh3oTQm6orKHuZpXsp-Vu4u8iKsU12d6Fqt9LUAFEMtbgyDf28QLgmdrtvb0xlZ7mjZYSOGR6veIOcpHhAuCzoiHmcGmv6objd54RLOWot5jfcfZGOI-9rYsCDXz0T8ofGPQ_I499gr7R137bNGPjV6dEnnuEKIy96I58ekpB8yYfHJANY7-HObxUGR7Ww69oqikGHso9QWwkzxCQbDuPMP6U4cbvd9hv45BYoBYFhrisIa9LWqvedOFnnBxKLgzFs1efXHrVxpNfuCu9For7mStEWRvqocPlz26eL2-eOcezq5tPsEBl8ebLDWaCyxt2A7-ez-dw_z92A0_h7u_PFO5tGrkgHBCab1I1fT2xlRF41RCkp8onQA1H7UIplGGtuoNpqpC4SagF3DD2Yo80lW-9X0wekBUtuhwL2tL5PR1CRW56BO29_PCvy-yJI8xmQySesoQFr7YVFgHXG7dbMPZBdE7eX5oczX6nvHRV9P99frj30IqWr1-HHwJx682bXx62B4co-vi_P1zunyP6SXTa_Br5Ow).

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
