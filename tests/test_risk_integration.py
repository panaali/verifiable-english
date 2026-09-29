"""Three-way checks of the risk spec's cell fixtures through the integrated route.

Python transports the raw record to Lean; Rust independently evaluates the
prepared cell. Rust's result is never used to admit the record.
"""
import json
import subprocess
from pathlib import Path

import pytest

from conformance.risk import Log, cell_env, condition, dec, estimate, gt, q, record
from ve.risk import run_case


ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean/.lake/build/bin/ve_risk_route"
RUST = ROOT / "rust/target/release/ve"


def _direct_lean(case):
    completed = subprocess.run([str(LEAN), "-"], input=json.dumps([case]),
                               text=True, capture_output=True, timeout=60)
    assert completed.returncode in (0, 1), completed.stderr
    return json.loads(completed.stdout)[0]


def _rust(case):
    completed = subprocess.run([str(RUST), "conformance"], input=json.dumps([case]),
                               text=True, capture_output=True, timeout=60)
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
