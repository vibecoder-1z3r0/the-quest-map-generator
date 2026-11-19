import { CELL } from "./constants.js";

// The build replaces the placeholder below with src/catalog.json.
export const CATALOG = /*@CATALOG@*/ [];
export const BY_ID = new Map(CATALOG.map((piece) => [piece.id, piece]));
export const GROUPS = [...new Set(CATALOG.map((piece) => piece.group))];
export const MONSTERS = CATALOG.filter((piece) => piece.monster);

// Footprint (width, height) in squares after rotation (0-3 clockwise quarter turns).
export function footprint(item) {
  const piece = BY_ID.get(item.id);
  return item.r % 2 === 1 ? [piece.h, piece.w] : [piece.w, piece.h];
}

export function iconSize(piece) {
  return [piece.w * CELL, piece.h * CELL];
}
