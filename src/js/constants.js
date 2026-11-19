// Shared constants. See docs/FORMAT.md for what the numbers mean in the link format.
export const COLS = 26;
export const ROWS = 19;
export const CELL = 32;
export const SQUARES = COLS * ROWS;
export const FORMAT_VERSION = 1;
export const MAX_BODY = 65536;
export const MAX_PAYLOAD_CHARS = 200000;
export const MAX_ITEMS = 1024;
export const SOFT_LINK_LIMIT = 2000;

export const LIMITS = { num: 10, title: 160, intro: 2500, notes: 10000, wmText: 160, legend: 40 };

// Highlight values are permanent once assigned (docs/FORMAT.md section 4.1).
export const HIGHLIGHTS = [
  { value: 0, name: "None", color: null },
  { value: 1, name: "Grey (solid rock)", color: "#6f6f78" },
  { value: 2, name: "Orange", color: "#f08a1c" },
  { value: 3, name: "Cyan", color: "#18b8d0" },
  { value: 4, name: "Yellow", color: "#f2d21b" },
  { value: 5, name: "Bright green", color: "#3fd24a" },
];

// Theme ids are permanent. printSafe themes print as themselves; others print as theme 0.
export const THEMES = [
  { id: 0, slug: "light", name: "Light", printSafe: true },
  { id: 1, slug: "dark", name: "Dark", printSafe: false },
];

export const MIN_BROWSERS = "Chrome 103, Edge 103, Safari 16.4 or Firefox 113";
