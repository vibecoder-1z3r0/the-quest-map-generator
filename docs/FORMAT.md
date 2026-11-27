# URL Format Specification

**Status: DRAFT, format version 1.** The format may change freely until the first tagged release.
After that, changes are additive and versioned, and every link ever issued must keep decoding (the
golden-link tests enforce this). This document is the contract; the code follows it.

A map is stored entirely in the URL **hash** (`#...`). The hash is never sent to a server.

```
https://example.com/quest-map/#AWNQZBiRgImRhZ0phZ0xhYWViZmRiaWkKLGA0Zg1LLE0pwQkz-xfkgEA
                               └──────────────── payload ────────────────┘
```

## 1. Payload

```
payload = base64url( [ version byte ] ++ deflateRaw( body ) )
```

- `base64url` is RFC 4648 §5 (`-` and `_`), **no padding**.
- The first byte is the **format version** (`1`). A decoder that does not know the version must show
  an "unsupported link version" banner and start blank. It must never guess.
- `deflateRaw` is raw DEFLATE (RFC 1951), no zlib or gzip header. Browsers expose it as
  `CompressionStream("deflate-raw")`.
- An empty hash means a blank map. A blank map may be written as an empty hash.

> **Not canonical.** Different deflate implementations produce different bytes for the same body, so
> two links can differ and still describe the same map. The editor also does not normalize placements
> (§7). Tests therefore compare *decoded* maps, never freshly encoded URLs byte for byte. Only the
> decode direction has fixed golden URLs.

## 2. Conventions

- **Varint**: unsigned LEB128 (7 bits per byte, low bits first, high bit set means "more").
- **String**: `varint byteLength` followed by that many bytes of UTF-8. Strings are always filtered
  and normalized first (§6).
- All fixed-size integers are single bytes. There is no multi-byte endianness to worry about.
- Reserved bits and values must be written as `0` and are ignored when reading.

## 3. Grid

> The room map and the quest statistics are derived from `src/board.txt` and the placed pieces.
> Nothing about them is stored in the link.

- 26 columns (`x` = 0..25) by 19 rows (`y` = 0..18). Origin is the top-left square.
- Board-style labels are for display only: column letter `A`..`Z` plus row number `1`..`19`.
  `x=4, y=7` is `E8`. The URL always uses numbers.
- Square index `i = y * 26 + x`, from 0 to 493.

## 4. Body

The body is these sections, in this order, with no padding between them.

| # | Section | Size |
|---|---|---|
| 0 | Flags | 1 byte |
| 1 | Highlights | fixed 247 bytes |
| 2 | Items | `varint count` + 3 bytes per item |
| 3 | Tiles | `varint count` + 5 bytes per tile |
| 4 | Legend | `varint count` + entries |
| 5 | Quest number | string |
| 6 | Quest title | string |
| 7 | Intro | string |
| 8 | Zargon's notes | string |
| 9 | Wandering monster id | 1 byte |
| 10 | Wandering monster text | string |
| 11 | Series (optional, trailing) | string |
| 12 | Hero view: zone layer and rooms (optional, trailing) | 494 bytes + `varint count` + records |
| 13 | Hero view play state (optional, trailing) | 28 bytes |

### 4.0 Flags

One byte of view settings.

| Bits | Meaning |
|---|---|
| 0-3 | editor **theme** id, 0..15 |
| 4 | **hero view**: `1` means the link opens in hero view (section 4.7), `0` the editor |
| 5-7 | reserved (`0`) |

| Theme id | Theme | Prints as |
|---|---|---|
| 0 | light (default) | itself |
| 1 | dark | light (id 0) |
| 2-15 | reserved for future themes | each declares its own |

Theme ids are permanent once assigned. A decoder that meets an unknown theme id shows the light
theme but keeps the id in the map, so it survives re-encoding.

Every theme declares whether it is **print-safe** (a light theme). **Printing never uses a dark
theme**: a print-safe theme prints as itself, and any other theme prints using the default light
theme (id 0). So a link in a future light theme prints in that theme, and a dark one prints light.
Opening a link applies its theme; changing the theme updates the link but is not an undo step.

### 4.1 Highlights

494 squares, 4 bits each, packed two per byte: square `i` lives in byte `i >> 1`; even `i` uses the
**low** nibble and odd `i` the **high** nibble. The final byte's high nibble is unused (`0`).

| Value | Color |
|---|---|
| 0 | none |
| 1 | grey (solid stone) |
| 2 | orange (a trap of any kind) |
| 3 | cyan |
| 4 | yellow |
| 5 | bright green |
| 6-15 | reserved |

Values are permanent once assigned. A decoder that meets a reserved value keeps it in the map (so it
survives re-encoding) and draws a neutral tint. A highlight is a translucent tint drawn over whatever
is in the square; it never hides anything. (Hero view zones are a separate layer, section 4.7, so a
square can have a highlight and be in a zone at once.)

### 4.2 Items

`varint count`, then `count` records of exactly 3 bytes:

```
byte 0   icon id        1..255  (0 is invalid)
byte 1   bits 0-4       x       0..25
         bits 5-6       rotation 0..3
         bit  7         reserved
byte 2   bits 0-4       y       0..18
         bits 5-7       reserved
```

- **Icon id** is the permanent numeric id from `catalog.json`. Ids are never reused or renumbered.
- **Rotation** is the number of clockwise quarter-turns from the piece's default orientation.
  Rotations 1 and 3 swap the footprint from `w x h` to `h x w`.
- **Position** is the top-left square of the piece's footprint *after* rotation. Pieces rotate
  around the center of that footprint, so rotating a piece in the editor re-anchors it to keep it on
  the board.
- A piece's whole rotated footprint must lie on the board. Records that do not fit are dropped and
  a warning is shown.
- **Doors and hidden doors** (catalog entries marked `edge`) are ordinary 1x1 pieces. Their artwork sits on the **north** edge at
  rotation 0; rotation 1, 2 and 3 move it to the east, south and west edges. A door on the outer
  edge of the board is valid.
- **Order is the z-order.** Items are drawn in list order, so later items are on top. The editor
  always appends new items. Items are drawn **above all tiles** (section 4.3). Any number of items may share a square, including exact duplicates read
  from a link.
- The count is limited to 1024. A larger count makes the link invalid.
- An id the decoder does not know is skipped, with a warning, so newer links degrade gracefully.

### 4.3 Tiles

Resizable rectangles laid over the board, such as a room tile that merges rooms. They live in their
own list because, unlike a piece, each tile carries its own size. `varint count` (at most 256), then
`count` records of exactly 5 bytes:

```
byte 0   tile id        1..255, a catalog entry marked "tile"
byte 1   x              0..25   left column
byte 2   y              0..18   top row
byte 3   width          1..26
byte 4   height         1..19
```

- A tile is always a rectangle and is never rotated. Its whole rectangle must lie on the board
  (`x + width <= 26`, `y + height <= 19`); records that do not fit are dropped with a warning.
- The tile id selects the style, a single 1x1 icon repeated across every square of the rectangle.
- **Layering:** tiles are drawn above the board and the highlights' base but **below every piece**.
  The list order is the z-order among tiles only; the editor appends new tiles at the end.
- An id that is not a tile (or unknown) is skipped, with a warning.
- Tiles do not affect the statistics, which keep the board's printed rooms.

### 4.4 Legend

Optional labels for highlight colors (for example "cyan = secret room").

`varint count` (0..35), then per entry: one byte **color value** (2..35), then a **string** label
(at most 40 characters). A color appears at most once; if repeated, the last entry wins. Labels are
filtered like single-line text (§6).

- **Grey (1) has no editable label.** It always means solid stone and is shown as "Solid stone". An
  entry for color 1 is never written, and one read from a link is ignored.
- **Orange (2) means a trap of any kind.** With no label it is shown as "Trap"; a stored label
  replaces that text.
- Legend entries **6 to 35 name zones 1 to 30** (section 4.7): zone *n* is named by entry *5 + n*. They
  are not highlight colors and are listed with the zones that are used on the map.
- Display: the viewer lists an entry for each color that is used on the map (grey as "Solid stone",
  orange as its label or "Trap", the others only if they have a label).

### 4.5 Quest text

| Field | Kind | Limit (characters) |
|---|---|---|
| Quest number | single line, plain | 10 |
| Quest title | single line, plain | 160 |
| Intro | multi-line, bold/italics only | 2,500 |
| Zargon's notes | multi-line, markdown subset | 10,000 |
| Wandering monster text | single line, plain | 160 |
| Series | single line, plain | 160 |

**Series** (for example "The Order of the Oth") is an optional *trailing* field: the last string in
the body. Encoders always write it, but a decoder must accept a body that ends right after the
wandering monster text and treat the series as empty, so links made before the field existed keep
working. Later fields can be added after it the same way.

Limits count Unicode code points after filtering. A decoded field longer than its limit is
truncated and a warning is shown. The editor stops accepting input at the limit.

**Wandering monster** is the pair *(id, text)*. The id byte is `0` for none, or the icon id of a
monster piece from the catalog. If the id is `0` and the text is empty, the quest has no wandering
monster. A non-monster id is treated as `0` with a warning.

### 4.6 Markdown subset (Zargon's notes)

Headings `#`, `##`, `###`; bullet lists (`-`); numbered lists (`1.`); `**bold**`; `*italic*`; a
horizontal rule (`---`); pipe tables with a header separator row; backslash escapes (`\*`). No
nested lists, raw HTML, images or links. A single newline is a line break; each blank line beyond
the first adds one blank line of vertical space. The intro supports **only** bold and italics;
everything else shows literally. Rendering uses DOM text nodes only, never `innerHTML`.

### 4.7 Hero view rooms and zones

Optional trailing section, written only when at least one room or zone has hero view data (or a play
state is stored). Hero view is a second way to look at the same quest: the map starts hidden and the
heroes reveal it room by room. See `docs/HERO_VIEW.md` for how it behaves.

A **region** is a room or a zone. Rooms are the board's letters: A..Z are regions 0..25 (the standard
board uses A..V). Zones 1..30 are regions 26..55.

The section starts with the **zone layer**: 494 bytes, one byte per square in the order of section 3:
`0` no zone, `1`..`30` zone 1..30; a larger value is read as no zone. It compresses to almost nothing
when few zones are used. A quest has at least ten zones and can have up to thirty; the number of zones
is not stored (it is the highest zone that is painted, has a record or has a name, never under ten). It is separate
from the highlights, so any square, including solid stone or a trap highlight, can be in a zone. A zone
on a square inside a lettered room is ignored for hero view. A zone is named by a legend entry
(section 4.4).

Then, as before, the room records:

`varint count` (0..56), then `count` records:

```
byte 0   region        0..55
byte 1   bit 0         the region is revealed at the start of the game
         bits 1-7      reserved (0)
byte 2   group         0 = none; regions that share a non-zero group reveal together
then four strings, in this order:
         read aloud (shown when the region is revealed)
         treasure   (shown by "search for treasure")
         traps      (shown by "search for traps")
         secret doors (shown by "search for secret doors")
```

- Each text is multi-line, bold/italics only like the intro, at most **600** characters, and is
  filtered like the intro (section 6). A longer text is truncated with a warning.
- A region at or above 56 is skipped with a warning. If a region appears twice the last record wins.
  A count above 56 makes the link invalid.
- Regions with no data have no record. Texts of the regions in a group are shown together, joined in
  region order.
- An encoder leaves the whole section out (and with it section 4.8) when there is no zone, no record and
  no play state, so a quest without hero view data keeps exactly the link it always had.

### 4.8 Hero view play state

Optional, directly after the records of section 4.7 (even when there are none, `count` is then 0 and the
zone layer is still present).
Exactly **28 bytes**: four masks of 7 bytes each (56 bits), in this order:

1. revealed regions
2. regions where the treasure search was done
3. regions where the traps search was done
4. regions where the secret-door search was done

Bit `r & 7` of byte `r >> 3` is region `r`, low bit first; bits for regions 56 and up are ignored.
If this section is absent the game is at its start: exactly the regions with the "revealed at the
start" flag are revealed and no search was done. If it is present it replaces that start state
completely, so an all-zero play state means that nothing is revealed, not even the start regions.
Fewer than 28 bytes remaining is a truncated link.

## 5. Size limits (defensive decoding)

- The inflated body must not exceed **262,144 bytes** (256 KiB). Decompression must stop and the link
  be rejected as soon as the limit is passed; never inflate unbounded.
- Every length, count, index and coordinate is bounds-checked. A truncated body is invalid.
- On any invalid link the app shows a banner and starts with a blank map. It never throws to the
  user and never partially applies garbage.

## 6. Character handling

Applied to **all** text fields, on typing, on paste and on every decode.

1. **Normalize**: Unicode NFC; `CR LF` and `CR` become `LF`; non-breaking space and tab become a
   space; curly quotes become `'` and `"`; en and em dashes become `-`; the ellipsis becomes `...`.
   Single-line fields also turn `LF` into a space.
2. **Filter**: keep only
   - letters (`\p{L}`), combining marks (`\p{M}`) and decimal digits (`\p{Nd}`), in any script
   - space and `LF` (the latter only in the intro and notes)
   - ``. , ! ? ' " : ; ( ) [ ] - * # | & \ / + _``

   Everything else is removed: `< > ` % = ~ @ $ ^`, control characters, and invisible or
   direction-changing characters (zero-width characters, bidi overrides and so on).
3. If anything was removed from a decoded link, show a notice saying so.

The filter is defense in depth. The primary protection is that text is only ever inserted as text.

## 7. No normalization of placements

The link records exactly what was placed, in the order it was placed. The same physical door can be
stored as the east edge of one square or the west edge of its neighbor, and both are valid and
distinct in the link. Nothing is merged, sorted or de-duplicated on decode.

## 8. Worked example

Highlights: `A1` grey, `B1` orange. Two items at `E8` (illustrative ids `1` and `2`; real ids come
from `catalog.json`): id 1 at rotation 0, and id 2 at rotation 3. One tile (illustrative id `100`)
at `E6`, 2 wide and 3 high. A legend entry `2 = "trap"`. Quest number `3`, title `Vault`,
series `Oth`, everything else empty, light theme.

Body (284 bytes) as hex, with the 246 zero bytes after the first highlight byte elided:

```
00                                 flags: light theme
21 [00 x246]                       highlights (247 bytes)
02                                 item count
01 04 07                           id 1, x=4, rot 0, y=7
02 64 07                           id 2, x=4 | (3<<5)=0x64, y=7
01 64 04 05 02 03                  tiles: 1 tile, id 100, x=4, y=5, w=2, h=3
01 02 04 74 72 61 70               legend: 1 entry, color 2, "trap"
01 33                              number "3"
05 56 61 75 6c 74                  title "Vault"
00                                 intro ""
00                                 notes ""
00                                 wandering monster id 0
00                                 wandering monster text ""
03 4f 74 68                        series "Oth"
```

One valid encoding (raw deflate from zlib level 9; other deflaters give other bytes):

```
#AWNQZBiRgImRhZ0phZ0xhYWViZmRiaWkKLGA0Zg1LLE0pwQkz-xfkgEA
```

## 9. Changing the format

- Until the first tagged release, change this document and the code together and replace the golden
  links.
- After the first release: bump the version byte for any change that old decoders cannot read,
  keep decoding every older version, add a golden link per version, and never reuse an icon id or
  highlight value.
