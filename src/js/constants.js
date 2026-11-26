// Shared constants. See docs/FORMAT.md for what the numbers mean in the link format.
export const COLS = 26;
export const ROWS = 19;
export const CELL = 32;
export const SQUARES = COLS * ROWS;
export const FORMAT_VERSION = 1;
export const MAX_BODY = 262144;
export const MAX_PAYLOAD_CHARS = 200000;
export const MAX_ITEMS = 1024;
export const MAX_TILES = 256;
export const SOFT_LINK_LIMIT = 2000;

export const LIMITS = {
  series: 160,
  num: 10,
  title: 160,
  intro: 2500,
  notes: 10000,
  wmText: 160,
  legend: 40,
  roomText: 600,
};

// Hero view regions (docs/FORMAT.md 4.7): rooms A-Z are regions 0-25, zones 1-10 are regions 26-35
// and come from the highlight values 6-15.
export const ROOM_REGIONS = 26;
export const ZONE_FIRST_VALUE = 6;
export const REGIONS = 36;
export const ROOM_TEXT_KINDS = ["Read aloud", "Search for treasure", "Search for traps", "Search for secret doors"];

// Highlight values are permanent once assigned (docs/FORMAT.md section 4.1).
export const HIGHLIGHTS = [
  { value: 0, name: "None", color: null },
  // Grey is always "Solid stone" and has no editable legend. Orange means a trap of any kind.
  { value: 1, name: "Grey (solid stone)", color: "#6f6f78", fixedLabel: "Solid stone" },
  { value: 2, name: "Orange (trap)", color: "#f08a1c", defaultLabel: "Trap" },
  { value: 3, name: "Cyan", color: "#18b8d0" },
  { value: 4, name: "Yellow", color: "#f2d21b" },
  { value: 5, name: "Bright green", color: "#3fd24a" },
];

export const ZONE_COLORS = [
  "#8e5bd9",
  "#e0457b",
  "#2f9e8f",
  "#a8602a",
  "#5b7be0",
  "#7a8f2f",
  "#d94f4f",
  "#4fb3e0",
  "#c58be8",
  "#c9a66b",
];
// The ten hero view zones: their own per-square layer (docs/FORMAT.md 4.7), so a square can be solid
// stone or a trap highlight and in a zone at once. Zone n is named by legend entry 5 + n.
export const ZONES = ZONE_COLORS.map((color, i) => ({ n: i + 1, color, legendKey: ZONE_FIRST_VALUE + i, name: `Zone ${i + 1}` }));

// Theme ids are permanent. printSafe themes print as themselves; others print as theme 0.
export const THEMES = [
  { id: 0, slug: "light", name: "Light", printSafe: true },
  { id: 1, slug: "dark", name: "Dark", printSafe: false },
];

export const MIN_BROWSERS = "Chrome 103, Edge 103, Safari 16.4 or Firefox 113";
