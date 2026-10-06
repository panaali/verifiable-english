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
from conformance.norm_defaults_three_way import conflict_case, gap_cases, status_cases  # noqa: E402
from conformance import frozen_norm_defaults as nd  # noqa: E402
from ve import norm_defaults_route as route  # noqa: E402
from ve.environment import Environment  # noqa: E402

PREDICATES = (check.PERMISSION, check.OBLIGATION)
# The completed outcome columns of results.json, per predicate.
COLUMNS = {check.PERMISSION: ("deny", "allow"), check.OBLIGATION: ("need not", "must")}
CONFLICT_ACTION = "a10"
# A situation where each predicate's gap is reached: a27 is NOT-COVERED and no reporting rule covers it.
GAP_ACTION = "a27"


def status_text(status):
    if status.status == "SETTLED":
        return "SETTLED " + ("yes" if status.value else "no")
    return status.status


def _documents(action, inventory, record):
    """The document and situation of one record, flagged (the case's environment)
    and flag-free (the Lean copy)."""
    rules = check.policy().rules
    out = {}
    for name in ("unspecified", "unspecified.lean"):
        env = check.environment(action=action, data=check.read_json(f"environment.{name}.json"))
        document = nd.UnspecifiedDocument(env, rules)
        situation = check.record_model(document.situation_environment(), (*inventory, *record))
        out[name] = (document, situation)
    return out


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
    actions, changes, lean_cases, expected = {}, [], [], []
    conflict = gaps = None
    for action in complete:
        docs = _documents(action, inventory, records[action])
        document, situation = docs["unspecified"]
        lean_document, lean_situation = docs["unspecified.lean"]
        statuses = {s.predicate: s for s in document.statuses(situation)}
        cases = status_cases(lean_document, lean_situation)
        flag_free = {case["predicate"]: answer for case, answer in cases}
        if flag_free != {p: status_text(s) for p, s in statuses.items()}:
            raise AssertionError(f"{action}: the flag-free environment changes a status")
        for case, answer in cases:
            lean_cases.append({**case, "id": f"status:{action}:{case['predicate']}"})
            expected.append(answer)
        report = nd.check_conflict(document, model=situation.to_dict())
        actions[action] = {p: status_text(statuses[p]) for p in PREDICATES}
        actions[action]["conflict"] = report.status if report.status == "CONFLICT" else "none"
        if report.status == "CONFLICT":
            if action != CONFLICT_ACTION:
                raise AssertionError(f"unexpected conflict at {action}")
            numbers = check.numbers(document.author.rules)
            filled = document.with_filling(situation, {k: frozenset(tuple(r) for r in v)
                                                       for k, v in report.filling.items()})
            selected = document.filled.selected_rules(report.target, filled, (action,))
            lean_report, case = conflict_case(lean_document, lean_situation.to_dict())
            lean_cases.append({**case, "id": f"conflict:{action}"})
            expected.append(lean_report.status)
            conflict = {"action": action, "target": report.target, "kind": report.kind,
                        "rules": sorted(numbers[r.name] for r in selected)}
        if action == GAP_ACTION:
            lines = nd.report(document, model=situation.to_dict(), predicates=PREDICATES)
            gaps = {line.predicate: {"lines": list(line.lines()), "witness": action} for line in lines}
            for case, answer in gap_cases(lean_document, lean_situation.to_dict()):
                lean_cases.append({**case, "id": f"gaps:{case['predicate']}"})
                expected.append(answer)
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
    # Lean regenerates `fill U` from the same source; Python's regeneration must equal it byte for byte.
    route.elaborate(_documents(GAP_ACTION, inventory, records[GAP_ACTION])["unspecified.lean"][0])
    rows = route.run_cases(lean_cases, timeout=1800)
    mismatches = []
    for case, answer, row in zip(lean_cases, expected, rows):
        got = row.get("point_status", row.get("verdict", row.get("gaps"))) if row.get("status") == "ok" \
            else row.get("error")
        if got != answer:
            mismatches.append({"id": case["id"], "lean": got, "python": answer})
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
        "inherits_from": {p: list(nd.UnspecifiedDocument(Environment(raw), check.policy().rules).inherits_from(p))
                          for p in PREDICATES},
        "reporting_breaches": breaches,
        "lean": {"elaborate": "regenerated", "cases": len(lean_cases), "agree": len(lean_cases) - len(mismatches),
                 "mismatches": mismatches},
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
