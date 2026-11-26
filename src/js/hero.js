// Hero view: regions, groups, visibility and the play actions. See docs/HERO_VIEW.md.
import { roomAt, isRoom } from "./board.js";
import { COLS, HIGHLIGHTS, ROOM_REGIONS, ROWS, ZONE_FIRST_VALUE } from "./constants.js";

// A square's region: its room (regions 0-25 for A-Z), else its zone (26-35, painted with highlight
// values 6-15), else null. A zone painted inside a room is ignored.
export function regionAt(st, x, y) {
  if (x < 0 || y < 0 || x >= COLS || y >= ROWS) return null;
  const ch = roomAt(x, y);
  if (isRoom(ch)) return ch.charCodeAt(0) - 65;
  const value = st.hl[y * COLS + x];
  if (value >= ZONE_FIRST_VALUE && value < ZONE_FIRST_VALUE + 10) return ROOM_REGIONS + (value - ZONE_FIRST_VALUE);
  return null;
}

// The author's name for a region: "Room K", or the zone's legend name ("Zone 1" if unnamed).
export function regionName(st, region) {
  if (region < ROOM_REGIONS) return `Room ${String.fromCharCode(65 + region)}`;
  const value = ZONE_FIRST_VALUE + (region - ROOM_REGIONS);
  return st.legend[value] || HIGHLIGHTS.find((h) => h.value === value)?.defaultLabel || `Zone ${region - ROOM_REGIONS + 1}`;
}
