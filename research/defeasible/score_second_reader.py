"""DF-0 item 1's bar, applied to a second reader's answers (run when the deferred reader has answered).

    uv run python research/defeasible/score_second_reader.py ANSWERS.json

ANSWERS.json maps unit id to class code for every unit of `second-reader-packet.json`. Bar (plan DF-0 item 1, fixed
before any reading): agreement on "G or not G" on at least 90 of 99 units; if not, research 2.3's G-class figures are
withdrawn and replaced by the second reader's.
"""
from __future__ import annotations

import json
import sys

from common import EVIDENCE


def main(path):
    answers = json.loads(open(path).read())
    packet = json.loads((EVIDENCE / "second-reader-packet.json").read_text())
    key = set(json.loads((EVIDENCE / "second-reader-key.json").read_text())["g_units"])
    ids = [u["id"] for u in packet["units"]]
    if set(answers) != set(ids):
        raise SystemExit("the answers must name every packet unit exactly once")
    if len(ids) != 99:
        raise SystemExit("the bar is stated for the 99 screened units")
    agree = sum((answers[u] == "G") == (u in key) for u in ids)
    need = 90
    print(json.dumps({"units": len(ids), "agree_g_or_not": agree, "bar": need,
                      "result": "PASS" if agree >= need else "FAIL",
                      "second_reader_g": sorted(u for u in ids if answers[u] == "G")}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
