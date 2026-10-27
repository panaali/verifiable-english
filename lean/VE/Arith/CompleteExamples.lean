import VE.Arith.BoundedExamples

/-! The fixtures of spec 12.2's `decideBounded_mono` and `decideBounded_complete`: each statement's work W is the
first budget that decides it, and every budget from there on gives the same answer and units (W − 1, W and W + 1, then
the whole sweep). Each hypothesis of completeness on its refusing side: no budget decides without it. -/

namespace VE.Arith.Examples
open VE.Arith

/-- Whether each budget from 0 through `n` is decided: none below the work, then decided, each answer kept. -/
def sweep (D : Defs) (φ : Formula) (n : Nat) : List Bool := (List.range (n + 1)).map (decideBounded D · φ |>.isSome)
def keeps (D : Defs) (φ : Formula) (n : Nat) : Bool :=
  (List.range n).all fun l => (decideBounded D l φ).all fun r => decideBounded D (l + 1) φ == some r

/-! Admitted and bounded: decided exactly from the work on, with calls, counts, nested binders and short circuits. -/
#guard chain.WellFormed && countDefs.WellFormed && [(chain, Formula.call "big" [lit 3]), (chain, .call "big" [lit 1]),
  (primeDefs, m5), (countDefs, atLeast 2 (.num 11)), (chain, .imp (.call "pos" [lit 0]) no)].all fun (D, φ) =>
    φ.Scoped D 0 && φ.Bounded D
#guard sweep chain (.call "big" [lit 3]) 6 = [false, false, false, false, false, true, true]
#guard [4, 5, 6].map (decideBounded chain · (.call "big" [lit 1])) = [none, some (false, 5), some (false, 5)]
#guard sweep primeDefs m5 3 = [false, false, true, true]
#guard [127, 128, 129].map (decideBounded countDefs · (atLeast 2 (.num 11))) = [none, some (true, 128), some (true, 128)]
#guard [2, 3, 4].map (decideBounded chain · (.imp (.call "pos" [lit 0]) no)) = [none, some (true, 3), some (true, 3)]
#guard [395, 396].map (decideBounded primeDefs · m2) = [some (true, 395), some (true, 395)]
#guard keeps chain (.call "big" [lit 3]) 40 && keeps primeDefs m5 40 && keeps countDefs (atLeast 2 (.num 11)) 200 &&
  keeps [] (.allFromTo (lit 1) (lit 3) (.allFromTo (lit 1) (.var 0) (.le (.var 0) (.var 1)))) 40 &&
  keeps chain (.eq (.call "succ" [lit 3]) (lit 4)) 6

/-! The refusing side: without boundedness, scoping or well-formed definitions, no budget decides. An unbounded
statement, a variable no binder gives, a call with the wrong arity, a missing name and a recursive definition. -/
def selfCall : Defs := [.fn "f" 0 (.call "f" [])]
#guard [Formula.allNat yes, .eq (.var 0) (lit 0), .call "prime" [lit 7, lit 1], .call "odd" [lit 7]].all fun φ =>
  [0, 1, maxSteps].all (decideBounded primeDefs · φ == none)
#guard !(Formula.allNat yes).Bounded primeDefs && (Formula.allNat yes).Scoped primeDefs 0 &&
  !(Formula.eq (.var 0) (lit 0)).Scoped primeDefs 0 && !(Formula.call "prime" [lit 7, lit 1]).Scoped primeDefs 0 &&
  !(Formula.call "odd" [lit 7]).Scoped primeDefs 0
#guard !selfCall.WellFormed && [0, 1, maxSteps].all (decideBounded selfCall · (.eq (.call "f" []) (lit 0)) == none)

/-! Why `decideBounded_mono` needs `Defs.opEnv`: in an environment that reads the budget (`tick` is the limit), the
larger budget changes the answer. -/
def tickEnv (limit : Nat) : OpEnv :=
  ⟨fun f => if f = "tick" then some (0, fun _ w => some ((limit : Int), w)) else none, fun _ => none⟩
#guard [5, 6].map (fun l => Formula.evalB (tickEnv l) l [] (.eq (.call "tick" []) (lit 5)) 0) =
  [some (true, 1), some (false, 1)]

/-- The theorems on a fixture: M-5 is decided at some budget, and the larger budget keeps its answer. -/
example : ∃ limit r, decideBounded primeDefs limit m5 = some r :=
  decideBounded_complete primeDefs (by decide) m5 (by decide) (by decide)
example : decideBounded primeDefs maxSteps m5 = some (false, 2) :=
  decideBounded_mono primeDefs m5 2 maxSteps (false, 2) (by decide) (by decide)

end VE.Arith.Examples
