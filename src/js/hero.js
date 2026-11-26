// Hero view: regions, groups, visibility and the play actions. See docs/HERO_VIEW.md.
import { roomAt, isRoom } from "./board.js";
import { BY_ID } from "./catalog.js";
import { COLS, ROOM_REGIONS, ROWS, ZONES } from "./constants.js";

// A square's region: its room (regions 0-25 for A-Z), else its zone (26-35, from the zone layer),
// else null. A zone painted inside a room is ignored.
export function regionAt(st, x, y) {
  if (x < 0 || y < 0 || x >= COLS || y >= ROWS) return null;
  const ch = roomAt(x, y);
  if (isRoom(ch)) return ch.charCodeAt(0) - 65;
  const zone = st.zones[y * COLS + x];
  return zone >= 1 && zone <= ZONES.length ? ROOM_REGIONS + zone - 1 : null;
}

// The author's name for a region: "Room K", or the zone's legend name ("Zone 1" if unnamed).
export function regionName(st, region) {
  if (region < ROOM_REGIONS) return `Room ${String.fromCharCode(65 + region)}`;
  const zone = ZONES[region - ROOM_REGIONS];
  return st.legend[zone.legendKey] || zone.name;
}

// ---------------------------------------------------------------- play state
// st.play is null at the start of a game (exactly the "revealed at the start" regions are revealed) or
// { rev, t, tr, sd }: Sets of revealed regions and of regions searched for treasure, traps and secret
// doors. Once a game action changes anything, st.play becomes explicit; resetGame makes it null again.
function startPlay(st) {
  const rev = new Set();
  for (const [region, rec] of Object.entries(st.rooms)) if (rec.start) rev.add(Number(region));
  return { rev, t: new Set(), tr: new Set(), sd: new Set() };
}

function currentPlay(st) {
  return st.play ?? startPlay(st);
}

function editablePlay(st) {
  if (!st.play) st.play = startPlay(st);
  return st.play;
}

// The regions that reveal, hide and search together with `region` (itself when it has no group).
export function groupMembers(st, region) {
  const group = st.rooms[region]?.group ?? 0;
  if (!group) return [region];
  const members = new Set([region]);
  for (const [other, rec] of Object.entries(st.rooms)) if (rec.group === group) members.add(Number(other));
  return [...members].sort((a, b) => a - b);
}

export function isRevealed(st, region) {
  return currentPlay(st).rev.has(region);
}

// kind: "t" treasure, "tr" traps, "sd" secret doors.
export function isSearched(st, region, kind) {
  return currentPlay(st)[kind].has(region);
}

export function revealRegion(st, region) {
  const members = groupMembers(st, region);
  if (members.every((m) => isRevealed(st, m))) return false;
  const play = editablePlay(st);
  for (const m of members) play.rev.add(m);
  return true;
}

// Hides the group again and forgets its searches (this also works for a "revealed at the start" region).
export function hideRegion(st, region) {
  const members = groupMembers(st, region);
  const now = currentPlay(st);
  if (!members.some((m) => now.rev.has(m) || now.t.has(m) || now.tr.has(m) || now.sd.has(m))) return false;
  const play = editablePlay(st);
  for (const m of members) for (const key of ["rev", "t", "tr", "sd"]) play[key].delete(m);
  return true;
}

export function searchRegion(st, region, kind) {
  if (!isRevealed(st, region)) return false;
  const members = groupMembers(st, region);
  if (members.every((m) => isSearched(st, m, kind))) return false;
  const play = editablePlay(st);
  for (const m of members) play[kind].add(m);
  return true;
}

export function resetGame(st) {
  st.play = null;
}

// The texts shown for a region: those of its whole group, joined in region order, empty ones skipped.
export function regionTexts(st, region) {
  const members = groupMembers(st, region);
  const join = (k) =>
    members
      .map((m) => st.rooms[m]?.texts[k] ?? "")
      .filter(Boolean)
      .join("\n\n");
  return { readAloud: join(0), treasure: join(1), traps: join(2), secretDoors: join(3) };
}

// ---------------------------------------------------------------- what the heroes can see
// A square is visible when it belongs to no region (plain corridor) or its region is revealed.
export function squareVisible(st, x, y) {
  const region = regionAt(st, x, y);
  return region === null || isRevealed(st, region);
}

// Solid stone (grey) shows only where its square is visible, so hidden stone looks like any hidden area.
export function stoneVisible(st, x, y) {
  return st.hl[y * COLS + x] === 1 && squareVisible(st, x, y);
}

const EDGE_STEP = [
  [0, -1],
  [1, 0],
  [0, 1],
  [-1, 0],
];

function onBoard(x, y) {
  return x >= 0 && y >= 0 && x < COLS && y < ROWS;
}

// The squares an edge piece touches: its own and the one across the edge it sits on.
function edgeSides(item) {
  const [dx, dy] = EDGE_STEP[item.r];
  const sides = [[item.x, item.y]];
  if (onBoard(item.x + dx, item.y + dy)) sides.push([item.x + dx, item.y + dy]);
  return sides;
}

// The regions whose secret-door search reveals this secret door tile or hidden door (docs/HERO_VIEW.md).
export function secretOwners(st, item) {
  const piece = BY_ID.get(item.id);
  const squares = piece.edge ? edgeSides(item) : [[item.x, item.y]];
  let regions = squares.map(([x, y]) => regionAt(st, x, y)).filter((r) => r !== null);
  if (!piece.edge && regions.length === 0) {
    // A tile on a corridor square with no zone belongs to every region that shares a wall with it.
    regions = EDGE_STEP.map(([dx, dy]) => regionAt(st, item.x + dx, item.y + dy)).filter((r) => r !== null);
  }
  return [...new Set(regions)].sort((a, b) => a - b);
}

// For each piece (same order as st.items): whether the heroes can see it right now.
export function itemVisibility(st) {
  return st.items.map((item) => {
    const piece = BY_ID.get(item.id);
    if (piece.group === "Markers" || piece.slug.endsWith("-trap")) return false;
    if (item.id === 2 || item.id === 4) return secretOwners(st, item).some((r) => isSearched(st, r, "sd"));
    if (piece.edge) return edgeSides(item).some(([x, y]) => squareVisible(st, x, y));
    return squareVisible(st, item.x, item.y);
  });
}
