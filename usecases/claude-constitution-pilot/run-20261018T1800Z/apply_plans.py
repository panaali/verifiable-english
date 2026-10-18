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


# ---------------------------------------------------------------------------------------------------------------- PS-0p
# step 3 (u0286) and step 5 (class B). The wordings are the ones the English vocabulary lint admits without changing an existing wording (ps0p_wordings.py,
# evidence/ps0p/wording-lint.json). u0069 ("Understanding existing deployment contexts": "is a deployment context" is refused, UNARY_MODIFIER) and u0083 ("values other
# than helpfulness" needs the noun “core value”, which waits for PS-6r) are not offered.
PS_UNITS = {
    "u0286.presupposition": {
        "predicate": "open_problem", "wording": "{0} is unsolved", "fence": "Some thing is unsolved.", "open": None,
        "description": "The thing is an open problem, in the source's sense (u0286, “Acknowledging open problems”): a problem that has not been solved. Declared for the heading's presupposition "
                       "(PS-0p): the heading takes for granted that there are open problems, and nothing more.",
        "ast": ["exists", "entity", ["unary", "open_problem", ["var", 0]]]},
    "u0245.presupposition": {
        "predicate": "novel_entity", "wording": "{0} is novel", "fence": "Claude is novel.", "open": "novel_entity",
        "description": "The thing is a novel entity, in the source's sense (u0245, “Claude as a novel entity”). The English lint admits “is novel” but not “is a novel entity” (an \u201cis a ...\u201d "
                       "wording for a unary predicate is refused, UNARY_MODIFIER), so the English drops the noun: the sort already says the argument is a thing. The heading takes for granted that "
                       "Claude is a novel entity, and nothing more.",
        "factors": ["what counts as novel, and novel compared with what (u0245 is a heading; the source's own discussion is in the sentences under it)"],
        "ast": ["unary", "novel_entity", ["const", "claude"]]},
    "u0032.presupposition": {
        "predicate": "genuine_helpfulness", "wording": "{0} is helpful", "fence": "Some thing is helpful.", "open": "genuine_helpfulness",
        "description": "The thing constitutes genuine helpfulness, in the source's sense (u0032, “What constitutes genuine helpfulness”). The English lint admits “is helpful” but refuses “constitutes genuine "
                       "helpfulness” (TEMPLATE_SHAPE) and “is genuinely helpful” (UNARY_MODIFIER), so the English drops “genuine” and “constitutes”; this open term keeps them. The heading takes for granted "
                       "that something constitutes genuine helpfulness, and nothing more.",
        "factors": ["what counts as genuine helpfulness (the source's own discussion is in the sentences under u0032)"],
        "ast": ["exists", "entity", ["unary", "genuine_helpfulness", ["var", 0]]]},
}


PS_NOTE = (
    "Measured in this run (evidence/ps0p/premise-diag-*.txt, premise-variants.json): with QT-0p's `principal_type` (size 3), any existential premise over the sort `entity` that no ground fact names a "
    "witness for makes the whole-document premise check UNKNOWN (u0286 alone; u0032 alone; u0286 with either), because the budget (100,000 evaluations) is spent before the search finds a model and the "
    "ground-fact route has no witness. u0245 (the ground fact `novel_entity(claude)`) keeps the check at `model`. The DRI has not accepted UNKNOWN for the constitution's premise check, so u0286 and "
    "u0032 are reverted (a failing item is reverted alone) and u0245 is kept.")


def ps0p(meta, body, only=None):
    voc = meta["environment"]["vocabulary"]
    fences = b""
    for uid, spec in PS_UNITS.items():
        if only is not None and uid not in only:
            continue
        i = unit_index(meta, uid)
        u = meta["units"][i]
        assert u["kind"] == ["unformalised", "other.discourse"] or u["kind"][0] == "unformalised", (uid, u)
        assert spec["predicate"] not in voc["predicates"], spec["predicate"]
        voc["predicates"][spec["predicate"]] = {"arguments": ["entity"], "description": spec["description"], "verbalisation": spec["wording"]}
        unit = {"id": uid, "span": u["span"], "support": "assumption", "kind": "asserted",
                "meaning": "specified" if spec["open"] is None else {"open": [spec["open"]]},
                "content": {"fence": uid}, "surface": "english"}
        meta["units"][i] = unit
        if spec["open"] is not None:
            meta["open_terms"].append({"name": spec["open"], "arguments": ["entity"], "decided_by": "unresolved_decider", "necessary": [], "sufficient": [],
                                       "factors": spec["factors"], "precedents": [], "jurisdiction": "claude_constitution", "version": 1})
        fences += f"```ve {uid}\n{spec['fence']}\n```\n".encode()
    assert body.endswith(b"```\n")
    return meta, body + fences


def main(argv):
    step = argv[1]
    global TARGET
    only = ["u0245.presupposition"]   # u0286 and u0032 break the premise check (see PS_NOTE), so the default offers u0245 only
    for a in argv[2:]:
        if a.startswith("--only="):
            only = a[len("--only="):].split(",")
        elif a.startswith("--target="):
            TARGET = Path(a[len("--target="):])
    meta, body = read(TARGET)
    if step == "qt0p":
        assert "principal_type" not in meta["environment"]["vocabulary"]["sorts"], "QT-0p already applied"
        meta = qt0p(meta)
    elif step == "ps0p":
        assert "open_problem" not in meta["environment"]["vocabulary"]["predicates"], "PS-0p already applied"
        meta, body = ps0p(meta, body, only)
    else:
        raise SystemExit("usage: apply_plans.py qt0p|ps0p")
    write(TARGET, meta, body)
    print("applied", step)


if __name__ == "__main__":
    main(sys.argv)
