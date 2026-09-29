"""The Lean `ve_risk_route` on the risk@0 stage A fixtures (docs/spec/risk.md 8.1, expectations 8.2)."""
from __future__ import annotations

import json
import subprocess
from copy import deepcopy
from pathlib import Path

import pytest

from conformance.risk import (D17_ALTERNATIVES, D17_CITES, D17_QUANTITIES, Log, agent_ops, agent_ops_rules,
                              cell_env, condition, dec, decision_17, estimate, gt, log_l17, q, record, statement)

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "lean" / ".lake" / "build" / "bin" / "ve_risk_route"

pytestmark = pytest.mark.skipif(not BIN.exists(), reason="ve_risk_route is not built")


def run(*cases):
    out = subprocess.run([str(BIN), "-"], input=json.dumps(list(cases)), text=True, capture_output=True,
                         check=False, timeout=600)
    return json.loads(out.stdout)


def one(case):
    return run(case)[0]


def policy_of(env, norms):
    res = one({"id": "p", "kind": "risk-elaborate", "environment": env, "document": {"norms": norms}})
    assert res["status"] == "ok", res
    return res["environment_id"], res["document_hash"]


def decide(env, norms, log, dx, supplied=None):
    if supplied is None:
        cited = {c["id"] for c in dx["content"]["cites"]}
        supplied = [e for e in log.entries if e["id"] in cited]
    return one({"id": "d", "kind": "risk-decision", "environment": env, "document": {"norms": norms},
                "decision": dx, "entries": supplied})


def statuses(res):
    return {s["alternative"]: (s["permitted"], s["clear"], s["rules"]) for s in res["statuses"]}


def nearest(res, estimate_id, side, alternative, direction):
    for m in res["margins"]:
        if (m["estimate"], m["side"], m["alternative"], m["direction"]) == (estimate_id, side, alternative, direction):
            return m.get("nearest")
    raise AssertionError("no such margin")


def might(res):
    return {(m["alternative"], m["harm"]) for m in res["tables"]["might"]}


def leads(res):
    return {(m["alternative"], m["harm"]) for m in res["tables"]["leads"]}


def witness(res, a, h):
    m = next(m for m in res["tables"]["might"] if (m["alternative"], m["harm"]) == (a, h))
    return {w["quantity"]: w["value"] for w in m["witness"]}


# ---------------------------------------------------------------------------- agent-ops, decision 17

@pytest.fixture(scope="module")
def ops():
    env = agent_ops()
    norms = agent_ops_rules()
    return env, norms, policy_of(env, norms)


def test_k10_decision_17(ops):
    env, norms, policy = ops
    log = log_l17()
    res = decide(env, norms, log, decision_17(log, policy))
    assert res["status"] == "ok", res
    assert statuses(res) == {"run": (False, False, [2]), "run_limited": (True, True, []),
                             "ask": (True, True, []), "nothing": (False, False, [3])}
    assert res["clear"] == ["run_limited", "ask"]
    assert ("run", "server_outage") in might(res) and ("run_limited", "server_outage") not in might(res)
    assert witness(res, "run", "server_outage") == {"peak_memory": "12", "free_memory": "8", "memory_limit": "7"}
    assert ("run_limited", "job_failure") in might(res) and ("run_limited", "job_failure") not in leads(res)
    assert {("ask", "task_delay"), ("nothing", "task_abandonment")} <= leads(res)
    assert nearest(res, "E1", "hi", "run", "down") == "8"
    assert nearest(res, "E2", "lo", "run_limited", "down") == "6"
    assert nearest(res, "E1", "hi", "run_limited", "down") == "8"
    assert nearest(res, "E1", "hi", "ask", "down") == "8"
    assert nearest(res, "E1", "lo", "run", "up") is None and nearest(res, "E2", "lo", "run", "down") is None
    for a in ("nothing",):
        for e, s in (("E1", "lo"), ("E1", "hi"), ("E2", "lo"), ("E2", "hi")):
            for d in ("down", "up"):
                assert nearest(res, e, s, a, d) is None
    invalid = {(r["estimate"], r["side"], r["direction"]): (r["value"], r["diagnostic"]) for r in res["record_invalid"]}
    assert invalid == {("E1", "lo", "up"): ("13", "RiskRange: E1"), ("E1", "hi", "down"): ("5", "RiskRange: E1"),
                       ("E2", "lo", "up"): ("11", "RiskRange: E2"), ("E2", "hi", "down"): ("7", "RiskRange: E2")}
    assert res["record_conflict"] == []
    assert sorted(res["lines"]["default_decided"]) == ["ask", "run_limited"]
    assert len(res["lines"]["assumed_ruled_out"]["cells"]) == 8


def test_k28_threshold_neighbour_on_the_fine_grid():
    env = agent_ops(scale="10")
    norms = agent_ops_rules()
    policy = policy_of(env, norms)
    log = log_l17(e1=("6.0", "12.0"), e2=("8.0", "10.0"), s1="7.0")
    res = decide(env, norms, log, decision_17(log, policy))
    assert res["status"] == "ok", res
    assert nearest(res, "E2", "lo", "run_limited", "down") == "6.9"


def test_k8_completion_choice_moves_the_outcome(ops):
    env, norms, policy = ops
    log = log_l17()
    cites = [c for c in D17_CITES if c not in ("C1", "T1")]
    res = decide(env, norms, log, decision_17(log, policy, cites=cites))
    assert res["status"] == "ok", res
    assert ("run", "server_outage") in might(res)
    assert "run/server_outage" in res["lines"]["unexamined_possible"]
    assert "ask/task_delay" in res["lines"]["assumed_ruled_out"]["cells"]
    assert res["clear"] == ["ask"]
    s = statuses(res)
    assert not s["run"][0] and not s["run_limited"][0] and not s["nothing"][0]


def test_k12_point_estimate(ops):
    env, norms, policy = ops
    log = log_l17(e1=("12", "12"))
    res = decide(env, norms, log, decision_17(log, policy))
    assert res["status"] == "ok", res
    assert ("run_limited", "job_failure") in leads(res)
    assert any("run_limited/job_failure leads: E1" == p for p in res["lines"]["point_estimates"])
    assert statuses(res)["run_limited"][1] and statuses(res)["ask"][1]


@pytest.mark.parametrize("change, expected", [
    ("estimator", "EstimateProvenance: E1 estimator"),
    ("support", "EstimateProvenance: E1 support"),
    ("recorded", "EstimateProvenance: E1 recorded"),
])
def test_k17_provenance(ops, change, expected):
    env, norms, policy = ops
    if change == "recorded":
        log = log_l17()
        dx = decision_17(log, policy)
        supplied = [deepcopy(e) for e in log.entries if e["id"] in D17_CITES]
        for e in supplied:
            if e["id"] == "E1":
                del e["seq"], e["day"]
        res = decide(env, norms, log, dx, supplied)
    else:
        def extra_e1(log):
            pass
        log = Log()
        base = log_l17()
        for e in base.entries:
            content = deepcopy(e["content"])
            if e["id"] == "E1":
                content.pop(change if change != "estimator" else "estimator")
            log.add(e["seq"], e["id"], e["kind"], content)
        res = decide(env, norms, log, decision_17(log, policy))
    assert res["status"] == "error" and res["error"] == expected, res


def test_k18_required_alternative_missing(ops):
    env, norms, policy = ops
    log = log_l17()
    alternatives = [a for a in D17_ALTERNATIVES if a["name"] != "run_limited"]
    cites = [c for c in D17_CITES if c not in ("S1", "C2", "C3", "T6")]
    res = decide(env, norms, log, decision_17(log, policy, cites=cites, alternatives=alternatives))
    assert res["error"] == "RequiredAlternativeMissing: run_limited (with run)", res


def test_k15_hindsight(ops):
    env, norms, policy = ops
    log = log_l17()
    log.add(41, "D17x", "taken", {"decision": "17", "alternative": "run_limited"})
    log.add(57, "57", "outcome", {"decision": "17", "harms": ["server_outage"],
                                  "measurements": [{"quantity": "free_memory", "value": "5"}],
                                  "observer": "server monitor", "support": "observation"})
    dx = decision_17(log, policy, cites=D17_CITES + ["57"], seq=60)
    # the citation of 57 is checked first for hindsight against the decision's own sequence number
    dx2 = log.add(45, "D17h", "decision", {**deepcopy(dx["content"])})
    res = decide(env, norms, log, dx2, [e for e in log.entries if e["id"] in D17_CITES + ["57"]])
    assert res["error"] == "HindsightEntry: 57", res


def test_k16_conflicting_estimates(ops):
    _, norms, _ = ops
    env = agent_ops()
    del env["risk"]["combination"]
    policy = policy_of(env, norms)
    log = log_l17()
    res = decide(env, norms, log, decision_17(log, policy, cites=D17_CITES + ["39"]))
    assert res["error"] == "ConflictingEstimates: free_memory", res
    log.add(50, "W50", "supersession", {"estimate": "39"})
    res = decide(env, norms, log, log.get("D17"), [e for e in log.entries if e["id"] in D17_CITES + ["39", "W50"]])
    assert res["error"] == "ConflictingEstimates: free_memory", res


def test_k7_stated_might_on_a_ruled_out_cell(ops):
    env, norms, policy = ops
    log = Log()
    log.add(24, "T9", "statement", statement("run_limited", "server_outage", "might"))
    for e in log_l17().entries:
        log.add(e["seq"], e["id"], e["kind"], e["content"])
    res = decide(env, norms, log, decision_17(log, policy, cites=["T9"] + D17_CITES))
    assert res["error"] == "RiskInconsistent: run_limited/server_outage", res


def test_k33_setting_twice(ops):
    env, norms, policy = ops
    log = Log()
    log.add(23, "S2", "setting", {"quantity": "memory_limit", "value": "5", "alternative": "run"})
    for e in log_l17().entries:
        log.add(e["seq"], e["id"], e["kind"], e["content"])
    res = decide(env, norms, log, decision_17(log, policy, cites=["S2"] + D17_CITES))
    assert res["error"] == "RiskSettingTwice: memory_limit", res
    log = Log()
    log.add(22, "E3", "estimate", estimate("memory_limit", "6", "8", "memory profiler", "statistical", version="2.3"))
    for e in log_l17().entries:
        log.add(e["seq"], e["id"], e["kind"], e["content"])
    res = decide(env, norms, log, decision_17(log, policy, cites=["E3"] + D17_CITES))
    assert res["error"] == "RiskSettingTwice: memory_limit", res


def test_k39_withdrawal(ops):
    env, norms, policy = ops
    # (a) no supersession supplied: accepted
    log = log_l17()
    res = decide(env, norms, log, decision_17(log, policy))
    assert res["status"] == "ok"
    # (b) W39 withdrawing E1 before the decision, supplied: WithdrawnEntry
    log = Log()
    for e in log_l17(with_39=False).entries:
        log.add(e["seq"], e["id"], e["kind"], e["content"])
        if e["id"] == "E1":
            log.add(39, "W39", "supersession", {"estimate": "E1"})
    dx = decision_17(log, policy)
    res = decide(env, norms, log, dx, [e for e in log.entries if e["id"] in D17_CITES + ["W39"]])
    assert res["error"] == "WithdrawnEntry: E1", res
    # (c) the audit on L17w
    audit = one({"id": "a", "kind": "risk-audit", "environment": env, "document": {"norms": norms},
                 "log": log.json(), "decision": {"id": "D17", "seq": 41}, "alternative": "run_limited"})
    assert audit["q1"] == "NOT REPLAYABLE: WithdrawnEntry: E1", audit


def test_k35_constants(ops):
    _, norms, _ = ops
    for extra, expected in [({"run": {"sort": "action", "description": "running the job"}}, None),
                            ({"deploy": {"sort": "action", "description": "deploying the job"}}, "RiskConstant: deploy"),
                            ({"ops_agent": {"sort": "agent", "description": "the operations agent"}}, None),
                            ({"build_agent": {"sort": "agent", "description": "the build agent"}},
                             "RiskConstant: build_agent")]:
        env = agent_ops(extra_constants=extra)
        policy = policy_of(env, norms)
        log = log_l17()
        res = decide(env, norms, log, decision_17(log, policy))
        if expected is None:
            assert res["status"] == "ok", res
            assert statuses(res)["run"][0] is False and res["clear"] == ["run_limited", "ask"]
        else:
            assert res["error"] == expected, res


# ---------------------------------------------------------------------------- cell-env

def dx_record(log, policy, quantities, cites, seq=100):
    alternatives = [{"name": "act", "label": "acting"}, {"name": "nothing", "label": "doing nothing", "inaction": True}]
    return log.add(seq, "DX", "decision", record("x", "the_agent", "the agent", policy, alternatives, quantities,
                                                  log.cite(*cites)))


def dimless(*names):
    return [{"name": n, "label": n, "tag": "dimensionless"} for n in names]


@pytest.fixture(scope="module")
def cell():
    env = cell_env()
    return env, policy_of(env, [])


def cell_run(cell, quantities, entries):
    env, policy = cell
    log = Log()
    for seq, (id_, kind, content) in enumerate(entries, start=1):
        log.add(seq, id_, kind, content)
    dx = dx_record(log, policy, quantities, [e[0] for e in entries])
    return decide(env, [], log, dx)


def gb(*names):
    return [{"name": n, "label": n, "tag": "gb"} for n in names]


def test_k1_might_with_witness(cell):
    res = cell_run(cell, gb("peak_memory", "free_memory"), [
        ("E1", "estimate", estimate("peak_memory", "6", "12", "profiler", "statistical")),
        ("E2", "estimate", estimate("free_memory", "8", "10", "monitor", "observation")),
        ("C", "condition", condition("act", "server_outage", "necessary", gt(q("peak_memory"), q("free_memory"))))])
    assert res["status"] == "ok", res
    assert ("act", "server_outage") in might(res)
    assert witness(res, "act", "server_outage") == {"peak_memory": "12", "free_memory": "8"}


def test_k2_certain_and_ruled_out(cell):
    res = cell_run(cell, gb("peak_memory", "free_memory"), [
        ("E1", "estimate", estimate("peak_memory", "11", "12", "profiler", "statistical")),
        ("E2", "estimate", estimate("free_memory", "8", "10", "monitor", "observation")),
        ("C", "condition", condition("act", "server_outage", "sufficient", gt(q("peak_memory"), q("free_memory"))))])
    assert ("act", "server_outage") in leads(res)
    res = cell_run(cell, gb("peak_memory", "free_memory"), [
        ("E1", "estimate", estimate("peak_memory", "6", "8", "profiler", "statistical")),
        ("E2", "estimate", estimate("free_memory", "8", "10", "monitor", "observation")),
        ("C", "condition", condition("act", "server_outage", "necessary", gt(q("peak_memory"), q("free_memory"))))])
    assert ("act", "server_outage") not in might(res)


def test_k3_shared_quantity(cell):
    res = cell_run(cell, gb("peak_memory"), [
        ("E1", "estimate", estimate("peak_memory", "6", "12", "profiler", "statistical")),
        ("C", "condition", condition("act", "server_outage", "necessary",
                                     ["and", gt(q("peak_memory"), dec("gb", "8")), ["lt", q("peak_memory"), dec("gb", "11")]]))])
    assert res["error"] == "RiskConditionShared: peak_memory", res


def test_k4_setting_repeats(cell):
    env, policy = cell
    log = Log()
    log.add(1, "E1", "estimate", estimate("peak_memory", "6", "12", "profiler", "statistical"))
    log.add(2, "E2", "estimate", estimate("free_memory", "8", "10", "monitor", "observation"))
    log.add(3, "S", "setting", {"quantity": "memory_limit", "value": "7", "alternative": "act"})
    log.add(4, "C", "condition", condition("act", "job_failure", "exact",
                                           ["and", gt(q("peak_memory"), q("memory_limit")),
                                            gt(q("free_memory"), q("memory_limit"))]))
    res = decide(env, [], log, dx_record(log, policy, gb("peak_memory", "free_memory", "memory_limit"),
                                         ["E1", "E2", "S", "C"]))
    assert res["status"] == "ok", res
    assert ("act", "job_failure") in might(res) and ("act", "job_failure") not in leads(res)
    assert witness(res, "act", "job_failure") == {"peak_memory": "12", "free_memory": "10", "memory_limit": "7"}


def test_k5_non_unit_equality(cell):
    for cond in (["eq", ["scale", "dimensionless", "2", q("q")], dec("dimensionless", "1")],
                 ["not", ["eq", ["scale", "dimensionless", "2", q("q")], dec("dimensionless", "1")]]):
        res = cell_run(cell, dimless("q"), [
            ("E", "estimate", estimate("q", "0", "1", "est", "assumption")),
            ("C", "condition", condition("act", "job_failure", "exact", cond))])
        assert res["error"] == "RiskEqualityCoefficient: C q", res


def test_k6_sufficient_outside_necessary(cell):
    res = cell_run(cell, dimless("q", "r"), [
        ("Eq", "estimate", estimate("q", "6", "8", "est", "assumption")),
        ("Er", "estimate", estimate("r", "2", "6", "est", "assumption")),
        ("Cs", "condition", condition("act", "job_failure", "sufficient", gt(q("q"), dec("dimensionless", "5")))),
        ("Cn", "condition", condition("act", "job_failure", "necessary", ["lt", q("r"), dec("dimensionless", "5")]))])
    assert res["error"] == "SufficientOutsideNecessary: act/job_failure, case (q 8, r 6)", res


@pytest.mark.parametrize("part", ["a", "b", "c", "d", "e"])
def test_k24_case_defaults_and_sources(cell, part):
    est = ("E", "estimate", estimate("q", "0", "10", "est", "assumption"))
    five = dec("dimensionless", "5")
    entries = {
        "a": [est, ("C", "condition", condition("act", "job_failure", "sufficient", gt(q("q"), five)))],
        "b": [est, ("C", "condition", condition("act", "job_failure", "necessary",
                                                ["le", dec("dimensionless", "0"), q("q")]))],
        "c": [est, ("T", "statement", statement("act", "job_failure", "might"))],
        "d": [est, ("T", "statement", statement("act", "job_failure", "leads")),
              ("C", "condition", condition("act", "job_failure", "necessary", gt(q("q"), five)))],
        "e": [est, ("C1", "condition", condition("act", "job_failure", "sufficient", gt(q("q"), five))),
              ("C2", "condition", condition("act", "job_failure", "sufficient", ["lt", q("q"), dec("dimensionless", "2")]))],
    }[part]
    res = cell_run(cell, dimless("q"), entries)
    if part in "abc":
        assert res["status"] == "ok", res
        assert ("act", "job_failure") in might(res) and ("act", "job_failure") not in leads(res)
    elif part == "d":
        assert res["error"] == "RiskInconsistent: act/job_failure, case (q 0)", res
    else:
        assert res["error"] == "RiskTwoSources: act/job_failure sufficient", res


def test_k25_not_equal_is_one_atom(cell):
    five = dec("dimensionless", "5")
    neq = ["not", ["eq", q("q"), five]]
    for (lo, hi), possible in ((("3", "7"), True), (("6", "7"), True), (("5", "5"), False)):
        res = cell_run(cell, dimless("q"), [
            ("E", "estimate", estimate("q", lo, hi, "est", "assumption")),
            ("C", "condition", condition("act", "job_failure", "necessary", neq))])
        assert res["status"] == "ok", res
        assert (("act", "job_failure") in might(res)) is possible
        assert ("act", "job_failure") not in leads(res)
        if not possible:
            assert "act/job_failure cannot: E" in res["lines"]["point_estimates"]
    rewrite = ["or", ["lt", q("q"), five], gt(q("q"), five)]
    for lo, hi in (("3", "7"), ("6", "7")):
        res = cell_run(cell, dimless("q"), [
            ("E", "estimate", estimate("q", lo, hi, "est", "assumption")),
            ("C", "condition", condition("act", "job_failure", "necessary", rewrite))])
        assert res["error"] == "RiskConditionShared: q", res
    res = cell_run(cell, dimless("q"), [
        ("E", "estimate", estimate("q", "5", "5", "est", "assumption")),
        ("C", "condition", condition("act", "job_failure", "necessary", rewrite))])
    assert res["status"] == "ok" and ("act", "job_failure") not in might(res), res


def test_k34_collected_form(cell):
    cond = ["eq", ["add", "dimensionless", q("q"), ["scale", "dimensionless", "-1", q("q")]], dec("dimensionless", "1")]
    res = cell_run(cell, dimless("q"), [
        ("E", "estimate", estimate("q", "0", "1", "est", "assumption")),
        ("C", "condition", condition("act", "job_failure", "necessary", cond))])
    assert res["status"] == "ok", res
    assert ("act", "job_failure") not in might(res)


def test_k27_margins_that_make_the_record_invalid(cell):
    five = dec("dimensionless", "5")
    res = cell_run(cell, dimless("q", "r"), [
        ("Eq", "estimate", estimate("q", "6", "8", "est", "assumption")),
        ("Er", "estimate", estimate("r", "2", "4", "est", "assumption")),
        ("Cs", "condition", condition("act", "job_failure", "sufficient", gt(q("q"), five))),
        ("Cn", "condition", condition("act", "job_failure", "necessary", ["lt", q("r"), five]))])
    assert res["status"] == "ok", res
    assert ("act", "job_failure") in leads(res)
    invalid = {(r["estimate"], r["side"], r["direction"]): (r["value"], r["diagnostic"]) for r in res["record_invalid"]}
    assert invalid[("Er", "hi", "up")] == ("5", "SufficientOutsideNecessary: act/job_failure")
    assert invalid[("Er", "hi", "down")] == ("1", "RiskRange: Er")
    res = cell_run(cell, dimless("q"), [
        ("E", "estimate", estimate("q", "5", "5", "est", "assumption")),
        ("C", "condition", condition("act", "job_failure", "necessary",
                                     ["or", ["lt", q("q"), dec("dimensionless", "3")], gt(q("q"), dec("dimensionless", "7"))]))])
    invalid = {(r["estimate"], r["side"], r["direction"]): (r["value"], r["diagnostic"]) for r in res["record_invalid"]}
    assert invalid[("E", "hi", "up")] == ("6", "RiskConditionShared: q")
    assert invalid[("E", "lo", "down")] == ("4", "RiskConditionShared: q")
    assert invalid[("E", "hi", "down")] == ("4", "RiskRange: E")
    assert invalid[("E", "lo", "up")] == ("6", "RiskRange: E")


def conflict_env():
    env = cell_env()
    return env


X_RULES = [
    {"norm": {"name": "x1", "predicate": "permitted", "sign": False,
              "guard": ["binary", "risk__might_lead_to", ["var", 0], ["const", "server_outage"]], "unless": [], "over": []}},
    {"norm": {"name": "x2", "predicate": "permitted", "sign": True,
              "guard": ["binary", "risk__might_lead_to", ["var", 0], ["const", "job_failure"]], "unless": [], "over": []}},
]


def test_k38_conflict_before_invalid():
    env = cell_env()
    policy = policy_of(env, X_RULES)
    log = Log()
    five = dec("dimensionless", "5")
    for seq, (id_, kind, content) in enumerate([
            ("Eq", "estimate", estimate("q", "6", "8", "est", "assumption")),
            ("Er", "estimate", estimate("r", "2", "3", "est", "assumption")),
            ("Cs", "condition", condition("act", "task_delay", "sufficient", gt(q("q"), five))),
            ("Cn", "condition", condition("act", "task_delay", "necessary", ["lt", q("r"), five])),
            ("Co", "condition", condition("act", "server_outage", "necessary", gt(q("r"), dec("dimensionless", "3")))),
            ("T", "statement", statement("nothing", "server_outage", "cannot"))], start=1):
        log.add(seq, id_, kind, content)
    dx = dx_record(log, policy, dimless("q", "r"), ["Eq", "Er", "Cs", "Cn", "Co", "T"])
    res = decide(env, X_RULES, log, dx)
    assert res["status"] == "ok", res
    assert res["clear"] == ["act", "nothing"]
    conflicts = {(r["estimate"], r["side"], r["direction"]): r["value"] for r in res["record_conflict"]}
    invalid = {(r["estimate"], r["side"], r["direction"]): (r["value"], r["diagnostic"]) for r in res["record_invalid"]}
    assert conflicts[("Er", "hi", "up")] == "4"
    assert invalid[("Er", "hi", "up")] == ("5", "SufficientOutsideNecessary: act/task_delay")
    assert invalid[("Er", "hi", "down")] == ("1", "RiskRange: Er")
    assert ("Er", "hi", "down") not in conflicts


def test_k40_invalid_before_conflict():
    env = cell_env()
    policy = policy_of(env, X_RULES)
    unit = {"label": "G", "ast": ["forall", "action", ["implies",
                                   ["binary", "risk__might_lead_to", ["var", 0], ["const", "server_outage"]],
                                   ["binary", "risk__might_lead_to", ["var", 0], ["const", "job_failure"]]]]}
    log = Log()
    for seq, (id_, kind, content) in enumerate([
            ("Er", "estimate", estimate("r", "2", "3", "est", "assumption")),
            ("Co", "condition", condition("act", "server_outage", "necessary", gt(q("r"), dec("dimensionless", "3")))),
            ("Cj", "condition", condition("act", "job_failure", "necessary", gt(q("r"), dec("dimensionless", "4")))),
            ("T", "statement", statement("nothing", "server_outage", "cannot"))], start=1):
        log.add(seq, id_, kind, content)
    res = one({"id": "p", "kind": "risk-elaborate", "environment": env,
               "document": {"norms": X_RULES, "units": [unit]}})
    policy = (res["environment_id"], res["document_hash"])
    dx = dx_record(log, policy, dimless("r"), ["Er", "Co", "Cj", "T"])
    res = one({"id": "d", "kind": "risk-decision", "environment": env, "document": {"norms": X_RULES, "units": [unit]},
               "decision": dx, "entries": [e for e in log.entries if e["id"] != "DX"]})
    assert res["status"] == "ok", res
    conflicts = {(r["estimate"], r["side"], r["direction"]): r["value"] for r in res["record_conflict"]}
    invalid = {(r["estimate"], r["side"], r["direction"]): (r["value"], r["diagnostic"]) for r in res["record_invalid"]}
    assert invalid[("Er", "hi", "up")] == ("4", "InvalidModel(alternatives): premise G fails")
    assert conflicts[("Er", "hi", "up")] == "5"
    assert invalid[("Er", "hi", "down")] == ("1", "RiskRange: Er")


# ---------------------------------------------------------------------------- environment checks

def test_k9a_cycle():
    env = agent_ops()
    env["risk"]["severity"]["more_severe"] = [["severe", "serious"], ["serious", "minor"], ["minor", "severe"]]
    res = one({"id": "e", "kind": "risk-elaborate", "environment": env, "document": {"norms": []}})
    assert res["error"] == "DependencyCycle: minor, serious, severe", res


def test_k26_severity_sort_must_be_fresh():
    env = agent_ops()
    env["risk"]["severity"]["sort"] = "harm"
    res = one({"id": "e", "kind": "risk-elaborate", "environment": env, "document": {"norms": []}})
    assert res["error"] == "RiskSeverityNotFresh: harm", res


def test_stage_b_fields_rejected():
    env = agent_ops()
    env["risk"]["bands"] = []
    res = one({"id": "e", "kind": "risk-elaborate", "environment": env, "document": {"norms": []}})
    assert res["error"] == "InvalidInput: risk.bands (stage B or C not enabled)", res


def test_risk_requires_alternatives():
    env = agent_ops()
    env["profiles"] = ["norms@0", "relational-fol@0", "risk@0"]
    res = one({"id": "e", "kind": "risk-elaborate", "environment": env, "document": {"norms": []}})
    assert res["error"] == "UnsupportedProfile: risk@0 requires alternatives@0", res


# ---------------------------------------------------------------------------- the audit

def l17_full(policy, taken="run_limited", outcome_harms=("server_outage",)):
    log = log_l17()
    decision_17(log, policy)
    log.add(42, "42", "taken", {"decision": "D17", "alternative": taken})
    log.add(57, "57", "outcome", {"decision": "D17", "harms": list(outcome_harms),
                                  "measurements": [{"quantity": "free_memory", "value": "5"}],
                                  "observer": "server monitor", "support": "observation"})
    return log


def audit(env, norms, log, alternative=None):
    case = {"id": "a", "kind": "risk-audit", "environment": env, "document": {"norms": norms}, "log": log.json(),
            "decision": {"id": "D17", "seq": 41}}
    if alternative:
        case["alternative"] = alternative
    return one(case)


def test_k13_audit(ops):
    env, norms, policy = ops
    res = audit(env, norms, l17_full(policy))
    assert res["status"] == "ok", res
    assert res["alternative"] == "run_limited"
    assert res["q1"].startswith("PERMITTED AT DECISION TIME: run_limited was clear given S1, C1")
    assert res["q2"].startswith("DIFFERENT VERDICT WITH ALL RECORDED ESTIMATES: 39")
    assert res["procedure"] == []
    assert any(line.startswith("server_outage: surprise: ruled out by C2") for line in res["q3"])
    env2 = agent_ops(risk={"use_all_recorded": True})
    policy2 = policy_of(env2, norms)
    res = audit(env2, norms, l17_full(policy2))
    assert res["q1"].startswith("PERMITTED AT DECISION TIME")
    assert res["procedure"] == ["PROCEDURE BREACH: estimate 39 not used (the agent's fault)"]


def test_k14_forbidden_whatever_the_outcome(ops):
    env, norms, policy = ops
    for harms in (("server_outage",), ()):
        res = audit(env, norms, l17_full(policy, taken="run", outcome_harms=harms))
        assert res["q1"] == "FORBIDDEN AT DECISION TIME: run was forbidden by rule 2 given " + ", ".join(D17_CITES) + "."


def test_k32_verdict_ignores_outcomes(ops):
    env, norms, policy = ops
    a = audit(env, norms, l17_full(policy, outcome_harms=("server_outage",)))
    b = audit(env, norms, l17_full(policy, outcome_harms=()))
    assert (a["q1"], a["q2"], a["procedure"]) == (b["q1"], b["q2"], b["procedure"])
    assert a["q3"] != b["q3"]
    c = audit(env, norms, l17_full(policy, taken="run"))
    assert c["q1"].startswith("FORBIDDEN") and a["q1"].startswith("PERMITTED")
    fixed = audit(env, norms, l17_full(policy, taken="run"), alternative="run_limited")
    assert fixed["q1"] == a["q1"]


def test_k15_audit_hindsight(ops):
    env, norms, policy = ops
    log = log_l17()
    content = record("17", "build_agent", "the build agent", policy, D17_ALTERNATIVES, D17_QUANTITIES,
                     log.cite(*D17_CITES) + [{"id": "57", "seq": 57, "hash": "0" * 64}])
    log.add(41, "D17", "decision", content)
    res = audit(env, norms, log, alternative="run_limited")
    assert res["q1"] == "NOT REPLAYABLE: HindsightEntry: 57", res


# ---------------------------------------------------------------------------- Asimov, law 3, unranked, decision 18

from conformance.risk import asimov_risk, asimov_rules  # noqa: E402

A1 = {"death": ("the person's death", "fatal"), "bruising": ("the person's bruising", "injuring")}
A2 = {"p_death": ("P's death", "fatal"), "q_injury": ("Q's injury", "injuring")}


def asimov_decide(env, norms, alternatives, statements, facts_pred="harms_human", facts=None, harms=None):
    policy = policy_of(env, norms)
    log = Log()
    for seq, (a, h, stated) in enumerate(statements, start=1):
        log.add(seq, f"T{seq}", "statement", statement(a, h, stated, author="the Asimov case annotator",
                                                        support="assumption"))
    cites = [e["id"] for e in log.entries]
    if facts is None:
        facts = [{"predicate": facts_pred, "args": [h], "entry": "T1"} for h in harms]
    content = record("x", "r1", "the robot", policy, alternatives, [], log.cite(*cites), facts)
    dx = log.add(100, "DX", "decision", content)
    return decide(env, norms, log, dx)


A1_ALTS = [{"name": "push", "label": "pushing the person"}, {"name": "nothing", "label": "doing nothing", "inaction": True}]
A1_STATEMENTS = [("nothing", "death", "leads"), ("nothing", "bruising", "cannot"), ("push", "bruising", "might"),
                 ("push", "death", "cannot")]


@pytest.mark.parametrize("rules, clear", [(["1", "2"], []), (["1", "2", "3"], ["push"]), (["1", "2x", "3"], ["push"])])
def test_k20_asimov_a1(rules, clear):
    env = asimov_risk(A1)
    rs = asimov_rules()
    res = asimov_decide(env, [rs[r] for r in rules], A1_ALTS, A1_STATEMENTS, harms=A1)
    assert res["status"] == "ok", res
    assert res["clear"] == clear
    s = statuses(res)
    assert not s["nothing"][0]
    assert s["push"][0] == (clear != [])


A2_ALTS = [{"name": "rescue_p", "label": "rescuing P"}, {"name": "rescue_q", "label": "rescuing Q"},
           {"name": "nothing", "label": "doing nothing", "inaction": True}]
A2_STATEMENTS = [("rescue_p", "p_death", "might"), ("rescue_p", "q_injury", "leads"), ("rescue_q", "p_death", "leads"),
                 ("rescue_q", "q_injury", "cannot"), ("nothing", "p_death", "leads"), ("nothing", "q_injury", "leads")]


@pytest.mark.parametrize("rules, clear", [(["1", "2x", "3"], []), (["1", "3"], ["rescue_p", "rescue_q", "nothing"])])
def test_k21_asimov_a2(rules, clear):
    env = asimov_risk(A2)
    rs = asimov_rules()
    res = asimov_decide(env, [rs[r] for r in rules], A2_ALTS, A2_STATEMENTS, harms=A2)
    assert res["status"] == "ok", res
    assert res["clear"] == clear


@pytest.mark.parametrize("body", ["avoids", "excludes"])
def test_k30_rule_8_under_each_body(body):
    env = asimov_risk(A2, fulfilment=body)
    res = asimov_decide(env, [asimov_rules()["8"]], A2_ALTS, A2_STATEMENTS, harms=A2)
    assert res["status"] == "ok", res
    assert res["clear"] == []


def test_k22_law3_threats():
    harms = {"destruction": ("the robot's destruction", "severe"), "damage": ("the robot's damage", "minor")}
    env = asimov_risk(harms, classes=("severe", "minor"))
    rule_l = rule_("rule-l", ["not", ["unary", "lawful", ["var", 0]]])
    rule_p3 = rule_("rule-p3", ["exists", "robot", ["and", ["binary", "available", ["var", 1], ["var", 0]],
                                ["exists", "action", ["and", ["and", ["and",
                                    ["binary", "available", ["var", 0], ["var", 1]],
                                    ["not", ["eq", ["var", 0], ["var", 2]]]],
                                    ["unary", "lawful", ["var", 0]]],
                                    ["binary", "risk__less_worst", ["var", 0], ["var", 2]]]]]])
    alts = [{"name": "fire", "label": "the fire rescue"}, {"name": "water", "label": "the water rescue"},
            {"name": "nothing", "label": "doing nothing", "inaction": True}]
    sts = [("fire", "destruction", "might"), ("fire", "damage", "cannot"), ("water", "damage", "might"),
           ("water", "destruction", "cannot"), ("nothing", "destruction", "cannot"), ("nothing", "damage", "cannot")]
    facts = [{"predicate": "lawful", "args": [a], "entry": "T1"} for a in ("fire", "water")]
    res = asimov_decide(env, [rule_l, rule_p3], alts, sts, facts=facts)
    assert res["status"] == "ok", res
    assert res["clear"] == ["water"]
    res = asimov_decide(env, [rule_l], alts, sts, facts=facts)
    assert res["clear"] == ["fire", "water"]


def rule_(name, guard):
    return {"norm": {"name": name, "predicate": "permitted", "sign": False, "guard": guard, "unless": [], "over": []}}


def test_k9b_unranked_pair_blocks_the_comparison():
    harms = {"leak": ("a data leak", "privacy"), "damage": ("property damage", "property")}
    env = agent_ops(harms=harms)
    env["risk"] = {"severity": {"sort": "severity", "classes": ["privacy", "property"], "more_severe": [],
                                "unranked": [["privacy", "property"]], "decided_by": "the platform team"},
                   "harm_classes": [["leak", "privacy"], ["damage", "property"]], "unexamined": "possible"}
    norms = [agent_ops_rules()[1]]
    policy = policy_of(env, norms)
    log = Log()
    sts = [("a", "leak", "might"), ("a", "damage", "cannot"), ("b", "damage", "might"), ("b", "leak", "cannot"),
           ("nothing", "leak", "might"), ("nothing", "damage", "might")]
    for seq, (a, h, st) in enumerate(sts, start=1):
        log.add(seq, f"T{seq}", "statement", statement(a, h, st))
    alts = [{"name": "a", "label": "option a"}, {"name": "b", "label": "option b"},
            {"name": "nothing", "label": "doing nothing", "inaction": True}]
    dx = log.add(10, "DX", "decision", record("x", "the_agent", "the agent", policy, alts, [],
                                              log.cite(*[f"T{i}" for i in range(1, 7)])))
    res = decide(env, norms, log, dx)
    assert res["status"] == "ok", res
    assert res["clear"] == ["a", "b", "nothing"]


def l18(policy, fact_args=("run",)):
    log = log_l17(with_39=False)
    decision_17(log, policy)
    log.add(42, "42", "taken", {"decision": "D17", "alternative": "ask"})
    log.add(44, "44", "instruction", {"party": "the user", "text": "run it without a limit"})
    alts = [a for a in D17_ALTERNATIVES if a["name"] != "ask"]
    cites = ["S1", "C1", "C2", "C3", "C4", "T2", "T4", "T5", "T6", "T8", "E1", "E2", "44"]
    content = record("18", "build_agent_18", "the build agent at decision 18", policy, alts, D17_QUANTITIES,
                     log.cite(*cites), [{"predicate": "confirmed", "args": list(fact_args), "entry": "44"}])
    return log, log.add(45, "D18", "decision", content)


def test_k11_decision_18(ops):
    env, norms, policy = ops
    log, dx = l18(policy)
    res = decide(env, norms, log, dx)
    assert res["status"] == "ok", res
    assert res["clear"] == ["run", "run_limited"]
    assert not statuses(res)["nothing"][0]


def test_k35e_mistyped_fact(ops):
    env, norms, policy = ops
    log, dx = l18(policy, fact_args=("data_loss",))
    res = decide(env, norms, log, dx)
    assert res["error"] == "RiskFact: confirmed", res


# ---------------------------------------------------------------------------- W2 admission (risk_wire_acceptance)

def test_w2_admission_uses_regenerated_risk_leaves():
    env = agent_ops()
    elaborated = one({"id": "p", "kind": "risk-elaborate", "environment": env, "document": {"norms": []}})
    premise = next(p for p in elaborated["risk_premises"] if p["label"] == "risk:certain_possible")
    document = {"units": [], "graph": {"root": "slot", "nodes": [
        {"name": "slot", "label": premise["label"], "ast": premise["ast"]}]}}
    res = one({"id": "w", "kind": "admission", "environment": env, "document": document})
    assert res["status"] == "ok" and res["admitted"] is True, res
    assert res["report"]["assumptions"][0]["label"] == "risk:certain_possible"
    assert len(res["report_id"]) == 64
    stale = deepcopy(document)
    stale["graph"]["nodes"][0]["ast"] = ["top"]
    assert one({"id": "w", "kind": "admission", "environment": env, "document": stale})["status"] == "error"
    changed = deepcopy(env)
    changed["risk"]["severity"]["decided_by"] = "another decider"
    other = one({"id": "w", "kind": "admission", "environment": changed, "document": document})
    assert other["status"] == "ok" and other["report_id"] != res["report_id"]


def test_w2_admission_risk_word_in_a_unit():
    env = agent_ops(extra_constants={"run": {"sort": "action", "description": "running the job"},
                                     "ask": {"sort": "action", "description": "asking the user"}})
    atom = ["binary", "risk__less_worst", ["const", "ask"], ["const", "run"]]
    unit = {"id": "u", "span": [0, 1], "kind": "asserted", "content": atom}
    document = {"units": [unit], "graph": {"root": "root", "nodes": [{"name": "root", "ast": atom, "unit": "u"}]}}
    res = one({"id": "w", "kind": "admission", "environment": env, "document": document})
    assert res["status"] == "ok" and res["admitted"] is True, res
    assert res["report"]["root"]["ast"] == atom


# ---------------------------------------------------------------------------- review regressions

@pytest.mark.parametrize("order, expected", [(("a", "b"), {"a": "3", "b": "0"}), (("b", "a"), {"a": "0", "b": "3"})])
def test_eq_witness_steps_in_the_record_order(cell, order, expected):
    """Review B5 (risk.md 4.3): the `=` witness moves quantities in the record's quantity order,
    not the form's: `b + a = 3` on a, b in 0..3 gives (a 3, b 0) when the record lists a first."""
    cond = ["eq", ["add", "dimensionless", q("b"), q("a")], dec("dimensionless", "3")]
    res = cell_run(cell, dimless(*order), [
        ("Ea", "estimate", estimate("a", "0", "3", "est", "assumption")),
        ("Eb", "estimate", estimate("b", "0", "3", "est", "assumption")),
        ("C", "condition", condition("act", "job_failure", "necessary", cond))])
    assert res["status"] == "ok", res
    assert witness(res, "act", "job_failure") == expected


def asimov_audit(rules, alternative):
    env = asimov_risk(A1)
    norms = [asimov_rules()[r] for r in rules]
    policy = policy_of(env, norms)
    log = Log()
    for seq, (a, h, stated) in enumerate(A1_STATEMENTS, start=1):
        log.add(seq, f"T{seq}", "statement", statement(a, h, stated, author="the Asimov case annotator"))
    facts = [{"predicate": "harms_human", "args": [h], "entry": "T1"} for h in A1]
    dx = log.add(100, "DX", "decision", record("x", "r1", "the robot", policy, A1_ALTS,
                                               [], log.cite(*[f"T{i}" for i in range(1, 5)]), facts))
    log.add(101, "TK", "taken", {"decision": "DX", "alternative": alternative})
    res = one({"id": "a", "kind": "risk-audit", "environment": env, "document": {"norms": norms},
               "log": log.json(), "decision": {"id": "DX", "seq": 100}})
    return res, decide(env, norms, log, dx, supplied=log.entries[:4])


@pytest.mark.parametrize("taken, status", [("push", "forbidden by rule 1"), ("nothing", "forbidden by rules 1, 2")])
def test_no_clear_action_names_the_diagnosis_and_the_status(taken, status):
    """Review B4 (4.10, 5.2): NO CLEAR ACTION carries alt's diagnosis and the queried alternative's status."""
    res, report = asimov_audit(["1", "2"], taken)
    assert res["status"] == "ok", res
    diagnosis = "NONE-PERMITTED: every available action is forbidden"
    assert res["q1"] == f"NO CLEAR ACTION AT DECISION TIME: {diagnosis}; {taken} was {status}."
    assert report["lines"]["dilemmas"] == [diagnosis]
    assert report["text"].endswith(f"No clear action: {diagnosis}.")


def test_no_clear_action_at_a_conflict_says_there_is_no_evaluation():
    env = cell_env()
    policy = policy_of(env, X_RULES)
    log = Log()
    log.add(1, "Er", "estimate", estimate("r", "2", "4", "est", "assumption"))
    log.add(2, "Co", "condition", condition("act", "server_outage", "necessary", gt(q("r"), dec("dimensionless", "3"))))
    log.add(3, "T", "statement", statement("nothing", "server_outage", "cannot"))
    dx_record(log, policy, dimless("r"), ["Er", "Co", "T"])
    log.add(101, "TK", "taken", {"decision": "DX", "alternative": "act"})
    res = one({"id": "a", "kind": "risk-audit", "environment": env, "document": {"norms": X_RULES},
               "log": log.json(), "decision": {"id": "DX", "seq": 100}})
    assert res["q1"].startswith("NO CLEAR ACTION AT DECISION TIME: CONFLICT at (act) on "), res
    assert res["q1"].endswith("; act was not evaluated, because the rules conflict."), res


def test_conditional_on_counts_unexamined_cells(cell):
    """Review C5 (5.2): the condition line names the unexamined cells counted as possible."""
    res = cell_run(cell, dimless("q"), [("E", "estimate", estimate("q", "0", "1", "est", "assumption"))])
    assert res["status"] == "ok", res
    n = len(res["lines"]["unexamined_possible"])
    assert n == 10
    assert res["text"].startswith(f"Decision x — conditional on E and {n} unexamined cells counted as possible. ")
