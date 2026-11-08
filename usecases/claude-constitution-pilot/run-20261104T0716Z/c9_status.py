"""SC-9 C9 concrete point-status requests over every reading choice, with Lean as the sole status owner."""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
sys.path.insert(0, str(RUN))
import migrate_soft

pilot = migrate_soft.pilot


def strict_twin(meta):
    """The probe with u0073.s05's default rule as its strict force twin: `mode: strict`, no exception, no `unless`."""
    meta = copy.deepcopy(meta)
    [unit] = [u for u in pilot._flat(meta["units"]) if u["id"] == migrate_soft.CONDITIONED]
    rule = {k: v for k, v in unit["content"]["norm"].items() if k not in ("mode", "exception")}
    unit["content"] = {"norm": {**rule, "unless": []}}
    return meta


def point_status_cases(path):
    """Propose C9 point requests on every compatible choice. Lean supplies each choice's base vocabulary and answers
    every status; this measurement builds only concrete models and UNDECIDED witnesses for Lean to check."""
    from ve.document import load_document
    from ve.readings_route import run_lean
    from ve.readings_verdicts import context

    meta, _ = pilot.read(path)
    probe, _ = pilot.read(migrate_soft.PROBE)
    [rule] = [u["content"]["norm"] for u in pilot._flat(probe["units"]) if u["id"] == migrate_soft.CONDITIONED]
    [target] = [u["content"]["norm"] for u in pilot._flat(meta["units"]) if u["id"] == migrate_soft.CONDITIONED]
    conditions = rule["exception"]["sufficient"]
    if any(formula[:1] != ["unary"] or formula[2] != ["var", 0] for formula in conditions):
        raise ValueError("C9 requires unary sufficient conditions on the situation")
    scenarios = [("c9-unsafe-required", 0), ("c9-unsafe-not-required", 0),
                 *[(f"c9-{formula[1]}", i) for i, formula in enumerate(conditions[1:], 1)],
                 ("c9-none-required", None)]
    [first] = meta["reading_sets"][:1]
    base = next(iter(first["situations"].values()))["base"]
    c = context(load_document(path))
    if c.route != "enumerated" or not c.choices:
        raise ValueError("C9 point statuses require compatible enumerated choices")
    choices = [c.choice_json(choice) for choice in c.choices]
    elaborations = run_lean([{"id": f"c9-choice-{i}", "kind": "readings-choice", "environment": c.environment,
                              "document": c.document, "choice": choice,
                              "inner": {"kind": "norm-defaults-elaborate"}}
                             for i, choice in enumerate(choices)])
    cases, labels = [], []
    for choice, elaboration in zip(choices, elaborations, strict=True):
        inner = elaboration.get("inner", {})
        if elaboration.get("status") != "ok" or inner.get("status") != "ok":
            raise ValueError(f"C9 choice elaboration failed: {elaboration}")
        names = inner["base_environment"]["vocabulary"]["predicates"]
        decision = [name for name in names if name.startswith("soft__excepted__") and
                    name.endswith(rule["name"].replace("-", "_"))]
        if (target.get("mode") == "default") != bool(decision) or len(decision) > 1:
            raise ValueError("C9 decision table does not match its reading")
        for scenario, condition in scenarios:
            model = {"complete": True, "domains": copy.deepcopy(base["domains"]),
                     "constants": copy.deepcopy(base["constants"]),
                     "relations": {name: [] for name in names if not name.startswith("unsaid__")}}
            model["relations"][rule["guard"][1]] = [["s"]]
            if condition is not None:
                model["relations"][conditions[condition][1]] = [["s"]]
                if decision:
                    model["relations"][decision[0]] = [["c", "s"]]
            inner_case = {"kind": "norm-defaults-status", "model": model, "predicate": rule["predicate"],
                          "tuple": ["c", "s"], "method": "undecided" if decision and condition is not None
                          else "table3"}
            if inner_case["method"] == "undecided":
                inner_case.update(yes={"unsaid__" + rule["predicate"]: [["c", "s"]]}, no={})
            cases.append({"id": f"{scenario}:{len(labels) // len(scenarios)}", "kind": "readings-choice",
                          "environment": c.environment, "document": c.document, "choice": choice,
                          "inner": inner_case})
            labels.append(scenario)
    return cases, labels


def point_statuses(path):
    """Print the request and Lean's verbatim row for every C9 situation and choice, including an error or UNKNOWN."""
    from ve.readings_route import run_lean

    cases, labels = point_status_cases(Path(path))
    rows = run_lean(cases)
    print(json.dumps({"cases": [{"scenario": label, "choice": case["choice"], "inner_request": case["inner"],
                                 "answer": row} for label, case, row in zip(labels, cases, rows, strict=True)]},
                     indent=1, ensure_ascii=False))
