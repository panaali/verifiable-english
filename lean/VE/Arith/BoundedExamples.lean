import VE.Arith.Bounded
import VE.Arith.Examples

/-! The evaluation fixtures of plan 4.3 (spec 13.3): M-1, M-1b, M-2, M-4 at its measured bounds, M-4b, M-4x and the
evaluator's half of M-5, each budget boundary at, just under and just over its limit; then one fixture per clause of
the evaluator, on both sides, with its units. Budget 0 is the unknown row, never a verdict. -/

namespace VE.Arith.Examples
open VE.Arith VE.Numbers

/-! The budget: 1,000,000 by default and at most (W6's). Budget 0 refuses the first visit; the one-visit statement
needs exactly 1. -/
#guard maxSteps = 1000000 && maxSteps = VE.Time.maxEvaluations
#guard [0, 1, 2].map (decideBounded [] · (.eq (.num 0) (.num 0))) = [none, some (true, 1), some (true, 1)]
#guard decideBounded primeDefs 0 (m1 161) = none
#guard arithOutcome primeDefs 0 (m1 161) = .unknown (.limit .evaluations)

/-! M-1, M-1b, M-4x: holds, in exactly 17,011 units; one fewer, or 1,000, is unknown, never fails. -/
#guard decideBounded primeDefs maxSteps (m1 161) = some (true, 17011)
#guard [17010, 17011, 17012].map (decideBounded primeDefs · (m1 161)) = [none, some (true, 17011), some (true, 17011)]
#guard arithOutcome primeDefs maxSteps (m1 161) = .decided .holds
#guard arithOutcome primeDefs 17010 (m1 161) = .unknown (.limit .evaluations)
#guard arithOutcome primeDefs 1000 (m1 161) = .unknown (.limit .evaluations)

/-! M-2 holds; one link broken (163 against 81) fails. -/
#guard decideBounded primeDefs maxSteps m2 = some (true, 395)
#guard [394, 395].map (decideBounded primeDefs · m2) = [none, some (true, 395)]
#guard (decideBounded primeDefs maxSteps (.and m2 (.lt (.num 163) (.mul (.num 2) (.num 81))))).map (·.1) = some false

/-! M-3: stated, not decided, at every budget, before any evaluation. -/
#guard [0, maxSteps].map (arithOutcome primeDefs · bertrand) = [.unknown .unboundedStatement, .unknown .unboundedStatement]
#guard decideBounded primeDefs maxSteps bertrand = none

/-! M-5 fails in 2 units: the ∀ node and the ∃ at n = 1, whose range 2 … 1 is empty, so n = 1 decides it. -/
#guard [1, 2, 3].map (decideBounded primeDefs · m5) = [none, some (false, 2), some (false, 2)]
#guard arithOutcome primeDefs maxSteps m5 = .decided .fails
#guard arithOutcome primeDefs 1 m5 = .unknown (.limit .evaluations)
#guard decideBounded primeDefs maxSteps
  (.exFromTo (.add (.num 1) (.num 1)) (.sub (.mul (.num 2) (.num 1)) (.num 1)) (.call "prime" [.var 0])) = some (false, 1)
/-! M-5 from n = 2: no n from 2 through 161 decides it, so n = 1 is its deciding value. -/
#guard (decideBounded primeDefs maxSteps (.allFromTo (.num 2) (.num 161)
    (.exFromTo (.add (.var 0) (.num 1)) (.sub (.mul (.num 2) (.var 0)) (.num 1)) (.call "prime" [.var 0])))).map (·.1) =
  some true

/-! M-4: π(10) − π(5) = 1 and π(11) − π(5) = 2 (spec 13.3's 111 and 127 units for the difference, plus the `le` node);
measured at the candidate bounds 200 and 1,000, the completing bound is 248 within 1,000,000 units. -/
#guard decideBounded countDefs maxSteps (atLeast 2 (.num 10)) = some (false, 112)
#guard decideBounded countDefs maxSteps (atLeast 2 (.num 11)) = some (true, 128)
#guard decideBounded countDefs maxSteps (m4 2 11 200) = some (true, 576518)
#guard (decideBounded countDefs maxSteps (m4 2 11 247)).map (·.1) = some true
#guard decideBounded countDefs maxSteps (m4 2 11 248) = some (true, 998395)
#guard decideBounded countDefs maxSteps (m4 2 11 249) = none
#guard [1008567, 1008568, 1008569].map (decideBounded countDefs · (m4 2 11 249)) =
  [none, some (true, 1008568), some (true, 1008568)]
#guard decideBounded countDefs maxSteps (m4 2 11 1000) = none

/-! M-4b: each pair (k, T) fails at T − 1 and holds at T and T + 1; it holds through its measured bound N, unknown at
N + 1. -/
#guard [(1, 2), (3, 17), (4, 29), (5, 41)].map (fun (k, T) =>
    [T - 1, T, T + 1].map fun x => (decideBounded countDefs maxSteps (atLeast k (.num x))).map (·.1)) =
  List.replicate 4 [some false, some true, some true]
#guard decideBounded countDefs maxSteps (m4 1 2 248) = some (true, 998948)
#guard decideBounded countDefs maxSteps (m4 1 2 249) = none
#guard decideBounded countDefs maxSteps (m4 3 17 248) = some (true, 997399)
#guard decideBounded countDefs maxSteps (m4 3 17 249) = none
#guard decideBounded countDefs maxSteps (m4 4 29 248) = some (true, 993580)
#guard decideBounded countDefs maxSteps (m4 4 29 249) = none
#guard decideBounded countDefs maxSteps (m4 5 41 249) = some (true, 997116)
#guard decideBounded countDefs maxSteps (m4 5 41 250) = none

/-! Each clause of the evaluator, both ways, with its units: a term costs nothing, each formula node one. -/
def ev (D : Defs) (φ : Formula) : Option (Bool × Nat) := decideBounded D maxSteps φ
def yes : Formula := .eq (lit 1) (lit 1)
def no : Formula := .eq (lit 1) (lit 2)
#guard [ev [] (.eq (.add (lit 2) (lit 3)) (.sub (.mul (lit 2) (lit 4)) (lit 3))), ev [] (.eq (lit 2) (lit 3)),
  ev [] (.lt (lit 2) (lit 3)), ev [] (.lt (lit 3) (lit 3)), ev [] (.le (lit 3) (lit 3)), ev [] (.le (lit 4) (lit 3)),
  ev [] (.dvd (lit 3) (lit 6)), ev [] (.dvd (lit 4) (lit 6)), ev [] (.not no), ev [] (.not yes)] =
  [some (true, 1), some (false, 1), some (true, 1), some (false, 1), some (true, 1), some (false, 1),
   some (true, 1), some (false, 1), some (true, 2), some (false, 2)]
/-! Left to right, short-circuiting: the right side is visited only when the left does not decide. -/
#guard [ev [] (.and yes no), ev [] (.and no yes), ev [] (.and yes yes), ev [] (.or no yes), ev [] (.or yes no),
  ev [] (.or no no), ev [] (.imp yes no), ev [] (.imp no no), ev [] (.imp yes yes)] =
  [some (false, 3), some (false, 2), some (true, 3), some (true, 3), some (true, 2), some (false, 3),
   some (false, 3), some (true, 2), some (true, 3)]
/-! No unbounded quantifier is evaluated, at any budget. -/
#guard [Formula.allNat yes, .exNat yes, .allInt yes, .exInt yes].map (ev []) = [none, none, none, none]
/-! A range from lo through hi: tried in order, stopping at the first decisive value; empty when hi is below lo. -/
#guard [ev [] (.allFromTo (lit 1) (lit 3) (.lt (.var 0) (lit 4))), ev [] (.allFromTo (lit 1) (lit 4) (.lt (.var 0) (lit 4))),
  ev [] (.allFromTo (lit 1) (lit 4) (.lt (.var 0) (lit 2))), ev [] (.allFromTo (lit 2) (lit 1) no),
  ev [] (.exFromTo (lit 1) (lit 3) (.eq (.var 0) (lit 3))), ev [] (.exFromTo (lit 1) (lit 3) (.eq (.var 0) (lit 4))),
  ev [] (.exFromTo (lit 1) (lit 3) (.eq (.var 0) (lit 1))), ev [] (.exFromTo (lit 2) (lit 1) yes)] =
  [some (true, 4), some (false, 5), some (false, 3), some (true, 1),
   some (true, 4), some (false, 4), some (true, 2), some (false, 1)]
/-! A count visits every value of its range and counts those that hold (here 2, 4, 6 of 1 … 7); none when empty. -/
#guard [ev [] (.eq (.countFromTo (lit 1) (lit 7) (.dvd (lit 2) (.var 0))) (lit 3)),
  ev [] (.eq (.countFromTo (lit 1) (lit 7) (.dvd (lit 2) (.var 0))) (lit 4)),
  ev [] (.eq (.countFromTo (lit 1) (lit 0) yes) (lit 0)), ev [] (.eq (.countFromTo (lit 3) (lit 3) yes) (lit 1))] =
  [some (true, 8), some (false, 8), some (true, 1), some (true, 2)]
/-! Each binder puts its value first: the inner `var 1` reads the outer value, ranges start past it. -/
#guard [ev [] (.allFromTo (lit 1) (lit 3) (.allFromTo (lit 1) (.var 0) (.le (.var 0) (.var 1)))),
  ev [] (.allFromTo (lit 1) (lit 3) (.allFromTo (.var 0) (lit 3) (.le (.var 0) (.var 1)))),
  ev [] (.exFromTo (lit 5) (lit 9) (.eq (.countFromTo (lit 1) (.var 0) (.dvd (.var 0) (.var 1))) (lit 4))),
  ev [] (.eq (.countFromTo (lit 2) (lit 4) (.eq (.countFromTo (.var 0) (lit 4) yes) (.sub (lit 5) (.var 0)))) (lit 3))] =
  [some (true, 10), some (false, 4), some (true, 14), some (true, 10)]
/-! A variable no binder gives, and a call of a missing name or with the wrong arity, has no value: none. -/
#guard [ev [] (.eq (.var 0) (lit 0)), ev [] (.call "prime" [lit 7]), ev primeDefs (.call "prime" [lit 7, lit 1]),
  ev primeDefs (.eq (.call "prime" [lit 7]) (lit 1)), ev [.fn "one" 0 (lit 1)] (.eq (.call "one" [lit 1]) (lit 1))] =
  [none, none, none, none, none]
/-! Calls read the definitions in order, each over the ones above it; a call costs its body's visits (functions)
or one more (predicates). -/
#guard [ev chain (.eq (.call "one" []) (lit 1)), ev chain (.call "pos" [lit 3]), ev chain (.call "pos" [lit 0]),
  ev chain (.eq (.call "succ" [lit 3]) (lit 4)), ev chain (.call "big" [lit 3]), ev chain (.call "big" [lit 1]),
  ev chain (.eq (.call "minus" [lit 5, lit 3]) (lit 2)), ev chain (.eq (.call "minus" [lit 3, lit 5]) (lit 2))] =
  [some (true, 1), some (true, 2), some (false, 2), some (true, 1), some (true, 5), some (false, 5),
   some (true, 1), some (false, 1)]
/-! The budget is spent inside a definition's body too: `big 3` needs 5 visits. -/
#guard [4, 5].map (decideBounded chain · (.call "big" [lit 3])) = [none, some (true, 5)]
/-! The definitions are folded in order: a later definition of a name shadows an earlier one for the statements, and
the earlier one keeps its readers (admission refuses such a case as `DuplicateName`; this pins the fold's order). -/
#guard [ev [.fn "c" 0 (lit 1), .fn "d" 0 (.call "c" []), .fn "c" 0 (lit 2)] (.eq (.call "c" []) (lit 2)),
  ev [.fn "c" 0 (lit 1), .fn "d" 0 (.call "c" []), .fn "c" 0 (lit 2)] (.eq (.call "d" []) (lit 1)),
  ev [.pred "p" 0 yes, .pred "q" 0 (.call "p" []), .pred "p" 0 no] (.call "p" []),
  ev [.pred "p" 0 yes, .pred "q" 0 (.call "p" []), .pred "p" 0 no] (.call "q" [])] =
  [some (true, 1), some (true, 1), some (false, 2), some (true, 3)]
/-! The fixtures are admitted, so the soundness theorem applies to their answers. -/
#guard countDefs.WellFormed && chain.WellFormed && [m1 161, m5, m2, m4 2 11 248].all (·.Scoped countDefs 0)

/-- M-5's answer is its meaning, by `decideBounded_sound`. -/
example : ¬ primeDefs.Means m5 := fun h =>
  absurd ((decideBounded_sound primeDefs (by decide) m5 (by decide) maxSteps false 2 (by decide)).mp h) (by decide)

end VE.Arith.Examples
