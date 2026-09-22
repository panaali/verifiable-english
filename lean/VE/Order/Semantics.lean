import VE.Order.Typing

namespace VE.Order
universe u

/-- Disjoint object and standard integer values. Integers are never enumerated
by a structure, truncated to a machine word, or supplied by a user domain. -/
abbrev Value (α : Type u) := Sum α Int

structure Structure where
  Carrier : Type u
  objects : String → Carrier → Prop
  constant : String → Option (Value Carrier)
  relation : String → List (Value Carrier) → Prop

def Structure.domain (S : Structure) : SortName → Value S.Carrier → Prop
  | .user s, .inl v => S.objects s v
  | .int, .inr _ => True
  | _, _ => False

def TupleTyped (S : Structure) : List SortName → List (Value S.Carrier) → Prop
  | [], [] => True
  | s :: ss, v :: vs => S.domain s v ∧ TupleTyped S ss vs
  | _, _ => False

def Structure.Admissible (S : Structure) (E : Environment) : Prop :=
  (∀ c s, E.constants c = some s →
    ∃ v, S.constant c = some v ∧ S.domain s v) ∧
  (∀ p vs, S.relation p vs → ∃ ss, E.predicates p = some ss ∧ TupleTyped S ss vs)

abbrev Valuation (S : Structure) := List (Value S.Carrier)

def Term.denote (S : Structure) (ρ : Valuation S) : Term → Option (Value S.Carrier)
  | .var i => ρ[i]?
  | .const c => S.constant c
  | .num z => some (.inr z)
  | .add t u => match t.denote S ρ, u.denote S ρ with
      | some (.inr x), some (.inr y) => some (.inr (x + y))
      | _, _ => none
  | .scale z t => match t.denote S ρ with
      | some (.inr x) => some (.inr (z * x))
      | _ => none

/-- Comparison is false on undefined terms and on object values, even in raw
ill-typed syntax. Typed terms are proved defined separately. -/
def Compare {α : Type u} (R : Int → Int → Prop) (x y : Option (Value α)) : Prop :=
  ∃ a b, x = some (.inr a) ∧ y = some (.inr b) ∧ R a b

def Formula.denote (S : Structure) (ρ : Valuation S) : Formula → Prop
  | .top => True
  | .bottom => False
  | .unary p t => ∃ v, t.denote S ρ = some v ∧ S.relation p [v]
  | .binary p t u => ∃ v w, t.denote S ρ = some v ∧
      u.denote S ρ = some w ∧ S.relation p [v, w]
  | .eq t u => ∃ v, t.denote S ρ = some v ∧ u.denote S ρ = some v
  | .lt t u => Compare (· < ·) (t.denote S ρ) (u.denote S ρ)
  | .le t u => Compare (· ≤ ·) (t.denote S ρ) (u.denote S ρ)
  | .not a => ¬ a.denote S ρ
  | .and a b => a.denote S ρ ∧ b.denote S ρ
  | .or a b => a.denote S ρ ∨ b.denote S ρ
  | .implies a b => a.denote S ρ → b.denote S ρ
  | .all s a => ∀ v, S.objects s v → a.denote S (.inl v :: ρ)
  | .ex s a => ∃ v, S.objects s v ∧ a.denote S (.inl v :: ρ)

def Valuation.Typed (S : Structure) (Γ : List SortName) (ρ : Valuation S) : Prop :=
  ∀ (i : Nat) s, Γ[i]? = some s → ∃ v, ρ[i]? = some v ∧ S.domain s v

theorem integer_of_domain {S : Structure} {v : Value S.Carrier}
    (h : S.domain .int v) : ∃ z, v = .inr z := by
  cases v with
  | inl a => exact False.elim h
  | inr z => exact ⟨z, rfl⟩

theorem term_defined {E : Environment} {S : Structure} (hS : S.Admissible E)
    {Γ : List SortName} {ρ : Valuation S} (hρ : Valuation.Typed S Γ ρ)
    {t : Term} {s : SortName} (ht : t.sortOf E Γ = some s) :
    ∃ v, t.denote S ρ = some v ∧ S.domain s v := by
  induction t generalizing s with
  | var i => exact hρ i s ht
  | const c => exact hS.1 c s ht
  | num z =>
    simp only [Term.sortOf, Option.some.injEq] at ht
    subst s
    exact ⟨.inr z, rfl, trivial⟩
  | add t u it iu =>
    simp only [Term.sortOf] at ht
    split at ht
    next h =>
      cases ht
      obtain ⟨v, hv, hd⟩ := it h.1
      obtain ⟨w, hw, he⟩ := iu h.2
      obtain ⟨x, rfl⟩ := integer_of_domain hd
      obtain ⟨y, rfl⟩ := integer_of_domain he
      exact ⟨.inr (x+y), by simp [Term.denote, hv, hw], trivial⟩
    next => contradiction
  | scale z t it =>
    simp only [Term.sortOf] at ht
    split at ht
    next h =>
      cases ht
      obtain ⟨v, hv, hd⟩ := it h
      obtain ⟨x, rfl⟩ := integer_of_domain hd
      exact ⟨.inr (z*x), by simp [Term.denote, hv], trivial⟩
    next => contradiction

theorem numerals_distinct (S : Structure) (ρ : Valuation S) (x y : Int) :
    (Formula.eq (.num x) (.num y)).denote S ρ ↔ x = y := by
  simp [Formula.denote, Term.denote, eq_comm]

end VE.Order
