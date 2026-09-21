#!/usr/bin/env python3
"""Assemble paper/sections/*.md into build/paper.md.

A line of the form `<!-- INCLUDE generated/NAME.md -->` is replaced by that
file's content. The script also fails if the body contains a character that
the LaTeX fonts in use may not have, so that such characters are caught here
and not as missing glyphs in the PDF.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
ALLOWED_NON_ASCII = set("äáöüé")  # names: Graedel, Davila, Alpoge and similar

def main() -> int:
    parts = []
    for path in sorted((ROOT / "sections").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        def include(match: re.Match) -> str:
            return (ROOT / match.group(1)).read_text(encoding="utf-8")
        text = re.sub(r"^<!-- INCLUDE (\S+) -->$", include, text, flags=re.M)
        bad = sorted({c for c in text if ord(c) > 127 and c not in ALLOWED_NON_ASCII})
        if bad:
            print(f"{path.name}: non-ASCII characters {bad!r}", file=sys.stderr)
            return 1
        parts.append(text.rstrip() + "\n")
    out = ROOT / "build"
    out.mkdir(exist_ok=True)
    (out / "paper.md").write_text("\n".join(parts), encoding="utf-8")
    return 0

if __name__ == "__main__":
    sys.exit(main())
