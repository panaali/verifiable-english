"""Python's own search answers, recorded at the base of lean-first batch 15b (review B2).

Since batch 15b `find_countermodel` runs Rust's search under every authority, so a test that compares the
Rust binary's answer with `find_countermodel`'s compares Rust with itself. The tests that compared them now
compare the Rust binary with these answers, which Python's deleted search gave at the base (`record`, run
from a base checkout), and check every witness with Python's own countermodel check.

    python -I tests/b15b_search_oracle.py record tests/data/b15b-search-oracle.json
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
CLOSURE_SOURCES = [
    ('rtc[edge](@start, @end).\n', 'tc[edge](@start, @end).\n'),
    ('tc[edge](@start, @end).\n', 'false.\n'),
    ('tc[node a, b | (a edge b)](@start, @end).\n', 'false.\n'),
    ('tc[node a, b | (rtc[edge](a, b))](@start, @end).\n', 'false.\n'),
    ('true.\n', 'for every node a, (rtc[edge](a, a)).\n'),
    ('true.\n', 'for every node z, (rtc[node a, b | ((a edge b) and (not (b equals z)))](z, z)).\n'),
]
CLOSURE_BUDGETS = [(0, 1000, 1_000_000), (1, 1000, 1_000_000), (2, 1000, 1_000_000), (2, 0, 1_000_000),
                   (2, 1000, 2)]


def closure_search_cases():
    """The closure search cases of tests/test_rust_conformance.py (environment JSON, Rust case)."""
    from ve import Environment, parse
    from ve.ast import formula_to_data
    raw = json.loads((ROOT / "conformance/closure.json").read_text())[3]["environment"]
    raw["vocabulary"]["sorts"].pop("other")
    raw["vocabulary"]["predicates"]["unused"] = {"arguments": ["node", "node"], "description": "Unused."}
    env = Environment(raw)
    cases = []
    for left, right in CLOSURE_SOURCES:
        p, q = parse(env, left).formulas[0], parse(env, right).formulas[0]
        for size, models, work in CLOSURE_BUDGETS:
            cases.append({"environment": raw, "premises": [formula_to_data(env, p)],
                          "conclusion": formula_to_data(env, q), "max_domain_size": size,
                          "max_models": models, "max_evaluations": work})
    return raw, cases


def p0_search_cases():
    cases = json.loads((ROOT / "conformance/elaborated-document.json").read_text())
    return [case for case in cases if case["kind"] == "search" and "pending" not in case
            and case["expected"]["status"] == "ok"]


def record() -> dict:
    from conformance.three_way import python_verdict
    from ve import Environment
    from ve.ast import formula_from_data
    from ve.search import find_countermodel
    raw, cases = closure_search_cases()
    env = Environment(raw)
    closure = []
    for case in cases:
        found = find_countermodel(env, [formula_from_data(env, f) for f in case["premises"]],
                                  formula_from_data(env, case["conclusion"]),
                                  **{k: case[k] for k in ("max_domain_size", "max_models", "max_evaluations")})
        closure.append({"status": found.status, "models_checked": found.models_checked,
                        "evaluations": found.evaluations,
                        "model": None if found.model is None else found.model.to_dict()})
    return {"closure_search": closure,
            "p0_search_models": {case["id"]: python_verdict(case)["model"] for case in p0_search_cases()}}


def main() -> None:
    if len(sys.argv) != 3 or sys.argv[1] != "record":
        raise SystemExit(__doc__)
    sys.path.insert(0, str(Path.cwd()))
    Path(sys.argv[2]).write_text(json.dumps(record(), indent=1, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
