"""Three-way checks of the risk spec's cell fixtures through the integrated route.

Python transports the raw record to Lean; Rust independently evaluates the
prepared cell. Rust's result is never used to admit the record.
"""
import json
import subprocess
from pathlib import Path

import pytest

from tests import lean_routes

from conformance.risk import Log, cell_env, condition, dec, estimate, gt, q, record
from subprocesses import HANG_TIMEOUT
from ve.risk import run_case


ROOT = Path(__file__).resolve().parents[1]
LEAN = "ve_risk_route"  # its service mode, through tests/lean_routes.py
RUST = ROOT / "rust/target/release/ve"


def _direct_lean(case):
    completed = lean_routes.completed(LEAN, [case])
    assert completed.returncode in (0, 1), completed.stderr
    return json.loads(completed.stdout)[0]


def _rust(case):
    completed = subprocess.run([str(RUST), "conformance"], input=json.dumps([case]),
                               text=True, capture_output=True, timeout=HANG_TIMEOUT)
    assert completed.returncode == 0, completed.stderr
    return json.loads(completed.stdout)[0]


@pytest.mark.parametrize("fixture,peak,free,form,expected", [
    ("k1", ("6", "12"), ("8", "10"), "necessary", (True, False)),
    ("k2-sufficient", ("11", "12"), ("8", "10"), "sufficient", (True, True)),
    ("k2-necessary", ("6", "8"), ("8", "10"), "necessary", (False, False)),
])
def test_spec_cell_three_way(fixture, peak, free, form, expected):
    env = cell_env()
    source = {"id": fixture + "-policy", "kind": "risk-elaborate",
              "environment": env, "document": {"norms": []}}
    policy = run_case(source)
    assert policy == _direct_lean(source)
    assert policy["status"] == "ok", policy

    log = Log()
    log.add(1, "E1", "estimate", estimate("peak_memory", *peak, "profiler", "statistical"))
    log.add(2, "E2", "estimate", estimate("free_memory", *free, "monitor", "observation"))
    comparison = gt(q("peak_memory"), q("free_memory"))
    log.add(3, "C", "condition", condition("act", "server_outage", form, comparison))
    alternatives = [{"name": "act", "label": "acting"},
                    {"name": "nothing", "label": "doing nothing", "inaction": True}]
    quantities = [{"name": name, "label": name, "tag": "gb"}
                  for name in ("peak_memory", "free_memory")]
    decision = log.add(4, "DX", "decision", record(
        "x", "the_agent", "the agent", (policy["environment_id"], policy["document_hash"]),
        alternatives, quantities, log.cite("E1", "E2", "C")))
    raw = {"id": fixture, "kind": "risk-decision", "environment": env,
           "document": {"norms": []}, "decision": decision, "entries": log.entries[:-1]}
    via_python = run_case(raw)
    assert via_python == _direct_lean(raw)
    assert via_python["status"] == "ok", via_python
    lean_cell = (("act", "server_outage") in
                 {(row["alternative"], row["harm"]) for row in via_python["tables"]["might"]},
                 ("act", "server_outage") in
                 {(row["alternative"], row["harm"]) for row in via_python["tables"]["leads"]})

    prepared = {"id": fixture, "kind": "risk-cells",
                "ranges": {"peak_memory": {"tag": "gb", "lo": peak[0], "hi": peak[1]},
                           "free_memory": {"tag": "gb", "lo": free[0], "hi": free[1]}},
                "scales": {"gb": "1"},
                "record": {"alternatives": ["act", "nothing"],
                           "harms": ["server_outage"], "classes": {"server_outage": "serious"},
                           "always_possible": [], "unexamined": "possible",
                           "cells": [{"action": "act", "harm": "server_outage", form: comparison}]}}
    rust_cell = _rust(prepared)["tables"][0]
    assert lean_cell == (rust_cell["might"], rust_cell["leads"]) == expected


@pytest.mark.parametrize("sufficient,necessary,expected", [
    # Review A2: S and N are the same condition after normalisation (4.4 V8): 8 and 8.0 lower
    # to one grid value, so V8 does not build S ∧ ¬N and the record is valid in both.
    (["lt", dec("gb", "8"), q("peak_memory")], ["lt", dec("gb", "8.0"), q("peak_memory")], (True, False)),
    (["lt", ["add", "gb", dec("gb", "8"), ["scale", "gb", "0", q("free_memory")]], q("peak_memory")],
     ["lt", dec("gb", "8"), q("peak_memory")], (True, False)),
    # a different coefficient order is a different condition in Lean: S ∧ ¬N then shares peak
    (["lt", ["add", "gb", q("peak_memory"), q("free_memory")], dec("gb", "20")],
     ["lt", ["add", "gb", q("free_memory"), q("peak_memory")], dec("gb", "20")], "RiskConditionShared"),
])
def test_same_condition_after_normalisation_three_way(sufficient, necessary, expected):
    env = cell_env()
    policy = run_case({"id": "p", "kind": "risk-elaborate", "environment": env, "document": {"norms": []}})
    log = Log()
    log.add(1, "E1", "estimate", estimate("peak_memory", "6", "12", "profiler", "statistical"))
    log.add(2, "E2", "estimate", estimate("free_memory", "8", "10", "monitor", "observation"))
    log.add(3, "S", "condition", condition("act", "server_outage", "sufficient", sufficient))
    log.add(4, "N", "condition", condition("act", "server_outage", "necessary", necessary))
    alternatives = [{"name": "act", "label": "acting"},
                    {"name": "nothing", "label": "doing nothing", "inaction": True}]
    quantities = [{"name": name, "label": name, "tag": "gb"} for name in ("peak_memory", "free_memory")]
    decision = log.add(5, "DX", "decision", record(
        "x", "the_agent", "the agent", (policy["environment_id"], policy["document_hash"]),
        alternatives, quantities, log.cite("E1", "E2", "S", "N")))
    lean = run_case({"id": "v8", "kind": "risk-decision", "environment": env, "document": {"norms": []},
                     "decision": decision, "entries": log.entries[:-1]})
    prepared = {"id": "v8", "kind": "risk-cells",
                "ranges": {"peak_memory": {"tag": "gb", "lo": "6", "hi": "12"},
                           "free_memory": {"tag": "gb", "lo": "8", "hi": "10"}},
                "scales": {"gb": "1"},
                "record": {"alternatives": ["act", "nothing"], "harms": ["server_outage"],
                           "classes": {"server_outage": "serious"}, "always_possible": [],
                           "unexamined": "possible",
                           "cells": [{"action": "act", "harm": "server_outage",
                                      "sufficient": sufficient, "necessary": necessary}]}}
    completed = subprocess.run([str(RUST), "conformance"], input=json.dumps([prepared]),
                               text=True, capture_output=True, timeout=HANG_TIMEOUT)
    rust = json.loads(completed.stdout)[0]
    if isinstance(expected, str):
        assert lean["status"] == "error" and lean["error"].startswith(expected), lean
        assert rust["status"] == "error", rust
        assert f'{rust["error"]["code"]}: {rust["error"]["message"]}' == lean["error"]
        return
    assert lean["status"] == "ok", lean
    cell = ("act", "server_outage")
    lean_cell = (cell in {(r["alternative"], r["harm"]) for r in lean["tables"]["might"]},
                 cell in {(r["alternative"], r["harm"]) for r in lean["tables"]["leads"]})
    assert lean_cell == (rust["tables"][0]["might"], rust["tables"][0]["leads"]) == expected


def test_w2_admission_through_python_route_binds_regenerated_risk_leaf():
    env = cell_env()
    source = {"id": "policy", "kind": "risk-elaborate", "environment": env,
              "document": {"norms": []}}
    premise = next(row for row in run_case(source)["risk_premises"]
                   if row["label"] == "risk:certain_possible")
    document = {"units": [], "graph": {"root": "slot", "nodes": [
        {"name": "slot", "label": premise["label"], "ast": premise["ast"]}]}}
    case = {"id": "w2", "kind": "admission", "environment": env, "document": document}
    result = run_case(case)
    assert result == _direct_lean(case)
    assert result["status"] == "ok" and result["admitted"] is True
    assert result["report"]["assumptions"][0]["label"] == "risk:certain_possible"


def test_random_records_lean_and_rust_regenerate_the_same_cells():
    """Review C1 (Fable) / B8: Lean against Rust on random records, not hand-built cells only.

    Each record's conditions and statements become Rust's prepared sides (a necessary condition
    gives N, a sufficient one S, an exact one both; `leads` gives S = ⊤ and `cannot` N = ⊥, both
    marked as stated sides, and `might` the stated flag). Lean's regenerated `might`/`leads` tables, or its diagnostic, must equal Rust's.
    """
    import random
    from conformance.risk import statement
    rng = random.Random(4242)
    env = cell_env()
    policy = run_case({"id": "p", "kind": "risk-elaborate", "environment": env, "document": {"norms": []}})
    harms = [h for h, _ in env["risk"]["harm_classes"]]
    D = "dimensionless"

    def cmp(name):
        op = rng.choice(("lt", "le", "eq"))
        tree = [op, ["add", D, q(name), ["scale", D, str(rng.choice((1, -1, 2))), q("p")]] if op != "eq"
                else q(name), dec(D, str(rng.randrange(-2, 9)))]
        return ["not", tree] if rng.randrange(4) == 0 else tree

    cases, prepared = [], []
    for index in range(300):
        log = Log()
        ranges = {}
        for seq, name in enumerate(("a", "b"), start=1):
            lo = rng.randrange(0, 6)
            hi = lo + rng.randrange(0, 4)
            ranges[name] = {"tag": D, "lo": str(lo), "hi": str(hi)}
            log.add(seq, "E" + name, "estimate", estimate(name, str(lo), str(hi), "est", "assumption"))
        point = rng.randrange(0, 3)
        ranges["p"] = {"tag": D, "lo": str(point), "hi": str(point)}
        log.add(3, "Ep", "estimate", estimate("p", str(point), str(point), "est", "assumption"))
        sides = {}
        seq = 4
        for harm in rng.sample(harms, rng.randrange(1, 4)):
            action = rng.choice(("act", "nothing"))
            cell = sides.setdefault((action, harm), {"action": action, "harm": harm})
            if rng.randrange(3) == 0:
                stated = rng.choice(("leads", "cannot", "might"))
                log.add(seq, f"T{seq}", "statement", statement(action, harm, stated))
                if stated == "leads":
                    cell["sufficient"], cell["sufficient_stated"] = ["top"], True
                elif stated == "cannot":
                    cell["necessary"], cell["necessary_stated"] = ["bottom"], True
                else:
                    cell["stated_might"] = True
            else:
                form = rng.choice(("necessary", "sufficient", "exact"))
                tree = cmp(rng.choice(("a", "b")))
                if rng.randrange(2):
                    tree = [rng.choice(("and", "or")), tree, cmp("b" if "a" in json.dumps(tree) else "a")]
                log.add(seq, f"C{seq}", "condition", condition(action, harm, form, tree))
                if form in ("necessary", "exact"):
                    cell["necessary"] = tree
                if form in ("sufficient", "exact"):
                    cell["sufficient"] = tree
            seq += 1
        alternatives = [{"name": "act", "label": "acting"},
                        {"name": "nothing", "label": "doing nothing", "inaction": True}]
        quantities = [{"name": n, "label": n, "tag": D} for n in ("a", "b", "p")]
        dx = log.add(50, "DX", "decision", record(
            "x", "the_agent", "the agent", (policy["environment_id"], policy["document_hash"]),
            alternatives, quantities, log.cite(*[e["id"] for e in log.entries])))
        cases.append({"id": str(index), "kind": "risk-decision", "environment": env, "document": {"norms": []},
                      "decision": dx, "entries": log.entries[:-1]})
        prepared.append({"id": str(index), "kind": "risk-cells", "ranges": ranges, "scales": {},
                         "record": {"alternatives": ["act", "nothing"], "harms": harms,
                                    "classes": dict(env["risk"]["harm_classes"]), "always_possible": [],
                                    "unexamined": "possible", "cells": list(sides.values())}})
    lean = json.loads(lean_routes.completed(LEAN, cases).stdout)
    rust = json.loads(subprocess.run([str(RUST), "conformance"], input=json.dumps(prepared), text=True,
                                     capture_output=True, timeout=HANG_TIMEOUT).stdout)
    kinds = {"ok": 0, "error": 0}
    for case, l, r in zip(cases, lean, rust):
        kinds[l["status"]] += 1
        if l["status"] == "error":
            assert r["status"] == "error", (case["id"], l, r)
            # Lean adds the witness case of S ∧ ¬N to V8's text (4.3); Rust gives the diagnostic only
            text = l["error"].split(", case ")[0]
            assert f'{r["error"]["code"]}: {r["error"]["message"]}' == text, (case["id"], l, r)
            continue
        assert r["status"] == "ok", (case["id"], l, r)
        lean_cells = {(row["alternative"], row["harm"]): [True, False] for row in l["tables"]["might"]}
        for row in l["tables"]["leads"]:
            lean_cells.setdefault((row["alternative"], row["harm"]), [False, False])[1] = True
        rust_cells = {(c["action"], c["harm"]): [c["might"], c["leads"]] for c in r["tables"]
                      if c["might"] or c["leads"]}
        assert lean_cells == rust_cells, (case["id"], lean_cells, rust_cells)
    assert kinds["ok"] > 100 and kinds["error"] > 10, kinds
