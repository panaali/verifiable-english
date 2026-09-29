"""Seven W6a date operations: endpoint and duration behavior on frozen core."""
from ve.ast import formula_from_data
from ve.environment import Environment
from ve.evaluate import evaluate
from ve.model import FiniteModel
from ve.units import elaborate_quantity, erased_environment


def fixture():
    env = Environment({"language": "ve.core@0.2",
        "profiles": ["order@0", "relational-fol@0", "time@0"],
        "spec_revision": "ve-v0.2-expand2-2026-09-25",
        "vocabulary": {"sorts": {}, "predicates": {}, "constants": {}},
        "unit_schema": "ve-units@1",
        "units": {"day": {"scale": "1", "display": {"kind": "iso_date"}},
                  "elapsed_day": {"scale": "1", "display": {"kind": "decimal", "label": "days"}}}})
    core_env = erased_environment(env)
    model = FiniteModel.from_dict(core_env, {"complete": True, "domains": {},
                                             "constants": {}, "relations": {}})
    return env, core_env, model


def truth(env, core_env, model, formula):
    _, core = elaborate_quantity(env, {"format": "ve-quantity@1", "formula": formula})
    result = evaluate(core_env, formula_from_data(core_env, core), model, trace=False)
    assert result.status in ("Satisfied", "Violated")
    return result.value


def d(s):
    return ["date", s]


def test_exact_endpoints_and_signed_duration():
    env, core_env, model = fixture()
    sept16, sept17, sept18 = map(d, ("2026-09-16", "2026-09-17", "2026-09-18"))
    assert truth(env, core_env, model, ["date_on", sept16, sept16])
    assert not truth(env, core_env, model, ["date_on", sept17, sept16])
    assert truth(env, core_env, model, ["date_before", sept16, sept17])
    assert not truth(env, core_env, model, ["date_before", sept17, sept17])
    assert truth(env, core_env, model, ["date_after", sept17, sept16])
    assert not truth(env, core_env, model, ["date_after", sept16, sept16])
    assert truth(env, core_env, model, ["date_no_later", sept16, sept16])
    assert not truth(env, core_env, model, ["date_no_later", sept17, sept16])
    assert truth(env, core_env, model, ["within_days", sept16, sept16, "0"])
    assert not truth(env, core_env, model, ["within_days", sept17, sept16, "0"])
    assert truth(env, core_env, model, ["within_days", sept18, sept16, "2"])
    assert not truth(env, core_env, model, ["within_days", sept16, sept17, "2"])
    assert truth(env, core_env, model, ["shift_days", sept17, sept16, "1"])
    assert not truth(env, core_env, model, ["shift_days", sept18, sept16, "1"])
    assert truth(env, core_env, model, ["elapsed_days", sept17, sept16,
                                        ["num", "elapsed_day", "-1"]])
    assert not truth(env, core_env, model, ["elapsed_days", sept17, sept16,
                                            ["num", "elapsed_day", "1"]])


def test_leap_crossing_and_range_guard():
    env, core_env, model = fixture()
    assert truth(env, core_env, model, ["shift_days", d("2000-03-01"), d("2000-02-28"), "2"])
    assert not truth(env, core_env, model, ["shift_days", d("9999-12-31"), d("9999-12-31"), "1"])
