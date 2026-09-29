"""Lean rights route (docs/spec/rights.md 9.4, item 4) on inputs in the shapes of the item-1 fixtures.

The Lean executable regenerates E″, T″, Lim_D and every target from raw rights units; nothing
here is elaborated by Python (the Python rights profile is item 2). Checked: the regenerated
names and the packed limitation carve-out (γ), diagnostics (β, φ, π, υ), projections on finite
base models (α, γ), the limitation-scope audit with an uncited and a cited adopter exception
(γ, rule 7), the bar under both readings (η), delegation of soft cases, and an end-to-end
CONFLICT-FREE replay whose certificate, found by Python's unchanged prover over the
Lean-regenerated E″′_base, needs a Lim_D premise and is reported conditional on it.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from ve.ast import formula_from_data
from ve.entailment import prove_entailment
from ve.environment import Environment
from ve.wire import digest
from tests.test_norms import environment, obligation, permission

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean/.lake/build/bin/ve_rights_route"
SOFT = ROOT / "lean/.lake/build/bin/ve_soft_norms_route"
BLOCK = {"holders": ["person"], "bearers": ["state", "person"]}


@pytest.fixture(scope="module")
def lean():
    if not LEAN.exists():
        lake = shutil.which("lake")
        if lake is None:
            pytest.skip("lake is required for the rights Lean route")
        built = subprocess.run([lake, "build"], cwd=ROOT / "lean", capture_output=True,
                               text=True, timeout=600)
        assert built.returncode == 0, built.stdout + built.stderr
    return LEAN


def run(executable, cases):
    result = subprocess.run([str(executable), "-"], input=json.dumps(cases), text=True,
                            capture_output=True, timeout=180)
    assert result.returncode in (0, 1), result.stderr
    rows = json.loads(result.stdout)
    assert len(rows) == len(cases)
    return rows


def base(*args):
    return {"arguments": list(args), "description": "base"}


def env(predicates, sorts=("state", "person"), *, rights=None,
        profiles=("norms@0", "rights@0", "soft-norms@0")):
    raw = environment(predicates, sorts=sorts).to_dict()
    raw["profiles"] = sorted({"relational-fol@0"} | set(profiles))
    raw["vocabulary"]["rights"] = rights or BLOCK
    return raw


ARREST = {"arrest_permitted": permission("allow", act="{0} arrest {1}", args=("state", "person")),
          "arbitrary_arrest": base("state", "person"), "journalist": base("person")}
DEPRIVE = {"deprive_required": obligation("deny", "deprive_permitted", act="{0} deprive {1} of life",
                                          args=("state", "person")),
           "deprive_permitted": permission("allow", act="{0} deprive {1} of life", args=("state", "person"))}
IMPART = {"impart_required": obligation("deny", "impart_permitted", act="{0} impart {1}", args=("person", "idea")),
          "impart_permitted": permission("allow", act="{0} impart {1}", args=("person", "idea"))}
ARBITRARY = ["binary", "arbitrary_arrest", ["var", 1], ["var", 0]]


def norm(name, pred, sign, *, guard=("top",), unless=(), over=(), **soft):
    body = {"name": name, "sign": sign, "guard": list(guard), "unless": [list(u) for u in unless],
            "over": list(over), **soft}
    if pred is not None:
        body["predicate"] = pred
    return body


def right(name, lines, holder="person", guard=None):
    body = {"name": name, "holder": holder, "lines": lines}
    if guard is not None:
        body["guard"] = guard
    return {"right": body}


def line(kind, n, **extra):
    return {"kind": kind, "norm": n, **extra}


def limitation(name="l29", conditions=(), scope="all", kinds="all"):
    return {"limitation": {"name": name, "scope": scope, "kinds": kinds, "decided_by": "unstated",
                           "conditions": list(conditions), "factors": []}}


def condition(name, role="necessary"):
    return {"name": name, "role": role, "verbalisation": f"the limitation is {name.replace('_', ' ')}"}


L29 = limitation(conditions=[condition("determined_by_law"), condition("solely_for_permitted_purpose")])
GAMMA = [right("r9", [line("claim", norm("no-arbitrary-arrest", "arrest_permitted", False, guard=ARBITRARY))]), L29]


def elaborate(lean, environment_json, document):
    row = run(lean, [{"id": "e", "kind": "rights-elaborate", "environment": environment_json,
                      "document": document}])[0]
    assert row["status"] == "ok", row
    return row


def test_gamma_generated_names_and_packed_limitation(lean):
    row = elaborate(lean, env(ARREST), GAMMA)
    assert [g["name"] for g in row["generated"]] == ["rights__lim__1", "rights__cond__1", "rights__cond__2"]
    assert row["generated"][0] == {"name": "rights__lim__1", "kind": "lim", "limitation": "l29",
                                   "act": "arrest_permitted"}
    node = row["lines"][0]["node"]
    assert node["guard"] == ARBITRARY
    assert node["unless"] == [["or", ["bottom"], ["binary", "rights__lim__1", ["var", 1], ["var", 0]]]]
    assert [x["label"] for x in row["limitations"]] == [
        "rights:limitation:l29:arrest_permitted:necessary:determined_by_law",
        "rights:limitation:l29:arrest_permitted:necessary:solely_for_permitted_purpose"]
    assert [{k: m[k] for k in ("mechanism", "target", "licence")} for m in row["narrowings"][0]["mechanisms"]] == [
        {"mechanism": "limitation", "target": "no-arbitrary-arrest:limitation", "licence": "limitation"}]
    predicates = row["environment_prime"]["vocabulary"]["predicates"]
    assert predicates["rights__lim__1"]["arguments"] == ["state", "person"]


def test_fan_out_power_and_diagnostics(lean):
    torture = {"torture_permitted_state": permission("allow", act="{0} torture {1}", args=("state", "person")),
               "torture_permitted_person": permission("allow", act="{0} torture {1}", args=("person", "person"))}
    fan = {"state": "torture_permitted_state", "person": "torture_permitted_person"}
    beta = [right("r5", [line("claim", norm("no-torture", None, False), fan_out=fan)])]
    row = elaborate(lean, env(torture), beta)
    assert [(x["rule"], x["predicate"], x["bearer"]) for x in row["lines"]] == [
        ("rights-fan-1", "torture_permitted_person", "person"), ("rights-fan-2", "torture_permitted_state", "state")]
    nationality = {"deprive_of_nationality_permitted": permission("allow", act="{0} deprive {1} of nationality",
                                                                  args=("state", "person")),
                   "has_nationality": base("person")}

    def alters(slot):
        return {**BLOCK, "alters": {"deprive_of_nationality_permitted": {"holder_slot": slot,
                                                                        "status": "has_nationality"}}}
    phi = [right("r15", [line("immunity", norm("no-deprivation", "deprive_of_nationality_permitted", False))])]
    cases = [
        (env(torture), [right("r5", [line("claim", norm("no-torture", None, False),
                                          fan_out={"state": "torture_permitted_state"})])],
         "FanOutUndeclared: no-torture, person"),
        (env(nationality, rights=alters(0)), phi, "InvalidInput: alters deprive_of_nationality_permitted"),
        (env(ARREST), [right("r9", [line("claim", norm("rights-x", "arrest_permitted", False))])],
         "InvalidInput: name rights-x begins with rights-"),
        (env(ARREST), [right("r9", [])], "RightWithoutIncident: r9"),
        (env(ARREST), [GAMMA[0], {"limitation": {**L29["limitation"], "decided_by": "unstated"}},
                       {"bar": {"name": "b", "reading": "rule"}}, {"bar": {"name": "c", "reading": "query"}}],
         "DuplicateDeclaration: bar"),
    ]
    rows = run(lean, [{"id": str(i), "kind": "rights-elaborate", "environment": e, "document": d}
                      for i, (e, d, _) in enumerate(cases)])
    for row, (_, _, expected) in zip(rows, cases):
        assert row["status"] == "error" and row["error"] == expected, row
    assert elaborate(lean, env(nationality, rights=alters(1)), phi)["lines"][0]["holder_slot"] == 1
    no_decider = {"limitation": {k: v for k, v in L29["limitation"].items() if k != "decided_by"}}
    row = run(lean, [{"id": "p", "kind": "rights-elaborate", "environment": env(ARREST),
                      "document": [GAMMA[0], no_decider]}])[0]
    assert row["error"] == "MissingExceptionDecider: limitation l29"


def model(domains, relations):
    return {"complete": True, "domains": domains, "constants": {}, "relations": relations}


def test_projections_alpha_and_gamma(lean):
    alpha = [right("r3", [line("claim", norm("no-deprivation", "deprive_permitted", False))])]
    people = {"state": ["texas"], "person": ["ann"]}
    lim = {"rights__lim__1": [["texas", "ann"]], "rights__cond__1": [["texas", "ann"]],
           "rights__cond__2": [["texas", "ann"]]}
    none = {"rights__lim__1": [], "rights__cond__1": [], "rights__cond__2": []}
    rows = run(lean, [
        {"id": "a", "kind": "rights-projections", "environment": env(DEPRIVE), "document": alpha,
         "model": model(people, {}), "holder": "ann", "bearer": "texas"},
        {"id": "g", "kind": "rights-projections", "environment": env(ARREST), "document": GAMMA,
         "model": model(people, {"arbitrary_arrest": [["texas", "ann"]], "journalist": [], **none})},
        {"id": "g2", "kind": "rights-projections", "environment": env(ARREST), "document": GAMMA,
         "model": model(people, {"arbitrary_arrest": [["texas", "ann"]], "journalist": [], **lim})},
        # lim true with a necessary condition false violates Lim_D: not a base-admissible situation
        {"id": "g3", "kind": "rights-projections", "environment": env(ARREST), "document": GAMMA,
         "model": model(people, {"arbitrary_arrest": [["texas", "ann"]], "journalist": [],
                                 **{**lim, "rights__cond__2": []}})},
    ])
    entry = {"right": "r3", "rule": "no-deprivation", "instance": "claim", "tuple": ["texas", "ann"]}
    assert rows[0]["rights_of"] == [entry] and rows[0]["duties_of"] == [entry]
    assert [x["rule"] for x in rows[1]["duties_of"]] == ["no-arbitrary-arrest"]
    assert rows[2]["rights_of"] == [] and rows[2]["duties_of"] == []
    assert rows[3]["status"] == "error" and rows[3]["error"].startswith("InvalidModel(rights background)")


def test_scope_audit_adopter_exception(lean):
    rule7 = norm("rule-7", "arrest_permitted", True, guard=("unary", "journalist", ["var", 0]),
                 over=["no-arbitrary-arrest"])
    uncited = GAMMA + [{"norm": rule7}]
    cited = [{"source_units": ["u9"]}] + GAMMA + [{"norm": rule7, "cites": {"narrows:no-arbitrary-arrest": ["u9"]}}]
    rows = run(lean, [{"id": "u", "kind": "rights-scope", "environment": env(ARREST), "document": uncited},
                      {"id": "c", "kind": "rights-scope", "environment": env(ARREST), "document": cited},
                      # a citation to a unit the source does not have licenses nothing (4.1 step 3)
                      {"id": "x", "kind": "rights-scope", "environment": env(ARREST), "document": cited[1:]},
                      {"id": "y", "kind": "rights-scope", "environment": env(ARREST),
                       "document": [{"source_units": ["u8"]}] + cited[1:]}])
    assert rows[0]["findings"] == ["UnlicensedLimitation: exception rule-7 of rule no-arbitrary-arrest on right r9"]
    assert rows[0]["licensed"] is False
    assert rows[1]["findings"] == [] and rows[1]["licensed"] is True
    assert rows[2]["status"] == "error" and rows[2]["error"] == "UnknownSymbol: unit u9"
    assert rows[3]["status"] == "error" and rows[3]["error"] == "UnknownSymbol: unit u9"


PUBLISH = {"publish_about_required": obligation("deny", "publish_about_permitted", act="{0} publish about {1}",
                                                args=("person", "person")),
           "publish_about_permitted": permission("allow", act="{0} publish about {1}", args=("person", "person")),
           "attacks_honour": base("person", "person")}
EXCEPTION = {"decided_by": "unstated", "sufficient": [], "necessary": [], "factors": []}
ONE = {"holders": ["person"], "bearers": ["person"]}


def mu_env():
    raw = env(PUBLISH, sorts=("person",), rights=ONE)
    raw["vocabulary"]["soft"] = {"ranks": ["dignity", "expression"], "outranks": [["dignity", "expression"]],
                                 "outranking": {"mode": "strict"}}
    return raw


def mu_document(liberty_cites=None, claim_cites=None, *, strict_liberty=False):
    liberty = (norm("may-publish", "publish_about_permitted", True) if strict_liberty else
               norm("may-publish", "publish_about_permitted", True, mode="default", exception=EXCEPTION,
                    rank="expression"))
    claim = norm("no-attack", "publish_about_permitted", False, mode="default", exception=EXCEPTION,
                 rank="dignity", guard=("binary", "attacks_honour", ["var", 1], ["var", 0]))
    return [right("r19", [line("liberty", liberty, cites={"exception": ["u1"], **(liberty_cites or {})})]),
            right("r12", [line("claim", claim, holder_slot=1, cites={"exception": ["u1"], **(claim_cites or {})})]),
            limitation(), {"source_units": ["u1"]}]


def test_mu_uncited_rank_is_unlicensed_and_cited_rank_is_a_collision(lean):
    rows = run(lean, [{"id": str(i), "kind": "rights-scope", "environment": mu_env(), "document": d}
                      for i, d in enumerate([mu_document(), mu_document({"rank": ["u1"]}),
                                             mu_document(None, {"rank": ["u1"]}),
                                             mu_document(strict_liberty=True)])])
    # both default and ranked, the rank uncited: RANK-RESOLVED, and the dominance is a finding
    assert rows[0]["findings"] == ["UnlicensedLimitation: dominatedBy no-attack of rule may-publish on right r19"]
    # the lower-ranked claim is never dominated by the liberty under strict outranking
    claim = next(x for x in rows[0]["narrowings"] if x["rule"] == "no-attack")
    assert all(not m["mechanism"].startswith("dominatedBy") for m in claim["mechanisms"])
    # the rank cited on the dominated line: cited; on the dominating line: a collision
    assert rows[1]["findings"] == [] and rows[2]["findings"] == []
    dominated = next(x for x in rows[2]["narrowings"] if x["rule"] == "may-publish")
    assert {"mechanism": "dominatedBy no-attack", "target": "may-publish:dominatedBy no-attack",
            "licence": "collision"} in [{k: m[k] for k in ("mechanism", "target", "licence")}
                                        for m in dominated["mechanisms"]]
    # another right's strict liberty blocks the default claim: a collision, no finding
    assert rows[3]["findings"] == []
    blocked = next(x for x in rows[3]["narrowings"] if x["rule"] == "no-attack")
    assert {"mechanism": "blockedBy may-publish", "target": "no-attack:blockedBy may-publish",
            "licence": "collision"} in [{k: m[k] for k in ("mechanism", "target", "licence")}
                                        for m in blocked["mechanisms"]]


def test_bar_rule_and_query_readings(lean):
    liberty = right("r19", [line("liberty", norm("may-impart", "impart_permitted", True))])
    outside = [{"norm": norm("must-impart", "impart_required", True)},
               {"norm": norm("should-impart", "impart_required", True, mode="default",
                             exception={"decided_by": "unstated", "sufficient": [], "necessary": [],
                                        "factors": []})}]
    one = {"holders": ["person"], "bearers": ["person"]}
    environment_json = env(IMPART, sorts=("person", "idea"), rights=one)
    rows = run(lean, [
        {"id": "r", "kind": "rights-bar", "environment": environment_json,
         "document": [liberty, *outside, {"bar": {"name": "b30", "reading": "rule"}}]},
        {"id": "q", "kind": "rights-bar", "environment": environment_json,
         "document": [liberty, {"bar": {"name": "b30", "reading": "query"}}]},
    ])
    assert rows[0]["bars"] == [{"predicate": "impart_permitted", "aimed": "rights__bar__1", "reading": "rule",
                                "barred": ["may-impart"], "blocked_defaults": ["should-impart"],
                                "composition_candidates": ["must-impart"], "composition_conflicts": []}]
    query = rows[1]["bars"][0]
    assert query["reading"] == "query" and "entailed" not in query
    assert query["target"][0] == "forall"


def test_absent_bar_has_no_generated_aimed_predicate_or_query(lean):
    one = {"holders": ["person"], "bearers": ["person"]}
    raw = env(IMPART, sorts=("person", "idea"), rights=one)
    source = [right("r19", [line("liberty", norm("may-impart", "impart_permitted", True))])]
    rows = run(lean, [{"id": "e", "kind": "rights-elaborate", "environment": raw,
                       "document": source},
                      {"id": "b", "kind": "rights-bar", "environment": raw,
                       "document": source}])
    assert rows[0]["generated"] == []
    assert "rights__bar__1" not in rows[0]["environment_prime"]["vocabulary"]["predicates"]
    assert rows[1]["bars"] == []


def test_unsatisfiable_strict_bar_overlap_is_only_a_candidate(lean):
    one = {"holders": ["person"], "bearers": ["person"]}
    raw = env(IMPART, sorts=("person", "idea"), rights=one)
    source = [right("r19", [line("liberty", norm("may-impart", "impart_permitted", True))]),
              {"norm": norm("impossible-impart", "impart_required", True,
                            guard=("bottom",))},
              {"bar": {"name": "b30", "reading": "rule"}}]
    row = run(lean, [{"id": "b", "kind": "rights-bar", "environment": raw,
                      "document": source}])[0]["bars"][0]
    assert row["composition_candidates"] == ["impossible-impart"]
    assert row["composition_conflicts"] == []


def test_right_lines_follow_document_order_across_rights(lean):
    first = right("r1", [line("claim", norm("first", "deprive_required", True))])
    second = right("r2", [line("claim", norm("second", "deprive_required", True))])
    later = {"right_lines": {"right": "r1", "lines": [
        line("claim", norm("third", "deprive_required", True))]}}
    raw = env(DEPRIVE)
    row = run(lean, [{"id": "o", "kind": "rights-elaborate", "environment": raw,
                      "document": [first, second, later]}])[0]
    assert [item["rule"] for item in row["lines"]] == ["first", "second", "third"]


def test_interleaved_fan_out_names_follow_source_unit_order(lean):
    torture = {"torture_permitted_state": permission(
        "allow", act="{0} torture {1}", args=("state", "person")),
        "torture_permitted_person": permission(
            "allow", act="{0} torture {1}", args=("person", "person"))}
    fan = {"state": "torture_permitted_state", "person": "torture_permitted_person"}

    def fan_line(name, guard=("top",)):
        return line("claim", norm(name, None, False, guard=guard), fan_out=fan)

    units = [right("r5", [fan_line("first")]),
             right("r6", [fan_line("middle", guard=("bottom",))]),
             {"right_lines": {"right": "r5", "lines": [fan_line("last")]}}]
    row = elaborate(lean, env(torture), units)
    assert [(x["right"], x["rule"], x["node"]["guard"]) for x in row["lines"]] == [
        ("r5", "rights-fan-1", ["top"]), ("r5", "rights-fan-2", ["top"]),
        ("r6", "rights-fan-3", ["bottom"]), ("r6", "rights-fan-4", ["bottom"]),
        ("r5", "rights-fan-5", ["top"]), ("r5", "rights-fan-6", ["top"])]


def test_rights_admission_replays_regenerated_layer_and_limitation_leaves(lean):
    raw = env(ARREST)
    elaborated = run(lean, [{"id": "e", "kind": "rights-elaborate", "environment": raw,
                             "document": GAMMA}])[0]
    layer = next(p for p in elaborated["premises"] if p["label"].startswith("layer:norms:"))
    limitation = elaborated["limitations"][0]
    units = [{"id": f"u{i}", "span": [i, i + 1],
              "kind": next(iter(content)), "content": content}
             for i, content in enumerate(GAMMA)]

    def admission(premise):
        return {"units": units, "graph": {"root": "leaf", "nodes": [
            {"name": "leaf", "ast": premise["ast"], "label": premise["label"]}]}}

    rows = run(lean, [{"id": "l", "kind": "admission", "environment": raw,
                       "document": admission(layer)},
                      {"id": "r", "kind": "admission", "environment": raw,
                       "document": admission(limitation)},
                      {"id": "bad", "kind": "admission", "environment": raw,
                       "document": admission({**limitation, "ast": ["top"]})}])
    assert rows[0]["admitted"] is True and rows[0]["kinds"] == ["right", "limitation"]
    assert rows[1]["admitted"] is True
    assert rows[1]["conditional_on"] == [limitation["label"]]
    assert rows[2]["status"] == "error"


def test_rights_admission_rejects_nonexistent_citation_target(lean):
    source = right("r9", [line("claim", norm("no-arbitrary-arrest", "arrest_permitted", False),
                                cites={"exception": ["nonexistent-source-unit"]})])
    document = {"units": [{"id": "u1", "span": [0, 1], "kind": "right", "content": source}],
                "graph": {"root": "leaf", "nodes": [
                    {"name": "leaf", "ast": ["top"], "label": "asserted", "unit": "u1"}]}}
    row = run(lean, [{"id": "c", "kind": "admission", "environment": env(ARREST),
                      "document": document}])[0]
    assert row["error"] == "UnknownSymbol: unit nonexistent-source-unit"


def test_rights_admission_validates_coupled_reading_labels(lean):
    raw = env(ARREST)
    source = [right("r9", [line("claim", norm("no-arbitrary-arrest", "arrest_permitted", False))])]
    elaborated = run(lean, [{"id": "e", "kind": "rights-elaborate", "environment": raw,
                             "document": source}])[0]
    premise = elaborated["premises"][0]
    base = {"units": [{"id": "u1", "span": [0, 1], "kind": "right", "content": source[0]}],
            "graph": {"root": "leaf", "nodes": [
                {"name": "leaf", "ast": premise["ast"], "label": premise["label"]}]},
            "reading_sets": [{"id": "a", "version": 1, "readings": [["top"], ["bottom"]],
                              "labels": [{"force": "strict"}, {"force": "default"}]},
                             {"id": "b", "version": 1, "readings": [["top"], ["bottom"]],
                              "labels": [{"force": "strict"}, {"force": "default"}]}]}
    coupling = {"id": "c-force", "axis": "force", "sets": [
        {"set": "a", "version": 1}, {"set": "b", "version": 1}],
        "by": "translator", "reason_spans": ["u1"]}
    good = {**base, "couplings": [coupling]}
    bad = {**base, "couplings": [{**coupling, "axis": "missing"}]}
    many = {**base, "couplings": [{**coupling, "id": f"c{i}"} for i in range(9)]}
    rows = run(lean, [{"id": "good", "kind": "admission", "environment": raw,
                       "document": good},
                      {"id": "bad", "kind": "admission", "environment": raw,
                       "document": bad},
                      {"id": "many", "kind": "admission", "environment": raw,
                       "document": many}])
    assert rows[0]["admitted"] is True
    assert rows[1]["error"] == "CouplingLabelMissing: c-force, a"
    assert rows[2]["error"] == "ResourceLimit: couplings"


def test_rights_admission_couplings_need_one_complete_choice_as_in_python(lean):
    # Each axis alone is satisfiable, but no single choice of a's and b's readings agrees on
    # both: 6.2 rejects at admission on both routes, with the ids sorted.
    from ve.errors import VEError
    from ve.readings import validate_couplings
    from ve.rights import RightsEnvironment
    from tests.test_rights import rights_env
    raw = env(ARREST)
    source = [right("r9", [line("claim", norm("no-arbitrary-arrest", "arrest_permitted", False))])]
    elaborated = run(lean, [{"id": "e", "kind": "rights-elaborate", "environment": raw,
                             "document": source}])[0]
    premise = elaborated["premises"][0]
    labels = {"a": [{"force": "strict", "polarity": "positive"},
                    {"force": "default", "polarity": "negative"}],
              "b": [{"force": "strict", "polarity": "negative"},
                    {"force": "default", "polarity": "positive"}]}

    def document(axes, sets=labels, versions=(("a", 1), ("b", 1)), refs=1):
        couplings = [{"id": f"z-{axis}", "axis": axis,
                      "sets": [{"set": name, "version": refs} for name in ("a", "b")],
                      "by": "translator", "reason_spans": ["u1"]} for axis in axes]
        return {"units": [{"id": "u1", "span": [0, 1], "kind": "right", "content": source[0]}],
                "graph": {"root": "leaf", "nodes": [
                    {"name": "leaf", "ast": premise["ast"], "label": premise["label"]}]},
                "reading_sets": [{"id": name, "version": version,
                                  "readings": [["top"], ["bottom"]], "labels": sets[name]}
                                 for name, version in versions],
                "couplings": couplings}

    def python(doc):
        sets = [{"id": s["id"], "version": s["version"], "unit": s["id"],
                 "readings": [{"labels": lab} for lab in s["labels"]]}
                for s in doc["reading_sets"]]
        try:
            validate_couplings(RightsEnvironment(rights_env()), doc["couplings"], sets, {"u1", "a", "b"})
        except VEError as error:
            return str(error)
        return None

    agreed = {**labels, "b": [{"force": "strict", "polarity": "positive"},
                              {"force": "default", "polarity": "negative"}]}
    cases = [document(("polarity", "force")), document(("force",)), document(("polarity",)),
             document(("force", "polarity"), agreed),
             document(("force",), versions=(("a", 1), ("a", 2), ("b", 1)))]
    rows = run(lean, [{"id": str(i), "kind": "admission", "environment": raw, "document": doc}
                      for i, doc in enumerate(cases)])
    assert rows[0]["error"] == python(cases[0]) == "CouplingUnsatisfiable: z-force, z-polarity"
    assert rows[1]["admitted"] is True and python(cases[1]) is None
    assert rows[2]["admitted"] is True and python(cases[2]) is None
    assert rows[3]["admitted"] is True and python(cases[3]) is None
    # a coupling may name only the latest version of a set
    assert rows[4]["error"] == python(cases[4]) == "invalid coupling set"


def test_soft_cases_delegate_unchanged(lean):
    raw = env(DEPRIVE, profiles=("norms@0", "soft-norms@0"))
    del raw["vocabulary"]["rights"]
    case = {"id": "s", "kind": "soft-elaborate", "environment": raw,
            "norms": [{"norm": norm("m", "deprive_required", True)}]}
    assert run(lean, [case])[0] == run(SOFT, [case])[0]


# End-to-end CONFLICT-FREE replay: certificates found by Python's unchanged prover over the
# Lean-regenerated E″′_base and Background_base″, packaged with the bindings of 3.5.

def identity(profiles):
    return "v0.2:" + ",".join(profiles)


def canonical_raw(n):
    defaults = {"mode": "strict", "alterable": [], "hard": False}
    return {k: v for k, v in n.items() if defaults.get(k, object()) != v}


def canonical_unit(u):
    if "norm" in u:
        return {**u, "norm": canonical_raw(u["norm"])}
    for key in ("right", "right_lines"):
        if key in u:
            lines = [{**x, **{k: canonical_raw(x[k]) for k in ("norm", "liberty", "recognition") if k in x}}
                     for x in u[key]["lines"]]
            return {key: {**u[key], "lines": lines}}
    return u


def base_prime(row):
    data = json.loads(json.dumps(row["environment_prime"]))
    data["profiles"] = [p for p in data["profiles"] if p not in ("norms@0", "soft-norms@0", "rights@0")]
    vocab = data["vocabulary"]
    vocab.pop("soft", None)
    vocab.pop("rights", None)
    vocab["predicates"] = {n: e for n, e in vocab["predicates"].items() if "regulated" not in e}
    return Environment(data)


def packages(environment_json, document, row, *, rights=True):
    profiles = environment_json["profiles"]
    env_id = digest(f"ve-environment-{identity(profiles)}\n", environment_json)
    doc_hash = digest(f"ve-rights-{identity(profiles)}\n",
                      {"environment_id": env_id, "document": [canonical_unit(u) for u in document]})
    base_env = base_prime(row)
    slots = [b["ast"] for b in row["background"] if b["generator"] == "soft"]
    if rights:
        slots += [b["ast"] for b in row["rights_background"]]
    premises = [formula_from_data(base_env, a) for a in slots]
    out = {}
    for t in row["conflict_targets"]:
        closed = ["not", t["ast"]]
        for sort in reversed(t["sorts"]):
            closed = ["forall", sort, closed]
        result = prove_entailment(base_env, premises, formula_from_data(base_env, closed))
        if result.status == "Found":
            out[t["target"]] = {"environment_id": env_id, "document_hash": doc_hash,
                                "target": t["target"], "certificate": result.certificate}
    return out


def test_conflict_free_conditional_on_a_limitation_premise(lean):
    # limitation 29 with a sufficient condition; an adopter's permission guarded by that condition
    # collides with the claim unless Lim_D's sufficient premise makes the limitation hold there
    l29 = limitation(conditions=[condition("determined_by_law"), condition("diplomatic_immunity", "sufficient")])
    permit = norm("may-arrest", "arrest_permitted", True,
                  guard=("binary", "rights__cond__2", ["var", 1], ["var", 0]))
    document = [GAMMA[0], l29, {"norm": permit}]
    environment_json = env(ARREST)
    row = elaborate(lean, environment_json, document)
    assert [g["name"] for g in row["generated"]][1:] == ["rights__cond__1", "rights__cond__2"]
    certified = packages(environment_json, document, row)
    assert set(certified) == {t["target"] for t in row["conflict_targets"]}
    verdict = run(lean, [{"id": "c", "kind": "rights-conflict", "environment": environment_json,
                          "document": document, "packages": certified}])[0]
    assert verdict["verdict"] == "CONFLICT-FREE", verdict
    # a label is reported when replay fails with its premise replaced by ⊤ (the soft route's
    # convention), so the sufficient premise the proof needs is always among them
    assert "rights:limitation:l29:arrest_permitted:sufficient:diplomatic_immunity" in verdict["conditional_on"]
    assert all(label.startswith("rights:limitation:l29:") for label in verdict["conditional_on"])
    assert f"{len(verdict['conditional_on'])} limitation premises" in verdict["status_text"]
    # without Lim_D no certificate for the target exists
    bare = packages(environment_json, document, row, rights=False)
    assert "arrest_permitted" not in bare
    # a witness where the condition holds and the limitation fails violates Lim_D: no countermodel
    people = {"state": ["texas"], "person": ["ann"]}
    witness = {"target": "arrest_permitted", "tuple": ["texas", "ann"],
               "model": model(people, {"arbitrary_arrest": [["texas", "ann"]], "journalist": [],
                                       "rights__lim__1": [], "rights__cond__1": [],
                                       "rights__cond__2": [["texas", "ann"]]})}
    row = run(lean, [{"id": "w", "kind": "rights-conflict", "environment": environment_json,
                      "document": document, "witness": witness}])[0]
    assert row["status"] == "error" and row["error"].startswith("InvalidModel(rights background)")


def test_tau_certified_carve_out_licence(lean):
    # fixture tau: right 9's claim under limitation 29 with a declared sufficient condition; the
    # uncited carve-out U_1 = diplomat(p) and cond(l29, diplomatic_immunity, arrest)(s, p) is licensed
    # by a certificate for (own_N and U_1)° -> limpack_N over Background_base″, through Lim_D alone
    predicates = {**ARREST, "diplomat": base("person")}
    l29 = limitation(conditions=[condition("determined_by_law"), condition("solely_for_permitted_purpose"),
                                 condition("diplomatic_immunity", "sufficient")])
    carve = ["and", ["unary", "diplomat", ["var", 0]], ["binary", "rights__cond__2", ["var", 1], ["var", 0]]]
    claim = line("claim", norm("no-arbitrary-arrest", "arrest_permitted", False, guard=ARBITRARY,
                               unless=[carve]))
    document = [right("r9", [claim]), l29]
    environment_json = env(predicates)
    row = elaborate(lean, environment_json, document)
    assert row["generated"][2] == {"name": "rights__cond__2", "kind": "cond", "limitation": "l29",
                                   "act": "arrest_permitted", "condition": "diplomatic_immunity"}
    assert "rights:limitation:l29:arrest_permitted:sufficient:diplomatic_immunity" in [
        x["label"] for x in row["limitations"]]
    uncited = run(lean, [{"id": "s", "kind": "rights-scope", "environment": environment_json,
                          "document": document, "certificates": {}}])[0]
    assert uncited["findings"] == [
        "UnlicensedLimitation: carve-out 1 of rule no-arbitrary-arrest on right r9"]
    mechanism = next(m for m in uncited["narrowings"][0]["mechanisms"] if m["mechanism"] == "carve-out 1")
    profiles = environment_json["profiles"]
    env_id = digest(f"ve-environment-{identity(profiles)}\n", environment_json)
    doc_hash = digest(f"ve-rights-{identity(profiles)}\n",
                      {"environment_id": env_id, "document": [canonical_unit(u) for u in document]})
    base_env = base_prime(row)
    premises = [formula_from_data(base_env, b["ast"]) for b in row["background"] if b["generator"] == "soft"]
    premises += [formula_from_data(base_env, b["ast"]) for b in row["rights_background"]]

    def package(conclusion):
        found = prove_entailment(base_env, premises, formula_from_data(base_env, conclusion))
        assert found.status == "Found"
        return {"environment_id": env_id, "document_hash": doc_hash, "target": mechanism["target"],
                "certificate": found.certificate}

    certified = run(lean, [{"id": "c", "kind": "rights-scope", "environment": environment_json,
                            "document": document,
                            "certificates": {mechanism["target"]: package(mechanism["conclusion"])}}])[0]
    assert certified["findings"] == [] and certified["licensed"] is True
    licensed = next(m for m in certified["narrowings"][0]["mechanisms"] if m["mechanism"] == "carve-out 1")
    assert licensed["licence"] == "certified"
    # a certificate for another formula is not the target: the finding stands
    other = ["forall", "state", ["forall", "person", ["implies",
             ["and", ARBITRARY, ["and", ["unary", "diplomat", ["var", 0]],
                                 ["binary", "rights__cond__2", ["var", 1], ["var", 0]]]],
             ["binary", "rights__lim__1", ["var", 1], ["var", 0]]]]]
    wrong = run(lean, [{"id": "w", "kind": "rights-scope", "environment": environment_json,
                        "document": document, "certificates": {mechanism["target"]: package(other)}}])[0]
    assert wrong["findings"] == uncited["findings"]
    # situation B: condition and limitation false is base-admissible; the line is silent by its own guard
    people = {"state": ["texas"], "person": ["ann"]}
    situation = model(people, {"arbitrary_arrest": [], "journalist": [], "diplomat": [["ann"]],
                               "rights__lim__1": [], "rights__cond__1": [], "rights__cond__2": [],
                               "rights__cond__3": []})
    rows = run(lean, [{"id": "b", "kind": "rights-projections", "environment": environment_json,
                       "document": document, "model": situation}])
    assert rows[0]["status"] == "ok" and rows[0]["duties_of"] == []


def test_psi_bar_across_the_dual_pair_and_sigma_same_effect(lean):
    raw = env(PUBLISH, sorts=("person",), rights=ONE)
    liberty = right("r19", [line("liberty", norm("may-publish", "publish_about_permitted", True))])
    claim = right("r12", [line("claim", norm("should-publish", "publish_about_required", True, mode="default",
                                             exception=EXCEPTION), holder_slot=1, cites={"exception": ["u1"]})])
    bar = {"bar": {"name": "b30", "reading": "rule"}}
    psi = [{"source_units": ["u1"]}, liberty, claim, limitation(), bar]
    people = {"person": ["ann", "bob"]}
    aimed = model(people, {"attacks_honour": [], "rights__bar__1": [["ann", "bob"]], "rights__lim__1": [],
                           "soft__excepted__should_publish": []})
    rows = run(lean, [{"id": "s", "kind": "rights-scope", "environment": raw, "document": psi},
                      {"id": "p", "kind": "rights-projections", "environment": raw, "document": psi,
                       "model": aimed, "bearer": "ann"}])
    # the default claim on the dual obligation is reached by the bar: one mechanism `bar`, no finding
    claim_row = next(x for x in rows[0]["narrowings"] if x["rule"] == "should-publish")
    assert [(m["mechanism"], m["licence"]) for m in claim_row["mechanisms"]] == [
        ("limitation", "limitation"), ("exception", "cited"), ("bar", "bar")]
    assert rows[0]["findings"] == []
    # where the act is aimed at destruction the claim does not select: Ann owes Bob nothing
    owed = [x["tuple"] for x in rows[1]["duties_of"] if x["rule"] == "should-publish"]
    assert ["ann", "bob"] not in owed and ["ann", "ann"] in owed
    # sigma: a strict outside rule of the default liberty's own effect delivers it; the opposite
    # effect outside rights is unlicensed unless it cites the narrowing
    default_liberty = right("r19", [line("liberty", norm("may-publish", "publish_about_permitted", True,
                                                         mode="default", exception=EXCEPTION),
                                         cites={"exception": ["u1"]})])
    rule4 = norm("rule-4", "publish_about_permitted", True)
    rule5 = norm("rule-5", "publish_about_permitted", False)
    same, opposite, cited = (
        [{"source_units": ["u1"]}, default_liberty, limitation(), {"norm": rule4}],
        [{"source_units": ["u1"]}, default_liberty, limitation(), {"norm": rule5}],
        [{"source_units": ["u1"]}, default_liberty, limitation(),
         {"norm": rule5, "cites": {"narrows:may-publish": ["u1"]}}])
    rows = run(lean, [{"id": str(i), "kind": "rights-scope", "environment": raw, "document": d}
                      for i, d in enumerate((same, opposite, cited))])
    delivered = next(m for m in rows[0]["narrowings"][0]["mechanisms"] if m["mechanism"] == "blockedBy rule-4")
    assert delivered["licence"] == "effect delivered by strict rule rule-4" and rows[0]["findings"] == []
    assert rows[1]["findings"] == ["UnlicensedLimitation: blockedBy rule-5 of rule may-publish on right r19"]
    assert rows[2]["findings"] == []
