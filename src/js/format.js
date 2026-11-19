// Link format, version 1. This file implements docs/FORMAT.md; keep the two in sync.
import { BY_ID, footprint } from "./catalog.js";
import {
  COLS,
  FORMAT_VERSION,
  LIMITS,
  MAX_BODY,
  MAX_ITEMS,
  MAX_TILES,
  MAX_PAYLOAD_CHARS,
  ROWS,
  SQUARES,
} from "./constants.js";
import { cleanText } from "./text.js";

const HIGHLIGHT_BYTES = Math.ceil(SQUARES / 2);

function toBase64Url(bytes) {
  let bin = "";
  for (let i = 0; i < bytes.length; i += 0x8000) {
    bin += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  }
  return btoa(bin).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function fromBase64Url(text) {
  if (!/^[A-Za-z0-9_-]*$/.test(text)) throw new Error("not a valid link");
  let s = text.replace(/-/g, "+").replace(/_/g, "/");
  while (s.length % 4) s += "=";
  const bin = atob(s);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

function pushVarint(out, n) {
  let v = n;
  while (v >= 0x80) {
    out.push((v & 0x7f) | 0x80);
    v = Math.floor(v / 128);
  }
  out.push(v);
}

function pushString(out, text) {
  const bytes = new TextEncoder().encode(text);
  pushVarint(out, bytes.length);
  for (const b of bytes) out.push(b);
}

async function deflate(bytes) {
  const stream = new Blob([bytes]).stream().pipeThrough(new CompressionStream("deflate-raw"));
  return new Uint8Array(await new Response(stream).arrayBuffer());
}

// Inflates at most `limit` bytes; stops reading and fails as soon as the limit is passed.
async function inflateLimited(bytes, limit) {
  const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream("deflate-raw"));
  const reader = stream.getReader();
  const chunks = [];
  let total = 0;
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    total += value.length;
    if (total > limit) {
      await reader.cancel();
      throw new Error("link is too large");
    }
    chunks.push(value);
  }
  const out = new Uint8Array(total);
  let pos = 0;
  for (const chunk of chunks) {
    out.set(chunk, pos);
    pos += chunk.length;
  }
  return out;
}

export function blankState() {
  return {
    theme: 0,
    hl: new Uint8Array(SQUARES),
    items: [],
    tiles: [],
    legend: {},
    num: "",
    title: "",
    intro: "",
    notes: "",
    wmId: 0,
    wmText: "",
  };
}

// Returns the link payload (without the leading #).
export async function encodeState(st) {
  const out = [st.theme & 0x0f];
  const hl = new Uint8Array(HIGHLIGHT_BYTES);
  for (let i = 0; i < SQUARES; i++) hl[i >> 1] |= (st.hl[i] & 15) << ((i & 1) * 4);
  for (const b of hl) out.push(b);
  pushVarint(out, st.items.length);
  for (const it of st.items) out.push(it.id, it.x | (it.r << 5), it.y);
  pushVarint(out, st.tiles.length);
  for (const t of st.tiles) out.push(t.id, t.x, t.y, t.w, t.h);
  const legend = Object.entries(st.legend)
    .filter(([color, label]) => label && Number(color) >= 2)
    .sort((a, b) => a[0] - b[0]);
  pushVarint(out, legend.length);
  for (const [color, label] of legend) {
    out.push(Number(color));
    pushString(out, label);
  }
  pushString(out, st.num);
  pushString(out, st.title);
  pushString(out, st.intro);
  pushString(out, st.notes);
  out.push(st.wmId);
  pushString(out, st.wmText);
  const body = new Uint8Array(out);
  if (body.length > MAX_BODY) throw new Error("quest is too large to store in a link");
  const packed = await deflate(body);
  const full = new Uint8Array(packed.length + 1);
  full[0] = FORMAT_VERSION;
  full.set(packed, 1);
  return toBase64Url(full);
}

class Reader {
  constructor(bytes) {
    this.b = bytes;
    this.p = 0;
  }

  need(n) {
    if (this.p + n > this.b.length) throw new Error("link is truncated");
  }

  byte() {
    this.need(1);
    return this.b[this.p++];
  }

  varint() {
    let n = 0;
    let scale = 1;
    for (let i = 0; i < 5; i++) {
      const b = this.byte();
      n += (b & 0x7f) * scale;
      if (!(b & 0x80)) return n;
      scale *= 128;
    }
    throw new Error("link is corrupt");
  }

  string() {
    const len = this.varint();
    this.need(len);
    const text = new TextDecoder("utf-8", { fatal: false }).decode(this.b.subarray(this.p, this.p + len));
    this.p += len;
    return text;
  }
}

// Decodes a payload (without the leading #). Throws on an invalid link.
// Returns { state, warnings } where warnings are non-fatal notices.
export async function decodeHash(payload) {
  if (payload.length > MAX_PAYLOAD_CHARS) throw new Error("link is too large");
  const full = fromBase64Url(payload);
  if (full.length < 2) throw new Error("link is empty or truncated");
  if (full[0] !== FORMAT_VERSION) throw new Error(`unsupported link version ${full[0]}`);
  const body = await inflateLimited(full.subarray(1), MAX_BODY);
  const r = new Reader(body);
  const st = blankState();
  const warnings = [];
  let stripped = false;

  st.theme = r.byte() & 0x0f;
  r.need(HIGHLIGHT_BYTES);
  for (let i = 0; i < SQUARES; i++) st.hl[i] = (r.b[r.p + (i >> 1)] >> ((i & 1) * 4)) & 15;
  r.p += HIGHLIGHT_BYTES;

  const count = r.varint();
  if (count > MAX_ITEMS) throw new Error("too many pieces");
  let skipped = 0;
  for (let n = 0; n < count; n++) {
    const id = r.byte();
    const b1 = r.byte();
    const y = r.byte() & 31;
    const item = { id, x: b1 & 31, y, r: (b1 >> 5) & 3 };
    if (!BY_ID.has(id) || BY_ID.get(id).tile) {
      skipped += 1;
      continue;
    }
    const [w, h] = footprint(item);
    if (item.x + w > COLS || item.y + h > ROWS) {
      skipped += 1;
      continue;
    }
    st.items.push(item);
  }
  if (skipped) warnings.push(`${skipped} piece(s) in this link could not be shown and were skipped.`);

  const tileCount = r.varint();
  if (tileCount > MAX_TILES) throw new Error("too many tiles");
  let skippedTiles = 0;
  for (let n = 0; n < tileCount; n++) {
    const tile = { id: r.byte(), x: r.byte(), y: r.byte(), w: r.byte(), h: r.byte() };
    const ok =
      BY_ID.get(tile.id)?.tile &&
      tile.w >= 1 &&
      tile.h >= 1 &&
      tile.x + tile.w <= COLS &&
      tile.y + tile.h <= ROWS;
    if (ok) st.tiles.push(tile);
    else skippedTiles += 1;
  }
  if (skippedTiles) warnings.push(`${skippedTiles} room tile(s) in this link could not be shown and were skipped.`);

  const legendCount = r.varint();
  if (legendCount > 16) throw new Error("link is corrupt");
  for (let n = 0; n < legendCount; n++) {
    const color = r.byte();
    const label = cleanText(r.string(), { limit: LIMITS.legend });
    stripped ||= label.removed;
    if (color >= 2 && color <= 15) st.legend[color] = label.text;
  }

  const field = (key, opts) => {
    const res = cleanText(r.string(), opts);
    stripped ||= res.removed;
    if (res.truncated) warnings.push(`The ${key} was too long and was shortened.`);
    return res.text;
  };
  st.num = field("quest number", { limit: LIMITS.num });
  st.title = field("quest title", { limit: LIMITS.title });
  st.intro = field("intro", { multiline: true, limit: LIMITS.intro });
  st.notes = field("notes", { multiline: true, limit: LIMITS.notes });
  const wmId = r.byte();
  st.wmText = field("wandering monster text", { limit: LIMITS.wmText });
  if (wmId === 0 || BY_ID.get(wmId)?.monster) {
    st.wmId = wmId;
  } else {
    warnings.push("The wandering monster in this link is not a monster and was ignored.");
  }
  if (stripped) warnings.push("Some unsupported characters in this link were removed.");
  return { state: st, warnings };
}
