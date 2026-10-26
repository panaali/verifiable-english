import VE.Numbers.Round

/-! `arith@0`'s statements (spec 12.1): terms and formulas over whole numbers and integers, with de Bruijn variables,
calls of defined names and bounded counts, and the list of definitions they call. -/

namespace VE.Arith

mutual
inductive Term where
  | var (i : Nat)
  | num (n : Int)
  | add (a b : Term)
  | sub (a b : Term)
  | mul (a b : Term)
  | call (f : String) (args : List Term)
  | countFromTo (lo hi : Term) (φ : Formula)
inductive Formula where
  | eq (a b : Term)
  | lt (a b : Term)
  | le (a b : Term)
  | dvd (a b : Term)
  | call (p : String) (args : List Term)
  | not (φ : Formula)
  | and (φ ψ : Formula)
  | or (φ ψ : Formula)
  | imp (φ ψ : Formula)
  | allNat (φ : Formula)
  | exNat (φ : Formula)
  | allInt (φ : Formula)
  | exInt (φ : Formula)
  | allFromTo (lo hi : Term) (φ : Formula)
  | exFromTo (lo hi : Term) (φ : Formula)
end

/-- Definitions in order; a body reads its parameters as `var 0 … var (arity − 1)` and only earlier names. -/
inductive Def where
  | fn (name : String) (arity : Nat) (body : Term)
  | pred (name : String) (arity : Nat) (body : Formula)

abbrev Defs := List Def

end VE.Arith
