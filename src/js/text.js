// Character handling for every text field (docs/FORMAT.md section 6).
const DISALLOWED = /[^\p{L}\p{M}\p{Nd} \n.,!?'":;()[\]\-*#|&\\/+_]/gu;
const REPLACEMENTS = {
  "\u2018": "'",
  "\u2019": "'",
  "\u201C": '"',
  "\u201D": '"',
  "\u2013": "-",
  "\u2014": "-",
  "\u2026": "...",
  "\u00A0": " ",
  "\t": " ",
};
const REPLACEABLE = /[\u2018\u2019\u201C\u201D\u2013\u2014\u2026\u00A0\t]/g;

// Normalizes, filters and length-limits text. Returns { text, removed, truncated }.
export function cleanText(input, { multiline = false, limit = Infinity } = {}) {
  let s = String(input ?? "").normalize("NFC");
  s = s.replace(/\r\n?/g, "\n");
  s = s.replace(REPLACEABLE, (c) => REPLACEMENTS[c]);
  if (!multiline) s = s.replace(/\n/g, " ");
  const before = s.length;
  s = s.replace(DISALLOWED, "");
  const removed = s.length !== before;
  const chars = Array.from(s);
  let truncated = false;
  if (chars.length > limit) {
    s = chars.slice(0, limit).join("");
    truncated = true;
  }
  return { text: s, removed, truncated };
}
