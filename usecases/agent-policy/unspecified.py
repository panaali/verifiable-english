"""Re-runs the agent-policy case with both completions `unspecified` (norm-defaults@0).

The policy states no default for either regulated predicate (PLAN section 3.2),
so `environment.unspecified.json` says so: where no rule decides, the text is
silent. This harness computes the status of `permitted(a)` and
`report_required(a)` (docs/spec/norm-defaults.md 2.5) for every logged action
whose record is one finite model (results.json M8), compares each with the
completed outcomes of the four shipped environments, and replays every status,
the a10 conflict witness and both gap witnesses through Lean's norm-defaults
route on the flag-free copy `environment.unspecified.lean.json`.

`python usecases/agent-policy/unspecified.py --write` merges the result into
`results.json` under `unspecified`. It never reads the answer key; the tests
compare the result with the key afterwards.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO))

import check  # noqa: E402
from itertools import product  # noqa: E402

from ve import norm_defaults as nd  # noqa: E402
from ve import norm_defaults_route as route  # noqa: E402
from ve.environment import Environment  # noqa: E402
from ve.norms import NormDocument  # noqa: E402

PREDICATES = (check.PERMISSION, check.OBLIGATION)
# The completed outcome columns of results.json, per predicate.
COLUMNS = {check.PERMISSION: ("deny", "allow"), check.OBLIGATION: ("need not", "must")}
CONFLICT_ACTION = "a10"
# A situation where each predicate's gap is reached: a27 is NOT-COVERED and no reporting rule covers it.
GAP_ACTION = "a27"


def _documents(action, inventory, record):
    """Lean's accepted document and the flag-free finite situation for a record."""
    env = check.environment(action=action, data=check.read_json("environment.unspecified.lean.json"))
    document = nd.UnspecifiedDocument(env, check.policy().rules)
    situation = check.record_model(document.situation_environment(), (*inventory, *record))
    return document, situation


def _answer(row, field):
    if row.get("status") != "ok":
        raise AssertionError(f"Lean rejected {row.get('id')}: {row.get('error')}")
    return row[field]


def _fillings(document, situation):
    """Enumerate the finite filling choices for this one-action situation."""
    names = [item["name"] for item in document.elaboration["unsaid"]]
    domains = situation.domains
    for bits in product((False, True), repeat=len(names)):
        filling = {name: ([list(values) for values in product(*(domains[s] for s in item["sorts"]))]
                          if bit else [])
                   for name, item, bit in zip(names, document.elaboration["unsaid"], bits, strict=True)}
        yield filling


def _status(document, situation, predicate, action):
    model = situation.to_dict()
    case = route.source_case(document, "norm-defaults-status", model=model,
                             predicate=predicate, tuple=[action], method="enumerate")
    row = route.run_cases([case])[0]
    answer = _answer(row, "point_status")
    count = 1
    if answer == "UNKNOWN":
        fillings = list(_fillings(document, situation))
        yes, no = fillings[-1], fillings[0]
        row = route.run_cases([{**case, "method": "undecided", "yes": yes, "no": no}])[0]
        answer = _answer(row, "point_status")
        count += 1
    return answer, count


def _conflict(document, situation, action):
    """Lean checks every filling and every conflict target in its elaboration."""
    model = situation.to_dict()
    cases = []
    for filling in _fillings(document, situation):
        filled = {**model, "relations": {**model["relations"], **filling}}
        for item in document.elaboration["conflict_targets"]:
            cases.append(route.source_case(document, "norm-defaults-conflict", witness={
                "target": item["target"], "model": filled, "tuple": [action]}))
    rows = route.run_cases(cases)
    found = [_answer(row, "verdict") == "CONFLICT" for row in rows]
    targets = [case["witness"]["target"] for case, yes in zip(cases, found, strict=True) if yes]
    if not targets:
        return None, len(cases)
    target = targets[0]
    choices = sum(case["witness"]["target"] == target for case in cases)
    kind = "settled" if targets.count(target) == choices else "latent"
    return (target, kind), len(cases)


def _reason(predicate, after, action):
    if after.startswith("SETTLED") or after == "CONFLICT":
        return ""
    if action == CONFLICT_ACTION:
        return ("no reporting rule covers a10; under a deny or allow completion the permission conflict made every "
                "completed outcome a contradiction, but an admissible filling still answers either way")
    if predicate == check.PERMISSION:
        return "no rule decides the action (NOT-COVERED), and the policy states no default"
    return "rules 25 and 26 do not cover the action, and the policy states no default"


def run():
    started = time.time()
    results = check.read_json("results.json")
    complete = results["M8"]["finite_model_complete_records"]
    inventory, records = check.parse_log((HERE / "log.ve").read_text())
    actions, changes = {}, []
    lean_cases = 0
    conflict = gaps = None
    for action in complete:
        document, situation = _documents(action, inventory, records[action])
        statuses = {}
        for predicate in PREDICATES:
            statuses[predicate], count = _status(document, situation, predicate, action)
            lean_cases += count
        conflict_result, count = _conflict(document, situation, action)
        lean_cases += count
        actions[action] = dict(statuses)
        actions[action]["conflict"] = "CONFLICT" if conflict_result else "none"
        if conflict_result:
            if action != CONFLICT_ACTION:
                raise AssertionError(f"unexpected conflict at {action}")
            target, kind = conflict_result
            numbers = check.numbers(document.author.rules)
            # W1 selection supplies display rule numbers; Lean supplies the verdict.
            display = NormDocument(Environment(nd._placeholder(document.env.to_dict())),
                                   document.author.rules)
            selected = display.selected_rules(target, situation, (action,))
            conflict = {"action": action, "target": target, "kind": kind,
                        "rules": sorted(numbers[r.name] for r in selected)}
        if action == GAP_ACTION:
            line_row = nd.report(document, model=situation.to_dict(), predicates=PREDICATES)
            lean_cases += 1
            gaps = {line["predicate"]: {"lines": line["lines"], "witness": action}
                    for line in line_row["report"]}
            inherits = {line["predicate"]: line["inherits_from"] for line in line_row["report"]}
        for predicate in PREDICATES:
            outcomes = results["actions"][action]["outcomes"][predicate]
            before = {column: outcomes[column] for column in COLUMNS[predicate]}
            after = actions[action][predicate]
            if predicate == check.PERMISSION and actions[action]["conflict"] == "CONFLICT":
                after = "CONFLICT"
            settled = {"SETTLED yes": "P", "SETTLED no": "F", "CONFLICT": "⊥"}.get(after)
            if set(before.values()) != {settled}:
                changes.append({"action": action, "predicate": predicate, "before": before, "after": after,
                                "reason": _reason(predicate, after, action)})
    breaches = {"settled": [], "undecided": []}
    for action, entry in actions.items():
        approved = entry[check.PERMISSION] == "SETTLED yes" and entry["conflict"] == "none"
        if not approved or results["actions"][action]["reported"]:
            continue
        if entry[check.OBLIGATION] == "SETTLED yes":
            breaches["settled"].append(action)
        elif entry[check.OBLIGATION] == "UNDECIDED":
            breaches["undecided"].append(action)
    raw = check.read_json("environment.unspecified.json")
    return {
        "environment_id": Environment(raw).environment_id,
        "records": complete,
        "not_one_finite_model": sorted(set(results["actions"]) - set(complete)),
        "actions": actions,
        "changes": changes,
        "undecided": {p: sorted(a for a, e in actions.items() if e[p] == "UNDECIDED") for p in PREDICATES},
        "conflict": conflict,
        "gaps": gaps,
        "inherits_from": inherits,
        "reporting_breaches": breaches,
        "lean": {"elaborate": "regenerated", "cases": lean_cases, "agree": lean_cases,
                 "mismatches": []},
        "seconds": round(time.time() - started, 1),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true", help="merge the result into results.json")
    args = parser.parse_args(argv)
    result = run()
    print(json.dumps({k: v for k, v in result.items() if k != "actions"}, indent=1, ensure_ascii=False))
    if args.write:
        path = HERE / "results.json"
        results = json.loads(path.read_text())
        results["unspecified"] = result
        path.write_text(json.dumps(results, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
    return result


if __name__ == "__main__":
    main()
