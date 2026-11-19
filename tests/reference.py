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
        "legend": {},
        "num": "",
        "title": "",
        "intro": "",
        "notes": "",
        "wm_id": 0,
        "wm_text": "",
    }


def encode_body(st: dict) -> bytes:
    hl = bytearray((SQUARES + 1) // 2)
    for i, v in enumerate(st["hl"]):
        hl[i >> 1] |= (v & 15) << ((i & 1) * 4)
    out = bytearray([st["theme"] & 15]) + hl
    out += varint(len(st["items"]))
    for item_id, x, y, r in st["items"]:
        out += bytes([item_id, x | (r << 5), y])
    legend = sorted((int(k), v) for k, v in st["legend"].items() if v)
    out += varint(len(legend))
    for color, label in legend:
        out += bytes([color]) + string(label)
    for key in ("num", "title", "intro", "notes"):
        out += string(st[key])
    out += bytes([st["wm_id"]]) + string(st["wm_text"])
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
    st["theme"] = byte() & 15
    hl_bytes = body[pos : pos + (SQUARES + 1) // 2]
    pos += len(hl_bytes)
    st["hl"] = [(hl_bytes[i >> 1] >> ((i & 1) * 4)) & 15 for i in range(SQUARES)]
    for _ in range(read_varint()):
        item_id, b1, y = byte(), byte(), byte()
        st["items"].append((item_id, b1 & 31, y & 31, (b1 >> 5) & 3))
    for _ in range(read_varint()):
        color = byte()
        st["legend"][color] = read_string()
    for key in ("num", "title", "intro", "notes"):
        st[key] = read_string()
    st["wm_id"] = byte()
    st["wm_text"] = read_string()
    return st
