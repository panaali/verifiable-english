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
def check (s : String) (vals : List (String × Option String)) (c : Claim) : String :=
  says (do let u := env! s; checkClaim u (← u.context vals) (fun n => some ("the " ++ n)) c) (fun _ => "")
/-- Each claim decided under the values and units, then again with every length rescaled by 1,000. -/
def rescaled (s : String) (vals : List (String × Option String)) (σ : Values) (c : Claim) : String :=
  let u := env! s
  let ρ : Rescale := ⟨fun b => if b = "length" then 1000 else 1, fun b => by
    by_cases h : b = "length" <;> simp only [h, if_true, if_false] <;> decide⟩
  let τ : Values := fun n => (σ n).orElse fun _ => u.values n
  says (u.context vals) fun Γ => reprStr (c.decide τ) ++ " " ++ reprStr (c.decide (ρ.apply Γ τ))
def line (key value : String) : IO Unit := IO.println (key ++ "\\t" ++ value)
"""


def case(key: str, expression: str) -> str:
    return f"#eval line {json.dumps(key)} ({expression})\n"


def physics(key, expression):
    return case(key, f"dims {lean_str(PHYSICS)} {H7} ({expression})")


CASES = "".join([
    # H-7: "D/(V − v)" is a time, "D/λ" is dimensionless, "D + T" is refused naming both.
    physics("h7-time", '.div (.val "d") (.sub (.val "vv") (.val "v"))'),
    physics("h7-ratio", '.div (.val "d") (.val "lam")'),
    physics("h7-sum", '.add (.val "d") (.val "t")'),
    physics("h7-velocity", '.div (.val "d") (.val "t")'),
    physics("h7-area", '.pow (.val "d") 2'),
    physics("h7-unknown", '.add (.val "d") (.val "absent")'),
    case("h7-compare", f'check {lean_str(PHYSICS)} {H7} (.compare ⟨.lt, false⟩ (.val "d") (.val "t"))'),
    case("h7-within", f'check {lean_str(PHYSICS)} {H7} (.within (.val "d") (.val "lam") (.val "t"))'),
    case("h7-rounds", f'check {lean_str(PHYSICS)} {H7} (.rounds .tiesUp (.val "d") ⟨4, 1⟩)'),
    case("h7-rounds-ratio", f'check {lean_str(PHYSICS)} {H7} (.rounds .tiesUp (.div (.val "d") (.val "lam")) ⟨4, 1⟩)'),
    # H-7u: a change of units moves no verdict (path 2 × 10^7 meters, ratio 10^-4, lengths times 1,000).
    *(case(f"h7u-{name}", f'rescaled {lean_str(PHYSICS)} {H7} (fun n => if n = "path" then some 20000000 else '
                          f'if n = "ratio" then some (1/10000) else none) ({claim})')
      for name, claim in [
          ("lt", '.compare ⟨.lt, false⟩ (.mul (.mul (.lit 2) (.val "path")) (.pow (.val "ratio") 2)) (.val "path")'),
          ("rounds", '.rounds .tiesUp (.mul (.lit 2) (.pow (.val "ratio") 2)) ⟨2, 8⟩'),
          ("eq", '.compare ⟨.eq, false⟩ (.mul (.mul (.lit 2) (.val "path")) (.pow (.val "ratio") 2)) '
                 '(.mul (.lit (2/5)) (.val "path"))'),
          ("rounds-3", '.rounds .tiesUp (.mul (.lit 2) (.pow (.val "ratio") 2)) ⟨3, 8⟩'),
          ("unit", '.compare ⟨.eq, false⟩ (.mul (.lit (5/2)) (.val "kilometer")) (.mul (.lit 2500) (.val "meter"))'),
          ("unit-n", '.compare ⟨.eq, false⟩ (.mul (.lit (5/2)) (.val "kilometer")) (.mul (.lit (5/2)) (.val "meter"))'),
      ]),
    # H-7c: 2.5 kilometers are 2,500 meters, by the ratio of the factors.
    case("h7c", f'reprStr (Expr.eval (env! {lean_str(PHYSICS)}).values (.mul (.lit (5/2)) (.val "kilometer")))'),
    # H-7l: two `ve-units@1` tags declared alike stay two dimensions.
    case("h7l", f'dims {lean_str(legacy(usd_cent="USD", eur_cent="EUR"))} [("a", some "usd_cent"), '
                f'("b", some "eur_cent")] (.add (.val "a") (.val "b"))'),
    case("h7l-same", f'dims {lean_str(legacy(usd_cent="USD", eur_cent="EUR"))} [("a", some "usd_cent"), '
                     f'("b", some "usd_cent")] (.add (.val "a") (.val "b"))'),
    case("h7l-value", f'reprStr ((env! {lean_str(legacy(usd_cent="USD"))}).values "usd_cent")'),
    # H-7d and the other refusals of 6.2.
    *(case(f"refuse-{key}", f'says (Json.parse {lean_str(env)} >>= decode) (fun u => reprStr (u.units.map (·.name)))')
      for key, env in [
          ("day", units(["time"], day=({"time": 1}, "86400"))),
          ("celsius", units(["temperature"], celsius=({"temperature": 1}, "1"))),
          ("fahrenheit", units(["temperature"], degree_fahrenheit=({"temperature": 1}, "1"))),
          ("decibel", units([], decibel=({}, "1"))),
          ("neper", units([], neper=({}, "1"))),
          ("zero", units(["length"], meter=({"length": 1}, "0"))),
          ("negative", units(["length"], meter=({"length": 1}, "-1"))),
          ("number", units(["length"], meter=({"length": 1}, 1))),
          ("base", units(["length"], gram=({"mass": 1}, "0.001"))),
          ("zero-exponent", units(["length"], meter=({"length": 0}, "1"))),
          ("fraction", units(["length"], meter=({"length": 1.5}, "1"))),
          ("bool", units(["length"], meter=({"length": True}, "1"))),
          ("extra", {**units(["length"]), "risk": {}}),
          ("repeat", units(["length", "length"])),
          ("schema", {**units(["length"]), "unit_schema": "ve-units@3"}),
          ("elapsed", units(["time"], elapsed_day=({"time": 1}, "86400"))),
          ("radian", units([], radian=({}, "1"))),
      ]),
    # I-2: exponents hash as canonical decimal strings, key order does not matter, `ve-units@1` as written.
    case("i2-text", f'says (VE.CertificateWire.canonical 257 (env! {lean_str(I2)}).identity) id'),
    case("i2-id", f'says (env! {lean_str(I2)}).environmentId id'),
    case("i2-reordered", f'says (env! {lean_str(I2_REORDERED)}).environmentId id'),
    case("i2-raw", f'says (Json.parse {lean_str(I2)} >>= VE.CertificateWire.canonical 257) id'),
    case("i2-factor", f'says (VE.CertificateWire.canonical 257 (env! {lean_str(PHYSICS)}).identity) id'),
    case("i2-legacy", f'says (Json.parse {lean_str(json.loads(NEWS.read_text())["environment"])} >>= fun j => do '
                      f'let u ← decode j; let a ← u.environmentId; let b ← VE.Route.Wire.environmentId ["calc@0"] j; '
                      f'let w ← VE.Time.Wire.decodeEnvironment j; pure (a ++ " " ++ b ++ " " ++ w.environmentId)) id'),
])


@pytest.fixture(scope="module")
def lean(tmp_path_factory):
    lake = shutil.which("lake")
    if lake is None:
        pytest.skip("lake is not available")
    lean_build("VE")
    source = tmp_path_factory.mktemp("dimensions") / "Dimensions.lean"
    source.write_text(HEADER + CASES)
    done = subprocess.run([lake, "env", "lean", str(source)], cwd=LEAN, capture_output=True, text=True,
                          timeout=HANG_TIMEOUT)
    assert done.returncode == 0, done.stdout + done.stderr
    return dict(row.split("\t", 1) for row in done.stdout.splitlines())


def test_h7_dimensions(lean):
    assert lean["h7-time"] == "ok time"
    assert lean["h7-ratio"] == "ok dimensionless"
    assert lean["h7-sum"] == "DimensionMismatch: length and time"
    assert lean["h7-velocity"] == "ok length per time"
    assert lean["h7-area"] == "ok length squared"
    assert lean["h7-unknown"] == "UnknownName: absent (declare it before the value that uses it)"


def test_claims_need_one_dimension_and_rounding_a_number(lean):
    assert lean["h7-compare"] == "DimensionMismatch: length and time"
    assert lean["h7-within"] == "DimensionMismatch: length and time"
    assert lean["h7-rounds"] == "RoundingNeedsNumber: divide by one meter to round the d"
    assert lean["h7-rounds-ratio"] == "ok "


def test_h7u_a_change_of_units_moves_no_verdict(lean):
    assert lean["h7u-lt"] == "ok VE.Numbers.Verdict.holds VE.Numbers.Verdict.holds"
    assert lean["h7u-rounds"] == "ok VE.Numbers.Verdict.holds VE.Numbers.Verdict.holds"
    assert lean["h7u-eq"] == "ok VE.Numbers.Verdict.fails VE.Numbers.Verdict.fails"
    assert lean["h7u-rounds-3"] == "ok VE.Numbers.Verdict.fails VE.Numbers.Verdict.fails"
    assert lean["h7u-unit"] == "ok VE.Numbers.Verdict.holds VE.Numbers.Verdict.holds"
    assert lean["h7u-unit-n"] == "ok VE.Numbers.Verdict.fails VE.Numbers.Verdict.fails"


def test_h7c_conversion_by_factors(lean):
    assert lean["h7c"] == "some 2500"


def test_h7l_legacy_tags_stay_nominal(lean):
    assert lean["h7l"] == "DimensionMismatch: usd_cent and eur_cent"
    assert lean["h7l-same"] == "ok usd_cent"
    assert lean["h7l-value"] == "none"


@pytest.mark.parametrize("key, text", [
    ("day", "CalendarTagNotUnit: day (durations use elapsed_day)"),
    ("celsius", "AffineUnit: celsius"),
    ("fahrenheit", "AffineUnit: degree_fahrenheit"),
    ("decibel", "LogarithmicUnit: decibel"),
    ("neper", "LogarithmicUnit: neper"),
    ("zero", "InvalidInput: units.meter.factor must be more than zero"),
    ("negative", "InvalidInput: units.meter.factor must be more than zero"),
    ("number", "InvalidInput: units.meter.factor must be a decimal string"),
    ("base", "InvalidInput: units.gram.base_exponents.mass names no base dimension"),
    ("zero-exponent", "InvalidInput: units.meter.base_exponents.length must not be zero"),
    ("fraction", "InvalidInput: units.meter.base_exponents.length must be an integer"),
    ("bool", "InvalidInput: units.meter.base_exponents.length must be an integer"),
    ("extra", "InvalidInput: environment.risk is unknown"),
    ("repeat", "InvalidInput: base_dimensions must not repeat a name"),
    ("schema", 'InvalidInput: environment.unit_schema must be "ve-units@2" or "ve-units@1"'),
    ("elapsed", 'ok ["elapsed_day"]'),
    ("radian", 'ok ["radian"]'),
])
def test_decoder_refusals(lean, key, text):
    assert lean[f"refuse-{key}"] == text


def test_i2_identity(lean):
    assert lean["i2-text"] == ('ok {"base_dimensions":["length","time"],"unit_schema":"ve-units@2","units":'
                               '{"meter_per_second":{"base_exponents":{"length":"1","time":"-1"},"factor":"1"}}}')
    assert lean["i2-id"] == "ok 448c08512dd76f488354a57f1811e10464d6a369e3c955f1ea87d8661ee1e8fd"
    assert lean["i2-reordered"] == lean["i2-id"]
    assert lean["i2-raw"] == "Natural number expected"
    assert json.loads(lean["i2-factor"].removeprefix("ok "))["units"]["kilometer"] == {
        "base_exponents": {"length": "1"}, "factor": "1000"}
    calc, as_written, w6a = lean["i2-legacy"].removeprefix("ok ").split(" ")
    # W6a's own identity of the news environment, as `tests/data/route-cases.jsonl` records it.
    assert calc == as_written and w6a == "b4a20af92b499f3c44cab20a05cb687ffa980b23af4697bcd579282fe19a5c33"
