// SVG rendering of the map: board, highlights, pieces, coordinate labels and overlays.
import { roomSquares } from "./board.js";
import { BY_ID, footprint } from "./catalog.js";
import { CELL, COLS, HIGHLIGHTS, ROWS, ZONES } from "./constants.js";
import { itemVisibility, regionAnchor, regionSquares, squareVisible, stoneVisible } from "./hero.js";

export const MARGIN = 22;
const BOARD_W = COLS * CELL;
const BOARD_H = ROWS * CELL;

export function boardSkeleton() {
  const labels = [];
  for (let x = 0; x < COLS; x++) {
    labels.push(
      `<text x="${x * CELL + CELL / 2}" y="-8" text-anchor="middle">${String.fromCharCode(65 + x)}</text>`,
    );
  }
  for (let y = 0; y < ROWS; y++) {
    labels.push(`<text x="-8" y="${y * CELL + CELL / 2 + 4}" text-anchor="end">${y + 1}</text>`);
  }
  const roomLabels = [...roomSquares()].map(
    ([letter, squares]) =>
      `<text x="${squares[0].x * CELL + 5}" y="${squares[0].y * CELL + 13}">${letter}</text>`,
  );
  return `
    <defs>
      <pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
        <rect width="8" height="8" fill="#6f6f78" fill-opacity="0.55"/>
        <line x1="0" y1="0" x2="0" y2="8" stroke="#2b2b32" stroke-opacity="0.55" stroke-width="3"/>
      </pattern>
    </defs>
    <use href="#board-art" x="0" y="0" width="${BOARD_W}" height="${BOARD_H}"/>
    <g id="layer-rooms" class="room-labels">${roomLabels.join("")}</g>
    <g id="layer-tiles"></g>
    <g id="layer-zones"></g>
    <g id="layer-hl"></g>
    <g id="layer-items"></g>
    <g id="layer-fog"></g>
    <g id="layer-overlay" pointer-events="none"></g>
    <g id="layer-labels" class="coords">${labels.join("")}</g>`;
}

export function boardViewBox() {
  return `${-MARGIN} ${-MARGIN} ${BOARD_W + MARGIN * 2} ${BOARD_H + MARGIN * 2}`;
}

// The zone layer: a translucent tint in the zone's color under the highlights.
export function zonesMarkup(zones) {
  const out = [];
  for (let i = 0; i < zones.length; i++) {
    const zone = ZONES[zones[i] - 1];
    if (!zone) continue;
    const x = (i % COLS) * CELL;
    const y = Math.floor(i / COLS) * CELL;
    out.push(`<rect x="${x + 1}" y="${y + 1}" width="${CELL - 2}" height="${CELL - 2}" rx="4" fill="${zone.color}" fill-opacity="0.5"/>`);
  }
  return out.join("");
}

export function highlightMarkup(hl) {
  const out = [];
  for (let i = 0; i < hl.length; i++) {
    const v = hl[i];
    if (!v) continue;
    const x = (i % COLS) * CELL;
    const y = Math.floor(i / COLS) * CELL;
    const def = HIGHLIGHTS.find((h) => h.value === v);
    if (v === 1) {
      out.push(`<rect x="${x}" y="${y}" width="${CELL}" height="${CELL}" fill="url(#hatch)"/>`);
    } else if (def) {
      out.push(`<rect x="${x}" y="${y}" width="${CELL}" height="${CELL}" fill="${def.color}" fill-opacity="0.5"/>`);
    } else {
      out.push(
        `<rect x="${x + 1}" y="${y + 1}" width="${CELL - 2}" height="${CELL - 2}" fill="#888" fill-opacity="0.25" stroke="#666" stroke-dasharray="3 2"/>`,
      );
    }
  }
  return out.join("");
}

// A piece as a <use> of its sprite, rotated about the center of its rotated footprint.
export function itemMarkup(item, index) {
  const piece = BY_ID.get(item.id);
  const [fw, fh] = footprint(item);
  const cx = item.x * CELL + (fw * CELL) / 2;
  const cy = item.y * CELL + (fh * CELL) / 2;
  const w = piece.w * CELL;
  const h = piece.h * CELL;
  const transform = `translate(${cx} ${cy}) rotate(${item.r * 90}) translate(${-w / 2} ${-h / 2})`;
  const idx = index === undefined ? "" : ` data-i="${index}"`;
  return `<use href="#icon-${piece.slug}" width="${w}" height="${h}" transform="${transform}"${idx}/>`;
}

export function itemsMarkup(items) {
  return items.map((item, i) => itemMarkup(item, i)).join("");
}

export function outlineMarkup(item, cls) {
  const [fw, fh] = footprint(item);
  return `<rect class="${cls}" x="${item.x * CELL + 1}" y="${item.y * CELL + 1}" width="${fw * CELL - 2}" height="${fh * CELL - 2}" rx="3"/>`;
}

export function cellMarkup(x, y, cls) {
  return `<rect class="${cls}" x="${x * CELL}" y="${y * CELL}" width="${CELL}" height="${CELL}"/>`;
}


// A tile is its 1x1 style icon repeated across every square of the rectangle.
export function tileMarkup(tile) {
  const piece = BY_ID.get(tile.id);
  const out = [];
  for (let dy = 0; dy < tile.h; dy++) {
    for (let dx = 0; dx < tile.w; dx++) {
      out.push(
        `<use href="#icon-${piece.slug}" x="${(tile.x + dx) * CELL}" y="${(tile.y + dy) * CELL}" width="${CELL}" height="${CELL}"/>`,
      );
    }
  }
  return out.join("");
}

export function tilesMarkup(tiles) {
  return tiles.map(tileMarkup).join("");
}

export function rectOutlineMarkup(x, y, w, h, cls) {
  return `<rect class="${cls}" x="${x * CELL + 1}" y="${y * CELL + 1}" width="${w * CELL - 2}" height="${h * CELL - 2}" rx="3"/>`;
}

// ---------------------------------------------------------------- hero view
// Everything hidden from the heroes is covered by one flat, opaque shape (a single path, so there are
// no seams), with the printed room letters repeated on top.
export function fogMarkup(st) {
  const parts = [];
  for (let y = 0; y < ROWS; y++) {
    let x = 0;
    while (x < COLS) {
      if (squareVisible(st, x, y)) {
        x += 1;
        continue;
      }
      let run = 1;
      while (x + run < COLS && !squareVisible(st, x + run, y)) run += 1;
      parts.push(`M${x * CELL} ${y * CELL}h${run * CELL}v${CELL}h${-run * CELL}z`);
      x += run;
    }
  }
  if (!parts.length) return "";
  const letters = [...roomSquares()]
    .filter(([, squares]) => !squareVisible(st, squares[0].x, squares[0].y))
    .map(([letter, squares]) => `<text x="${squares[0].x * CELL + 5}" y="${squares[0].y * CELL + 13}">${letter}</text>`);
  return `<path d="${parts.join("")}" fill="#2b2118"/>${letters.join("")}`;
}

// Room tiles, solid stone and pieces, limited to what the heroes can see.
export function heroTilesMarkup(st) {
  const out = [];
  for (const tile of st.tiles) {
    const piece = BY_ID.get(tile.id);
    for (let dy = 0; dy < tile.h; dy++) {
      for (let dx = 0; dx < tile.w; dx++) {
        const x = tile.x + dx;
        const y = tile.y + dy;
        if (squareVisible(st, x, y)) {
          out.push(`<use href="#icon-${piece.slug}" x="${x * CELL}" y="${y * CELL}" width="${CELL}" height="${CELL}"/>`);
        }
      }
    }
  }
  return out.join("");
}

export function heroHighlightMarkup(st) {
  const out = [];
  for (let y = 0; y < ROWS; y++) {
    for (let x = 0; x < COLS; x++) {
      if (stoneVisible(st, x, y)) {
        out.push(`<rect x="${x * CELL}" y="${y * CELL}" width="${CELL}" height="${CELL}" fill="url(#hatch)"/>`);
      }
    }
  }
  return out.join("");
}

export function heroItemsMarkup(st) {
  const visible = itemVisibility(st);
  return st.items.map((item, i) => (visible[i] ? itemMarkup(item, i) : "")).join("");
}

// Editor badges for hero view: a dot on regions that have text, a tag on grouped ones, and the tint
// of the region whose card is open.
export function heroBadgesMarkup(st, activeRegion) {
  const out = [];
  if (activeRegion !== null) {
    for (const { x, y } of regionSquares(st, activeRegion)) out.push(cellMarkup(x, y, "hero-sel"));
  }
  for (const [key, rec] of Object.entries(st.rooms)) {
    const region = Number(key);
    const anchor = regionAnchor(st, region);
    if (!anchor) continue;
    const left = anchor.x * CELL;
    const top = anchor.y * CELL;
    if (rec.texts.some(Boolean)) {
      out.push(`<circle class="hero-dot" data-region="${region}" cx="${left + CELL - 7}" cy="${top + 7}" r="4.5"/>`);
    }
    if (rec.group) {
      out.push(`<text class="hero-group" data-region="${region}" x="${left + 3}" y="${top + CELL - 4}">G${rec.group}</text>`);
    }
  }
  return out.join("");
}
