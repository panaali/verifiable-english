"""The W6a ground family through Python's relay of Lean's quantity typing.

Rust's quantity route was deleted by Lean-first batch 9 (Lean decides; Python relays);
these were its parity tests, kept for the relay's answers. Lean's own route tests are
`test_units_lean_w6a.py`."""
import json
from pathlib import Path

import pytest

from ve.ast import formula_from_data
from ve import ast
from ve.environment import Environment
from ve.evaluate import evaluate
from ve.errors import VEError
from ve.model import FiniteModel
from ve.units import elaborate_quantity, erased_environment, quantity_meaning_id
from ve.surface.count import at_least

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "usecases" / "news-article" / "w6a-quantity-fixtures.json"


def test_news_regeneration_ids_and_evaluation_agree():
    fixture = json.loads(FIXTURE.read_text())
    env = Environment(fixture["environment"])
    target = erased_environment(env)
    model_data = fixture["model"]
    model = FiniteModel.from_dict(target, model_data)
    for item in fixture["cases"]:
        payload = {"format": "ve-quantity@1", "formula": item["formula"]}
        canonical, core = elaborate_quantity(env, payload)
        assert canonical == {"format": "ve-quantity@1", "formula": canonical["formula"], "traces": []}
        assert len(quantity_meaning_id(env, payload)) == 64
        assert evaluate(target, formula_from_data(target, core), model, trace=False).value is True


def test_hostile_literal_and_tag_changes_reject_in_both():
    fixture = json.loads(FIXTURE.read_text())
    env = Environment(fixture["environment"])
    cases = [
        (["eq", ["decimal", "bp", "3.755"], ["num", "bp", "375"]], "UnitPrecision"),
        (["eq", ["num", "bp", "375"], ["num", "calendar_year", "375"]], "UnitMismatch"),
        (["eq", ["num", "bp", "0"], ["num", "0"]], "UnitMismatch"),
        (["eq", ["add", "bp", ["num", "bp", "1"], ["num", "calendar_year", "1"]],
          ["num", "bp", "2"]], "UnitMismatch"),
        (["eq", ["date", "1969-12-31"], ["num", "day", "0"]], "DateRange"),
    ]
    for formula, message in cases:
        payload = {"format": "ve-quantity@1", "formula": formula}
        with pytest.raises(VEError, match=message):
            elaborate_quantity(env, payload)
    payload = {"format": "ve-quantity@1", "formula": ["eq", ["decimal", "bp", "3.75"],
                                                        ["num", "bp", "375"]],
               "Q": ["eq", ["num", "bp", "376"], ["num", "bp", "375"]]}
    with pytest.raises(VEError, match="Q differs"):
        elaborate_quantity(env, payload)


def test_user_sort_counting_expansion_agrees_on_a_finite_model():
    raw = {"language": "ve.core@0.2", "profiles": ["order@0", "relational-fol@0", "time@0"],
           "spec_revision": "ve-v0.2-expand2-2026-09-25",
           "vocabulary": {"sorts": {"item": {"description": "item"}},
                          "predicates": {"p": {"arguments": ["item"], "description": "P"}},
                          "constants": {}}, "unit_schema": "ve-units@1", "units": {}}
    env = Environment(raw)
    expanded = at_least(env, "item", 2, ast.Unary("p", ast.Var(0)))
    payload = {"format": "ve-quantity@1", "formula": ast._to_data(expanded)}
    canonical, core = elaborate_quantity(env, payload)
    target = erased_environment(env)
    model_data = {"complete": True, "domains": {"item": ["e1", "e2"]},
                  "constants": {}, "relations": {"p": [["e1"], ["e2"]]}}
    model = FiniteModel.from_dict(target, model_data)
    assert canonical["formula"] == payload["formula"]
    assert evaluate(target, formula_from_data(target, core), model, trace=False).value is True


def test_display_collision_rejects():
    fixture = json.loads(FIXTURE.read_text())
    raw = fixture["environment"]
    raw["units"]["other_percent"] = {"scale": "100", "display": {"kind": "percent"}}
    with pytest.raises(VEError, match="DisplayCollision"):
        Environment(raw)


def test_integer_predicate_slot_is_checked_before_erasure():
    raw = json.loads(FIXTURE.read_text())["environment"]
    raw["vocabulary"]["predicates"]["reported"] = {
        "arguments": ["$int"], "argument_units": {"0": "bp"}, "description": "reported rate"}
    env = Environment(raw)
    good = {"format": "ve-quantity@1", "formula": ["unary", "reported", ["num", "bp", "375"]]}
    canonical, core = elaborate_quantity(env, good)
    assert canonical["formula"] == good["formula"]
    assert core == ["unary", "reported", ["num", "375"]]
    bad = {"format": "ve-quantity@1", "formula": ["unary", "reported", ["num", "calendar_year", "375"]]}
    with pytest.raises(VEError, match="UnitMismatch"):
        elaborate_quantity(env, bad)


# --- Review regressions: every class the deleted Rust route decided ------------

from tests.test_w6a_review_regressions import (COLLIDING_UNITS, IDENTITY_VARIANTS, money,
                                               raw_environment)


def _quantity(raw, formula=("top",), **more):
    return elaborate_quantity(Environment(raw), {"format": "ve-quantity@1", "formula": list(formula), **more})


def test_every_display_collision_class_rejects():
    for units in COLLIDING_UNITS:
        with pytest.raises(VEError, match="DisplayCollision"):
            Environment(raw_environment(units))


def test_non_normalized_display_strings_reject():
    for text in ["", " $", "$  ", "U\tS", "US\u00a0 $", "a  b", "US\u2003$", "US\x1c$"]:
        with pytest.raises(VEError):
            Environment(raw_environment({"usd": money("USD", text)}))
    _quantity(raw_environment({"usd": money("USD", "US$ ")}))


def test_the_undeclared_date_tag_rejects():
    for formula in (["date_on", ["date", "2026-09-16"], ["date", "2026-09-16"]],
                    ["eq", ["date", "2026-09-16"], ["date", "2026-09-16"]]):
        with pytest.raises(VEError, match=r"UnknownUnit\(day\)"):
            _quantity(raw_environment({}), formula)


def test_identities_are_lean_s_on_every_spelling():
    """Every submitted spelling is bound by the identity Lean's check mode answers, and the
    relay's three identities agree with the environment Python constructed from it."""
    from ve.backends.relay import decide
    payload = {"format": "ve-quantity@1", "formula": ["top"]}
    for variant in IDENTITY_VARIANTS:
        raw = raw_environment(variant.get("units"), variant.get("constants"),
                              predicates=variant.get("predicates"))
        env = Environment(raw)
        [row] = decide("check", [{"id": "v", "environment": raw, "quantity": payload}])
        assert row["environment_id"] == env.environment_id
        assert row["meaning_id"] == quantity_meaning_id(env, payload)
        assert row["target_environment_id"] == erased_environment(env).environment_id


def test_traces_sorts_profiles_and_literals_are_gated():
    trace = {"name": "w", "tick_tag": "dimensionless", "origin": "e", "horizon": "1"}
    raw = raw_environment(sorts={"item": {"description": "i"}},
                          constants={"e": {"sort": "item", "description": "e"}})
    with pytest.raises(VEError, match="numbers2"):
        _quantity(raw, traces=[trace])
    rejected = []
    for sort in ("bp", "dimensionless"):
        rejected.append(raw_environment(sorts={sort: {"description": "s"}}))
    for profiles in (["data@0", "order@0", "relational-fol@0", "time@0"],
                     ["definitions@0", "order@0", "relational-fol@0", "time@0"]):
        changed = raw_environment()
        changed["profiles"] = profiles
        rejected.append(changed)
    rejected.append(raw_environment(constants={"s": {"sort": "$string"}}))
    rejected.append(raw_environment(constants={"c": {"sort": "$int", "description": "c",
                                                     "verbalisation": 3}}))
    for raw in rejected:
        with pytest.raises(VEError):
            Environment(raw)
    documents = raw_environment()
    documents["profiles"] = ["documents@1", "order@0", "relational-fol@0", "time@0"]
    _quantity(documents)


def test_invalid_date_is_reported_before_date_range():
    raw = raw_environment({"day": {"scale": "1", "display": {"kind": "iso_date"}}})
    for spelling, message in (("1969-13-45", "InvalidDate"), ("0000-01-01", "InvalidDate"),
                              ("1969-12-31", "DateRange"), ("2100-02-29", "InvalidDate"),
                              ("2000-02-29", None)):
        formula = ["date_on", ["date", spelling], ["date", spelling]]
        if message is None:
            _quantity(raw, formula)
            continue
        with pytest.raises(VEError, match=message):
            _quantity(raw, formula)


def test_formula_and_term_depth_are_budgeted_separately():
    raw = raw_environment()
    term = ["num", "bp", "1"]
    for _ in range(60):
        term = ["add", "bp", term, ["num", "bp", "1"]]
    formula = ["eq", term, term]
    for _ in range(60):
        formula = ["not", formula]
    canonical, _ = _quantity(raw, formula)
    assert canonical["formula"] == formula
    deep = ["not", ["top"]]
    for _ in range(64):
        deep = ["not", deep]
    with pytest.raises(VEError, match="depth"):
        _quantity(raw, deep)


def test_either_w6_field_takes_lean_s_decoder():
    """`units` without `unit_schema` (or the reverse) is decided by Lean's W6 decoder, which
    names the missing field; Python raises Lean's text (Lean-first batch 9)."""
    for missing in ("unit_schema", "units"):
        raw = raw_environment()
        raw.pop(missing)
        with pytest.raises(VEError) as caught:
            Environment(raw)
        assert str(caught.value).startswith("fields do not match: expected [language, profiles, "
                                            "spec_revision, vocabulary, unit_schema, units]"), caught.value


# --- kb-8c: the shown quantity values come from the `quantity` mode's admission row (decision D13) -------

PAYLOAD = {"format": "ve-quantity@1", "formula": ["eq", ["date", "2026-09-16"], ["date", "2026-09-16"]]}


def _spied(monkeypatch):
    """Every relay call `ve.units` makes, with the rows Lean answered."""
    from ve.backends import relay
    calls, original = [], relay.decide

    def spy(mode, cases, **options):
        rows = original(mode, cases, **options)
        calls.append((mode, cases, rows))
        return rows

    monkeypatch.setattr(relay, "decide", spy)
    return calls


def test_the_shown_values_are_the_quantity_admission_rows(monkeypatch):
    """`_checked_quantity` asks the `quantity` mode's admission kind (no `kind`, no `model`: the answer
    `quantity_admission_wire_sound_plain` states) and shows its `Q`, `core` and `meaning_id` as answered."""
    from ve.units import core_formula
    env = Environment(raw_environment({"day": {"scale": "1", "display": {"kind": "iso_date"}}}))
    calls = _spied(monkeypatch)
    canonical, core = elaborate_quantity(env, PAYLOAD)
    meaning_id = quantity_meaning_id(env, PAYLOAD)
    target, formula = core_formula(env, PAYLOAD)
    # core_formula also types the core in the erased environment (ve.ast's `check` typing case, no `quantity`)
    assert not [case for mode, cases, _ in calls if mode != "quantity" for case in cases if "quantity" in case]
    calls = [call for call in calls if call[0] == "quantity"]
    assert len(calls) == 3
    for mode, [case], [row] in calls:
        assert set(case) == {"id", "environment", "quantity"}
        assert case["quantity"] == PAYLOAD and row["environment_id"] == env.environment_id
        assert set(row) == {"id", "status", "assurance", "Q", "core", "meaning_id", "core_meaning_id",
                            "environment_id", "target_environment_id"}
    row = calls[0][2][0]
    assert canonical == {"format": "ve-quantity@1", "formula": row["Q"], "traces": []} and core == row["core"]
    assert meaning_id == row["meaning_id"] and formula == formula_from_data(target, row["core"])


@pytest.mark.parametrize("entry", ["elaborate_quantity", "quantity_meaning_id", "core_formula"])
def test_an_admission_row_of_another_environment_is_refused(monkeypatch, entry):
    """The row's `environment_id` is bound to the request's environment: a genuine row rebound to another
    environment's identity is `CheckerUnavailable` at every entry that shows its values, never a value."""
    from ve import units
    from ve.backends import relay
    from ve.errors import CheckerUnavailable
    env = Environment(raw_environment({"day": {"scale": "1", "display": {"kind": "iso_date"}}}))
    [genuine] = relay.decide("quantity", [{"id": "quantity", "environment": env.to_dict(), "quantity": PAYLOAD}])
    other = Environment(raw_environment()).environment_id
    assert other != env.environment_id
    for rebound in (other, "0" * 64):
        monkeypatch.setattr(relay, "decide", lambda mode, cases, **options: [{**genuine, "environment_id": rebound}])
        with pytest.raises(CheckerUnavailable, match="W6 environment identity mismatch"):
            getattr(units, entry)(env, PAYLOAD)


RETYPES = [None, True, 7, 1.5, "x", "\ud800", [], {}, "a" * 64, "deep", "deleted"]


@pytest.mark.parametrize("field", ["environment_id", "Q", "core", "meaning_id"])
def test_a_retyped_admission_field_fails_the_schema(field):
    """The four fields `_checked_quantity` reads are typed by the `quantity` mode's schema: the genuine exchange
    passes, and every retype of one of them, sent as bytes through the service's decoder, is refused."""
    from tests.lean_build import lean_build
    from tests.subprocesses import HANG_TIMEOUT
    from ve.backends.lean_service import LeanService, _decode_json, case_digest, case_texts
    from ve.backends.service_schema import Invalid, check_response
    env = Environment(raw_environment({"day": {"scale": "1", "display": {"kind": "iso_date"}}}))
    cases = [{"id": "quantity", "environment": env.to_dict(), "quantity": PAYLOAD}]
    text = json.dumps(cases, ensure_ascii=False, separators=(",", ":"))
    with LeanService(lean_build("ve_service") / "ve_service", timeout=HANG_TIMEOUT) as service:
        _, response = service.exchange("quantity", text, 1, timeout=HANG_TIMEOUT)
    request = {"id": response["id"], "mode": "quantity", "cases": cases,
               "digests": [case_digest(t) for t in case_texts(text)], "bytes": len(text.encode())}
    check_response("quantity", _decode_json(json.dumps(response).encode()), request)
    genuine = response["results"][0]["result"]
    for value in RETYPES:
        if value == genuine[field] or (field == "meaning_id" or field == "environment_id") and value == "a" * 64:
            continue  # a hex64 is a well-typed identity; its binding is the test above
        mutant = json.loads(json.dumps(response))
        if value == "deleted":
            del mutant["results"][0]["result"][field]
        else:
            mutant["results"][0]["result"][field] = value
        line = json.dumps(mutant).replace('"deep"', "[" * 10_000 + "]" * 10_000).encode()
        with pytest.raises((Invalid, ValueError)):
            check_response("quantity", _decode_json(line), request)
