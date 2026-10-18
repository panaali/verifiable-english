#!/usr/bin/env python3
"""Run 20261018T1800Z: the document changes of the plans merged for this run (QT-0p, then PS-0p), applied to `translation-without-content.ve.md`, the input of `nd.py`.

    uv run python usecases/claude-constitution-pilot/run-20261018T1800Z/apply_plans.py qt0p     # QT-0p: u0042.presupposition and u0043.s02
    (nd.py all; probes; document check)
    uv run python usecases/claude-constitution-pilot/run-20261018T1800Z/apply_plans.py ps0p     # PS-0p: u0286 and the class B offers

Each step refuses a second run. The starting file of the run is `prev/translation-without-content.ve.md`.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(RUN))
TARGET = RUN / "translation-without-content.ve.md"
SOURCE = (RUN.parent / "source/claude-constitution.md").read_bytes()
EVIDENCE = RUN / "evidence/qt0p-constitution-u0042-u0043.ve.md"   # git show research/quantities-p1:docs/research/evidence/quantities/qt0p/constitution-u0042-u0043.ve.md

READ_SPLIT = b"---\n"


def read(path):
    raw = Path(path).read_bytes()
    _, front, body = raw.split(READ_SPLIT, 2)
    return json.loads(front), body


def write(path, meta, body):
    Path(path).write_bytes(READ_SPLIT + json.dumps(meta, ensure_ascii=False).encode() + b"\n" + READ_SPLIT + body)


def unit_index(meta, unit_id):
    return next(i for i, u in enumerate(meta["units"]) if u["id"] == unit_id)


def shift(unit, delta):
    unit = copy.deepcopy(unit)
    unit["span"] = [unit["span"][0] + delta, unit["span"][1] + delta]
    for p in unit.get("parts", []):
        p["span"] = [p["span"][0] + delta, p["span"][1] + delta]
    return unit


# ---------------------------------------------------------------------------------------------------------------- QT-0p
QT_UNITS = ["u0042.presupposition", "u0043.s01", "u0043.s02"]
QT_SPANS = {"u0042.presupposition": [23448, 23486], "u0043.s01": [23486, 23587], "u0043.s02": [23587, 23677]}
QT_PARTS = {"u0043.s02.p1": [23587, 23602], "u0043.s02.p2": [23602, 23677]}


def qt0p(meta):
    """QT-0p, constitution part: the content of docs/research/evidence/quantities/qt0p/constitution-u0042-u0043.ve.md (research/quantities-p1), re-offset to this source."""
    ev, _ = read(EVIDENCE)
    ev_units = {u["id"]: u for u in ev["units"]}
    # 1. the three units' spans and kinds are as the plan expects
    for uid in QT_UNITS:
        i = unit_index(meta, uid)
        u = meta["units"][i]
        assert u["span"] == QT_SPANS[uid] and u["kind"] == ["unformalised", "counting"], (uid, u)
    assert SOURCE[23448:23486] == "Claude’s three types of principals\n\n".encode()
    assert SOURCE[23587:23602] == b"At the moment, " and SOURCE[23602:23677].startswith("Claude’s three types".encode())
    # 2. the vocabulary (sort, constants, predicate)
    voc = meta["environment"]["vocabulary"]
    evoc = ev["environment"]["vocabulary"]
    assert "principal_type" not in voc["sorts"] and not set(evoc["constants"]) & set(voc["constants"]) and "claude_principal_type" not in voc["predicates"]
    voc["sorts"]["principal_type"] = evoc["sorts"]["principal_type"]
    voc["constants"].update(evoc["constants"])
    voc["predicates"]["claude_principal_type"] = evoc["predicates"]["claude_principal_type"]
    # 3. the units: u0042.presupposition CHECKED; u0043.s01 unchanged; u0043.s02 MIXED
    delta = 23448
    for uid in ("u0042.presupposition", "u0043.s02"):
        new = shift(ev_units[uid], delta)
        assert new["span"] == QT_SPANS[uid]
        meta["units"][unit_index(meta, uid)] = new
    p = [x["span"] for x in meta["units"][unit_index(meta, "u0043.s02")]["parts"]]
    assert p == [QT_PARTS["u0043.s02.p1"], QT_PARTS["u0043.s02.p2"]], p
    for uid, part in zip(QT_PARTS, meta["units"][unit_index(meta, "u0043.s02")]["parts"]):
        assert part["id"] == uid
    return meta


def main(argv):
    step = argv[1]
    meta, body = read(TARGET)
    if step == "qt0p":
        assert "principal_type" not in meta["environment"]["vocabulary"]["sorts"], "QT-0p already applied"
        meta = qt0p(meta)
    else:
        raise SystemExit("usage: apply_plans.py qt0p|ps0p")
    write(TARGET, meta, body)
    print("applied", step)


if __name__ == "__main__":
    main(sys.argv)
