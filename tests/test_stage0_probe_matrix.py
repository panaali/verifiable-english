"""Regressions for rejected Stage 0 baseline probes."""
import json
import pytest

from tests import probe_matrix as probe
from ve import Environment, FiniteModel
from ve.ast import Atom, Const
from ve.evaluate import evaluate
from ve.environment import (LANGUAGE, PROFILE, SPEC_REVISION,
                            CLOSURE_LANGUAGE, CLOSURE_PROFILES, CLOSURE_REVISION)


def test_legacy_environment_rejection_reaches_environment():
    raw = probe.raw_environment(())
    raw.update(language=LANGUAGE, spec_revision=SPEC_REVISION)
    raw.pop("profiles")
    raw["profile"] = PROFILE
    env = Environment(raw)
    model = FiniteModel.from_dict(env, probe.model_wire(env))
    assert probe.outcome(probe.operation("parse_accept", "positive", env, model))["cell"] == "S"
    result = probe.outcome(probe.operation("environment_validation", "rejection", env, model))
    assert result["cell"] == "R" and result["status"] == "UnknownSymbol"


def test_unexpected_probe_exception_fails_generation():
    with pytest.raises(KeyError):
        probe.outcome(lambda: {}["missing"])


def test_legacy_closure_without_step_uses_supported_positive():
    raw = probe.raw_environment(())
    raw.update(language=CLOSURE_LANGUAGE, spec_revision=CLOSURE_REVISION,
               profiles=list(CLOSURE_PROFILES))
    env = Environment(raw)
    model = FiniteModel.from_dict(env, probe.model_wire(env))
    assert probe.outcome(probe.operation("parse_accept", "positive", env, model))["cell"] == "S"


def test_search_rejections_are_semantic_diagnostics():
    env = Environment(probe.raw_environment(()))
    model = FiniteModel.from_dict(env, probe.model_wire(env))
    for name in probe.OPERATIONS:
        if name.startswith("countermodel_search") or name == "distinguishing_model":
            result = probe.outcome(probe.operation(name, "rejection", env, model))
            assert result["cell"] == "R" and result["status"] == "UnknownSymbol"


def test_reading_choices_options_and_replay_have_discriminating_evidence():
    cases = probe.feature_baselines()
    assert cases["readings:all_disjunction"]["status"] == "ALL"
    some = cases["readings:some_fixed_choice"]["output"]
    assert some["verdict"] == "SOME"
    assert some["proof"]["choice"] == ["readings:s@2:0"]
    assert some["countermodel"]["choice"] == ["readings:s@2:1"]
    assert cases["readings:none_shared_model"]["status"] == "NONE"
    assert cases["search:min_domain_size_0"]["output"]["model"]["domains"]["item"] == []
    assert len(cases["search:min_domain_size_1"]["output"]["model"]["domains"]["item"]) == 1
    assert cases["search:syntactic_nonvacuity"]["output"]["models_checked"] == 1
    assert cases["search:semantic_nonvacuity"]["output"]["models_checked"] == 2
    for name in ("replay:closure_transitivity", "replay:closure_induction", "replay:order_farkas",
                 "replay:nary_instantiation"):
        assert cases[name]["output"]["valid"] is True


def test_baseline_projection_only_drops_python_build_record_ids():
    source = {"checker_build": "machine-specific", "record_id": "derived",
              "environment_id": "semantic", "nested": [{"record_id": "derived", "status": "Valid"}]}
    assert probe.baseline_projection(source) == {"environment_id": "semantic", "nested": [{"status": "Valid"}]}
    assert set(probe.GAP_ASSIGNMENTS) == set(probe.OPERATIONS)


def test_graph_projection_survives_python_build_string_change(monkeypatch):
    original = probe.baseline_projection(probe.graph_baselines())
    monkeypatch.setattr(probe.sys, "version", probe.sys.version.split()[0] + " (other build)")
    assert probe.baseline_projection(probe.graph_baselines()) == original


def test_frozen_baseline_keeps_rejection_codes_and_complete_graph_evidence():
    data = json.loads((probe.OUT / "python.json").read_text())
    assert data["runtime_sha256"] == probe.runtime_sha256()
    assert not any(row["status"] in {"KeyError", "ValueError"} for row in data["cells"])
    assert {data["feature_probes"][f"readings:{name}"]["status"]
            for name in ("all_disjunction", "some_fixed_choice", "none_shared_model")} == {
                "ALL", "SOME", "NONE"}
    assert "checker_build" not in json.dumps(data["graph_probes"])
    boundaries = data["budget_boundaries"]
    assert boundaries["MAX_TABLEAU_DEPTH_replay"]["at"]["status"] == "Valid"
    assert boundaries["MAX_TABLEAU_DEPTH_replay"]["over"]["status"] == "_Budget"
    assert boundaries["MAX_TABLEAU_DEPTH_search"]["at"]["status"] == "Found"
    assert boundaries["MAX_TABLEAU_DEPTH_search"]["over"]["status"] == "Cutoff"
    assert boundaries["order_search_depth"]["at"]["status"] == "Found"
    assert boundaries["order_search_depth"]["over"]["status"] == "Cutoff"
    probe.test_amended_graph_baselines()


@pytest.mark.parametrize("profiles,tag", [
    (("data@0",), "binary"), (("definitions@0",), "unary"),
    (("closure@0",), "reach"), (("order@0",), "le"),
    (("closure@0", "nary@0"), "atom"),
])
def test_profile_positive_uses_its_semantics(profiles, tag):
    env = Environment(probe.raw_environment(profiles))
    model = FiniteModel.from_dict(env, probe.model_wire(env))
    assert probe.formula_to_data(env, probe.semantic_formula(env))[0] == tag
    for name in ("parse_accept", "typing", "evaluate", "countermodel_check"):
        result = probe.outcome(probe.operation(name, "positive", env, model))
        assert result["cell"] == "S", (profiles, name, result)


def test_nary_probe_distinguishes_argument_positions():
    env = Environment(probe.raw_environment(("closure@0", "nary@0")))
    model = FiniteModel.from_dict(env, probe.model_wire(env))
    positive = probe.semantic_formula(env)
    reversed_atom = Atom("triple", (Const("y"), Const("x"), Const("x")))
    assert evaluate(env, positive, model).value is True
    assert evaluate(env, reversed_atom, model).value is False
    env_with_data = Environment(probe.raw_environment(("closure@0", "nary@0", "data@0")))
    model_with_data = FiniteModel.from_dict(env_with_data, probe.model_wire(env_with_data))
    result = probe.outcome(probe.operation("countermodel_search", "positive", env_with_data, model_with_data))
    assert result["status"] == "Found"
