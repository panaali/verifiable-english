"""date-arith C2 (ve/surface/dates.py `_day_constants_in`): a conclusion whose day terms are decimal literals
(["decimal", "day", n], here from the facts map) compares fixed dates only and is refused, as the raw
["date", iso] and ["num", "day", n] spellings already are (Codex AR 2026-11-24 MEDIUM 3). A conclusion that
names a day constant stays accepted. Synthetic inputs only."""
import pytest

from ve.surface.dates import DateRuleError, lower_date_item
from tests.test_date_arith import FACTS, _deadline_env

CODEX = "If 1 January 1970 is on 1 January 1970, then 2 January 1970 is on 3 January 1970."
CODEX_FACTS = {"2 January 1970 is on 3 January 1970": ["date_on", ["decimal", "day", "1"], ["decimal", "day", "2"]]}


def _lower(text, facts):
    return lower_date_item(_deadline_env(), text, {}, roles=["the person"], may_lack=[], facts=facts)


def test_codex_ar_med3_decimal_day_terms_compare_fixed_dates_only():
    with pytest.raises(DateRuleError, match=r"compares fixed dates only"):
        _lower(CODEX, CODEX_FACTS)


@pytest.mark.parametrize("formula", [
    ["date_before", ["decimal", "day", "2"], ["decimal", "day", "1"]],
    ["date_on", ["decimal", "day", "1"], ["num", "day", "2"]],
    ["date_on", ["decimal", "day", "1.0"], ["date", "1970-01-03"]],
    ["not", ["date_after", ["decimal", "day", "1"], ["decimal", "day", "2"]]],
    ["and", ["unary", "eligible", ["const", "p"]], ["date_on", ["decimal", "day", "1"], ["decimal", "day", "2"]]],
])
def test_decimal_day_terms_any_node_compare_fixed_dates_only(formula):
    text = "If the person is a man, then the fixed thing holds."
    with pytest.raises(DateRuleError, match=r"compares fixed dates only"):
        _lower(text, {**FACTS, "the fixed thing holds": formula})


def test_decimal_day_term_beside_a_day_constant_stays_accepted():
    """A conclusion that names a date of the logic (a day constant) concludes it, even with a decimal literal."""
    formula = ["date_on", ["const", "day", "deadline"], ["decimal", "day", "2"]]
    lowered = _lower("If the person is a man, then the deadline holds.", {**FACTS, "the deadline holds": formula})
    assert lowered["concluded"] == [("deadline", ["unary", "man", ["const", "p"]],
                                     "If the person is a man, then the deadline holds.")]
    assert [p["formula"] for p in lowered["premises"]] == [["implies", ["unary", "man", ["const", "p"]], formula]]


def test_role_conclusion_without_day_terms_stays_accepted():
    lowered = _lower("If the person is a man, then the person is eligible.", FACTS)
    assert [p["formula"] for p in lowered["premises"]] == [
        ["implies", ["unary", "man", ["const", "p"]], ["unary", "eligible", ["const", "p"]]]]
    assert lowered["concluded"] == []

