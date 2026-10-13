"""ME-0: split a pinned source into sentence units whose spans partition every byte.

Rules (fixed before labelling, the same for every target):
  1. Blocks are separated by blank lines. A heading line (`#`), a table line (it contains ` | `) and an image
     placeholder line (`[Image: ...]`) is one unit each.
  2. Inside a block, a sentence ends after `.`, `?` or `!` (and any closing quote or bracket) followed by
     whitespace and then an uppercase letter, a digit, a quote, `(` or `[`, unless the word before the stop is an
     abbreviation (list `ABBREV`) or the stop is inside `[...]`.
  3. A physics footnote, `[note n: ...]`, is a unit of its own.
  4. Whitespace after a unit belongs to it, so spans partition the source exactly.
Units are numbered `<prefix>NNN` in source order.

    python3 -I research/math-evidence/segment.py <source> <prefix>   # prints one line per unit
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ABBREV = {"fig", "figs", "al", "e.g", "i.e", "vs", "no", "vol", "pp", "jour", "sci", "ann", "phys", "chim", "m",
          "dr", "mr", "ref", "refs", "approx", "cf", "eq", "eqs", "ed", "eds", "pogg", "lum", "phen", "w.l", "w", "l",
          "p", "a", "ext", "suppl", "proc", "natl", "acad", "u.s", "st", "etc", "nos", "c", "b"}

STOP = re.compile(r"[.?!][\"'”’)\]]*\s+(?=[A-Z0-9\"“‘(\[])")


def _sentences(block: str, base: int) -> list[tuple[int, int]]:
    cuts = [0]
    depth = 0
    depths = []
    for ch in block:
        depths.append(depth)
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth = max(0, depth - 1)
    for m in STOP.finditer(block):
        stop = m.start()
        if depths[stop] > 0:
            continue
        word = re.search(r"([A-Za-z.]+)$", block[:stop])
        if word and word.group(1).lower().rstrip(".") in ABBREV:
            continue
        if re.search(r"\d$", block[:stop]) and re.match(r"\d", block[m.end():]):
            continue
        cuts.append(m.end())
    for m in re.finditer(r" \[note \d+:", block):
        cuts.append(m.start())
        close = m.end()
        depth = 1
        while close < len(block) and depth:
            depth += {"[": 1, "]": -1}.get(block[close], 0)
            close += 1
        cuts.append(close)
    cuts = sorted(set(c for c in cuts if 0 <= c < len(block)))
    spans = []
    for a, b in zip(cuts, cuts[1:] + [len(block)]):
        if a < b:
            spans.append((base + a, base + b))
    return spans


def segment(text: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    pos = 0
    for m in re.finditer(r".*?(?:\n\n+|\Z)", text, flags=re.S):
        block = m.group(0)
        if not block:
            continue
        start = m.start()
        lines = block.splitlines(keepends=True)
        if any(l.startswith("#") or " | " in l or l.startswith("[Image:") for l in lines):
            off = start
            para: list[str] = []
            for l in lines:
                if l.startswith("#") or " | " in l or l.startswith("[Image:"):
                    if para:
                        spans.extend(_sentences("".join(para), off - len("".join(para))))
                        para = []
                    spans.append((off, off + len(l)))
                else:
                    para.append(l)
                off += len(l)
            if para:
                spans.extend(_sentences("".join(para), off - len("".join(para))))
        else:
            spans.extend(_sentences(block, start))
        pos = m.end()
    # whitespace-only spans join the unit before them
    merged: list[tuple[int, int]] = []
    for a, b in spans:
        if merged and not text[a:b].strip():
            merged[-1] = (merged[-1][0], b)
        else:
            merged.append((a, b))
    assert merged[0][0] == 0 and merged[-1][1] == len(text)
    assert all(x[1] == y[0] for x, y in zip(merged, merged[1:]))
    return merged


def byte_spans(text: str, spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
    offsets = [0]
    for ch in text:
        offsets.append(offsets[-1] + len(ch.encode("utf-8")))
    return [(offsets[a], offsets[b]) for a, b in spans]


def units(path: Path, prefix: str) -> list[dict]:
    text = path.read_bytes().decode("utf-8")
    spans = segment(text)
    out = []
    for i, ((a, b), (ba, bb)) in enumerate(zip(spans, byte_spans(text, spans)), 1):
        out.append({"id": f"{prefix}{i:03d}", "span": [ba, bb], "text": text[a:b]})
    return out


if __name__ == "__main__":
    for u in units(Path(sys.argv[1]), sys.argv[2]):
        print(json.dumps([u["id"], u["span"][1] - u["span"][0], u["text"].strip()[:200]], ensure_ascii=False))
