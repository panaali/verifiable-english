"""ME-9: algebraic identities (math-evidence spec 8.2, plan 3.8; fixtures H-1 to H-4 and R-6).

Lean decides every answer here: one Lean file evaluates each fixture with `VE.Calc.Poly` and `VE.Calc.Identity`, and
the tests read its printed lines. Python only states the fixtures. R-10c waits for ME-4.
"""
import itertools
import json
import math
import shutil
import subprocess
from fractions import Fraction

import pytest

from subprocesses import HANG_TIMEOUT
from tests.lean_build import LEAN, lean_build

HEADER = """import Lean
import VE.Calc.Poly
import VE.Calc.Identity
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
def free (n : String) : Decl := ⟨n, .free⟩
def defd (n : String) (e : Expr) : Decl := ⟨n, .defined e⟩
def counted (n : String) (r : Counted) : Decl := ⟨n, .counted (Thunk.pure none) r⟩
/-- R-6 (spec 13.6): the round-trip and closed-form times over free path, light and speed, and x, y free; then a
counted value that is undefined, one whose budget ran out, and a definition that divides by zero. -/
def r6 : List Decl :=
  [free "path", free "light", free "speed",
   defd "round_trip" (.add (.div (v "path") (.sub (v "light") (v "speed")))
     (.div (v "path") (.add (v "light") (v "speed")))),
   defd "closed_form" (.div (.mul (.mul (l 2) (v "path")) (v "light")) (.sub (sq (v "light")) (sq (v "speed")))),
   free "x", free "y", counted "none" (.ok none), counted "spent" .exhausted,
   defd "zero_rate" (.div (v "path") (.sub (v "speed") (v "speed")))]
/-- H-4: the squared speed ratio stated as 10⁻⁸, with the path D free or stated as 2 × 10⁷. -/
def h4 (d : Source) : List Decl := [⟨"sq", .stated (1 / 10 ^ 8)⟩, ⟨"D", d⟩]
def twoDsq : Expr := .mul twoD (v "sq")
/-- A chain of definitions, each the previous one twice: 2ᵏ⁺¹ − 1 nodes once inlined, k + 1 in memory. -/
def chain (k : Nat) : List Decl :=
  free "c0" :: (List.range k).map fun i => defd s!"c{i + 1}" (.add (v s!"c{i}") (v s!"c{i}"))
/-- Zero at each of the 13 values tried, and not the zero polynomial. -/
def roots : Expr := identityValues.foldl (fun e q => .mul e (.sub (v "x") (l q))) (l 1)
/-- A row: its outcome, point, sides and the reason it shows (with a budget of 7). -/
def run (ds : List Decl) (p : Expr × Expr) : String :=
  let r := identityRun ds p.1 p.2
  (wide (r.outcome, r.point, r.sides, r.reason 7)).replace "VE.Numbers." ""
def κ6 (n : String) : Rat := if n = "light" then 3 else 1
/-- me-9c (review F5): `four` with `k` more nodes `+ 0`; 1/(1/(… e)), k divisions; x, y, z and w free. -/
def zeros (k : Nat) (e : Expr) : Expr := (List.range k).foldl (fun e _ => .add e (l 0)) e
def nest (k : Nat) (e : Expr) : Expr := (List.range k).foldl (fun e _ => .div (l 1) e) e
def xyzw : List Decl := ["x", "y", "z", "w"].map free
/-- `roots` times 1 + (y0 − y0) + … + (yₖ₋₁ − yₖ₋₁), a balanced sum: the normal form is `roots`, so all 13 points
are tried, each reading every yᵢ (x and the yᵢ free). -/
def pairs (i j : Nat) : Expr :=
  if j ≤ i + 1 then .sub (v s!"y{i}") (v s!"y{i}") else .add (pairs i ((i + j) / 2)) (pairs ((i + j) / 2) j)
termination_by j - i
def flat (k : Nat) : Expr := .mul roots (.add (l 1) (pairs 0 k))
def ys (k : Nat) : List Decl := free "x" :: (List.range k).map fun i => free s!"y{i}"
/-- The units the normaliser charges for both sides, and the 13 points over the names they read, of a large budget. -/
def cost (p : Expr × Expr) : String :=
  let n := 10 ^ 9
  let pts := (List.range 13).map (identityPoint (p.1.names ++ p.2.names).eraseDups)
  reprStr ((Identity.compareB p.1 p.2 n).map (n - ·.2), (pointsB p.1 p.2 pts n).map (n - ·.2))
/-- The row over a and b free within a budget of `n` units, as `run` prints it. -/
def runB (n : Nat) (p : Expr × Expr) : String :=
  let r := identityDecideB ["a", "b"] p.1 p.2 n
  (wide (r.outcome, r.point, r.sides, r.reason 7)).replace "VE.Numbers." ""
/-- An inlined claim's names, and its verdict before and after inlining at κ6. -/
def inl (c : Claim) : String := wide ((c.inline r6 (freeNames r6)).toOption.map fun c' =>
  (c'.exprs.map (·.names.eraseDups), c.decide (values (assign r6 (freeNames r6) κ6)), c'.decide (some ∘ κ6)))
def fault (c : Claim) : String := match c.inline r6 (freeNames r6) with | .error v => reprStr v | .ok _ => "ok"
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
open Lean Meta in
/-- Each constructor of an inductive, with how many of its fields are expressions: the places the tables of
`OPERANDS` and `CLAIMS` fill (me-9b review F1). -/
def exprFields (ind : Name) : MetaM String := do
  let some (.inductInfo i) := (← getEnv).find? ind | throwError "no inductive {ind}"
  let rows ← i.ctors.mapM fun c => do
    let n ← forallTelescope (← getConstInfo c).type fun xs _ =>
      xs.foldlM (init := 0) fun k x => return if (← inferType x).isConstOf ``VE.Calc.Expr then k + 1 else k
    return s!"{c.components.getLast!}:{n}"
  return " ".intercalate rows
"""

# Every limit check of `VE.Calc.Poly`, by the declaration that makes it (REPORT.md, "Limit truth table"). A row is
# (check, key, side, other side or None, at the limit). Exactly at its limit a side is answered; exactly one past
# it, it is `none`. A row with one side gives two fixtures: `{key}`, whether the side has a fraction form, and
# `{key}-compare`, the side compared with itself, so past a limit even that is no identity. A row with two sides
# gives `{key}`, their comparison (`some true` at the limit, `none` past it), and `{key}-form`, whether the first
# side has a fraction form: `compare` multiplies each side by the other's denominator, which checks the term count
# again, so the form is what pins a check of one factor only (recheck F8's hunt). A row past its limit also gives
# `{key}-swapped`, its side compared second (after the other side, or after x), so a check of the first side only is
# caught (hunt 2).
LIMIT_CHECKS = {
    "nodes": ("VE.Calc.Frac.ofExpr?", "e.nodesWithin maxPolyTerms: at most 10,000 nodes in a side"),
    "sum": ("VE.Calc.Poly.add?", "p.length + q.length ≤ maxPolyTerms: at most 10,000 terms in a sum"),
    "product": ("VE.Calc.Poly.mul?", "p.length * q.length ≤ maxPolyTerms: at most 10,000 terms in a product"),
    "power": ("VE.Calc.Poly.powWithin", "k ≤ maxPolyExponent: a power node's exponent at most 4,096 (`pow?`, `pow?B`)"),
    "exponent": ("VE.Calc.Poly.fits", "each variable's exponent ≤ maxPolyExponent, in every monomial"),
    "numerator": ("VE.Calc.Poly.fits", "num.natAbs < Poly.coeffBound: at most 4,096 digits, either sign"),
    "denominator": ("VE.Calc.Poly.fits", "den < Poly.coeffBound: at most 4,096 digits"),
}


def digit_rows():
    """ME-1's digit limit (2.4), for each sign and each side of the line: `top` (10^4096 − 1, 4,096 digits) is at
    it, `big` (10^4096, 4,097 digits) one past it. At it by a literal and by a product; past it by a literal, a
    product and a sum, so each place that builds a polynomial (`Frac.go`'s literal, `mul?`, `add?`) is pinned; and
    at and past it in the middle monomial of three, c + c'·x + c·z, so a check of some monomials only, or of
    constant ones only, is caught (hunt 2)."""
    middle = '.mul (.add (.add (l 1) (.mul ({big} ) (v "x"))) (v "z")) (l ({c}))'.replace(" )", ")")
    for sign, minus in (("", ""), ("neg-", "-")):
        yield from (("numerator", f"digits-{sign}{kind}", side, None, kind.startswith("4096")) for kind, side in (
            ("4096", f"l ({minus}top)"),
            ("4096-product", f".mul (l ({minus}top / 9)) (l 9)"),
            ("4097-literal", f"l ({minus}big)"),
            ("4097", f".mul (.pow (l 10) 4095) (l ({minus}10))"),
            ("4097-sum", f".add (l ({minus}top)) (l ({minus}1))"),
            ("4096-middle-term", middle.format(big="l (top / 9)", c=f"{minus}9")),
            ("4097-middle-term", middle.format(big=".pow (l 10) 4095", c=f"{minus}10")),
        ))
        # 4,096 digits above and below the line at once (top and top − 1 are coprime), so a bound on their product
        # is caught (hunt 1).
        yield "numerator", f"digits-{sign}both-4096", f"l ({minus}top / (top - 1))", None, True
        yield from (("denominator", f"digits-{sign}den-{kind}", side, None, kind.startswith("4096")) for kind, side in (
            ("4096", f"l ({minus}1 / top)"),
            ("4096-product", f".mul (l ({minus}9 / top)) (l (1 / 9))"),
            ("4097-literal", f"l ({minus}1 / big)"),
            ("4097", f".mul (.pow (l (1 / 10)) 4095) (l ({minus}1 / 10))"),
            # (2^4096 + 5^4096) / 10^4096 is in lowest terms: the sum is odd and 1 modulo 5.
            ("4097-sum", f".add (l ({minus}1 / 5 ^ 4096)) (l ({minus}1 / 2 ^ 4096))"),
            ("4096-middle-term", middle.format(big="l (9 / top)", c=f"{minus}1 / 9")),
            ("4097-middle-term", middle.format(big=".pow (l (1 / 10)) 4095", c=f"{minus}1 / 10")),
        ))


LIMITS = [
    ("nodes", "nodes-10000", "(sumx 4999).pow 1", '.mul (l 5000) (v "x")', True),
    ("nodes", "nodes-10001", "sumx 5000", '.mul (l 5001) (v "x")', False),
    ("nodes", "nodes-10001-pow", "((sumx 4999).pow 1).pow 1", '.mul (l 5000) (v "x")', False),
    ("nodes", "nodes-10001-right", '.add (v "x") (sumx 4999)', '.mul (l 5001) (v "x")', False),
    # Each kind of node, each at the limit (a two-node power last) and one past it (hunt 1).
    *(row for op in ("sub", "mul", "div") for row in (
        ("nodes", f"nodes-10000-{op}", f'.{op} (sumx 4998) (.pow (v "x") 1)', None, True),
        ("nodes", f"nodes-10001-{op}", f'.{op} (sumx 4999) (v "x")', None, False))),
    ("nodes", "nodes-10000-lit", ".add (sumx 4998) (.pow (l 1) 1)", None, True),
    ("nodes", "nodes-10001-lit", ".add (sumx 4998) (.add (l 1) (l 1))", None, False),
    # A side that shares itself, 2^15 − 1 nodes as a tree: past the limit, and cheap to normalise if it is let
    # through; `test_a_shared_side_costs_only_the_limit` has one of 2^41 − 1.
    ("nodes", "nodes-shared", "doubled 14", '.mul (l 16384) (v "x")', False),
    ("sum", "sum-10000", "four", None, True),
    ("sum", "sum-10001", ".add four (l 1)", None, False),
    # 10,001 terms before like terms merge and 10,000 after (`four` has an xy term), so a count after merging is
    # caught (hunt 2).
    ("sum", "sum-merged-10001", '.add four (.mul (v "x") (v "y"))', None, False),
    # The sum of `Frac.add?`'s cross products: 9,900 + 101 terms (hunt 1).
    ("sum", "add-cross-sum-10001", '.add (.div (.mul (geo "x" 99) (geo "y" 98)) (v "u")) (.div (geo "z" 100) (v "w"))',
     None, False),
    # 100 × 100, 73 × 137 (review F8: exactly one past) and 101 × 100 terms.
    ("product", "product-10000", '.mul (geo "x" 99) (geo "y" 99)', '.mul (geo "y" 99) (geo "x" 99)', True),
    ("product", "product-10001", '.mul (geo "x" 72) (geo "y" 136)', '.mul (geo "y" 136) (geo "x" 72)', False),
    ("product", "product-10100", '.mul (geo "x" 100) (geo "y" 99)', '.mul (geo "y" 99) (geo "x" 100)', False),
    # Every product a fraction form takes, one past the limit (hunt 1): `Frac.add?`'s cross products (73 × 137 terms
    # before like terms merge, 209 after, so the sum after them does not mask the count) and its denominator,
    # `Frac.mul?`'s and `Frac.div?`'s, and a power's steps, where 10,001 cannot be reached (a power of a 73-term
    # polynomial has more than 137 terms): 100 × 100 and 101 × 101.
    ("product", "add-cross-10001", '.add (.div (geo "x" 72) (v "u")) (.div (l 1) (geo "x" 136))', None, False),
    ("product", "add-cross-right-10001", '.add (.div (l 1) (geo "x" 136)) (.div (geo "x" 72) (v "u"))', None, False),
    ("product", "add-den-10001", '.add (.div (l 1) (geo "x" 72)) (.div (l 1) (geo "y" 136))', None, False),
    ("product", "mul-den-10001", '.mul (.div (l 1) (geo "x" 72)) (.div (l 1) (geo "y" 136))', None, False),
    ("product", "div-num-10001", '.div (geo "x" 72) (.div (l 1) (geo "y" 136))', None, False),
    ("product", "div-den-10001", '.div (.div (l 1) (geo "x" 72)) (geo "y" 136)', None, False),
    ("product", "pow-10000", '.pow (geo "x" 99) 2', None, True),
    ("product", "pow-10201", '.pow (geo "x" 100) 2', None, False),
    # A constant base, where only the power node's guard refuses.
    ("power", "exponent-constant-4096", ".pow (l 1) 4096", None, True),
    ("power", "exponent-constant-4097", ".pow (l 1) 4097", None, False),
    # Exponents reached by products; past the limit in the middle variable of three and the middle monomial of four,
    # so a check of the first or the last one only is caught.
    ("exponent", "exponent-4096", '.mul (.pow (v "x") 2048) (.pow (v "x") 2048)', '.pow (.pow (v "x") 64) 64', True),
    # Each variable at the limit, so a bound on the total degree is caught (hunt 1).
    ("exponent", "exponent-4096-two-vars",
     '.mul (.mul (.pow (v "x") 2048) (.pow (v "x") 2048)) (.mul (.pow (v "y") 2048) (.pow (v "y") 2048))', None, True),
    ("exponent", "exponent-4097", '.mul (.pow (v "x") 4096) (v "x")', '.pow (v "x") 4097', False),
    ("exponent", "exponent-4097-product", '.mul (.pow (v "x") 4096) (v "x")', '.mul (v "x") (.pow (v "x") 4096)',
     False),
    ("exponent", "exponent-4097-middle-var", '.mul (.pow (v "y") 4096) (.mul (v "x") (.mul (v "y") (v "z")))', None,
     False),
    ("exponent", "exponent-4097-middle-term", '.mul (.add (.pow (v "x") 4096) (v "z")) (.add (v "x") (v "z"))', None,
     False),
    # A power's numerator and its denominator, past the exponent limit at the last step: x^(17 · 241) (hunt 1).
    ("exponent", "pow-num-4097", '.pow (.pow (v "x") 17) 241', None, False),
    ("exponent", "pow-den-4097", '.pow (.div (l 1) (.pow (v "x") 17)) 241', None, False),
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
        if not at:
            yield f"{key}-swapped", f'compare ({other or 'v "x"'}, {side})', "none"


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
    # `compare`'s own cross products, one past the limit (hunt 1).
    ("compare-cross-10001", 'compare (geo "x" 72, .div (l 1) (geo "y" 136))', "none"),
    ("compare-cross-right-10001", 'compare (.div (l 1) (geo "y" 136), geo "x" 72)', "none"),
    # A product by zero (no terms) is within the limit, so a count that divides by a factor's terms is caught (hunt 2).
    ("product-by-zero", 'form (.mul (v "x") (l 0))', "true"),
    # Two fractions over one denominator are added without cross products: 101 × 101 terms would be past the limit.
    ("same-denominator", 'form (.add (.div (v "x") (geo "y" 100)) (.div (v "z") (geo "y" 100)))', "true"),
]


BUDGET = ('(Outcome.unknown (UnknownReason.limit (Limit.polyTerms)), none, none, '
          'some "unknown: the budget of 1000000 evaluation steps ran out")')
HOLDS, FAILS, UNDEFINED = (f"(Outcome.decided (Verdict.{v}), none, none, none)" for v in ("holds", "fails", "undefined"))
EVALUATIONS = ('(Outcome.unknown (UnknownReason.limit (Limit.evaluations)), none, none, '
               'some "unknown: the budget of 7 evaluation steps ran out")')
# me-9 review F4: past the node limit a side may have one term, and a product is counted before like terms merge, so
# neither shows spec 1.5's "more than 10,000 terms"; nor do the exponent and digit bounds.
POLY_LIMIT = "(Outcome.unknown (UnknownReason.limit (Limit.polyTerms)), none, none, some \"unknown: {}\")"
NODES = POLY_LIMIT.format("a side would have more than 10,000 nodes once its named values are written out")
FORM = POLY_LIMIT.format("a normal form on the way would have more than 10,000 terms before like terms merge, "
                         "an exponent above 4,096 or a coefficient of more than 4,096 digits")


def fails(point, sides):
    return f"(Outcome.decided (Verdict.fails), some {point}, some {sides}, none)"


# The runner over named, stated and free values (spec 8.2 and 2.7; R-6, H-4, me-9 review F3 and F4).
IDENTITY_FIXTURES = [
    ("r6-h1", 'run r6 (v "round_trip", v "closed_form")', HOLDS),
    # R-6's `sq`: point 0 sets every free value read to 1, in declaration order; path, light and speed are not read.
    ("r6-sq", 'run r6 (sq (.add (v "x") (v "y")), .add (sq (v "x")) (sq (v "y")))', fails('[("x", 1), ("y", 1)]', "(4, 2)")),
    ("h4", 'run (h4 .free) (twoDsq, .mul twoD (l (1 / 10 ^ 8)))', HOLDS),
    ("h4-stated", "run (h4 (.stated (2 * 10 ^ 7))) (twoDsq, l (2 / 5))", HOLDS),
    ("h4-stated-fails", "run (h4 (.stated (2 * 10 ^ 7))) (twoDsq, l (1 / 2))", fails("[]", "((2 : Rat)/5, (1 : Rat)/2)")),
    ("point-later", 'run r6 (sq (v "x"), v "x")', fails('[("x", 2)]', "(4, 2)")),
    # At x = 1 the left side denotes nothing, at 2 the sides agree, at 3 they differ.
    ("point-skips-undefined", "run r6 recip", fails('[("x", 3)]', "((1 : Rat)/2, 1)")),
    ("not-shown", "run r6 (roots, l 0)", '(Outcome.unknown (UnknownReason.identityNotShown), none, none, '
     'some "unknown: the normal forms differ and no point where the sides differ was found")'),
    ("undefined-missing", 'run r6 (v "nowhere", v "x")', UNDEFINED),
    ("undefined-counted", 'run r6 (v "x", v "none")', UNDEFINED),
    ("exhausted", 'run r6 (v "spent", v "x")', EVALUATIONS),
    # The first faulty side names the fault.
    ("fault-undefined-first", 'run r6 (v "nowhere", v "spent")', UNDEFINED),
    ("fault-exhausted-first", 'run r6 (v "spent", v "nowhere")', EVALUATIONS),
    ("fault-right", 'run r6 (v "x", v "spent")', EVALUATIONS),
    # F3: a side whose divisor is zero wherever it denotes is undefined, not a vacuous identity: the review's four
    # cases, through a definition, and a zero divisor inside a divisor or under a power 0.
    ("f3-0/0", "run r6 (.div (l 0) (l 0), l 5)", UNDEFINED),
    ("f3-0/0-compare", "compare (.div (l 0) (l 0), l 5)", "some true"),
    ("f3-x-x", 'run r6 (.div (.sub (v "x") (v "x")) (.sub (v "x") (v "x")), l 5)', UNDEFINED),
    ("f3-1/0", "run r6 (.div (l 1) (l 0), .div (l 2) (l 0))", UNDEFINED),
    ("f3-binom", 'run r6 (.add (sq (.add (v "x") (v "y"))) (.div (l 1) (l 0)), '
     '.add (.add (sq (v "x")) (sq (v "y"))) (.div (l 1) (l 0)))', UNDEFINED),
    ("f3-zero-rate", 'run r6 (v "zero_rate", v "zero_rate")', UNDEFINED),
    ("f3-right", "run r6 (l 5, .div (l 0) (l 0))", UNDEFINED),
    ("f3-inner", "run r6 (.div (l 1) (.div (l 1) (l 0)), l 0)", UNDEFINED),
    ("f3-pow-0", "run r6 (.pow (.div (l 1) (l 0)) 0, l 1)", UNDEFINED),
    # A divisor that is zero at some points only.
    ("f3-cancel-holds", "run r6 cancel", HOLDS),
    ("f4-nodes", 'run r6 (sumx 5000, .mul (l 5001) (v "x"))', NODES),
    ("f4-nodes-right", 'run r6 (v "x", sumx 5000)', NODES),
    ("f4-product", 'run r6 (.pow (geo "x" 100) 2, .pow (geo "x" 100) 2)', FORM),
    ("f4-exponent", 'run r6 (.mul (.pow (v "x") 4096) (v "x"), .pow (v "x") 4097)', FORM),
    ("f4-digits", "run r6 (l big, l big)", FORM),
    # Inlining (spec 2.7) and the meaning's assignment.
    ("free-names", "reprStr (freeNames r6)", '["path", "light", "speed", "x", "y"]'),
    ("assign", 'reprStr (values (assign r6 (freeNames r6) κ6) "round_trip", '
     'values (assign r6 (freeNames r6) κ6) "closed_form")', "(some (3 : Rat)/4, some (3 : Rat)/4)"),
    # x = 1 is not less than the round-trip time 3/4, before inlining or after.
    ("claim-inline", 'inl (.compare ⟨.lt, false⟩ (v "x") (v "round_trip"))',
     'some ([["x"], ["path", "light", "speed"]], VE.Numbers.Verdict.fails, VE.Numbers.Verdict.fails)'),
    ("claim-fault-undefined-first", 'fault (.within (v "x") (v "nowhere") (v "spent"))', "VE.Calc.Val.undefined"),
    ("claim-fault-exhausted-first", 'fault (.within (v "x") (v "spent") (v "nowhere"))', "VE.Calc.Val.exhausted"),
    # me-9b review F1's examples; the tables below hold the class.
    ("f3-numerator", 'run r6 (.div (.div (l 1) (l 0)) (v "x"), .div (.div (l 2) (l 0)) (v "x"))', UNDEFINED),
    ("f3-left", 'run r6 (.add (.div (l 1) (l 0)) (v "x"), .add (.div (l 2) (l 0)) (v "x"))', UNDEFINED),
    ("fault-inside-side", 'run r6 (.add (v "nowhere") (v "spent"), v "x")', UNDEFINED),
    ("claim-fault-compare", 'fault (.compare ⟨.lt, false⟩ (v "nowhere") (v "spent"))', "VE.Calc.Val.undefined"),
    ("claim-fault-within-e", 'fault (.within (v "nowhere") (v "spent") (v "x"))', "VE.Calc.Val.undefined"),
    # The point reads the names of both sides, in declaration order, not the order the sides read them.
    ("point-right-only", 'run r6 (l 2, v "y")', fails('[("y", 1)]', "(2, 1)")),
    ("point-left-only", 'run r6 (v "y", l 2)', fails('[("y", 1)]', "(1, 2)")),
    ("point-declaration-order", 'run r6 (v "y", v "x")', fails('[("x", 2), ("y", 3)]', "(3, 2)")),
]

# me-9b review F1, a check with a place no fixture fills: every place of every constructor, generated from these
# tables, which `test_the_place_tables_are_lean_s_constructors` holds to Lean's `Expr` and `Claim`. A value for each
# place: a free value read (`x`), a missing name and a counted value whose budget ran out.
OPERANDS = {"lit": 0, "val": 0, "add": 2, "sub": 2, "mul": 2, "div": 2, "pow": 1}
CLAIMS = {"compare": ".compare ⟨.lt, false⟩ ({}) ({})", "within": ".within ({}) ({}) ({})",
          "rounds": ".rounds .tiesUp ({}) ⟨2, 8⟩"}
PLACE_VALUES = {"x": None, "nowhere": "undefined", "spent": "exhausted"}


def node(ctor, args):
    return f".pow ({args[0]}) 2" if ctor == "pow" else f".{ctor} ({args[0]}) ({args[1]})"


def first_fault(names):
    return next((PLACE_VALUES[n] for n in names if PLACE_VALUES[n]), None)


def place_fixtures():
    for ctor, arity in OPERANDS.items():
        for place in range(arity):
            # `Expr.zeroDivisor` reads every operand: 1/0 in each one, the side compared with itself.
            side = node(ctor, ['.div (l 1) (l 0)' if i == place else 'v "x"' for i in range(arity)])
            yield f"zero-divisor-{ctor}-{place}", f"run r6 ({side}, {side})", UNDEFINED
        # `Expr.subst`'s fault order: the first faulty operand, left to right, names the fault.
        for names in itertools.product(PLACE_VALUES, repeat=arity):
            if fault := first_fault(names):
                yield (f"subst-{ctor}-{'-'.join(names)}", f'run r6 ({node(ctor, [f'v "{n}"' for n in names])}, v "x")',
                       UNDEFINED if fault == "undefined" else EVALUATIONS)
    # `Claim.inline`'s fault order, in `Claim.exprs`' order.
    for ctor, claim in CLAIMS.items():
        for names in itertools.product(PLACE_VALUES, repeat=claim.count("{}")):
            fault = first_fault(names)
            yield (f"claim-{ctor}-{'-'.join(names)}", f"fault ({claim.format(*(f'v "{n}"' for n in names))})",
                   f"VE.Calc.Val.{fault}" if fault else "ok")


# The 13 values tried, in order (spec 8.2): point i gives a single name the ith value.
VALUES = [Fraction(q) for q in ("1", "2", "3", "-1", "1/2", "5", "-2", "1/3", "7", "-3", "3/2", "11", "0")]


def rat(q):
    return str(q.numerator) if q.denominator == 1 else f"({q.numerator} : Rat)/{q.denominator}"


def point_fixtures():
    """For each point, a side zero at every earlier point and not at it, against 0 · x: the first differing point is
    that one, so a search that stops early, skips a point or reorders the values is caught."""
    yield "identity-values", "reprStr identityValues", f"[{', '.join(rat(q) for q in VALUES)}]"
    for i, x in enumerate(VALUES):
        side = "l 1"
        for q in VALUES[:i]:
            side = f'.mul ({side}) (.sub (v "x") (l ({q.numerator} / {q.denominator})))'
        value = math.prod((x - q for q in VALUES[:i]), start=Fraction(1))
        yield (f"point-{i + 1}{ {1: 'st', 2: 'nd', 3: 'rd'}.get(i + 1, 'th')}", f'run r6 ({side}, .mul (l 0) (v "x"))',
               fails(f'[("x", {rat(x)})]', f"({rat(value)}, 0)"))


# me-9c (me-9 review F5): the runner's work budget, `VE.Limits.maxEvaluations` units a row. Sides within the limits
# whose work runs out of it answer the budget's unknown row at once (`zeros`: about 60 s before, at the node limit
# about 24 minutes; a power of 2,048 steps 49 s; the 13 points over 2,401 names 16 s); those within it answer as
# before (H-1 to H-4 and R-6 above, unchanged). Nested divisors cost their nodes: their zero divisors are found in the
# normaliser's pass (133 s before, when each divisor was normalised again).
BUDGET_FIXTURES = [
    ("budget-f5-zeros", "run xyzw (zeros 400 four, four)", BUDGET),
    ("budget-f5-node-limit", "run xyzw (zeros 4404 four, four)", BUDGET),
    ("budget-f5-node-limit-size", "nodes (zeros 4404 four)", "some 9999"),
    ("budget-four", "run xyzw (four, four)", HOLDS),
    ("budget-power-2048", 'run xyzw (.pow (.add (v "x") (l 1)) 2048, .pow (.add (v "x") (l 1)) 2048)', BUDGET),
    ("budget-power-64", 'run xyzw (.pow (.add (v "x") (l 1)) 64, .pow (.add (v "x") (l 1)) 64)', HOLDS),
    ("budget-power-exponent", 'run xyzw (.pow (l 1) 4097, l 1)', FORM),
    ("budget-nested-divisors", 'run xyzw (nest 4998 (v "x"), v "x")', HOLDS),
    ("budget-nested-divisors-size", 'nodes (nest 4998 (v "x"))', "some 9997"),
    ("budget-nested-zero-divisor", 'run xyzw (nest 4996 (.div (v "x") (.sub (v "x") (v "x"))), v "x")', UNDEFINED),
    ("budget-points", "run (ys 2400) (flat 2400, l 0)", BUDGET),
    ("budget-points-size", "nodes (flat 2400)", "some 9655"),
    ("budget-points-within", "run (ys 30) (flat 30, l 0)", '(Outcome.unknown (UnknownReason.identityNotShown), none, '
     'none, some "unknown: the normal forms differ and no point where the sides differ was found")'),
    # The charges, exactly: a sum, a product, a fraction's sum and quotient, a power's steps, and each node and value
    # the 13 points read, so a charge dropped or not taken off is caught.
    ("budget-cost-binom", "cost binom", "(some 105, some 9)"),
    ("budget-cost-h1", "cost h1", "(some 198, some 269)"),
    ("budget-cost-power", 'cost (.pow (.add (v "x") (l 1)) 3, l 1)', "(some 83, some 5)"),
    ("budget-cost-divisors", 'cost (nest 3 (v "x"), .sub (v "x") (v "y"))', "(some 48, some 10)"),
    ("budget-cost-recip", "cost recip", "(some 30, some 17)"),
    # 2⁶⁴ and 2⁴⁰⁹⁶ at x = 2 (a word, and 64), and a point of 9 names (a value read: 2 units).
    # R5: the binomial's row with the budget it costs (105 units for the forms, 9 for the point) and one unit less,
    # in each phase, and with none.
    ("budget-binom-114", "runB 114 binom", fails('[("a", 1), ("b", 1)]', "(4, 2)")),
    ("budget-binom-113", "runB 113 binom", BUDGET),
    ("budget-binom-105", "runB 105 binom", BUDGET),
    ("budget-binom-104", "runB 104 binom", BUDGET),
    ("budget-binom-0", "runB 0 binom", BUDGET),
    ("budget-literal-0", "runB 0 (l 1, l 1)", BUDGET),
    ("budget-literal-10", "runB 10 (l 1, l 1)", BUDGET),
    ("budget-literal-11", "runB 11 (l 1, l 1)", HOLDS),
    ("budget-cost-words", 'cost (.mul (.sub (v "x") (l 1)) (.pow (.pow (v "x") 64) 64), l 0)', "(some 1041, some 144)"),
    ("budget-cost-names", "cost (flat 8, l 0)", "(some 923, some 1521)"),
]
IDENTITY_FIXTURES += [*place_fixtures(), *point_fixtures(), *BUDGET_FIXTURES]
FIXTURES += IDENTITY_FIXTURES


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
                    '#eval show Lean.CoreM Unit from do line "limit-readers" (← limitReaders)\n'
                    + "".join(f'#eval show Lean.Meta.MetaM Unit from do line "{key}" (← exprFields ``VE.Calc.{ind})\n'
                              for key, ind in EXTRA.items() if ind))


# The lines the fixture file prints besides `FIXTURES`, with the inductive whose constructors each one lists.
EXTRA = {"limit-readers": None, "expr-fields": "Expr", "claim-fields": "Claim"}


@pytest.mark.parametrize("key, expected", [pytest.param(key, expected, id=key) for key, _, expected in FIXTURES])
def test_fixture(lean, key, expected):
    assert lean[key] == expected


def test_every_fixture_printed_once(lean):
    assert sorted(lean) == sorted([key for key, _, _ in FIXTURES] + list(EXTRA))


def test_the_place_tables_are_lean_s_constructors(lean):
    """The place tables list every constructor of `Expr` and `Claim`, in order, with its number of expression fields,
    so a constructor added in Lean gets its places filled (me-9b review F1)."""
    assert lean["expr-fields"] == " ".join(f"{ctor}:{arity}" for ctor, arity in OPERANDS.items())
    assert lean["claim-fields"] == " ".join(f"{ctor}:{claim.count('{}')}" for ctor, claim in CLAIMS.items())


def test_every_limit_check_is_pinned_at_and_past_it(lean):
    """Each definition that reads a limit, as Lean's environment lists them, makes a check of the table (or is the
    limit theorems' predicate `Poly.Within`), and each check has a fixture at its limit and one past it."""
    assert lean["limit-readers"].split() == sorted({owner for owner, _ in LIMIT_CHECKS.values()}
                                                   | {"VE.Calc.Poly.Within"})
    for check in LIMIT_CHECKS:
        assert {at for row, _, _, _, at in LIMITS if row == check} == {True, False}, check
    assert {row for row, _, _, _, _ in LIMITS} == set(LIMIT_CHECKS)


SHARED = [
    ("nodes-shared-41", 'compare (doubled 40, .mul (l 1099511627776) (v "x"))', "none"),
    # `Poly.ofExpr?` looks for division only within the limits (hunt 1: it walked the whole tree first).
    ("poly-shared-41", "reprStr (Poly.ofExpr? (doubled 40))", "none"),
    # A power's exponent is checked before its steps, in the numerator as in the denominator (hunt 2).
    ("power-10^12", "compare (.pow (l 1) 1000000000000, l 1)", "none"),
    # The runner lists the names a side reads, and looks for zero divisors, only once the normaliser accepted it
    # (wip/me-9b 10819663b: listing them first walked this chain as a tree for 17 minutes).
    ("chain-41", 'run (chain 40) (v "c40", .mul (l 1099511627776) (v "c0"))', NODES),
]


@pytest.mark.parametrize("fixture", [pytest.param(fixture, id=fixture[0]) for fixture in SHARED])
def test_a_shared_side_costs_only_the_limit(tmp_path, fixture):
    """Sides whose work stops at a limit at once: 2^41 − 1 nodes as a tree, 41 in memory, and a power of exponent
    10^12. Each in its own process, so a walk that does not stop fails its test alone (by `HANG_TIMEOUT`)."""
    assert run_lean(tmp_path / "Shared.lean", [fixture]) == {fixture[0]: fixture[2]}
