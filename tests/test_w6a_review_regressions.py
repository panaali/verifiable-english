"""Regressions for the W6a review findings, each generalized to its class.

Astra: currency alias collisions, first-split English ambiguity, undeclared
`day`, environment identity spelling, literal-first round trip.
Fable: trace parity (see test_units_w6a), sentence-initial folding, display
injectivity, tag/sort namespace.
"""
import copy
from itertools import product

import pytest

from ve.environment import Environment
from ve.errors import AmbiguousDerivation, TypeMismatch, UnsupportedProfile, VEError
from ve.surface.time import parse_quantity_sentence, render_quantity_sentence
from ve.units import SPACES, elaborate_quantity, quantity_meaning_id
from ve.wire import digest


def raw_environment(units=None, constants=None, sorts=None, predicates=None):
    return {"language": "ve.core@0.2", "profiles": ["order@0", "relational-fol@0", "time@0"],
            "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": sorts or {}, "predicates": predicates or {},
                           "constants": constants or {}},
            "unit_schema": "ve-units@1",
            "units": {"bp": {"scale": "100", "display": {"kind": "percent"}}} if units is None else units}


def money(currency, symbol=None):
    display = {"kind": "money", "currency": currency}
    if symbol is not None:
        display["input_symbol"] = symbol
    return {"scale": "100", "display": display}


def label(text, placement=None):
    display = {"kind": "decimal", "label": text}
    if placement is not None:
        display["placement"] = placement
    return {"scale": "1", "display": display}


def named(unit, words):
    return {"sort": "$int", "unit": unit, "description": words, "verbalisation": words}


# --- Astra P1 / Fable 3: every enabled literal form is injective -------------

COLLIDING_UNITS = [
    # The review reproducer: a USD alias spelling the EUR canonical prefix.
    {"usd": money("USD", "EUR "), "eur": money("EUR")},
    # Alias equal to another alias, and alias extending another alias.
    {"usd": money("USD", "$"), "cad": money("CAD", "$")},
    {"usd": money("USD", "$"), "aud": money("AUD", "$A")},
    # An alias of the same tag equal to its canonical prefix still yields two readings.
    {"usd": money("USD", "USD ")},
    # Alias or currency spelling a prefix label, and prefix labels extending each other.
    {"usd": money("USD", "calendar year "), "calendar_year": label("calendar year", "prefix")},
    {"usd": money("USD"), "code": label("USD", "prefix")},
    {"a": label("fiscal", "prefix"), "b": label("fiscal year", "prefix")},
    # Suffix labels extending each other, the percent sign, and the points alias.
    {"days_a": label("days"), "days_b": label("calendar days")},
    {"bp": {"scale": "100", "display": {"kind": "percent"}}, "pct": label("%")},
    {"bp": {"scale": "100", "display": {"kind": "percent"}}, "pts": label("points")},
    {"bp": {"scale": "100", "display": {"kind": "percent"}}, "pts": label("percentage points")},
    {"bp": {"scale": "100", "display": {"kind": "percent"}},
     "other": {"scale": "1000", "display": {"kind": "percent"}}},
    # Affixes that touch the amount with a digit, sign or point.
    {"usd": money("USD", "-$")}, {"n": label("2nd", "prefix")}, {"n": label("x 2")},
    {"n": label(".x", "prefix")},
]


@pytest.mark.parametrize("units", COLLIDING_UNITS)
def test_display_collisions_reject_before_parsing(units):
    with pytest.raises(VEError, match="DisplayCollision"):
        Environment(raw_environment(units))


def test_distinct_affixes_still_admit():
    env = Environment(raw_environment({
        "bp": {"scale": "100", "display": {"kind": "percent"}},
        "usd": money("USD", "$"), "eur": money("EUR", "€"), "aud": money("AUD", "A$"),
        "calendar_year": label("calendar year", "prefix"),
        "age_year": label("completed years of age"),
        "elapsed_day": {"scale": "1", "display": {"kind": "decimal", "label": "days"}},
    }))
    assert set(env.units) == {"bp", "usd", "eur", "aud", "calendar_year", "age_year", "elapsed_day"}


def test_review_currency_alias_never_reads_as_the_other_currency():
    # Before the fix this environment admitted and "EUR 3.75" parsed as USD.
    raw = raw_environment({"usd": money("USD", "EUR "), "eur": money("EUR")},
                          {"amount": named("usd", "the amount")})
    with pytest.raises(VEError, match="DisplayCollision"):
        Environment(raw)


@pytest.mark.parametrize("text", ["", " $", "$  ", "U\tS", "US $", "a  b", "US $"])
def test_display_strings_are_whitespace_normalized(text):
    for units in ({"usd": money("USD", text)}, {"n": label(text)}):
        with pytest.raises(VEError):
            Environment(raw_environment(units))


def test_only_an_input_symbol_may_end_in_one_space():
    assert Environment(raw_environment({"usd": money("USD", "US$ ")}))
    with pytest.raises(VEError):
        Environment(raw_environment({"n": label("items ")}))


def test_space_set_is_pythons_isspace():
    assert SPACES == {chr(c) for c in range(0x110000) if chr(c).isspace()}


# --- Astra P1: all derivations, not the first regex split --------------------

def ambiguous_env():
    return Environment(raw_environment(constants={
        "a": named("bp", "the a"), "b": named("bp", "the b"), "c": named("bp", "the c"),
        "b_minus_c": named("bp", "the b minus the c"),
        "a_minus_b": named("bp", "the a minus the b"),
        "a_equals_b": named("bp", "the a equals the b"),
        "b_equals_c": named("bp", "the b equals the c"),
    }))


def test_review_two_subtraction_trees_reject():
    env = ambiguous_env()
    with pytest.raises(AmbiguousDerivation, match="2 derivations"):
        parse_quantity_sentence(env, "The a minus the b minus the c equals 0.10 percentage points.")
    # Each tree renders to that same sentence, so neither may round-trip silently.
    for left, right in (("a", "b_minus_c"), ("a_minus_b", "c")):
        q = {"format": "ve-quantity@1", "traces": [], "formula": ["eq", ["add", "bp",
             ["const", "bp", left], ["scale", "bp", "-1", ["const", "bp", right]]], ["num", "bp", "10"]]}
        sentence = render_quantity_sentence(env, q)
        assert sentence == "The a minus the b minus the c equals 0.10 percentage points."
        with pytest.raises(AmbiguousDerivation):
            parse_quantity_sentence(env, sentence)


@pytest.mark.parametrize("sentence", [
    "The a equals the b equals the c.",
    "The a equals the b is less than the c.",
])
def test_connector_inside_names_is_ambiguous_or_unique_never_first_split(sentence):
    env = ambiguous_env()
    readings = []
    for q in _all_readings(env, sentence):
        readings.append(q)
    if len(readings) > 1:
        with pytest.raises(AmbiguousDerivation):
            parse_quantity_sentence(env, sentence)
    elif readings:
        assert parse_quantity_sentence(env, sentence) == readings[0]


def _all_readings(env, sentence):
    """Independent brute force: every split at every connector occurrence."""
    text = sentence[:-1]
    ops = {" equals ": ("eq", False), " is less than ": ("lt", False)}
    names = {d.verbalisation: n for n, d in env.constants.items()}
    found = []
    for connector, (op, _) in ops.items():
        start = text.find(connector)
        while start != -1:
            left, right = text[:start], text[start + len(connector):]
            left = left[:1].lower() + left[1:]
            if left in names and right in names:
                found.append({"format": "ve-quantity@1", "traces": [],
                              "formula": [op, ["const", "bp", names[left]], ["const", "bp", names[right]]]})
            start = text.find(connector, start + 1)
    return found


def test_derivation_budget_is_named():
    env = ambiguous_env()
    sentence = "The a" + " is 3 days after the a" * 200 + "."
    with pytest.raises(VEError, match="MAX_DERIVATIONS"):
        parse_quantity_sentence(env, sentence)


# --- Astra P2 / Fable 2: literal-first and capitalized names round-trip ---------

def surface_env():
    return Environment(raw_environment({
        "bp": {"scale": "100", "display": {"kind": "percent"}},
        "usd_cent": money("USD", "$"),
        "calendar_year": label("calendar year", "prefix"),
        "day": {"scale": "1", "display": {"kind": "iso_date"}},
        "elapsed_day": {"scale": "1", "display": {"kind": "decimal", "label": "days"}},
    }, {
        "amount": named("usd_cent", "the amount"),
        "fed_rate": named("bp", "The Fed rate"),
        "rate": named("bp", "the rate"),
        "year": named("calendar_year", "the first year"),
        "start": named("day", "the start date"),
        "end": named("day", "the end date"),
        "span": named("elapsed_day", "the span"),
    }))


def test_review_money_literal_first_round_trips():
    env = surface_env()
    q = parse_quantity_sentence(env, "USD 3.75 is less than USD 4.00.")
    assert q["formula"] == ["lt", ["num", "usd_cent", "375"], ["num", "usd_cent", "400"]]
    assert render_quantity_sentence(env, q) == "USD 3.75 is less than USD 4.00."
    q = parse_quantity_sentence(env, "USD 3.75 is less than the amount.")
    assert parse_quantity_sentence(env, render_quantity_sentence(env, q)) == q


def test_every_rendered_operand_order_round_trips():
    """Class check: each literal/constant in each position, for every wording."""
    env = surface_env()
    operands = {
        "usd_cent": [["num", "usd_cent", "375"], ["const", "usd_cent", "amount"]],
        "bp": [["num", "bp", "-25"], ["const", "bp", "fed_rate"], ["const", "bp", "rate"]],
        "calendar_year": [["num", "calendar_year", "2029"], ["const", "calendar_year", "year"]],
        "day": [["num", "day", "20712"], ["const", "day", "start"], ["const", "day", "end"]],
        "elapsed_day": [["num", "elapsed_day", "-3"], ["const", "elapsed_day", "span"]],
    }
    formulas = []
    for tag, terms in operands.items():
        for left, right in product(terms, terms):
            formulas += [["eq", left, right], ["lt", left, right], ["le", left, right]]
            if tag == "day":
                formulas += [[op, left, right] for op in ("date_on", "date_before", "date_after",
                                                          "date_no_later")]
                formulas += [["within_days", left, right, "0"], ["shift_days", left, right, "10"]]
                formulas += [["elapsed_days", left, right, v] for v in operands["elapsed_day"]]
            if tag == "bp":
                formulas += [["eq", ["add", "bp", left, ["scale", "bp", "-1", right]],
                              ["num", "bp", "10"]]]
    assert len(formulas) > 100
    for formula in formulas:
        q = {"format": "ve-quantity@1", "traces": [], "formula": formula}
        sentence = render_quantity_sentence(env, q)
        assert parse_quantity_sentence(env, sentence) == q, sentence


def test_initial_folding_applies_to_names_only():
    env = surface_env()
    # A capitalized verbalisation renders and parses unchanged at sentence start.
    q = parse_quantity_sentence(env, "The Fed rate equals 2.00%.")
    assert q["formula"][1] == ["const", "bp", "fed_rate"]
    # Lower-case "the rate" is a name; its capitalized form reads the same constant.
    assert parse_quantity_sentence(env, "the rate equals 2.00%.") == \
        parse_quantity_sentence(env, "The rate equals 2.00%.")
    # A prefix label is not case-folded into a literal.
    with pytest.raises(VEError):
        parse_quantity_sentence(env, "Calendar year 2029 equals the first year.")
    assert parse_quantity_sentence(env, "calendar year 2029 equals the first year.")["formula"] == \
        ["eq", ["num", "calendar_year", "2029"], ["const", "calendar_year", "year"]]


def test_capitalization_collision_is_ambiguous():
    raw = raw_environment(constants={"a": named("bp", "the rate"), "b": named("bp", "The rate")})
    with pytest.raises(AmbiguousDerivation):
        parse_quantity_sentence(Environment(raw), "The rate equals 2.00%.")


# --- Astra P2: the literal `date` names the reserved tag -----------------------

@pytest.mark.parametrize("formula", [
    ["date_on", ["date", "2026-09-16"], ["date", "2026-09-16"]],
    ["eq", ["date", "2026-09-16"], ["date", "2026-09-16"]],
    ["lt", ["date", "2026-09-16"], ["date", "2026-09-17"]],
])
def test_review_undeclared_day_rejects(formula):
    env = Environment(raw_environment({}))
    with pytest.raises(VEError, match=r"UnknownUnit\(day\)"):
        elaborate_quantity(env, {"format": "ve-quantity@1", "formula": formula})


def test_undeclared_elapsed_day_rejects():
    env = Environment(raw_environment({"day": {"scale": "1", "display": {"kind": "iso_date"}}}))
    with pytest.raises(VEError, match=r"UnknownUnit\(elapsed_day\)"):
        elaborate_quantity(env, {"format": "ve-quantity@1", "formula":
                                 ["elapsed_days", ["date", "2026-09-16"], ["date", "2026-09-17"],
                                  ["num", "elapsed_day", "1"]]})


# --- Astra P2: the submitted spelling is the identity ------------------------

IDENTITY_VARIANTS = [
    # The review reproducer: an explicit empty argument_units map.
    {"predicates": {"p": {"arguments": ["$int"], "argument_units": {}, "description": "P"}}},
    {"predicates": {"p": {"arguments": ["$int"], "argument_units": {"0": "dimensionless"},
                          "description": "P"}}},
    {"predicates": {"p": {"arguments": ["$int"], "argument_units": {"0": "bp"}, "description": "P"}}},
    {"predicates": {"p": {"arguments": ["$int"], "description": "P"}}},
    {"units": {"n": label("items", "suffix")}},
    {"units": {"n": label("items")}},
    {"units": {}},
    {"constants": {"c": {"sort": "$int", "unit": "dimensionless", "description": "c"}}},
    {"constants": {"c": {"sort": "$int", "description": "c"}}},
]


@pytest.mark.parametrize("variant", IDENTITY_VARIANTS)
def test_environment_identity_is_the_submitted_declaration(variant):
    raw = raw_environment(variant.get("units"), variant.get("constants"),
                          predicates=variant.get("predicates"))
    env = Environment(copy.deepcopy(raw))
    assert env.environment_id == digest(f"ve-environment-{env.identity_version}\n", raw)
    assert env.to_dict() == raw


def test_distinct_spellings_are_distinct_identities():
    ids = {Environment(raw_environment(v.get("units"), v.get("constants"),
                                       predicates=v.get("predicates"))).environment_id
           for v in IDENTITY_VARIANTS}
    assert len(ids) == len(IDENTITY_VARIANTS)


# --- Fable 4: tags and user sorts do not share a namespace ------------------

@pytest.mark.parametrize("sort", ["bp", "dimensionless"])
def test_sort_named_like_a_tag_rejects(sort):
    raw = raw_environment(sorts={sort: {"description": "a sort"}})
    with pytest.raises(VEError, match="collides with a declared sort"):
        Environment(raw)


def test_object_and_quantity_types_never_unify():
    raw = raw_environment(sorts={"item": {"description": "item"}},
                          constants={"e": {"sort": "item", "description": "e"},
                                     "rate": named("bp", "the rate")})
    env = Environment(raw)
    with pytest.raises(TypeMismatch):
        elaborate_quantity(env, {"format": "ve-quantity@1", "formula": ["eq", ["const", "e"],
                                                                          ["const", "bp", "rate"]]})
    with pytest.raises(TypeMismatch):
        elaborate_quantity(env, {"format": "ve-quantity@1", "formula": ["lt", ["const", "e"],
                                                                          ["const", "e"]]})


# --- Unsupported combinations stay explicit ---------------------------------

@pytest.mark.parametrize("profiles", [
    ["data@0", "order@0", "relational-fol@0", "time@0"],
    ["definitions@0", "order@0", "relational-fol@0", "time@0"],
    ["norms@0", "order@0", "relational-fol@0", "time@0"],
    ["order@0", "relational-fol@0"],
])
def test_w6_profiles_are_exact(profiles):
    raw = raw_environment()
    raw["profiles"] = profiles
    with pytest.raises(UnsupportedProfile):
        Environment(raw)


def test_string_literals_and_nary_atoms_are_gated():
    raw = raw_environment(constants={"s": {"sort": "$string"}})
    with pytest.raises(UnsupportedProfile, match=r"\$string"):
        Environment(raw)
    env = Environment(raw_environment())
    with pytest.raises(UnsupportedProfile, match="n-ary"):
        elaborate_quantity(env, {"format": "ve-quantity@1", "formula": ["atom", "p", []]})


def test_meaning_id_changes_with_the_tag_only():
    raw = raw_environment({"bp": {"scale": "100", "display": {"kind": "percent"}},
                           "usd": money("USD")})
    env = Environment(raw)
    ids = {quantity_meaning_id(env, {"format": "ve-quantity@1",
                                     "formula": ["lt", ["num", tag, "375"], ["num", tag, "400"]]})
           for tag in ("bp", "usd", "dimensionless")}
    assert len(ids) == 3
