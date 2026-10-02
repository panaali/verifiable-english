#!/usr/bin/env python3
"""Post-seal scoring wrapper for risk wording probe 2 (not in the manifest; written after the run).

    python3 score_one_text.py

The sealed score.py finds a reader's block for text n only at a heading such as "Text 1". That fits the first
probe, whose sessions held up to eight texts. Here every session holds exactly one text (one construct, at most one
item per construct per session), and no reader wrote a heading, so the sealed splitter finds no block and marks all
32 answers unparseable (RESULTS.sealed-parser.md, scored.sealed-parser.json). This wrapper changes one thing: when a
session has one text, the whole response is that text's block. The sealed option-picking rules (score.pick), key,
critical labels and decision code run unchanged; nothing sealed is edited.
"""

import score

_sealed_blocks = score.blocks


def blocks(response, count):
    if count == 1:
        return {1: response}
    return _sealed_blocks(response, count)


score.blocks = blocks

if __name__ == "__main__":
    score.main()
