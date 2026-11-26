// Map state and the operations on it. Items are [id, x, y, rotation]; list order is z-order.
import { BY_ID, footprint } from "./catalog.js";
import { COLS, ROWS, SQUARES } from "./constants.js";

export const squareIndex = (x, y) => y * COLS + x;

// Board-style label: column letter + row number, e.g. x=4, y=7 is "E8".
export function squareLabel(x, y) {
  return String.fromCharCode(65 + x) + (y + 1);
}

export function cloneItems(items) {
  return items.map((it) => ({ ...it }));
}

// A snapshot is everything the undo history tracks (the theme is deliberately excluded).
export function snapshot(st) {
  return {
    hl: Uint8Array.from(st.hl),
    zones: Uint8Array.from(st.zones),
    items: cloneItems(st.items),
    tiles: cloneItems(st.tiles),
    legend: { ...st.legend },
    num: st.num,
    title: st.title,
    intro: st.intro,
    notes: st.notes,
    wmId: st.wmId,
    wmText: st.wmText,
    series: st.series,
  };
}

export function restore(st, snap) {
  st.hl = Uint8Array.from(snap.hl);
  st.zones = Uint8Array.from(snap.zones);
  st.items = cloneItems(snap.items);
  st.tiles = cloneItems(snap.tiles);
  st.legend = { ...snap.legend };
  st.num = snap.num;
  st.title = snap.title;
  st.intro = snap.intro;
  st.notes = snap.notes;
  st.wmId = snap.wmId;
  st.wmText = snap.wmText;
  st.series = snap.series;
}

const snapshotKey = (a) =>
  JSON.stringify([Array.from(a.hl), Array.from(a.zones), a.items, a.tiles, a.legend, a.num, a.title, a.intro, a.notes, a.wmId, a.wmText, a.series]);

export function sameSnapshot(a, b) {
  return snapshotKey(a) === snapshotKey(b);
}

export function clampPosition(item, x, y) {
  const [w, h] = footprint(item);
  return [Math.max(0, Math.min(COLS - w, x)), Math.max(0, Math.min(ROWS - h, y))];
}

// Appends a new piece on top. An exact duplicate is refused (returns -1).
export function placeItem(st, id, x, y, r) {
  const probe = { id, x: 0, y: 0, r };
  const [cx, cy] = clampPosition(probe, x, y);
  const item = { id, x: cx, y: cy, r };
  if (st.items.some((o) => o.id === id && o.x === cx && o.y === cy && o.r === r)) return -1;
  st.items.push(item);
  return st.items.length - 1;
}

export function moveItem(st, index, x, y) {
  const item = st.items[index];
  const [cx, cy] = clampPosition(item, x, y);
  if (cx === item.x && cy === item.y) return false;
  item.x = cx;
  item.y = cy;
  return true;
}

// Quarter turn clockwise about the footprint's center, kept on the board.
export function rotateItem(st, index) {
  const item = st.items[index];
  const piece = BY_ID.get(item.id);
  if (piece.w === 1 && piece.h === 1 && !piece.edge) {
    item.r = (item.r + 1) % 4;
    return true;
  }
  const [w, h] = footprint(item);
  const cx = item.x + w / 2;
  const cy = item.y + h / 2;
  item.r = (item.r + 1) % 4;
  const [nw, nh] = footprint(item);
  const [x, y] = clampPosition(item, Math.round(cx - nw / 2), Math.round(cy - nh / 2));
  item.x = x;
  item.y = y;
  return true;
}

export function removeItem(st, index) {
  st.items.splice(index, 1);
}

// Moves an item one step up (toward the top of the stack) or down in the list.
export function reorderItem(st, index, delta) {
  const target = index + delta;
  if (target < 0 || target >= st.items.length) return index;
  const [item] = st.items.splice(index, 1);
  st.items.splice(target, 0, item);
  return target;
}

// Indexes of the items covering a square, topmost first.
export function itemsAt(st, x, y) {
  const hits = [];
  for (let i = st.items.length - 1; i >= 0; i--) {
    const it = st.items[i];
    const [w, h] = footprint(it);
    if (x >= it.x && x < it.x + w && y >= it.y && y < it.y + h) hits.push(i);
  }
  return hits;
}

export function highlightAt(st, x, y) {
  return st.hl[squareIndex(x, y)];
}

export function setHighlight(st, x, y, value) {
  const i = squareIndex(x, y);
  if (i < 0 || i >= SQUARES || st.hl[i] === value) return false;
  st.hl[i] = value;
  return true;
}

export function setZone(st, x, y, value) {
  const i = squareIndex(x, y);
  if (i < 0 || i >= SQUARES || st.zones[i] === value) return false;
  st.zones[i] = value;
  return true;
}

export const EDGE_NAMES = ["north", "east", "south", "west"];

// ---------------------------------------------------------------- room tiles
// Tiles are resizable rectangles { id, x, y, w, h } in their own list, always drawn below pieces.

export function clampTile(tile, x, y, w, h) {
  const cw = Math.max(1, Math.min(COLS, w));
  const ch = Math.max(1, Math.min(ROWS, h));
  return { ...tile, x: Math.max(0, Math.min(COLS - cw, x)), y: Math.max(0, Math.min(ROWS - ch, y)), w: cw, h: ch };
}

export function addTile(st, id, x, y, w, h) {
  st.tiles.push(clampTile({ id }, x, y, w, h));
  return st.tiles.length - 1;
}

export function moveTile(st, index, x, y) {
  const tile = st.tiles[index];
  const next = clampTile(tile, x, y, tile.w, tile.h);
  if (next.x === tile.x && next.y === tile.y) return false;
  st.tiles[index] = next;
  return true;
}

// Keeps the top-left corner and limits the size to what fits on the board.
export function resizeTile(st, index, w, h) {
  const tile = st.tiles[index];
  const next = clampTile(tile, tile.x, tile.y, Math.min(w, COLS - tile.x), Math.min(h, ROWS - tile.y));
  if (next.w === tile.w && next.h === tile.h) return false;
  st.tiles[index] = next;
  return true;
}

export function removeTile(st, index) {
  st.tiles.splice(index, 1);
}

export function reorderTile(st, index, delta) {
  const target = index + delta;
  if (target < 0 || target >= st.tiles.length) return index;
  const [tile] = st.tiles.splice(index, 1);
  st.tiles.splice(target, 0, tile);
  return target;
}

// Indexes of the tiles covering a square, topmost first.
export function tilesAt(st, x, y) {
  const hits = [];
  for (let i = st.tiles.length - 1; i >= 0; i--) {
    const t = st.tiles[i];
    if (x >= t.x && x < t.x + t.w && y >= t.y && y < t.y + t.h) hits.push(i);
  }
  return hits;
}
