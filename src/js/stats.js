// Quest statistics, derived from the placed monsters and the board's room map.
// Counted: monsters on the map. Not counted: the wandering monster (shown separately) and anything
// described only in the notes. Every monster counts at its catalog body points (BP).
import { BY_ID } from "./catalog.js";
import { isRoom, roomAt, roomSquares } from "./board.js";
import { COLS } from "./constants.js";

export function computeStats(state) {
  const rooms = roomSquares();
  const byRoom = new Map(); // room letter -> { count, bp }
  const byType = new Map(); // monster id -> { name, count, bp }
  const corridor = { count: 0, bp: 0 };
  const total = { count: 0, bp: 0 };
  const missing = new Set(); // monster names without a BP value

  for (const item of state.items) {
    const piece = BY_ID.get(item.id);
    if (!piece?.monster) continue;
    const known = typeof piece.bp === "number";
    if (!known) missing.add(piece.name);
    const bp = known ? piece.bp : 0;
    total.count += 1;
    total.bp += bp;
    const type = byType.get(piece.id) ?? { name: piece.name, count: 0, bp: 0 };
    type.count += 1;
    type.bp += bp;
    byType.set(piece.id, type);
    const room = roomAt(item.x, item.y);
    if (isRoom(room)) {
      const entry = byRoom.get(room) ?? { count: 0, bp: 0 };
      entry.count += 1;
      entry.bp += bp;
      byRoom.set(room, entry);
    } else {
      corridor.count += 1;
      corridor.bp += bp;
    }
  }

  // A room is active when none of its squares is highlighted grey (value 1).
  const activeRooms = [];
  for (const [letter, squares] of rooms) {
    if (!squares.some((s) => state.hl[s.y * COLS + s.x] === 1)) activeRooms.push(letter);
  }
  const roomBp = (letter) => byRoom.get(letter)?.bp ?? 0;
  const activeTotal = activeRooms.reduce((sum, letter) => sum + roomBp(letter), 0);
  const occupied = [...byRoom.keys()];
  const occupiedTotal = occupied.reduce((sum, letter) => sum + roomBp(letter), 0);
  const top = occupied.length ? Math.max(...occupied.map(roomBp)) : 0;

  const monster = BY_ID.get(state.wmId);
  return {
    monsters: total.count,
    bp: total.bp,
    bpKnown: missing.size === 0,
    missing: [...missing],
    activeRooms,
    averageActive: activeRooms.length ? activeTotal / activeRooms.length : null,
    occupiedRooms: occupied.sort(),
    averageOccupied: occupied.length ? occupiedTotal / occupied.length : null,
    highest: occupied.length ? { bp: top, rooms: occupied.filter((l) => roomBp(l) === top).sort() } : null,
    corridor,
    types: [...byType.values()],
    wandering: {
      monster: monster?.monster ? monster.name : "",
      bp: monster?.monster && typeof monster.bp === "number" ? monster.bp : null,
      text: state.wmText,
    },
  };
}
