"""norm-defaults@0 on the soft and rights routes, in Lean (lean-first batch 10a;
docs/spec/norm-defaults.md 2.3 and 3.3; lean/VE/NormDefaults/Layered.lean).

`fill` runs last: `fill (soften T)` and `fill (soften (correlate D))`. No caller uses the
Lean branch yet (batch 10b switches them); these tests hold it to Python's
`UnspecifiedSoftDocument` and `UnspecifiedRightsDocument` and check that the route's base
premises (`Soft_T` on the filled tree, the rights limitation premises) bind every answer.
"""
from __future__ import annotations

import json
from copy import deepcopy

import pytest

from conformance import norm_defaults_layered as layered
from tests.test_norm_defaults_three_way import lean_executable  # noqa: F401  (the route fixture)
from ve import norm_defaults as nd
from ve import norm_defaults_route as route
from ve.errors import VEError


def _fixture(name):
    return next((kind, env, source, situations) for n, kind, env, source, situations in layered.fixtures()
                if n == name)


def _run(cases, executable):
    return route.run_cases(cases, executable)


def _elaborate(name, executable):
    kind, env, source, _ = _fixture(name)
    (row,) = _run([layered.case(kind, env, source, "norm-defaults-elaborate")], executable)
    assert row["status"] == "ok", row
    return row


def test_soft_and_rights_fixtures_agree_with_python(lean_executable):
    """Spec 9 u2, u3, u8 and u9 and a coherence case: the regeneration, `Soft_T`, the
    rights premises and the bound base environment byte for byte; every status, conflict
    verdict and report line as Python's."""
    result = layered.run(lean_executable)
    rows = {r["fixture"]: r for r in result["fixtures"]}
    assert [(r["fixture"], r["mismatches"]) for r in result["fixtures"] if r["mismatches"]] == []
    assert result["passed"] == len(rows) == 12
    # u8: CONFLICT-FREE (soft's deny variant is CONFLICT); X is permitted where rule `s`
    # selects and UNDECIDED where it is excepted (statuses in layer order, x_permitted first).
    assert rows["u8-unspecified"]["conflict"] == ["CONFLICT-FREE"] * 2
    assert rows["u8-unspecified"]["statuses"] == ["SETTLED yes", "SETTLED yes", "UNDECIDED", "SETTLED no"]
    assert rows["u8-deny"]["conflict"][0] == "CONFLICT"
    # u2: where the exception holds, strict is SETTLED no and default UNDECIDED; the deny
    # variant keeps the collapse (SETTLED no) and reports `default reached`.
    assert rows["u2-unspecified-strict"]["statuses"] == ["SETTLED no", "SETTLED no"]
    assert rows["u2-unspecified-default"]["statuses"] == ["SETTLED no", "UNDECIDED"]
    assert rows["u2-deny-default"]["statuses"] == ["SETTLED no", "SETTLED no"]
    assert rows["u2-deny-default"]["reached"] == ["reachable"]
    assert rows["u3-strict"]["statuses"] == ["SETTLED no"] and rows["u3-default"]["statuses"][-1] == "UNDECIDED"
    # u9: the limited arrest is UNDECIDED, SETTLED yes under allow, SETTLED no under deny
    assert [rows[f"u9-{d}"]["statuses"][-1] for d in ("unspecified", "allow", "deny")] == \
        ["UNDECIDED", "SETTLED yes", "SETTLED no"]
    assert all(rows[f"u9-{d}"]["rights"] == ["rights:limitation:l29:arrest_permitted:necessary:law"]
               for d in ("unspecified", "allow", "deny"))
    assert rows["coherent"]["soft"] == ["soft:exception:must-x:sufficient:0", "soft:coherence:must-x,need-not-x"]


def test_coherence_is_regenerated_on_the_filled_tree(lean_executable):
    """3.3: `Coh_T`'s selections read unsaid atoms where guards mention unspecified
    predicates; soft's own `Coh_T` (on `soften T`) reads the placeholder deny instead."""
    row = _elaborate("coherent", lean_executable)
    (coherence,) = [p for p in row["soft"] if p["label"].startswith("soft:coherence:")]
    assert "unsaid__y_permitted" in json.dumps(coherence["ast"])
    kind, env, source, _ = _fixture("coherent")
    doc = layered.document(kind, env, source)
    soft_own = dict(doc.soft.coherence_premises)["soft:coherence:must-x,need-not-x"]
    assert "unsaid__y_permitted" not in json.dumps(layered._to_data(soft_own))


def test_undecided_fillings_must_satisfy_the_route_premises(lean_executable):
    """`coherent` with no rule excepted: `Coh_T` forces `unsaid__y_permitted` false, so a
    pair whose `yes` filling makes y permitted is no UNDECIDED witness. Python's own
    enumeration reads `Fill_T` only and refuses the pair it then finds."""
    env, rules, situation = layered.coherent_unexcepted()
    doc = layered.document("soft", env, rules)
    with pytest.raises(VEError, match="undecided witness failed its own check"):
        doc.status(doc.situation(situation), "x_required", ("a",))
    point = {"model": situation, "predicate": "y_permitted", "tuple": ["a"]}
    yes, no = {"unsaid__y_permitted": [["a"]]}, {"unsaid__y_permitted": []}
    cases = [layered.case("soft", env, rules, "norm-defaults-status", method="undecided", yes=yes, no=no, **point),
             layered.case("soft", env, rules, "norm-defaults-status", method="enumerate", **point),
             layered.case("soft", env, rules, "norm-defaults-status", method="table3", **point)]
    assert [r["point_status"] for r in _run(cases, lean_executable)] == ["UNKNOWN"] * 3
    # the same filling as evidence of a gap is refused as inadmissible, naming soft
    witness = {"model": situation, "filling": yes, "tuple": ["a"]}
    (row,) = _run([layered.case("soft", env, rules, "norm-defaults-report", witnesses={"y_permitted": witness})],
                  lean_executable)
    assert row["error"] == "InvalidModel(soft): the model violates a background premise"
    # with the admissible filling the gap is reachable
    witness["filling"] = no
    (row,) = _run([layered.case("soft", env, rules, "norm-defaults-report", witnesses={"y_permitted": witness})],
                  lean_executable)
    assert [r["reached"] for r in row["report"] if r["predicate"] == "y_permitted"] == ["reachable"]


def test_rights_limitation_premises_bind_fillings(lean_executable):
    """u9: a limited arrest without its necessary condition violates the limitation
    premise, whatever the filling; Lean refuses it as `InvalidModel(rights)`."""
    kind, env, source, situations = _fixture("u9-unspecified")
    bad = deepcopy(situations[1])
    bad["relations"]["rights__cond__1"] = []
    doc = layered.document(kind, env, source)
    situation = doc.situation(bad)
    assert not doc.fill_valid(situation, doc.canonical_filling(situation))
    witness = {"model": bad, "filling": {}, "tuple": ["s", "p"]}
    (row,) = _run([layered.case(kind, env, source, "norm-defaults-report", witnesses={"arrest_permitted": witness})],
                  lean_executable)
    assert row["error"] == "InvalidModel(rights): the model violates a background premise"


def test_packages_are_bound_to_the_source_and_the_layered_background(lean_executable):
    """Python's certificates replay only under the bindings Lean regenerates: another
    document hash, another environment id, or a certificate whose premise list drops a
    rights premise is a missing or invalid certificate, never CONFLICT-FREE."""
    kind, env, source, situations = _fixture("u9-unspecified")
    doc = layered.document(kind, env, source)
    row = _elaborate("u9-unspecified", lean_executable)
    bindings = {"environment_id": row["environment_id"], "document_hash": row["document_hash"]}
    verdict, good = layered.conflict_case(kind, env, source, doc, situations[0], bindings)
    assert verdict == "CONFLICT-FREE"

    def mutant(edit):
        case = deepcopy(good)
        for package in case["packages"].values():
            edit(package)
        return case
    cases = [good,
             mutant(lambda p: p.update(document_hash="0" * 64)),
             mutant(lambda p: p.update(environment_id=doc.env.environment_id[:-1] + "0")),
             mutant(lambda p: p["certificate"]["premise_meaning_ids"].pop())]
    rows = _run(cases, lean_executable)
    assert [r["verdict"] for r in rows] == ["CONFLICT-FREE", "UNKNOWN", "UNKNOWN", "UNKNOWN"]
    assert all(r["detail"].startswith("missing certificate for ") for r in rows[1:])


def test_a_conflict_witness_is_checked(lean_executable):
    """u8-deny: Python's settled witness is a Lean CONFLICT; the same filling at a
    situation where the rule is excepted is not."""
    kind, env, source, situations = _fixture("u8-deny")
    doc = layered.document(kind, env, source)
    verdict, case = layered.conflict_case(kind, env, source, doc, situations[0], {})
    assert verdict == "CONFLICT"
    moved = deepcopy(case)
    moved["witness"]["model"] = situations[1]
    assert [r["verdict"] for r in _run([case, moved], lean_executable)] == ["CONFLICT", "UNKNOWN"]


def test_reserved_names_and_kinds(lean_executable):
    kind, env, source, situations = _fixture("u8-unspecified")
    reserved = deepcopy(source)
    reserved[0]["norm"]["name"] = "unsaid--s"
    with pytest.raises(VEError) as caught:
        layered.document(kind, env, reserved)
    rows = _run([layered.case(kind, env, reserved, "norm-defaults-elaborate"),
                 layered.case(kind, env, source, "norm-defaults-gaps", predicate="x_permitted"),
                 layered.case(kind, env, source, "norm-defaults-certificate")], lean_executable)
    assert rows[0]["error"] == str(caught.value) == "InvalidInput: reserved name unsaid--s"
    assert rows[1]["error"] == ("UnsupportedProfile: case kind norm-defaults-gaps is not available on the "
                                "soft-norms@0 norm-defaults branch")
    assert rows[2]["error"].startswith("UnsupportedProfile: case kind norm-defaults-certificate")
    # without the profile the soft route's unspecified completion is refused, as on the norms route
    plain = deepcopy(env)
    plain["profiles"].remove("norm-defaults@0")
    (row,) = _run([layered.case(kind, plain, source, "norm-defaults-elaborate")], lean_executable)
    assert row["error"] == "UnsupportedProfile: unspecified completion requires norm-defaults@0"


def test_situations_are_typed_and_unsaid_tables_are_fillings(lean_executable):
    kind, env, source, situations = _fixture("u8-unspecified")
    point = {"predicate": "x_permitted", "tuple": ["a"], "method": "table3"}
    unsaid = deepcopy(situations[0])
    unsaid["relations"]["unsaid__x_permitted"] = [["a"]]
    cases = [layered.case(kind, env, source, "norm-defaults-status", model=unsaid, **point),
             layered.case(kind, env, source, "norm-defaults-status", model=situations[0],
                          **{**point, "tuple": ["nobody"]}),
             layered.case(kind, env, source, "norm-defaults-status", model=situations[0],
                          **{**point, "method": "guess"})]
    rows = _run(cases, lean_executable)
    assert rows[0]["error"] == ("InvalidModel(norm-defaults): unsaid__x_permitted is a filling; "
                                "supply it as a filling, not a table")
    assert rows[1]["error"] == "InvalidInput: tuple has the wrong length or sort"
    assert rows[2]["error"] == "InvalidInput: unknown status method guess"


@pytest.mark.parametrize("fixture,entities,predicate", [
    ("u8-unspecified", ["a"], "x_permitted"),
    ("u9-unspecified", ["s", "p"], "arrest_permitted"),
])
def test_nested_fillings_are_checked_before_evidence_replay(lean_executable, fixture, entities, predicate):
    """Every evidence entry uses the same strict decoder. An oversized tuple must
    never become its valid prefix, and an unknown entity must not disappear when
    the finite model filters untyped tuples."""
    kind, env, source, situations = _fixture(fixture)
    table = "unsaid__" + predicate
    status = layered.case(kind, env, source, "norm-defaults-status", model=situations[1],
                          predicate=predicate, tuple=entities, method="undecided",
                          yes={table: [entities]}, no={})
    mutations = [7, True, [], {"other": []},
                 {table: [entities + ["extra"]]},
                 {table: [entities[:-1]]},
                 {table: [["nobody", *entities[1:]]]},
                 {table: [7]}, {table: [entities, entities]}]
    # Both sides of an undecided witness, plus the filling of a report witness.
    cases = []
    for field in ("yes", "no"):
        for value in mutations[:8]:
            case = deepcopy(status)
            case[field] = value
            cases.append(case)
    for value in mutations:
        witness = {"model": status["model"], "filling": value, "tuple": entities}
        cases.append(layered.case(kind, env, source, "norm-defaults-report",
                                  witnesses={predicate: witness}))
    rows = _run([status, *cases], lean_executable)
    assert rows[0]["point_status"] == "UNDECIDED"
    assert all(row["status"] == "error" for row in rows[1:]), rows
    assert all(row.get("point_status") != "UNDECIDED" and
               all(line.get("reached") != "reachable" for line in row.get("report", []))
               for row in rows[1:])


def test_layered_report_grounding(lean_executable):
    """u9-allow is a translation: its reached allow completion is `UngroundedDefault`
    unless the block cites it, as on the norms route."""
    kind, env, source, situations = _fixture("u9-allow")
    block = {"arrest_permitted": {"cites": ["a29"], "reason": "Article 29 states it"}}
    cases = [layered.case(kind, env, source, "norm-defaults-report", model=situations[1], translation=True),
             layered.case(kind, env, source, "norm-defaults-report", model=situations[1], translation=True,
                          completions=block, unit_ids=["a29"])]
    rows = _run(cases, lean_executable)
    assert rows[0]["findings"] == ["UngroundedDefault: arrest_permitted"]
    assert rows[1]["findings"] == [] and rows[1]["report"][0]["lines"][-1] == "grounded: a29"
    doc = layered.document(kind, env, source)
    lines = nd.report(doc, model=situations[1], translation=True,
                      completions=nd.validate_completions(doc, block, {"a29"}))
    assert rows[1]["report"][0]["lines"] == list(lines[0].lines())
