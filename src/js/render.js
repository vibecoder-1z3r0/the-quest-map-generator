// SVG rendering of the map: board, highlights, pieces, coordinate labels and overlays.
import { BY_ID, footprint } from "./catalog.js";
import { CELL, COLS, HIGHLIGHTS, ROWS } from "./constants.js";

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
  return `
    <defs>
      <pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
        <rect width="8" height="8" fill="#6f6f78" fill-opacity="0.55"/>
        <line x1="0" y1="0" x2="0" y2="8" stroke="#2b2b32" stroke-opacity="0.55" stroke-width="3"/>
      </pattern>
    </defs>
    <use href="#board-art" x="0" y="0" width="${BOARD_W}" height="${BOARD_H}"/>
    <g id="layer-hl"></g>
    <g id="layer-items"></g>
    <g id="layer-overlay" pointer-events="none"></g>
    <g id="layer-labels" class="coords">${labels.join("")}</g>`;
}

export function boardViewBox() {
  return `${-MARGIN} ${-MARGIN} ${BOARD_W + MARGIN * 2} ${BOARD_H + MARGIN * 2}`;
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

