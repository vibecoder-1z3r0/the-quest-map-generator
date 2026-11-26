import { BY_ID, CATALOG } from "./catalog.js";
import { computeStats } from "./stats.js";
import { decodeHash, encodeState } from "./format.js";
import {
  groupMembers,
  hideRegion,
  isRevealed,
  isSearched,
  itemVisibility,
  regionAt,
  regionName,
  regionTexts,
  resetGame,
  revealRegion,
  searchRegion,
  secretOwners,
  squareVisible,
  stoneVisible,
} from "./hero.js";
import { renderIntro, renderNotes } from "./markdown.js";
import { cleanText } from "./text.js";
import { app, initUi, loadFromHash, syncUrl } from "./ui.js";

if (initUi()) loadFromHash();

// Test hook: lets the test suite drive the pure pieces inside the real built page.
window.QMG = {
  app,
  CATALOG,
  BY_ID,
  encodeState,
  decodeHash,
  cleanText,
  renderNotes,
  renderIntro,
  syncUrl,
  computeStats,
  hero: {
    groupMembers,
    hideRegion,
    isRevealed,
    isSearched,
    itemVisibility,
    regionAt,
    regionName,
    regionTexts,
    resetGame,
    revealRegion,
    searchRegion,
    secretOwners,
    squareVisible,
    stoneVisible,
  },
};
