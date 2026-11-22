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

**[Open the quest from these screenshots in the live editor](https://vibecoder-1z3r0.github.io/the-quest-map-generator/#AY1VW4vbRhSWbI1tSdbNu-skUFajEMrUdQMtgby0D1taQiAtSy4P6ZWxNZbEyhp3RlrXhf6R_pn-tZ4ZSV4vpLRiYTWa75zzne9cbEZ3j2F0L9eGeroDQv92uAczPnwwjeuTQ_duhPDdQMa1aWB9fgcXyDSODzJa6HVr2d8g4_RB7X33EQ16fPf_-njqwD0t_fzpROjLCH01G5nPRuYcmc3g_Dm82O7cPPttQM4tcjYkZwMyH5GLCbmwyHxIHljWI0QeIvTQRpGN5gaaz6xHnvV8Zr62zWeB-SYyI280jUZTz7twgu-jyygivk-CgIQBiXwyc8m5R86d-MI2nVlke2YZxNOATEMy9YkXXHohsmbmi8h84plPXDNzp8uJldkI2cgeI3dqGS4ybGTMTBpYwRj5IxROLoPBZTA0g9H7yDSdqfux7yXOD1EYD4J4CH_wEv5kegvfJtMxcSbEd4nrkGDyo-f_bPmJYye-k3jjZOomcz95ECYXQXIWJudR4oaJE8Rnbhz4cWDF4TD2h3E4iP1BHJixO4kDOx5Ok4mfjLxk5CRjJ7EdMgkJ8skoImOPDBwydIk1_cUZ_-pDJc3PP3qbM_ym5hXDb-mqZLXEfIPfZbTidf6X9YpXGaYZX2KKd3zPxKYp8b74g4oUV3TLUrxYdODFAq-puIVPdS4Yw7RaF6yqsdTO6875mlc1LaoC3NYQWbK16GJuaVasscbmvMnyGm-4yHhdsypxnJc4p7cMCwZOVYw9FyoQrYHYilap8vCCr8qikktcAmB10AE2jIqSSYllSQ9MAN1XzZaVmu8SfEoMHJnQrIEOXatX0YAb5XGxuCozLtrsigroUrHO1Q2gJcO3TBz61J46znve4G0ja_he1Y1gYFJz7bgXQ3teQhq1UHlgWpb6_qQCpwUA2SE1QDeiUrgtBn9bpjKEKPDhgDfKxTHOXqiC5WAlQbSv2Z4KQK-E0i5ngjMIDrJq7DHLPkec8zLFKa0yJiQ4FjgTjII6Suiqlxc4A9fkb1t1zkoUqlKAY0BQ0B1UGKDAHa8YTgu55rdK3acYK7giq0q_Kvn6psMDQ3grskxXoc1X8lIVeQehKy62tASypeKe8ta3tt_ROt_TgwTn10XduYMqtWy0XxWz5JBwVtyqwABf9tHkaTB5Egz8fccrWStIF7Az6cquI0G9336gZY5iqvhr0WyVaBmAr_BnoEEBwhYCiqeqoarZtZQuCqgt27aBQIAUnG8BDsVsM9GGp8N60ipA-jWjaWtYsd9rkEfUqlhNCpEf73PQ5AANWtMbBrMsJUxFwauumTvnp8Oq0RvG2g7VXGSujJVsR2WXoGlZtlquWaHLq8YKOBVrphyBCnR9o0R47DjfAJf6_6nQJk7heruCnaMk7aYIyEFxVCSuxwKvAKqOmhlMVqp87ho1GbBGBDDX052zcgM6vduBWcqVgeR3ya1YpmoIloLWNfCmrewrzm-gq6HusixS6BQBk0vLNh7mO6a3WdEyUWKAp7zoNDoaQwd8C7k3u45yO43t9mm3YV_wu6a9YwTtq3wfMNG4D85YJ6Jy1uoITfoJpHtVHfpo9xpLbyrBgS-FtbxdwS5NoWRg8XLT7pbuUt407Zo66KaWKkf4LUjv1s4OZFbay2azgSn5AtJOD9BkANBDkVLY7qxfAv9Z-Xs0-wRVK8itXphNVemupKoVaKoVUjR66EHF1FMBZO619Mm8fGoY_wA)** (it's the owner's quest #1; the whole quest is in that link).

More to try in the live editor: [a blank map](https://vibecoder-1z3r0.github.io/the-quest-map-generator/) to start your own, or [Quest 2, The Parchment of Oaths](https://vibecoder-1z3r0.github.io/the-quest-map-generator/#AeVSsU7EMAzlJKabmJi9sZxu4BNgATEcEsfA6CbuJbo0qRznKjHy5ThpewufQJWhseP3np-9ufm33-bx_ugI3pGNGygKpB4OKC7_3L4QJ8o7wF6IIY8UrY8nMKlECZQzuFQ4gyXjR0dcc6JQH5IiwRG7QJIr3OcJYxK3g1dweCGwPpt0ISYLCM5bSxEGHLUYpdLguZVh1GN81YQsvkcjcI5p0nBuRH8177fbhUMYjeLXZw06td9nFDRp6Br-GzdRk0qnlmUa0MeWq9cxTcR9CTD5b2S7tgHBEyipwpBVwq9UYChZ4KLBolA-LmxmZdtBSHqhFeJB9WtcnY1WWYU9XWYJ47WlxZfJi_NRaZ6KQEcTMu2g49qiW8bTJ17k53ksJVpCO_sQkk6lI0WarVNpofBZRbaa7NCmaW0509VxhyHkve7HXd2OA1vdgOqyuF8) (the start of the owner's second quest).

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

### Heads up

- **Anyone with the link can read Zargon's secret notes**, because they are stored in the link.
  Only share a link with players if you are happy for them to see everything in it.
- Very long links may be cut off by some chat apps. A warning appears above about 2,000 characters.
- Needs a recent browser (about Chrome 103, Safari 16.4 or Firefox 113). Older browsers show a
  message with the minimum versions.

## Screenshots

These are generated by script (`make screenshots`) from the real editor, so they always match what
the tool does. They show [quest #1 in the live editor](https://vibecoder-1z3r0.github.io/the-quest-map-generator/#AY1VW4vbRhSWbI1tSdbNu-skUFajEMrUdQMtgby0D1taQiAtSy4P6ZWxNZbEyhp3RlrXhf6R_pn-tZ4ZSV4vpLRiYTWa75zzne9cbEZ3j2F0L9eGeroDQv92uAczPnwwjeuTQ_duhPDdQMa1aWB9fgcXyDSODzJa6HVr2d8g4_RB7X33EQ16fPf_-njqwD0t_fzpROjLCH01G5nPRuYcmc3g_Dm82O7cPPttQM4tcjYkZwMyH5GLCbmwyHxIHljWI0QeIvTQRpGN5gaaz6xHnvV8Zr62zWeB-SYyI280jUZTz7twgu-jyygivk-CgIQBiXwyc8m5R86d-MI2nVlke2YZxNOATEMy9YkXXHohsmbmi8h84plPXDNzp8uJldkI2cgeI3dqGS4ybGTMTBpYwRj5IxROLoPBZTA0g9H7yDSdqfux7yXOD1EYD4J4CH_wEv5kegvfJtMxcSbEd4nrkGDyo-f_bPmJYye-k3jjZOomcz95ECYXQXIWJudR4oaJE8Rnbhz4cWDF4TD2h3E4iP1BHJixO4kDOx5Ok4mfjLxk5CRjJ7EdMgkJ8skoImOPDBwydIk1_cUZ_-pDJc3PP3qbM_ym5hXDb-mqZLXEfIPfZbTidf6X9YpXGaYZX2KKd3zPxKYp8b74g4oUV3TLUrxYdODFAq-puIVPdS4Yw7RaF6yqsdTO6875mlc1LaoC3NYQWbK16GJuaVasscbmvMnyGm-4yHhdsypxnJc4p7cMCwZOVYw9FyoQrYHYilap8vCCr8qikktcAmB10AE2jIqSSYllSQ9MAN1XzZaVmu8SfEoMHJnQrIEOXatX0YAb5XGxuCozLtrsigroUrHO1Q2gJcO3TBz61J46znve4G0ja_he1Y1gYFJz7bgXQ3teQhq1UHlgWpb6_qQCpwUA2SE1QDeiUrgtBn9bpjKEKPDhgDfKxTHOXqiC5WAlQbSv2Z4KQK-E0i5ngjMIDrJq7DHLPkec8zLFKa0yJiQ4FjgTjII6Suiqlxc4A9fkb1t1zkoUqlKAY0BQ0B1UGKDAHa8YTgu55rdK3acYK7giq0q_Kvn6psMDQ3grskxXoc1X8lIVeQehKy62tASypeKe8ta3tt_ROt_TgwTn10XduYMqtWy0XxWz5JBwVtyqwABf9tHkaTB5Egz8fccrWStIF7Az6cquI0G9336gZY5iqvhr0WyVaBmAr_BnoEEBwhYCiqeqoarZtZQuCqgt27aBQIAUnG8BDsVsM9GGp8N60ipA-jWjaWtYsd9rkEfUqlhNCpEf73PQ5AANWtMbBrMsJUxFwauumTvnp8Oq0RvG2g7VXGSujJVsR2WXoGlZtlquWaHLq8YKOBVrphyBCnR9o0R47DjfAJf6_6nQJk7heruCnaMk7aYIyEFxVCSuxwKvAKqOmhlMVqp87ho1GbBGBDDX052zcgM6vduBWcqVgeR3ya1YpmoIloLWNfCmrewrzm-gq6HusixS6BQBk0vLNh7mO6a3WdEyUWKAp7zoNDoaQwd8C7k3u45yO43t9mm3YV_wu6a9YwTtq3wfMNG4D85YJ6Jy1uoITfoJpHtVHfpo9xpLbyrBgS-FtbxdwS5NoWRg8XLT7pbuUt407Zo66KaWKkf4LUjv1s4OZFbay2azgSn5AtJOD9BkANBDkVLY7qxfAv9Z-Xs0-wRVK8itXphNVemupKoVaKoVUjR66EHF1FMBZO619Mm8fGoY_wA).

| | |
|---|---|
| ![Empty board](docs/screenshots/01-empty-board.png) **The empty board** | ![Dark mode](docs/screenshots/04-dark-mode.png) **Dark mode** (stored in the link) |
| ![Quest text](docs/screenshots/03-quest-text.png) **Quest text, previews and legend** | ![Print view](docs/screenshots/05-print-view.png) **Print view** (always light) |

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
