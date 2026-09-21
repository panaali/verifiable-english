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
ALLOWED_NON_ASCII = set()  # Logic symbols are mechanically mapped to TeX math.

def main() -> int:
    parts = []
    for path in sorted((ROOT / "sections").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if '--placeholders' in sys.argv:
            for marker in re.findall(r'RESULT-[A-Z0-9-]+', text):
                print(f'{marker}: sections/{path.name}')
            continue
        def include(match: re.Match) -> str:
            target = (ROOT / match.group(1)).resolve()
            if not target.is_relative_to(ROOT):
                raise ValueError(f'Include outside paper directory: {target}')
            return target.read_text(encoding="utf-8")
        text = re.sub(r"^<!-- INCLUDE (\S+) -->$", include, text, flags=re.M)
        bad = sorted({c for c in text if ord(c) > 127 and c not in ALLOWED_NON_ASCII})
        if bad:
            print(f"{path.name}: non-ASCII characters {bad!r}", file=sys.stderr)
            return 1
        parts.append(text.rstrip() + "\n")
    if '--placeholders' in sys.argv:
        return 0
    out = ROOT / "build"
    out.mkdir(exist_ok=True)
    (out / "paper.md").write_text("\n".join(parts), encoding="utf-8")
    body = re.sub(r'<!--.*?-->', '', '\n'.join(parts), flags=re.S)
    count = len(re.findall(r"\b[\w]+(?:['-][\w]+)*\b", body))
    placeholders = sorted(set(re.findall(r'RESULT-[A-Z0-9-]+', body)))
    import json
    (out / 'draft-status.json').write_text(json.dumps({
        'word_count_method': 'Word tokens in assembled Markdown, excluding HTML comments; includes tables, references, link targets and markup identifiers.',
        'word_count': count,
        'result_placeholders': placeholders,
    }, indent=2) + '\n')
    print(f'Assembled {len(parts)} section files; {count:,} draft word tokens; {len(placeholders)} RESULT markers.')
    return 0

if __name__ == "__main__":
    sys.exit(main())
