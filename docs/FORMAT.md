# URL Format Specification

**Status: DRAFT, format version 1.** The format may change freely until the first tagged release.
After that, changes are additive and versioned, and every link ever issued must keep decoding (the
golden-link tests enforce this). This document is the contract; the code follows it.

A map is stored entirely in the URL **hash** (`#...`). The hash is never sent to a server.

```
https://example.com/quest-map/#AWNQZBiRgImRhZ0phZ2RiaWkKLGA0Zg1LLE0pwQkAwA
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
| 3 | Legend | `varint count` + entries |
| 4 | Quest number | string |
| 5 | Quest title | string |
| 6 | Intro | string |
| 7 | Zargon's notes | string |
| 8 | Wandering monster id | 1 byte |
| 9 | Wandering monster text | string |

### 4.0 Flags

One byte of view settings.

| Bits | Meaning |
|---|---|
| 0-3 | editor **theme** id, 0..15 |
| 4-7 | reserved (`0`) |

| Theme id | Theme |
|---|---|
| 0 | light (default) |
| 1 | dark |
| 2-15 | reserved for future themes |

Theme ids are permanent once assigned. A decoder that meets an unknown theme id shows the light
theme but keeps the id in the map, so it survives re-encoding.

The theme only affects the editor on screen. **Printing is always light**, whatever the theme id
says. Opening a link applies its theme; changing the theme updates the link but is not an undo step.

### 4.1 Highlights

494 squares, 4 bits each, packed two per byte: square `i` lives in byte `i >> 1`; even `i` uses the
**low** nibble and odd `i` the **high** nibble. The final byte's high nibble is unused (`0`).

| Value | Color |
|---|---|
| 0 | none |
| 1 | grey (solid rock) |
| 2 | orange |
| 3 | cyan |
| 4 | yellow |
| 5 | bright green |
| 6-15 | reserved |

Values are permanent once assigned. A decoder that meets a reserved value keeps it in the map (so it
survives re-encoding) and draws a neutral tint. A highlight is a translucent tint drawn over
whatever is in the square; it never hides anything.

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
- **Doors and secret doors** are ordinary 1x1 pieces. Their artwork sits on the **north** edge at
  rotation 0; rotation 1, 2 and 3 move it to the east, south and west edges. A door on the outer
  edge of the board is valid.
- **Order is the z-order.** Items are drawn in list order, so later items are on top. The editor
  always appends new items. Any number of items may share a square, including exact duplicates read
  from a link.
- The count is limited to 1024. A larger count makes the link invalid.
- An id the decoder does not know is skipped, with a warning, so newer links degrade gracefully.

### 4.3 Legend

Optional labels for highlight colors (for example "orange = pit trap area").

`varint count` (0..16), then per entry: one byte **color value** (1..15), then a **string** label
(at most 40 characters). A color appears at most once; if repeated, the last entry wins. Labels are
filtered like single-line text (§6).

### 4.4 Quest text

| Field | Kind | Limit (characters) |
|---|---|---|
| Quest number | single line, plain | 10 |
| Quest title | single line, plain | 160 |
| Intro | multi-line, bold/italics only | 2,500 |
| Zargon's notes | multi-line, markdown subset | 10,000 |
| Wandering monster text | single line, plain | 160 |

Limits count Unicode code points after filtering. A decoded field longer than its limit is
truncated and a warning is shown. The editor stops accepting input at the limit.

**Wandering monster** is the pair *(id, text)*. The id byte is `0` for none, or the icon id of a
monster piece from the catalog. If the id is `0` and the text is empty, the quest has no wandering
monster. A non-monster id is treated as `0` with a warning.

### 4.5 Markdown subset (Zargon's notes)

Headings `#`, `##`, `###`; bullet lists (`-`); numbered lists (`1.`); `**bold**`; `*italic*`; a
horizontal rule (`---`); pipe tables with a header separator row; backslash escapes (`\*`). No
nested lists, raw HTML, images or links. A single newline is a line break; each blank line beyond
the first adds one blank line of vertical space. The intro supports **only** bold and italics;
everything else shows literally. Rendering uses DOM text nodes only, never `innerHTML`.

## 5. Size limits (defensive decoding)

- The inflated body must not exceed **65,536 bytes** (64 KiB). Decompression must stop and the link
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
from `catalog.json`): id 1 at rotation 0, and id 2 at rotation 3. A legend entry `2 = "trap"`.
Quest number `3`, title `Vault`, everything else empty, light theme.

Body (274 bytes) as hex, with the 246 zero bytes after the first highlight byte elided:

```
00                                 flags: light theme
21 [00 x246]                       highlights (247 bytes)
02                                 item count
01 04 07                           id 1, x=4, rot 0, y=7
02 64 07                           id 2, x=4 | (3<<5)=0x64, y=7
01 02 04 74 72 61 70               legend: 1 entry, color 2, "trap"
01 33                              number "3"
05 56 61 75 6c 74                  title "Vault"
00                                 intro ""
00                                 notes ""
00                                 wandering monster id 0
00                                 wandering monster text ""
```

One valid encoding (raw deflate from zlib level 9; other deflaters give other bytes):

```
#AWNQZBiRgImRhZ0phZ2RiaWkKLGA0Zg1LLE0pwQkAwA
```

## 9. Changing the format

- Until the first tagged release, change this document and the code together and replace the golden
  links.
- After the first release: bump the version byte for any change that old decoders cannot read,
  keep decoding every older version, add a golden link per version, and never reuse an icon id or
  highlight value.
