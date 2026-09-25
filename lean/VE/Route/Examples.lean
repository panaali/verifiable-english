import VE.Route.Background

/-! A genuine environment-extending layer, as evidence that the frozen `Layer`
contract is satisfiable beyond the identity: `copyLayer` adds a new unary
predicate `p` over sort `s` and the premise `∀x:s. (p(x) → q(x)) ∧ (q(x) → p(x))`
for an existing unary `q`. Restriction forgets `p`; expansion interprets `p` as
`q` on `s`, and is unique. W3's `Definitions` layer generalises this to
arbitrary bodies and arities. -/
namespace VE.Route.Examples
universe u

variable (E : VE.Environment) (p q s : String)

/-- `E` extended with `p : [s]`. -/
def extend : VE.Environment :=
  { E with predicates := fun r => if r = p then some [s] else E.predicates r }

def body : VE.Formula :=
  .all s (.and (.implies (.unary p (.var 0)) (.unary q (.var 0)))
    (.implies (.unary q (.var 0)) (.unary p (.var 0))))

def forget (S : VE.Structure.{u}) : VE.Structure.{u} :=
  { S with relation := fun r vs => r ≠ p ∧ S.relation r vs }

def interpret (S : VE.Structure.{u}) : VE.Structure.{u} :=
  { S with relation := fun r vs =>
      if r = p then ∃ v, vs = [v] ∧ S.domain s v ∧ S.relation q [v] else S.relation r vs }

variable {E p q s}

theorem tupleTyped_relation (S : VE.Structure.{u}) (R : String → List S.Carrier → Prop) (ss : List String)
    (vs : List S.Carrier) :
    VE.TupleTyped { S with relation := R } ss vs ↔ VE.TupleTyped S ss vs := by
  induction ss generalizing vs with
  | nil => cases vs <;> simp [VE.TupleTyped]
  | cons t ts ih => cases vs <;> simp [VE.TupleTyped, ih]

/-- Truth of a formula over `E` ignores the relation of an undeclared predicate. -/
theorem denote_forget (hp : E.predicates p = none) (S : VE.Structure.{u})
    (a : VE.Formula) (Γ : List String) (ρ : VE.Valuation S) (hw : a.WellFormed E Γ) :
    a.denote (forget p S) ρ ↔ a.denote S ρ := by
  induction a generalizing Γ ρ with
  | unary r t =>
    obtain ⟨_, hr, _⟩ := hw
    have : r ≠ p := fun h => by subst h; rw [hp] at hr; cases hr
    simp [VE.Formula.denote, forget, this, VE.Term.denote]
  | binary r t w =>
    obtain ⟨_, _, hr, _⟩ := hw
    have : r ≠ p := fun h => by subst h; rw [hp] at hr; cases hr
    simp [VE.Formula.denote, forget, this, VE.Term.denote]
  | eq t w => simp [VE.Formula.denote, forget, VE.Term.denote]
  | top | bottom => simp [VE.Formula.denote]
  | not a ih => simp only [VE.Formula.denote]; rw [ih Γ ρ hw]
  | and a b ia ib | or a b ia ib | implies a b ia ib =>
    simp only [VE.Formula.denote]; rw [ia Γ ρ hw.1, ib Γ ρ hw.2]
  | all t a ih | ex t a ih =>
    simp only [VE.Formula.denote]
    constructor
    · intro h
      first
      | exact fun v hv => (ih (t :: Γ) (v :: ρ) hw.2).mp (h v hv)
      | exact let ⟨v, hv, ha⟩ := h; ⟨v, hv, (ih (t :: Γ) (v :: ρ) hw.2).mp ha⟩
    · intro h
      first
      | exact fun v hv => (ih (t :: Γ) (v :: ρ) hw.2).mpr (h v hv)
      | exact let ⟨v, hv, ha⟩ := h; ⟨v, hv, (ih (t :: Γ) (v :: ρ) hw.2).mpr ha⟩

theorem body_holds_iff (S : VE.Structure.{u}) :
    (body p q s).denote S [] ↔ ∀ v, S.domain s v → (S.relation p [v] ↔ S.relation q [v]) := by
  simp only [body, VE.Formula.denote, VE.Term.denote]
  constructor
  · intro h v hv
    obtain ⟨h₁, h₂⟩ := h v hv
    exact ⟨fun hp' => by obtain ⟨_, hw, hq⟩ := h₁ ⟨v, rfl, hp'⟩; cases hw; exact hq,
      fun hq' => by obtain ⟨_, hw, hp'⟩ := h₂ ⟨v, rfl, hq'⟩; cases hw; exact hp'⟩
  · intro h v hv
    refine ⟨fun ⟨w, hw, hp'⟩ => ⟨w, hw, ?_⟩, fun ⟨w, hw, hq'⟩ => ⟨w, hw, ?_⟩⟩
    · cases hw; exact (h v hv).mp hp'
    · cases hw; exact (h v hv).mpr hq'

theorem wf_extend (hp : E.predicates p = none) (a : VE.Formula) (Γ : List String)
    (hw : a.WellFormed E Γ) : a.WellFormed (extend E p s) Γ := by
  induction a generalizing Γ with
  | unary r t =>
    obtain ⟨t', hr, ht⟩ := hw
    have : r ≠ p := fun h => by subst h; rw [hp] at hr; cases hr
    exact ⟨t', by simp [extend, this, hr], by simpa [extend, VE.Term.sortOf] using ht⟩
  | binary r t w =>
    obtain ⟨t₁, t₂, hr, ht, hw'⟩ := hw
    have : r ≠ p := fun h => by subst h; rw [hp] at hr; cases hr
    exact ⟨t₁, t₂, by simp [extend, this, hr], by simpa [extend, VE.Term.sortOf] using ht,
      by simpa [extend, VE.Term.sortOf] using hw'⟩
  | eq t w =>
    obtain ⟨t', ht, hw'⟩ := hw
    exact ⟨t', by simpa [extend, VE.Term.sortOf] using ht, by simpa [extend, VE.Term.sortOf] using hw'⟩
  | top | bottom => trivial
  | not a ih => exact ih Γ hw
  | and a b ia ib | or a b ia ib | implies a b ia ib => exact ⟨ia Γ hw.1, ib Γ hw.2⟩
  | all t a ih | ex t a ih => exact ⟨by simpa [extend] using hw.1, ih (t :: Γ) hw.2⟩

theorem body_wellFormed (hs : s ∈ E.sorts) (hq : E.predicates q = some [s]) (hpq : q ≠ p) :
    (body p q s).WellFormed (extend E p s) [] := by
  simp [body, VE.Formula.WellFormed, extend, hpq, hq, VE.Term.sortOf, hs]

theorem forget_admissible (S : VE.Structure.{u})
    (h : S.Admissible (extend E p s)) : (forget p S).Admissible E := by
  refine ⟨fun c t hc => h.1 c t (by simpa [extend] using hc), fun r vs hr => ?_⟩
  obtain ⟨hne, hr⟩ := hr
  obtain ⟨ss, hss, ht⟩ := h.2 r vs hr
  exact ⟨ss, by simpa [extend, hne] using hss, (tupleTyped_relation S _ ss vs).mpr ht⟩

theorem forget_interpret (hp : E.predicates p = none) (hpq : q ≠ p) (S₀ : VE.Structure.{u})
    (h : S₀.Admissible E) : forget p (interpret p q s S₀) = S₀ := by
  cases S₀ with
  | mk C d c rel =>
    simp only [forget, interpret, VE.Structure.mk.injEq, heq_eq_eq, true_and]
    funext r vs
    apply propext
    by_cases hr : r = p
    · subst hr
      simp only [ne_eq, not_true_eq_false, false_and, false_iff]
      intro hrel
      obtain ⟨ss, hss, _⟩ := h.2 r vs hrel
      simp [hp] at hss
    · simp [hr]

theorem interpret_admissible (S₀ : VE.Structure.{u})
    (h : S₀.Admissible E) : (interpret p q s S₀).Admissible (extend E p s) := by
  refine ⟨fun c t hc => h.1 c t (by simpa [extend] using hc), fun r vs hr => ?_⟩
  by_cases hrp : r = p
  · subst hrp
    simp only [interpret, if_true] at hr
    obtain ⟨v, rfl, hv, _⟩ := hr
    exact ⟨[s], by simp [extend], by simp [VE.TupleTyped, interpret, hv]⟩
  · simp only [interpret, hrp, if_false] at hr
    obtain ⟨ss, hss, ht⟩ := h.2 r vs hr
    exact ⟨ss, by simp [extend, hrp, hss], (tupleTyped_relation S₀ _ ss vs).mpr ht⟩

theorem copy_expands (hp : E.predicates p = none) (hpq : q ≠ p)
    (S₀ : VE.Structure.{u}) (h : S₀.Admissible E) :
    Unique fun S => forget p S = S₀ ∧ S.Admissible (extend E p s) ∧
      ∀ a ∈ [body p q s], a.denote S [] := by
  refine ⟨interpret p q s S₀, ⟨forget_interpret hp hpq S₀ h, interpret_admissible S₀ h, ?_⟩, ?_⟩
  · simp only [List.mem_singleton, forall_eq]
    apply (body_holds_iff _).mpr
    intro v hv
    simp only [interpret, hpq, if_false, if_true]
    exact ⟨fun ⟨_, hw, _, hq'⟩ => by cases hw; exact hq', fun hq' => ⟨v, rfl, hv, hq'⟩⟩
  · rintro S ⟨rfl, hS, hb⟩
    have hb' := (body_holds_iff S).mp (hb _ (List.mem_singleton_self _))
    cases S with
    | mk C d c rel =>
      simp only [interpret, forget, VE.Structure.mk.injEq, heq_eq_eq, true_and]
      funext r vs
      apply propext
      by_cases hr : r = p
      · subst hr
        simp only [if_true, ne_eq, hpq, not_false_eq_true, true_and]
        constructor
        · intro hrel
          obtain ⟨ss, hss, ht⟩ := hS.2 r vs hrel
          simp only [extend, if_true, Option.some.injEq] at hss
          subst hss
          match vs, ht with
          | [v], ⟨hv, _⟩ => exact ⟨v, rfl, hv, (hb' v hv).mp hrel⟩
        · rintro ⟨v, rfl, hv, hqv⟩
          exact (hb' v hv).mpr hqv
      · simp [hr]

variable (E p q s)

/-- The copy layer: a genuine vocabulary-extending instance of `Layer`. -/
def copyLayer (hs : s ∈ E.sorts) (hp : E.predicates p = none) (hq : E.predicates q = some [s])
    (hpq : q ≠ p) : Layer fol.{u} Unit where
  E_in := E
  E_out := extend E p s
  extends_env a h := wf_extend hp a [] h
  premises _ := [body p q s]
  premises_wellFormed _ a ha := by
    rw [List.mem_singleton.mp ha]
    exact body_wellFormed hs hq hpq
  Admissible_in S := S.Admissible E
  Admissible_out S := S.Admissible (extend E p s)
  admissible_out _ h := h
  restrict := forget p
  restrict_admissible S h := forget_admissible S h
  restrict_holds S a _ ha := denote_forget hp S a [] [] ha
  Intended _ S := ∀ v, S.domain s v → (S.relation p [v] ↔ S.relation q [v])
  faithful _ S _ := by
    simp only [List.mem_singleton, forall_eq]
    exact body_holds_iff S
  expands _ S₀ h := copy_expands hp hpq S₀ h

/-- Two copy layers compose: `p := q`, then `r := p`, innermost first. -/
def twoCopies (t : String) (hs : s ∈ E.sorts) (hp : E.predicates p = none)
    (hq : E.predicates q = some [s]) (hpq : q ≠ p) (ht : (extend E p s).predicates t = none)
    (htp : p ≠ t) : Layer fol.{u} Unit :=
  Layer.comp (copyLayer E p q s hs hp hq hpq)
    (copyLayer (extend E p s) t p s (by simpa [extend] using hs) ht (by simp [extend]) htp) rfl
    (fun _ => Iff.rfl)

end VE.Route.Examples
