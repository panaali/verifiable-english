import VE.Numbers.Phrases

namespace VE.Calc
open VE.Numbers

inductive Expr where
  | lit (q : Rat)
  | val (name : String)
  | add (a b : Expr)
  | sub (a b : Expr)
  | mul (a b : Expr)
  | div (a b : Expr)
  | pow (a : Expr) (k : Nat)
  deriving Repr, DecidableEq

abbrev Values := String → Option Rat

/-- Independent expression meaning; in particular, division needs a nonzero divisor. -/
inductive Denotes (σ : Values) : Expr → Rat → Prop
  | lit {q} : Denotes σ (.lit q) q
  | val {n q} : σ n = some q → Denotes σ (.val n) q
  | add {a b x y} : Denotes σ a x → Denotes σ b y → Denotes σ (.add a b) (x + y)
  | sub {a b x y} : Denotes σ a x → Denotes σ b y → Denotes σ (.sub a b) (x - y)
  | mul {a b x y} : Denotes σ a x → Denotes σ b y → Denotes σ (.mul a b) (x * y)
  | div {a b x y} : Denotes σ a x → Denotes σ b y → y ≠ 0 → Denotes σ (.div a b) (x / y)
  | pow {a x k} : Denotes σ a x → Denotes σ (.pow a k) (x ^ k)

def Expr.names : Expr → List String
  | .lit _ => []
  | .val n => [n]
  | .add a b | .sub a b | .mul a b | .div a b => a.names ++ b.names
  | .pow a _ => a.names

def Expr.subexprs : Expr → List Expr
  | .lit q => [.lit q]
  | .val n => [.val n]
  | .add a b => .add a b :: (a.subexprs ++ b.subexprs)
  | .sub a b => .sub a b :: (a.subexprs ++ b.subexprs)
  | .mul a b => .mul a b :: (a.subexprs ++ b.subexprs)
  | .div a b => .div a b :: (a.subexprs ++ b.subexprs)
  | .pow a k => .pow a k :: a.subexprs

inductive Claim where
  | compare (c : Comparison) (a b : Expr)
  | within (e lo hi : Expr)
  | rounds (r : Rounding) (e : Expr) (p : Printed)
  deriving Repr, DecidableEq

def Claim.exprs : Claim → List Expr
  | .compare _ a b => [a, b]
  | .within e lo hi => [e, lo, hi]
  | .rounds _ e _ => [e]

def Claim.Holds (σ : Values) : Claim → Prop
  | .compare c a b => ∃ x y, Denotes σ a x ∧ Denotes σ b y ∧ c.Holds x y
  | .within e lo hi =>
      ∃ x l h, Denotes σ e x ∧ Denotes σ lo l ∧ Denotes σ hi h ∧ l ≤ x ∧ x ≤ h
  | .rounds r e p => ∃ x, Denotes σ e x ∧ RoundsTo r p x

def Claim.Defined (σ : Values) (c : Claim) : Prop :=
  ∀ e ∈ c.exprs, ∃ q, Denotes σ e q

end VE.Calc
