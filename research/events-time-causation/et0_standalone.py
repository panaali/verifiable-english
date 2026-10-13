"""ET-0 diagnostic (outside the bar): u042 alone in a one-unit document on part01's profile list.

The body is u042's source sentence, cut from the pinned part by its span; the vocabulary is only what u042 uses.
It separates "the encoding checks" from "the part's search fits the checker's limits".

Usage: python3 et0_standalone.py <pinned translation-part01.ve.md> <out.ve.md> [u042|u042u043]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import et0_build as B  # noqa: E402


def main(src, out, variant="u042"):
    lines = Path(src).read_text().split("\n")
    fm = json.loads(lines[1])
    body = "\n".join(lines[3:]).encode()
    units = [B.UNIT_042] + ([B.UNIT_043] if variant == "u042u043" else [])
    start, stop = units[0]["span"][0], units[-1]["span"][1]
    text = body[start:stop].decode()
    sorts, preds, opens = dict(B.SORTS_042), dict(B.PREDICATES_042), []
    if variant == "u042u043":
        sorts.update(B.SORTS_043)
        preds.update(B.PREDICATES_043)
        opens.append(B.OPEN_043)
    env = {k: v for k, v in fm["environment"].items() if k != "vocabulary"}
    env["vocabulary"] = {"constants": {}, "predicates": preds, "sorts": sorts}
    rows = []
    for u in units:
        u = json.loads(json.dumps(u))
        u["span"] = [u["span"][0] - start, u["span"][1] - start]
        rows.append(u)
    doc = {"environment": env, "format": fm["format"], "open_terms": opens, "reading_sets": [], "units": rows}
    Path(out).write_text("---\n" + json.dumps(doc) + "\n---\n" + text)


if __name__ == "__main__":
    main(*sys.argv[1:])
