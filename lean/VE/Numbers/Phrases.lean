import VE.Numbers.Round

namespace VE.Numbers

inductive Rel where
  | eq | lt | le
  deriving Repr, DecidableEq

def Rel.Holds : Rel → Rat → Rat → Prop
  | .eq, x, y => x = y
  | .lt, x, y => x < y
  | .le, x, y => x ≤ y

structure Comparison where
  rel : Rel
  swap : Bool
  deriving Repr, DecidableEq

def Comparison.Holds (c : Comparison) (x y : Rat) : Prop :=
  if c.swap then c.rel.Holds y x else c.rel.Holds x y

instance (c : Comparison) (x y : Rat) : Decidable (c.Holds x y) := by
  cases c with
  | mk rel swap =>
    cases rel <;> cases swap <;> dsimp [Comparison.Holds, Rel.Holds] <;> infer_instance

def orderPhrases : List (String × Comparison) :=
  [("{0} is less than {1}", ⟨.lt, false⟩),
   ("{0} is at most {1}", ⟨.le, false⟩),
   ("{0} is more than {1}", ⟨.lt, true⟩),
   ("{0} is at least {1}", ⟨.le, true⟩)]

def equalsPhrase : String × Comparison := ("{0} equals {1}", ⟨.eq, false⟩)
def withinPhrase : String := "{0} is from {1} through {2}"

end VE.Numbers
