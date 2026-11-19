// The fixed board's room map. The build replaces the placeholder with src/board.txt.
import { COLS, ROWS } from "./constants.js";

export const BOARD_ROWS = /*@BOARD@*/ [];

// "." corridor, "#" solid, "A".."Z" a room.
export function roomAt(x, y) {
  return BOARD_ROWS[y]?.[x] ?? ".";
}

export function isRoom(ch) {
  return ch >= "A" && ch <= "Z";
}

// Room letter -> list of { x, y } squares.
export function roomSquares() {
  const rooms = new Map();
  for (let y = 0; y < ROWS; y++) {
    for (let x = 0; x < COLS; x++) {
      const ch = roomAt(x, y);
      if (!isRoom(ch)) continue;
      if (!rooms.has(ch)) rooms.set(ch, []);
      rooms.get(ch).push({ x, y });
    }
  }
  return rooms;
}
