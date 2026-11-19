#!/usr/bin/env python3
"""Lint dist/index.html without Node: strict HTML5 parse, unique ids, and resolvable references."""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

import html5lib

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "dist" / "index.html"


def main() -> int:
    text = PAGE.read_text(encoding="utf-8")
    problems: list[str] = []

    parser = html5lib.HTMLParser(strict=True)
    try:
        parser.parse(text)
    except html5lib.html5parser.ParseError as exc:
        problems.append(f"HTML parse error: {exc}")

    ids = re.findall(r'\bid="([^"]+)"', text)
    for name, count in Counter(ids).items():
        if count > 1:
            problems.append(f"duplicate id '{name}' ({count} times)")

    known = set(ids)
    for ref in re.findall(r'\bhref="#([\w-]+)"', text):
        if ref not in known:
            problems.append(f'href="#{ref}" points to a missing id')

    for ref in re.findall(r'\bfor="([\w-]+)"', text):
        if ref not in known:
            problems.append(f'label for="{ref}" points to a missing id')

    if "<meta charset" not in text.lower() or 'name="viewport"' not in text:
        problems.append("missing charset or viewport meta tag")
    if not re.search(r"<title>[^<]+</title>", text):
        problems.append("missing <title>")

    for problem in problems:
        print(f"lint_html: {problem}", file=sys.stderr)
    if not problems:
        print("lint_html: ok")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
