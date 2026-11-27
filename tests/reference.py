"""Independent reference implementation of docs/FORMAT.md (version 1) in Python.

Used to prove the JavaScript matches the written spec, and to produce golden links. Deliberately
shares no code with the app.
"""

from __future__ import annotations

import base64
import zlib

COLS, ROWS = 26, 19
SQUARES = COLS * ROWS
VERSION = 1
REGIONS = 56  # rooms A-Z are regions 0-25, zones 1-30 are regions 26-55
ZONES = 30
ROOM_TEXTS = 4  # read aloud, treasure, traps, secret doors
PLAY_BYTES = 4 * ((REGIONS + 7) // 8)  # revealed, treasure, traps, secret-door masks (28 bytes)


def varint(n: int) -> bytes:
    out = bytearray()
    while n >= 0x80:
        out.append((n & 0x7F) | 0x80)
        n >>= 7
    out.append(n)
    return bytes(out)


def string(text: str) -> bytes:
    raw = text.encode("utf-8")
    return varint(len(raw)) + raw


def blank() -> dict:
    return {
        "theme": 0,
        "hl": [0] * SQUARES,
        "items": [],
        "tiles": [],
        "legend": {},
        "num": "",
        "title": "",
        "intro": "",
        "notes": "",
        "wm_id": 0,
        "wm_text": "",
        "series": "",
        "hero": False,
        "zones": [0] * SQUARES,  # 0 none, 1-30 zone n
        "rooms": {},  # region -> {"start": bool, "group": int, "texts": [4 strings]}
        "play": None,  # None, or {"rev": [regions], "t": [...], "tr": [...], "sd": [...]}
    }


def mask(regions, count: int = REGIONS) -> bytes:
    out = bytearray((count + 7) // 8)
    for r in regions:
        out[r >> 3] |= 1 << (r & 7)
    return bytes(out)


def unmask(data: bytes, count: int = REGIONS) -> list[int]:
    return [r for r in range(count) if data[r >> 3] >> (r & 7) & 1]


def encode_body(st: dict) -> bytes:
    hl = bytearray((SQUARES + 1) // 2)
    for i, v in enumerate(st["hl"]):
        hl[i >> 1] |= (v & 15) << ((i & 1) * 4)
    out = bytearray([(st["theme"] & 15) | (0x10 if st.get("hero") else 0)]) + hl
    out += varint(len(st["items"]))
    for item_id, x, y, r in st["items"]:
        out += bytes([item_id, x | (r << 5), y])
    out += varint(len(st["tiles"]))
    for tile_id, x, y, w, h in st["tiles"]:
        out += bytes([tile_id, x, y, w, h])
    legend = sorted((int(k), v) for k, v in st["legend"].items() if v and int(k) >= 2)
    out += varint(len(legend))
    for color, label in legend:
        out += bytes([color]) + string(label)
    for key in ("num", "title", "intro", "notes"):
        out += string(st[key])
    out += bytes([st["wm_id"]]) + string(st["wm_text"])
    out += string(st["series"])
    rooms, play = st.get("rooms") or {}, st.get("play")
    zones = st.get("zones") or [0] * SQUARES
    if (
        rooms or play or any(zones)
    ):  # optional trailing sections: omitted entirely when there is nothing to say
        out += bytes(zones)  # one byte per square: 0 none, 1-30 zone n
        out += varint(len(rooms))
        for region in sorted(rooms):
            rec = rooms[region]
            out += bytes([region, 1 if rec.get("start") else 0, rec.get("group", 0)])
            for text in rec.get("texts", [""] * ROOM_TEXTS):
                out += string(text)
        if play:
            for key in ("rev", "t", "tr", "sd"):
                out += mask(play[key])
    return bytes(out)


def encode(st: dict) -> str:
    comp = zlib.compressobj(9, zlib.DEFLATED, -15)
    packed = comp.compress(encode_body(st)) + comp.flush()
    return base64.urlsafe_b64encode(bytes([VERSION]) + packed).rstrip(b"=").decode()


def raw_payload(body: bytes, version: int = VERSION) -> str:
    comp = zlib.compressobj(9, zlib.DEFLATED, -15)
    packed = comp.compress(body) + comp.flush()
    return base64.urlsafe_b64encode(bytes([version]) + packed).rstrip(b"=").decode()


def decode(payload: str) -> dict:
    data = base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4))
    assert data[0] == VERSION
    body = zlib.decompress(data[1:], -15)
    pos = 0

    def byte() -> int:
        nonlocal pos
        pos += 1
        return body[pos - 1]

    def read_varint() -> int:
        n = shift = 0
        while True:
            b = byte()
            n |= (b & 0x7F) << shift
            shift += 7
            if not b & 0x80:
                return n

    def read_string() -> str:
        nonlocal pos
        length = read_varint()
        text = body[pos : pos + length].decode("utf-8")
        pos += length
        return text

    st = blank()
    flags = byte()
    st["theme"] = flags & 15
    st["hero"] = bool(flags & 0x10)
    hl_bytes = body[pos : pos + (SQUARES + 1) // 2]
    pos += len(hl_bytes)
    st["hl"] = [(hl_bytes[i >> 1] >> ((i & 1) * 4)) & 15 for i in range(SQUARES)]
    for _ in range(read_varint()):
        item_id, b1, y = byte(), byte(), byte()
        st["items"].append((item_id, b1 & 31, y & 31, (b1 >> 5) & 3))
    for _ in range(read_varint()):
        st["tiles"].append((byte(), byte(), byte(), byte(), byte()))
    for _ in range(read_varint()):
        color = byte()
        st["legend"][color] = read_string()
    for key in ("num", "title", "intro", "notes"):
        st[key] = read_string()
    st["wm_id"] = byte()
    st["wm_text"] = read_string()
    if pos < len(body):  # optional trailing field; older links end before it
        st["series"] = read_string()
    if pos < len(body):  # optional hero view data: the zone layer, then the room records
        st["zones"] = list(body[pos : pos + SQUARES])
        pos += SQUARES
        for _ in range(read_varint()):
            region, flags, group = byte(), byte(), byte()
            st["rooms"][region] = {
                "start": bool(flags & 1),
                "group": group,
                "texts": [read_string() for _ in range(ROOM_TEXTS)],
            }
    if pos < len(body):  # optional play state
        size = (REGIONS + 7) // 8
        masks = [body[pos + i * size : pos + (i + 1) * size] for i in range(4)]
        play = (unmask(m) for m in masks)
        st["play"] = dict(zip(("rev", "t", "tr", "sd"), play, strict=True))
        pos += 4 * size
    return st
