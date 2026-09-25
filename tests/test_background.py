from dataclasses import replace
from types import MappingProxyType

import pytest

from conformance.p0 import environment
from ve.argument import (ArgumentGraph, Claim, Deduction, _checker_build,
                         check_argument, outstanding_obligations)
from ve.ast import Bottom, Const, Eq, Not, Top
from ve.background import HOOKS, background, dependency_order, validate_background
from ve.check import check
from ve.entailment import check_entailment_certificate, prove_entailment
from ve.environment import Environment
from ve.equivalence import compare
from ve.errors import InvalidModel, ResourceLimit, VEError
from ve.evaluate import evaluate
from ve.model import FiniteModel
from ve.search import check_countermodel, find_countermodel, find_distinguishing_model


def setup():
    env = Environment(environment())
    valid = FiniteModel.from_dict(env, {"complete": True, "domains": {"$string": ["a", "b"]},
                                     "constants": {"alpha": "a", "beta": "b"}, "relations": {}})
    alias = replace(valid, constants=MappingProxyType({"alpha": "a", "beta": "a"}))
    return env, valid, alias


def test_literal_background_is_derived_and_identity_bound():
    env, valid, alias = setup()
    assert tuple((p.generator, p.formula) for p in background(env)) == (
        ("literals", Not(Eq(Const("alpha"), Const("beta")))),)
    with pytest.raises(InvalidModel) as exc:
        validate_background(env, alias)
    assert exc.value.generator == "literals"
    with pytest.raises(InvalidModel) as exc:
        FiniteModel.from_dict(env, alias.to_dict())
    assert exc.value.generator == "literals"
    changed = environment()
    changed["vocabulary"]["constants"]["gamma"] = {"sort": "$string", "description": "Third."}
    assert Environment(changed).environment_id != env.environment_id
    assert list(HOOKS) == ["flags", "definitions", "literals", "profile"]


def test_all_public_model_sites_reject_alias_and_search_valid_models():
    env, valid, alias = setup()
    for call in (lambda: evaluate(env, Top(), alias),
                 lambda: check_countermodel(env, (), Bottom(), alias),
                 lambda: check(env, "true.\n", alias)):
        with pytest.raises(InvalidModel) as exc:
            call()
        assert exc.value.generator == "literals"
    result = find_countermodel(env, (), Bottom(), max_domain_size=2, max_models=10)
    assert result.status == "Found" and result.model.constants["alpha"] != result.model.constants["beta"]
    found = find_distinguishing_model(env, Eq(Const("alpha"), Const("beta")), Top(),
                                      max_domain_size=2, max_models=10)
    assert found.status == "Found"
    assert found.model.constants["alpha"] != found.model.constants["beta"]
    assert compare(env, Eq(Const("alpha"), Const("beta")), Bottom()).status == "EQUIVALENT"
    assert evaluate(env, Not(Eq(Const("alpha"), Const("beta"))), valid).value


def test_proofs_and_argument_replay_include_background():
    env, _, alias = setup()
    goal = Not(Eq(Const("alpha"), Const("beta")))
    proof = prove_entailment(env, (), goal)
    assert proof.status == "Found"
    assert check_entailment_certificate(env, (), goal, proof.certificate).valid
    claim = Claim.create(env, "root", "true.\n")
    graph = ArgumentGraph(env, (claim,), (Deduction("edge", (), "root", countermodels=(alias,)),), "root")
    result = check_argument(graph, search=False)
    assert result.status == "InvalidInput"
    assert result.errors[0]["generator"] == "literals"


def test_claim_labels_bind_new_graphs_without_moving_default_wire():
    env, _, _ = setup()
    plain = Claim.create(env, "root", "true.\n")
    labelled = Claim.create(env, "root", "true.\n", label="bridge:accepts(alice,u1)")
    assert "label" not in plain.to_dict(env)
    assert labelled.to_dict(env)["label"] == "bridge:accepts(alice,u1)"
    assert labelled.claim_id != plain.claim_id
    assert Claim.from_dict(env, labelled.to_dict(env)) == labelled
    assert ArgumentGraph(env, (plain,), (), "root").graph_id != ArgumentGraph(
        env, (labelled,), (), "root").graph_id
    report = check_argument(ArgumentGraph(env, (labelled,), (), "root"))
    assert report.composition["assumptions"][0]["label"] == "bridge:accepts(alice,u1)"
    assert {x["label"] for x in report.composition["assumptions"][1:]} == {"background:literals"}
    display = outstanding_obligations(ArgumentGraph(env, (labelled,), (), "root"), report)
    assert display["assumptions"][-1]["label"] == "background:literals"


def test_one_dependency_dag():
    assert dependency_order({"violation": {"required"}, "required": {"exception"},
                             "exception": set()}) == ("exception", "required", "violation")
    assert dependency_order({"a": {"c"}, "b": set(), "c": set()}) == ("b", "c", "a")
    with pytest.raises(VEError, match="DependencyCycle: a, b"):
        dependency_order({"a": {"b"}, "b": {"a"}})
    with pytest.raises(ResourceLimit, match="dependency graph size"):
        dependency_order({str(i): set() for i in range(257)})


def test_checker_build_covers_all_python_modules(monkeypatch):
    from pathlib import Path
    root = Path(__file__).resolve().parents[1] / "ve"
    modules = {path.relative_to(root).as_posix() for path in root.rglob("*.py")}
    assert {"order.py", "background.py", "profiles.py", "surface/registry.py",
            "vacuity.py"} <= modules
    before = _checker_build()
    original = Path.read_bytes
    def changed(path):
        data = original(path)
        return data + b"\n" if path == root / "background.py" else data
    monkeypatch.setattr(Path, "read_bytes", changed)
    assert _checker_build() != before
