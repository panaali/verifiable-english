"""Python entry points opened by the S1 wrapper profile."""

import pytest

from tests.test_norms import environment
from ve.ast import formula_from_data
from ve.environment import Environment
from ve.errors import VEError
from ve.identity import meaning_id
from ve.readings import validate_couplings, validate_reading_sets
from ve.readings_english import coupling_sentence


def _formula_sets(env):
    content = ["top"]
    mid = meaning_id(env, formula_from_data(env, content))
    return [
        {"id": name, "unit": unit, "version": 1, "status": "open", "readings": [{
            "id": "yes", "kind": "asserted", "meaning_id": mid, "content": content,
            "labels": {"force": "strict"},
            "admission": {"who": "reviewer", "why": "recorded", "distinguishing_models": {}}
        }]}
        for name, unit in (("first", "u1"), ("second", "u2"))
    ]


def test_formula_labels_and_couplings_on_norms_chain():
    raw = environment({}).to_dict()
    raw["profiles"] = sorted({*raw["profiles"], "readings@1"})
    env = Environment(raw)
    sets = _formula_sets(env)
    assert validate_reading_sets(env, sets, {"u1", "u2"}) == {("first", 1), ("second", 1)}
    coupling = {"id": "c-force", "axis": "force", "sets": [
        {"set": "first", "version": 1}, {"set": "second", "version": 1}],
        "by": "reviewer", "reason_spans": ["u1"]}
    assert validate_couplings(env, [coupling], sets, {"u1", "u2"}) == {"c-force"}
    del sets[1]["readings"][0]["labels"]
    with pytest.raises(VEError, match="CouplingLabelMissing: c-force, second"):
        validate_couplings(env, [coupling], sets, {"u1", "u2"})


def test_formula_labels_stay_gated_without_s1_or_rights():
    env = environment({})
    sets = _formula_sets(env)
    with pytest.raises(VEError, match="invalid reading"):
        validate_reading_sets(env, sets, {"u1", "u2"})


def test_coupling_english_uses_sentence_numbers_and_closed_axis():
    sets = {"first": {"unit": "u1"}, "second": {"unit": "u2"}}
    units = [{"id": "u1"}, {"id": "u2"}, {"id": "citation"}]
    coupling = {"axis": "force", "sets": [
        {"set": "first", "version": 1}, {"set": "second", "version": 1}],
        "reason_spans": ["citation"]}
    assert coupling_sentence(coupling, sets, units) == (
        "Sentences 1 and 2 are read with the same force, because of sentence 3.")
    coupling["axis"] = "history"
    assert "same label history" in coupling_sentence(coupling, sets, units)
