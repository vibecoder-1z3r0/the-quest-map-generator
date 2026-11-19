// A very small markdown subset, rendered with DOM nodes only (never innerHTML).
// Notes: headings (#, ##, ###), bullets (-), numbered lists (1.), **bold**, *italic*, --- rules,
// pipe tables, backslash escapes. The intro supports only bold and italics.

function tokenize(s) {
  const out = [];
  let i = 0;
  while (i < s.length) {
    const c = s[i];
    if (c === "\\" && i + 1 < s.length) {
      out.push({ k: "t", v: s[i + 1] });
      i += 2;
    } else if (c === "*") {
      if (s[i + 1] === "*") {
        out.push({ k: "**" });
        i += 2;
      } else {
        out.push({ k: "*" });
        i += 1;
      }
    } else {
      out.push({ k: "t", v: c });
      i += 1;
    }
  }
  return out;
}

function spill(parent, node) {
  parent.ch.push({ k: "t", v: node.k });
  for (const child of node.ch) parent.ch.push(child);
}

function buildTree(tokens) {
  const root = { k: "root", ch: [] };
  const stack = [root];
  for (const tk of tokens) {
    if (tk.k === "t") {
      stack[stack.length - 1].ch.push(tk);
      continue;
    }
    let idx = -1;
    for (let j = stack.length - 1; j > 0; j--) {
      if (stack[j].k === tk.k) {
        idx = j;
        break;
      }
    }
    if (idx > 0) {
      while (stack.length - 1 > idx) {
        const inner = stack.pop();
        spill(stack[stack.length - 1], inner);
      }
      const node = stack.pop();
      stack[stack.length - 1].ch.push(node);
    } else {
      stack.push({ k: tk.k, ch: [] });
    }
  }
  while (stack.length > 1) {
    const inner = stack.pop();
    spill(stack[stack.length - 1], inner);
  }
  return root.ch;
}

function emit(parent, nodes) {
  let text = "";
  const flush = () => {
    if (text) {
      parent.appendChild(document.createTextNode(text));
      text = "";
    }
  };
  for (const node of nodes) {
    if (node.k === "t") {
      text += node.v;
    } else {
      flush();
      const el = document.createElement(node.k === "**" ? "strong" : "em");
      emit(el, node.ch);
      parent.appendChild(el);
    }
  }
  flush();
}

export function renderInline(parent, text) {
  emit(parent, buildTree(tokenize(text)));
}

function splitCells(line) {
  const cells = [];
  let cur = "";
  for (let i = 0; i < line.length; i++) {
    const c = line[i];
    if (c === "\\" && i + 1 < line.length) {
      cur += c + line[i + 1];
      i += 1;
    } else if (c === "|") {
      cells.push(cur);
      cur = "";
    } else {
      cur += c;
    }
  }
  cells.push(cur);
  if (cells.length && cells[0].trim() === "") cells.shift();
  if (cells.length && cells[cells.length - 1].trim() === "") cells.pop();
  return cells.map((cell) => cell.trim());
}

const HEADING = /^(#{1,3}) (.*)$/;
const RULE = /^-{3,}$/;
const BULLET = /^- (.*)$/;
const NUMBERED = /^\d+\. (.*)$/;
const TABLE_SEPARATOR = /^[|\-: ]+$/;

function startsBlock(line, next) {
  return (
    HEADING.test(line) ||
    RULE.test(line) ||
    BULLET.test(line) ||
    NUMBERED.test(line) ||
    (line.startsWith("|") && next !== undefined && TABLE_SEPARATOR.test(next) && next.includes("-"))
  );
}

function spacer(container) {
  const el = document.createElement("div");
  el.className = "md-spacer";
  container.appendChild(el);
}

// blocks=false renders the intro: only paragraphs with bold and italics.
function renderBlocks(container, raw, blocks) {
  container.replaceChildren();
  const lines = String(raw ?? "").split("\n");
  let blank = 0;
  let i = 0;
  let any = false;
  const gap = () => {
    for (let k = 1; k < blank; k++) spacer(container);
    blank = 0;
  };
  while (i < lines.length) {
    const line = lines[i];
    if (line.trim() === "") {
      blank += 1;
      i += 1;
      continue;
    }
    if (any) gap();
    blank = 0;
    any = true;
    if (blocks) {
      const heading = HEADING.exec(line);
      if (heading) {
        const el = document.createElement(`h${heading[1].length + 2}`);
        el.className = "md-heading";
        renderInline(el, heading[2]);
        container.appendChild(el);
        i += 1;
        continue;
      }
      if (RULE.test(line)) {
        container.appendChild(document.createElement("hr"));
        i += 1;
        continue;
      }
      if (BULLET.test(line) || NUMBERED.test(line)) {
        const ordered = NUMBERED.test(line);
        const re = ordered ? NUMBERED : BULLET;
        const list = document.createElement(ordered ? "ol" : "ul");
        while (i < lines.length && re.test(lines[i])) {
          const li = document.createElement("li");
          renderInline(li, re.exec(lines[i])[1]);
          list.appendChild(li);
          i += 1;
        }
        container.appendChild(list);
        continue;
      }
      if (line.startsWith("|") && startsBlock(line, lines[i + 1])) {
        const table = document.createElement("table");
        const head = splitCells(line);
        const thead = table.createTHead().insertRow();
        for (const cell of head) renderInline(thead.appendChild(document.createElement("th")), cell);
        i += 2;
        const body = table.createTBody();
        while (i < lines.length && lines[i].startsWith("|")) {
          const row = body.insertRow();
          for (const cell of splitCells(lines[i])) renderInline(row.insertCell(), cell);
          i += 1;
        }
        container.appendChild(table);
        continue;
      }
    }
    const p = document.createElement("p");
    let first = true;
    while (i < lines.length && lines[i].trim() !== "" && (first || !blocks || !startsBlock(lines[i], lines[i + 1]))) {
      if (!first) p.appendChild(document.createElement("br"));
      renderInline(p, lines[i]);
      first = false;
      i += 1;
    }
    container.appendChild(p);
  }
}

export function renderNotes(container, raw) {
  renderBlocks(container, raw, true);
}

export function renderIntro(container, raw) {
  renderBlocks(container, raw, false);
}
