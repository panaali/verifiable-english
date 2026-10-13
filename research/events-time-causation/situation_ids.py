"""Recompute the content-addressed ids of a document's reading-set situations after a vocabulary change.

A situation's id is the digest of the whole situation under the document's environment id
(Lean `VE.Readings.Wire.decodeSituation`; computed with `tests/test_readings_s1_lean.py` `situation_id`, as the
pilot's own `refusal_test.py` does), so any new sort or
predicate changes it. `extend` adds one element per new sort and an empty relation per new predicate
to every situation, then renames each situation and every `distinguishing_models` reference to the new id.
`check_ids` recomputes the ids of an unchanged document, to show the method reproduces the stored ones.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tests.test_readings_s1_lean import situation_id  # noqa: E402


def check_ids(fm):
    out = []
    for rs in fm["reading_sets"]:
        for sid, s in rs["situations"].items():
            out.append((rs["id"], sid, situation_id(fm["environment"], s)))
    return out


def extend(fm, new_sorts, new_predicates):
    renames = {}
    for rs in fm["reading_sets"]:
        situations = {}
        for sid, s in rs["situations"].items():
            base = s["base"]
            for sort in new_sorts:
                base["domains"][sort] = [sort]
            for pred in new_predicates:
                base["relations"][pred] = []
            base["domains"] = dict(sorted(base["domains"].items()))
            base["relations"] = dict(sorted(base["relations"].items()))
            new = situation_id(fm["environment"], s)
            renames[sid] = new
            situations[new] = s
        rs["situations"] = situations
        for r in rs["readings"]:
            dm = r.get("admission", {}).get("distinguishing_models")
            if dm:
                r["admission"]["distinguishing_models"] = {k: renames.get(m, m) for k, m in dm.items()}
    return renames


if __name__ == "__main__":
    lines = Path(sys.argv[1]).read_text().split("\n")
    for row in check_ids(json.loads(lines[1])):
        print(*row, "same" if row[1] == row[2] else "DIFFERENT")
