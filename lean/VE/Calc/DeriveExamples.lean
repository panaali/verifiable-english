import VE.Calc.Derive

/-! Fixtures of ME-5 at the level of facts (spec 13.2, 13.3): H-6, H-6p, H-6n, H-6a (debate A2), a linear system with
no solution, and a forged certificate with a negative weight. The lowering of claims to these facts is me-5b's. -/

namespace VE.Calc.DeriveExamples
open VE.Calc

def fact (k : Rat) (cs : List (String × Rat)) (strict : Bool) : QFact := ⟨⟨k, cs⟩, strict⟩
def pt (κ : List (String × Rat)) : String → Rat := Answer.point κ

/-- H-6's premises: d = 0.4 s as two facts, and d < 0.02 (Michelson and Morley 1887, h115-h116). -/
def h6 (bound : Rat) : List QFact :=
  [fact 0 [("d", 1), ("s", -2/5)] false, fact 0 [("s", 2/5), ("d", -1)] false, fact bound [("d", -1)] true]
def links : List (String × String) := [("s", "r")]
/-- "r is less than b". -/
def below (b : Rat) : QFact := fact b [("r", -1)] true

/-! H-6: r < 1/4 follows, with R-3's certificate. -/
def h6First : Step := .farkas (fact (1/20) [("s", -1)] true) ⟨[1, 0, 1, 2/5]⟩
def h6Steps : List Step := [h6First, .square "s" "r" (1/20) (1/4)]
#guard Derive.run (h6 (2/100)) links (below (1/4)) = .follows ⟨h6Steps⟩
#guard Derivation.check (h6 (2/100)) links (below (1/4)) ⟨h6Steps⟩
#guard Farkas.check (h6 (2/100) ++ [(fact (1/20) [("s", -1)] true).negate]) ⟨[1, 0, 1, 2/5]⟩
#guard !Farkas.check (h6 (2/100) ++ [(fact (1/20) [("s", -1)] true).negate]) ⟨[1, 0, 1, -2/5]⟩
#guard (1/20 : Rat) ≤ (1/4) * (1/4)
-- Without the link the conclusion does not follow: r is unconstrained.
#guard Derive.run (h6 (2/100)) [] (below (1/4)) matches .counterexample _

/-! H-6p: d < 0.01 gives r < 1/6, with the same weights. -/
#guard Derive.run (h6 (1/100)) links (below (1/6)) =
  .follows ⟨[.farkas (fact (1/40) [("s", -1)] true) ⟨[1, 0, 1, 2/5]⟩, .square "s" "r" (1/40) (1/6)]⟩
#guard (1/40 : Rat) ≤ (1/6) * (1/6)

/-! H-6n: r < 1/5 does not follow; the claimed bound is tried first (R-4's counterexample). -/
#guard Derive.run (h6 (2/100)) links (below (1/5)) = .counterexample [("r", 1/5), ("s", 1/25), ("d", 2/125)]
#guard counterexampleCheck (h6 (2/100)) links (below (1/5)) (pt [("r", 1/5), ("s", 1/25), ("d", 2/125)])
#guard !decide ((1/20 : Rat) ≤ (1/5) * (1/5))

/-! H-6a (debate A2): s = 0, r = 1 against r < 1/4 breaks the link s = r², so it is no counterexample with the link;
without links it would be one. -/
#guard !counterexampleCheck (h6 (2/100)) links (below (1/4)) (pt [("r", 1), ("s", 0), ("d", 0)])
#guard counterexampleCheck (h6 (2/100)) [] (below (1/4)) (pt [("r", 1), ("s", 0), ("d", 0)])
-- The root's nonnegativity is part of the link: s = 1/25, r = -1/5 meets s = r² but not 0 ≤ r.
#guard !counterexampleCheck (h6 (2/100)) links (below (-1/5)) (pt [("r", -1/5), ("s", 1/25), ("d", 2/125)])

/-! A linear system with no solution: x + y ≥ 2, x ≤ 0, y ≤ 0; its certificate weighs each fact once. -/
def none3 : List QFact := [fact (-2) [("x", 1), ("y", 1)] false, fact 0 [("x", -1)] false, fact 0 [("y", -1)] false]
#guard Farkas.check none3 ⟨[1, 1, 1]⟩
#guard match FM.search none3 with | .refuted ws => Farkas.check none3 ⟨ws⟩ | _ => false
#guard !Farkas.check none3 ⟨[1, 1]⟩
#guard !Farkas.check none3 ⟨[1, 1, 0]⟩
-- Anything follows from it, by one Farkas step.
#guard Derive.run none3 [] (fact 0 [("x", 1)] true) matches .follows _
-- A strict fact closes a zero constant: x > 0 and x ≤ 0.
#guard Farkas.check [fact 0 [("x", 1)] true, fact 0 [("x", -1)] false] ⟨[1, 1]⟩
#guard !Farkas.check [fact 0 [("x", 1)] false, fact 0 [("x", -1)] false] ⟨[1, 1]⟩

/-! A forged certificate with a negative weight is refused: from H-6's premises s < 1/25 is false (s may be up to
1/20), and the weights [0, 1, -1, -2/5] cancel every unknown and leave -1/250. -/
def forged : Farkas := ⟨[0, 1, -1, -2/5]⟩
#guard (forged.combination (h6 (2/100) ++ [(fact (1/25) [("s", -1)] true).negate])).const = -1/250
#guard !Farkas.check (h6 (2/100) ++ [(fact (1/25) [("s", -1)] true).negate]) forged
#guard !Derivation.check (h6 (2/100)) links (fact (1/25) [("s", -1)] true) ⟨[.farkas (fact (1/25) [("s", -1)] true) forged]⟩
-- The search does not refute it either: its linear point breaks the link, and the conclusion bounds no root.
#guard Derive.run (h6 (2/100)) links (fact (1/25) [("s", -1)] true) = .unknown .derivationInconclusive

/-! The square step needs its link, its established bound and a ≤ b². -/
#guard !Derivation.check (h6 (2/100)) [] (below (1/4)) ⟨h6Steps⟩
#guard !Derivation.check (h6 (2/100)) links (below (1/5)) ⟨[h6First, .square "s" "r" (1/20) (1/5)]⟩
#guard !Derivation.check (h6 (2/100)) links (below (1/4)) ⟨[.square "s" "r" (1/20) (1/4)]⟩
-- The conclusion must be the last derived fact.
#guard !Derivation.check (h6 (2/100)) links (below (1/3)) ⟨h6Steps⟩
#guard Derive.run (h6 (2/100)) links (fact (1/3) [("r", -1)] false) matches .follows _

/-! The budget: 17 unknowns are beyond the 16 the search takes. -/
#guard Derive.run ((List.range 17).map fun i => fact 0 [(s!"x{i}", 1)] false) [] (fact 0 [("x0", 1)] true) =
  .unknown (.limit .derivationSteps)

end VE.Calc.DeriveExamples
