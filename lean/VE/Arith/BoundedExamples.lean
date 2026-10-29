import VE.Arith.Bounded
import VE.Arith.TableExamples
import VE.Arith.Examples

/-! The evaluation fixtures of plan 4.3 (spec 13.3, draft 5): M-1, M-1b, M-2, M-4 at its measured bounds, M-4b, M-4x
and the evaluator's half of M-5, each budget boundary at, just under and just over its limit; then one fixture per
clause of the evaluator, on both sides, with its units; then B-1 to B-4, the chains the budget must stop. Budget 0 is
the unknown row, never a verdict. -/

namespace VE.Arith.Examples
open VE.Arith VE.Numbers

/-! The budget: 1,000,000 by default and at most (W6's). Budget 0 refuses the first visit; `0 = 0` needs exactly 5,
the `eq` node and each literal's visit and bit. -/
#guard maxSteps = 1000000 && maxSteps = VE.Time.maxEvaluations
#guard [0, 4, 5, 6].map (decideBounded [] · (.eq (.num 0) (.num 0))) = [none, none, some (true, 5), some (true, 5)]
#guard decideBounded primeDefs 0 (m1 161) = none
#guard arithOutcome primeDefs 0 (m1 161) = .unknown (.limit .evaluations)

/-! A value's size is its bit length, 1 for 0; a charge that would pass the budget is refused, one at the budget is
not; a range step charges its value, then its condition. -/
#guard [0, 1, -1, 2, 3, -4, 7, 1023, 1024, -1024].map bits = [1, 1, 1, 2, 2, 3, 3, 10, 11, 11]
#guard [chargeBits 10 1024 0, chargeBits 11 1024 0, chargeBits 12 1024 1, chargeBits 12 1024 2] =
  [none, some (1024, 11), some (1024, 12), none]
#guard [4, 5, 6].map (stepB · (fun i w => some (decide (i = 7), w)) 7 2) = [none, some (true, 5), some (true, 5)]

/-! Hand checks, each derived clause by clause in 13.3: a predicate call, an empty count, `pos 3`. -/
#guard decideBounded primeDefs maxSteps (.call "prime" [lit 7]) = some (true, 85)
#guard decideBounded [] maxSteps (.eq (.countFromTo (lit 1) (lit 0) (.eq (lit 0) (lit 0))) (lit 0)) = some (true, 9)
#guard decideBounded chain maxSteps (.call "pos" [lit 3]) = some (true, 10)

/-! M-1, M-1b, M-4x: holds, in exactly 337,735 units; one fewer, 1,000, or 13.2's draft-4 budgets 17,010 and 17,011,
is unknown, never fails. -/
#guard [337734, 337735, 337736].map (decideBounded primeDefs · (m1 161)) = [none, some (true, 337735), some (true, 337735)]
#guard [1000, 17010, 17011].map (decideBounded primeDefs · (m1 161)) = [none, none, none]
#guard arithOutcome primeDefs maxSteps (m1 161) = .decided .holds
#guard arithOutcome primeDefs 337734 (m1 161) = .unknown (.limit .evaluations)
#guard arithOutcome primeDefs 1000 (m1 161) = .unknown (.limit .evaluations)

/-! M-2 holds; one link broken (163 against 81) fails. -/
#guard [7419, 7420, 7421].map (decideBounded primeDefs · m2) = [none, some (true, 7420), some (true, 7420)]
#guard (decideBounded primeDefs maxSteps (.and m2 (.lt (.num 163) (.mul (.num 2) (.num 81))))).map (·.1) = some false

/-! M-3: stated, not decided, at every budget, before any evaluation. -/
#guard [0, maxSteps].map (arithOutcome primeDefs · bertrand) = [.unknown .unboundedStatement, .unknown .unboundedStatement]
#guard decideBounded primeDefs maxSteps bertrand = none

/-! M-5 fails in 33 units (13.3 derives them): the ∀ node, its range's ends, the step at n = 1, the ∃ node and its
ends; the range 2 … 1 is empty, so n = 1 decides it. -/
#guard [32, 33, 34].map (decideBounded primeDefs · m5) = [none, some (false, 33), some (false, 33)]
#guard arithOutcome primeDefs maxSteps m5 = .decided .fails
#guard arithOutcome primeDefs 32 m5 = .unknown (.limit .evaluations)
#guard decideBounded primeDefs maxSteps
  (.exFromTo (.add (.num 1) (.num 1)) (.sub (.mul (.num 2) (.num 1)) (.num 1)) (.call "prime" [.var 0])) = some (false, 20)
/-! M-5 from n = 2: no n from 2 through 161 decides it, so n = 1 is its deciding value. -/
#guard (decideBounded primeDefs maxSteps (.allFromTo (.num 2) (.num 161)
    (.exFromTo (.add (.var 0) (.num 1)) (.sub (.mul (.num 2) (.var 0)) (.num 1)) (.call "prime" [.var 0])))).map (·.1) =
  some true

/-! M-4: π(10) − π(5) = 1 and π(11) − π(5) = 2. Within 1,000,000 units the completing bound is 87 (draft 4: 248), so
13.2's candidate bounds 200, 248, 249 and 1,000 are unknown; 200 holds with a budget of 10,000,000. M-4b: each pair
(k, T) fails at T − 1 and holds at T and T + 1; it holds through its bound N and is unknown at N + 1, which holds with
the units it needs. -/
#guard decideBounded countDefs maxSteps (atLeast 2 (.num 10)) = some (false, 890)
#guard decideBounded countDefs maxSteps (atLeast 2 (.num 11)) = some (true, 1072)
#guard ([(1, 2), (3, 17), (4, 29), (5, 41)] : List (Int × Int)).map (fun (k, T) =>
    [T - 1, T, T + 1].map fun x => (decideBounded countDefs maxSteps (atLeast k (.num x))).map (·.1)) =
  List.replicate 4 [some false, some true, some true]
#guard ([(2, 11, 87, 973791, 1004183), (1, 2, 87, 977913, 1008304), (3, 17, 88, 995531, 1027872),
    (4, 29, 89, 989822, 1022334), (5, 41, 91, 981126, 1013976)] : List (Int × Int × Int × Nat × Nat)).all
  fun (k, T, N, u, u') => decideBounded countDefs maxSteps (m4 k T N) == some (true, u) &&
    decideBounded countDefs maxSteps (m4 k T (N + 1)) == none && decideBounded countDefs (u' - 1) (m4 k T (N + 1)) == none &&
    decideBounded countDefs u' (m4 k T (N + 1)) == some (true, u')
#guard [200, 248, 249, 1000].all fun N => decideBounded countDefs maxSteps (m4 2 11 N) == none
#guard decideBounded countDefs 10000000 (m4 2 11 200) = some (true, 9694873)

/-! Each clause of the evaluator, both ways, with its units: each node one visit, each term's value its bits. -/
def ev (D : Defs) (φ : Formula) : Option (Bool × Nat) := decideBounded D maxSteps φ
def yes : Formula := .eq (lit 1) (lit 1)
def no : Formula := .eq (lit 1) (lit 2)
#guard [ev [] (.eq (.add (lit 2) (lit 3)) (.sub (.mul (lit 2) (lit 4)) (lit 3))), ev [] (.eq (lit 2) (lit 3)),
  ev [] (.lt (lit 2) (lit 3)), ev [] (.lt (lit 3) (lit 3)), ev [] (.le (lit 3) (lit 3)), ev [] (.le (lit 4) (lit 3)),
  ev [] (.dvd (lit 3) (lit 6)), ev [] (.dvd (lit 4) (lit 6)), ev [] (.not no), ev [] (.not yes)] =
  [some (true, 30), some (false, 7), some (true, 7), some (false, 7), some (true, 7), some (false, 8),
   some (true, 8), some (false, 9), some (true, 7), some (false, 6)]
/-! Left to right, short-circuiting: the right side is visited only when the left does not decide. -/
#guard [ev [] (.and yes no), ev [] (.and no yes), ev [] (.and yes yes), ev [] (.or no yes), ev [] (.or yes no),
  ev [] (.or no no), ev [] (.imp yes no), ev [] (.imp no no), ev [] (.imp yes yes)] =
  [some (false, 12), some (false, 7), some (true, 11), some (true, 12), some (true, 6), some (false, 13),
   some (false, 12), some (true, 7), some (true, 11)]
/-! No unbounded quantifier is evaluated, at any budget. -/
#guard [Formula.allNat yes, .exNat yes, .allInt yes, .exInt yes].map (ev []) = [none, none, none, none]
/-! A range from lo through hi: tried in order, stopping at the first decisive value; empty when hi is below lo. -/
#guard [ev [] (.allFromTo (lit 1) (lit 3) (.lt (.var 0) (lit 4))), ev [] (.allFromTo (lit 1) (lit 4) (.lt (.var 0) (lit 4))),
  ev [] (.allFromTo (lit 1) (lit 4) (.lt (.var 0) (lit 2))), ev [] (.allFromTo (lit 2) (lit 1) no),
  ev [] (.exFromTo (lit 1) (lit 3) (.eq (.var 0) (lit 3))), ev [] (.exFromTo (lit 1) (lit 3) (.eq (.var 0) (lit 4))),
  ev [] (.exFromTo (lit 1) (lit 3) (.eq (.var 0) (lit 1))), ev [] (.exFromTo (lit 2) (lit 1) yes)] =
  [some (true, 34), some (false, 47), some (false, 23), some (true, 6),
   some (true, 31), some (false, 34), some (true, 12), some (false, 6)]
/-! A count visits every value of its range and counts those that hold (here 2, 4, 6 of 1 … 7); none when empty. -/
#guard [ev [] (.eq (.countFromTo (lit 1) (lit 7) (.dvd (lit 2) (.var 0))) (lit 3)),
  ev [] (.eq (.countFromTo (lit 1) (lit 7) (.dvd (lit 2) (.var 0))) (lit 4)),
  ev [] (.eq (.countFromTo (lit 1) (lit 0) yes) (lit 0)), ev [] (.eq (.countFromTo (lit 3) (lit 3) yes) (lit 1))] =
  [some (true, 82), some (false, 83), some (true, 9), some (true, 18)]
/-! Each binder puts its value first: the inner `var 1` reads the outer value, ranges start past it. -/
#guard [ev [] (.allFromTo (lit 1) (lit 3) (.allFromTo (lit 1) (.var 0) (.le (.var 0) (.var 1)))),
  ev [] (.allFromTo (lit 1) (lit 3) (.allFromTo (.var 0) (lit 3) (.le (.var 0) (.var 1)))),
  ev [] (.exFromTo (lit 5) (lit 9) (.eq (.countFromTo (lit 1) (.var 0) (.dvd (.var 0) (.var 1))) (lit 4))),
  ev [] (.eq (.countFromTo (lit 2) (lit 4) (.eq (.countFromTo (.var 0) (lit 4) yes) (.sub (lit 5) (.var 0)))) (lit 3))] =
  [some (true, 75), some (false, 27), some (true, 161), some (true, 129)]
/-! A variable no binder gives, and a call of a missing name or with the wrong arity, has no value: none. -/
#guard [ev [] (.eq (.var 0) (lit 0)), ev [] (.call "prime" [lit 7]), ev primeDefs (.call "prime" [lit 7, lit 1]),
  ev primeDefs (.eq (.call "prime" [lit 7]) (lit 1)), ev [.fn "one" 0 (lit 1)] (.eq (.call "one" [lit 1]) (lit 1))] =
  [none, none, none, none, none]
/-! Calls read the definitions in order, each over the ones above it; a call, of a function or a predicate, is one
visit plus its arguments' and its body's, and a function's result is charged its size. -/
#guard [ev chain (.eq (.call "one" []) (lit 1)), ev chain (.call "pos" [lit 3]), ev chain (.call "pos" [lit 0]),
  ev chain (.eq (.call "succ" [lit 3]) (lit 4)), ev chain (.call "big" [lit 3]), ev chain (.call "big" [lit 1]),
  ev chain (.eq (.call "minus" [lit 5, lit 3]) (lit 2)), ev chain (.eq (.call "minus" [lit 3, lit 5]) (lit 2))] =
  [some (true, 7), some (true, 10), some (false, 8), some (true, 23), some (true, 23), some (false, 19),
   some (true, 24), some (false, 24)]
/-! The budget is spent inside a definition's body too: `big 3` needs 23 units. -/
#guard [22, 23, 24].map (decideBounded chain · (.call "big" [lit 3])) = [none, some (true, 23), some (true, 23)]
/-! The definitions are folded in order: a later definition of a name shadows an earlier one for the statements, and
the earlier one keeps its readers (admission refuses such a case as `DuplicateName`; this pins the fold's order). -/
#guard [ev [.fn "c" 0 (lit 1), .fn "d" 0 (.call "c" []), .fn "c" 0 (lit 2)] (.eq (.call "c" []) (lit 2)),
  ev [.fn "c" 0 (lit 1), .fn "d" 0 (.call "c" []), .fn "c" 0 (lit 2)] (.eq (.call "d" []) (lit 1)),
  ev [.pred "p" 0 yes, .pred "q" 0 (.call "p" []), .pred "p" 0 no] (.call "p" []),
  ev [.pred "p" 0 yes, .pred "q" 0 (.call "p" []), .pred "p" 0 no] (.call "q" [])] =
  [some (true, 10), some (true, 9), some (false, 7), some (true, 7)]

/-! B-1 to B-4 (13.3): the chains whose work the budget must bound (me-12aa's N1 and its review's F1). Each is unknown
at 1,000,000 units within seconds (REPORT, me-12nb). B-1 is N1's pin: `f10` calls `f9` twice, and so on down, so `f0`
is evaluated 1,024 times; draft 4 decided it at budget 1. -/
def dbl (k : Nat) : Defs :=
  .fn "f0" 0 (lit 1) :: (List.range k).map fun i => .fn s!"f{i + 1}" 0 (.add (.call s!"f{i}" []) (.call s!"f{i}" []))
def dblx (k : Nat) : Defs :=
  .fn "f0" 1 (.var 0) :: (List.range k).map fun i =>
    .fn s!"f{i + 1}" 1 (.add (.call s!"f{i}" [.var 0]) (.call s!"f{i}" [.var 0]))
def sqChain (k : Nat) : Defs :=
  .fn "sq" 1 (.mul (.var 0) (.var 0)) :: .fn "g0" 0 (lit 2) ::
    (List.range k).map fun i => .fn s!"g{i + 1}" 0 (.call "sq" [.call s!"g{i}" []])
def reuse : Defs := sqChain 16 ++ [.fn "r" 2 (.countFromTo (lit 1) (lit 999000) (.dvd (.var 1) (.var 2)))]
def reuseStmt : Formula := .le (lit 0) (.call "r" [.add (.call "g15" []) (lit 1), .call "g16" []])
#guard (dbl 24).WellFormed && (dblx 24).WellFormed && (sqChain 31).WellFormed && reuse.WellFormed &&
  (Formula.lt (lit 0) (.call "f24" [])).Bounded (dbl 24) && (Formula.lt (lit 0) (.call "g31" [])).Bounded (sqChain 31) &&
  reuseStmt.Bounded reuse && reuseStmt.Scoped reuse 0
#guard decideBounded (dbl 2) maxSteps (.eq (lit 4) (.call "f2" [])) = some (true, 41)
#guard [1, 1000, 12272, 12273, 12274].map (decideBounded (dbl 10) · (.eq (lit 1024) (.call "f10" []))) =
  [none, none, none, some (true, 12273), some (true, 12273)]
#guard decideBounded (dbl 24) maxSteps (.lt (lit 0) (.call "f24" [])) = none
#guard decideBounded (dblx 2) maxSteps (.eq (lit 4) (.call "f2" [lit 1])) = some (true, 55)
#guard decideBounded (dblx 24) maxSteps (.lt (lit 0) (.call "f24" [lit 1])) = none
/-! B-3, F1's squaring chain: `0 < g_k` costs 8 · 2^k + 10k + 1 units. -/
#guard decideBounded (sqChain 3) maxSteps (.lt (lit 0) (.call "g3" [])) = some (true, 95)
#guard decideBounded (sqChain 16) maxSteps (.lt (lit 0) (.call "g16" [])) = some (true, 524449)
#guard [maxSteps, 1048746, 1048747].map (decideBounded (sqChain 17) · (.lt (lit 0) (.call "g17" []))) =
  [none, none, some (true, 1048747)]
#guard decideBounded (sqChain 31) maxSteps (.lt (lit 0) (.call "g31" [])) = none
/-! B-4: a 65,537-bit value passed as a parameter costs its bits at every read. -/
#guard decideBounded reuse maxSteps reuseStmt = none

/-! The fixtures are admitted, so the soundness theorem applies to their answers. -/
#guard countDefs.WellFormed && chain.WellFormed && [m1 161, m5, m2, m4 2 11 87].all (·.Scoped countDefs 0)

/-- M-5's answer is its meaning, by `decideBounded_sound`. -/
example : ¬ primeDefs.Means m5 := fun h =>
  absurd ((decideBounded_sound primeDefs (by decide) m5 (by decide) maxSteps false 33 (by decide)).mp h) (by decide)

end VE.Arith.Examples
