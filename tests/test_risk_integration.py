"""Risk spec cell fixtures through the Python relay and direct Lean route."""
import json

import pytest

from tests import lean_routes

from conformance.risk import Log, cell_env, condition, dec, estimate, gt, q, record
from ve.risk import run_case
from ve.admission import admit_document
from ve.environment import Environment


LEAN = "ve_risk_route"  # its service mode, through tests/lean_routes.py


def _direct_lean(case):
    completed = lean_routes.completed(LEAN, [case])
    assert completed.returncode in (0, 1), completed.stderr
    return json.loads(completed.stdout)[0]


@pytest.mark.parametrize("fixture,peak,free,form,expected", [
    ("k1", ("6", "12"), ("8", "10"), "necessary", (True, False)),
    ("k2-sufficient", ("11", "12"), ("8", "10"), "sufficient", (True, True)),
    ("k2-necessary", ("6", "8"), ("8", "10"), "necessary", (False, False)),
])
def test_spec_cell_relay_and_lean(fixture, peak, free, form, expected):
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

    assert lean_cell == expected


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
def test_same_condition_after_normalisation_in_lean(sufficient, necessary, expected):
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
    if isinstance(expected, str):
        assert lean["status"] == "error" and lean["error"].startswith(expected), lean
        return
    assert lean["status"] == "ok", lean
    cell = ("act", "server_outage")
    lean_cell = (cell in {(r["alternative"], r["harm"]) for r in lean["tables"]["might"]},
                 cell in {(r["alternative"], r["harm"]) for r in lean["tables"]["leads"]})
    assert lean_cell == expected


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


def test_risk_admission_calls_risk_owner(monkeypatch):
    env = cell_env()
    source = run_case({"id": "policy", "kind": "risk-elaborate", "environment": env,
                       "document": {"norms": []}})
    premise = next(row for row in source["risk_premises"]
                   if row["label"] == "risk:certain_possible")
    document = {"units": [], "graph": {"root": "slot", "nodes": [
        {"name": "slot", "label": premise["label"], "ast": premise["ast"]}]}}
    accepted = Environment(env)
    from ve.backends import relay
    original_decide = relay.decide
    routed = []
    def record_owner(mode, cases, **kwargs):
        if cases[0]["kind"] == "admission":
            routed.append(mode)
        return original_decide(mode, cases, **kwargs)
    monkeypatch.setattr(relay, "decide", record_owner)
    result = admit_document(accepted, document)
    assert result["admitted"] is True
    assert result["conditional_on"] == run_case({"id": "direct", "kind": "admission",
                                                    "environment": env, "document": document})["conditional_on"]
    assert routed == ["risk"]
