"""me-6b: the `ve-units@2` fixtures of math-evidence spec 6.2 (H-7, H-7c, H-7d, H-7l, H-7u and I-2), as one table.

Each row is (key, Lean expression, Lean's expected answer); the key names the spec's fixture. Lean decides every
answer: `tools/calc_units_fixtures.py` renders the table as the `#guard`s of `lean/VE/Calc/UnitsExamples.lean`,
which `lake build` evaluates (and `tools/trust_mutants.py` reads as the checks of `VE.Calc.Units`), and
`tests/test_calc_units.py` prints each answer with Lean, so a failure names its fixture. Python only states the
fixtures. Dimensions alone are `tests/test_calc_dimensions.py`'s.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NEWS = ROOT / "usecases/news-article/w6a-quantity-fixtures.json"


def units(base_dimensions, **declared):
    return {"unit_schema": "ve-units@2", "base_dimensions": base_dimensions,
            "units": {name: {"base_exponents": exps, "factor": factor} for name, (exps, factor) in declared.items()}}


def legacy(**tags):
    environment = json.loads(NEWS.read_text())["environment"]
    return {**environment, "units": {**environment["units"], **{
        tag: {"scale": "1", "display": {"kind": "money", "currency": currency}} for tag, currency in tags.items()}}}


def lean_str(value) -> str:
    """`value`'s JSON text as a Lean string literal."""
    return json.dumps(json.dumps(value, ensure_ascii=False), ensure_ascii=False)


def meter(factor):
    return lean_str(units(["length"], meter=({"length": 1}, factor)))


def spelled(factor) -> str:
    """The meter's factor `factor` as its environment's identity spells it, or the environment's refusal."""
    return (f'says ((fun (u : UnitEnv) => (u.identity.getObjValD "units" |>.getObjValD "meter" |>.getObjValD "factor")'
            f'.compress) <$> (Json.parse {meter(factor)} >>= decode)) id')


def same_id(a, b) -> str:
    """Whether the meter's factor written `a` and written `b` give one `environment_id`."""
    ids = [f"(Json.parse {meter(f)} >>= decode >>= UnitEnv.environmentId)" for f in (a, b)]
    return f"says (do pure ((← {ids[0]}) == (← {ids[1]}))) toString"


PHYSICS = units(["length", "time", "fringe"], meter=({"length": 1}, "1"), kilometer=({"length": 1}, "1000.0"),
                second=({"time": 1}, "1"), meter_per_second=({"length": 1, "time": -1}, "1"),
                fringe_width=({"fringe": 1}, "1"))
# PHYSICS with every factor but one written `["sci", d, e]`; its identity is PHYSICS's (me-6c).
PHYSICS_SCI = units(["length", "time", "fringe"], meter=({"length": 1}, ["sci", "1", 0]),
                    kilometer=({"length": 1}, ["sci", "1", 3]), second=({"time": 1}, ["sci", "10", -1]),
                    meter_per_second=({"length": 1, "time": -1}, ["sci", "0.1", 1]), fringe_width=({"fringe": 1}, "1"))
PHYSICS_ID = "cb0ef65f08f172d62305ff6587cfd41fcea9ee305d8589c739ff7b4ed1563526"
I2 = {"unit_schema": "ve-units@2", "base_dimensions": ["length", "time"],
      "units": {"meter_per_second": {"base_exponents": {"length": 1, "time": -1}, "factor": "1"}}}
I2_REORDERED = {"units": {"meter_per_second": {"factor": "1", "base_exponents": {"time": -1, "length": 1}}},
                "base_dimensions": ["length", "time"], "unit_schema": "ve-units@2"}

# The Lean definitions the fixtures name: (name, type, term).
DEFINITIONS = [
    ("physics", "String", lean_str(PHYSICS)),
    ("physicsSci", "String", lean_str(PHYSICS_SCI)),
    # H-7's names: D and the wavelength are lengths, V and v velocities, T a time; the shift is in fringes.
    ("h7", "List (String × Option String)",
     '[("d", some "meter"), ("lam", some "meter"), ("vv", some "meter_per_second"), ("v", some "meter_per_second"),\n'
     '   ("t", some "second"), ("ratio", none), ("path", some "meter"), ("shift", some "fringe_width")]'),
    ("sigma", "Values", '(fun n => if n = "path" then some 20000000 else if n = "ratio" then some (1/10000) else none)'),
    ("legacyEnv", "String", lean_str(legacy(usd_cent="USD", eur_cent="EUR"))),
    ("newsEnv", "String", lean_str(json.loads(NEWS.read_text())["environment"])),
    ("dOverLam", "Expr", '.div (.val "d") (.val "lam")'),
    ("miles", "String", lean_str(units(["length"], mile=({"length": 1}, "1609.344"), kilometer=({"length": 1}, "1000")))),
    ("i2", "String", lean_str(I2)),
    ("i2Reordered", "String", lean_str(I2_REORDERED)),
]

FIXTURES = [
    # H-7 through the decoder: "D/(V − v)" is a time, "D/λ" is dimensionless, "D + T" is refused naming both.
    ("h7-time", 'dims physics h7 (.div (.val "d") (.sub (.val "vv") (.val "v")))', "ok time"),
    ("h7-ratio", "dims physics h7 dOverLam", "ok dimensionless"),
    ("h7-sum", 'dims physics h7 (.add (.val "d") (.val "t"))', "DimensionMismatch: length and time"),
    ("h7-difference", 'dims physics h7 (.sub (.val "t") dOverLam)', "DimensionMismatch: time and dimensionless"),
    ("h7-frequency", 'dims physics h7 (.div (.lit 3) (.pow (.val "t") 4))', "ok one per time to the power 4"),
    ("normal", 'reprStr ((["meter_per_second", "second"].filterMap (env! physics).unit?).map (decide ·.dim.Normal))',
     "[true, true]"),
    ("h7-number", 'dims physics h7 (.mul (.val "ratio") (.val "d"))', "ok length"),
    ("h7-velocity", 'dims physics h7 (.div (.val "d") (.val "t"))', "ok length per time"),
    ("h7-cube", 'dims physics h7 (.mul (.val "d") (.pow (.val "d") 2))', "ok length cubed"),
    ("h7-squared", 'dims physics h7 (.div (.lit 1) (.mul (.val "t") (.val "t")))', "ok one per time squared"),
    # Two bases on each side of "per" (dimWords' lists, not only their first member).
    ("h7-two-below", 'dims physics h7 (.div (.val "shift") (.mul (.val "d") (.val "t")))',
     "ok fringe per length times time"),
    ("h7-two-below-one", 'dims physics h7 (.div (.lit 1) (.mul (.val "d") (.val "t")))', "ok one per length times time"),
    ("h7-two-above", 'dims physics h7 (.div (.mul (.val "shift") (.val "d")) (.val "t"))',
     "ok fringe times length per time"),
    ("h7-two-above-only", 'dims physics h7 (.mul (.val "shift") (.val "d"))', "ok fringe times length"),
    ("h7-unknown", 'dims physics h7 (.add (.val "d") (.val "absent"))',
     "UnknownName: absent (declare it before the value that uses it)"),
    ("h7-spoken", 'dims physics h7 (.add (.val "shift") (.val "d"))', "DimensionMismatch: fringe and length"),
    # H-7u: a value moves by its unit's dimension's factor.
    ("h7u-values", 'reprStr (["path", "vv", "ratio", "t"].map (ρ.apply (context! physics h7) '
                   '(fun n => if n = "path" then some 20000000 else if n = "vv" then some 3 else '
                   'if n = "ratio" then some (1/10000) else none)))',
     "[some 20000000000, some 1500, some (1 : Rat)/10000, none]"),
    # H-7c: 2.5 kilometers are 2,500 meters, by the ratio of the factors, in any units.
    ("h7c", 'rescaled physics h7 sigma (.compare ⟨.eq, false⟩ (.mul (.lit (5/2)) (.val "kilometer")) '
            '(.mul (.lit 2500) (.val "meter")))', "ok holds holds"),
    ("h7c-n", 'rescaled physics h7 sigma (.compare ⟨.eq, false⟩ (.mul (.lit (5/2)) (.val "kilometer")) '
              '(.mul (.lit (5/2)) (.val "meter")))', "ok fails fails"),
    ("h7c-value", 'reprStr (Expr.eval (env! physics).values (.mul (.lit (5/2)) (.val "kilometer")))', "some 2500"),
    # A factor below one is a factor (gram 0.001, H-9's 0.02), spelled at its shortest.
    ("factor-below-one", f'reprStr ((env! {lean_str(units(["mass"], gram=({"mass": 1}, "0.001")))}).values "gram")',
     "some (1 : Rat)/1000"),
    ("factor-below-one-spelling", f'((env! {lean_str(units(["length"], step=({"length": 1}, "0.020")))}).identity'
                                  '.getObjValD "units" |>.getObjValD "step" |>.compress)',
     '{"base_exponents":{"length":"1"},"factor":"0.02"}'),
    ("factor-spelling", 'says ((env! miles).identity.getObjValD "units" |>.getObjValD "mile" |>.compress |> pure) id',
     'ok {"base_exponents":{"length":"1"},"factor":"1609.344"}'),
    # H-7l: `ve-units@1` tags stay nominal and have no factor.
    ("h7l", 'dims legacyEnv [("a", some "usd_cent"), ("b", some "eur_cent")] (.add (.val "a") (.val "b"))',
     "DimensionMismatch: usd cent and eur cent"),
    ("h7l-same", 'dims legacyEnv [("a", some "usd_cent"), ("b", some "usd_cent")] (.add (.val "a") (.val "b"))',
     "ok usd cent"),
    ("h7l-value", 'reprStr ((env! legacyEnv).values "usd_cent")', "none"),
    ("context-unit", 'dims physics [("d", some "furlong")] (.val "d")', "InvalidInput: values.d.unit names no declared unit"),
    ("context-name", 'dims physics [("meter", none)] (.val "meter")', "DuplicateName: meter"),
    # The claim-level checks of 6.2: one dimension on every side; a rounding claim on a number.
    ("claim-compare", 'check physics h7 (.compare ⟨.lt, false⟩ (.val "d") (.mul (.lit 2) (.val "lam")))', "ok admitted"),
    ("claim-compare-mismatch", 'check physics h7 (.compare ⟨.lt, false⟩ (.val "d") (.val "t"))',
     "DimensionMismatch: length and time"),
    ("claim-compare-inner", 'check physics h7 (.compare ⟨.lt, false⟩ (.add (.val "d") (.val "vv")) (.val "d"))',
     "DimensionMismatch: length and length per time"),
    ("claim-within", 'check physics h7 (.within (.val "d") (.val "lam") (.val "path"))', "ok admitted"),
    ("claim-within-low", 'check physics h7 (.within (.val "d") (.val "t") (.val "path"))',
     "DimensionMismatch: length and time"),
    ("claim-within-high", 'check physics h7 (.within (.val "d") (.val "lam") (.val "vv"))',
     "DimensionMismatch: length and length per time"),
    ("claim-rounds", 'check physics h7 (.rounds .tiesUp (.div (.val "shift") (.val "fringe_width")) ⟨4, 1⟩)',
     "ok admitted"),
    ("claim-rounds-number", "check physics h7 (.rounds .tiesUp dOverLam ⟨4, 1⟩)", "ok admitted"),
    ("claim-rounds-fringe", 'check physics h7 (.rounds .tiesUp (.val "shift") ⟨4, 1⟩)',
     "RoundingNeedsNumber: divide by one fringe width to round the displacement"),
    ("claim-rounds-length", 'check physics h7 (.rounds .down (.mul (.lit 2) (.val "path")) ⟨4, 1⟩)',
     "RoundingNeedsNumber: divide by one meter to round the displacement"),
    ("claim-rounds-velocity", 'check physics h7 (.rounds .tiesUp (.sub (.val "vv") (.val "v")) ⟨4, 1⟩)',
     "RoundingNeedsNumber: divide by one meter per second to round the displacement"),
    ("claim-rounds-no-coherent", 'check miles [("d", some "mile")] (.rounds .tiesUp (.val "d") ⟨4, 1⟩)',
     "RoundingNeedsNumber: divide by one kilometer to round the displacement"),
    ("claim-rounds-no-unit", 'check physics h7 (.rounds .tiesUp (.mul (.val "d") (.val "t")) ⟨4, 1⟩)',
     "RoundingNeedsNumber: divide by one unit of length times time to round the displacement"),
    ("claim-rounds-legacy", 'check legacyEnv [("a", some "usd_cent")] (.rounds .tiesUp (.val "a") ⟨4, 1⟩)',
     "RoundingNeedsNumber: divide by one usd cent to round the displacement"),
    ("claim-rounds-unknown", 'check physics h7 (.rounds .tiesUp (.val "absent") ⟨4, 1⟩)',
     "UnknownName: absent (declare it before the value that uses it)"),
    # H-7d and the other refusals of 6.2; `elapsed_day` and a dimensionless unit are admitted.
    *((f"refuse-{key}", f"decoded {lean_str(env)}", text) for key, env, text in [
        ("day", units(["time"], day=({"time": 1}, "86400")), "CalendarTagNotUnit: day (durations use elapsed_day)"),
        ("celsius", units(["k"], celsius=({"k": 1}, "1")), "AffineUnit: celsius"),
        ("degree-celsius", units(["k"], degree_celsius=({"k": 1}, "1")), "AffineUnit: degree_celsius"),
        ("fahrenheit", units(["k"], fahrenheit=({"k": 1}, "1")), "AffineUnit: fahrenheit"),
        ("degree-fahrenheit", units(["k"], degree_fahrenheit=({"k": 1}, "1")), "AffineUnit: degree_fahrenheit"),
        ("decibel", units([], decibel=({}, "1")), "LogarithmicUnit: decibel"),
        ("bel", units([], bel=({}, "1")), "LogarithmicUnit: bel"),
        ("neper", units([], neper=({}, "1")), "LogarithmicUnit: neper"),
        ("zero", units(["length"], meter=({"length": 1}, "0.0")), "InvalidInput: units.meter.factor must be more than zero"),
        ("negative", units(["length"], meter=({"length": 1}, "-1")),
         "InvalidInput: units.meter.factor must be more than zero"),
        ("negative-below-one", units(["length"], meter=({"length": 1}, "-0.5")),
         "InvalidInput: units.meter.factor must be more than zero"),
        ("number", units(["length"], meter=({"length": 1}, 1)), "InvalidInput: units.meter.factor must be a literal"),
        ("text", units(["length"], meter=({"length": 1}, "1e3")), "InvalidInput: units.meter.factor must be a decimal"),
        ("digits", units(["length"], meter=({"length": 1}, "1" * 41)),
         "ResourceLimit: Decimal literal exceeds 40 digits"),
        ("digits-40", units(["length"], meter=({"length": 1}, "1" * 40)), 'ok ["meter"]'),
        ("base", units(["length"], gram=({"mass": 1}, "0.001")),
         "InvalidInput: units.gram.base_exponents.mass names no base dimension"),
        # Each base dimension is an identifier: one that is not ("Mass", the empty name) is refused.
        ("base-identifier", units(["Mass"]), "InvalidInput: base_dimensions must list identifiers"),
        ("base-empty", units([""]), "InvalidInput: base_dimensions must list identifiers"),
        ("base-identifier-later", units(["length", "Mass"]), "InvalidInput: base_dimensions must list identifiers"),
        ("zero-exponent", units(["length"], meter=({"length": 0}, "1")),
         "InvalidInput: units.meter.base_exponents.length must not be zero"),
        ("fraction", units(["length"], meter=({"length": 1.5}, "1")),
         "InvalidInput: units.meter.base_exponents.length must be an integer"),
        ("bool", units(["length"], meter=({"length": True}, "1")),
         "InvalidInput: units.meter.base_exponents.length must be an integer"),
        ("name", units([], Meter=({}, "1")), "InvalidInput: units.Meter must be an identifier"),
        ("record", {**units([]), "units": {"meter": {"factor": "1"}}}, "InvalidInput: units.meter.base_exponents is missing"),
        ("record-extra", {**units([]), "units": {"meter": {"factor": "1", "base_exponents": {}, "scale": "1"}}},
         "InvalidInput: units.meter.scale is unknown"),
        ("extra", {**units(["length"]), "risk": {}}, "InvalidInput: environment.risk is unknown"),
        ("missing", {"unit_schema": "ve-units@2", "units": {}}, "InvalidInput: environment.base_dimensions is missing"),
        ("repeat", units(["length", "length"]), "InvalidInput: base_dimensions must not repeat a name"),
        ("bases", {**units([]), "base_dimensions": "length"}, "InvalidInput: base_dimensions must be a list"),
        ("schema", {**units(["length"]), "unit_schema": "ve-units@3"},
         'InvalidInput: environment.unit_schema must be "ve-units@2" or "ve-units@1"'),
        ("elapsed", units(["time"], elapsed_day=({"time": 1}, "86400")), 'ok ["elapsed_day"]'),
        ("radian", units([], radian=({}, "1")), 'ok ["radian"]'),
        # A name before "day" in the order of strings is no calendar tag either.
        ("several", units(["length", "mass", "current"], meter=({"length": 1}, "1"), gram=({"mass": 1}, "0.001"),
                          ampere=({"current": 1}, "1")), 'ok ["ampere", "gram", "meter"]'),  # in key order
    ]),
    # I-2: exponents hash as canonical decimal strings, factors at their shortest; key order is not identity.
    ("i2-text", "says (VE.CertificateWire.canonical 257 (env! i2).identity) id",
     'ok {"base_dimensions":["length","time"],"unit_schema":"ve-units@2","units":'
     '{"meter_per_second":{"base_exponents":{"length":"1","time":"-1"},"factor":"1"}}}'),
    ("i2-id", "says (env! i2).environmentId id",
     "ok 448c08512dd76f488354a57f1811e10464d6a369e3c955f1ea87d8661ee1e8fd"),
    ("i2-reordered", "says (env! i2Reordered).environmentId id",
     "ok 448c08512dd76f488354a57f1811e10464d6a369e3c955f1ea87d8661ee1e8fd"),
    ("i2-raw", "says (Json.parse i2 >>= VE.CertificateWire.canonical 257) id", "Natural number expected"),
    ("i2-factor", 'says ((env! physics).identity.getObjValD "units" |>.getObjValD "kilometer" |>.compress |> pure) id',
     'ok {"base_exponents":{"length":"1"},"factor":"1000"}'),
    # A `ve-units@1` environment is hashed as written, and W6a's own identity of it is the one
    # `tests/data/route-cases.jsonl` records.
    ("i2-legacy", 'says (Json.parse newsEnv >>= fun j => do let u ← decode j; '
                  'pure (toString (u.identity.compress == j.compress) ++ " " ++ '
                  '(← VE.Time.Wire.decodeEnvironment j).environmentId)) id',
     "ok true b4a20af92b499f3c44cab20a05cb687ffa980b23af4697bcd579282fe19a5c33"),
    # me-6c: factors written `["sci", d, e]` (3.1's literal; DRI 2026-10-27 item 6). (i) A `sci` factor and its plain
    # decimal give one identity and the same answers (11: no `sci` exponent remains).
    ("sci-physics-id", "says (env! physicsSci).environmentId id", f"ok {PHYSICS_ID}"),
    ("sci-physics-id-plain", "says (env! physics).environmentId id", f"ok {PHYSICS_ID}"),
    ("sci-values", 'reprStr (["meter", "kilometer", "second", "meter_per_second"].map (env! physicsSci).values)',
     "[some 1, some 1000, some 1, some 1]"),
    ("sci-values-plain", 'reprStr (["meter", "kilometer", "second", "meter_per_second"].map (env! physics).values)',
     "[some 1, some 1000, some 1, some 1]"),
    ("sci-h7c", 'rescaled physicsSci h7 sigma (.compare ⟨.eq, false⟩ (.mul (.lit (5/2)) (.val "kilometer")) '
                '(.mul (.lit 2500) (.val "meter")))', "ok holds holds"),
    ("sci-h7c-n", 'rescaled physicsSci h7 sigma (.compare ⟨.eq, false⟩ (.mul (.lit (5/2)) (.val "kilometer")) '
                  '(.mul (.lit (5/2)) (.val "meter")))', "ok fails fails"),
    ("sci-h7-time", 'dims physicsSci h7 (.div (.val "d") (.sub (.val "vv") (.val "v")))', "ok time"),
    *((f"sci-same-{key}", same_id(a, b), want) for key, a, b, want in [
        ("small", ["sci", "5.89", -7], "0.000000589", "ok true"),
        ("large", ["sci", "2", 7], "20000000", "ok true"),
        ("places", ["sci", "0.020", 1], "0.2", "ok true"),
        ("nano", ["sci", "1", -9], "0.000000001", "ok true"),
        ("other", ["sci", "2", 6], "20000000", "ok false"),  # a different value is a different identity
    ]),
    *((f"sci-{key}", spelled(literal), want) for key, literal, want in [
        ("spelling", ["sci", "2", 7], 'ok "20000000"'),
        ("spelling-small", ["sci", "5.89", -7], 'ok "0.000000589"'),
        ("spelling-places", ["sci", "0.020", 1], 'ok "0.2"'),
        ("spelling-exponent-zero", ["sci", "1609.344", 0], 'ok "1609.344"'),
        ("spelling-integer", ["sci", "1.5", 3], 'ok "1500"'),
        ("spelling-whole", ["sci", "10", -1], 'ok "1"'),
        # (ii) Limit 5 (3.2): an exponent of 64 in absolute value is read, 65 is refused, on both sides of zero.
        ("exponent-63", ["sci", "1", 63], f'ok "1{"0" * 63}"'),
        ("exponent-64", ["sci", "1", 64], f'ok "1{"0" * 64}"'),
        ("exponent-65", ["sci", "1", 65], "ResourceLimit: an exponent exceeds 64"),
        ("exponent-minus-63", ["sci", "1", -63], f'ok "0.{"0" * 62}1"'),
        ("exponent-minus-64", ["sci", "1", -64], f'ok "0.{"0" * 63}1"'),
        ("exponent-minus-65", ["sci", "1", -65], "ResourceLimit: an exponent exceeds 64"),
        ("exponent-1000", ["sci", "1", 1000], "ResourceLimit: an exponent exceeds 64"),
        ("exponent-minus-1000", ["sci", "1", -1000], "ResourceLimit: an exponent exceeds 64"),
        ("exponent-first", ["sci", "1" * 41, 65], "ResourceLimit: an exponent exceeds 64"),  # limit 5 before 6
        # (iii) A zero or negative `sci` factor is refused; the nearest positive ones are read.
        ("zero", ["sci", "0", 5], "InvalidInput: units.meter.factor must be more than zero"),
        ("zero-places", ["sci", "0.000", -64], "InvalidInput: units.meter.factor must be more than zero"),
        ("negative", ["sci", "-1", 3], "InvalidInput: units.meter.factor must be more than zero"),
        ("negative-small", ["sci", "-5.89", -7], "InvalidInput: units.meter.factor must be more than zero"),
        ("positive-small", ["sci", "0.001", -64], f'ok "0.{"0" * 66}1"'),
        # Limit 6 and the literal's own form.
        ("digits", ["sci", "1" * 41, 0], "ResourceLimit: Decimal literal exceeds 40 digits"),
        ("digits-40", ["sci", "1" * 40, -30], f'ok "{"1" * 10}.{"1" * 30}"'),
        ("integer", ["sci", "1", 1.5], "InvalidInput: units.meter.factor.2 must be an integer"),
        ("integer-text", ["sci", "1", "3"], "InvalidInput: units.meter.factor.2 must be an integer"),
        ("decimal", ["sci", "1e3", 3], "InvalidInput: units.meter.factor must be a decimal"),
        ("number", ["sci", 1, 3], "InvalidInput: units.meter.factor must be a literal"),
        ("short", ["sci", "1"], "InvalidInput: units.meter.factor must be a literal"),
        ("long", ["sci", "1", 3, 4], "InvalidInput: units.meter.factor must be a literal"),
        ("tag", ["lit", "1"], "InvalidInput: units.meter.factor must be a literal"),
        # me-6cc: a factor's shape is checked before its limits; limits apply only to literal factors. Each shape a
        # limit of 3.2 reads in a case, on both sides of that limit, and `sci` nested; a `sci` list keeps its limits.
        *((key, literal, "InvalidInput: units.meter.factor must be a literal") for key, literal in [
            ("shape-pow-64", ["pow", "1", 64]),
            ("shape-pow-65", ["pow", "1", 65]),
            ("shape-lit-40", ["lit", "1" * 40]),
            ("shape-lit-41", ["lit", "1" * 41]),
            ("shape-rounds-40", ["rounds-x", 1, "1" * 40]),
            ("shape-rounds-41", ["rounds-x", 1, "1" * 41]),
            ("shape-stated-40", {"stated": "1" * 40}),
            ("shape-stated-41", {"stated": "1" * 41}),
            ("shape-nested", [["sci", "1", 65]]),
            ("shape-sci-long-65", ["sci", "1", 65, 4]),
        ]),
        ("shape-sci-short-41", ["sci", "1" * 41], "ResourceLimit: Decimal literal exceeds 40 digits"),
    ]),
]

# Malformed environments (checklist item 5): I-2 with one node replaced by 7, true, null, [], {} or 10,000 nested
# lists (`deep`). Each answer is stated whole, its JSON path included. The answer at each path for a replacement
# that is not an object (or not a string, a list or an integer, as the path asks), then the replacements whose
# answer differs.
SCHEMA = 'InvalidInput: environment.unit_schema must be "ve-units@2" or "ve-units@1"'
BAD = (7, True, None, [], {}, "deep")
UNIT = "units.meter_per_second"
MALFORMED_ANSWERS = {
    (): (SCHEMA, {}),
    ("unit_schema",): (SCHEMA, {}),
    ("base_dimensions",): ("InvalidInput: base_dimensions must be a list",
                           {"[]": f"InvalidInput: {UNIT}.base_exponents.length names no base dimension",
                            "deep": "InvalidInput: base_dimensions must list identifiers"}),
    ("base_dimensions", 0): ("InvalidInput: base_dimensions must list identifiers", {}),
    ("base_dimensions", 1): ("InvalidInput: base_dimensions must list identifiers", {}),
    ("units",): ("InvalidInput: units must be an object", {"{}": "ok []"}),
    ("units", "meter_per_second"): (f"InvalidInput: {UNIT} must be an object",
                                    {"{}": f"InvalidInput: {UNIT}.base_exponents is missing"}),
    ("units", "meter_per_second", "base_exponents"): (f"InvalidInput: {UNIT}.base_exponents must be an object",
                                                      {"{}": 'ok ["meter_per_second"]'}),
    ("units", "meter_per_second", "base_exponents", "length"): (
        f"InvalidInput: {UNIT}.base_exponents.length must be an integer", {"7": 'ok ["meter_per_second"]'}),
    ("units", "meter_per_second", "base_exponents", "time"): (
        f"InvalidInput: {UNIT}.base_exponents.time must be an integer", {"7": 'ok ["meter_per_second"]'}),
    ("units", "meter_per_second", "factor"): (f"InvalidInput: {UNIT}.factor must be a literal", {}),
}


def paths(value, path=()):
    """Every node's path in `value`."""
    yield path
    children = value.items() if isinstance(value, dict) else enumerate(value) if isinstance(value, list) else ()
    for key, child in children:
        yield from paths(child, path + (key,))


def put(value, path, bad):
    if not path:
        return bad
    copy = json.loads(json.dumps(value))
    copy[path[0]] = put(value[path[0]], path[1:], bad) if len(path) > 1 else bad
    return copy


def deep_text(value) -> str:
    """`decoded` of `value`'s JSON text, with each `"deep"` string as 10,000 nested lists (Lean's `deep`)."""
    parts = json.dumps(value, ensure_ascii=False).split('"deep"')
    return "decoded (" + " ++ deep ++ ".join(json.dumps(part, ensure_ascii=False) for part in parts) + ")"


MALFORMED = [(f"malformed-{'.'.join(map(str, path)) or 'environment'}-{json.dumps(bad).strip(chr(34))}",
              deep_text(put(I2, path, bad)),
              MALFORMED_ANSWERS[path][1].get(json.dumps(bad).strip('"'), MALFORMED_ANSWERS[path][0]))
             for path in paths(I2) for bad in BAD]
