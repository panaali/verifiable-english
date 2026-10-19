"""ET-8: the ET-1 component (the seven hard constraints, as run in phase 1) on the completion.

`python experiments/events-time-causation/et8_component.py` writes
`docs/events-time-causation/et-8/evidence/component.json` (the switched component) and `component-results.json`.
Phase 1 completed "may be given" (`permitted`) to allow, with the legend "'may be given' means no hard constraint
forbids it". Here `permitted` is completed `unspecified` under `norm-defaults@0` and the legend is removed from its
description: when no rule decides, the text does not say whether a response may be given. The plan pre-judges no
outcome (FOLLOWABLE resting on a stated permission, or DILEMMA `UNSETTLED(refuse)`); this records which Lean answers:

1. elaboration, and CONFLICT-FREE from certificates the prover finds and Lean replays;
2. FOLLOWABLE from a certificate over the premises Lean binds, if the prover finds one;
3. DILEMMA witnesses with the filling that permits nothing unsaid: phase 1's scenario, and one decision whose only
   response is refusal (the response u0172.s02's first premise makes available at every decision);
4. the scenario's status for each response;
5. for comparison only, the same component with u0172.s02 read as a permission ("Every response that is inaction
   may be given, unless a hard constraint forbids it"). That reading is the targeted audit's to accept; it is not
   the component's.
"""
from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tests import test_alternatives_fill as fill  # noqa: E402
from ve.alternatives import run_case  # noqa: E402

OUT = REPO / "docs/events-time-causation/et-8/evidence"
PHASE1 = REPO / "tests/data/et7/et1-component.json"
MAY_BE_GIVEN = "The response may be given"
NOTHING_UNSAID = {"unsaid__permitted": []}


def component():
    """Phase 1's component with `permitted` completed `unspecified` and the legend removed."""
    phase1 = json.loads(PHASE1.read_text())
    raw = deepcopy(phase1["environment"])
    raw["profiles"] = sorted({*raw["profiles"], "norm-defaults@0"})
    permitted = raw["vocabulary"]["predicates"]["permitted"]
    permitted["description"] = MAY_BE_GIVEN
    permitted["regulated"]["default"] = "unspecified"
    return {"id": "et8-hard-constraints", "environment": raw, "norms": phase1["norms"],
            "units": phase1["units"]}, phase1["scenario"]


def refusal_only():
    """One decision whose only available response is refusal."""
    relations = {"available": [["refuse", "d"]], "leads_to": [], "inaction": [["refuse"]]}
    model = {"complete": True, "domains": {"decision": ["d"], "response": ["refuse"], "harm": ["attack"]},
             "constants": {}, "relations": relations}
    return {"model": model, "outcomes": [{"action": "refuse", "harm": "attack", "leads_to": False,
                                          "support": "testimony"}]}


def with_relations(situation, names):
    """Every predicate of the base vocabulary has a table in a complete model."""
    out = deepcopy(situation)
    for name in names:
        out["model"]["relations"].setdefault(name, [])
    return out


def permission_reading(src):
    """u0172.s02 read as a permission (comparison only): inaction may be given unless a hard constraint forbids it."""
    rule = {"norm": {"name": "u0172-s02-refusal-may-be-given", "predicate": "permitted", "sign": True,
                     "guard": ["unary", "inaction", ["var", 0]],
                     "unless": [r["norm"]["guard"] for r in src["norms"]], "over": []}}
    return src | {"norms": [*src["norms"], rule]}


def answers(src, situations):
    elaborated = fill.elaborate(src)
    packages = {**fill.conflict_packages(src, elaborated), **fill.conflict_packages(src, elaborated, slots=False)}
    conflict = run_case(src | {"kind": "alt-conflict", "packages": packages})
    package = fill.followable_package(src, elaborated)
    followable = run_case(src | {"kind": "alt-followable", "packages": packages,
                                 **({"package": package} if package else {})})
    out = {"unspecified": elaborated["unspecified"], "unsaid": [x["name"] for x in elaborated["unsaid"]],
           "unmapped_obligations": elaborated["unmapped_obligations"],
           "conflict": {k: conflict.get(k) for k in ("verdict", "detail")},
           "conflict_targets": [t["target"] for t in elaborated["conflict_targets"]],
           "followable_certificate": package is not None,
           "followable": {k: followable.get(k) for k in ("verdict", "text", "conditional_on")}}
    for name, situation in situations.items():
        witness = {**situation, "chooser": "d", "filling": NOTHING_UNSAID}
        row = run_case(src | {"kind": "alt-followable", "packages": packages, "witness": witness})
        validate = run_case(src | {"kind": "alt-validate", "scenario": situation})
        (chooser,) = validate["choosers"]
        out[name] = {"witness": {k: row.get(k) for k in ("verdict", "diagnosis", "text")},
                     "scenario": dict(zip(chooser["alternatives"], zip(chooser["statuses"], chooser["evidence"]))),
                     "scenario_text": chooser["text"]}
    return out


def compute():
    src, scenario = component()
    names = [p for p, d in src["environment"]["vocabulary"]["predicates"].items() if "regulated" not in d]
    situations = {"phase1_scenario": scenario, "refusal_only": with_relations(refusal_only(), names)}
    return src | {"scenario": scenario}, {"component": answers(src, situations),
                                          "permission_reading": answers(permission_reading(src), situations)}


def main():
    src, results = compute()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "component.json").write_text(json.dumps(src, indent=1) + "\n")
    (OUT / "component-results.json").write_text(json.dumps(results, indent=1, sort_keys=True) + "\n")
    print(json.dumps(results, indent=1)[:8000])


if __name__ == "__main__":
    main()
