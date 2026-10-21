"""Audit repairs of run 20261021T0600Z (the 20261020T1800Z audit rejected u042, u043, u060 and u061).  Nothing here calls a model.

    uv run --frozen python usecases/udhr-pilot/run-20261021T0600Z/repair_20261021.py [--dry-run]

* u042, u043 (Article 11(2)): back to UNFORMALISED (missing feature `time`), as they were before ET-0.  The audit accepted the reification of
  findings and acts but rejected the civil `day`: it cannot tell an act committed before a change within a day from one committed after it;
  and for u043 it rejected the every/some pair, because "the one that was applicable" names one comparison penalty and the words do not
  license two quantifications.  Every trace goes: the sorts finding, act, day, imposition, penalty and applicability; the seven predicates
  that used them; the open term `heavier`; the reading set rs_u043.  (The pre-registered content stays in evidence/, as history.)
* u060 (Article 16(3), first clause): the content now also states the uniqueness of "the ... group unit": the family is a natural and
  fundamental group unit of society, and whatever is one is the family.
* u061 (Article 16(3), second clause): the subject is the same institution as u060's (`the_family`), not "every family": the content is
  one ground atom of the shared sort `thing`.  The sort `family` (used by no other unit) and its domains are removed.

Every reading-set id is recomputed over the new environment with vocab_patch.reidentified_by (the identity transform reproduces the old ids).
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2]))
import vocab_patch as V  # noqa: E402

DOCS = {"part01": HERE / "translation-part01.ve.md", "part02": HERE / "translation-part02.ve.md",
        "whole": HERE / "experiment-whole" / "translation-whole.ve.md"}

ET0_SORTS = ["finding", "act", "day", "imposition", "penalty", "applicability"]
ET0_PREDICATES = ["finding_of_guilt_permitted", "on_account_of", "committed_on", "constitutes_penal_offence_on",
                  "imposition_permitted", "imposes", "imposed_for", "applicability_of", "applicability_to", "applicable_on", "heavier_than"]
ET0_RELATIONS = [*ET0_PREDICATES, *[f"unsaid__{p}" for p in ET0_PREDICATES]]

P_FAMILY = "natural_and_fundamental_group_unit_of_society"
P_ENTITLED = "is_entitled_to_protection_by_society_and_the_state"
FAMILY = "the_family"

U060_CONTENT = {"ast": ["and", ["unary", P_FAMILY, ["const", FAMILY]],
                        ["forall", "thing", ["implies", ["unary", P_FAMILY, ["var", 0]], ["eq", ["var", 0], ["const", FAMILY]]]]]}
U061_CONTENT = {"ast": ["unary", P_ENTITLED, ["const", FAMILY]]}
ENTITLED_PREDICATE = {"arguments": ["thing"],
                      "description": "The thing is entitled to protection by society and the State (here the thing is the family, the institution "
                                     "Article 16 names, as in the previous clause)",
                      "verbalisation": "{0} is entitled to protection by society and the State"}


def read(path):
    raw = Path(path).read_bytes()
    _, front, source = raw.split(b"---\n", 2)
    return json.loads(front), source


def write(path, meta, source):
    Path(path).write_bytes(b"---\n" + json.dumps(meta, ensure_ascii=False).encode() + b"\n---\n" + source)


def revert_et0(meta):
    vocab = meta["environment"]["vocabulary"]
    for s in ET0_SORTS:
        assert s in vocab["sorts"], s
        del vocab["sorts"][s]
    for p in ET0_PREDICATES:
        assert p in vocab["predicates"], p
        del vocab["predicates"][p]
    names = [t["name"] for t in meta["open_terms"]]
    assert "heavier" in names
    meta["open_terms"] = [t for t in meta["open_terms"] if t["name"] != "heavier"]
    assert sum(s["unit"] == "u043" for s in meta["reading_sets"]) == 1
    meta["reading_sets"] = [s for s in meta["reading_sets"] if s["unit"] != "u043"]
    for uid in ("u042", "u043"):
        unit = next(u for u in meta["units"] if u["id"] == uid)
        span = unit["span"]
        for k in list(unit):
            if k not in ("id", "span"):
                del unit[k]
        unit.update({"kind": ["unformalised", "time"], "meaning": {"unformalised": "time"}, "support": "none"})
        assert unit["span"] == span
    meta["units"] = [dict(sorted(u.items(), key=lambda kv: ("id", "kind", "meaning", "span", "support").index(kv[0]))) if u["id"] in ("u042", "u043") else u
                     for u in meta["units"]]


def repair_family(meta):
    vocab = meta["environment"]["vocabulary"]
    assert vocab["constants"][FAMILY]["sort"] == "thing" and vocab["predicates"][P_ENTITLED]["arguments"] == ["family"]
    del vocab["sorts"]["family"]
    vocab["predicates"][P_ENTITLED] = copy.deepcopy(ENTITLED_PREDICATE)
    for uid, content in (("u060", U060_CONTENT), ("u061", U061_CONTENT)):
        unit = next(u for u in meta["units"] if u["id"] == uid)
        assert unit["kind"] == "asserted", unit
        unit["content"] = copy.deepcopy(content)


def transform(data):
    return V.dropped(data, sorts=[*ET0_SORTS, "family"], relations=ET0_RELATIONS)


def apply(label, meta):
    meta = copy.deepcopy(meta)
    if label in ("part01", "whole"):
        revert_et0(meta)
    if label in ("part02", "whole"):
        repair_family(meta)
    meta["reading_sets"] = V.reidentified_by(meta["environment"], meta["reading_sets"], transform)
    return meta


def main():
    dry = "--dry-run" in sys.argv
    for label, path in DOCS.items():
        meta, src = read(path)
        new = apply(label, meta)
        if not dry:
            write(path, new, src)
        print("repaired", label, "(dry run)" if dry else "", flush=True)


if __name__ == "__main__":
    main()
