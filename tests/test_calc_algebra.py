"""ME-9: algebraic identities (math-evidence spec 8.2, plan 3.8; fixtures H-1, H-2, H-3, R-6's false identity).

Lean decides every answer here: one Lean file evaluates each fixture with `VE.Calc.Poly`, and the tests read its
printed lines. Python only states the fixtures. Inlining named values (H-4, R-6's named sides), the meaning
`IsIdentity`, the runner and its point search are me-9b's; R-10c waits for ME-4.
"""
import json
import shutil
import subprocess

import pytest

from subprocesses import HANG_TIMEOUT
from tests.lean_build import LEAN, lean_build

HEADER = """import VE.Calc.Poly
open VE.Calc

def v (n : String) : Expr := .val n
def l (q : Rat) : Expr := .lit q
def sq (e : Expr) : Expr := .pow e 2
def twoD : Expr := .mul (l 2) (v "D")
/-- H-1: D/(V − v) + D/(V + v) = 2DV/(V² − v²). -/
def h1 : Expr × Expr :=
  (.add (.div (v "D") (.sub (v "V") (v "v"))) (.div (v "D") (.add (v "V") (v "v"))),
   .div (.mul twoD (v "V")) (.sub (sq (v "V")) (sq (v "v"))))
/-- H-2: 2DV²/(V² − v²) − 2D(1 + v²/V²) = 2Dv⁴/(V²(V² − v²)). -/
def h2 : Expr × Expr :=
  (.sub (.div (.mul twoD (sq (v "V"))) (.sub (sq (v "V")) (sq (v "v"))))
        (.mul twoD (.add (l 1) (.div (sq (v "v")) (sq (v "V"))))),
   .div (.mul twoD (.pow (v "v") 4)) (.mul (sq (v "V")) (.sub (sq (v "V")) (sq (v "v")))))
/-- H-3: 2D(1 + v²/V²) − 2D(1 + v²/(2V²)) = Dv²/V². -/
def h3 : Expr × Expr :=
  (.sub (.mul twoD (.add (l 1) (.div (sq (v "v")) (sq (v "V")))))
        (.mul twoD (.add (l 1) (.div (sq (v "v")) (.mul (l 2) (sq (v "V")))))),
   .div (.mul (v "D") (sq (v "v"))) (sq (v "V")))
/-- The false (a + b)² = a² + b² (plan ME-9, R-6's `sq`). -/
def binom : Expr × Expr := (sq (.add (v "a") (v "b")), .add (sq (v "a")) (sq (v "b")))
/-- x/(x − 1) · (x − 1) = x holds wherever its left side denotes; 1/(x − 1) = 1 does not. -/
def cancel : Expr × Expr := (.mul (.div (v "x") (.sub (v "x") (l 1))) (.sub (v "x") (l 1)), v "x")
def recip : Expr × Expr := (.div (l 1) (.sub (v "x") (l 1)), l 1)
/-- x + … + x (k + 1 times): 2k + 1 nodes. -/
def sumx (k : Nat) : Expr := (List.range k).foldl (fun e _ => .add e (v "x")) (v "x")
/-- n + n² + … + nᵏ, and 1 + n + … + nᵏ. -/
def powers (n : String) (k : Nat) : Expr := (List.range (k - 1)).foldl (fun e i => .add e (.pow (v n) (i + 2))) (v n)
def geo (n : String) (k : Nat) : Expr := .add (l 1) (powers n k)
/-- Four products of 50 × 50 terms with no term in common: 10,000 terms. -/
def four : Expr :=
  .add (.add (.add (.mul (powers "x" 50) (powers "y" 50)) (.mul (powers "x" 50) (powers "z" 50)))
    (.mul (powers "y" 50) (powers "z" 50))) (.mul (powers "x" 50) (powers "w" 50))
/-- A side that shares itself: 2⁴¹ − 1 nodes as a tree, 41 in memory. -/
def doubled : Expr := (List.range 40).foldl (fun e _ => .add e e) (v "x")
def wide {α} [Repr α] (x : α) : String := (repr x).pretty 1000
def check (p : Expr × Expr) : String := reprStr (identityCheck p.1 p.2)
def compare (p : Expr × Expr) : String := reprStr (Identity.compare p.1 p.2)
def at' (p : Expr × Expr) (κ : List (String × Rat)) : String :=
  reprStr (differsAt p.1 p.2 κ, p.1.eval (κ.lookup ·), p.2.eval (κ.lookup ·))
def line (key value : String) : IO Unit := IO.println (key ++ "\\t" ++ value)
"""

# (key, Lean expression, Lean's expected answer); the key names the spec's fixture.
FIXTURES = [
    # H-1, H-2, H-3 with D, V and v free: identities.
    ("h1", "check h1", "true"),
    ("h2", "check h2", "true"),
    ("h3", "check h3", "true"),
    # Where V = v the left side of H-1 denotes nothing, so no point there refutes it (spec 13.3).
    ("h1-at-v", 'at\' h1 [("D", 11), ("V", 3), ("v", 3)]', "(false, none, none)"),
    ("h1-point", 'at\' h1 [("D", 11), ("V", 3), ("v", 1)]', "(false, some (33 : Rat)/4, some (33 : Rat)/4)"),
    ("h2-flipped", "check (h2.1, .sub (l 0) h2.2)", "false"),
    # The false (a + b)² = a² + b², and the point a = b = 1 where the sides are 4 and 2.
    ("binom", "check binom", "false"),
    ("binom-compare", "compare binom", "some false"),
    ("binom-point", 'at\' binom [("a", 1), ("b", 1)]', "(true, some 4, some 2)"),
    ("binom-expanded", "check (binom.1, .add binom.2 (.mul (l 2) (.mul (v \"b\") (v \"a\"))))", "true"),
    # Normal forms: sorted variables and monomials, like terms merged, zeros dropped; their value.
    ("binom-form", "wide (Poly.ofExpr? binom.1)",
     'some [{ coeff := 2, vars := [("a", 1), ("b", 1)] }, { coeff := 1, vars := [("a", 2)] }, '
     '{ coeff := 1, vars := [("b", 2)] }]'),
    ("binom-value", 'reprStr ((Poly.ofExpr? binom.1).map (Poly.eval fun n => if n = "a" then 2 else 3))', "some 25"),
    ("distinct-terms", 'reprStr ((Poly.ofExpr? (.add (.mul (v "a") (v "b")) (.mul (v "a") (v "c")))).map List.length)',
     "some 2"),
    ("commute", 'check (.mul (v "x") (v "y"), .mul (v "y") (v "x"))', "true"),
    ("square", 'check (.mul (v "x") (v "x"), sq (v "x"))', "true"),
    ("zero", 'reprStr (Poly.ofExpr? (.sub (v "x") (v "x")))', "some []"),
    ("division-has-no-polynomial", 'reprStr (Poly.ofExpr? (.div (v "x") (l 1)))', "none"),
    # A division by an expression that can be zero denotes nothing at that point.
    ("cancel", "check cancel", "true"),
    ("cancel-at-1", 'at\' cancel [("x", 1)]', "(false, none, some 1)"),
    ("recip", "check recip", "false"),
    ("recip-at-1", 'at\' recip [("x", 1)]', "(false, none, some 1)"),
    ("recip-at-2", 'at\' recip [("x", 2)]', "(false, some 1, some 1)"),
    ("recip-at-3", 'at\' recip [("x", 3)]', "(true, some (1 : Rat)/2, some 1)"),
    ("recip-form", "wide (Frac.ofExpr? recip.1)",
     'some ([{ coeff := 1, vars := [] }], [{ coeff := -1, vars := [] }, { coeff := 1, vars := [("x", 1)] }])'),
    # Limits (spec 3.2, `limit .polyTerms`): at and just past each one, never a verdict past it.
    ("nodes-10000", 'compare ((sumx 4999).pow 1, .mul (l 5000) (v "x"))', "some true"),
    ("nodes-10001", 'compare (sumx 5000, .mul (l 5001) (v "x"))', "none"),
    ("nodes-10001-pow", 'compare (((sumx 4999).pow 1).pow 1, .mul (l 5000) (v "x"))', "none"),
    ("nodes-shared", 'compare (doubled, .mul (l 1099511627776) (v "x"))', "none"),
    ("product-10000", 'compare (.mul (geo "x" 99) (geo "y" 99), .mul (geo "y" 99) (geo "x" 99))', "some true"),
    ("product-10100", 'compare (.mul (geo "x" 100) (geo "y" 99), .mul (geo "y" 99) (geo "x" 100))', "none"),
    ("sum-10000", "reprStr ((Frac.ofExpr? four).map (·.1.length))", "some 10000"),
    ("sum-10001", "reprStr ((Frac.ofExpr? (.add four (l 1))).map (·.1.length))", "none"),
    ("digits-4096", "reprStr ((Poly.ofExpr? (.pow (l 10) 4095)).map List.length)", "some 1"),
    ("digits-4097", "reprStr (Poly.ofExpr? (.pow (l 10) 4096))", "none"),
    ("exponent-4096", 'check (.pow (v "x") 4096, .pow (.pow (v "x") 64) 64)', "true"),
    ("exponent-4097", 'compare (.mul (.pow (v "x") 4096) (v "x"), .pow (v "x") 4097)', "none"),
    ("exponent-4097-product", 'compare (.mul (.pow (v "x") 4096) (v "x"), .mul (v "x") (.pow (v "x") 4096))', "none"),
    ("over-the-limit-is-not-an-identity", 'check (sumx 5000, .mul (l 5001) (v "x"))', "false"),
]


@pytest.fixture(scope="module")
def lean(tmp_path_factory):
    lake = shutil.which("lake")
    if lake is None:
        pytest.skip("lake is not available")
    lean_build("VE")
    source = tmp_path_factory.mktemp("algebra") / "Algebra.lean"
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
