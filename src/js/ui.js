// The editor: tools, pointer handling, inspector, quest fields, history and URL sync.
import { BY_ID, CATALOG, GROUPS, MONSTERS, footprint } from "./catalog.js";
import {
  CELL,
  COLS,
  HIGHLIGHTS,
  LIMITS,
  MIN_BROWSERS,
  ROOM_REGIONS,
  ROWS,
  SOFT_LINK_LIMIT,
  THEMES,
  ZONES,
} from "./constants.js";
import { blankState, decodeHash, encodeState } from "./format.js";
import {
  chooserRegions,
  editRoom,
  hideRegion,
  isRevealed,
  isSearched,
  regionAt,
  regionName,
  regionTexts,
  resetGame,
  revealRegion,
  searchRegion,
  setGroupMember,
  totalRoomText,
} from "./hero.js";
import { renderIntro, renderNotes } from "./markdown.js";
import { computeStats } from "./stats.js";
import {
  boardSkeleton,
  boardViewBox,
  cellMarkup,
  fogMarkup,
  heroBadgesMarkup,
  heroHighlightMarkup,
  heroItemsMarkup,
  heroTilesMarkup,
  highlightMarkup,
  itemMarkup,
  itemsMarkup,
  outlineMarkup,
  rectOutlineMarkup,
  tileMarkup,
  tilesMarkup,
  zonesMarkup,
} from "./render.js";
import {
  EDGE_NAMES,
  addTile,
  highlightAt,
  itemsAt,
  moveItem,
  moveTile,
  placeItem,
  removeItem,
  removeTile,
  reorderItem,
  reorderTile,
  resizeTile,
  restore,
  rotateItem,
  sameSnapshot,
  setHighlight,
  setZone,
  snapshot,
  squareLabel,
  tilesAt,
} from "./state.js";
import { cleanText } from "./text.js";

const $ = (selector) => document.querySelector(selector);

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (key === "class") node.className = value;
    else if (key === "text") node.textContent = value;
    else if (value === true) node.setAttribute(key, "");
    else if (value !== false && value !== null && value !== undefined) node.setAttribute(key, value);
  }
  for (const child of children) node.append(child);
  return node;
}

export const app = {
  state: blankState(),
  tool: { kind: "select", value: 0 },
  selected: -1,
  selectedTile: -1,
  tileDraw: null,
  pinned: null,
  hover: null,
  ghostRot: 0,
  inside: false,
  drag: null,
  paint: null,
  zoom: 1,
  past: [],
  future: [],
  editable: true,
  heroRegion: null, // the region whose panel hero view shows
  heroCell: null, // the square the heroes tapped (only that square is highlighted for a hallway)
  editRegion: null, // the region whose hero view data card the editor shows
  shownRegion: null,
};

// ---------------------------------------------------------------- theme
function themeSlug(id) {
  return (THEMES.find((t) => t.id === id) || THEMES[0]).slug;
}

function applyTheme() {
  document.documentElement.dataset.theme = themeSlug(app.state.theme);
  const select = $("#theme");
  if (select.value !== String(app.state.theme)) {
    select.value = THEMES.some((t) => t.id === app.state.theme) ? String(app.state.theme) : "0";
  }
}

// ---------------------------------------------------------------- banner and link info
function showBanner(messages, isError) {
  const banner = $("#banner");
  if (!messages.length) {
    banner.hidden = true;
    return;
  }
  banner.textContent = messages.join(" ");
  banner.className = isError ? "error" : "";
  banner.hidden = false;
}

function updateLinkInfo() {
  const info = $("#linkinfo");
  const length = location.href.length;
  const long = length > SOFT_LINK_LIMIT;
  info.textContent = long
    ? `Link length: ${length.toLocaleString()} characters. Some chat apps may cut links this long.`
    : `Link length: ${length.toLocaleString()} characters`;
  info.classList.toggle("warn", long);
}

// ---------------------------------------------------------------- URL sync
let urlSeq = 0;
let pendingPush = false;
let urlTimer = 0;
let lastHash = "";

function scheduleUrl(push, delay = 0) {
  pendingPush ||= push;
  clearTimeout(urlTimer);
  urlTimer = setTimeout(syncUrl, delay);
}

export async function syncUrl() {
  clearTimeout(urlTimer);
  const mine = ++urlSeq;
  let hash;
  try {
    hash = `#${await encodeState(app.state)}`;
  } catch (error) {
    showBanner([`Could not store this map in a link: ${error.message}.`], true);
    return;
  }
  if (mine !== urlSeq) return;
  const push = pendingPush;
  pendingPush = false;
  if (hash !== lastHash) {
    lastHash = hash;
    if (push) history.pushState(null, "", hash);
    else history.replaceState(null, "", hash);
  }
  updateLinkInfo();
}

export async function loadFromHash() {
  const hash = location.hash;
  if (hash === lastHash) return;
  lastHash = hash;
  if (hash.length <= 1) {
    app.state = blankState();
    showBanner([], false);
  } else {
    try {
      const { state, warnings } = await decodeHash(hash.slice(1));
      app.state = state;
      showBanner(warnings, false);
    } catch (error) {
      app.state = blankState();
      showBanner([`Couldn't read a map from this link (${error.message}). Starting with a blank map.`], true);
    }
  }
  app.selected = -1;
  app.selectedTile = -1;
  app.pinned = null;
  app.heroRegion = null;
  app.heroCell = null;
  app.editRegion = null;
  app.past = [];
  app.future = [];
  app.baseline = snapshot(app.state);
  syncFields();
  applyTheme();
  renderAll();
  updateLinkInfo();
}

// ---------------------------------------------------------------- history
function commit() {
  const snap = snapshot(app.state);
  if (app.baseline && sameSnapshot(snap, app.baseline)) {
    renderAll();
    return;
  }
  if (app.baseline) app.past.push(app.baseline);
  if (app.past.length > 200) app.past.shift();
  app.future = [];
  app.baseline = snap;
  scheduleUrl(true);
  renderAll();
}

function undo() {
  flushTextCommit();
  if (!app.past.length) return;
  app.future.push(app.baseline);
  app.baseline = app.past.pop();
  restore(app.state, app.baseline);
  afterHistoryJump();
}

function redo() {
  flushTextCommit();
  if (!app.future.length) return;
  app.past.push(app.baseline);
  app.baseline = app.future.pop();
  restore(app.state, app.baseline);
  afterHistoryJump();
}

function afterHistoryJump() {
  app.selected = -1;
  app.selectedTile = -1;
  syncFields();
  scheduleUrl(false);
  renderAll();
}

let textTimer = 0;
function flushTextCommit() {
  if (!textTimer) return;
  clearTimeout(textTimer);
  textTimer = 0;
  commit();
}

// ---------------------------------------------------------------- geometry
function boardPoint(event) {
  const svg = $("#board");
  const matrix = svg.getScreenCTM();
  if (!matrix) return null;
  const point = new DOMPoint(event.clientX, event.clientY).matrixTransform(matrix.inverse());
  return { px: point.x, py: point.y };
}

function cellAt(event) {
  const p = boardPoint(event);
  if (!p) return null;
  const x = Math.floor(p.px / CELL);
  const y = Math.floor(p.py / CELL);
  if (x < 0 || y < 0 || x >= COLS || y >= ROWS) return null;
  return { x, y, fx: p.px / CELL - x, fy: p.py / CELL - y };
}

// Nearest edge of a square as a rotation (0 north, 1 east, 2 south, 3 west).
function nearestEdge(cell) {
  const d = [cell.fy, 1 - cell.fx, 1 - cell.fy, cell.fx];
  return d.indexOf(Math.min(...d));
}

function ghostItem() {
  if (app.tool.kind !== "piece" || !app.hover) return null;
  const piece = BY_ID.get(app.tool.value);
  const r = piece.edge ? app.hover.edge : app.ghostRot;
  return { id: piece.id, x: app.hover.x, y: app.hover.y, r };
}

// ---------------------------------------------------------------- rendering
function renderMap() {
  const hero = app.state.hero;
  $("#layer-tiles").innerHTML = hero ? heroTilesMarkup(app.state) : tilesMarkup(app.state.tiles);
  $("#layer-zones").innerHTML = hero ? "" : zonesMarkup(app.state.zones);
  $("#layer-hl").innerHTML = hero ? heroHighlightMarkup(app.state) : highlightMarkup(app.state.hl);
  $("#layer-items").innerHTML = hero ? heroItemsMarkup(app.state) : itemsMarkup(app.state.items);
  $("#layer-fog").innerHTML = hero ? fogMarkup(app.state) : "";
}

function renderOverlay() {
  if (app.state.hero) {
    // A room is highlighted whole (its shape is printed on the board). A hallway is never highlighted
    // beyond the tapped square, because the extent of a zone would give the map away.
    let marks = "";
    if (app.heroCell) {
      if (app.heroRegion !== null && app.heroRegion < ROOM_REGIONS) {
        for (let y = 0; y < ROWS; y++) {
          for (let x = 0; x < COLS; x++) {
            if (regionAt(app.state, x, y) === app.heroRegion) marks += cellMarkup(x, y, "hero-sel");
          }
        }
      } else {
        marks = cellMarkup(app.heroCell.x, app.heroCell.y, "hero-sel");
      }
    }
    $("#layer-overlay").innerHTML = marks;
    return;
  }
  let out = heroBadgesMarkup(app.state, app.editRegion);
  const view = app.pinned || app.hover;
  if (app.pinned) out += cellMarkup(app.pinned.x, app.pinned.y, "pinned");
  if (app.hover && app.inside && !app.drag && !app.paint && app.pointerType !== "touch") {
    if (app.tool.kind !== "piece") out += cellMarkup(app.hover.x, app.hover.y, "hover");
    const ghost = ghostItem();
    if (ghost) {
      const clamped = { ...ghost };
      const [fw, fh] = footprint(clamped);
      clamped.x = Math.max(0, Math.min(COLS - fw, clamped.x));
      clamped.y = Math.max(0, Math.min(ROWS - fh, clamped.y));
      out += `<g class="ghost">${itemMarkup(clamped)}</g>`;
    }
  }
  if (app.tileDraw) {
    const { x, y, w, h, id } = app.tileDraw;
    out += `<g class="ghost">${tileMarkup({ id, x, y, w, h })}</g>${rectOutlineMarkup(x, y, w, h, "selected")}`;
  }
  if (app.selected >= 0 && app.state.items[app.selected]) {
    out += outlineMarkup(app.state.items[app.selected], "selected");
  }
  const tile = app.state.tiles[app.selectedTile];
  if (tile) out += rectOutlineMarkup(tile.x, tile.y, tile.w, tile.h, "selected");
  $("#layer-overlay").innerHTML = out;
  return view;
}

function pieceLine(item) {
  const piece = BY_ID.get(item.id);
  const [w, h] = footprint(item);
  const parts = [`${w}×${h}`];
  if (piece.edge) parts.push(`${EDGE_NAMES[item.r]} edge`);
  else if (item.r) parts.push(`rotated ${item.r * 90}°`);
  parts.push(`anchor ${squareLabel(item.x, item.y)}`);
  return parts.join(" · ");
}

function stackButton(label, title, handler) {
  const button = el("button", { type: "button", title, text: label });
  button.addEventListener("click", handler);
  return button;
}

function pieceStack(hits) {
  const list = el("ol", { class: "stack", "aria-label": "Pieces here, top first" });
  hits.forEach((index, position) => {
    const item = app.state.items[index];
    const piece = BY_ID.get(item.id);
    const li = el("li", { class: index === app.selected ? "sel" : "" });
    const name = el("div", { class: "name", text: piece.name });
    name.addEventListener("click", () => selectItem(index));
    li.append(name, el("div", { class: "meta", text: pieceLine(item) }));
    const buttons = el("div", { class: "btns" });
    const above = hits[position - 1];
    const below = hits[position + 1];
    const forward = stackButton("Forward", "Bring forward", () => reorderTo(index, above));
    forward.disabled = above === undefined;
    const back = stackButton("Back", "Send back", () => reorderTo(index, below));
    back.disabled = below === undefined;
    buttons.append(
      forward,
      back,
      stackButton("Rotate", "Rotate a quarter turn clockwise", () => rotateAt(index)),
      stackButton("\u2190", "Move left", () => nudgeAt(index, -1, 0)),
      stackButton("\u2191", "Move up", () => nudgeAt(index, 0, -1)),
      stackButton("\u2193", "Move down", () => nudgeAt(index, 0, 1)),
      stackButton("\u2192", "Move right", () => nudgeAt(index, 1, 0)),
      stackButton("Remove", "Remove this piece", () => removeAt(index)),
    );
    li.append(buttons);
    list.append(li);
  });
  return list;
}

function sizeInput(label, value, max, onChange) {
  const input = el("input", { type: "number", min: "1", max: String(max), value: String(value), "aria-label": label });
  input.addEventListener("change", () => onChange(Math.max(1, Math.min(max, Math.round(Number(input.value) || 1)))));
  return el("label", { class: "size" }, label, input);
}

function tileStack(hits) {
  const list = el("ol", { class: "stack", "aria-label": "Room tiles here, top first" });
  hits.forEach((index, position) => {
    const tile = app.state.tiles[index];
    const li = el("li", { class: index === app.selectedTile ? "sel" : "" });
    const name = el("div", { class: "name", text: BY_ID.get(tile.id).name });
    name.addEventListener("click", () => selectTile(index));
    li.append(
      name,
      el("div", { class: "meta", text: `${tile.w}\u00D7${tile.h} \u00B7 anchor ${squareLabel(tile.x, tile.y)}` }),
    );
    const sizes = el(
      "div",
      { class: "sizes" },
      sizeInput("Width", tile.w, COLS - tile.x, (w) => resizeTileTo(index, w, tile.h)),
      sizeInput("Height", tile.h, ROWS - tile.y, (h) => resizeTileTo(index, tile.w, h)),
    );
    const buttons = el("div", { class: "btns" });
    const above = hits[position - 1];
    const below = hits[position + 1];
    const forward = stackButton("Forward", "Bring forward", () => reorderTileTo(index, above));
    forward.disabled = above === undefined;
    const back = stackButton("Back", "Send back", () => reorderTileTo(index, below));
    back.disabled = below === undefined;
    buttons.append(
      forward,
      back,
      stackButton("\u2190", "Move left", () => nudgeTile(index, -1, 0)),
      stackButton("\u2191", "Move up", () => nudgeTile(index, 0, -1)),
      stackButton("\u2193", "Move down", () => nudgeTile(index, 0, 1)),
      stackButton("\u2192", "Move right", () => nudgeTile(index, 1, 0)),
      stackButton("Remove", "Remove this tile", () => removeTileAt(index)),
    );
    li.append(sizes, buttons);
    list.append(li);
  });
  return list;
}

function renderInspector() {
  const box = $("#inspector");
  box.replaceChildren();
  const cell = app.pinned || app.hover;
  $("#inspector-hint").textContent = app.pinned ? "(pinned, Esc to unpin)" : "";
  if (!cell) {
    box.append(el("p", { class: "none", text: "Hover over the map, or click a square with the Select tool to pin it." }));
    return;
  }
  const hl = highlightAt(app.state, cell.x, cell.y);
  const hlName = HIGHLIGHTS.find((h) => h.value === hl)?.name ?? `Highlight ${hl}`;
  box.append(el("div", { class: "square", text: `Square ${squareLabel(cell.x, cell.y)}` }));
  box.append(el("div", { class: "meta", text: hl ? `Highlight: ${hlName}` : "No highlight" }));
  const zone = ZONES[app.state.zones[cell.y * COLS + cell.x] - 1];
  if (zone) box.append(el("div", { class: "meta", text: `Zone: ${app.state.legend[zone.legendKey] || zone.name}` }));
  const hits = itemsAt(app.state, cell.x, cell.y);
  if (hits.length) box.append(pieceStack(hits));
  else box.append(el("p", { class: "none", text: "No pieces here." }));
  const tileHits = tilesAt(app.state, cell.x, cell.y);
  if (tileHits.length) {
    box.append(el("h3", { class: "subhead", text: "Room tiles (under the pieces)" }), tileStack(tileHits));
  }
}

// A legend entry shows for each color used on the map: grey is always "Solid stone", orange
// defaults to "Trap", the others show the label typed in the legend editor (if any).
function legendLabel(h) {
  if (h.fixedLabel) return h.fixedLabel;
  return app.state.legend[h.value] || h.defaultLabel || "";
}

function renderLegend() {
  const used = new Set(app.state.hl);
  const items = [];
  for (const h of HIGHLIGHTS) {
    const label = h.value && used.has(h.value) ? legendLabel(h) : "";
    if (label) {
      items.push(el("li", {}, el("span", { class: "swatch", style: `background:${h.color}` }), label));
    }
  }
  const usedZones = new Set(app.state.zones);
  for (const zone of ZONES) {
    if (!usedZones.has(zone.n)) continue;
    items.push(
      el("li", {}, el("span", { class: "swatch", style: `background:${zone.color}` }), app.state.legend[zone.legendKey] || zone.name),
    );
  }
  $("#legend").replaceChildren(...items);
}

function formatNumber(value) {
  return String(Math.round(value * 100) / 100);
}

function plural(count, name) {
  return `${count} ${name}${count === 1 ? "" : "s"}`;
}

// Rows for the Quest stats card: [label, value] pairs, or { note } / { sub } lines.
function statRows(stats) {
  const bp = (value) => (stats.bpKnown ? formatNumber(value) : "n/a");
  const rows = [["Monsters", String(stats.monsters)], ["Total quest BP", bp(stats.bp)]];
  rows.push([
    `Avg BP, active rooms (${stats.activeRooms.length})`,
    stats.averageActive === null || !stats.bpKnown ? "n/a" : formatNumber(stats.averageActive),
  ]);
  rows.push([
    `Avg BP, occupied rooms (${stats.occupiedRooms.length})`,
    stats.averageOccupied === null || !stats.bpKnown ? "n/a" : formatNumber(stats.averageOccupied),
  ]);
  rows.push([
    "Highest room BP",
    stats.highest && stats.bpKnown ? `${formatNumber(stats.highest.bp)} (room ${stats.highest.rooms.join(", ")})` : "n/a",
  ]);
  rows.push(["In corridors", `${plural(stats.corridor.count, "monster")}, ${bp(stats.corridor.bp)} BP`]);
  if (stats.types.length) {
    rows.push({ sub: stats.types.map((t) => plural(t.count, t.name)).join(", ") });
  }
  const wm = stats.wandering;
  const wandering = [wm.monster, wm.text].filter(Boolean).join(" \u2013 ");
  if (wandering) {
    const bpText = wm.bpVaries ? "BP varies" : wm.bp === null ? "BP not set" : `${wm.bp} BP`;
    const extra = wm.monster ? ` (${bpText})` : "";
    rows.push(["Wandering (not counted)", `${wandering}${extra}`]);
  }
  if (stats.varies.length) {
    rows.push({ note: `BP not included (varies by quest): ${stats.varies.join(", ")}.`, info: true });
  }
  if (!stats.bpKnown) {
    rows.push({ note: `BP is not set yet for: ${stats.missing.join(", ")}.` });
  }
  return rows;
}

function renderStats() {
  const rows = statRows(computeStats(app.state));
  for (const id of ["#stats", "#print-stats"]) {
    const list = $(id);
    list.replaceChildren();
    for (const row of rows) {
      if (Array.isArray(row)) {
        list.append(el("dt", { text: row[0] }), el("dd", { text: row[1] }));
      } else if (row.sub) {
        list.append(el("dd", { class: "sub", text: row.sub }));
      } else {
        list.append(el("dd", { class: row.info ? "note info" : "note", text: row.note }));
      }
    }
  }
}

// "Pieces on this map": every distinct piece or tile style in use, grouped like the palette, with its
// icon and how many there are. Numbered markers share one line.
function pieceKeyGroups(state) {
  const counts = new Map();
  for (const item of state.items) counts.set(item.id, (counts.get(item.id) ?? 0) + 1);
  for (const tile of state.tiles) counts.set(tile.id, (counts.get(tile.id) ?? 0) + 1);
  const groups = [];
  for (const group of GROUPS) {
    const used = CATALOG.filter((piece) => piece.group === group && counts.has(piece.id));
    if (used.length) groups.push({ group, pieces: used.map((piece) => ({ piece, count: counts.get(piece.id) })) });
  }
  return groups;
}

function renderPieceKey(container, groups) {
  container.replaceChildren();
  for (const { group, pieces } of groups) {
    const list = el("ul");
    if (group === "Markers") {
      const numbers = pieces.map(({ piece }) => piece.name.replace("Marker ", "")).join(", ");
      list.append(el("li", {}, el("span", { class: "keyicon" }, iconThumb(pieces[0].piece)), el("span", { text: `Markers ${numbers}` })));
    } else {
      for (const { piece, count } of pieces) {
        const label = el("span", { text: piece.name });
        if (count > 1) label.append(el("span", { class: "keycount", text: ` \u00D7${count}` }));
        list.append(el("li", {}, el("span", { class: "keyicon" }, iconThumb(piece)), label));
      }
    }
    container.append(el("div", { class: "keygroup", "data-group": group }, el("h4", { text: group }), list));
  }
}

function renderPieceKeys() {
  const groups = pieceKeyGroups(app.state);
  renderPieceKey($("#sheet-key"), groups);
  renderPieceKey($("#print-key"), groups);
  $("#sheet-key-section").hidden = groups.length === 0;
  $("#print-key-section").hidden = groups.length === 0;
}

function renderUndoRedo() {
  $("#undo").disabled = !app.past.length;
  $("#redo").disabled = !app.future.length;
}

function renderPreviews() {
  renderIntro($("#sheet-intro"), app.state.intro);
  renderNotes($("#sheet-notes"), app.state.notes);
  renderIntro($("#print-intro"), app.state.intro);
  renderNotes($("#print-notes"), app.state.notes);
  $("#print-notes-section").hidden = !app.state.notes.trim();
  $("#print-intro").hidden = !app.state.intro.trim();
  const title = [app.state.num ? `Quest ${app.state.num}` : "", app.state.title].filter(Boolean).join(": ");
  $("#print-title").textContent = title;
  const head = [app.state.series ? `${app.state.series}:` : "", app.state.num ? `Quest ${app.state.num} -` : "", app.state.title]
    .filter(Boolean)
    .join(" ");
  $("#head-title").textContent = head;
  $("#head-title").title = head;
  $("#print-series").textContent = app.state.series;
  $("#print-series").hidden = !app.state.series;
  const monster = BY_ID.get(app.state.wmId);
  const wm = [monster?.name, app.state.wmText].filter(Boolean).join(" – ");
  $("#print-wm").textContent = wm ? `Wandering monster: ${wm}` : "";
  // The live quest sheet below the legend shows the same information as it is typed.
  $("#sheet-series").textContent = app.state.series;
  $("#sheet-series").hidden = !app.state.series;
  $("#sheet-title").textContent = title;
  $("#sheet-title").hidden = !title;
  $("#sheet-wm").textContent = wm ? `Wandering monster: ${wm}` : "";
  $("#sheet-wm").hidden = !wm;
  $("#sheet-intro-section").hidden = !app.state.intro.trim();
  $("#sheet-notes-section").hidden = !app.state.notes.trim();
  $("#sheet-empty").hidden = Boolean(app.state.series || title || wm || app.state.intro.trim() || app.state.notes.trim());
  document.title = `${app.state.series ? `${app.state.series}: ` : ""}${title || "Quest"} – Quest Map Generator`;
}

function renderAll() {
  applyMode();
  renderMap();
  renderOverlay();
  renderInspector();
  renderHeroCard();
  renderLegend();
  renderStats();
  renderPieceKeys();
  renderUndoRedo();
  renderPreviews();
  markTools();
  renderHero();
}

// ---------------------------------------------------------------- hero view data card (editor)
function chipButton(label, region, pressed, onClick) {
  const button = el("button", { type: "button", "data-region": String(region), "aria-pressed": String(pressed), text: label });
  button.addEventListener("click", onClick);
  return button;
}

function chipLabel(region) {
  return region < ROOM_REGIONS ? String.fromCharCode(65 + region) : regionName(app.state, region);
}

// Shows the card for app.editRegion. It is updated, never rebuilt, so typing in it keeps its focus.
function renderHeroCard() {
  const st = app.state;
  const region = app.editRegion;
  const details = $("#hero-card details");
  $("#hero-card-title").textContent = region === null ? "Hero view data" : `Hero view data \u00B7 ${regionName(st, region)}`;
  if (region !== app.shownRegion) {
    app.shownRegion = region;
    if (region !== null) details.open = true;
  }
  const regions = chooserRegions(st);
  $("#hero-chooser").replaceChildren(
    ...regions.map((r) =>
      chipButton(chipLabel(r), r, r === region, () => {
        app.editRegion = r;
        renderHeroCard();
        renderOverlay();
      }),
    ),
  );
  $("#hero-none").hidden = region !== null;
  $("#hero-fields").hidden = region === null;
  if (region !== null) {
    const rec = st.rooms[region] ?? { start: false, group: 0, texts: ["", "", "", ""] };
    const start = $("#hero-start");
    if (document.activeElement !== start) start.checked = rec.start;
    $("#hero-group").replaceChildren(
      ...regions
        .filter((r) => r !== region)
        .map((r) =>
          chipButton(chipLabel(r), r, rec.group !== 0 && st.rooms[r]?.group === rec.group, () => {
            const on = !(rec.group !== 0 && st.rooms[r]?.group === rec.group);
            setGroupMember(st, region, r, on);
            heroDataChanged();
          }),
        ),
    );
    for (let i = 0; i < 4; i++) {
      const box = $(`#hero-text-${i}`);
      if (document.activeElement !== box) box.value = rec.texts[i];
      box.closest(".field").querySelector(".hero-count").textContent = `${Array.from(rec.texts[i]).length}/${LIMITS.roomText}`;
    }
  }
  const { chars, regions: withText } = totalRoomText(st);
  $("#hero-total").textContent = chars
    ? `${chars} characters of room text in ${withText} room${withText === 1 ? "" : "s"} or zone${withText === 1 ? "" : "s"}.`
    : "No room text yet.";
}

// A change to hero view data: the link follows at once, and undo gets one step per pause in typing.
function heroDataChanged() {
  renderOverlay();
  renderHeroCard();
  scheduleUrl(false, 300);
  clearTimeout(textTimer);
  textTimer = setTimeout(() => {
    textTimer = 0;
    commit();
  }, 700);
}

function bindHeroCard() {
  $("#hero-start").addEventListener("change", (event) => {
    if (app.editRegion === null) return;
    editRoom(app.state, app.editRegion, (rec) => (rec.start = event.target.checked));
    heroDataChanged();
  });
  for (let i = 0; i < 4; i++) {
    const box = $(`#hero-text-${i}`);
    box.addEventListener("input", () => {
      if (app.editRegion === null) return;
      const { text } = cleanText(box.value, { multiline: true, limit: LIMITS.roomText });
      if (text !== box.value) box.value = text;
      editRoom(app.state, app.editRegion, (rec) => (rec.texts[i] = text));
      heroDataChanged();
    });
  }
  $("#copy-hero").addEventListener("click", async () => {
    const button = $("#copy-hero");
    const label = button.textContent;
    const payload = await encodeState({ ...app.state, hero: true, play: null });
    const link = `${location.href.split("#")[0]}#${payload}`;
    try {
      await navigator.clipboard.writeText(link);
      button.textContent = "Copied!";
    } catch {
      window.prompt("Copy this hero link:", link);
    }
    setTimeout(() => {
      button.textContent = label;
    }, 1500);
  });
}

// ---------------------------------------------------------------- hero view
function applyMode() {
  const hero = app.state.hero;
  document.body.classList.toggle("hero", hero);
  for (const id of ["#hero-badge", "#to-zargon", "#reset-game", "#hero-hint", "#hero-panel"]) $(id).hidden = !hero;
}

// A yes/no question in a dialog; resolves true only when the person confirms. The answer is taken
// from the button click itself, so whatever follows runs before the dialog is gone.
function askConfirm(message, okLabel, { info = false } = {}) {
  const dialog = $("#confirm-dialog");
  const ok = $("#confirm-ok");
  const cancel = $("#confirm-cancel");
  $("#confirm-message").textContent = message;
  ok.textContent = okLabel;
  cancel.hidden = info; // a plain message has nothing to cancel
  return new Promise((resolve) => {
    let settled = false;
    const finish = (answer) => {
      if (settled) return;
      settled = true;
      ok.removeEventListener("click", onOk);
      cancel.removeEventListener("click", onCancel);
      dialog.removeEventListener("close", onClose);
      if (dialog.open) dialog.close();
      resolve(answer);
    };
    const onOk = (event) => {
      event.preventDefault();
      finish(true);
    };
    const onCancel = (event) => {
      event.preventDefault();
      finish(false);
    };
    const onClose = () => finish(false); // Esc
    ok.addEventListener("click", onOk);
    cancel.addEventListener("click", onCancel);
    dialog.addEventListener("close", onClose);
    dialog.showModal();
  });
}

// A message with a single OK button.
function tellUser(message) {
  return askConfirm(message, "OK", { info: true });
}

// Play changes the link in place: no history entries and no undo (docs/HERO_VIEW.md).
function heroChanged() {
  renderAll();
  scheduleUrl(false);
}

function heroTap(event) {
  const cell = cellAt(event);
  if (!cell) return;
  app.heroRegion = regionAt(app.state, cell.x, cell.y);
  app.heroCell = { x: cell.x, y: cell.y };
  renderOverlay();
  renderHero();
}

function heroRegionTitle(region) {
  return region >= ROOM_REGIONS ? "Hallway" : regionName(app.state, region);
}

function heroText(className, text) {
  const box = el("div", { class: className });
  renderIntro(box, text);
  return box;
}

const HERO_SEARCHES = [
  { kind: "t", label: "Search for treasure", key: "treasure" },
  { kind: "tr", label: "Search for traps", key: "traps" },
  { kind: "sd", label: "Search for secret doors", key: "secretDoors" },
];

function heroQuestCard() {
  const st = app.state;
  const card = el("section", { class: "card" });
  if (st.series) card.append(el("div", { class: "muted", text: st.series }));
  const title = [st.num ? `Quest ${st.num}` : "", st.title].filter(Boolean).join(": ");
  if (title) card.append(el("h2", { text: title }));
  if (st.intro.trim()) card.append(heroText("hero-quote", st.intro));
  const monster = BY_ID.get(st.wmId);
  const wm = [monster?.name, st.wmText].filter(Boolean).join(" \u2013 ");
  if (wm) card.append(el("p", { class: "muted", text: `Wandering monster: ${wm}` }));
  return card;
}

function heroRegionCard() {
  const st = app.state;
  const region = app.heroRegion;
  const card = el("section", { class: "card" });
  if (region === null) {
    if (!app.heroCell) {
      card.append(el("p", { class: "muted", text: "Tap a room or a hallway on the map." }));
      return card;
    }
    // A square in no room or zone: it looks and behaves like any hidden hallway until Reveal is pressed.
    card.append(el("h2", { class: "hero-title", text: "Hallway" }));
    const reveal = el("button", { id: "hero-reveal", type: "button", class: "primary", text: "Reveal this hallway" });
    reveal.addEventListener("click", () => tellUser("Nothing to reveal. This is solid stone."));
    card.append(reveal);
    return card;
  }
  const noun = region >= ROOM_REGIONS ? "hallway" : "room";
  if (!isRevealed(st, region)) {
    card.append(el("h2", { class: "hero-title", text: heroRegionTitle(region) }));
    const reveal = el("button", { id: "hero-reveal", type: "button", class: "primary", text: `Reveal this ${noun}` });
    reveal.addEventListener("click", async () => {
      const ok = await askConfirm(`Reveal this ${noun}? Everything in it will show for everyone looking at the screen.`, "Reveal");
      if (ok && revealRegion(st, region)) heroChanged();
    });
    card.append(reveal);
    return card;
  }
  card.append(el("h2", { class: "hero-title" }, heroRegionTitle(region), el("small", { text: " \u00B7 revealed" })));
  const texts = regionTexts(st, region);
  if (texts.readAloud) card.append(heroText("hero-quote", texts.readAloud));
  const actions = el("div", { class: "hero-actions" });
  for (const { kind, label, key } of HERO_SEARCHES) {
    if (isSearched(st, region, kind)) {
      const result = el("div", { class: "hero-result" }, el("b", { text: label }));
      result.append(texts[key] ? heroText("", texts[key]) : el("div", { class: "muted", text: "You find nothing." }));
      actions.append(result);
    } else {
      const button = el("button", { id: `hero-search-${kind}`, type: "button", text: label });
      button.addEventListener("click", () => {
        if (searchRegion(st, region, kind)) heroChanged();
      });
      actions.append(button);
    }
  }
  const hide = el("button", { id: "hero-hide", type: "button", text: `Hide this ${noun} again` });
  hide.addEventListener("click", async () => {
    const ok = await askConfirm(`Hide this ${noun} again? Its searches are forgotten too.`, "Hide again");
    if (ok && hideRegion(st, region)) heroChanged();
  });
  actions.append(hide);
  card.append(actions);
  return card;
}

function renderHero() {
  if (!app.state.hero) return;
  $("#hero-panel").replaceChildren(heroQuestCard(), heroRegionCard());
}

function bindHeroControls() {
  $("#to-hero").addEventListener("click", () => {
    flushTextCommit();
    app.state.hero = true;
    app.heroRegion = null;
    app.heroCell = null;
    heroChanged();
  });
  $("#to-zargon").addEventListener("click", async () => {
    const ok = await askConfirm(
      "Switch to Zargon's view? Zargon's secret notes and every hidden room, trap and secret door will be visible. Only continue if the heroes are not looking.",
      "Switch to Zargon's view",
    );
    if (!ok) return;
    app.state.hero = false;
    app.heroRegion = null;
    app.heroCell = null;
    heroChanged();
  });
  $("#reset-game").addEventListener("click", async () => {
    const ok = await askConfirm("Reset the game? Every room and hallway is hidden again and all searches are forgotten.", "Reset game");
    if (!ok) return;
    resetGame(app.state);
    app.heroRegion = null;
    app.heroCell = null;
    heroChanged();
  });
}

// ---------------------------------------------------------------- actions on pieces
// The What's here panel shows a square. When the selected piece or tile moves (panel buttons, arrow
// keys, drag, or a rotation that re-anchors it), pin the panel to its new square so it keeps showing
// the piece instead of the square it left.
function followSelection() {
  const target = app.state.items[app.selected] ?? app.state.tiles[app.selectedTile];
  if (target) app.pinned = { x: target.x, y: target.y };
}

function selectItem(index) {
  app.selected = index;
  app.selectedTile = -1;
  renderOverlay();
  renderInspector();
}

function selectTile(index) {
  app.selectedTile = index;
  app.selected = -1;
  renderOverlay();
  renderInspector();
}

function nudgeTile(index, dx, dy) {
  const tile = app.state.tiles[index];
  if (moveTile(app.state, index, tile.x + dx, tile.y + dy)) {
    if (app.selectedTile === index) followSelection();
    commit();
  }
}

function removeTileAt(index) {
  removeTile(app.state, index);
  app.selectedTile = -1;
  commit();
}

function reorderTileTo(index, targetIndex) {
  if (targetIndex === undefined) return;
  const newIndex = reorderTile(app.state, index, targetIndex - index);
  app.selectedTile = app.selectedTile === index ? newIndex : app.selectedTile;
  commit();
}

function resizeTileTo(index, w, h) {
  if (resizeTile(app.state, index, w, h)) commit();
}

function rotateAt(index) {
  rotateItem(app.state, index);
  if (app.selected === index) followSelection();
  commit();
}

function nudgeAt(index, dx, dy) {
  const item = app.state.items[index];
  if (moveItem(app.state, index, item.x + dx, item.y + dy)) {
    if (app.selected === index) followSelection();
    commit();
  }
}

function removeAt(index) {
  removeItem(app.state, index);
  app.selected = -1;
  commit();
}

function reorderTo(index, targetIndex) {
  if (targetIndex === undefined) return;
  const newIndex = reorderItem(app.state, index, targetIndex - index);
  app.selected = app.selected === index ? newIndex : app.selected;
  commit();
}

// ---------------------------------------------------------------- pointer handling
function onPointerDown(event) {
  if (!app.editable || (event.pointerType === "mouse" && event.button !== 0)) return;
  if (app.state.hero) {
    heroTap(event);
    return;
  }
  const cell = cellAt(event);
  if (!cell) return;
  app.hover = { ...cell, edge: nearestEdge(cell) };
  app.pointerType = event.pointerType;
  app.inside = true;
  const { kind, value } = app.tool;
  if (kind === "piece") {
    const ghost = ghostItem();
    const placed = placeItem(app.state, ghost.id, ghost.x, ghost.y, ghost.r);
    if (placed >= 0) {
      app.selected = placed;
      app.selectedTile = -1;
      if (app.pinned) followSelection(); // a pinned square would otherwise hide the piece just placed
      commit();
    } else {
      // An identical piece is already there, so nothing is added. Select that one instead of
      // clearing the selection, so the panel still shows the square you tapped.
      const same = itemsAt(app.state, cell.x, cell.y).find((i) => {
        const o = app.state.items[i];
        return o.id === ghost.id && o.r === ghost.r;
      });
      app.selected = same ?? -1;
      app.selectedTile = -1;
      if (app.pinned) followSelection();
      renderOverlay();
      renderInspector();
    }
  } else if (kind === "tile") {
    event.preventDefault();
    $("#board").setPointerCapture(event.pointerId);
    app.tileDraw = { id: value, sx: cell.x, sy: cell.y, x: cell.x, y: cell.y, w: 1, h: 1 };
    renderOverlay();
  } else if (kind === "erase") {
    const hits = itemsAt(app.state, cell.x, cell.y);
    const tileHits = tilesAt(app.state, cell.x, cell.y);
    if (hits.length) removeAt(hits[0]);
    else if (tileHits.length) removeTileAt(tileHits[0]);
  } else if (kind === "highlight" || kind === "zone") {
    event.preventDefault();
    $("#board").setPointerCapture(event.pointerId);
    app.paint = { kind, value, changed: false };
    paintCell(cell);
  } else {
    app.pinned = { x: cell.x, y: cell.y };
    app.editRegion = regionAt(app.state, cell.x, cell.y);
    renderHeroCard();
    const hits = itemsAt(app.state, cell.x, cell.y);
    const already = hits.includes(app.selected);
    const tileHits = tilesAt(app.state, cell.x, cell.y);
    if (hits.length) {
      if (!already) app.selected = hits[0];
      app.selectedTile = -1;
      const item = app.state.items[app.selected];
      event.preventDefault();
      $("#board").setPointerCapture(event.pointerId);
      app.drag = { kind: "item", index: app.selected, dx: cell.x - item.x, dy: cell.y - item.y, moved: false, already, hits };
    } else if (tileHits.length) {
      app.selected = -1;
      app.selectedTile = tileHits[0];
      const tile = app.state.tiles[app.selectedTile];
      event.preventDefault();
      $("#board").setPointerCapture(event.pointerId);
      app.drag = { kind: "tile", index: app.selectedTile, dx: cell.x - tile.x, dy: cell.y - tile.y, moved: false, already: false, hits: [] };
    } else {
      app.selected = -1;
      app.selectedTile = -1;
    }
    renderOverlay();
    renderInspector();
  }
}

function paintCell(cell) {
  const paint = app.paint.kind === "zone" ? setZone : setHighlight;
  if (paint(app.state, cell.x, cell.y, app.paint.value)) {
    app.paint.changed = true;
    renderMap();
  }
}

function onPointerMove(event) {
  if (app.state.hero) return;
  const cell = cellAt(event);
  app.pointerType = event.pointerType;
  app.inside = cell !== null;
  if (cell) app.hover = { ...cell, edge: nearestEdge(cell) };
  if (app.paint && cell) paintCell(cell);
  if (app.tileDraw && cell) {
    const d = app.tileDraw;
    d.x = Math.min(d.sx, cell.x);
    d.y = Math.min(d.sy, cell.y);
    d.w = Math.abs(cell.x - d.sx) + 1;
    d.h = Math.abs(cell.y - d.sy) + 1;
  }
  if (app.drag && cell) {
    const { kind, index, dx, dy } = app.drag;
    const moved =
      kind === "tile"
        ? moveTile(app.state, index, cell.x - dx, cell.y - dy)
        : moveItem(app.state, index, cell.x - dx, cell.y - dy);
    if (moved) {
      app.drag.moved = true;
      followSelection();
      renderMap();
    }
  }
  renderOverlay();
  renderInspector();
}

function onPointerUp() {
  if (app.tileDraw) {
    const { id, x, y, w, h } = app.tileDraw;
    app.tileDraw = null;
    app.selectedTile = addTile(app.state, id, x, y, w, h);
    app.selected = -1;
    if (app.pinned) followSelection();
    commit();
  }
  if (app.paint) {
    const changed = app.paint.changed;
    app.paint = null;
    if (changed) commit();
  }
  if (app.drag) {
    const { moved, already, hits, index } = app.drag;
    app.drag = null;
    if (moved) {
      commit();
    } else if (already && hits.length > 1) {
      app.selected = hits[(hits.indexOf(index) + 1) % hits.length];
      renderOverlay();
      renderInspector();
    }
  }
}

// The last hovered square stays in the inspector so its buttons can be reached with the mouse.
function onPointerLeave() {
  if (app.paint || app.drag || app.tileDraw) return;
  app.inside = false;
  renderOverlay();
}

// ---------------------------------------------------------------- keyboard
function onKeyDown(event) {
  if (app.state.hero) {
    // Hero view has no undo and no editing keys; Esc just closes the room panel.
    if (event.key === "Escape" && app.heroCell) {
      app.heroRegion = null;
      app.heroCell = null;
      renderOverlay();
      renderHero();
    }
    return;
  }
  const target = event.target;
  const typing = target instanceof HTMLElement && /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName);
  if ((event.ctrlKey || event.metaKey) && !event.altKey) {
    const key = event.key.toLowerCase();
    if (key === "z" && !typing) {
      event.preventDefault();
      if (event.shiftKey) redo();
      else undo();
    } else if (key === "y" && !typing) {
      event.preventDefault();
      redo();
    }
    return;
  }
  if (typing || !app.editable) return;
  const key = event.key;
  if (key === "r" || key === "R") {
    if (app.tool.kind === "piece") {
      app.ghostRot = (app.ghostRot + 1) % 4;
      renderOverlay();
    } else if (app.selected >= 0) {
      rotateAt(app.selected);
    }
  } else if ((key === "Delete" || key === "Backspace") && app.selectedTile >= 0) {
    event.preventDefault();
    removeTileAt(app.selectedTile);
  } else if ((key === "Delete" || key === "Backspace") && app.selected >= 0) {
    event.preventDefault();
    removeAt(app.selected);
  } else if (key === "Escape") {
    // Cancel whatever is in progress and go back to the Select tool with nothing selected.
    app.tileDraw = null;
    app.tool = { kind: "select", value: 0 };
    app.ghostRot = 0;
    app.selected = -1;
    app.selectedTile = -1;
    app.pinned = null;
    app.editRegion = null;
    renderAll();
  } else if ((app.selected >= 0 || app.selectedTile >= 0) && key.startsWith("Arrow")) {
    event.preventDefault();
    const d = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] }[key];
    if (app.selectedTile >= 0) nudgeTile(app.selectedTile, d[0], d[1]);
    else nudgeAt(app.selected, d[0], d[1]);
  }
}

// ---------------------------------------------------------------- tools palette
function iconThumb(piece) {
  const w = piece.w * CELL;
  const h = piece.h * CELL;
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  // Edge pieces (doors) are drawn centered on the top edge, so center that strip in the thumbnail.
  svg.setAttribute("viewBox", piece.edge ? `-2 -10 ${w + 4} 20` : `0 0 ${w} ${h}`);
  svg.setAttribute("aria-hidden", "true");
  const use = document.createElementNS("http://www.w3.org/2000/svg", "use");
  use.setAttribute("href", `#icon-${piece.slug}`);
  use.setAttribute("width", String(w));
  use.setAttribute("height", String(h));
  svg.append(use);
  return svg;
}

function toolButton(label, kind, value, lead) {
  const button = el("button", { type: "button", "data-kind": kind, "data-value": String(value) });
  if (lead) button.append(lead);
  button.append(document.createTextNode(label));
  button.addEventListener("click", () => {
    // Picking a different piece starts it upright; re-picking the same one keeps your rotation.
    if (app.tool.kind !== kind || app.tool.value !== value) app.ghostRot = 0;
    app.tool = { kind, value };
    if (kind !== "select") {
      app.selected = -1;
      app.selectedTile = -1;
    }
    renderAll();
  });
  return button;
}

function buildPalette() {
  const root = $("#tools");
  root.replaceChildren();
  root.append(el("h2", { text: "Tools" }));
  const basics = el("div", { class: "tgrid" });
  basics.append(toolButton("Select", "select", 0), toolButton("Eraser", "erase", 0));
  root.append(basics);
  root.append(el("h2", { text: "Highlight" }));
  const hls = el("div", { class: "tgrid" });
  const solid = el("div", { class: "tgrid" });
  const zones = el("div", { class: "tgrid" });
  for (const h of HIGHLIGHTS) {
    const swatch = el("span", { class: "swatch", style: h.color ? `background:${h.color}` : "background:transparent" });
    const button = toolButton(h.value ? h.name.replace(" (solid stone)", "") : "Clear", "highlight", h.value, swatch);
    // Grey (value 1) marks solid stone, so it has its own section; the other colors stay together.
    if (h.value === 1) button.title = "Paint solid stone like a highlight; Clear erases it";
    (h.value === 1 ? solid : hls).append(button);
  }
  root.append(hls);
  solid.append(toolButton("Clear", "highlight", 0, el("span", { class: "swatch", style: "background:transparent" })));
  root.append(el("h2", { text: "Solid stone areas" }), solid);
  for (const zone of ZONES) {
    zones.append(toolButton(zone.name, "zone", zone.n, el("span", { class: "swatch", style: `background:${zone.color}` })));
  }
  zones.append(toolButton("Clear", "zone", 0, el("span", { class: "swatch", style: "background:transparent" })));
  root.append(el("h2", { text: "Hero view zones" }), zones);
  root.append(
    el("p", { class: "muted", text: "Paint corridor squares to make hallways that heroes reveal like a room." }),
  );
  for (const group of GROUPS) {
    root.append(el("h2", { text: group }));
    const grid = el("div", { class: "tgrid" });
    for (const piece of CATALOG.filter((p) => p.group === group)) {
      const button = toolButton(piece.name, piece.tile ? "tile" : "piece", piece.id, iconThumb(piece));
      button.title = `${piece.name} (${piece.w}×${piece.h})`;
      grid.append(button);
    }
    root.append(grid);
  }
}

function markTools() {
  for (const button of document.querySelectorAll("#tools button")) {
    const active =
      button.dataset.kind === app.tool.kind && Number(button.dataset.value) === app.tool.value;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
  }
  $("#board").style.cursor = app.tool.kind === "select" ? "default" : "crosshair";
}

// ---------------------------------------------------------------- quest fields
function buildLegendEditor() {
  const root = $("#legend-edit");
  root.replaceChildren();
  // The ordinary colors, then the zones: zone n is named by legend entry 5 + n.
  const entries = [
    ...HIGHLIGHTS.filter((x) => x.value > 1).map((h) => ({ key: h.value, name: h.name, placeholder: h.defaultLabel || h.name, color: h.color })),
    ...ZONES.map((z) => ({ key: z.legendKey, name: z.name, placeholder: z.name, color: z.color })),
  ];
  for (const entry of entries) {
    const input = el("input", {
      type: "text",
      "data-color": String(entry.key),
      maxlength: String(LIMITS.legend),
      placeholder: entry.placeholder,
      "aria-label": `Legend label for ${entry.name}`,
      autocomplete: "off",
    });
    input.addEventListener("input", () => {
      const cleaned = cleanText(input.value, { limit: LIMITS.legend }).text;
      if (cleaned !== input.value) input.value = cleaned;
      app.state.legend[entry.key] = cleaned;
      textChanged();
    });
    root.append(el("div", { class: "lg" }, el("span", { class: "swatch", style: `background:${entry.color}` }), input));
  }
}

function buildWandering() {
  const select = $("#wm-select");
  select.replaceChildren(el("option", { value: "0", text: "(none)" }));
  for (const monster of MONSTERS) select.append(el("option", { value: String(monster.id), text: monster.name }));
  select.addEventListener("change", () => {
    app.state.wmId = Number(select.value);
    textChanged();
  });
}

function bindField(selector, key, options) {
  const input = $(selector);
  input.addEventListener("input", () => {
    const start = input.selectionStart ?? input.value.length;
    const { text } = cleanText(input.value, options);
    if (text !== input.value) {
      const delta = input.value.length - text.length;
      input.value = text;
      input.setSelectionRange(Math.max(0, start - delta), Math.max(0, start - delta));
    }
    app.state[key] = text;
    textChanged();
  });
}

// A zone's palette button shows its name once the author has typed one in the legend.
function refreshZoneButtons() {
  for (const zone of ZONES) {
    const button = document.querySelector(`#tools button[data-kind="zone"][data-value="${zone.n}"]`);
    if (button) button.lastChild.textContent = app.state.legend[zone.legendKey] || zone.name;
  }
}

function textChanged() {
  renderPreviews();
  renderLegend();
  refreshZoneButtons();
  renderStats();
  scheduleUrl(false, 300);
  clearTimeout(textTimer);
  textTimer = setTimeout(() => {
    textTimer = 0;
    commit();
  }, 700);
}

function syncFields() {
  $("#series").value = app.state.series;
  $("#qnum").value = app.state.num;
  $("#qtitle").value = app.state.title;
  $("#qintro").value = app.state.intro;
  $("#notes").value = app.state.notes;
  $("#wm-select").value = BY_ID.has(app.state.wmId) ? String(app.state.wmId) : "0";
  $("#wm-text").value = app.state.wmText;
  for (const input of document.querySelectorAll("#legend-edit input")) {
    input.value = app.state.legend[Number(input.dataset.color)] ?? "";
  }
  refreshZoneButtons();
}

// ---------------------------------------------------------------- zoom
function setZoom(value) {
  app.zoom = Math.max(1, Math.min(4, value));
  $("#board").style.width = `${app.zoom * 100}%`;
}

// ---------------------------------------------------------------- init
function browserSupported() {
  return typeof CompressionStream === "function" && typeof DecompressionStream === "function";
}

export function showUnsupported() {
  app.editable = false;
  const box = $("#unsupported");
  box.hidden = false;
  box.replaceChildren(
    el("h2", { text: "This browser is too old" }),
    el("p", {
      text: `Quest Map Generator stores the whole map in the link and needs built-in compression. Please use a recent browser: ${MIN_BROWSERS}, or newer.`,
    }),
  );
  $("#app").hidden = true;
  $("#topbar").hidden = true;
}

export function initUi() {
  if (!browserSupported()) {
    showUnsupported();
    return false;
  }
  const board = $("#board");
  board.setAttribute("viewBox", boardViewBox());
  board.innerHTML = boardSkeleton();
  buildPalette();
  buildLegendEditor();
  buildWandering();
  const themeSelect = $("#theme");
  for (const theme of THEMES) themeSelect.append(el("option", { value: String(theme.id), text: theme.name }));
  themeSelect.addEventListener("change", () => {
    app.state.theme = Number(themeSelect.value);
    applyTheme();
    scheduleUrl(false);
  });

  board.addEventListener("pointerdown", onPointerDown);
  board.addEventListener("pointermove", onPointerMove);
  board.addEventListener("pointerup", onPointerUp);
  board.addEventListener("pointercancel", onPointerUp);
  board.addEventListener("pointerleave", onPointerLeave);
  document.addEventListener("keydown", onKeyDown);

  bindField("#series", "series", { limit: LIMITS.series });
  bindField("#qnum", "num", { limit: LIMITS.num });
  bindField("#qtitle", "title", { limit: LIMITS.title });
  bindField("#qintro", "intro", { multiline: true, limit: LIMITS.intro });
  bindField("#notes", "notes", { multiline: true, limit: LIMITS.notes });
  bindField("#wm-text", "wmText", { limit: LIMITS.wmText });

  $("#undo").addEventListener("click", undo);
  $("#redo").addEventListener("click", redo);
  $("#zoom-in").addEventListener("click", () => setZoom(app.zoom * 1.25));
  $("#zoom-out").addEventListener("click", () => setZoom(app.zoom / 1.25));
  $("#zoom-fit").addEventListener("click", () => setZoom(1));
  $("#print-btn").addEventListener("click", () => window.print());
  bindHeroControls();
  bindHeroCard();
  for (const [id, cls] of [["intro", "np-intro"], ["key", "np-key"], ["stats", "np-stats"], ["notes", "np-notes"], ["legend", "np-legend"]]) {
    $(`#po-${id}`).addEventListener("change", (e) => document.body.classList.toggle(cls, !e.target.checked));
  }
  $("#po-monsters").addEventListener("change", (e) => document.body.classList.toggle("po-monsters", e.target.checked));
  $("#clear").addEventListener("click", () => {
    if (!window.confirm("Start a new, empty map? You can get back with Undo or the browser's back button.")) return;
    const theme = app.state.theme;
    app.state = blankState();
    app.state.theme = theme;
    app.selected = -1;
    app.selectedTile = -1;
    app.pinned = null;
    syncFields();
    commit();
  });
  $("#copy").addEventListener("click", async () => {
    await syncUrl();
    const button = $("#copy");
    const label = button.textContent;
    try {
      await navigator.clipboard.writeText(location.href);
      button.textContent = "Copied!";
    } catch {
      window.prompt("Copy this link:", location.href);
    }
    setTimeout(() => {
      button.textContent = label;
    }, 1500);
  });
  window.addEventListener("beforeprint", () => {
    app.inside = false;
    renderOverlay();
  });
  window.addEventListener("popstate", loadFromHash);
  window.addEventListener("hashchange", loadFromHash);

  app.baseline = snapshot(app.state);
  syncFields();
  applyTheme();
  renderAll();
  return true;
}
