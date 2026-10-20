"""Backend integration on the public evaluation and Background signatures.

Since lean-first batch 18 the public operations are Lean's with no authority to select: each test
compares Lean's public answer with the retained Python evaluator (`tests/python_oracle.py`), or checks
the answer itself where no Python implementation is left."""
from __future__ import annotations

from pathlib import Path
import json

import pytest

from conformance.p0 import environment
from ve import Environment, FiniteModel
from ve.ast import (And, Atom, Binary, Bottom, Const, Eq, Exists, Forall, Implies,
                    Named, Not, Or, Reach, Top, Unary, Var)
from ve.background import background
from ve.evaluate import evaluate
from ve.errors import VEError
from ve.backends.lean_service import CheckerUnavailable
from ve.search import check_countermodel, find_countermodel
from ve.admission import admit_document
from tests import python_oracle

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean/.lake/build/bin/ve_service"
RUST = ROOT / "rust/target/release/ve"


@pytest.mark.skipif(not LEAN.exists(), reason="Lean service has not been built")
def test_lean_norms_admission_with_data_flags():
    from ve.norms import NormDocument
    from tests.test_norms import permission, rule
    raw = {"language": "ve.core@0.2", "profiles": ["data@0", "norms@0", "relational-fol@0"],
           "spec_revision": environment()["spec_revision"],
           "vocabulary": {"sorts": {"act": {"description": "act"}}, "constants": {},
                          "predicates": {"permitted": permission(),
                                         "owner": {"arguments": ["act", "act"], "description": "owner",
                                                   "functional": True}}}}
    env = Environment(raw)
    norms = NormDocument(env, [rule("allow", "permitted", True)])
    flag = Forall("act", Forall("act", Forall("act", Implies(
        And(Binary("owner", Var(2), Var(1)), Binary("owner", Var(2), Var(0))), Eq(Var(1), Var(0))))))
    from ve.ast import formula_to_data
    document = {"units": [{"id": "u1", "span": [0, 20], "kind": "norm",
                           "content": norms.rules[0].to_dict()}],
                "graph": {"root": "flag", "nodes": [
                    {"name": "layer", "ast": formula_to_data(env, norms.elaborate("permitted")),
                     "label": "layer:norms:permitted"},
                    {"name": "flag", "ast": formula_to_data(env, flag, _generated=True),
                     "label": "background:flags"}]}}
    rejected = {**document, "graph": {"root": "flag", "nodes": [
        {**document["graph"]["nodes"][1], "label": "background:literals"}]}}
    closure = {**raw, "profiles": ["closure@0", "norms@0", "relational-fol@0"],
               "vocabulary": {**raw["vocabulary"], "predicates": {"permitted": permission()}}}
    row = [admit_document(env, document)]
    for e, d in ((env, rejected), (closure, document)):
        try:
            admit_document(e, d)
        except VEError as error:
            row.append((error.code, str(error)))
    assert row[0]["admitted"] and len(row) == 3


@pytest.mark.skipif(not (LEAN.exists() and RUST.exists()), reason="backends have not been built")
def test_budgeted_order_evaluation_matches_python():
    from tests.probe_matrix import model_wire, raw_environment
    from ve.ast import Le, Num
    env = Environment(raw_environment(("order@0",)))
    model = FiniteModel.from_dict(env, model_wire(env))
    formula = Le(Num(0), Num(1))
    expected = [python_oracle.evaluate(env, formula, model, trace=False, max_evaluations=n).to_dict()
                for n in (0, 1, 2)]
    assert [evaluate(env, formula, model, trace=False, max_evaluations=n).to_dict()
            for n in (0, 1, 2)] == expected


@pytest.mark.skipif(not (LEAN.exists() and RUST.exists()), reason="backends have not been built")
@pytest.mark.parametrize("formula,budget,trace_budget", [
    (Top(), 1, 1), (Top(), 0, 1),
    (And(Top(), Bottom()), 3, 3), (Or(Top(), Bottom()), 2, 2),
    (Implies(Bottom(), Top()), 2, 2),
    (Forall("item", Eq(Var(0), Const("x"))), 3, 3),
    (Forall("item", Eq(Var(0), Const("x"))), 3, 1),
])
def test_traced_order_evaluation_matches_python(formula, budget, trace_budget):
    from tests.probe_matrix import model_wire, raw_environment
    from ve.ast import Le, Num
    env = Environment(raw_environment(("order@0",)))
    model = FiniteModel.from_dict(env, model_wire(env))
    cases = (formula, Le(Num(0), Num(1)))
    expected = [python_oracle.evaluate(env, f, model, trace=True, max_evaluations=budget,
                                       max_trace_nodes=trace_budget).to_dict() for f in cases]
    assert [evaluate(env, f, model, trace=True, max_evaluations=budget,
                     max_trace_nodes=trace_budget).to_dict() for f in cases] == expected


@pytest.fixture
def fixture():
    wire = environment()
    wire["vocabulary"]["sorts"]["person"] = {"description": "A person."}
    for item in wire["vocabulary"]["constants"].values():
        item["sort"] = "person"
        item["description"] = "A named person."
    wire["vocabulary"]["predicates"]["ready"] = {
        "arguments": ["person"], "description": "A ready person."}
    wire["vocabulary"]["predicates"]["knows"] = {
        "arguments": ["person", "person"], "description": "One person knows another."}
    env = Environment(wire)
    model = FiniteModel.from_dict(env, {"complete": True,
                                      "domains": {"person": ["a", "b"]},
                                      "constants": {"alpha": "a", "beta": "b"},
                                      "relations": {"ready": [["a"]], "knows": [["a", "b"]]}})
    return env, model


@pytest.mark.skipif(not (LEAN.exists() and RUST.exists()), reason="backends have not been built")
@pytest.mark.parametrize("formula,budget", [(Top(), 1), (Bottom(), 1),
                                           (And(Top(), Top()), 2), (Top(), 0)])
def test_budgeted_evaluation_matches_python(fixture, formula, budget):
    env, model = fixture
    expected = python_oracle.evaluate(env, formula, model, trace=False, max_evaluations=budget)
    assert evaluate(env, formula, model, trace=False,
                    max_evaluations=budget).to_dict() == expected.to_dict()


def test_missing_rust_binary_fails_closed_and_lean_evaluation_does_not_need_it(monkeypatch, fixture, tmp_path):
    env, model = fixture
    monkeypatch.setenv("VE_RUST_JSONL", str(tmp_path / "missing-ve"))
    # Neither evaluation nor the countermodel check runs Rust (lean-first batches 15b and 18): both
    # report Lean's metered evaluator. Only the search needs the Rust binary.
    assert evaluate(env, Top(), model, trace=True).value is True
    assert check_countermodel(env, (), Bottom(), model).valid is True
    with pytest.raises(CheckerUnavailable):
        find_countermodel(env, (), Bottom(), max_domain_size=1)


@pytest.mark.skipif(not (LEAN.exists() and RUST.exists()), reason="backends have not been built")
@pytest.mark.parametrize("formula,budget,trace_budget", [
    (Top(), 1, 1), (Top(), 1, 10 ** 100), (Top(), 0, 10),
    (And(Top(), Bottom()), 3, 3),
    (And(Bottom(), Top()), 2, 2), (Or(Top(), Bottom()), 2, 2),
    (Implies(Bottom(), Top()), 2, 2), (Not(Top()), 2, 2),
    (Eq(Const("alpha"), Const("beta")), 1, 1),
    (Unary("ready", Const("alpha")), 1, 1),
    (Binary("knows", Const("alpha"), Const("beta")), 1, 1),
    (Forall("person", Eq(Var(0), Const("alpha"))), 3, 3),
    (Exists("person", Eq(Var(0), Const("beta"))), 3, 3),
    (Exists("person", Top()), 4, 1),
])
def test_traced_evaluation_matches_python(fixture, formula, budget, trace_budget):
    env, model = fixture
    expected = python_oracle.evaluate(env, formula, model, trace=True,
                                      max_evaluations=budget, max_trace_nodes=trace_budget)
    actual = evaluate(env, formula, model, trace=True, max_evaluations=budget, max_trace_nodes=trace_budget)
    assert actual.to_dict() == expected.to_dict()


@pytest.mark.skipif(not (LEAN.exists() and RUST.exists()), reason="backends have not been built")
@pytest.mark.parametrize("profiles,formula", [
    (("closure@0",), Reach("star", Named("step"), Const("x"), Const("x"))),
    (("closure@0", "nary@0"), Atom("triple", (Const("x"), Const("y"), Const("x")))),
])
def test_traced_profile_cases_match_python(profiles, formula):
    from tests.probe_matrix import model_wire, raw_environment
    env = Environment(raw_environment(profiles))
    model = FiniteModel.from_dict(env, model_wire(env))
    expected = python_oracle.evaluate(env, formula, model, trace=True, max_evaluations=100)
    assert evaluate(env, formula, model, trace=True, max_evaluations=100).to_dict() == expected.to_dict()


@pytest.mark.skipif(not (LEAN.exists() and RUST.exists()), reason="backends have not been built")
@pytest.mark.parametrize("premises,conclusion,budget", [
    ((Top(),), Bottom(), 2), ((Bottom(),), Top(), 2),
    ((Top(),), Bottom(), 1),
])
def test_countermodel_schema_identity_and_budget(fixture, premises, conclusion, budget):
    env, model = fixture
    expected = python_oracle.check_countermodel(env, premises, conclusion, model, max_evaluations=budget)
    assert check_countermodel(env, premises, conclusion, model, max_evaluations=budget) == expected


def _order_search_env():
    from ve.profiles import SPEC_REVISION
    return Environment({"language": "ve.core@0.2", "profiles": ["order@0", "relational-fol@0"],
                        "spec_revision": SPEC_REVISION, "vocabulary": {
        "sorts": {"item": {"description": "item"}},
        "predicates": {"base": {"arguments": ["item"], "description": "base"},
                       "score": {"arguments": ["item", "$int"], "description": "score"}},
        "constants": {"x": {"sort": "item", "description": "x"},
                      "n": {"sort": "$int", "description": "n"}}}})


@pytest.mark.skipif(not (LEAN.exists() and RUST.exists()), reason="backends have not been built")
@pytest.mark.parametrize("budget", [0, 1, 2, 1000])
def test_order_countermodel_check_matches_python(budget):
    from ve.ast import Le, Num
    env = _order_search_env()
    model = FiniteModel.from_dict(env, {"complete": True, "domains": {"item": ["i"]},
                                        "constants": {"x": "i", "n": "2"},
                                        "relations": {"base": [["i"]], "score": [["i", "3"]]}})
    args = (env, (Le(Const("n"), Num(2)), Unary("base", Const("x"))),
            Binary("score", Const("x"), Const("n")), model)
    expected = python_oracle.check_countermodel(*args, max_evaluations=budget)
    assert check_countermodel(*args, max_evaluations=budget) == expected


@pytest.mark.skipif(not (LEAN.exists() and RUST.exists()), reason="backends have not been built")
@pytest.mark.parametrize("layers", [("definitions@0",), ("data@0",), ("data@0", "definitions@0")])
def test_core_family_layers_match_python(layers):
    """Definitions and data flags on closure@0 + nary@0 through the Lean core route."""
    from tests.probe_matrix import model_wire, raw_environment
    from ve.errors import InvalidModel
    env = Environment(raw_environment(("closure@0", "nary@0", *layers)))
    data = model_wire(env)
    model = FiniteModel.from_dict(env, data)
    formula = (Unary("derived", Const("x")) if "definitions@0" in layers
               else Binary("edge", Const("x"), Const("x")))
    assert background(env)
    assert (evaluate(env, formula, model, trace=False).to_dict()
            == python_oracle.evaluate(env, formula, model, trace=False).to_dict())
    assert (check_countermodel(env, (formula,), Bottom(), model)
            == python_oracle.check_countermodel(env, (formula,), Bottom(), model))
    if "data@0" in layers:
        from ve.ast import formula_to_data
        from ve.backends.relay import decide as run
        bad = {**data, "relations": {**data["relations"], "edge": [["i", "i"], ["i", "j"]]}}
        with pytest.raises(InvalidModel) as caught:
            run("route", [{"id": "bad", "kind": "evaluate", "environment": env.to_dict(),
                           "model": bad, "ast": [formula_to_data(env, formula)]}])
        assert caught.value.generator == "flags"


@pytest.mark.skipif(not LEAN.exists(), reason="Lean service has not been built")
@pytest.mark.parametrize("profiles", [(), ("data@0",), ("definitions@0",), ("norms@0",),
    ("closure@0",), ("closure@0", "nary@0"), ("closure@0", "nary@0", "definitions@0"), ("order@0",)])
def test_certificate_replay(profiles):
    """Lean replays; the public budget is charged one step per trace node: a budget of 0 is
    `ResourceLimit`, never a verdict, and a certificate for another conclusion is refused."""
    from tests.probe_matrix import raw_environment, semantic_formula
    from ve.entailment import check_entailment_certificate, prove_entailment
    env = Environment(raw_environment(profiles))
    formula = semantic_formula(env)
    proof = prove_entailment(env, (formula,), formula, max_steps=1000)
    assert proof.status == "Found"
    stale = {**proof.certificate, "conclusion_meaning_id": "0" * 64}
    outcomes = [(check.valid, check.status) for check in (
        check_entailment_certificate(env, (formula,), formula, certificate, max_steps=budget)
        for certificate, budget in ((proof.certificate, 1000), (proof.certificate, 0), (stale, 1000)))]
    assert outcomes == [(True, "Valid"), (False, "ResourceLimit"), (False, "InvalidCertificate")]


@pytest.mark.skipif(not LEAN.exists(), reason="Lean service has not been built")
def test_a_cached_model_encoding_never_stands_for_another_model(fixture):
    """Lean-first batch 18: a model's case encoding is written once per model object. A second object that
    claims the first one's identities with other contents is encoded from its own contents, so Lean refuses
    the claim, however warm the cache is."""
    from dataclasses import replace
    from ve.errors import InvalidModel
    from ve.backends.lean_runner import encoded_model
    env, model = fixture
    assert evaluate(env, Unary("ready", Const("alpha")), model, trace=False).value is True
    other = FiniteModel.from_dict(env, {**model.to_dict(), "relations": {"ready": [], "knows": [["a", "b"]]}})
    forged = replace(other, model_id=model.model_id)
    assert encoded_model(forged) is not encoded_model(model) and dict(encoded_model(forged)) == other.to_dict()
    with pytest.raises(InvalidModel, match="does not match its contents"):
        evaluate(env, Unary("ready", Const("alpha")), forged, trace=False)
    with pytest.raises(InvalidModel, match="does not match its contents"):
        check_countermodel(env, (), Unary("ready", Const("alpha")), forged)
