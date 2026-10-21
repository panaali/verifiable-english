import VE.Calc.Lower
import VE.Calc.DeriveExamples

/-! Fixtures of the lowering and the derivation's meaning (spec 5, 13.4, 13.6): R-3 (H-6) follows and R-4 (H-6n) does
not, as claims over declarations; each lowered claim agrees with its own meaning at several points, both ways. -/

namespace VE.Calc.LowerExamples
open VE.Calc VE.Numbers

def lt (a b : Expr) : Claim := .compare ⟨.lt, false⟩ a b
def le (a b : Expr) : Claim := .compare ⟨.le, false⟩ a b
def gt (a b : Expr) : Claim := .compare ⟨.lt, true⟩ a b
def ge (a b : Expr) : Claim := .compare ⟨.le, true⟩ a b
def eq (a b : Expr) : Claim := .compare ⟨.eq, false⟩ a b
def v (n : String) : Expr := .val n
def k (q : Rat) : Expr := .lit q

/-- R-3's case: three free values, p1 (d = 0.4 s) and p2 (d < 0.02), the link (s, r). -/
def ds : List Decl := [⟨"r", .free⟩, ⟨"s", .free⟩, ⟨"d", .free⟩]
def p1 : Claim := eq (v "d") (.mul (k (2/5)) (v "s"))
def P : List Claim := [p1, lt (v "d") (k (2/100))]
def links : List (String × String) := [("s", "r")]
/-- "r is less than 1 divided by `n`". -/
def rBelow (n : Rat) : Claim := lt (v "r") (.div (k 1) (k n))
def fss : List (List QFact) := [[DeriveExamples.fact 0 [("d", 1), ("s", -2/5)] false,
  DeriveExamples.fact 0 [("s", 2/5), ("d", -1)] false], [DeriveExamples.fact (2/100) [("d", -1)] true]]

-- The lowered facts are me-5's fact fixtures, in 3.4's order: d − 0.4 s ≥ 0, 0.4 s − d ≥ 0, 0.02 − d > 0.
#guard P.mapM (Claim.facts ds) = some fss && fss.flatten = DeriveExamples.h6 (2/100)
#guard (rBelow 4).facts ds = some [DeriveExamples.below (1/4)]
-- R-3: the search's certificate is R-3's (weights 1, 0, 1, 2/5, then the square step), and it replays.
#guard Derive.search fss.flatten links (DeriveExamples.below (1/4)) = .follows ⟨DeriveExamples.h6Steps⟩
theorem ds_wellFormed : WellFormed ds := by
  refine ⟨by decide, fun i hi e he => ?_, fun d hd q v hq => ?_⟩
  · obtain _ | _ | _ | i := i <;> simp [ds] at hi he; exact absurd hi (by omega)
  · simp only [ds, List.mem_cons, List.mem_nil_iff, or_false] at hd; rcases hd with rfl | rfl | rfl <;> cases hq
theorem r3_follows : Follows ds P links (rBelow 4) :=
  follows_of_check ds ds_wellFormed P links _ fss (DeriveExamples.below (1/4)) ⟨DeriveExamples.h6Steps⟩ (by decide +kernel)
    (by decide +kernel) (by decide +kernel)
-- R-4: r < 1/5 does not follow; R-4's counterexample, the claimed bound tried first.
def r4 : List (String × Rat) := [("r", 1/5), ("s", 1/25), ("d", 2/125)]
#guard Derive.search fss.flatten links (DeriveExamples.below (1/5)) = .counterexample r4
theorem r4_not_follows : ¬ Follows ds P links (rBelow 5) :=
  not_follows_of_counterexample _ _ _ _ <| counterexample_of_check ds ds_wellFormed P links _ fss
    (DeriveExamples.below (1/5)) (Answer.point r4) (by decide +kernel) (by decide +kernel) (by decide +kernel)

/-- The claim's facts hold at each point exactly when the claim does over the assigned values (`Claim.facts_sound`,
decided by `Claim.decide`, `Claim.decide_holds`). -/
def agrees (ds : List Decl) (c : Claim) (pts : List (List (String × Rat))) : Bool :=
  match c.facts ds with
  | some fs => pts.all fun κ => (fs.all fun f => decide (f.Holds (Answer.point κ))) ==
      (c.decide (values (assign ds (freeNames ds) (Answer.point κ))) == .holds)
  | none => false
/-- How many facts a claim lowers to, none when it is refused. -/
def count (ds : List Decl) (c : Claim) : Option Nat := (c.facts ds).map List.length

-- 13.4's row: p1 at d = 2/125, s = 1/25 (facts and premise hold), and at d = 1, s = 0 (both fail).
#guard P.all fun p => agrees ds p [r4, [("d", 1), ("s", 0)]]
#guard (p1.decide (values (assign ds (freeNames ds) (Answer.point r4)))) = .holds &&
  (p1.decide (values (assign ds (freeNames ds) (Answer.point [("d", 1)])))) = .fails

-- Each comparison and `within`, on both sides of its boundary and at it: eq gives two facts, within two, the rest one.
def xy : List Decl := [⟨"x", .free⟩, ⟨"y", .free⟩]
def pts : List (List (String × Rat)) := [[("x", 1), ("y", 2)], [("x", 2), ("y", 2)], [("x", 3), ("y", 2)]]
#guard [eq, lt, le, gt, ge].map (fun c => count xy (c (v "x") (v "y"))) = [some 2, some 1, some 1, some 1, some 1]
#guard [eq, lt, le, gt, ge].all fun c => agrees xy (c (v "x") (v "y")) pts && agrees xy (c (v "y") (v "x")) pts
#guard count xy (.within (v "x") (v "y") (k 3)) = some 2 && agrees xy (.within (v "x") (v "y") (k 3)) pts &&
  agrees xy (.within (v "x") (k 2) (v "y")) pts
#guard count xy (.rounds .tiesUp (v "x") ⟨3, 0⟩) = none

-- Linear: constants on either side of a product, a nonzero constant divisor, a constant power, powers 0 and 1, and a
-- factor whose terms cancel. Not linear: x · y, x², x / y, x / (y − y) (a zero divisor), x / (y + 1).
def lin : List Expr := [.mul (k 3) (v "x"), .mul (v "x") (.sub (k 1) (k 4)), .div (v "x") (k (-2)),
  .mul (.pow (k 2) 3) (v "x"), .pow (v "x") 1, .pow (v "x") 0, .mul (.sub (v "y") (v "y")) (v "x"),
  .add (v "x") (.mul (k 2) (v "y")), .sub (v "x") (.div (v "y") (.add (k 1) (k 1)))]
/-- x from −1 to 3, y = 2: x^0 = 1 and 8x ≠ 6x at x = 1/4 are told apart from each claim's own meaning. -/
def linPts : List (List (String × Rat)) := [-1, 0, 1/4, 1/2, 1, 3/2, 2, 3].map fun q => [("x", q), ("y", 2)]
#guard lin.all fun e => [0, 1, 2, 3].all fun q => [lt, le, eq].all fun c => agrees xy (c e (k q)) linPts
#guard [.mul (v "x") (v "y"), .pow (v "x") 2, .div (v "x") (v "y"), .div (v "x") (.sub (v "y") (v "y")),
  .div (k 1) (k 0), .div (v "x") (.add (v "y") (k 1))].all fun e => count xy (lt e (k 2)) == none

-- Inlining keeps the free values and nothing else: a stated value and a definition over the free values are
-- inlined; a missing name, an undefined or an exhausted counted value gives no facts.
def mixed : List Decl := [⟨"x", .free⟩, ⟨"c", .stated 3⟩, ⟨"e", .defined (.div (v "x") (v "c"))⟩,
  ⟨"u", .counted (Thunk.pure none) (.ok none)⟩, ⟨"w", .counted (Thunk.pure none) .exhausted⟩]
#guard (lt (v "e") (v "c")).facts mixed = some [⟨⟨3, [("x", -1/3)]⟩, true⟩]
#guard agrees mixed (lt (v "e") (v "c")) [[("x", 8)], [("x", 9)], [("x", 10)]]
#guard [v "z", v "u", v "w"].all fun e => count mixed (lt e (k 1)) == none && count mixed (lt (k 1) e) == none

end VE.Calc.LowerExamples
