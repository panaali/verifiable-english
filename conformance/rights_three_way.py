"""Rights fixtures (docs/spec/rights.md 10): Python correlation, Lean rights, and Lean soft replay.

Each fixture source is correlated by Python and regenerated independently by the Lean rights
route and, on the correlated soft document, by the Lean soft route; `check_rights_regenerated`
compares every output (generated keys, E″′ byte for byte, line instances and nodes, Lim_D,
bar nodes, layer order, premises, background, targets, warnings). Fixture θ is checked as its
own statement: every shape-fitting rule of the soft conformance trees, wrapped as a one-line
right with `H_R = ⊤`, correlates to exactly the flattened soft document on both routes, and
with a holder guard the nodes differ exactly by the conjunct."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from tests.test_norms import obligation, permission
from tests.test_rights import claim, right, rights_env
from ve.rights import correlate
from ve.rights_route import check_rights_regenerated, run_rights_case
from ve.backends.relay import decide
from ve.softnorms import SoftEnvironment, SoftNormDocument

EXCEPTION = {"decided_by": "unstated", "sufficient": [], "necessary": [], "factors": []}


def default(line, **soft):
    body = deepcopy(line)
    norm = body.get("norm") or body["liberty"]
    norm.update(mode="default", exception=dict(EXCEPTION), **soft)
    return body


def liberty(name, predicate="person_may_act", **soft):
    return {"kind": "liberty", "holder_slot": None, "cites": {},
            "norm": {"name": name, "predicate": predicate, "sign": True, "guard": ["top"],
                     "unless": [], "over": [], **soft}}


def l29(*conditions, scope="all", kinds="all", name="l29"):
    return {"limitation": {"name": name, "scope": scope, "kinds": kinds, "decided_by": "unstated",
                           "conditions": [{"name": c, "role": role, "decided_by": None,
                                           "verbalisation": f"the limitation is {c.replace('_', ' ')}"}
                                          for c, role in conditions], "factors": []}}


def arrest_env():
    raw = rights_env()
    predicates = raw["vocabulary"]["predicates"]
    predicates["arrest_permitted"] = permission("allow", act="{0} arrest {1}", args=("state", "person"))
    predicates["arbitrary"] = {"arguments": ["state", "person"], "description": "arbitrary"}
    predicates["diplomat"] = {"arguments": ["person"], "description": "diplomat"}
    predicates["charged"] = {"arguments": ["person"], "description": "charged"}
    return raw


def publish_env(soft=None):
    raw = rights_env()
    raw["vocabulary"]["rights"]["bearers"] = ["person"]
    predicates = raw["vocabulary"]["predicates"]
    predicates["publish_about_required"] = obligation("deny", "publish_about_permitted",
                                                      act="{0} publish about {1}", args=("person", "person"))
    predicates["publish_about_permitted"] = permission("allow", act="{0} publish about {1}",
                                                       args=("person", "person"))
    predicates["attacks_honour"] = {"arguments": ["person", "person"], "description": "attacks honour"}
    if soft is not None:
        raw["vocabulary"]["soft"] = soft
    return raw


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

    arbitrary = ["binary", "arbitrary", ["var", 1], ["var", 0]]
    arrest = {"kind": "claim", "holder_slot": None, "cites": {},
              "norm": {"name": "no-arbitrary-arrest", "predicate": "arrest_permitted", "sign": False,
                       "guard": arbitrary, "unless": [], "over": []}}
    r9 = {"right": {"name": "r9", "holder": "person", "guard": ["top"], "lines": [arrest]}}
    gamma = (arrest_env(), [r9, l29(("determined_by_law", "necessary"),
                                    ("solely_for_permitted_purpose", "necessary"))])

    delta_env = rights_env()
    delta_env["vocabulary"]["predicates"]["religion"] = {
        "arguments": ["person"], "description": "protected religion"}
    delta_env["vocabulary"]["rights"]["protected"] = ["religion"]
    guarded = claim("religion-protect")
    guarded["norm"]["guard"] = ["unary", "religion", ["var", 0]]
    delta = (delta_env, [right([guarded])])

    # (ε) a power and an immunity under a holder guard; a right_lines claim later in the
    # document; a power-only limitation that both power halves carry and the claim does not
    epsilon_env = rights_env()
    epsilon_preds = epsilon_env["vocabulary"]["predicates"]
    epsilon_preds["marry_permitted"] = permission("allow", act="{0} marry", args=("person",))
    epsilon_preds["recognise_required"] = obligation(
        "deny", None, act="{0} recognise {1}", args=("state", "person"))
    epsilon_preds["married"] = {"arguments": ["person"], "description": "married"}
    epsilon_preds["of_full_age"] = {"arguments": ["person"], "description": "of full age"}
    epsilon_preds["deprive_permitted"] = permission("allow", act="{0} deprive {1} of nationality",
                                                    args=("state", "person"))
    epsilon_preds["has_nationality"] = {"arguments": ["person"], "description": "nationality"}
    epsilon_env["vocabulary"]["rights"]["alters"] = {
        "marry_permitted": {"holder_slot": 0, "status": "married", "recognition": "recognise_required"},
        "deprive_permitted": {"holder_slot": 1, "status": "has_nationality", "recognition": None}}
    power = {"kind": "power", "cites": {},
             "liberty": {"name": "may-marry", "predicate": "marry_permitted", "sign": True,
                         "guard": ["top"], "unless": [], "over": []},
             "recognition": {"name": "recognise-marriage", "predicate": "recognise_required",
                             "sign": True, "guard": ["top"], "unless": [], "over": []}}
    immunity = {"kind": "immunity", "cites": {},
                "norm": {"name": "no-deprivation", "predicate": "deprive_permitted", "sign": False,
                         "guard": ["top"], "unless": [], "over": []}}
    r16 = {"right": {"name": "r16", "holder": "person", "guard": ["unary", "of_full_age", ["var", 0]],
                     "lines": [power]}}
    r15 = {"right": {"name": "r15", "holder": "person", "guard": ["top"], "lines": [immunity]}}
    epsilon = (epsilon_env, [r16, r15, {"right_lines": {"right": "r16", "lines": [claim("register")]}},
                             l29(kinds=["power"], name="lp")])

    eta_line = liberty("may-act")
    bar_rule = {"bar": {"name": "b30", "reading": "rule", "decided_by": "unstated"}}
    eta = (rights_env(), [right([eta_line]), bar_rule,
                          {"norm": {"name": "should-act", "predicate": "person_may_act", "sign": False,
                                    "guard": ["top"], "unless": [], "over": [], "mode": "default",
                                    "exception": dict(EXCEPTION)}}])
    pi = (rights_env(), [right([default(eta_line)]),
                         {"bar": {"name": "b30", "reading": "query", "decided_by": "unstated"}}])

    theta = (rights_env(), [right(), {"norm": {
        "name": "outside", "predicate": "protect_required", "sign": False,
        "guard": ["top"], "unless": [], "over": []}}])

    # (κ) Art. 25/22: a default claim citing its exception under limitation 29
    kappa_line = default(claim("secure"))
    kappa_line["cites"] = {"exception": ["u082"]}
    kappa = (rights_env(), [{"source_units": ["u082"]}, right([kappa_line]), l29(("law", "necessary"))])

    # (μ) binary shape: a default liberty of right 19 dominated by a ranked default claim of right 12
    ranked = {"ranks": ["dignity", "expression"], "outranks": [["dignity", "expression"]],
              "outranking": {"mode": "strict"}}
    may_publish = default(liberty("may-publish", "publish_about_permitted"), rank="expression")
    no_attack = default({"kind": "claim", "holder_slot": 1, "cites": {"rank": ["u1"]},
                         "norm": {"name": "no-attack", "predicate": "publish_about_permitted", "sign": False,
                                  "guard": ["binary", "attacks_honour", ["var", 1], ["var", 0]],
                                  "unless": [], "over": []}}, rank="dignity")
    r19 = {"right": {"name": "r19", "holder": "person", "guard": ["top"], "lines": [may_publish]}}
    r12 = {"right": {"name": "r12", "holder": "person", "guard": ["top"], "lines": [no_attack]}}
    mu = (publish_env(ranked), [{"source_units": ["u1"]}, r19, r12, l29()])

    # (ν) a switchable right line (users may turn off), uncited
    nu_env = rights_env()
    nu_env["vocabulary"]["soft"] = {"parties": ["user"], "ranks": [], "outranks": [],
                                    "outranking": {"mode": "strict"}}
    switched = claim("switched")
    switched["norm"]["alterable"] = ["user"]
    nu = (nu_env, [right([switched]), l29()])

    # (ο) six author carve-outs on a default switchable line: T″′ carries eight
    omicron_line = default(claim("six"))
    omicron_line["norm"]["unless"] = [["binary", "arbitrary", ["var", 1], ["var", 0]]] * 6
    omicron_line["norm"]["alterable"] = ["user"]
    omicron_env = deepcopy(nu_env)
    omicron_env["vocabulary"]["predicates"]["arbitrary"] = {"arguments": ["state", "person"],
                                                            "description": "arbitrary"}
    omicron = (omicron_env, [right([omicron_line]), l29()])

    rho = (arrest_env(), [r9, l29(("determined_by_law", "necessary")), l29(scope=["r9"], name="l29b")])

    # (σ) a default liberty and an adopter's strict same-effect rule outside rights
    sigma_env = rights_env()
    sigma_env["vocabulary"]["predicates"]["journalist"] = {"arguments": ["person"], "description": "j"}
    sigma = (sigma_env, [right([default(eta_line)]), l29(),
                         {"norm": {"name": "rule-4", "predicate": "person_may_act", "sign": True,
                                   "guard": ["unary", "journalist", ["var", 0]], "unless": [], "over": []}}])

    # (τ) right 9's claim under limitation 29 with the sufficient condition diplomatic_immunity; the
    # carve-out diplomat(p) ∧ cond_{l29,diplomatic_immunity,arrest}(s, p), uncited
    tau_claim = deepcopy(arrest)
    tau_claim["norm"]["unless"] = [["and", ["unary", "diplomat", ["var", 0]],
                                    ["binary", "rights__cond__2", ["var", 1], ["var", 0]]]]
    tau = (arrest_env(), [{"right": {**r9["right"], "lines": [tau_claim]}},
                          l29(("determined_by_law", "necessary"), ("diplomatic_immunity", "sufficient"),
                              ("solely_for_permitted_purpose", "necessary"))])

    # (ψ) the bar across the dual pair: a default positive claim on the dual obligation
    should_publish = default({"kind": "claim", "holder_slot": 1, "cites": {"exception": ["u1"]},
                              "norm": {"name": "should-publish", "predicate": "publish_about_required",
                                       "sign": True, "guard": ["top"], "unless": [], "over": []}})
    strict_publish = liberty("may-publish", "publish_about_permitted")
    psi = (publish_env(), [{"source_units": ["u1"]},
                           {"right": {**r19["right"], "lines": [strict_publish]}},
                           {"right": {**r12["right"], "lines": [should_publish]}}, l29(), bar_rule])

    # a holder guard and a charged holder (θ's second half, as a correlation fixture)
    charged = (arrest_env(), [{"right": {**r9["right"], "guard": ["unary", "charged", ["var", 0]]}}])
    return {"alpha": alpha, "beta": beta, "gamma": gamma, "delta": delta, "epsilon": epsilon,
            "eta": eta, "theta-row": theta, "kappa": kappa, "mu": mu, "nu": nu, "omicron": omicron,
            "pi": pi, "rho": rho, "sigma": sigma, "tau": tau, "psi": psi, "charged": charged}


def theta_rows(seeds=range(60)):
    """θ: every shape-fitting rule of the soft conformance trees wrapped as a one-line right
    (`H_R = ⊤`, no limitation, no bar) correlates to the flattened soft document on the
    Python route, the Lean rights route and the Lean soft route; with `H_R = u(h)` the Lean
    line nodes differ exactly by the conjunct. Rows with no fitting rule are skipped."""
    from conformance.soft_norms import generated
    compared = skipped = 0
    for seed in seeds:
        raw, rules = generated(seed)
        try:
            SoftNormDocument(SoftEnvironment(raw), rules)
        except Exception:
            continue
        fitting = [r for r in rules if r["norm"]["predicate"] == "x_permitted" and r["norm"]["sign"]]
        if not fitting:
            skipped += 1
            continue
        outside = [r for r in rules if r not in fitting]
        rights_raw = deepcopy(raw)
        rights_raw["profiles"] = sorted({*rights_raw["profiles"], "rights@0"})
        rights_raw["vocabulary"]["rights"] = {"holders": ["assistant"], "bearers": ["assistant"],
                                              "protected": [], "alters": {}}
        units = [{"right": {"name": f"r{i + 1}", "holder": "assistant", "guard": ["top"],
                            "lines": [{"kind": "liberty", "cites": {}, "norm": r["norm"]}]}}
                 for i, r in enumerate(fitting)] + outside
        rights = correlate(deepcopy(rights_raw), deepcopy(units))
        flat = SoftNormDocument(SoftEnvironment(raw), fitting + outside)
        # correlate D = flattenTop D: the same rules in the same order, E″′ = E′
        assert [r.to_dict() for r in rights.soft_document.rules] == [r.to_dict() for r in flat.rules], seed
        assert rights.soft_document.extended_env.to_dict() == flat.extended_env.to_dict(), seed
        lean = run_rights_case(rights.env, units, "rights-elaborate")
        check_rights_regenerated(rights, lean)
        soft = decide("soft-norms", [{"id": "f", "kind": "soft-elaborate", "environment": raw,
                                      "norms": fitting + outside}])[0]
        for field in ("order", "premises", "derived", "colliding_pairs", "conflict_targets",
                      "warnings", "decisions", "background"):
            assert lean[field] == soft[field], (seed, field)
        prime = deepcopy(lean["environment_prime"])
        prime["profiles"].remove("rights@0")
        del prime["vocabulary"]["rights"]
        assert prime == soft["environment_prime"], seed
        guarded = [{"right": {**u["right"], "guard": ["unary", "u", ["var", 0]]}} for u in units[:len(fitting)]]
        charged_row = run_rights_case(rights.env, guarded + outside, "rights-elaborate")
        for row, plain in zip(charged_row["lines"], lean["lines"]):
            assert row["node"] == {**plain["node"], "guard": ["and", plain["node"]["guard"],
                                                              ["unary", "u", ["var", 0]]]}, seed
        compared += 1
    return {"fixture": "theta", "wrapped_documents": compared, "skipped_documents": skipped,
            "three_way": "PASS"}


def run():
    summary = []
    for name, (raw, units) in fixtures().items():
        # Each route receives the source independently. No Python elaboration is
        # supplied to the rights executable.
        rights = correlate(deepcopy(raw), deepcopy(units))
        lean = run_rights_case(rights.env, units, "rights-elaborate")
        check_rights_regenerated(rights, lean)
        summary.append({"fixture": name, "lines": len(lean["lines"]),
                        "limitations": len(lean["limitations"]),
                        "conflict_targets": len(lean["conflict_targets"]),
                        "three_way": "PASS"})
    summary.append(theta_rows())
    return {"format": "rights-three-way@0", "fixtures": summary, "passed": len(summary)}


if __name__ == "__main__":
    result = run()
    Path(__file__).with_name("rights-three-way-report.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"PASS: {result['passed']} rights fixtures across Python, rights Lean, and soft Lean")
