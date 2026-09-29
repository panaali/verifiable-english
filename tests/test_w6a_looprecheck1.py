"""Regressions for the W6a loop recheck 1 findings, each generalized to its class.

P1 names that the sentence normalizer rewrites; P2 Lean evaluation without the
Python/Rust budget; P2 renderings that do not reparse; P2 the conditional
calendar inverse. Each class is checked in Python, Lean and Rust.
"""
from itertools import product
from pathlib import Path
import re

import pytest

from tests.test_units_lean_w6a import LEAN, lean, quantity, rust
from tests.test_w6a_review_regressions import label, named, raw_environment
from ve import ast
from ve.environment import Environment
from ve.errors import AmbiguousDerivation, ResourceLimit, VEError
from ve.evaluate import evaluate
from ve.model import FiniteModel
from ve.surface.count import at_least, exactly, n_of_m
from ve.surface.time import parse_quantity_sentence, render_quantity_sentence
from ve.units import (SPACES, decimal_exact, elaborate_quantity, erased_environment, iso_date,
                      quantity_countermodel, render_coordinate)

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(not LEAN.exists(), reason="build the Lean ve_quantity runner first")


def rejected_three_ways(raw, message):
    with pytest.raises(VEError, match=re.escape(message)):
        Environment(raw)
    probe = quantity(["top"])
    [got] = lean([{"id": "e", "environment": raw, "quantity": probe}])
    assert got["status"] == "error" and message in got["error"], got
    [other] = rust([{"id": "e", "kind": "quantity", "environment": raw, "quantity": probe}])
    assert other["status"] == "error" and message in other["error"]["message"], other


def admitted_three_ways(raw):
    env = Environment(raw)
    probe = quantity(["top"])
    [got] = lean([{"id": "a", "environment": raw, "quantity": probe}])
    assert got["status"] == "ok" and got["environment_id"] == env.environment_id, got
    [other] = rust([{"id": "a", "kind": "quantity", "environment": raw, "quantity": probe}])
    assert other["status"] == "ok" and other["environment_id"] == env.environment_id, other
    return env


# --- P1: a rendered name is read back as exactly its own constant ------------

# The reproducer, then every spelling the sentence normalizer rewrites: repeated,
# leading or trailing spaces, and any other Python whitespace character.
UNNORMALIZED = ["the  rate", " the rate", "the rate ", "the\trate", "the\nrate", "the rate",
                "the rate", "the　rate", "the rate "]


@pytest.mark.parametrize("words", UNNORMALIZED)
def test_names_the_normalizer_rewrites_reject_three_ways(words):
    raw = raw_environment(constants={"a": named("bp", words), "b": named("bp", "the rate")})
    rejected_three_ways(raw, "must be whitespace-normalized")
    # Alone, too: the name could never be read back.
    rejected_three_ways(raw_environment(constants={"a": named("bp", words)}),
                        "must be whitespace-normalized")


def test_every_python_space_is_rejected_inside_a_name():
    spaces = sorted(SPACES - {" "})
    raws = [raw_environment(constants={"a": named("bp", f"the{space}rate")}) for space in spaces]
    for raw in raws:
        with pytest.raises(VEError, match="whitespace-normalized"):
            Environment(raw)
    probe = quantity(["top"])
    for got in lean([{"id": str(i), "environment": raw, "quantity": probe}
                     for i, raw in enumerate(raws)]):
        assert got["status"] == "error" and "must be whitespace-normalized" in got["error"], got
    for got in rust([{"id": str(i), "kind": "quantity", "environment": raw, "quantity": probe}
                     for i, raw in enumerate(raws)]):
        assert got["status"] == "error" and "must be whitespace-normalized" in got["error"]["message"], got


@pytest.mark.parametrize("first,second", [
    ("the rate", "the rate"),       # the same spelling
    ("The rate", "the rate"),       # equal once the second starts a sentence
    ("the rate", "The rate"),
])
def test_names_sharing_a_sentence_spelling_reject_three_ways(first, second):
    raw = raw_environment(constants={"a": named("bp", first), "b": named("bp", second)})
    rejected_three_ways(raw, "VerbalisationCollision(")


def test_distinct_names_still_admit_three_ways():
    admitted_three_ways(raw_environment(constants={
        "a": named("bp", "the rate"), "b": named("bp", "the Rate"), "c": named("bp", "éclair rate"),
        "d": named("bp", "Éclair rate"), "e": named("bp", "the old rate")}))


def test_sentence_initial_capitalization_is_ascii_only():
    # Python would upper-case "é"; Lean and Rust do not. The spelling rule is ASCII
    # in all three, and the parser uses the same rule.
    env = admitted_three_ways(raw_environment(constants={
        "a": named("bp", "éclair rate"), "b": named("bp", "Éclair rate")}))
    for name in ("a", "b"):
        q = quantity(["eq", ["const", "bp", name], ["num", "bp", "0"]])
        canonical, _ = elaborate_quantity(env, q)
        sentence = render_quantity_sentence(env, canonical)
        assert parse_quantity_sentence(env, sentence) == canonical


def roundtrip_env(words):
    return Environment(raw_environment(
        {"bp": {"scale": "100", "display": {"kind": "percent"}},
         "day": {"scale": "1", "display": {"kind": "iso_date"}},
         "elapsed_day": {"scale": "1", "display": {"kind": "decimal", "label": "days"}}},
        {f"c{i}": named("bp", w) for i, w in enumerate(words)}
        | {"start": named("day", "the start"), "span": named("elapsed_day", "the span")}))


NAME_POOL = ["the rate", "the Rate", "rate", "Rate", "the rate equals", "the old rate", "rate.",
             "the rate is", "the rate minus", "equals the rate", "0", "3.75%", "the 3.75% rate",
             "the  rate", "the rate "]


def test_render_then_parse_is_identity_or_rejected_never_another_reading():
    """Over admitted name sets, a rendered sentence parses to its own formula or is
    rejected (ambiguity or a literal-shaped name); it is never read as another."""
    checked = 0
    for words in product(NAME_POOL, repeat=2):
        try:
            env = roundtrip_env(words)
        except VEError:
            continue
        terms = [["const", "bp", "c0"], ["const", "bp", "c1"], ["decimal", "bp", "3.75"]]
        for op, left, right in product(("eq", "lt"), terms, terms):
            if left[0] == right[0] == "decimal":
                continue
            canonical, _ = elaborate_quantity(env, quantity([op, left, right]))
            sentence = render_quantity_sentence(env, canonical)
            try:
                back = parse_quantity_sentence(env, sentence)
            except (AmbiguousDerivation, VEError):
                continue
            assert back == canonical, (words, sentence)
            checked += 1
    assert checked > 500


WHOLE_POOL = ["the rate", "The rate", "c0", "c1", "start", "the c1", "c1 rate", "rate",
              "the rate equals", "0", "3.75%"]


def test_whole_grammar_reads_a_rendering_as_itself_or_rejects():
    """The document route's parser (quantity wordings plus the frozen English
    grammar over the erased target) never reads a rendering as another formula,
    including when a name spells another constant's identifier."""
    from ve.surface.time import parse_w6_sentence
    checked = 0
    for words in product(WHOLE_POOL, repeat=2):
        try:
            env = roundtrip_env(words)
        except VEError:
            continue
        terms = [["const", "bp", "c0"], ["const", "bp", "c1"], ["decimal", "bp", "3.75"]]
        for op, left, right in product(("eq", "lt", "le"), terms, terms):
            if left[0] == right[0] == "decimal":
                continue
            canonical, _ = elaborate_quantity(env, quantity([op, left, right]))
            sentence = render_quantity_sentence(env, canonical)
            try:
                back = parse_w6_sentence(env, sentence)
            except VEError:
                continue
            assert back == canonical, (words, sentence)
            checked += 1
    assert checked > 200


def test_review_reproducer_cannot_be_declared():
    raw = raw_environment(constants={"a": named("bp", "the  rate"), "b": named("bp", "the rate")})
    with pytest.raises(VEError, match="whitespace-normalized"):
        Environment(raw)


# --- P2: every admitted coordinate's rendering reparses ------------------------

def extreme_coordinates():
    return [0, 1, -1, 9, -9, 10 ** 38, -(10 ** 38), int("9" * 40), -int("9" * 39),
            10 ** 39, -(10 ** 38) - 1, int("1" * 40), -int("1" * 39)]


@pytest.mark.parametrize("places", range(0, 40))
def test_every_scale_renders_every_admitted_coordinate_reparsably(places):
    raw = raw_environment({"q": label("units") | {"scale": "1" + "0" * places}})
    env = Environment(raw)
    lean_cases, rust_cases, expected = [], [], []
    for coordinate in extreme_coordinates():
        assert len(str(coordinate)) <= 40
        display = render_coordinate("q", coordinate, env)
        amount = display.removesuffix(" units")
        assert decimal_exact(amount, "q", env) == coordinate, display
        lean_cases.append({"id": amount, "kind": "lower", "decimal": amount, "places": places})
        lean_cases.append({"id": "r", "kind": "render", "coordinate": str(coordinate), "places": places})
        rust_cases.append({"id": amount, "kind": "quantity", "environment": raw,
                           "quantity": quantity(["eq", ["decimal", "q", amount],
                                                 ["num", "q", str(coordinate)]])})
        expected.append((amount, coordinate))
    results = lean(lean_cases)
    for (amount, coordinate), lowered, rendered in zip(expected, results[::2], results[1::2]):
        assert lowered["status"] == "ok" and lowered["coordinate"] == str(coordinate), lowered
        assert rendered["amount"] == amount
    for got in rust(rust_cases):
        assert got["status"] == "ok", got


def test_review_reproducers_round_trip_through_english():
    for scale, coordinate in (("100", int("9" * 40)), ("1" + "0" * 39, 1),
                              ("1" + "0" * 39, -int("9" * 39))):
        env = Environment(raw_environment(
            {"bp": {"scale": scale, "display": {"kind": "percent"}}},
            {"rate": named("bp", "the rate")}))
        q = quantity(["eq", ["const", "bp", "rate"], ["num", "bp", str(coordinate)]])
        canonical, _ = elaborate_quantity(env, q)
        sentence = render_quantity_sentence(env, canonical)
        assert parse_quantity_sentence(env, sentence) == canonical


def test_literals_over_forty_digits_still_reject_three_ways():
    raw = raw_environment()
    env = Environment(raw)
    for text in ("1" * 41, "-" + "1" * 41, "1." + "0" * 40, "0." + "0" * 39 + "1"):
        formula = ["eq", ["decimal", "bp", text], ["num", "bp", "0"]]
        with pytest.raises(ResourceLimit, match="40 digits"):
            elaborate_quantity(env, quantity(formula))
        [got] = lean([{"id": "l", "environment": raw, "quantity": quantity(formula)}])
        assert "40 digits" in got["error"]
        [other] = rust([{"id": "l", "kind": "quantity", "environment": raw, "quantity": quantity(formula)}])
        assert "40 digits" in other["error"]["message"]


# --- P2: Lean evaluates under the Python/Rust budget ---------------------------

def counting_raw():
    return raw_environment({}, sorts={"item": {"description": "an item"}}, predicates={
        name: {"arguments": ["item"], "description": name} for name in ("p", "s")})


def counting_model(n):
    entities = [f"e{i}" for i in range(1, n + 1)]
    return {"complete": True, "domains": {"item": entities}, "constants": {},
            "relations": {name: [[e] for e in entities] for name in ("p", "s")}}


PINNED = [
    (8, "at least 8", True, 359),
    (6, "exactly 6", True, 120536),
    (6, "6 of 6", True, 244997),
    (7, "exactly 7", None, None),
    (7, "7 of 7", None, None),
    (7, "at least 8", None, None),
]


def pinned_formula(env, name):
    p, s = ast.Unary("p", ast.Var(0)), ast.Unary("s", ast.Var(0))
    return {"at least 8": lambda: at_least(env, "item", 8, p),
            "exactly 6": lambda: exactly(env, "item", 6, p),
            "6 of 6": lambda: n_of_m(env, "item", 6, 6, s, p),
            "exactly 7": lambda: exactly(env, "item", 7, p),
            "7 of 7": lambda: n_of_m(env, "item", 7, 7, s, p)}[name]()


def test_pinned_counting_fixtures_evaluate_identically_three_ways():
    raw = counting_raw()
    env = Environment(raw)
    target = erased_environment(env)
    cases, expected = [], []
    for n, name, value, work in PINNED:
        data = ast._to_data(pinned_formula(env, name))
        result = evaluate(target, ast.formula_from_data(target, data),
                          FiniteModel.from_dict(target, counting_model(n)), trace=False)
        assert result.value is value
        if work is not None:
            assert result.evaluations == work
        cases.append({"id": name, "environment": raw, "quantity": quantity(data),
                      "model": counting_model(n)})
        expected.append((value, work))
    for case, got, other, (value, work) in zip(cases, lean(cases),
                                                rust([{**c, "kind": "quantity"} for c in cases]),
                                                expected):
        if value is None:
            # UNKNOWN naming the budget: never false, never a successful evaluation.
            assert got["status"] == "error" and "ResourceLimit" in got["error"], got
            assert "MAX_EVALUATIONS" in got["error"]
            assert other["status"] == "error" and other["error"]["code"] == "ResourceLimit", other
        else:
            assert got["status"] == "ok" and got["value"] is value and got["evaluations"] == work, got
            assert other["status"] == "ok" and other["value"] is value, other


def test_countermodels_share_the_budget_three_ways():
    raw = counting_raw()
    env = Environment(raw)
    seven = ast._to_data(pinned_formula(env, "exactly 7"))
    six = ast._to_data(pinned_formula(env, "exactly 6"))
    # Premise evaluation exhausts the budget: UNKNOWN, not "does not refute".
    for premises, conclusion, model, refutes in (
            ([quantity(seven)], quantity(["bottom"]), counting_model(7), None),
            ([], quantity(["not", seven]), counting_model(7), None),
            ([quantity(six)], quantity(["bottom"]), counting_model(6), True),
            ([quantity(["bottom"])], quantity(seven), counting_model(7), False)):
        case = {"environment": raw, "premises": premises, "conclusion": conclusion, "model": model}
        [got] = lean([{"id": "m", "kind": "countermodel", **case}])
        [other] = rust([{"id": "m", "kind": "quantity", "mode": "countermodel", **case}])
        if refutes is None:
            with pytest.raises(ResourceLimit, match="MAX_EVALUATIONS"):
                quantity_countermodel(env, premises, conclusion, model)
            assert got["status"] == "error" and "ResourceLimit" in got["error"], got
            assert other["status"] == "error" and other["error"]["code"] == "ResourceLimit", other
        else:
            assert quantity_countermodel(env, premises, conclusion, model) is refutes
            assert got["status"] == "ok" and got["refutes"] is refutes, got
            assert other["status"] == "ok" and other["refutes"] is refutes, other


def test_lean_budget_theorems_are_audited():
    audit = (ROOT / "lean" / "VE" / "Audit.lean").read_text()
    for name in ("evalB_sound", "refutesB_sound", "quantB_sound"):
        assert f"#print axioms VE.Time.{name}\n" in audit


# --- P2: the calendar inverse is unconditional -------------------------------

def test_calendar_inverse_statement_is_unconditional():
    source = (ROOT / "lean" / "VE" / "Time" / "Calendar.lean").read_text()
    assert "theorem civilOf_num {D : Civil} (hD : D.Valid) : civilOf D.num = some D" in source
    assert "theorem civilOf_complete {n : Nat} (hn : n ≤ dateMax) :" in source
    audit = (ROOT / "lean" / "VE" / "Audit.lean").read_text()
    for name in ("civilOf_num", "civilOf_complete", "civilCandidate_spec", "civilOf_isSome_iff"):
        assert f"#print axioms VE.Time.{name}\n" in audit


def test_every_month_boundary_converts_like_python():
    from datetime import date, timedelta
    days = set()
    for year in (1970, 1971, 1972, 1999, 2000, 2024, 2100, 2400, 9998, 9999):
        for month in range(1, 13):
            first = date(year, month, 1)
            days.add((first - date(1970, 1, 1)).days)
            days.add((first - date(1970, 1, 1)).days - 1)
            days.add((first - date(1970, 1, 1)).days + 27)
    days = sorted(d for d in days if 0 <= d <= 2932896) + [2932896]
    results = lean([{"id": str(d), "kind": "civil", "day": d} for d in days])
    for d, got in zip(days, results):
        assert got["status"] == "ok" and got["date"] == iso_date(d), (d, got)
    [past] = lean([{"id": "p", "kind": "civil", "day": 2932897}])
    assert past["status"] == "error" and "DateRange" in past["error"]
