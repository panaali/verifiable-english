"""Norms operations on the Lean authority: elaboration, certificates, conflicts, admission.

Each public entry point dispatches its own adapter on FOL-family norm documents,
with `data@0` flags and definitions (`lean/VE/Norms/Flagged.lean`), and on
norm documents over the closure, core and order families
(`lean/VE/Service/FamilyNorms.lean`).
"""
from __future__ import annotations

from pathlib import Path
from copy import deepcopy

import pytest

from ve.ast import Atom, Binary, Const, Exists, Le, Named, Num, Reach, Top, Unary, Var, _to_data
from ve.backends import dispatch, relay
from ve.backends.lean_service import CheckerUnavailable
from ve.background import background
from ve.environment import Environment
from ve.errors import InvalidModel, VEError
from ve.model import FiniteModel
from ve.norms import (NormDocument, check_conflict, check_norm_entailment_certificate,
                      prove_norm_entailment)
from ve.profiles import LANGUAGE, SPEC_REVISION
from tests.test_norms import obligation, permission, rule

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(not (ROOT / "lean/.lake/build/bin/ve_service").exists(),
                                reason="Lean service has not been built")


def flagged(*, total=False, definitions=False, family=(), data=True, relation=False):
    """Norms over a FOL environment (or a `family` one) with a flagged table
    (unless `data` is false) and, optionally, a definition and a homogeneous
    binary relation."""
    predicates = {
        "required": obligation(),
        "permitted": permission(),
        "owner": {"arguments": ["act", "party"], "description": "owner",
                  **({"functional": True, **({"total": True} if total else {})} if data else {})},
        "urgent": {"arguments": ["act"], "description": "urgent"},
        **({"before": {"arguments": ["act", "act"], "description": "before"}} if relation else {}),
    }
    profiles = {"norms@0", "relational-fol@0", *family, *(("data@0",) if data else ())}
    if definitions:
        profiles.add("definitions@0")
        predicates["pressing"] = {"arguments": ["act"], "description": "pressing",
                                  "defined": {"arguments": ["act"], "body": ["unary", "urgent", ["var", 0]]}}
    return Environment({"language": LANGUAGE, "profiles": sorted(profiles), "spec_revision": SPEC_REVISION,
                        "vocabulary": {"sorts": {"act": {"description": "act"}, "party": {"description": "party"}},
                                       "predicates": predicates, "constants": {}}})


def document(env):
    guard = Unary("pressing" if "pressing" in env.predicates else "urgent", Var(0))
    return NormDocument(env, [rule("must", "required", True, guard),
                              rule("may", "permitted", True, guard)])


def routed(monkeypatch, authority):
    ops = []
    monkeypatch.setattr(dispatch, "observers", [lambda op, auth: ops.append((op, auth))])
    monkeypatch.setenv("VE_AUTHORITY", authority)
    return ops


def outcomes(doc):
    layers = doc.premises()
    proof = prove_norm_entailment(doc, (), Top(), max_steps=200)
    return {"elaborate": [(label, _to_data(f)) for label, f in layers],
            "certificate": check_norm_entailment_certificate(doc, (), Top(), proof.certificate),
            "stale": check_norm_entailment_certificate(doc, (Top(),), Top(), proof.certificate),
            "schema": check_norm_entailment_certificate(doc, (), Top(), {}),
            "conflict": check_conflict(doc, prove=True, tableau_steps=500),
            "missing": check_conflict(doc, certificates={}),
            "no evidence": check_conflict(doc)}


@pytest.mark.parametrize("total", [False, True])
@pytest.mark.parametrize("definitions", [False, True])
def test_norms_operations_with_flags_and_definitions_match_python(monkeypatch, total, definitions):
    env = flagged(total=total, definitions=definitions)
    routed(monkeypatch, "python")
    expected = outcomes(document(env))
    assert expected["certificate"].valid and expected["conflict"].status == "CONFLICT-FREE"
    ops = routed(monkeypatch, "lean")
    assert outcomes(document(env)) == expected
    assert {"norms_elaborate", "norms_certificate", "norms_conflict"} <= {op for op, _ in ops}


def test_lean_norms_background_puts_flag_premises_first():
    from ve.backends.relay import decide as run
    env = flagged(total=True, definitions=True)
    doc = document(env)
    row = run("norms", [{"id": "e", "kind": "norms-elaborate", "environment": env.to_dict(),
                         "norms": [r.to_dict() for r in doc.rules]}])[0]
    python = [(p.generator, _to_data(p.formula)) for p in background(env)]
    assert [(b["generator"], b["ast"]) for b in row["background"]] == python
    assert [g for g, _ in python][:2] == ["flags", "flags"]
    # A total flag is a ∀∃ premise the small-model restriction does not keep.
    assert row["fragment"] is False
    functional = flagged(definitions=True)
    row = run("norms", [{"id": "e", "kind": "norms-elaborate", "environment": functional.to_dict(),
                         "norms": [r.to_dict() for r in document(functional).rules]}])[0]
    assert row["fragment"] is True


def witness_model(doc, owner):
    env = doc.base_environment()
    return FiniteModel.from_dict(env, {"complete": True, "domains": {"act": ["a"], "party": ["p", "q"]},
                                       "constants": {},
                                       "relations": {"owner": owner, "urgent": [["a"]]}})


def test_conflict_witness_over_flags_is_lean_checked(monkeypatch):
    env = flagged()
    doc = NormDocument(env, [rule("must", "required", True, Unary("urgent", Var(0)))])
    model = witness_model(doc, [["a", "p"]])
    routed(monkeypatch, "python")
    expected = check_conflict(doc, model=model)
    assert expected.status == "CONFLICT" and expected.target == "required->permitted"
    ops = routed(monkeypatch, "lean")
    assert check_conflict(doc, model=model) == expected
    assert ("norms_conflict", "lean") in ops


def test_lean_rejects_a_witness_model_that_violates_a_flag():
    from ve.backends.relay import decide as run
    env = flagged()
    doc = NormDocument(env, [rule("must", "required", True, Unary("urgent", Var(0)))])
    model = witness_model(doc, [])
    wire = {**model.to_dict(), "relations": {**model.to_dict()["relations"], "owner": [["a", "p"], ["a", "q"]]}}
    case = {"id": "w", "kind": "norms-conflict", "environment": env.to_dict(),
            "norms": [r.to_dict() for r in doc.rules],
            "witness": {"target": "required->permitted", "model": wire, "tuple": ["a"]}}
    with pytest.raises(InvalidModel) as caught:
        run("norms", [case])
    assert caught.value.generator == "flags"


def test_a_witness_lean_refuses_is_checker_unavailable(monkeypatch):
    from ve.backends import relay
    env = flagged()
    doc = NormDocument(env, [rule("must", "required", True, Unary("urgent", Var(0)))])
    model = witness_model(doc, [["a", "p"]])
    real = relay.decide

    def refuse(mode, cases, **kw):
        rows = real(mode, cases, **kw)
        return [{**row, "verdict": "UNKNOWN"} if "witness" in case else row
                for case, row in zip(cases, rows)]

    monkeypatch.setattr(relay, "decide", refuse)
    routed(monkeypatch, "lean")
    with pytest.raises(CheckerUnavailable, match="does not confirm"):
        check_conflict(doc, model=model)


FAMILIES = [(("closure@0",), False), (("closure@0",), True), (("closure@0", "nary@0"), False),
            (("closure@0", "nary@0"), True), (("order@0",), False)]


@pytest.mark.parametrize("family,definitions", FAMILIES)
def test_norms_on_the_closure_core_and_order_families_are_leans(monkeypatch, family, definitions):
    """First-order norm documents over the other families: Lean regenerates the
    layers over the FOL view and checks the family's certificates."""
    from ve.backends import relay
    env = flagged(definitions=definitions, family=family, data="order@0" not in family)
    routed(monkeypatch, "python")
    expected = outcomes(document(env))
    assert expected["certificate"].valid and expected["conflict"].status == "CONFLICT-FREE"
    ops = routed(monkeypatch, "lean")
    modes = []
    real = relay.decide

    def spy(mode, cases, **kw):
        modes.append(mode)
        return real(mode, cases, **kw)

    monkeypatch.setattr(relay, "decide", spy)
    assert outcomes(document(env)) == expected
    assert {"norms_elaborate", "norms_certificate", "norms_conflict"} <= {op for op, _ in ops}
    assert "family-norms" in modes


def test_a_family_certificate_bound_to_other_premises_is_invalid_in_lean():
    from ve.backends.relay import decide as run
    env = flagged(family=("closure@0",))
    doc = document(env)
    proof = prove_norm_entailment(doc, (), Top(), max_steps=200)
    case = {"id": "c", "kind": "norms-certificate", "environment": env.to_dict(),
            "norms": [r.to_dict() for r in doc.rules], "premises": [], "conclusion": ["top"],
            "certificate": proof.certificate}
    assert run("family-norms", [case])[0]["valid"] is True
    with pytest.raises(VEError, match="stale"):
        run("family-norms", [{**case, "premises": [["top"]]}])


def test_family_conflict_witness_is_lean_checked(monkeypatch):
    env = flagged(family=("closure@0",))
    doc = NormDocument(env, [rule("must", "required", True, Unary("urgent", Var(0)))])
    model = witness_model(doc, [["a", "p"]])
    routed(monkeypatch, "python")
    expected = check_conflict(doc, model=model)
    assert expected.status == "CONFLICT"
    ops = routed(monkeypatch, "lean")
    assert check_conflict(doc, model=model) == expected
    assert ("norms_conflict", "lean") in ops


@pytest.mark.parametrize("family,guard", [
    (("closure@0",), lambda: Reach("star", Named("before"), Var(0), Var(0))),
    (("closure@0", "nary@0"), lambda: Exists("party", Atom("tri", (Var(1), Var(1), Var(0))))),
    (("order@0",), lambda: Le(Num(1), Num(2))),
])
def test_non_first_order_norms_are_dispatched_and_match_python(monkeypatch, family, guard):
    env = flagged(family=family, relation="order@0" not in family,
                  data="order@0" not in family)
    if "nary@0" in family:
        raw = env.to_dict()
        raw["vocabulary"]["predicates"]["tri"] = {
            "arguments": ["act", "act", "party"], "description": "tri"}
        env = Environment(raw)
    doc = NormDocument(env, [rule("may", "permitted", True, guard())])
    expected_layers = [(label, _to_data(f)) for label, f in doc._premises_python()]
    ops = routed(monkeypatch, "lean")
    actual = outcomes(doc)
    assert actual["elaborate"] == expected_layers
    assert actual["certificate"].valid
    assert {"norms_elaborate", "norms_certificate", "norms_conflict"} <= {op for op, _ in ops}


@pytest.mark.parametrize("field", ["order", "label", "target", "sorts"])
def test_non_first_order_elaboration_refuses_unbound_rows(monkeypatch, field):
    env = flagged(family=("closure@0",), relation=True)
    doc = NormDocument(env, [rule("may", "permitted", True,
                                  Reach("star", Named("before"), Var(0), Var(0)))])
    real = relay.decide

    def corrupt(mode, cases, **kwargs):
        row = deepcopy(real(mode, cases, **kwargs)[0])
        if cases[0]["kind"] == "norms-elaborate":
            if field == "order":
                row["order"] = []
            elif field == "label":
                row["premises"][0]["label"] = "layer:norms:absent"
            elif field == "target":
                row["conflict_targets"][0]["target"] = "absent"
            else:
                row["conflict_targets"][0]["sorts"] = ["party"]
        return [row]

    monkeypatch.setattr(relay, "decide", corrupt)
    with pytest.raises(CheckerUnavailable, match="bound to the request"):
        doc.premises()


def test_non_first_order_conflict_refuses_extra_target(monkeypatch):
    env = flagged(family=("closure@0",), relation=True)
    doc = NormDocument(env, [rule("may", "permitted", True,
                                  Reach("star", Named("before"), Var(0), Var(0)))])
    real = relay.decide

    def corrupt(mode, cases, **kwargs):
        row = deepcopy(real(mode, cases, **kwargs)[0])
        row["targets"].append("absent")
        return [row]

    monkeypatch.setattr(relay, "decide", corrupt)
    with pytest.raises(CheckerUnavailable, match="bound to the request"):
        check_conflict(doc, certificates={})


def test_non_first_order_certificate_refuses_unbound_layer_count(monkeypatch):
    env = flagged(family=("closure@0",), relation=True)
    doc = NormDocument(env, [rule("may", "permitted", True,
                                  Reach("star", Named("before"), Var(0), Var(0)))])
    proof = prove_norm_entailment(doc, (), Top(), max_steps=200)
    real = relay.decide

    def corrupt(mode, cases, **kwargs):
        row = deepcopy(real(mode, cases, **kwargs)[0])
        row["layers"] += 1
        return [row]

    monkeypatch.setattr(relay, "decide", corrupt)
    with pytest.raises(CheckerUnavailable, match="bound to the request"):
        check_norm_entailment_certificate(doc, (), Top(), proof.certificate)


def test_non_first_order_conflict_witness_is_checked_by_lean(monkeypatch):
    env = flagged(family=("closure@0",), relation=True)
    doc = NormDocument(env, [rule("must", "required", True,
                                  Reach("star", Named("before"), Var(0), Var(0)))])
    model = {"complete": True, "domains": {"act": ["a"], "party": ["p"]},
             "constants": {}, "relations": {"owner": [["a", "p"]], "urgent": [], "before": []}}
    ops = routed(monkeypatch, "lean")
    report = check_conflict(doc, model=model)
    assert report.status == "CONFLICT" and report.target == "required->permitted"
    assert ("norms_conflict", "lean") in ops


def test_non_first_order_wire_faults_raise_content_errors():
    env = flagged(family=("closure@0",), relation=True)
    doc = NormDocument(env, [rule("may", "permitted", True,
                                  Reach("star", Named("before"), Var(0), Var(0)))])
    case = {"id": "fault", "kind": "norms-elaborate", "environment": env.to_dict(),
            "norms": [r.to_dict() for r in doc.rules]}
    from ve.backends.relay import decide

    deep = ["top"]
    for _ in range(10_000):
        deep = ["not", deep]
    for bad in (7, True, None, [], {}, deep):
        mutant = deepcopy(case)
        mutant["norms"][0]["norm"]["guard"] = bad
        with pytest.raises(VEError) as caught:
            decide("family-norms", [mutant])
        assert not isinstance(caught.value, CheckerUnavailable)
    two_faults = deepcopy(case)
    two_faults["norms"][0]["norm"].update({"guard": 7, "over": None})
    with pytest.raises(VEError) as caught:
        decide("family-norms", [two_faults])
    assert not isinstance(caught.value, CheckerUnavailable)


def test_unknown_regulated_predicate_is_python_wording(monkeypatch):
    doc = document(flagged())
    for authority in ("python", "lean"):
        routed(monkeypatch, authority)
        with pytest.raises(VEError, match="^UnknownSymbol: regulated predicate urgent$"):
            doc.elaborate("urgent")


def test_norm_admission_is_dispatched_to_lean(monkeypatch):
    from ve.norm_admission import admit_norm_document
    env = flagged()
    doc = document(env)
    units = [{"id": f"u{i}", "span": [i, i + 1], "kind": "norm", "content": r.to_dict()}
             for i, r in enumerate(doc.rules)]
    layer = dict(doc.premises())["layer:norms:permitted"]
    source = {"units": units, "graph": {"root": "l", "nodes": [
        {"name": "l", "ast": _to_data(layer), "label": "layer:norms:permitted"}]}}
    routed(monkeypatch, "python")
    expected = admit_norm_document(env, source)
    ops = routed(monkeypatch, "lean")
    assert admit_norm_document(env, source) == expected
    assert ("norms_admission", "lean") in ops
