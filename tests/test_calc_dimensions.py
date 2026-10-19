"""ME-6: physical dimensions and `ve-units@2` (math-evidence spec 6, fixtures H-7, H-7u, H-7c, H-7l, H-7d, I-2).

Lean decides every answer here: one Lean file evaluates each fixture with `VE.Calc.Units` and
`VE.Calc.Dimension`, and the tests read its printed lines. Python only states the fixtures.
"""
import json
from pathlib import Path
import shutil
import subprocess

import pytest

from subprocesses import HANG_TIMEOUT
from tests.lean_build import LEAN, ROOT, lean_build

NEWS = ROOT / "usecases/news-article/w6a-quantity-fixtures.json"


def units(base_dimensions, **declared):
    return {"unit_schema": "ve-units@2", "base_dimensions": base_dimensions,
            "units": {name: {"base_exponents": exps, "factor": factor} for name, (exps, factor) in declared.items()}}


PHYSICS = units(["length", "time"], meter=({"length": 1}, "1"), kilometer=({"length": 1}, "1000.0"),
                second=({"time": 1}, "1"), meter_per_second=({"length": 1, "time": -1}, "1"))
# H-7's names: D and the wavelength are lengths, V and v velocities, T a time.
H7 = '[("d", some "meter"), ("lam", some "meter"), ("vv", some "meter_per_second"), ("v", some "meter_per_second"), ' \
     '("t", some "second"), ("ratio", none), ("path", some "meter")]'
I2 = {"unit_schema": "ve-units@2", "base_dimensions": ["length", "time"],
      "units": {"meter_per_second": {"base_exponents": {"length": 1, "time": -1}, "factor": "1"}}}
I2_REORDERED = {"units": {"meter_per_second": {"factor": "1", "base_exponents": {"time": -1, "length": 1}}},
                "base_dimensions": ["length", "time"], "unit_schema": "ve-units@2"}


def legacy(**tags):
    environment = json.loads(NEWS.read_text())["environment"]
    return {**environment, "units": {**environment["units"], **{
        tag: {"scale": "1", "display": {"kind": "money", "currency": currency}} for tag, currency in tags.items()}}}


def lean_str(value) -> str:
    return json.dumps(json.dumps(value, ensure_ascii=False), ensure_ascii=False)


HEADER = """import VE.Calc.Units
open Lean VE.Calc VE.Calc.Units VE.Numbers

def says {α : Type} (r : Except String α) (f : α → String) : String :=
  match r with | .ok a => "ok " ++ f a | .error e => e
def env! (s : String) : UnitEnv :=
  match Json.parse s >>= decode with | .ok u => u | .error e => ⟨[], .str e⟩
def dims (s : String) (vals : List (String × Option String)) (e : Expr) : String :=
  says (do let Γ ← (env! s).context vals; dimE Γ e) dimWords
/-- Lengths times 1,000 and times 2. -/
def ρ : Rescale := ⟨fun b => if b = "length" then 1000 else if b = "time" then 2 else 1, fun b => by
  by_cases h : b = "length" <;> by_cases h' : b = "time" <;> simp only [h, h', if_true, if_false] <;> decide⟩
instance : DecidablePred PhysDim.Normal := fun d => by unfold PhysDim.Normal; infer_instance
def context! (s : String) (vals : List (String × Option String)) : String → Option PhysDim :=
  match (env! s).context vals with | .ok Γ => Γ | .error _ => fun _ => none
/-- Each claim decided under the values and units, then again in the units `ρ`. -/
def rescaled (s : String) (vals : List (String × Option String)) (σ : Values) (c : Claim) : String :=
  let u := env! s
  let τ : Values := fun n => (σ n).orElse fun _ => u.values n
  let word := fun (v : Verdict) => match v with | .holds => "holds" | .fails => "fails" | .undefined => "undefined"
  says (u.context vals) fun Γ => word (c.decide τ) ++ " " ++ word (c.decide (ρ.apply Γ τ))
def decoded (s : String) : String := says (Json.parse s >>= decode) fun u => reprStr (u.units.map (·.name))
def line (key value : String) : IO Unit := IO.println (key ++ "\\t" ++ value)
"""


P = lean_str(PHYSICS)
SIGMA = '(fun n => if n = "path" then some 20000000 else if n = "ratio" then some (1/10000) else none)'
TWO_PATH_SQ = '(.mul (.mul (.lit 2) (.val "path")) (.pow (.val "ratio") 2))'
LEGACY = lean_str(legacy(usd_cent="USD", eur_cent="EUR"))
NEWS_ENV = lean_str(json.loads(NEWS.read_text())["environment"])

# (key, Lean expression, Lean's expected answer); the key names the spec's fixture.
FIXTURES = [
    # H-7: "D/(V − v)" is a time, "D/λ" is dimensionless, "D + T" is refused naming both.
    ("h7-time", f'dims {P} {H7} (.div (.val "d") (.sub (.val "vv") (.val "v")))', "ok time"),
    ("h7-ratio", f'dims {P} {H7} (.div (.val "d") (.val "lam"))', "ok dimensionless"),
    ("h7-ratio-sum", f'dims {P} {H7} (.add (.div (.val "d") (.val "lam")) (.lit 1))', "ok dimensionless"),
    ("h7-sum", f'dims {P} {H7} (.add (.val "d") (.val "t"))', "DimensionMismatch: length and time"),
    ("h7-difference", f'dims {P} {H7} (.sub (.val "t") (.div (.val "d") (.val "lam")))',
     "DimensionMismatch: time and dimensionless"),
    ("h7-frequency", f'dims {P} {H7} (.div (.lit 3) (.pow (.val "t") 4))', "ok one per time to the power 4"),
    ("h7-dimof", f'reprStr ([.div (.val "d") (.sub (.val "vv") (.val "v")), .div (.val "d") (.val "lam"), '
                 f'.add (.val "d") (.val "t")].map fun (e : Expr) => (e.dimOf (context! {P} {H7})).map dimWords)',
     '[some "time", some "dimensionless", none]'),
    ("normal", f'reprStr ((["meter_per_second", "second"].filterMap (env! {P}).find?).map (decide ·.dim.Normal) ++ '
               '[⟨[("time", 1), ("length", 1)]⟩, ⟨[("length", 0)]⟩, ⟨[("length", 1), ("length", 1)]⟩].map '
               '(decide <| PhysDim.Normal ·))', "[true, true, false, false, false]"),
    ("h7-number", f'dims {P} {H7} (.mul (.val "ratio") (.val "d"))', "ok length"),
    ("h7-velocity", f'dims {P} {H7} (.div (.val "d") (.val "t"))', "ok length per time"),
    ("h7-area", f'dims {P} {H7} (.mul (.val "d") (.pow (.val "d") 2))', "ok length cubed"),
    ("h7-unknown", f'dims {P} {H7} (.add (.val "d") (.val "absent"))',
     "UnknownName: absent (declare it before the value that uses it)"),
    # H-7u: lengths rescaled by 1,000 move no verdict (path 2 × 10^7 meters, ratio 10^-4).
    ("h7u-lt", f'rescaled {P} {H7} {SIGMA} (.compare ⟨.lt, false⟩ {TWO_PATH_SQ} (.val "path"))', "ok holds holds"),
    ("h7u-eq", f'rescaled {P} {H7} {SIGMA} (.compare ⟨.eq, false⟩ {TWO_PATH_SQ} (.mul (.lit (2/5)) (.val "path")))',
     "ok fails fails"),
    ("h7u-rounds", f'rescaled {P} {H7} {SIGMA} (.rounds .tiesUp (.mul (.lit 2) (.pow (.val "ratio") 2)) ⟨2, 8⟩)',
     "ok holds holds"),
    ("h7u-rounds-3", f'rescaled {P} {H7} {SIGMA} (.rounds .tiesUp (.mul (.lit 2) (.pow (.val "ratio") 2)) ⟨3, 8⟩)',
     "ok fails fails"),
    ("h7u-values", f'reprStr (["path", "vv", "ratio", "t"].map (ρ.apply (context! {P} {H7}) '
                   f'(fun n => if n = "path" then some 20000000 else if n = "vv" then some 3 else '
                   f'if n = "ratio" then some (1/10000) else none)))',
     "[some 20000000000, some 1500, some (1 : Rat)/10000, none]"),
    # H-7c: 2.5 kilometers are 2,500 meters, by the ratio of the factors, in any units.
    ("h7c", f'rescaled {P} {H7} {SIGMA} (.compare ⟨.eq, false⟩ (.mul (.lit (5/2)) (.val "kilometer")) '
            f'(.mul (.lit 2500) (.val "meter")))', "ok holds holds"),
    ("h7c-n", f'rescaled {P} {H7} {SIGMA} (.compare ⟨.eq, false⟩ (.mul (.lit (5/2)) (.val "kilometer")) '
              f'(.mul (.lit (5/2)) (.val "meter")))', "ok fails fails"),
    ("h7c-value", f'reprStr (Expr.eval (env! {P}).values (.mul (.lit (5/2)) (.val "kilometer")))', "some 2500"),
    # H-7l: `ve-units@1` tags stay nominal and have no factor.
    ("h7l", f'dims {LEGACY} [("a", some "usd_cent"), ("b", some "eur_cent")] (.add (.val "a") (.val "b"))',
     "DimensionMismatch: usd_cent and eur_cent"),
    ("h7l-same", f'dims {LEGACY} [("a", some "usd_cent"), ("b", some "usd_cent")] (.add (.val "a") (.val "b"))',
     "ok usd_cent"),
    ("h7l-value", f'reprStr ((env! {LEGACY}).values "usd_cent")', "none"),
    ("context-unit", f'dims {P} [("d", some "furlong")] (.val "d")', "InvalidInput: values.d.unit names no declared unit"),
    ("context-name", f'dims {P} [("meter", none)] (.val "meter")', "DuplicateName: meter"),
    # H-7d and the other refusals of 6.2; `elapsed_day` and a dimensionless unit are admitted.
    *((f"refuse-{key}", f"decoded {lean_str(env)}", text) for key, env, text in [
        ("day", units(["time"], day=({"time": 1}, "86400")), "CalendarTagNotUnit: day (durations use elapsed_day)"),
        ("celsius", units(["k"], celsius=({"k": 1}, "1")), "AffineUnit: celsius"),
        ("fahrenheit", units(["k"], degree_fahrenheit=({"k": 1}, "1")), "AffineUnit: degree_fahrenheit"),
        ("decibel", units([], decibel=({}, "1")), "LogarithmicUnit: decibel"),
        ("neper", units([], neper=({}, "1")), "LogarithmicUnit: neper"),
        ("zero", units(["length"], meter=({"length": 1}, "0.0")), "InvalidInput: units.meter.factor must be more than zero"),
        ("negative", units(["length"], meter=({"length": 1}, "-1")),
         "InvalidInput: units.meter.factor must be more than zero"),
        ("number", units(["length"], meter=({"length": 1}, 1)), "InvalidInput: units.meter.factor must be a decimal string"),
        ("text", units(["length"], meter=({"length": 1}, "1e3")), "InvalidInput: units.meter.factor must be a decimal"),
        ("digits", units(["length"], meter=({"length": 1}, "1" * 41)),
         "ResourceLimit: Decimal literal exceeds 40 digits"),
        ("base", units(["length"], gram=({"mass": 1}, "0.001")),
         "InvalidInput: units.gram.base_exponents.mass names no base dimension"),
        ("zero-exponent", units(["length"], meter=({"length": 0}, "1")),
         "InvalidInput: units.meter.base_exponents.length must not be zero"),
        ("fraction", units(["length"], meter=({"length": 1.5}, "1")),
         "InvalidInput: units.meter.base_exponents.length must be an integer"),
        ("bool", units(["length"], meter=({"length": True}, "1")),
         "InvalidInput: units.meter.base_exponents.length must be an integer"),
        ("name", units([], Meter=({}, "1")), "InvalidInput: units.Meter must be an identifier"),
        ("record", {**units([]), "units": {"meter": {"factor": "1"}}}, "InvalidInput: units.meter.base_exponents is missing"),
        ("extra", {**units(["length"]), "risk": {}}, "InvalidInput: environment.risk is unknown"),
        ("repeat", units(["length", "length"]), "InvalidInput: base_dimensions must not repeat a name"),
        ("bases", {**units([]), "base_dimensions": "length"}, "InvalidInput: base_dimensions must be a list"),
        ("schema", {**units(["length"]), "unit_schema": "ve-units@3"},
         'InvalidInput: environment.unit_schema must be "ve-units@2" or "ve-units@1"'),
        ("elapsed", units(["time"], elapsed_day=({"time": 1}, "86400")), 'ok ["elapsed_day"]'),
        ("radian", units([], radian=({}, "1")), 'ok ["radian"]'),
    ]),
    # I-2: exponents hash as canonical decimal strings, factors at their shortest; key order is not identity.
    ("i2-text", f'says (VE.CertificateWire.canonical 257 (env! {lean_str(I2)}).identity) id',
     'ok {"base_dimensions":["length","time"],"unit_schema":"ve-units@2","units":'
     '{"meter_per_second":{"base_exponents":{"length":"1","time":"-1"},"factor":"1"}}}'),
    ("i2-id", f'says (env! {lean_str(I2)}).environmentId id',
     "ok 448c08512dd76f488354a57f1811e10464d6a369e3c955f1ea87d8661ee1e8fd"),
    ("i2-reordered", f'says (env! {lean_str(I2_REORDERED)}).environmentId id',
     "ok 448c08512dd76f488354a57f1811e10464d6a369e3c955f1ea87d8661ee1e8fd"),
    ("i2-raw", f'says (Json.parse {lean_str(I2)} >>= VE.CertificateWire.canonical 257) id', "Natural number expected"),
    ("i2-factor", f'says ((env! {P}).identity.getObjValD "units" |>.getObjValD "kilometer" |>.compress |> pure) id',
     'ok {"base_exponents":{"length":"1"},"factor":"1000"}'),
    # A `ve-units@1` environment is hashed as written, and W6a's own identity of it is the one
    # `tests/data/route-cases.jsonl` records.
    ("i2-legacy", f'says (Json.parse {NEWS_ENV} >>= fun j => do let u ← decode j; '
                  f'pure (toString (u.identity.compress == j.compress) ++ " " ++ '
                  f'(← VE.Time.Wire.decodeEnvironment j).environmentId)) id',
     "ok true b4a20af92b499f3c44cab20a05cb687ffa980b23af4697bcd579282fe19a5c33"),
]



def replaced(value, path=()):
    """Every copy of `value` with one node replaced by a malformed one (checklist item 5)."""
    for bad in (7, True, None, [], {}, "deep"):
        yield path, bad
    children = value.items() if isinstance(value, dict) else enumerate(value) if isinstance(value, list) else ()
    for key, child in children:
        yield from replaced(child, path + (key,))


def put(value, path, bad):
    if not path:
        return bad
    copy = json.loads(json.dumps(value))
    copy[path[0]] = put(value[path[0]], path[1:], bad) if len(path) > 1 else bad
    return copy


MALFORMED = [(f"malformed-{i}", f'decoded {lean_str(put(I2, path, bad))}'.replace(
    '\\"deep\\"', "[" * 10000 + "]" * 10000)) for i, (path, bad) in enumerate(replaced(I2))]
FIXTURES += [(key, expression, None) for key, expression in MALFORMED]


@pytest.fixture(scope="module")
def lean(tmp_path_factory):
    lake = shutil.which("lake")
    if lake is None:
        pytest.skip("lake is not available")
    lean_build("VE")
    source = tmp_path_factory.mktemp("dimensions") / "Dimensions.lean"
    source.write_text(HEADER + "".join(f"#eval line {json.dumps(key)} ({expression})\n"
                                       for key, expression, _ in FIXTURES))
    done = subprocess.run([lake, "env", "lean", str(source)], cwd=LEAN, capture_output=True, text=True,
                          timeout=HANG_TIMEOUT)
    assert done.returncode == 0, done.stdout + done.stderr
    return dict(row.split("\t", 1) for row in done.stdout.splitlines())


@pytest.mark.parametrize("key, expected", [pytest.param(key, expected, id=key) for key, _, expected in FIXTURES if expected])
def test_fixture(lean, key, expected):
    assert lean[key] == expected


def test_malformed_environments_get_a_lean_answer(lean):
    answers = [lean[key] for key, _ in MALFORMED]
    assert all(a.startswith(("ok ", "InvalidInput: ")) for a in answers), [a for a in answers if not a.startswith("I")]
    assert sum(a.startswith("ok ") for a in answers) == 4  # no units, a dimensionless unit, an exponent of 7 (twice)


def test_every_fixture_printed_once(lean):
    assert sorted(lean) == sorted(key for key, _, _ in FIXTURES)


def test_a_change_of_units_has_positive_factors(lean, tmp_path):
    """`Rescale` admits a factor of 1 and no factor of 0: the invariance theorems are about positive changes."""
    def elaborates(factor):
        source = tmp_path / "Factor.lean"
        source.write_text(f"import VE.Calc.Dimension\nexample : VE.Calc.Rescale := ⟨fun _ => {factor}, "
                          "fun _ => by dsimp only; decide⟩\n")
        return subprocess.run([shutil.which("lake"), "env", "lean", str(source)], cwd=LEAN, capture_output=True,
                              text=True, timeout=HANG_TIMEOUT)
    assert elaborates(1).returncode == 0
    refused = elaborates(0)
    assert refused.returncode != 0 and "decide" in refused.stdout, refused.stdout
