"""Backend integration on the public evaluation and Background signatures."""
from __future__ import annotations

from pathlib import Path
import json

import pytest

from conformance.p0 import environment
from ve import Environment, FiniteModel
from ve.ast import (And, Atom, Binary, Bottom, Const, Eq, Exists, Forall, Implies,
                    Named, Not, Or, Reach, Top, Unary, Var)
from ve.background import background, dependency_order
from ve.evaluate import evaluate
from ve.errors import VEError
from ve.backends.lean_service import CheckerUnavailable
from ve.search import check_countermodel, find_countermodel, find_distinguishing_model
from ve.admission import admit_document
from tests.lean_wording import lean_wording

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean/.lake/build/bin/ve_service"
RUST = ROOT / "rust/target/release/ve"


@pytest.mark.skipif(not LEAN.exists(), reason="Lean service has not been built")
def test_lean_admission_preserves_report_and_identity(monkeypatch):
    from conformance.p0 import admission_cases
    case = next(c for c in admission_cases() if c["id"] == "bridge-background")
    monkeypatch.setenv("VE_AUTHORITY", "python")
    expected = admit_document(case["environment"], case["document"])
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    assert admit_document(case["environment"], case["document"]) == expected


@pytest.mark.skipif(not LEAN.exists(), reason="Lean service has not been built")
def test_lean_norms_admission_with_data_flags_matches_python(monkeypatch):
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
    outcomes = {}
    for authority in ("python", "lean"):
        monkeypatch.setenv("VE_AUTHORITY", authority)
        row = [admit_document(env, document)]
        for e, d in ((env, rejected), (closure, document)):
            try:
                admit_document(e, d)
            except VEError as error:
                row.append((error.code, str(error)))
        outcomes[authority] = row
    assert outcomes["python"][0]["admitted"] and len(outcomes["python"]) == 3
    assert outcomes["lean"] == outcomes["python"][:1] + [lean_wording(*row) for row in outcomes["python"][1:]]


@pytest.mark.skipif(not (LEAN.exists() and RUST.exists()), reason="backends have not been built")
def test_budgeted_order_evaluation_matches_python(monkeypatch):
    from tests.probe_matrix import model_wire, raw_environment
    from ve.ast import Le, Num
    env = Environment(raw_environment(("order@0",)))
    model = FiniteModel.from_dict(env, model_wire(env))
    formula = Le(Num(0), Num(1))
    monkeypatch.setenv("VE_AUTHORITY", "python")
    expected = [evaluate(env, formula, model, trace=False, max_evaluations=n).to_dict()
                for n in (0, 1, 2)]
    for authority in ("rust-experimental", "lean"):
        monkeypatch.setenv("VE_AUTHORITY", authority)
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
def test_traced_order_evaluation_matches_python(monkeypatch, formula, budget, trace_budget):
    from tests.probe_matrix import model_wire, raw_environment
    from ve.ast import Le, Num
    env = Environment(raw_environment(("order@0",)))
    model = FiniteModel.from_dict(env, model_wire(env))
    cases = (formula, Le(Num(0), Num(1)))
    monkeypatch.setenv("VE_AUTHORITY", "python")
    expected = [evaluate(env, f, model, trace=True, max_evaluations=budget,
                         max_trace_nodes=trace_budget).to_dict() for f in cases]
    for authority in ("rust-experimental", "lean"):
        monkeypatch.setenv("VE_AUTHORITY", authority)
        assert [evaluate(env, f, model, trace=True, max_evaluations=budget,
                         max_trace_nodes=trace_budget).to_dict() for f in cases] == expected


@pytest.mark.skipif(not (LEAN.exists() and RUST.exists()), reason="backends have not been built")
@pytest.mark.parametrize("semantic", [False, True])
def test_nonvacuity_search_matches_python(monkeypatch, semantic):
    from tests.probe_matrix import raw_environment
    raw = raw_environment(())
    raw["vocabulary"]["constants"] = {}
    env = Environment(raw)
    guard = Forall("item", Or(Not(Unary("base", Var(0))), Top()))

    def search():
        return find_countermodel(env, (), Bottom(), min_domain_size=1,
            max_domain_size=1, max_models=4, nonvacuous_for=guard,
            semantic_nonvacuity=semantic)

    monkeypatch.setenv("VE_AUTHORITY", "python")
    expected = search().to_dict()
    for authority in ("rust-experimental", "lean"):
        monkeypatch.setenv("VE_AUTHORITY", authority)
        assert search().to_dict() == expected


@pytest.mark.skipif(not (LEAN.exists() and RUST.exists()), reason="backends have not been built")
def test_nonvacuity_distinguishing_matches_python(monkeypatch):
    from tests.probe_matrix import raw_environment
    raw = raw_environment(())
    raw["vocabulary"]["constants"] = {}
    env = Environment(raw)
    guard = Forall("item", Or(Not(Unary("base", Var(0))), Top()))

    def search():
        return find_distinguishing_model(env, Exists("item", Unary("base", Var(0))),
            Bottom(), min_domain_size=1, max_domain_size=1, max_models=4,
            nonvacuous_for=guard, semantic_nonvacuity=True)

    monkeypatch.setenv("VE_AUTHORITY", "python")
    expected = search().to_dict()
    for authority in ("rust-experimental", "lean"):
        monkeypatch.setenv("VE_AUTHORITY", authority)
        assert search().to_dict() == expected


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


@pytest.mark.skipif(not LEAN.exists(), reason="Lean service has not been built")
def test_lean_background_preserves_named_premises(monkeypatch, fixture):
    env, _ = fixture
    monkeypatch.setenv("VE_AUTHORITY", "python")
    expected = background(env)
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    assert background(env) == expected


@pytest.mark.skipif(not LEAN.exists(), reason="Lean service has not been built")
@pytest.mark.parametrize("dependencies", [
    {}, {"b": {"a"}, "a": set()},
    {"a": {"outside"}, "b": set(), "c": {"a", "b"}},
])
def test_lean_dependency_order_preserves_signature(monkeypatch, dependencies):
    monkeypatch.setenv("VE_AUTHORITY", "python")
    expected = dependency_order(dependencies)
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    assert dependency_order(dependencies) == expected


@pytest.mark.skipif(not LEAN.exists(), reason="Lean service has not been built")
def test_lean_dependency_cycle_keeps_diagnostic_code(monkeypatch):
    monkeypatch.setenv("VE_AUTHORITY", "python")
    with pytest.raises(VEError) as original:
        dependency_order({"a": {"b"}, "b": {"a"}})
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    with pytest.raises(VEError) as candidate:
        dependency_order({"a": {"b"}, "b": {"a"}})
    assert candidate.value.code == original.value.code


@pytest.mark.skipif(not (LEAN.exists() and RUST.exists()), reason="backends have not been built")
@pytest.mark.parametrize("formula,budget", [(Top(), 1), (Bottom(), 1),
                                           (And(Top(), Top()), 2), (Top(), 0)])
def test_budgeted_evaluation_matches_python(monkeypatch, fixture, formula, budget):
    env, model = fixture
    monkeypatch.setenv("VE_AUTHORITY", "python")
    expected = evaluate(env, formula, model, trace=False, max_evaluations=budget)
    for authority in ("rust-experimental", "lean"):
        monkeypatch.setenv("VE_AUTHORITY", authority)
        assert evaluate(env, formula, model, trace=False,
                        max_evaluations=budget).to_dict() == expected.to_dict()


@pytest.mark.skipif(not (LEAN.exists() and RUST.exists()), reason="backends have not been built")
def test_shadow_evaluation_has_no_divergence(monkeypatch, fixture, tmp_path):
    env, model = fixture
    log = tmp_path / "shadow.jsonl"
    monkeypatch.setenv("VE_SHADOW_LOG", str(log))
    monkeypatch.setenv("VE_AUTHORITY", "shadow")
    assert evaluate(env, Top(), model, trace=False).value is True
    assert not log.exists()


def test_missing_rust_binary_fails_closed_and_shadow_records_it(monkeypatch, fixture, tmp_path):
    env, model = fixture
    monkeypatch.setenv("VE_RUST_JSONL", str(tmp_path / "missing-ve"))
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    with pytest.raises(CheckerUnavailable):
        evaluate(env, Top(), model, trace=True)
    log = tmp_path / "shadow.jsonl"
    monkeypatch.setenv("VE_SHADOW_LOG", str(log))
    monkeypatch.setenv("VE_AUTHORITY", "shadow")
    assert evaluate(env, Top(), model, trace=True).value is True
    assert json.loads(log.read_text())["lean"]["code"] == "CheckerUnavailable"


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
def test_traced_evaluation_matches_python(monkeypatch, fixture, formula, budget, trace_budget):
    env, model = fixture
    monkeypatch.setenv("VE_AUTHORITY", "python")
    expected = evaluate(env, formula, model, trace=True,
                        max_evaluations=budget, max_trace_nodes=trace_budget)
    for authority in ("rust-experimental", "lean"):
        monkeypatch.setenv("VE_AUTHORITY", authority)
        actual = evaluate(env, formula, model, trace=True,
                          max_evaluations=budget, max_trace_nodes=trace_budget)
        assert actual.to_dict() == expected.to_dict()


@pytest.mark.skipif(not (LEAN.exists() and RUST.exists()), reason="backends have not been built")
@pytest.mark.parametrize("profiles,formula", [
    (("closure@0",), Reach("star", Named("step"), Const("x"), Const("x"))),
    (("closure@0", "nary@0"), Atom("triple", (Const("x"), Const("y"), Const("x")))),
])
def test_traced_profile_cases_match_python(monkeypatch, profiles, formula):
    from tests.probe_matrix import model_wire, raw_environment
    env = Environment(raw_environment(profiles))
    model = FiniteModel.from_dict(env, model_wire(env))
    monkeypatch.setenv("VE_AUTHORITY", "python")
    expected = evaluate(env, formula, model, trace=True, max_evaluations=100)
    for authority in ("rust-experimental", "lean"):
        monkeypatch.setenv("VE_AUTHORITY", authority)
        assert evaluate(env, formula, model, trace=True,
                        max_evaluations=100).to_dict() == expected.to_dict()


@pytest.mark.skipif(not (LEAN.exists() and RUST.exists()), reason="backends have not been built")
@pytest.mark.parametrize("premises,conclusion,budget", [
    ((Top(),), Bottom(), 2), ((Bottom(),), Top(), 2),
    ((Top(),), Bottom(), 1),
])
def test_countermodel_schema_identity_and_budget(monkeypatch, fixture, premises, conclusion, budget):
    env, model = fixture
    monkeypatch.setenv("VE_AUTHORITY", "python")
    expected = check_countermodel(env, premises, conclusion, model, max_evaluations=budget)
    for authority in ("rust-experimental", "lean"):
        monkeypatch.setenv("VE_AUTHORITY", authority)
        assert check_countermodel(env, premises, conclusion, model,
                                  max_evaluations=budget) == expected


@pytest.mark.skipif(not (LEAN.exists() and RUST.exists()), reason="backends have not been built")
@pytest.mark.parametrize("options", [
    {}, {"min_domain_size": 1}, {"nonempty_domains": True},
    {"max_models": 0}, {"max_evaluations": 0},
    {"max_models": 0, "max_evaluations": 0},
])
def test_search_adapter_preserves_witness_and_budgets(monkeypatch, options):
    wire = environment()
    wire["vocabulary"]["sorts"]["person"] = {"description": "A person."}
    wire["vocabulary"]["constants"] = {}
    env = Environment(wire)
    monkeypatch.setenv("VE_AUTHORITY", "python")
    expected = find_countermodel(env, (), Bottom(), max_domain_size=1, **options)
    for authority in ("rust-experimental", "lean"):
        monkeypatch.setenv("VE_AUTHORITY", authority)
        assert find_countermodel(env, (), Bottom(), max_domain_size=1,
                                 **options).to_dict() == expected.to_dict()


@pytest.mark.skipif(not (LEAN.exists() and RUST.exists()), reason="backends have not been built")
@pytest.mark.parametrize("a,b,options", [
    (Top(), Bottom(), {}), (Top(), Top(), {}),
    (Top(), Bottom(), {"nonempty_domains": True}),
    (Top(), Bottom(), {"max_models": 0}),
    (Top(), Bottom(), {"max_evaluations": 1}),
])
def test_distinguishing_adapter_preserves_witness_and_counts(monkeypatch, a, b, options):
    wire = environment()
    wire["vocabulary"]["sorts"]["person"] = {"description": "A person."}
    wire["vocabulary"]["constants"] = {}
    env = Environment(wire)
    monkeypatch.setenv("VE_AUTHORITY", "python")
    expected = find_distinguishing_model(env, a, b, max_domain_size=1, **options)
    for authority in ("rust-experimental", "lean"):
        monkeypatch.setenv("VE_AUTHORITY", authority)
        assert find_distinguishing_model(env, a, b, max_domain_size=1,
                                         **options).to_dict() == expected.to_dict()


@pytest.mark.skipif(not (LEAN.exists() and RUST.exists()), reason="backends have not been built")
def test_nary_search_matches_stage0_probe(monkeypatch):
    from tests.probe_matrix import model_wire, operation, raw_environment
    env = Environment(raw_environment(("closure@0", "nary@0")))
    model = FiniteModel.from_dict(env, model_wire(env))
    monkeypatch.setenv("VE_AUTHORITY", "python")
    expected = operation("countermodel_search", "positive", env, model)().to_dict()
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    assert operation("countermodel_search", "positive", env, model)().to_dict() == expected


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
@pytest.mark.parametrize("premises,conclusion,options", [
    ((), "bottom", {}),
    (("le n 2",), "score", {}),
    (("le n 2",), "score", {"max_models": 3}),
    (("score",), "lt", {"max_domain_size": 2, "min_domain_size": 1}),
    (("forall",), "bottom", {"nonempty_domains": True, "nonvacuous_for": "forall"}),
    (("forall",), "bottom", {"nonvacuous_for": "forall", "semantic_nonvacuity": True,
                             "max_models": 20}),
    (("le n 2",), "score", {"max_evaluations": 3}),
])
def test_order_search_matches_python(monkeypatch, premises, conclusion, options):
    """Rust order search streams Python's candidate models with its counters."""
    from ve.ast import Le, Lt, Num
    env = _order_search_env()
    formulas = {"bottom": Bottom(), "le n 2": Le(Const("n"), Num(2)),
                "score": Binary("score", Const("x"), Const("n")),
                "lt": Lt(Const("n"), Num(-1)),
                "forall": Forall("item", Implies(Unary("base", Var(0)),
                                                 Binary("score", Var(0), Num(1))))}
    options = {k: formulas[v] if k == "nonvacuous_for" else v for k, v in options.items()}
    args = (env, tuple(formulas[p] for p in premises), formulas[conclusion])
    monkeypatch.setenv("VE_AUTHORITY", "python")
    expected = find_countermodel(*args, **options).to_dict()
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    assert find_countermodel(*args, **options).to_dict() == expected
    a, b = (formulas[premises[0]] if premises else Top()), formulas[conclusion]
    monkeypatch.setenv("VE_AUTHORITY", "python")
    expected = find_distinguishing_model(env, a, b, **options).to_dict()
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    assert find_distinguishing_model(env, a, b, **options).to_dict() == expected


@pytest.mark.skipif(not (LEAN.exists() and RUST.exists()), reason="backends have not been built")
@pytest.mark.parametrize("budget", [0, 1, 2, 1000])
def test_order_countermodel_check_matches_python(monkeypatch, budget):
    from ve.ast import Le, Num
    env = _order_search_env()
    model = FiniteModel.from_dict(env, {"complete": True, "domains": {"item": ["i"]},
                                        "constants": {"x": "i", "n": "2"},
                                        "relations": {"base": [["i"]], "score": [["i", "3"]]}})
    args = (env, (Le(Const("n"), Num(2)), Unary("base", Const("x"))),
            Binary("score", Const("x"), Const("n")), model)
    monkeypatch.setenv("VE_AUTHORITY", "python")
    expected = check_countermodel(*args, max_evaluations=budget)
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    assert check_countermodel(*args, max_evaluations=budget) == expected


@pytest.mark.skipif(not (LEAN.exists() and RUST.exists()), reason="backends have not been built")
@pytest.mark.parametrize("layers", [("definitions@0",), ("data@0",), ("data@0", "definitions@0")])
def test_core_family_layers_match_python(monkeypatch, layers):
    """Definitions and data flags on closure@0 + nary@0 through the Lean core route."""
    from tests.probe_matrix import model_wire, raw_environment
    from ve.errors import InvalidModel
    env = Environment(raw_environment(("closure@0", "nary@0", *layers)))
    data = model_wire(env)
    model = FiniteModel.from_dict(env, data)
    formula = (Unary("derived", Const("x")) if "definitions@0" in layers
               else Binary("edge", Const("x"), Const("x")))
    results = {}
    for authority in ("python", "lean"):
        monkeypatch.setenv("VE_AUTHORITY", authority)
        results[authority] = (
            [(p.generator, p.formula) for p in background(env)],
            evaluate(env, formula, model, trace=False).to_dict(),
            check_countermodel(env, (formula,), Bottom(), model),
            find_countermodel(env, (), formula, max_domain_size=2, max_models=50).to_dict())
    assert results["lean"] == results["python"]
    if "data@0" in layers:
        from ve.ast import formula_to_data
        from ve.backends.relay import decide as run
        bad = {**data, "relations": {**data["relations"], "edge": [["i", "i"], ["i", "j"]]}}
        with pytest.raises(InvalidModel) as caught:
            run("route", [{"id": "bad", "kind": "evaluate", "environment": env.to_dict(),
                           "model": bad, "ast": [formula_to_data(env, formula)]}])
        assert caught.value.generator == "flags"


@pytest.mark.skipif(not (LEAN.exists() and RUST.exists()), reason="backends have not been built")
@pytest.mark.parametrize("profiles", [(), ("data@0",), ("definitions@0",), ("data@0", "definitions@0"),
    ("closure@0",), ("closure@0", "nary@0", "data@0"), ("norms@0",)])
def test_search_streams_python_model_order(monkeypatch, profiles):
    """Every model budget stops Rust's stream where Python's stops: same order and counts."""
    from tests.probe_matrix import raw_environment, semantic_formula
    env = Environment(raw_environment(profiles))
    late = And(Exists("item", Unary("base", Var(0))), semantic_formula(env))
    for max_models in range(0, 7):
        options = {"max_domain_size": 2, "max_models": max_models}
        monkeypatch.setenv("VE_AUTHORITY", "python")
        expected = (find_countermodel(env, (late,), Bottom(), **options).to_dict(),
                    find_distinguishing_model(env, Top(), late, **options).to_dict())
        monkeypatch.setenv("VE_AUTHORITY", "lean")
        assert (find_countermodel(env, (late,), Bottom(), **options).to_dict(),
                find_distinguishing_model(env, Top(), late, **options).to_dict()) == expected


@pytest.mark.skipif(not LEAN.exists(), reason="Lean service has not been built")
@pytest.mark.parametrize("profiles", [(), ("data@0",), ("definitions@0",), ("norms@0",),
    ("closure@0",), ("closure@0", "nary@0"), ("closure@0", "nary@0", "definitions@0"), ("order@0",)])
def test_certificate_replay_matches_python(monkeypatch, profiles):
    """Lean replays; the public budget is charged one step per trace node."""
    from tests.probe_matrix import raw_environment, semantic_formula
    from ve.entailment import check_entailment_certificate, prove_entailment
    env = Environment(raw_environment(profiles))
    formula = semantic_formula(env)
    proof = prove_entailment(env, (formula,), formula, max_steps=1000)
    assert proof.status == "Found"
    stale = {**proof.certificate, "conclusion_meaning_id": "0" * 64}
    for certificate, budget in ((proof.certificate, 1000), (proof.certificate, 0), (stale, 1000)):
        monkeypatch.setenv("VE_AUTHORITY", "python")
        expected = check_entailment_certificate(env, (formula,), formula, certificate, max_steps=budget)
        monkeypatch.setenv("VE_AUTHORITY", "lean")
        assert check_entailment_certificate(env, (formula,), formula, certificate,
                                            max_steps=budget) == expected
