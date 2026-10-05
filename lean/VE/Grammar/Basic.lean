/-! The grammar engine: matching, symbols, rules, grammars and well-formedness
(docs/spec/english-lean.md 2.4 and 5.2).

The engine is generic in the token type `T`, the terminal type `K` and the matching `Accepts K T`.
No definition here names a token or a terminal of an instance. `Grammar.wf` is conditions W1 to W3
of the specification; a condition about a sentence terminator belongs to an instance (W4).
-/

namespace VE.Grammar

/-- Which tokens a terminal accepts. The engine is generic in the token type `T`, the terminal
type `K` and this function. -/
class Accepts (K T : Type) where
  accepts : K → T → Bool

inductive Sym (K : Type) where
  | t (a : K)
  | n (A : Nat)
  deriving DecidableEq, Repr

structure Rule (K : Type) where
  lhs : Nat
  rhs : List (Sym K)
  act : Nat
  tag : String
  deriving DecidableEq, Repr

/-- Nonterminals are the numbers below `rank.size`. -/
structure Grammar (K : Type) where
  rules : Array (Rule K)
  start : Nat
  rank : Array Nat

variable {K : Type}

/-- W1 to W3 of the specification, for one rule. -/
def Rule.wf (G : Grammar K) (R : Rule K) : Bool :=
  decide (R.lhs < G.rank.size) &&
  !R.rhs.isEmpty &&
  R.rhs.all (fun
    | .t _ => true
    | .n A => decide (A < G.rank.size)) &&
  (match R.rhs with
    | .n B :: _ => decide (G.rank.getD B 0 < G.rank.getD R.lhs 0)
    | _ => true)

def Grammar.wf (G : Grammar K) : Bool :=
  decide (G.start < G.rank.size) && G.rules.all (Rule.wf G)

end VE.Grammar
