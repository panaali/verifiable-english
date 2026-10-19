"""ME-6: physical dimensions (math-evidence spec 6.1; fixtures H-7, H-7u, H-7c, H-7l).

Lean decides every answer here: one Lean file evaluates each fixture with `VE.Calc.Dimension`, and the tests
read its printed lines. Python only states the fixtures. The `ve-units@2` decoder and its fixtures (H-7d, I-2)
are me-6b's.
"""
import json
import shutil
import subprocess

import pytest

from subprocesses import HANG_TIMEOUT
from tests.lean_build import LEAN, lean_build

HEADER = """import VE.Calc.Dimension
open VE.Calc VE.Numbers

def length : PhysDim := ⟨[("length", 1)]⟩
def velocity : PhysDim := ⟨[("length", 1), ("time", -1)]⟩
/-- H-7's names: D, λ, the path and the two units are lengths, V and v velocities, T a time, the ratio a number;
a and b carry two `ve-units@1` tags, c the first again. -/
def Γ : String → Option PhysDim
  | "d" | "lam" | "path" | "meter" | "kilometer" => some length
  | "vv" | "v" => some velocity
  | "t" => some ⟨[("time", 1)]⟩
  | "ratio" => some PhysDim.one
  | "a" | "c" => some (legacyDim "usd_cent")
  | "b" => some (legacyDim "eur_cent")
  | _ => none
/-- H-7u's values (path 2 × 10^7 meters, ratio 10^-4) and the units' factors. -/
def σ : Values
  | "path" => some 20000000 | "vv" => some 3 | "ratio" => some (1/10000)
  | "meter" => some 1 | "kilometer" => some 1000 | _ => none
/-- Lengths times 1,000 and times 2. -/
def ρ : Rescale := ⟨fun b => if b = "length" then 1000 else if b = "time" then 2 else 1, fun b => by
  by_cases h : b = "length" <;> by_cases h' : b = "time" <;> simp only [h, h', if_true, if_false] <;> decide⟩
instance : DecidablePred PhysDim.Normal := fun d => by unfold PhysDim.Normal; infer_instance
def dim (e : Expr) : String := reprStr ((e.dimOf Γ).map (·.exps))
def word : Verdict → String | .holds => "holds" | .fails => "fails" | .undefined => "undefined"
/-- A claim decided in the units `σ` is written in, then in the units `ρ`. -/
def rescaled (c : Claim) : String := word (c.decide σ) ++ " " ++ word (c.decide (ρ.apply Γ σ))
def line (key value : String) : IO Unit := IO.println (key ++ "\\t" ++ value)
"""

D_OVER_LAM = '(.div (.val "d") (.val "lam"))'
TWO_PATH_SQ = '(.mul (.mul (.lit 2) (.val "path")) (.pow (.val "ratio") 2))'
H7 = ['.div (.val "d") (.sub (.val "vv") (.val "v"))', D_OVER_LAM, '.div (.val "d") (.val "t")',
      '.mul (.val "d") (.pow (.val "d") 2)', '.div (.lit 3) (.pow (.val "t") 4)']

# (key, Lean expression, Lean's expected answer); the key names the spec's fixture.
FIXTURES = [
    # H-7: "D/(V − v)" is a time, "D/λ" is dimensionless, "D + T" has none (`DimensionMismatch`).
    ("h7-time", f"dim ({H7[0]})", 'some [("time", 1)]'),
    ("h7-ratio", f"dim {D_OVER_LAM}", "some []"),
    ("h7-sum", 'dim (.add (.val "d") (.val "t"))', "none"),
    ("h7-difference", f'dim (.sub (.val "t") {D_OVER_LAM})', "none"),
    ("h7-ratio-sum", f"dim (.add {D_OVER_LAM} (.lit 1))", "some []"),
    ("h7-velocity", f"dim ({H7[2]})", 'some [("length", 1), ("time", -1)]'),
    ("h7-cube", f"dim ({H7[3]})", 'some [("length", 3)]'),
    ("h7-frequency", f"dim ({H7[4]})", 'some [("time", -4)]'),
    ("h7-number", 'dim (.mul (.val "ratio") (.val "d"))', 'some [("length", 1)]'),
    ("h7-unknown", 'dim (.add (.val "d") (.val "absent"))', "none"),
    # Each dimension above is in normal form; three that are not.
    ("normal", f'reprStr (([{", ".join(H7)}].filterMap (Expr.dimOf Γ)).map (decide ·.Normal) ++ '
               '[⟨[("time", 1), ("length", 1)]⟩, ⟨[("length", 0)]⟩, ⟨[("length", 1), ("length", 1)]⟩].map '
               '(decide <| PhysDim.Normal ·))', "[true, true, true, true, true, false, false, false]"),
    # H-7u: a change of units moves no verdict; the values move by their dimensions' factors.
    ("h7u-lt", f'rescaled (.compare ⟨.lt, false⟩ {TWO_PATH_SQ} (.val "path"))', "holds holds"),
    ("h7u-eq", f'rescaled (.compare ⟨.eq, false⟩ {TWO_PATH_SQ} (.mul (.lit (2/5)) (.val "path")))', "fails fails"),
    ("h7u-rounds", 'rescaled (.rounds .tiesUp (.mul (.lit 2) (.pow (.val "ratio") 2)) ⟨2, 8⟩)', "holds holds"),
    ("h7u-rounds-3", 'rescaled (.rounds .tiesUp (.mul (.lit 2) (.pow (.val "ratio") 2)) ⟨3, 8⟩)', "fails fails"),
    ("h7u-values", 'reprStr (["path", "vv", "ratio", "t"].map (ρ.apply Γ σ))',
     "[some 20000000000, some 1500, some (1 : Rat)/10000, none]"),
    # H-7c: 2.5 kilometers are 2,500 meters, by the ratio of the factors, in any units.
    ("h7c", 'rescaled (.compare ⟨.eq, false⟩ (.mul (.lit (5/2)) (.val "kilometer")) (.mul (.lit 2500) (.val "meter")))',
     "holds holds"),
    ("h7c-n", 'rescaled (.compare ⟨.eq, false⟩ (.mul (.lit (5/2)) (.val "kilometer")) '
              '(.mul (.lit (5/2)) (.val "meter")))', "fails fails"),
    ("h7c-value", 'reprStr (Expr.eval σ (.mul (.lit (5/2)) (.val "kilometer")))', "some 2500"),
    # H-7l: two `ve-units@1` tags stay two dimensions; one tag is one.
    ("h7l", 'dim (.add (.val "a") (.val "b"))', "none"),
    ("h7l-same", 'dim (.add (.val "a") (.val "c"))', 'some [("usd_cent", 1)]'),
]


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


@pytest.mark.parametrize("key, expected", [pytest.param(key, expected, id=key) for key, _, expected in FIXTURES])
def test_fixture(lean, key, expected):
    assert lean[key] == expected


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
