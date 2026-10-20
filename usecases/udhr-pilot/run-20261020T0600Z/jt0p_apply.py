"""JT-0p item 2 (judgment-terms plan): u010 and u060 as asserted judgments, applied to this run's four parts, the whole declaration and the legacy form.

Adapted from research/judgment-terms/jt0p.py on research/judgment-terms-p1 (the encoding of the phase-1 report, 1.3.2); this run's parts are the base,
never the reference run's.  Nothing here calls a model.

    uv run --frozen python usecases/udhr-pilot/run-20261018T1800Z/jt0p_apply.py [--check-only]

The shared record list changes in every document (greatest_importance -> of_greatest_importance_for, natural_group_unit ->
natural_and_fundamental_group_unit_of_society, replaced in place).  The sort `thing`, the constants and the predicate come only to the documents that
hold the unit that uses them.  The reading-set ids are recomputed by vocab_patch.py (the reference build's rule); the committed `--rebuild-reading-ids` command is not usable on this pilot's
S1 sets (see vocab_patch.py and evidence/rebuild-command.json).
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import vocab_patch as V

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
DOCS = {"part01": HERE / "translation-part01.ve.md", "part02": HERE / "translation-part02.ve.md",
        "part03": HERE / "translation-part03.ve.md", "part04": HERE / "translation-part04.ve.md",
        "whole": HERE / "experiment-whole" / "translation-whole.ve.md", "legacy": HERE / "translation.ve.md"}

U010_TERM, U060_TERM = "of_greatest_importance_for", "natural_and_fundamental_group_unit_of_society"
UNDERSTANDING = "common_understanding_of_these_rights_and_freedoms"
REALIZATION = "full_realization_of_this_pledge"
FAMILY = "the_family"

THING = {"description": "a thing the text names: an understanding, an aim or an institution",
         "verbalisation": {"plural": "things", "singular": "thing"}}


def record(name, arguments, factors):
    return {"arguments": arguments, "decided_by": "unresolved_decider", "factors": factors, "jurisdiction": "universal",
            "name": name, "necessary": [], "precedents": [], "sufficient": [], "version": 1}


REPLACE = {
    "greatest_importance": record(U010_TERM, ["understanding", "realization"], ["comparison class", "measure of importance"]),
    "natural_group_unit": record(U060_TERM, ["thing"], ["meaning of natural", "meaning of fundamental",
                                                        "what counts as a group unit of society"]),
}
U010_CONSTANTS = {
    UNDERSTANDING: {"sort": "thing",
                    "description": "a common understanding of these rights and freedoms: the human rights and fundamental "
                                   "freedoms whose universal respect and observance the Member States have pledged "
                                   "themselves to promote (the preceding clause, u009)"},
    REALIZATION: {"sort": "thing",
                  "description": "the full realization of this pledge: the pledge of the Member States in the preceding clause (u009)"},
}
U010_PREDICATE = {U010_TERM: {"arguments": ["thing", "thing"],
                              "description": "The first thing is of the greatest importance for the second; the open term "
                                             f"{U010_TERM} (a judgment; the text does not say who makes it)"}}
# No verbalisation for the binary predicate: the wording lint rejects "{0} is of the greatest importance for {1}".
U060_CONSTANTS = {FAMILY: {"sort": "thing", "description": "the family, the institution the Article names, not any one family"}}
U060_PREDICATE = {U060_TERM: {"arguments": ["thing"],
                              "description": "The thing is the natural and fundamental group unit of society; the open term "
                                             f"{U060_TERM} (a judgment; the text does not say who makes it)",
                              "verbalisation": "{0} is the natural and fundamental group unit of society"}}
UNITS = {
    "u010": {"kind": "asserted", "meaning": {"open": [U010_TERM]}, "support": "none",
             "content": {"ast": ["binary", U010_TERM, ["const", UNDERSTANDING], ["const", REALIZATION]]}},
    "u060": {"kind": "asserted", "meaning": {"open": [U060_TERM]}, "support": "none",
             "content": {"ast": ["unary", U060_TERM, ["const", FAMILY]]}},
}


def read(path):
    raw = Path(path).read_bytes()
    _, front, source = raw.split(b"---\n", 2)
    return json.loads(front), source


def write(path, meta, source):
    Path(path).write_bytes(b"---\n" + json.dumps(meta, ensure_ascii=False).encode() + b"\n---\n" + source)


def apply(meta, units=True):
    meta = copy.deepcopy(meta)
    terms = meta["open_terms"]
    names = [t["name"] for t in terms]
    for old, new in REPLACE.items():
        assert old in names and new["name"] not in names, old
        terms[names.index(old)] = new
    ids = {u["id"] for u in meta["units"]} if units else set()
    vocab = meta["environment"]["vocabulary"]
    new_constants, new_predicates = {}, {}
    for uid, constants, predicate in (("u010", U010_CONSTANTS, U010_PREDICATE), ("u060", U060_CONSTANTS, U060_PREDICATE)):
        if uid not in ids:
            continue
        vocab["sorts"].setdefault("thing", THING)
        assert vocab["sorts"]["thing"] == THING
        for k, v in constants.items():
            assert k not in vocab["constants"]
            vocab["constants"][k] = v
        for k, v in predicate.items():
            assert k not in vocab["predicates"]
            vocab["predicates"][k] = v
        new_constants.update(constants)
        new_predicates.update(predicate)
        unit = next(u for u in meta["units"] if u["id"] == uid)
        assert unit["kind"] == ["unformalised", "other_evaluative_open_claim"], unit
        span = unit["span"]
        for key in ("kind", "meaning", "support", "content"):
            unit.pop(key, None)
        unit.update(copy.deepcopy(UNITS[uid]))
        assert unit["span"] == span
    if new_constants:
        # every model and situation base gets the new sort, its constants and the new relations; every id is recomputed over the new environment
        meta["reading_sets"] = V.reidentified(
            meta["environment"], meta["reading_sets"], {"thing": ["thing"]}, {c: "thing" for c in new_constants},
            list(new_predicates), list(new_predicates))
    return meta


def main():
    for name, path in DOCS.items():
        meta, src = read(path)
        write(path, apply(meta, units=name != "legacy"), src)
        print("applied JT-0p to", name, flush=True)


if __name__ == "__main__":
    main()
