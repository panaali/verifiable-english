"""Restricted W6 wording derivations; whole document English remains gated."""
import pytest

from ve.environment import Environment
from ve.errors import AmbiguousDerivation, SyntaxError, VEError
from ve.surface.time import parse_quantity_sentence, render_quantity_sentence


def fixture(duplicate=False):
    constants = {
        "pce_sep": {"sort": "$int", "unit": "bp", "description": "September PCE estimate",
                    "verbalisation": "the September PCE estimate"},
        "pce_jun": {"sort": "$int", "unit": "bp", "description": "June PCE estimate",
                    "verbalisation": "the June PCE estimate"},
        "return_date": {"sort": "$int", "unit": "day", "description": "return date",
                        "verbalisation": "the return date"},
        "decision_date": {"sort": "$int", "unit": "day", "description": "decision date",
                          "verbalisation": "the decision date"},
        "amount": {"sort": "$int", "unit": "usd_cent", "description": "USD amount",
                   "verbalisation": "the amount"},
    }
    if duplicate:
        constants["other_sep"] = {"sort": "$int", "unit": "bp", "description": "other estimate",
                                  "verbalisation": "the September PCE estimate"}
    return Environment({"language": "ve.core@0.2",
        "profiles": ["order@0", "relational-fol@0", "time@0"],
        "spec_revision": "ve-v0.2-expand2-2026-09-25",
        "vocabulary": {"sorts": {}, "predicates": {}, "constants": constants},
        "unit_schema": "ve-units@1", "units": {
            "bp": {"scale": "100", "display": {"kind": "percent"}},
            "usd_cent": {"scale": "100", "display": {"kind": "money", "currency": "USD",
                                                          "input_symbol": "$"}},
            "day": {"scale": "1", "display": {"kind": "iso_date"}},
            "elapsed_day": {"scale": "1", "display": {"kind": "decimal", "label": "days"}}}})


def test_one_reading_roundtrip_without_tag_identifiers():
    env = fixture()
    examples = [
        "The September PCE estimate equals 3.70%.",
        "The September PCE estimate is greater than the June PCE estimate.",
        "The return date is after 2026-09-16.",
        "The return date is on or after the decision date and on or before 10 days after the decision date.",
        "The return date is 10 days after the decision date.",
        "The elapsed duration from the decision date to the return date equals 10 days.",
        "The September PCE estimate minus the June PCE estimate equals 0.10 percentage points.",
        "The amount equals USD 3.75.",
    ]
    for sentence in examples:
        q = parse_quantity_sentence(env, sentence)
        rendered = render_quantity_sentence(env, q)
        assert parse_quantity_sentence(env, rendered) == q
        assert all(tag not in rendered for tag in ("bp", "usd_cent", "elapsed_day", ":day"))
    assert render_quantity_sentence(env, parse_quantity_sentence(env, "The amount equals $3.75.")) == \
           "The amount equals USD 3.75."


def test_ambiguity_and_cross_tag_suppression():
    with pytest.raises(AmbiguousDerivation, match="2 derivations"):
        parse_quantity_sentence(fixture(duplicate=True), "The September PCE estimate equals 3.70%.")
    with pytest.raises(VEError, match="UnitMismatch"):
        parse_quantity_sentence(fixture(), "The amount equals 3.75%.")
    with pytest.raises(SyntaxError, match="No W6 quantity reading"):
        parse_quantity_sentence(fixture(), "The September PCE estimate is substantially higher.")
    with pytest.raises(SyntaxError, match="No W6 quantity reading"):
        parse_quantity_sentence(fixture(), "The September PCE estimate equals 0.10 percentage points.")
    forged = {"format": "ve-quantity@1", "traces": [],
              "formula": ["eq", ["const", "usd_cent", "pce_sep"], ["num", "usd_cent", "375"]]}
    with pytest.raises(VEError, match="UnitMismatch"):
        render_quantity_sentence(fixture(), forged)
