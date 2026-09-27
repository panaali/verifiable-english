"""Regressions for rejected Stage 0 baseline probes."""
import pytest

from tests import probe_matrix as probe
from ve import Environment, FiniteModel
from ve.environment import LANGUAGE, PROFILE, SPEC_REVISION


def test_legacy_environment_rejection_reaches_environment():
    raw = probe.raw_environment(())
    raw.update(language=LANGUAGE, spec_revision=SPEC_REVISION)
    raw.pop("profiles")
    raw["profile"] = PROFILE
    env = Environment(raw)
    model = FiniteModel.from_dict(env, probe.model_wire(env))
    result = probe.outcome(probe.operation("environment_validation", "rejection", env, model))
    assert result["cell"] == "R" and result["status"] == "UnknownSymbol"


def test_unexpected_probe_exception_fails_generation():
    with pytest.raises(KeyError):
        probe.outcome(lambda: {}["missing"])


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
    for name in ("replay:closure_transitivity", "replay:closure_induction", "replay:order_farkas"):
        assert cases[name]["output"]["valid"] is True


def test_baseline_projection_only_drops_python_build_record_ids():
    source = {"checker_build": "machine-specific", "record_id": "derived",
              "environment_id": "semantic", "nested": [{"record_id": "derived", "status": "Valid"}]}
    assert probe.baseline_projection(source) == {"environment_id": "semantic", "nested": [{"status": "Valid"}]}
    assert set(probe.GAP_ASSIGNMENTS) == set(probe.OPERATIONS)


@pytest.mark.parametrize("profiles,tag", [
    (("data@0",), "binary"), (("definitions@0",), "unary"),
    (("closure@0",), "reach"), (("order@0",), "le"),
])
def test_profile_positive_uses_its_semantics(profiles, tag):
    env = Environment(probe.raw_environment(profiles))
    model = FiniteModel.from_dict(env, probe.model_wire(env))
    assert probe.formula_to_data(env, probe.semantic_formula(env))[0] == tag
    for name in ("parse_accept", "typing", "evaluate", "countermodel_check"):
        result = probe.outcome(probe.operation(name, "positive", env, model))
        assert result["cell"] == "S", (profiles, name, result)
