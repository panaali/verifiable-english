import Std

/-! VE v0 raw indexed syntax and extrinsic typing. Descriptions, version tags and
artifact hashes belong to the wire boundary, not the logical signature. -/
namespace VE

structure Environment where
  sorts : List String
  predicates : String → Option (List String)
  constants : String → Option String

def Environment.Valid (E : Environment) : Prop :=
  E.sorts.Nodup ∧
  (∀ p ss, E.predicates p = some ss →
    (ss.length = 1 ∨ ss.length = 2) ∧ ∀ s ∈ ss, s ∈ E.sorts) ∧
  (∀ c s, E.constants c = some s → s ∈ E.sorts)

inductive Term where
  | var (index : Nat)
  | const (name : String)
  deriving DecidableEq, Repr, BEq

inductive Formula where
  | top
  | bottom
  | unary (predicate : String) (term : Term)
  | binary (predicate : String) (left right : Term)
  | eq (left right : Term)
  | not (body : Formula)
  | and (left right : Formula)
  | or (left right : Formula)
  | implies (left right : Formula)
  | all (sort : String) (body : Formula)
  | ex (sort : String) (body : Formula)
  deriving DecidableEq, Repr, BEq

def Term.sortOf (E : Environment) (Γ : List String) : Term → Option String
  | .var i => Γ[i]?
  | .const c => E.constants c

/-- Typing does not infer undeclared sorts or permit equality across sorts. -/
def Formula.WellFormed (E : Environment) (Γ : List String) : Formula → Prop
  | .top | .bottom => True
  | .unary p t => ∃ s, E.predicates p = some [s] ∧ t.sortOf E Γ = some s
  | .binary p t u => ∃ s r, E.predicates p = some [s, r] ∧
      t.sortOf E Γ = some s ∧ u.sortOf E Γ = some r
  | .eq t u => ∃ s, t.sortOf E Γ = some s ∧ u.sortOf E Γ = some s
  | .not a => a.WellFormed E Γ
  | .and a b | .or a b | .implies a b => a.WellFormed E Γ ∧ b.WellFormed E Γ
  | .all s a | .ex s a => s ∈ E.sorts ∧ a.WellFormed E (s :: Γ)

/-- A total executable scope, arity and sort checker. -/
def Formula.check (E : Environment) (Γ : List String) : Formula → Bool
  | .top | .bottom => true
  | .unary p t => match E.predicates p, t.sortOf E Γ with
      | some [s], some r => s == r
      | _, _ => false
  | .binary p t u => match E.predicates p, t.sortOf E Γ, u.sortOf E Γ with
      | some [s, r], some s', some r' => s == s' && r == r'
      | _, _, _ => false
  | .eq t u => match t.sortOf E Γ, u.sortOf E Γ with
      | some s, some r => s == r
      | _, _ => false
  | .not a => a.check E Γ
  | .and a b | .or a b | .implies a b => a.check E Γ && b.check E Γ
  | .all s a | .ex s a => E.sorts.contains s && a.check E (s :: Γ)

/-- Documents are ordered and nonempty; every formula is closed and typed. -/
structure Document (E : Environment) where
  formulas : List Formula
  nonempty : formulas ≠ []
  wellFormed : ∀ a ∈ formulas, a.WellFormed E []

end VE
