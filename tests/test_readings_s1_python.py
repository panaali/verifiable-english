"""Python entry points opened by the S1 wrapper profile."""

import pytest

from tests.test_norms import environment
from ve.ast import formula_from_data
from ve.environment import Environment
from ve.errors import VEError
from ve.identity import meaning_id
from ve.readings import source_word_text, validate_couplings, validate_reading_sets
from ve.readings_english import (E22, E23, E24, act_only_sentence,
                                 assertion_pair_sentence, coupling_sentence,
                                 decision_only_sentence, force_twin_sentence,
                                 outcome_pair_sentence)


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


def test_source_word_is_a_byte_span_and_has_a_closed_vocabulary():
    source = "SHALL MAY NOT shouldn’t".encode()
    shall = [0, 5]
    may_not = [6, 13]
    curly = [14, len(source)]
    assert source_word_text(source, shall, [0, len(source)]) == "shall"
    assert source_word_text(source, may_not, [0, len(source)]) is None
    assert source_word_text(source, curly, [0, len(source)]) == "shouldn't"
    with pytest.raises(VEError, match="invalid source word span"):
        source_word_text(source, [13, 15], [0, 13])
    with pytest.raises(VEError, match="invalid source word span"):
        source_word_text(source, [21, 22], [0, len(source)])


def test_s1_report_sentences_keep_their_checked_claims_narrow():
    twin = force_twin_sentence(
        "shall", "Every agent must avoid deceiving each user.",
        "Every agent should avoid deceiving each user.", "unstated", ("a", "u"),
        "obligation", True, False)
    assert twin == (
        "This sentence says *shall*. (1) *Every agent must avoid deceiving each user.* "
        "(2) *Every agent should avoid deceiving each user.* They differ here: "
        "suppose the decider decides the exception applies to a and u. "
        "Under (1) a still must. Under (2) a is not required to.")
    assert decision_only_sentence("unstated").startswith(
        "These two readings differ only where the decider decides")
    assert act_only_sentence("avoid deceiving", "help").endswith(
        "No situation separates them on a shared act.")
    assert outcome_pair_sentence("a is an agent; u is a user", "*should*", "*must*",
                                 "obligation", "a", False, other_admissible=True) == (
        "These two readings differ here: a is an agent; u is a user. "
        "Under *should*, a is not required to. "
        "Under *must* that is not so, whatever is decided.")
    assert "situation is ruled out" in outcome_pair_sentence(
        "a is an agent", "*must*", "*should*", "obligation", "a", True,
        other_admissible=False)
    assert "the sentence is false there" in assertion_pair_sentence(
        "a asks u", "reading 2", "reading 1")
    for sentence in (twin, E22, E23, E24):
        assert all(prefix not in sentence for prefix in ("ve__", "rd-", "soft__", "rights__", "may not"))
    with pytest.raises(VEError, match="E14 needs a source word"):
        force_twin_sentence("may not", "strict", "default", "unstated", ("a",),
                            "obligation", True, False)
