"""The RD-9 use of E14's existing sentence with Lean-selected gaps."""

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
