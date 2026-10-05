"""Every diagnostic of risk.md 6 from the Lean route on a hand-written input (docs/spec/risk.md 8.3).

One case per row of the diagnostics table, and per alternative of a row, each on a minimal input
with its exact expected text (or its exact prefix where the text carries a witness case or a
variable part). The English-layer row (the rejected wordings of 2.3) is not a route diagnostic.
`unranked_severities` is a warning: it is asserted in the `unranked_severities` output of
`risk-elaborate`, on an environment that is accepted.

Every case goes to the route in one batch (after one batch that computes the policy bindings the
records cite).
"""
from __future__ import annotations

import json
import subprocess
from copy import deepcopy
from pathlib import Path

import pytest

from conformance.risk import (D17_ALTERNATIVES, D17_CITES, D17_QUANTITIES, Log, agent_ops, agent_ops_rules,
                              cell_env, condition, dec, decision_17, estimate, gt, log_l17, q, record, rule,
                              statement)
from subprocesses import HANG_TIMEOUT

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "lean" / ".lake" / "build" / "bin" / "ve_risk_route"

pytestmark = pytest.mark.skipif(not BIN.exists(), reason="ve_risk_route is not built")


def run(cases):
    out = subprocess.run([str(BIN), "-"], input=json.dumps(cases), text=True, capture_output=True,
                         check=False, timeout=HANG_TIMEOUT)
    assert out.returncode in (0, 1), out.stderr
    rows = json.loads(out.stdout)
    assert len(rows) == len(cases)
    return rows


# ---------------------------------------------------------------------------- inputs

def with_risk(env, **fields):
    env = deepcopy(env)
    env["risk"].update(fields)
    return env


def with_severity(env, **fields):
    env = deepcopy(env)
    env["risk"]["severity"].update(fields)
    return env


HARMS_33 = {f"h{i:02d}": (f"harm {i}", "minor") for i in range(33)}

UNIT_G = {"label": "G", "ast": ["forall", "action", ["implies",
                                ["binary", "risk__might_lead_to", ["var", 0], ["const", "server_outage"]],
                                ["binary", "risk__might_lead_to", ["var", 0], ["const", "job_failure"]]]]}


def balanced_and(atoms):
    if len(atoms) == 1:
        return atoms[0]
    mid = len(atoms) // 2
    return ["and", balanced_and(atoms[:mid]), balanced_and(atoms[mid:])]


# The policies the records bind: (environment, document).
POLICIES = {
    "ops": (agent_ops(), {"norms": agent_ops_rules()}),
    "ops-no-combination": ({**agent_ops(), "risk": {k: v for k, v in agent_ops()["risk"].items()
                                                    if k != "combination"}}, {"norms": agent_ops_rules()}),
    "ops-deploy": (agent_ops(extra_constants={"deploy": {"sort": "action", "description": "deploying the job"}}),
                   {"norms": agent_ops_rules()}),
    "cell": (cell_env(), {"norms": []}),
    "cell-hull": (with_risk(cell_env(), combination="hull"), {"norms": []}),
    "cell-intersection": (with_risk(cell_env(), combination="intersection"), {"norms": []}),
    "cell-G": (cell_env(), {"norms": [], "units": [UNIT_G]}),
    "cell-33": (cell_env(harms=HARMS_33), {"norms": []}),
}


def elaborate(env, document):
    return {"kind": "risk-elaborate", "environment": env, "document": document}


def env_case(env, norms=()):
    return elaborate(env, {"norms": list(norms)})


def copy_log(log, replace=None, before=()):
    """A copy of `log` with contents replaced by id, and extra entries added before it (rehashed)."""
    out = Log()
    for seq, id_, kind, content in before:
        out.add(seq, id_, kind, content)
    for e in log.entries:
        out.add(e["seq"], e["id"], e["kind"], deepcopy((replace or {}).get(e["id"], e["content"])))
    return out


def decision_case(P, name, dx, supplied):
    env, document = P[name]["source"]
    return {"kind": "risk-decision", "environment": env, "document": document, "decision": dx, "entries": supplied}


def cited(log, dx):
    ids = {c["id"] for c in dx["content"]["cites"]}
    return [deepcopy(e) for e in log.entries if e["id"] in ids]


def d17(P, name="ops", log=None, supplied=None, **kw):
    log = log_l17() if log is None else log
    dx = decision_17(log, P[name]["policy"], **kw)
    return decision_case(P, name, dx, cited(log, dx) if supplied is None else supplied)


ACT = [{"name": "act", "label": "acting"}, {"name": "nothing", "label": "doing nothing", "inaction": True}]


def dimless(*names):
    return [{"name": n, "label": n, "tag": "dimensionless"} for n in names]


def gb(*names):
    return [{"name": n, "label": n, "tag": "gb"} for n in names]


def cell(P, quantities, entries, name="cell", alternatives=None, facts=(), chooser="the_agent", policy=None):
    """A record of `cell-env` (chooser `the_agent`, alternatives act and nothing) citing every entry."""
    log = Log()
    for seq, (id_, kind, content) in enumerate(entries, start=1):
        log.add(seq, id_, kind, content)
    content = record("x", chooser, "the agent", policy or P[name]["policy"], alternatives or ACT, quantities,
                     log.cite(*[e[0] for e in entries]), facts)
    dx = log.add(1000, "DX", "decision", content)
    return decision_case(P, name, dx, [e for e in log.entries if e["id"] != "DX"])


def est(id_, quantity, lo, hi, estimator="est", support="assumption"):
    return (id_, "estimate", estimate(quantity, lo, hi, estimator, support))


FIVE = dec("dimensionless", "5")


# ---------------------------------------------------------------------------- the cases

CASES = []


def case(name, expected, check="error", marks=()):
    def register(build):
        CASES.append(pytest.param(name, build, check, expected, id=name, marks=marks))
        return build
    return register


# -- environment declarations (4.1), in the order of 6

@case("UnsupportedProfile", "UnsupportedProfile: risk@0 requires alternatives@0")
def _(P):
    env = agent_ops()
    env["profiles"] = ["norms@0", "relational-fol@0", "risk@0"]
    return env_case(env)


@case("InvalidInput-risk-unknown-field", "InvalidInput: risk.zeta")
def _(P):
    return env_case(with_risk(agent_ops(), zeta=1))


@case("InvalidInput-risk-missing-field", "InvalidInput: risk.unexamined")
def _(P):
    env = agent_ops()
    del env["risk"]["unexamined"]
    return env_case(env)


@case("InvalidInput-risk-malformed-field", "InvalidInput: risk.combination")
def _(P):
    return env_case(with_risk(agent_ops(), combination="max"))


@case("InvalidInput-risk-stage-B", "InvalidInput: risk.bands (stage B or C not enabled)")
def _(P):
    return env_case(with_risk(agent_ops(), bands=[]))


@case("RiskOutcomes", "RiskOutcomes: risk@0 requires outcomes signed")
def _(P):
    env = agent_ops()
    env["alternatives"]["outcomes"] = {"complete_by": "the build agent"}
    return env_case(env)


@case("RiskSeverityNotFresh", "RiskSeverityNotFresh: harm")
def _(P):
    return env_case(with_severity(agent_ops(), sort="harm"))


@case("RiskReserved-prefix", "RiskReserved: risk__extra")
def _(P):
    env = agent_ops()
    env["vocabulary"]["predicates"]["risk__extra"] = {"arguments": ["action"], "description": "extra"}
    return env_case(env)


@case("RiskReserved-class-name", "RiskReserved: minor")
def _(P):
    return env_case(agent_ops(extra_constants={"minor": {"sort": "harm", "description": "a minor thing"}}))


@case("DuplicateDeclaration-risk-class", "DuplicateDeclaration: risk class serious")
def _(P):
    return env_case(with_severity(agent_ops(), classes=["severe", "serious", "minor", "serious"]))


@case("ResourceLimit-risk-classes-none", "ResourceLimit: risk classes")
def _(P):
    return env_case(with_severity(agent_ops(), classes=[]))


@case("ResourceLimit-risk-classes-17", "ResourceLimit: risk classes")
def _(P):
    return env_case(with_severity(agent_ops(), classes=["severe", "serious", "minor"] + [f"c{i}" for i in range(14)]))


@case("UnknownSymbol-risk.severity", "UnknownSymbol: risk.severity tiny")
def _(P):
    return env_case(with_severity(agent_ops(), more_severe=[["severe", "serious"], ["serious", "tiny"]]))


@case("UnknownSymbol-risk.harm_classes-harm", "UnknownSymbol: risk.harm_classes flood")
def _(P):
    env = agent_ops()
    env["risk"]["harm_classes"].append(["flood", "minor"])
    return env_case(env)


@case("UnknownSymbol-risk.harm_classes-class", "UnknownSymbol: risk.harm_classes grave")
def _(P):
    env = agent_ops()
    env["risk"]["harm_classes"][1] = ["server_outage", "grave"]
    return env_case(env)


@case("UnknownSymbol-risk.always_possible", "UnknownSymbol: risk.always_possible grave")
def _(P):
    return env_case(with_risk(agent_ops(), always_possible=["severe", "grave"]))


@case("UnknownSymbol-risk.required_alternatives", "UnknownSymbol: risk.required_alternatives fly")
def _(P):
    return env_case(with_risk(agent_ops(), required_alternatives=[{"when": "run", "require": ["ask", "fly"]}]))


@case("UnknownSymbol-risk.quantity_kinds", "UnknownSymbol: risk.quantity_kinds tb")
def _(P):
    return env_case(with_risk(agent_ops(), quantity_kinds={"peak_memory": "tb"}, required_estimators=[]))


@case("UnknownSymbol-risk.required_estimators", "UnknownSymbol: risk.required_estimators latency")
def _(P):
    return env_case(with_risk(agent_ops(), required_estimators=[{"quantity_kind": "latency", "estimators": ["probe"]}]))


@case("DependencyCycle", "DependencyCycle: minor, serious, severe")
def _(P):
    return env_case(with_severity(agent_ops(), more_severe=[["severe", "serious"], ["serious", "minor"],
                                                             ["minor", "severe"]]))


@case("RiskUnrankedAgainstOrder", "RiskUnrankedAgainstOrder: minor, severe")
def _(P):
    return env_case(with_severity(agent_ops(), unranked=[["minor", "severe"]]))


@case("unranked_severities-warning", [["serious", "minor"]], check="unranked")
def _(P):
    return env_case(with_severity(agent_ops(), more_severe=[["severe", "serious"], ["severe", "minor"]]))


@case("unranked_severities-declared-pair-is-no-warning", [], check="unranked")
def _(P):
    return env_case(with_severity(agent_ops(), more_severe=[["severe", "serious"], ["severe", "minor"]],
                                  unranked=[["serious", "minor"]]))


@case("HarmUnclassified", "HarmUnclassified: server_outage")
def _(P):
    env = agent_ops()
    env["risk"]["harm_classes"] = [p for p in env["risk"]["harm_classes"] if p[0] != "server_outage"]
    return env_case(env)


@case("HarmTwoClasses", "HarmTwoClasses: data_loss")
def _(P):
    env = agent_ops()
    env["risk"]["harm_classes"].insert(1, ["data_loss", "minor"])
    return env_case(env)


@case("FulfilmentSort-excludes", "FulfilmentSort: required")
def _(P):
    env = agent_ops()
    env["alternatives"]["fulfilments"] = [{"obligation": "required", "body": "excludes"}]
    return env_case(env)


@case("ResourceLimit-risk-inlining", "ResourceLimit: risk inlining of rule big")
def _(P):
    atoms = [["binary", "risk__less_worst", ["var", 0], ["var", 0]]] * 1024
    return env_case(cell_env(), [rule("big", "permitted", False, balanced_and(atoms))])


# -- records: admission (4.4 A1 to A3)

@case("InvalidInput-risk-decision-entry-field", "InvalidInput: risk-decision.seq")
def _(P):
    c = d17(P)
    c["decision"]["seq"] = "41"
    return c


@case("InvalidInput-risk-decision-record-field", "InvalidInput: risk-decision.format")
def _(P):
    log = log_l17()
    dx = decision_17(log, P["ops"]["policy"])
    content = {**deepcopy(dx["content"]), "format": "ve-risk-decision@1"}
    log.entries.pop()
    dx = log.add(41, "D17", "decision", content)
    return decision_case(P, "ops", dx, cited(log, dx))


@case("InvalidInput-risk-decision-supplied-entries", "InvalidInput: risk-decision.entries")
def _(P):
    return {**d17(P), "entries": {}}


@case("EstimateProvenance-recorded", "EstimateProvenance: E1 recorded")
def _(P):
    c = d17(P)
    for e in c["entries"]:
        if e["id"] == "E1":
            del e["seq"], e["day"]
    return c


@case("AlteredEntry-decision-entry", "AlteredEntry: D17")
def _(P):
    c = d17(P)
    c["decision"]["hash"] = "f" * 64
    return c


@case("RiskBinding", "RiskBinding: policy")
def _(P):
    log = log_l17()
    dx = decision_17(log, (P["ops"]["policy"][0], "0" * 64))
    return decision_case(P, "ops", dx, cited(log, dx))


@case("ResourceLimit-risk-alternatives", "ResourceLimit: risk alternatives")
def _(P):
    alternatives = [{"name": f"a{i}", "label": f"option {i}"} for i in range(16)] + [ACT[1]]
    return cell(P, [], [], alternatives=alternatives)


@case("ResourceLimit-risk-harms", "ResourceLimit: risk harms")
def _(P):
    return cell(P, [], [], name="cell-33")


@case("ResourceLimit-risk-estimates-and-settings", "ResourceLimit: risk estimates and settings")
def _(P):
    return cell(P, dimless("q"), [est(f"E{i}", "q", "0", "1") for i in range(65)])


@case("ResourceLimit-risk-conditions-and-statements", "ResourceLimit: risk conditions and statements")
def _(P):
    return cell(P, [], [(f"T{i}", "statement", statement("act", "job_failure", "might")) for i in range(129)])


@case("ResourceLimit-risk-condition-nodes", "ResourceLimit: risk condition nodes")
def _(P):
    # 4,096 normalised atoms of 2 nodes under 4,095 conjunctions: 12,287 > MAX_NODES (9), within depth 64
    atoms = [["lt", q("q"), dec("dimensionless", str(i))] for i in range(4096)]
    return cell(P, dimless("q"), [est("E", "q", "0", "1"),
                                  ("C", "condition", condition("act", "job_failure", "necessary",
                                                               balanced_and(atoms)))])


@case("HindsightEntry", "HindsightEntry: 57")
def _(P):
    log = log_l17()
    content = record("17", "build_agent", "the build agent", P["ops"]["policy"], D17_ALTERNATIVES, D17_QUANTITIES,
                     log.cite(*D17_CITES) + [{"id": "57", "seq": 57, "hash": "0" * 64}])
    dx = log.add(41, "D17", "decision", content)
    return decision_case(P, "ops", dx, cited(log, dx))


@case("MissingEntry", "MissingEntry: E1")
def _(P):
    c = d17(P)
    c["entries"] = [e for e in c["entries"] if e["id"] != "E1"]
    return c


@case("AlteredEntry-cited-entry", "AlteredEntry: E1")
def _(P):
    c = d17(P)
    for e in c["entries"]:
        if e["id"] == "E1":
            e["content"]["lo"] = "7"
    return c


@case("WithdrawnEntry", "WithdrawnEntry: E1")
def _(P):
    log = Log()
    for e in log_l17(with_39=False).entries:
        log.add(e["seq"], e["id"], e["kind"], e["content"])
        if e["id"] == "E1":
            log.add(39, "W39", "supersession", {"estimate": "E1"})
    dx = decision_17(log, P["ops"]["policy"])
    return decision_case(P, "ops", dx, [e for e in log.entries if e["id"] in D17_CITES + ["W39"]])


@case("InvalidInput-risk-decision-facts", "InvalidInput: risk-decision.facts")
def _(P):
    # A3: a fact must cite an instruction or statement entry that the record also cites
    return cell(P, dimless("q"), [est("E", "q", "0", "1")],
                facts=[{"predicate": "confirmed", "args": ["act"], "entry": "E"}])


# -- records: validation (4.4 V1 to V11)

@case("InvalidModel-no-inaction", "InvalidModel(alternatives): the_agent has no inaction")
def _(P):
    return cell(P, [], [], alternatives=[{"name": "act", "label": "acting"}, {"name": "idle", "label": "idling"}])


@case("InvalidModel-two-inactions", "InvalidModel(alternatives): the_agent has two inactions: act, nothing")
def _(P):
    return cell(P, [], [], alternatives=[{"name": "act", "label": "acting", "inaction": True}, ACT[1]])


@case("UnknownHarm", "UnknownHarm: flood")
def _(P):
    return cell(P, [], [("T", "statement", statement("act", "flood", "might"))])


@case("UnknownSymbol-alternative", "UnknownSymbol: alternative fly")
def _(P):
    return cell(P, [], [("T", "statement", statement("fly", "job_failure", "might"))])


@case("UnknownSymbol-quantity", "UnknownSymbol: quantity zz")
def _(P):
    return cell(P, dimless("q"), [est("E", "q", "0", "1"),
                                  ("C", "condition", condition("act", "job_failure", "necessary", gt(q("zz"), FIVE)))])


@case("UnknownSymbol-kind-alternative", "UnknownSymbol: kind fly")
def _(P):
    return d17(P, alternatives=D17_ALTERNATIVES + [{"name": "fly", "label": "flying", "kind": "fly"}])


@case("UnknownSymbol-kind-quantity", "UnknownSymbol: kind latency")
def _(P):
    return cell(P, [{"name": "q", "label": "q", "tag": "dimensionless", "kind": "latency"}], [])


@case("UnknownSymbol-unit", "UnknownSymbol: unit tb")
def _(P):
    return cell(P, [{"name": "q", "label": "q", "tag": "tb"}], [])


@case("RiskConstant-class-name", "RiskConstant: severe")
def _(P):
    return cell(P, [], [], alternatives=[{"name": "severe", "label": "the severe option"}, ACT[1]])


@case("RiskConstant-record-local-names", "RiskConstant: act")
def _(P):
    return cell(P, [], [], chooser="act")


@case("RiskConstant-uninterpreted-action-constant", "RiskConstant: deploy")
def _(P):
    return d17(P, name="ops-deploy")


@case("RiskFact-regulated-predicate", "RiskFact: permitted")
def _(P):
    return cell(P, [], [("T", "statement", statement("act", "job_failure", "might"))],
                facts=[{"predicate": "permitted", "args": ["act"], "entry": "T"}])


@case("RiskFact-generated-predicate", "RiskFact: risk__might_lead_to")
def _(P):
    return cell(P, [], [("T", "statement", statement("act", "job_failure", "might"))],
                facts=[{"predicate": "risk__might_lead_to", "args": ["act", "job_failure"], "entry": "T"}])


@case("RiskFact-mistyped-argument", "RiskFact: confirmed")
def _(P):
    return cell(P, [], [("T", "statement", statement("act", "job_failure", "might"))],
                facts=[{"predicate": "confirmed", "args": ["data_loss"], "entry": "T"}])


@case("RequiredAlternativeMissing", "RequiredAlternativeMissing: run_limited (with run)")
def _(P):
    alternatives = [a for a in D17_ALTERNATIVES if a["name"] != "run_limited"]
    return d17(P, cites=[c for c in D17_CITES if c not in ("S1", "C2", "C3", "T6")], alternatives=alternatives)


@case("UnitMismatch", "UnitMismatch(dimensionless,gb)")
def _(P):
    return cell(P, gb("peak_memory"), [
        est("E", "peak_memory", "6", "12"),
        ("C", "condition", condition("act", "server_outage", "necessary", gt(q("peak_memory"), FIVE)))])


@case("UnitPrecision", "UnitPrecision(gb, scale=1)")
def _(P):
    return cell(P, gb("peak_memory"), [est("E", "peak_memory", "6.5", "12")])


@case("RiskRange", "RiskRange: E")
def _(P):
    return cell(P, dimless("q"), [est("E", "q", "5", "3")])


@case("EstimateProvenance-estimator", "EstimateProvenance: E estimator")
def _(P):
    return cell(P, dimless("q"), [est("E", "q", "0", "1", estimator=None)])


@case("EstimateProvenance-support", "EstimateProvenance: E support")
def _(P):
    return cell(P, dimless("q"), [est("E", "q", "0", "1", support=None)])


@case("EstimatorNotAllowed", "EstimatorNotAllowed: E1 the scheduler")
def _(P):
    log = copy_log(log_l17(), {"E1": estimate("peak_memory", "6", "12", "the scheduler", "statistical")})
    return d17(P, log=log)


@case("RiskSettingTwice-two-settings", "RiskSettingTwice: memory_limit")
def _(P):
    log = copy_log(log_l17(), before=[(23, "S2", "setting", {"quantity": "memory_limit", "value": "5",
                                                            "alternative": "run"})])
    return d17(P, log=log, cites=["S2"] + D17_CITES)


@case("RiskSettingTwice-setting-and-estimate", "RiskSettingTwice: memory_limit")
def _(P):
    log = copy_log(log_l17(), before=[(22, "E3", "estimate", estimate("memory_limit", "6", "8", "memory profiler",
                                                                      "statistical"))])
    return d17(P, log=log, cites=["E3"] + D17_CITES)


@case("RiskSettingScope", "RiskSettingScope: S act")
def _(P):
    return cell(P, dimless("r"), [("S", "setting", {"quantity": "r", "value": "3", "alternative": "nothing"}),
                                  ("C", "condition", condition("act", "job_failure", "necessary",
                                                               gt(q("r"), dec("dimensionless", "1"))))])


@case("ConflictingEstimates", "ConflictingEstimates: free_memory")
def _(P):
    return d17(P, name="ops-no-combination", cites=D17_CITES + ["39"])


@case("RiskInconsistent-estimates-do-not-intersect", "RiskInconsistent: q estimates do not intersect")
def _(P):
    return cell(P, dimless("q"), [est("E1", "q", "0", "2"), est("E2", "q", "5", "7")], name="cell-intersection")


@case("RiskUnestimated", "RiskUnestimated: q")
def _(P):
    return cell(P, dimless("q"), [("C", "condition", condition("act", "job_failure", "necessary", gt(q("q"), FIVE)))])


@case("RiskTwoSources-sufficient", "RiskTwoSources: act/job_failure sufficient")
def _(P):
    return cell(P, dimless("q"), [
        est("E", "q", "0", "10"),
        ("C1", "condition", condition("act", "job_failure", "sufficient", gt(q("q"), FIVE))),
        ("C2", "condition", condition("act", "job_failure", "sufficient", ["lt", q("q"), dec("dimensionless", "2")]))])


@case("RiskTwoSources-necessary", "RiskTwoSources: act/job_failure necessary")
def _(P):
    return cell(P, dimless("q"), [
        est("E", "q", "0", "10"),
        ("C1", "condition", condition("act", "job_failure", "necessary", gt(q("q"), FIVE))),
        ("C2", "condition", condition("act", "job_failure", "exact", ["lt", q("q"), dec("dimensionless", "2")]))])


@case("RiskStatementForm", "RiskStatementForm: probably")
def _(P):
    return cell(P, [], [("T", "statement", statement("act", "job_failure", "probably"))])


@case("RiskConditionShared-condition", "RiskConditionShared: q")
def _(P):
    return cell(P, dimless("q"), [
        est("E", "q", "6", "12"),
        ("C", "condition", condition("act", "server_outage", "necessary",
                                     ["and", gt(q("q"), dec("dimensionless", "8")),
                                      ["lt", q("q"), dec("dimensionless", "11")]]))])


@case("RiskConditionShared-sufficient-and-not-necessary", "RiskConditionShared: q")
def _(P):
    # each condition is separable; `S ∧ ¬N` shares the non-point q (4.4 V8)
    return cell(P, dimless("q"), [
        est("E", "q", "0", "10"),
        ("Cs", "condition", condition("act", "job_failure", "sufficient", gt(q("q"), FIVE))),
        ("Cn", "condition", condition("act", "job_failure", "necessary", gt(q("q"), dec("dimensionless", "3"))))])


@case("RiskEqualityCoefficient", "RiskEqualityCoefficient: C q")
def _(P):
    return cell(P, dimless("q"), [
        est("E", "q", "0", "1"),
        ("C", "condition", condition("act", "job_failure", "exact",
                                     ["eq", ["scale", "dimensionless", "2", q("q")], dec("dimensionless", "1")]))])


@case("SufficientOutsideNecessary", "SufficientOutsideNecessary: act/job_failure, case (q 8, r 6)")
def _(P):
    return cell(P, dimless("q", "r"), [
        est("Eq", "q", "6", "8"), est("Er", "r", "2", "6"),
        ("Cs", "condition", condition("act", "job_failure", "sufficient", gt(q("q"), FIVE))),
        ("Cn", "condition", condition("act", "job_failure", "necessary", ["lt", q("r"), FIVE]))])


@case("RiskInconsistent-stated-cell", "RiskInconsistent: act/job_failure, case (q 0)")
def _(P):
    return cell(P, dimless("q"), [
        est("E", "q", "0", "10"),
        ("T", "statement", statement("act", "job_failure", "leads")),
        ("C", "condition", condition("act", "job_failure", "necessary", gt(q("q"), FIVE)))])


@case("RiskInconsistent-stated-might", "RiskInconsistent: act/job_failure")
def _(P):
    return cell(P, dimless("q"), [
        est("E", "q", "0", "3"),
        ("C", "condition", condition("act", "job_failure", "necessary", gt(q("q"), FIVE))),
        ("T", "statement", statement("act", "job_failure", "might"))])


@case("InvalidModel-premise-fails", "InvalidModel(alternatives): premise G fails")
def _(P):
    return cell(P, dimless("r"), [
        est("Er", "r", "2", "5"),
        ("Co", "condition", condition("act", "server_outage", "necessary", gt(q("r"), dec("dimensionless", "3")))),
        ("Tj", "statement", statement("act", "job_failure", "cannot")),
        ("Tn", "statement", statement("nothing", "server_outage", "cannot"))], name="cell-G")


# -- the margin-candidate limit (4.9), on the admitted and valid record

@case("ResourceLimit-risk-margin-candidates", "ResourceLimit: risk margin candidates")
def _(P):
    # 50 estimates of q combined by hull: 6 candidates each (w − 1, w, w + 1 at both endpoints), 300 > 256
    return cell(P, dimless("q"), [est(f"E{i}", "q", str(10 * i), str(10 * i + 5)) for i in range(50)],
                name="cell-hull")


# -- the log of an audit (4.10)

def audit_case(P, log, decision=("D17", 41), alternative="run_limited"):
    env, document = P["ops"]["source"]
    return {"kind": "risk-audit", "environment": env, "document": document, "log": log,
            "decision": {"id": decision[0], "seq": decision[1]}, "alternative": alternative}


@case("InvalidInput-risk-log-format", "InvalidInput: risk-log.format")
def _(P):
    return audit_case(P, {"format": "ve-risk-log@1", "entries": []})


@case("InvalidInput-risk-log-entry-field", "InvalidInput: risk-log.seq")
def _(P):
    log = log_l17()
    decision_17(log, P["ops"]["policy"])
    raw = log.json()
    raw["entries"][0]["seq"] = "25"
    return audit_case(P, raw)


@case("NOT-REPLAYABLE-HindsightEntry", "NOT REPLAYABLE: HindsightEntry: 57", check="q1")
def _(P):
    log = log_l17()
    content = record("17", "build_agent", "the build agent", P["ops"]["policy"], D17_ALTERNATIVES, D17_QUANTITIES,
                     log.cite(*D17_CITES) + [{"id": "57", "seq": 57, "hash": "0" * 64}])
    log.add(41, "D17", "decision", content)
    return audit_case(P, log.json())


# ---------------------------------------------------------------------------- the batch

@pytest.fixture(scope="module")
def results():
    names = list(POLICIES)
    rows = run([{"id": n, **elaborate(*POLICIES[n])} for n in names])
    P = {}
    for n, row in zip(names, rows):
        assert row["status"] == "ok", (n, row)
        P[n] = {"source": deepcopy(POLICIES[n]), "policy": (row["environment_id"], row["document_hash"])}
    cases = [{"id": p.values[0], **p.values[1](P)} for p in CASES]
    return dict(zip((c["id"] for c in cases), run(cases)))


@pytest.mark.parametrize("name, build, check, expected", CASES)
def test_diagnostic(results, name, build, check, expected):
    res = results[name]
    if check == "error":
        assert res["status"] == "error", res
        assert res["error"] == expected
    elif check == "q1":
        assert res["status"] == "ok", res
        assert res["q1"] == expected
    elif check == "unranked":
        assert res["status"] == "ok", res
        assert {frozenset(p) for p in res["unranked_severities"]} == {frozenset(p) for p in expected}
    else:
        raise AssertionError(check)
