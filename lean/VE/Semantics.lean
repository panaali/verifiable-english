import VE.Syntax

namespace VE
universe u

/-- A common carrier with a domain predicate per sort is an extrinsic presentation
of many-sorted structures. It admits arbitrary (including infinite) carriers and
empty sort domains. No carrier or sort is assumed inhabited. For disjoint carriers
one can take their tagged union. Only well-typed formulas are semantic claims. -/
structure Structure where
  Carrier : Type u
  domain : String → Carrier → Prop
  constant : String → Option Carrier
  relation : String → List Carrier → Prop

def TupleTyped (S : Structure) : List String → List S.Carrier → Prop
  | [], [] => True
  | s :: ss, v :: vs => S.domain s v ∧ TupleTyped S ss vs
  | _, _ => False

/-- Constants inhabit their declared sorts; true tuples have declared signatures.
There is no distinct-name or nonempty-domain assumption. -/
def Structure.Admissible (S : Structure) (E : Environment) : Prop :=
  (∀ c s, E.constants c = some s →
    ∃ v, S.constant c = some v ∧ S.domain s v) ∧
  (∀ p vs, S.relation p vs → ∃ ss, E.predicates p = some ss ∧
    TupleTyped S ss vs)

abbrev Valuation (S : Structure) := List S.Carrier

def Term.denote (S : Structure) (ρ : Valuation S) : Term → Option S.Carrier
  | .var i => ρ[i]?
  | .const c => S.constant c

def Valuation.Typed (S : Structure) (Γ : List String) (ρ : Valuation S) : Prop :=
  ∀ (i : Nat) s, Γ[i]? = some s → ∃ v, ρ[i]? = some v ∧ S.domain s v

/-- Explicit Tarski semantics. Undefined raw terms denote false atoms; the
term_defined theorem rules them out in typed claims and typed valuations. -/
def Formula.denote (S : Structure) (ρ : Valuation S) : Formula → Prop
  | .top => True
  | .bottom => False
  | .unary p t => ∃ v, t.denote S ρ = some v ∧ S.relation p [v]
  | .binary p t u => ∃ v w, t.denote S ρ = some v ∧
      u.denote S ρ = some w ∧ S.relation p [v, w]
  | .eq t u => ∃ v, t.denote S ρ = some v ∧ u.denote S ρ = some v
  | .not a => ¬ a.denote S ρ
  | .and a b => a.denote S ρ ∧ b.denote S ρ
  | .or a b => a.denote S ρ ∨ b.denote S ρ
  | .implies a b => a.denote S ρ → b.denote S ρ
  | .all s a => ∀ v, S.domain s v → a.denote S (v :: ρ)
  | .ex s a => ∃ v, S.domain s v ∧ a.denote S (v :: ρ)

def Document.denote {E : Environment} (d : Document E) (S : Structure) : Prop :=
  ∀ a ∈ d.formulas, a.denote S []

/-- Consequence ranges over every admissible structure in universe u, rather
than over the finite models used by the executable. -/
def Entails (E : Environment) (premises : List Formula) (conclusion : Formula) : Prop :=
  ∀ S : Structure.{u}, S.Admissible E →
    (∀ a ∈ premises, a.denote S []) → conclusion.denote S []

theorem term_defined {E : Environment} {S : Structure} (hS : S.Admissible E)
    {Γ : List String} {ρ : Valuation S} (hρ : Valuation.Typed S Γ ρ)
    {t : Term} {s : String} (ht : t.sortOf E Γ = some s) :
    ∃ v, t.denote S ρ = some v ∧ S.domain s v := by
  cases t with
  | var i => exact hρ i s ht
  | const c => exact hS.1 c s ht

theorem typed_empty (S : Structure) : Valuation.Typed S [] [] := by
  intro i s h
  simp at h

theorem typed_cons {S : Structure} {Γ : List String} {ρ : Valuation S}
    (hρ : Valuation.Typed S Γ ρ) {s : String} {v : S.Carrier}
    (hv : S.domain s v) : Valuation.Typed S (s :: Γ) (v :: ρ) := by
  intro i r h
  cases i with
  | zero => simp only [List.getElem?_cons_zero, Option.some.injEq] at h
            subst r
            exact ⟨v, rfl, hv⟩
  | succ i => exact hρ i r h

end VE
