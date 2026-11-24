"""date-arith-ar-fullwidth-span (Codex AR review, reviews/spare/date-arith/CODEX-AR-1124.final.md MEDIUM 2):
a duration-span count written in non-ASCII Unicode decimal digits (fullwidth, Arabic-Indic, ...) is refused
CANNOT (DateRuleSpan) exactly as its ASCII form is, before the facts map reads the clause as a plain fact.
Synthetic inputs only."""
from __future__ import annotations

import pytest

from ve.surface.dates import DateRuleError, lower_date_item

from test_date_arith import environment

RESIDENT = ["unary", "resident", ["const", "p"]]


def _env():
    return environment(("deadline", "the deadline"))


def _span_item(count, unit="weeks", link="before"):
    clause = f"the person lived in a care home for {count} {unit} {link} the qualifying week"
    return f"If {clause}, then the deadline is 1 June 2026.", {clause: RESIDENT}


@pytest.mark.parametrize("count", [
    "１２",        # the review's exact item: fullwidth 12 (U+FF11 U+FF12)
    "١٢",        # Arabic-Indic 12
    "۵۲",        # extended Arabic-Indic (Persian) 52
    "१२",        # Devanagari 12
    "1２",             # mixed ASCII and fullwidth
    "12",                  # the ASCII form keeps its refusal
])
def test_a_span_count_in_any_decimal_digits_is_refused_cannot(count):
    text, facts = _span_item(count)
    with pytest.raises(DateRuleError, match=r"CANNOT \(DateRuleSpan\)"):
        lower_date_item(_env(), text, {}, roles=["the person"], may_lack=[], facts=facts)


@pytest.mark.parametrize("unit, link", [("days", "preceding"), ("months", "ending with"), ("year", "after")])
def test_a_fullwidth_span_count_is_refused_for_each_unit(unit, link):
    text, facts = _span_item("３", unit, link)
    with pytest.raises(DateRuleError, match=r"CANNOT \(DateRuleSpan\)"):
        lower_date_item(_env(), text, {}, roles=["the person"], may_lack=[], facts=facts)


def test_a_period_of_fullwidth_weeks_is_refused():
    clause = "the person lived in a care home for a period of ５２ weeks prior to the qualifying week"
    with pytest.raises(DateRuleError, match=r"CANNOT \(DateRuleSpan\)"):
        lower_date_item(_env(), f"If {clause}, then the deadline is 1 June 2026.", {}, roles=["the person"],
                        may_lack=[], facts={clause: RESIDENT})


@pytest.mark.parametrize("clause", [
    "the person lived in a care home for ¹² weeks before the qualifying week",     # superscript 12 (No)
    "the person lived in a care home for ⑫ weeks before the qualifying week",           # circled 12 (No)
    "the person lived in a care home for 12 ｗｅｅｋｓ before the qualifying week",  # fullwidth unit
    "the person lived in a care home ｆｏｒ 12 weeks before the qualifying week",   # fullwidth "for"
    "the person lived in a care home for 12​ weeks before the qualifying week",          # zero-width space
    "the person lived in a care home for 12 wee⁠ks before the qualifying week",          # word joiner in the unit
    "the person lived in a care home for twenty­six weeks before the qualifying week",   # soft hyphen in the count
    "the person lived in a care home for twenty­ six weeks before the qualifying week",  # soft hyphen, then space
])
def test_review_b_compatibility_and_format_characters_do_not_escape_the_span_refusal(clause):
    """The review seat's B findings: NFKC-compatible spellings and format (Cf) characters are refused as their
    plain forms are."""
    with pytest.raises(DateRuleError, match=r"CANNOT \(DateRuleSpan\)"):
        lower_date_item(_env(), f"If {clause}, then the deadline is 1 June 2026.", {}, roles=["the person"],
                        may_lack=[], facts={clause: RESIDENT})


def test_control_fullwidth_digits_outside_a_span_still_lower_through_the_facts_map():
    """The guard only adds span refusals: a clause with fullwidth digits and no span unit still lowers."""
    clause = "the person lived in care home １２"
    lowered = lower_date_item(_env(), f"If {clause}, then the deadline is 1 June 2026.", {},
                              roles=["the person"], may_lack=[], facts={clause: RESIDENT})
    assert [p["formula"] for p in lowered["premises"]] == [
        ["implies", RESIDENT, ["date_on", ["const", "day", "deadline"], ["cal", ["date", "2026-06-01"]]]]]
