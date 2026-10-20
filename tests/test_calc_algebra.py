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

HEADER = """import Lean
import VE.Calc.Poly
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
/-- A side that shares itself: 2ᵏ⁺¹ − 1 nodes as a tree, k + 1 in memory. -/
def doubled (k : Nat) : Expr := (List.range k).foldl (fun e _ => .add e e) (v "x")
/-- 10⁴⁰⁹⁶ − 1, the largest numerator or denominator within the digit limit (4,096 digits); 10⁴⁰⁹⁶ is one past it. -/
def top : Rat := 10 ^ 4096 - 1
def big : Rat := 10 ^ 4096
def wide {α} [Repr α] (x : α) : String := (repr x).pretty 1000
def check (p : Expr × Expr) : String := reprStr (identityCheck p.1 p.2)
def compare (p : Expr × Expr) : String := reprStr (Identity.compare p.1 p.2)
def at' (p : Expr × Expr) (κ : List (String × Rat)) : String :=
  reprStr (differsAt p.1 p.2 κ, p.1.eval (κ.lookup ·), p.2.eval (κ.lookup ·))
/-- One line per fixture, whatever its answer prints, so a wrong answer fails only its own fixture. -/
def line (key value : String) : IO Unit := IO.println (key ++ "\\t" ++ value.replace "\\n" "\\\\n")
def form (e : Expr) : String := reprStr (Frac.ofExpr? e).isSome
def nodes (e : Expr) : String := reprStr ((e.nodesWithin 100000).map (100000 - ·))
open Lean in
/-- The definitions of `VE.Calc.Poly`, theorems aside, whose value reads a limit: each one is in the limit table. -/
def limitReaders : CoreM String := do
  let env ← getEnv
  let limits := [``maxPolyTerms, ``maxPolyExponent, ``Poly.coeffBound]
  let poly := env.getModuleIdx? `VE.Calc.Poly
  let names := env.constants.toList.filterMap fun (n, c) =>
    if poly.isSome && env.getModuleIdxFor? n == poly && !(c matches .thmInfo _) &&
        (c.value?.map fun v => limits.any v.getUsedConstants.contains).getD false then some n.toString else none
  return String.intercalate " " (names.toArray.qsort (· < ·)).toList
"""

# Every limit check of `VE.Calc.Poly`, by the declaration that makes it (REPORT.md, "Limit truth table"). A row is
# (check, key, side, other side or None, at the limit). Exactly at its limit a side is answered; exactly one past
# it, it is `none`. A row with one side gives two fixtures: `{key}`, whether the side has a fraction form, and
# `{key}-compare`, the side compared with itself, so past a limit even that is no identity. A row with two sides
# gives `{key}`, their comparison (`some true` at the limit, `none` past it), and `{key}-form`, whether the first
# side has a fraction form: `compare` multiplies each side by the other's denominator, which checks the term count
# again, so the form is what pins a check of one factor only (recheck F8's hunt).
LIMIT_CHECKS = {
    "nodes": ("VE.Calc.Frac.ofExpr?", "e.nodesWithin maxPolyTerms: at most 10,000 nodes in a side"),
    "sum": ("VE.Calc.Poly.add?", "p.length + q.length ≤ maxPolyTerms: at most 10,000 terms in a sum"),
    "product": ("VE.Calc.Poly.mul?", "p.length * q.length ≤ maxPolyTerms: at most 10,000 terms in a product"),
    "power": ("VE.Calc.Poly.pow?", "k ≤ maxPolyExponent: a power node's exponent at most 4,096"),
    "exponent": ("VE.Calc.Poly.fits", "each variable's exponent ≤ maxPolyExponent, in every monomial"),
    "numerator": ("VE.Calc.Poly.fits", "num.natAbs < Poly.coeffBound: at most 4,096 digits, either sign"),
    "denominator": ("VE.Calc.Poly.fits", "den < Poly.coeffBound: at most 4,096 digits"),
}


def digit_rows():
    """ME-1's digit limit (2.4), for each sign and each side of the line: `top` (10^4096 − 1, 4,096 digits) is at
    it, `big` (10^4096, 4,097 digits) one past it. At it by a literal and by a product; past it by a literal, a
    product and a sum, so each place that builds a polynomial (`Frac.go`'s literal, `mul?`, `add?`) is pinned."""
    for sign, minus in (("", ""), ("neg-", "-")):
        yield from (("numerator", f"digits-{sign}{kind}", side, None, kind.startswith("4096")) for kind, side in (
            ("4096", f"l ({minus}top)"),
            ("4096-product", f".mul (l ({minus}top / 9)) (l 9)"),
            ("4097-literal", f"l ({minus}big)"),
            ("4097", f".mul (.pow (l 10) 4095) (l ({minus}10))"),
            ("4097-sum", f".add (l ({minus}top)) (l ({minus}1))"),
        ))
        yield from (("denominator", f"digits-{sign}den-{kind}", side, None, kind.startswith("4096")) for kind, side in (
            ("4096", f"l ({minus}1 / top)"),
            ("4096-product", f".mul (l ({minus}9 / top)) (l (1 / 9))"),
            ("4097-literal", f"l ({minus}1 / big)"),
            ("4097", f".mul (.pow (l (1 / 10)) 4095) (l ({minus}1 / 10))"),
            # (2^4096 + 5^4096) / 10^4096 is in lowest terms: the sum is odd and 1 modulo 5.
            ("4097-sum", f".add (l ({minus}1 / 5 ^ 4096)) (l ({minus}1 / 2 ^ 4096))"),
        ))


LIMITS = [
    ("nodes", "nodes-10000", "(sumx 4999).pow 1", '.mul (l 5000) (v "x")', True),
    ("nodes", "nodes-10001", "sumx 5000", '.mul (l 5001) (v "x")', False),
    ("nodes", "nodes-10001-pow", "((sumx 4999).pow 1).pow 1", '.mul (l 5000) (v "x")', False),
    ("nodes", "nodes-10001-right", '.add (v "x") (sumx 4999)', '.mul (l 5001) (v "x")', False),
    # A side that shares itself, 2^15 − 1 nodes as a tree: past the limit, and cheap to normalise if it is let
    # through; `test_a_shared_side_costs_only_the_limit` has one of 2^41 − 1.
    ("nodes", "nodes-shared", "doubled 14", '.mul (l 16384) (v "x")', False),
    ("sum", "sum-10000", "four", None, True),
    ("sum", "sum-10001", ".add four (l 1)", None, False),
    # 100 × 100, 73 × 137 (review F8: exactly one past) and 101 × 100 terms.
    ("product", "product-10000", '.mul (geo "x" 99) (geo "y" 99)', '.mul (geo "y" 99) (geo "x" 99)', True),
    ("product", "product-10001", '.mul (geo "x" 72) (geo "y" 136)', '.mul (geo "y" 136) (geo "x" 72)', False),
    ("product", "product-10100", '.mul (geo "x" 100) (geo "y" 99)', '.mul (geo "y" 99) (geo "x" 100)', False),
    # A constant base, where only the power node's guard refuses.
    ("power", "exponent-constant-4096", ".pow (l 1) 4096", None, True),
    ("power", "exponent-constant-4097", ".pow (l 1) 4097", None, False),
    # Exponents reached by products; past the limit in the middle variable of three and the middle monomial of four,
    # so a check of the first or the last one only is caught.
    ("exponent", "exponent-4096", '.mul (.pow (v "x") 2048) (.pow (v "x") 2048)', '.pow (.pow (v "x") 64) 64', True),
    ("exponent", "exponent-4097", '.mul (.pow (v "x") 4096) (v "x")', '.pow (v "x") 4097', False),
    ("exponent", "exponent-4097-product", '.mul (.pow (v "x") 4096) (v "x")', '.mul (v "x") (.pow (v "x") 4096)',
     False),
    ("exponent", "exponent-4097-middle-var", '.mul (.pow (v "y") 4096) (.mul (v "x") (.mul (v "y") (v "z")))', None,
     False),
    ("exponent", "exponent-4097-middle-term", '.mul (.add (.pow (v "x") 4096) (v "z")) (.add (v "x") (v "z"))', None,
     False),
    # 10 + 10^4096·x + 10z: past the digit limit in the middle monomial of three.
    ("numerator", "digits-middle-term", '.mul (.add (.add (l 1) (.mul (.pow (l 10) 4095) (v "x"))) (v "z")) (l 10)',
     None, False),
    *digit_rows(),
]


def limit_fixtures():
    for _, key, side, other, at in LIMITS:
        if other is None:
            yield key, f"form ({side})", repr(at).lower()
            yield f"{key}-compare", f"compare ({side}, {side})", "some true" if at else "none"
        else:
            yield key, f"compare ({side}, {other})", "some true" if at else "none"
            yield f"{key}-form", f"form ({side})", repr(at).lower()


# The size of each side the table puts at or one past a limit, so its place is checked, not assumed.
SIZES = [
    ("size-nodes-9999", "nodes (sumx 4999)", "some 9999"),
    ("size-nodes-right", 'nodes (.add (v "x") (sumx 4999))', "some 10001"),
    ("size-four", "reprStr ((Frac.ofExpr? four).map (·.1.length))", "some 10000"),
    ("size-geo-99", 'reprStr ((Poly.ofExpr? (geo "x" 99)).map List.length)', "some 100"),
    ("size-geo-100", 'reprStr ((Poly.ofExpr? (geo "x" 100)).map List.length)', "some 101"),
    ("size-geo-72", 'reprStr ((Poly.ofExpr? (geo "x" 72)).map List.length)', "some 73"),
    ("size-geo-136", 'reprStr ((Poly.ofExpr? (geo "y" 136)).map List.length)', "some 137"),
    ("size-top", "reprStr ((toString top.num).length, (toString big.num).length, top.den)", "(4096, 4097, 1)"),
    ("size-past-sum-den", "reprStr ((1 / 5 ^ 4096 + 1 / 2 ^ 4096 : Rat).den == 10 ^ 4096)", "true"),
]

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
    ("zero-literal", "reprStr (Poly.ofExpr? (l 0))", "some []"),
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
    # Limits (spec 3.2, `limit .polyTerms`): the table above, at and one past each one, never a verdict past it.
    *limit_fixtures(),
    *SIZES,
    ("over-the-limit-is-not-an-identity", 'check (sumx 5000, .mul (l 5001) (v "x"))', "false"),
]


def run_lean(path, fixtures, extra=""):
    lake = shutil.which("lake")
    if lake is None:
        pytest.skip("lake is not available")
    lean_build("VE")
    path.write_text(HEADER + "".join(f"#eval line {json.dumps(key)} ({expression})\n"
                                     for key, expression, _ in fixtures) + extra)
    done = subprocess.run([lake, "env", "lean", str(path)], cwd=LEAN, capture_output=True, text=True,
                          timeout=HANG_TIMEOUT)
    assert done.returncode == 0, done.stdout + done.stderr
    return dict(row.split("\t", 1) for row in done.stdout.splitlines())


@pytest.fixture(scope="module")
def lean(tmp_path_factory):
    return run_lean(tmp_path_factory.mktemp("algebra") / "Algebra.lean", FIXTURES,
                    '#eval show Lean.CoreM Unit from do line "limit-readers" (← limitReaders)\n')


@pytest.mark.parametrize("key, expected", [pytest.param(key, expected, id=key) for key, _, expected in FIXTURES])
def test_fixture(lean, key, expected):
    assert lean[key] == expected


def test_every_fixture_printed_once(lean):
    assert sorted(lean) == sorted([key for key, _, _ in FIXTURES] + ["limit-readers"])


def test_every_limit_check_is_pinned_at_and_past_it(lean):
    """Each definition that reads a limit, as Lean's environment lists them, makes a check of the table (or is the
    limit theorems' predicate `Poly.Within`), and each check has a fixture at its limit and one past it."""
    assert lean["limit-readers"].split() == sorted({owner for owner, _ in LIMIT_CHECKS.values()}
                                                   | {"VE.Calc.Poly.Within"})
    for check in LIMIT_CHECKS:
        assert {at for row, _, _, _, at in LIMITS if row == check} == {True, False}, check
    assert {row for row, _, _, _, _ in LIMITS} == set(LIMIT_CHECKS)


def test_a_shared_side_costs_only_the_limit(tmp_path):
    """2^41 − 1 nodes as a tree, 41 in memory: the node walk stops at the limit, so the answer comes at once. Its own
    process, so a walk that does not stop fails this test alone (by `HANG_TIMEOUT`)."""
    answers = run_lean(tmp_path / "Shared.lean",
                       [("nodes-shared-41", 'compare (doubled 40, .mul (l 1099511627776) (v "x"))', "none")])
    assert answers == {"nodes-shared-41": "none"}
