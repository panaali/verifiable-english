"""The RD-9 use of E14's existing sentence with Lean-selected gaps."""

import copy

import pytest

from tests import lean_routes
from tests.test_readings_nd_lean import PROBE1, base1, doc1, env1
from tests.test_readings_s1_lean import entry
from ve.errors import CheckerUnavailable
from ve import readings_route

from ve.readings_english import force_twin_sentence
from ve.readings_s2_english import s1_gated


def _line(gaps=""):
    return force_twin_sentence("must", "a must act", "a should act", "the decider", ("a", "u"),
                               "obligation", True, False, gaps=gaps)


def test_e14_without_gaps_keeps_the_existing_wording():
    assert _line() == ("This sentence says *must*. (1) *a must act* (2) *a should act* "
                       "They differ here: suppose the decider decides the exception applies to a and u. "
                       "Under (1) a still must. Under (2) a is not required to.")


def test_e14_places_leans_gap_after_decision_and_before_outcomes():
    text = _line(" Here the text does not say whether a must act; this situation answers 'no'.")
    assert "exception applies to a and u. Here the text does not say whether" in text
    assert "answers 'no'. Under (1) a still must. Under (2) a is not required to." in text


def test_e14_keeps_both_readings_and_the_source_word_with_a_gap():
    text = _line(" Here the text does not say whether a must act; this situation answers 'no'.")
    assert "says *must*. (1) *a must act* (2) *a should act*" in text
    assert text.count("Under (1)") == text.count("Under (2)") == 1
    assert s1_gated("E14", text) == text


def test_pair_gaps_are_typed_and_bound_to_the_request(monkeypatch):
    if not lean_routes.SERVICE.exists():
        pytest.skip("the Lean service has not been built")
    raw = env1()
    document, _ = doc1(raw, entry(base1([["a", "u"]]), "asks", PROBE1, False))
    args = (raw, document["units"], document["reading_sets"])
    genuine = readings_route.validate(*args)
    pair = genuine["sets"][0]["pairs"][0]["pair"]
    assert pair["gaps"] == [["help_required", ["a", "u"], False]]

    for change in (
        lambda f: f.pop("gaps"),
        lambda f: f["gaps"][0].__setitem__(0, "asks"),
        lambda f: f["gaps"][0][1].__setitem__(0, "missing"),
        lambda f: f["gaps"][0].__setitem__(1, []),
        lambda f: f["gaps"][0].__setitem__(2, "yes"),
        lambda f: f["gaps"].append(copy.deepcopy(f["gaps"][0])),
    ):
        forged = copy.deepcopy(genuine)
        change(forged["sets"][0]["pairs"][0]["pair"])
        monkeypatch.setattr(readings_route, "run_lean", lambda *a, **k: [forged])
        with pytest.raises(CheckerUnavailable):
            readings_route.validate(*args)
