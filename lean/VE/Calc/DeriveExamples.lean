import VE.Calc.Derive

/-! Fixtures of ME-5 at the level of facts (spec 13.2, 13.3): H-6, H-6p, H-6n, H-6a (debate A2), a linear system with
no solution, and a forged certificate with a negative weight. The lowering of claims to these facts is me-5b's. -/

namespace VE.Calc.DeriveExamples
open VE.Calc

def fact (k : Rat) (cs : List (String × Rat)) (strict : Bool) : QFact := ⟨⟨k, cs⟩, strict⟩
def pt (κ : List (String × Rat)) : String → Rat := Answer.point κ
/-- The search's answer passes its check: a derivation replays, a point is a counterexample. -/
def checked (P : List QFact) (links : List (String × String)) (C : QFact) : Bool :=
  match Derive.search P links C with
  | .follows d => d.check P links C
  | .counterexample κ => counterexampleCheck P links C (pt κ)
  | .unknown _ => false

/-- H-6's premises: d = 0.4 s as two facts, and d < 0.02 (Michelson and Morley 1887, h115-h116). -/
def h6 (bound : Rat) : List QFact :=
  [fact 0 [("d", 1), ("s", -2/5)] false, fact 0 [("s", 2/5), ("d", -1)] false, fact bound [("d", -1)] true]
def links : List (String × String) := [("s", "r")]
/-- "r is less than b". -/
def below (b : Rat) : QFact := fact b [("r", -1)] true

-- H-6: r < 1/4 follows, with R-3's certificate; the weights with -2/5 for 2/5 are refused.
def h6First : Step := .farkas (fact (1/20) [("s", -1)] true) ⟨[1, 0, 1, 2/5]⟩
def h6Steps : List Step := [h6First, .square "s" "r" (1/20) (1/4)]
#guard Derive.search (h6 (2/100)) links (below (1/4)) = .follows ⟨h6Steps⟩
#guard Derivation.check (h6 (2/100)) links (below (1/4)) ⟨h6Steps⟩
#guard Farkas.check (h6 (2/100) ++ [(fact (1/20) [("s", -1)] true).negate]) ⟨[1, 0, 1, 2/5]⟩
#guard !Farkas.check (h6 (2/100) ++ [(fact (1/20) [("s", -1)] true).negate]) ⟨[1, 0, 1, -2/5]⟩
-- Without the link it does not follow: r is unconstrained.
#guard checked (h6 (2/100)) [] (below (1/4)) && Derive.search (h6 (2/100)) [] (below (1/4)) matches .counterexample _

-- H-6p: d < 0.01 gives r < 1/6, with the same weights; 1/40 ≤ (1/6)².
#guard Derive.search (h6 (1/100)) links (below (1/6)) =
  .follows ⟨[.farkas (fact (1/40) [("s", -1)] true) ⟨[1, 0, 1, 2/5]⟩, .square "s" "r" (1/40) (1/6)]⟩
#guard checked (h6 (1/100)) links (below (1/6))

-- H-6n: r < 1/5 does not follow (1/20 > (1/5)²); the claimed bound is tried first (R-4's counterexample).
#guard Derive.search (h6 (2/100)) links (below (1/5)) = .counterexample [("r", 1/5), ("s", 1/25), ("d", 2/125)]
#guard checked (h6 (2/100)) links (below (1/5))

-- H-6a (debate A2): s = 0, r = 1 breaks the link s = r², so it refutes r < 1/4 only without the link; and
-- s = 1/25, r = -1/5 breaks the root's nonnegativity.
#guard !counterexampleCheck (h6 (2/100)) links (below (1/4)) (pt [("r", 1), ("s", 0), ("d", 0)])
#guard counterexampleCheck (h6 (2/100)) [] (below (1/4)) (pt [("r", 1), ("s", 0), ("d", 0)])
#guard !counterexampleCheck (h6 (2/100)) links (below (-1/5)) (pt [("r", -1/5), ("s", 1/25), ("d", 2/125)])
-- A point must meet the premises too: d = 0 breaks d = 0.4 s at s = 1.
#guard !counterexampleCheck (h6 (2/100)) links (below (1/4)) (pt [("r", 1), ("s", 1), ("d", 0)])

-- A linear system with no solution: x + y ≥ 2, x ≤ 0, y ≤ 0, refuted with each fact weighed once; then anything
-- follows. A strict fact closes a zero constant.
def none3 : List QFact := [fact (-2) [("x", 1), ("y", 1)] false, fact 0 [("x", -1)] false, fact 0 [("y", -1)] false]
#guard Farkas.check none3 ⟨[1, 1, 1]⟩ && !Farkas.check none3 ⟨[1, 1]⟩ && !Farkas.check none3 ⟨[1, 1, 0]⟩
#guard !Farkas.check none3 ⟨[1, 1, 1, 0]⟩
#guard match (FM.search none3).run' FM.maxSteps with | .ok (.refuted ws) => Farkas.check none3 ⟨ws⟩ | _ => false
#guard checked none3 [] (fact 0 [("x", 1)] true) && Derive.search none3 [] (fact 0 [("x", 1)] true) matches .follows _
#guard Farkas.check [fact 0 [("x", 1)] true, fact 0 [("x", -1)] false] ⟨[1, 1]⟩
#guard !Farkas.check [fact 0 [("x", 1)] false, fact 0 [("x", -1)] false] ⟨[1, 1]⟩

-- A forged certificate with a negative weight: s < 1/25 is false under H-6's premises (s may be up to 1/20), and
-- [0, 1, -1, -2/5] cancels every unknown and leaves -1/250. It is refused, and the search does not claim it.
def forged : Farkas := ⟨[0, 1, -1, -2/5]⟩
def sBelow : QFact := fact (1/25) [("s", -1)] true
#guard (forged.combination (h6 (2/100) ++ [sBelow.negate])).const = -1/250
#guard !Farkas.check (h6 (2/100) ++ [sBelow.negate]) forged
#guard !Derivation.check (h6 (2/100)) links sBelow ⟨[.farkas sBelow forged]⟩
#guard Derive.search (h6 (2/100)) links sBelow = .unknown .derivationInconclusive

-- The square step needs its link, an established bound and a ≤ b²; the conclusion is the last derived fact.
#guard !Derivation.check (h6 (2/100)) [] (below (1/4)) ⟨h6Steps⟩
#guard !Derivation.check (h6 (2/100)) links (below (1/5)) ⟨[h6First, .square "s" "r" (1/20) (1/5)]⟩
#guard !Derivation.check (h6 (2/100)) links (below (1/4)) ⟨[.square "s" "r" (1/20) (1/4)]⟩
#guard !Derivation.check (h6 (2/100)) links (below (1/3)) ⟨h6Steps⟩
#guard checked (h6 (2/100)) links (fact (1/3) [("r", -1)] false)
-- The square route takes the least upper bound on s: a looser s ≤ 1 beside it changes nothing.
#guard checked (h6 (2/100) ++ [fact 1 [("s", -1)] false]) links (below (1/4)) &&
  Derive.search (h6 (2/100) ++ [fact 1 [("s", -1)] false]) links (below (1/4)) matches .follows _

-- The claimed bound is tried first even at 0; a reported point gives 0 to an unknown it does not list: here s and
-- r, which only the link reads, so the link holds.
#guard Derive.search [] links (below 0) = .counterexample [("r", 0), ("s", 0)] && checked [] links (below 0)
#guard Derive.search [] links (fact 0 [("t", -1)] true) = .counterexample [("t", 0)]

-- The limits, at and just past each (spec 5's table: 64 facts, 16 unknowns, 10,000 combinations, each giving
-- `limit .derivationSteps`). Facts and unknowns are counted once, on the derivation's input: the premises and the
-- negated conclusion, with the square links' names among the unknowns.
def stepLimit : Answer := .unknown (.limit .derivationSteps)
/-- `n` premises x ≥ −i; with the negated conclusion x ≥ −1000 they are n + 1 facts, refuted in n combinations. -/
def ladder (n : Nat) : List QFact := (List.range n).map fun (i : Nat) => fact ((i : Int) : Rat) [("x", 1)] false
def xFloor : QFact := fact 1000 [("x", 1)] false
#guard checked (ladder 63) [] xFloor && Derive.search (ladder 63) [] xFloor matches .follows _
#guard Derive.search (ladder 64) [] xFloor = stepLimit
/-- `n` premises x_i ≥ 0 on `n` unknowns. -/
def spread (n : Nat) : List QFact := (List.range n).map fun i => fact 0 [(s!"x{i}", 1)] false
def x0Pos : QFact := fact 0 [("x0", 1)] false
#guard checked (spread 16) [] x0Pos && Derive.search (spread 16) [] x0Pos matches .follows _
#guard Derive.search (spread 17) [] x0Pos = stepLimit
#guard checked (spread 15) [("s", "x0")] x0Pos && Derive.search (spread 15) [("s", "x0")] x0Pos matches .follows _
#guard Derive.search (spread 16) [("s", "x0")] x0Pos = stepLimit
/-- `a₁` facts x + y ≥ 0, `a₂` facts x − y + 10 ≥ 0, `b` facts −x ≥ 0, `c` facts 5 − y ≥ 0 and `d` facts y + 1 ≥ 0:
eliminating x takes (a₁ + a₂)·b combinations and y then (a₁·b + d)·(a₂·b + c). They are consistent (x = y = 0). -/
def grid (a₁ a₂ b c d : Nat) : List QFact :=
  List.replicate a₁ (fact 0 [("x", 1), ("y", 1)] false) ++ List.replicate a₂ (fact 10 [("x", 1), ("y", -1)] false) ++
  List.replicate b (fact 0 [("x", -1)] false) ++ List.replicate c (fact 5 [("y", -1)] false) ++
  List.replicate d (fact 1 [("y", 1)] false)
/-- y > −1 follows from y ≥ 0; its negation −1 − y ≥ 0 is one more of the `c` facts. -/
def yAbove : QFact := fact 1 [("y", 1)] true
-- 14·14 + (6·14 + 2)·(8·14 + 2) = 10,000 combinations, the second elimination taking exactly what is left:
-- answered; 10·20 + (4·20 + 1)·(6·20 + 1) = 10,001: not, and answered with a budget of 10,001.
#guard checked (grid 6 8 14 1 2) [] yAbove && Derive.search (grid 6 8 14 1 2) [] yAbove matches .follows _
#guard Derive.search (grid 4 6 20 0 1) [] yAbove = stepLimit
#guard Derive.searchWithin 10001 (grid 4 6 20 0 1) [] yAbove matches .follows _

-- 64 facts whose second elimination needs 261,888 combinations, beyond the 10,000 (counted before they are built:
-- the first takes 1,024).
def wide : List QFact :=
  ((List.range 32).map fun (i : Nat) => fact 0 [("x", 1), ("y", ((i : Int) : Rat)), ("z", 1)] false) ++
  ((List.range 32).map fun (j : Nat) => fact 0 [("x", -1), ("y", -((j : Int) : Rat) - 1/2), ("z", 1)] false)
#guard ((FM.eliminate "x" (FM.inputRows wide)).run FM.maxSteps).toOption.map (FM.maxSteps - ·.2) = some 1024
#guard Derive.search wide [] (fact 0 [("z", 1)] true) = stepLimit

-- The budget covers the whole derivation, and running out anywhere is `limit .derivationSteps`, never
-- `derivationInconclusive` or another answer. r ≤ 1/3 under H-6 runs all five searches, each taking combinations:
-- the main one 2, the claimed bound 2, the least upper bound on s 2, and the two Farkas steps 3 and 3.
def rAtMost : QFact := fact (1/3) [("r", -1)] false
def cost {α : Type} (m : FM.Search α) : Nat := match m.run FM.maxSteps with | .ok (_, l) => FM.maxSteps - l | _ => 0
#guard [cost (FM.search (h6 (2/100) ++ [rAtMost.negate])), cost (boundCandidate (h6 (2/100)) links rAtMost),
  cost (FM.upperBound (h6 (2/100)) "s"), cost (farkasStep (h6 (2/100)) (fact (1/20) [("s", -1)] true)),
  cost (farkasStep (h6 (2/100) ++ [fact (1/20) [("s", -1)] true, below (1/3)]) rAtMost),
  cost (Derive.answer (h6 (2/100)) links rAtMost)] = [2, 2, 2, 3, 3, 12]
#guard checked (h6 (2/100)) links rAtMost && Derive.search (h6 (2/100)) links rAtMost matches .follows ⟨[_, _, _]⟩
/-- Below the `need` the derivation takes, every budget answers `limit .derivationSteps`; from `need` on, the full
answer. -/
def budgetSweep (P : List QFact) (links : List (String × String)) (C : QFact) (need : Nat) : Bool :=
  (List.range need).all (fun b => Derive.searchWithin b P links C == stepLimit) &&
    Derive.searchWithin need P links C == Derive.search P links C && Derive.search P links C != stepLimit
#guard budgetSweep (h6 (2/100)) links rAtMost 12
#guard budgetSweep (h6 (2/100)) links (below (1/4)) 9
#guard budgetSweep (h6 (2/100)) links (below (1/5)) 4
#guard budgetSweep (h6 (2/100)) links sBelow 3
#guard budgetSweep (h6 (2/100)) [] (below (1/4)) 2
#guard budgetSweep none3 [] (fact 0 [("x", 1)] true) 4
-- Review me-5 F2: 63 of `wide`'s facts with s added: the main search finds a point, then the claimed bound runs out.
def wideS : List QFact := (wide.drop 1).map fun f => ⟨⟨f.form.const, ("s", 1) :: f.form.coeffs⟩, f.strict⟩
#guard Derive.search wideS links (below (1/4)) = stepLimit
-- The same at r < 0, where the main search takes no combination and the square rule does not apply (0 is not a
-- positive bound): only the claimed bound's search (r = 0, s = 0, a counterexample if found) can run out.
#guard cost (FM.search (wideS ++ [(below 0).negate])) = 0 && Derive.search wideS links (below 0) = stepLimit
-- Two searches of 6,228 combinations each, the main one and the claimed bound's: each alone fits, together they do
-- not; with the budget for both, the claimed bound is the counterexample.
#guard cost (FM.search (grid 6 6 12 6 6)) = 6228
#guard Derive.search (grid 6 6 12 6 6) links (below (1/4)) = stepLimit
#guard match Derive.searchWithin 12456 (grid 6 6 12 6 6) links (below (1/4)) with
  | .counterexample κ =>
    κ.take 2 == [("r", 1/4), ("s", 1/16)] && counterexampleCheck (grid 6 6 12 6 6) links (below (1/4)) (pt κ)
  | _ => false

end VE.Calc.DeriveExamples
