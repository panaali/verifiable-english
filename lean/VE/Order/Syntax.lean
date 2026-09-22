import Std

/-! The opt-in order core. Integer quantification is excluded from this first
executable fragment: binders name user sorts only. Int is a separate constructor,
never a finite user domain. Wire adapters must reserve `$int` for `.int`. -/
namespace VE.Order

inductive SortName where
  | user (name : String)
  | int
  deriving DecidableEq, Repr, BEq

structure Environment where
  sorts : List String
  predicates : String → Option (List SortName)
  constants : String → Option SortName

inductive Term where
  | var (index : Nat)
  | const (name : String)
  | num (value : Int)
  | add (left right : Term)
  | scale (coefficient : Int) (term : Term)
  deriving DecidableEq, Repr, BEq

/-- Unary minus and subtraction are syntax sugar, never variable products. -/
def Term.neg (t : Term) : Term := .scale (-1) t
def Term.sub (t u : Term) : Term := .add t u.neg

inductive Formula where
  | top
  | bottom
  | unary (predicate : String) (term : Term)
  | binary (predicate : String) (left right : Term)
  | eq (left right : Term)
  | lt (left right : Term)
  | le (left right : Term)
  | not (body : Formula)
  | and (left right : Formula)
  | or (left right : Formula)
  | implies (left right : Formula)
  | all (sort : String) (body : Formula)
  | ex (sort : String) (body : Formula)
  deriving DecidableEq, Repr, BEq

def Term.sortOf (E : Environment) (Γ : List SortName) : Term → Option SortName
  | .var i => Γ[i]?
  | .const c => E.constants c
  | .num _ => some .int
  | .add t u => if t.sortOf E Γ = some .int ∧ u.sortOf E Γ = some .int
      then some .int else none
  | .scale _ t => if t.sortOf E Γ = some .int then some .int else none

/-- Typing does not infer undeclared sorts or permit equality across sorts. -/
def Formula.WellFormed (E : Environment) (Γ : List SortName) : Formula → Prop
  | .top | .bottom => True
  | .unary p t => ∃ s, E.predicates p = some [s] ∧ t.sortOf E Γ = some s
  | .binary p t u => ∃ s r, E.predicates p = some [s, r] ∧
      t.sortOf E Γ = some s ∧ u.sortOf E Γ = some r
  | .eq t u => ∃ s, t.sortOf E Γ = some s ∧ u.sortOf E Γ = some s
  | .lt t u | .le t u => t.sortOf E Γ = some .int ∧ u.sortOf E Γ = some .int
  | .not a => a.WellFormed E Γ
  | .and a b | .or a b | .implies a b => a.WellFormed E Γ ∧ b.WellFormed E Γ
  | .all s a | .ex s a => s ≠ "$int" ∧ s ∈ E.sorts ∧ a.WellFormed E (.user s :: Γ)

/-- A total executable scope, arity and sort checker. -/
def Formula.check (E : Environment) (Γ : List SortName) : Formula → Bool
  | .top | .bottom => true
  | .unary p t => match E.predicates p, t.sortOf E Γ with
      | some [s], some r => decide (s = r)
      | _, _ => false
  | .binary p t u => match E.predicates p, t.sortOf E Γ, u.sortOf E Γ with
      | some [s, r], some s', some r' => decide (s = s') && decide (r = r')
      | _, _, _ => false
  | .eq t u => match t.sortOf E Γ, u.sortOf E Γ with
      | some s, some r => decide (s = r)
      | _, _ => false
  | .lt t u | .le t u => decide (t.sortOf E Γ = some .int) &&
      decide (u.sortOf E Γ = some .int)
  | .not a => a.check E Γ
  | .and a b | .or a b | .implies a b => a.check E Γ && b.check E Γ
  | .all s a | .ex s a => s != "$int" && E.sorts.contains s && a.check E (.user s :: Γ)

/-- Documents are ordered and nonempty; every formula is closed and typed. -/
structure Document (E : Environment) where
  formulas : List Formula
  nonempty : formulas ≠ []
  wellFormed : ∀ a ∈ formulas, a.WellFormed E []

end VE.Order
