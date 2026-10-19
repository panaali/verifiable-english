#!/usr/bin/env python3
"""Run 20261012T1800Z: repair of the five units the audit of run 20261012T0600Z rejected (AUDIT-20261012T0600Z-received.md).

    uv run python usecases/claude-constitution-pilot/run-20261012T1800Z/repair_20261012T1800Z.py
        # base/ + prev/units.json -> translation-without-content.ve.md, readings/all-strict.ve.md, units.json
    uv run python usecases/claude-constitution-pilot/run-20261012T1800Z/nd.py all   # adds the content of the three "should" reading sets

* u0125.s04.p2 ("Claude should never directly deny that it is Claude"): the defeasible candidate invented an exception. "General honesty is
  basically never violated" (u0109.s06) does not state an exception to this specific prohibition, and u0170.s01 says the hard-constraint list is
  not a list of all the behaviours Claude should never exhibit. The reading set `force-u0125-s04-p2`, its open term
  `exception_to_never_denying_being_claude` and everything that mentioned them go; the unit has ONE reading (the strict prohibition, a
  permission predicate with a negative rule, completion unspecified), written as content on the unit.
* u0165.s01 to u0165.s07 (the audit rejected s02, s03, s05 and s07; the other three are the same class): the absolute prohibitions depended on the
  action category alone. u0173.s01-s04 say the hard constraints are "centrally meant to apply to cases where Claude would either be knowingly and
  intentionally engaging in an action of the relevant restricted category, or where Claude thinks it quite likely that a given action would fall
  into such a category"; for "more unclear or uncertain" cases Claude is to be "guided by the more holistic and nuanced prioritization"; and Claude
  "could in principle end up contributing unknowingly ... without actually violating one of the constraints". The guard of each rule is now the
  category's case atom AND the new open term `restricted_action_knowing_or_quite_likely`; where the guard does not hold the rule says nothing
  (completion unspecified), so unclear and unknowing cases are not decided by the constraint.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(RUN))

_spec = importlib.util.spec_from_file_location("readings_s1_pilot", ROOT / "tools/readings_s1_pilot.py")
pilot = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pilot)
import spec_nd as nd  # noqa: E402
from ve.document import _environment  # noqa: E402

RUN_ID = "20261012T1800Z"
SET = "force-u0125-s04-p2"
UNIT = "u0125.s04.p2"
GONE_TERM = "exception_to_never_denying_being_claude"
HC_UNITS = [f"u0165.s0{i}" for i in range(1, 8)]
HC_REJECTED = ["u0165.s02", "u0165.s03", "u0165.s05", "u0165.s07"]
KNOW = "restricted_action_knowing_or_quite_likely"
KNOW_VERBALISATION = ("{0} is a case in which Claude would be knowingly and intentionally engaging in an action of the relevant restricted category, "
                      "or in which Claude thinks it quite likely that the action would fall into such a category")
KNOW_DESCRIPTION = ("u0173.s01: the hard constraints are “centrally meant to apply to cases where Claude would either be knowingly and intentionally "
                    "engaging in an action of the relevant restricted category, or where Claude thinks it quite likely that a given action would fall "
                    "into such a category”. Which situations these are is the open term " + KNOW + ".")
KNOW_TERM = {"name": KNOW, "arguments": [nd.SITUATION], "decided_by": "unresolved_decider", "necessary": [], "sufficient": [],
             "factors": ["what counts as Claude knowingly and intentionally engaging in an action of the relevant restricted category",
                         "how likely counts as Claude thinking it quite likely that an action would fall into such a category"],
             "precedents": [], "jurisdiction": "claude_constitution", "version": 1}


def add_know(meta):
    meta = copy.deepcopy(meta)
    meta["environment"]["vocabulary"]["predicates"][KNOW] = nd.base([nd.SITUATION], KNOW_VERBALISATION, KNOW_DESCRIPTION)
    assert KNOW not in [t["name"] for t in meta["open_terms"]]
    meta["open_terms"].append(copy.deepcopy(KNOW_TERM))
    done = []
    for u in pilot._flat(meta["units"]):
        if u["id"] in HC_UNITS:
            case = u["content"]["norm"]["guard"]
            assert case[0] == "unary" and case[2] == ["var", 0] and u["content"]["norm"]["unless"] == [], u["id"]
            u["content"]["norm"]["guard"] = ["and", case, nd.un(KNOW, 0)]
            assert KNOW not in u["meaning"]["open"]
            u["meaning"]["open"] = [*u["meaning"]["open"], KNOW]
            done.append(u["id"])
    assert done == HC_UNITS, done
    return meta


def drop_relation(x, name):
    if isinstance(x, dict):
        if isinstance(x.get("relations"), dict):
            x["relations"].pop(name, None)
        for v in x.values():
            drop_relation(v, name)
    elif isinstance(x, list):
        for v in x:
            drop_relation(v, name)


def main():
    strict, strict_source = pilot.read(RUN / "base/all-strict.ve.md")
    strict_content = {u["id"]: u["content"] for u in pilot._flat(strict["units"]) if u.get("content")}
    meta, source = pilot.read(RUN / "base/translation-without-content.ve.md")
    meta = add_know(meta)
    # u0125.s04.p2: the reading set, its open term and its stored models' relation go; the unit carries its one reading
    assert [s["unit"] for s in meta["reading_sets"] if s["id"] == SET] == [UNIT]
    meta["reading_sets"] = [s for s in meta["reading_sets"] if s["id"] != SET]
    assert GONE_TERM not in [t["name"] for t in meta["open_terms"]] and GONE_TERM not in meta["environment"]["vocabulary"]["predicates"]
    drop_relation(meta["reading_sets"], GONE_TERM)
    for u in pilot._flat(meta["units"]):
        if u["id"] == UNIT:
            assert u.get("content") is None and u["kind"] == "norm"
            u["content"] = copy.deepcopy(strict_content[UNIT])
    env = _environment(meta["environment"])
    meta["reading_sets"] = [pilot._reidentified(env, item) if all(r.get("content") is None for r in item["readings"]) else item
                            for item in meta["reading_sets"]]
    assert len(meta["reading_sets"]) == 3
    pilot.write(RUN / "translation-without-content.ve.md", meta, source)
    strict2 = add_know(strict)
    (RUN / "readings").mkdir(exist_ok=True)
    pilot.write(RUN / "readings/all-strict.ve.md", strict2, strict_source)
    print("ok", len(meta["open_terms"]), [s["id"] for s in meta["reading_sets"]])


if __name__ == "__main__":
    main()
