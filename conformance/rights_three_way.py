"""Rights fixture shapes: Python correlation, Lean rights, and Lean soft replay."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from tests.test_norms import obligation, permission
from tests.test_rights import claim, right, rights_env
from ve.ast import formula_to_data
from ve.rights import correlate
from ve.rights_route import expected_environment_prime, run_rights_case
from ve.soft_route import elaborate_soft_document


def fixtures():
    alpha = (rights_env(), [right()])

    beta_env = rights_env()
    beta_env["vocabulary"]["rights"]["bearers"] = ["state", "person"]
    beta_env["vocabulary"]["predicates"]["person_protect_permitted"] = permission(
        "allow", act="{0} protect {1}", args=("person", "person"))
    fan = {"kind": "claim", "holder_slot": 1, "cites": {},
           "fan_out": {"state": "protect_permitted", "person": "person_protect_permitted"},
           "norm": {"name": "no-protect", "predicate": None, "sign": False,
                    "guard": ["top"], "unless": [], "over": []}}
    beta = (beta_env, [right([fan])])

    gamma = (rights_env(), [right(), {"limitation": {
        "name": "l29", "scope": "all", "kinds": ["claim"], "decided_by": "unstated",
        "conditions": [{"name": "law", "role": "necessary", "decided_by": None,
                        "verbalisation": "determined by law"}], "factors": []}}])

    delta_env = rights_env()
    delta_env["vocabulary"]["predicates"]["religion"] = {
        "arguments": ["person"], "description": "protected religion"}
    delta_env["vocabulary"]["rights"]["protected"] = ["religion"]
    guarded = claim("religion-protect")
    guarded["norm"]["guard"] = ["unary", "religion", ["var", 0]]
    delta = (delta_env, [right([guarded])])

    rho = (rights_env(), [*gamma[1], {"limitation": {
        "name": "l29b", "scope": "all", "kinds": ["claim"], "decided_by": "unstated",
        "conditions": [{"name": "purpose", "role": "necessary", "decided_by": None,
                        "verbalisation": "for a permitted purpose"}], "factors": []}}])
    tau_line = claim("conditional-protect")
    tau_line["norm"]["guard"] = ["binary", "rights__cond__1", ["var", 1], ["var", 0]]
    tau = (rights_env(), [right([tau_line]), deepcopy(gamma[1][1])])

    epsilon_env = rights_env()
    epsilon_preds = epsilon_env["vocabulary"]["predicates"]
    epsilon_preds["marry_permitted"] = permission("allow", act="{0} marry", args=("person",))
    epsilon_preds["recognise_required"] = obligation(
        "deny", None, act="{0} recognise {1}", args=("state", "person"))
    epsilon_preds["married"] = {"arguments": ["person"], "description": "married"}
    epsilon_env["vocabulary"]["rights"]["alters"] = {
        "marry_permitted": {"holder_slot": 0, "status": "married",
                            "recognition": "recognise_required"}}
    power = {"kind": "power", "cites": {},
             "liberty": {"name": "may-marry", "predicate": "marry_permitted", "sign": True,
                         "guard": ["top"], "unless": [], "over": []},
             "recognition": {"name": "recognise-marriage", "predicate": "recognise_required",
                             "sign": True, "guard": ["top"], "unless": [], "over": []}}
    epsilon = (epsilon_env, [right([power])])

    eta_line = {"kind": "liberty", "holder_slot": None, "cites": {},
                "norm": {"name": "may-act", "predicate": "person_may_act", "sign": True,
                         "guard": ["top"], "unless": [], "over": []}}
    eta = (rights_env(), [right([eta_line]),
                              {"bar": {"name": "b30", "reading": "rule", "decided_by": "unstated"}}])
    pi = (rights_env(), [right([eta_line]),
                             {"bar": {"name": "b30", "reading": "query", "decided_by": "unstated"}}])

    theta = (rights_env(), [right(), {"norm": {
        "name": "outside", "predicate": "protect_required", "sign": False,
        "guard": ["top"], "unless": [], "over": []}}])
    return {"alpha": alpha, "beta": beta, "gamma": gamma, "delta": delta,
            "epsilon": epsilon, "eta": eta, "theta": theta, "rho": rho, "pi": pi,
            "tau": tau}


def run():
    summary = []
    for name, (raw, units) in fixtures().items():
        # Each route receives the source independently. No Python elaboration is
        # supplied to the rights executable.
        rights = correlate(deepcopy(raw), deepcopy(units))
        lean = run_rights_case(rights.env, units, "rights-elaborate")
        soft = elaborate_soft_document(rights.soft_document)
        # E″ = E + lim + cond + aimed exactly (1.5): every generated name, with no
        # allowance for a bar that is absent, and E″′ byte for byte.
        generated = (set(rights.limitation_names.values()) | set(rights.condition_names.values()) |
                     set(rights.bar_names.values()))
        assert {item["name"] for item in lean["generated"]} == generated, name
        assert lean["environment_prime"] == expected_environment_prime(rights), (name, "environment")
        assert [(item["right"], item["rule"], item["predicate"]) for item in lean["lines"]] == [
            (item["right"], item["rule"].core.name, item["rule"].core.predicate)
            for item in rights.instances], name
        assert [(item["label"], item["ast"]) for item in lean["limitations"]] == [
            (label, formula_to_data(rights.environment, formula, _generated=True))
            for label, formula in rights.limitation_premises], name
        for field in ("order", "premises", "derived", "colliding_pairs", "conflict_targets", "warnings"):
            assert lean[field] == soft[field], (name, field)
        summary.append({"fixture": name, "lines": len(lean["lines"]),
                        "limitations": len(lean["limitations"]),
                        "conflict_targets": len(lean["conflict_targets"]),
                        "three_way": "PASS"})
    return {"format": "rights-three-way@0", "fixtures": summary, "passed": len(summary)}


if __name__ == "__main__":
    result = run()
    Path(__file__).with_name("rights-three-way-report.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"PASS: {result['passed']} rights fixture shapes across Python, rights Lean, and soft Lean")
