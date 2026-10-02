"""Python entry points opened by the S1 wrapper profile."""

import pytest

from tests.test_norms import environment, permission
from ve.ast import formula_from_data
from ve.environment import Environment
from ve.errors import CheckerUnavailable, VEError
from ve.identity import meaning_id
from ve.readings import (s1_content_kind, s1_content_meaning_id, source_word_text,
                         validate_couplings, validate_reading_sets)
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
    # DRI ruling 2: `decision_only_sound` is unproved, so the finding's English says it is not certified
    # and never states the claim as checked (E15's "No situation separates them ..." is not shown).
    assert decision_only_sentence("unstated") == (
        "It is not certified that these two readings differ only where the decider decides "
        "that the exception applies.")
    assert "No situation separates" not in decision_only_sentence("the operator")
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
    # E21's frame (composition.md 2.1): the second sentence says "it is false there".
    assert assertion_pair_sentence("a asks u", "reading 2", "reading 1") == (
        "These two readings differ here: a asks u. Under reading 2, the sentence is true there. "
        "Under reading 1, it is false there.")
    for sentence in (twin, E22, E23, E24):
        assert all(prefix not in sentence for prefix in ("ve__", "rd-", "soft__", "rights__", "may not"))
    with pytest.raises(VEError, match="E14 needs a source word"):
        force_twin_sentence("may not", "strict", "default", "unstated", ("a",),
                            "obligation", True, False)


def test_candidate_norm_has_the_fixed_unit_meaning_id():
    from ve.norms import NormDocument, norm_meaning_id
    env = environment({"permitted": permission()})
    content = {"norm": {"name": "help", "predicate": "permitted", "sign": True,
                        "guard": ["top"], "unless": [], "over": []}}
    reading = {"id": "strict", "kind": "norm", "content": content}
    assert s1_content_kind(content) == "norm"
    assert s1_content_meaning_id(env, "rs", reading) == norm_meaning_id(
        env, NormDocument._decode(content))
    assert s1_content_kind({"quantity": {}}) is None
    with pytest.raises(VEError, match="kind asserted and content of kind norm"):
        s1_content_meaning_id(env, "rs", {**reading, "kind": "asserted"})
    with pytest.raises(VEError, match="requires rights@0"):
        s1_content_meaning_id(env, "rs", {**reading, "kind": "right",
                                               "content": {"right": {}}})
    with pytest.raises(VEError, match="bar candidate content is not implemented"):
        s1_content_meaning_id(env, "rs", {**reading, "kind": "bar",
                                               "content": {"bar": {}}})


def test_content_bearing_set_fails_closed_until_separation_replay_exists():
    raw = environment({"permitted": permission()}).to_dict()
    raw["profiles"] = sorted({*raw["profiles"], "readings@1"})
    env = Environment(raw)
    content = {"norm": {"name": "help", "predicate": "permitted", "sign": True,
                        "guard": ["top"], "unless": [], "over": []}}
    candidate = {"id": "strict", "kind": "norm", "content": content,
                 "meaning_id": s1_content_meaning_id(
                     env, "rs", {"id": "strict", "kind": "norm", "content": content}),
                 "admission": {"who": "reviewer", "why": "recorded",
                               "distinguishing_models": {}}}
    set_ = {"id": "rs", "unit": "u", "version": 1, "status": "open",
            "readings": [candidate], "situations": {}}
    with pytest.raises(CheckerUnavailable, match="awaits Lean replay"):
        validate_reading_sets(env, [set_], {"u"})
    candidate["meaning_id"] = "wrong"
    with pytest.raises(VEError, match="meaning id does not match content"):
        validate_reading_sets(env, [set_], {"u"})


def test_lines_compare_as_lean_decodes_them():
    """`line_value` is Lean's `SourceLine`: a default spelled out, an empty `cites` or `fan_out`, or another key
    order is the same line; a fan-out line's absent predicate is its first mapped predicate (compose-s1 review
    finding B: the line order and force twins compare these values, not JSON)."""
    from ve.readings_s1 import Content, force_twins, line_value
    norm = {"name": "no-arrest", "predicate": "arrest_permitted", "sign": False, "guard": ["top"], "unless": [],
            "over": []}
    line = {"kind": "claim", "norm": norm}
    same = [{**line, "cites": {}}, {**line, "fan_out": {}}, dict(reversed(list(line.items()))),
            {**line, "norm": {**norm, "mode": "strict", "alterable": [], "hard": False, "rank": None}}]
    assert all(line_value(x) == line_value(line) for x in same)
    assert line_value({**line, "cites": {"guard": ["u1"]}}) != line_value(line)
    assert line_value({**line, "holder_slot": 1}) != line_value(line)
    fan = {"kind": "claim", "fan_out": {"state": "arrest_permitted"},
           "norm": {k: v for k, v in norm.items() if k != "predicate"}}
    assert line_value(fan) == line_value({**fan, "norm": norm})
    # A line Lean does not decode keeps its JSON.
    assert line_value({"kind": "duty"}) != line_value({"kind": "duty", "cites": {}})
    default = {**norm, "mode": "default", "exception": {"decided_by": "unstated", "sufficient": [],
                                                        "necessary": [], "factors": []}}
    strict_right = Content("right", {"name": "r9", "holder": "person", "lines": [{**line, "cites": {}}]}, None)
    default_right = Content("right", {"name": "r9", "holder": "person", "guard": ["top"],
                                      "lines": [{"kind": "claim", "norm": default}]}, None)
    assert force_twins(strict_right, default_right) == (norm, default)
    assert force_twins(default_right, strict_right) is None


def test_rights_units_read_with_lean_defaults():
    from ve.readings_s1 import lean_defaults
    assert lean_defaults({"right": {"name": "r", "holder": "h", "lines": [{"kind": "claim", "fan_out": {}}]}}) == \
        {"right": {"name": "r", "holder": "h", "guard": ["top"], "lines": [{"kind": "claim"}]}}
    assert lean_defaults({"limitation": {"name": "l", "conditions": [{"name": "c"}]}}) == \
        {"limitation": {"decided_by": None, "name": "l", "conditions": [{"decided_by": None, "name": "c"}]}}
    assert lean_defaults({"bar": {"name": "b", "reading": "rule"}})["bar"]["decided_by"] == "unstated"
    assert lean_defaults({"bar": {"name": "b", "reading": "rule", "decided_by": ""}})["bar"]["decided_by"] == ""
    unit = {"norm": {"name": "n"}, "cites": {}}
    assert lean_defaults(unit) is unit
