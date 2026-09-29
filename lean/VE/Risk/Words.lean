import VE.Risk.Background

/-! The two defined words (docs/spec/risk.md 4.5 and 7.2): typing of their
bodies, `risk_inline_faithful`, and the properties of `less_worst` over every
structure satisfying the slot premises: it is irreflexive and transitive
(`lessWorst_strict`), and every chooser with an alternative has one that no
other alternative beats (`precaution_has_maximal`).

The second rests on profiles: whether `a′` beats `a` depends only on the set of
classes each might reach and on whether each might reach an unclassified harm
(`lessWorst_cong`). A profile is a list of `n` Booleans and a flag, so there are
finitely many, and a strict order whose left argument only matters through
such a profile has a minimal element on every nonempty set (`exists_minimal`). -/
namespace VE.Risk
open VE.Norms
open VE.Alternatives (AltDoc inlineTree Avail profileDef)
universe u

/-! ## Typing of the bodies -/

section Bodies
variable {R : RiskDoc} (hv : RiskValid R)
include hv

theorem harm_mem : R.alt.harm ∈ (riskEnv R).sorts :=
  (VE.Alternatives.altValid_of_wellFormed _ hv.alt).harmSort

theorem action_mem : R.alt.action ∈ (riskEnv R).sorts :=
  (VE.Alternatives.altValid_of_wellFormed _ hv.alt).actionSort

theorem chooser_mem : R.alt.chooser ∈ (riskEnv R).sorts :=
  (VE.Alternatives.altValid_of_wellFormed _ hv.alt).chooserSort

omit hv in
theorem orWorseF_wellFormed : (orWorseF R).WellFormed (riskEnv R) [R.sev, R.alt.harm] := by
  simp [orWorseF, VE.Formula.WellFormed, VE.Term.sortOf, riskEnv_class, riskEnv_ms, riskEnv_sev]

theorem lessWorstF_wellFormed : (lessWorstF R).WellFormed (riskEnv R) [R.alt.action, R.alt.action] := by
  simp [lessWorstF, VE.Formula.WellFormed, VE.Term.sortOf, riskEnv_class, riskEnv_ms, riskEnv_sev, riskEnv_might,
    harm_mem hv]

end Bodies

theorem riskWordDef_some {R : RiskDoc} {p : String} {ss : List String} {F : VE.Formula}
    (h : riskWordDef R p = some (ss, F)) :
    (ss = [R.alt.harm, R.sev] ∧ F = orWorseF R) ∨ (ss = [R.alt.action, R.alt.action] ∧ F = lessWorstF R) := by
  unfold riskWordDef at h
  split at h
  · cases h; exact Or.inl ⟨rfl, rfl⟩
  split at h
  · cases h; exact Or.inr ⟨rfl, rfl⟩
  · cases h

theorem riskWordDef_length {R : RiskDoc} {p : String} {ss : List String} {F : VE.Formula}
    (h : riskWordDef R p = some (ss, F)) : ss.length = 2 := by
  rcases riskWordDef_some h with ⟨rfl, _⟩ | ⟨rfl, _⟩ <;> rfl

theorem riskBody_wellFormed {R : RiskDoc} (hv : RiskValid R) {p : String} {ss : List String} {F : VE.Formula}
    (h : riskWordDef R p = some (ss, F)) : F.WellFormed (riskEnv R) ss.reverse := by
  rcases riskWordDef_some h with ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩
  · exact orWorseF_wellFormed
  · exact lessWorstF_wellFormed hv

theorem riskExtEnv_word {R : RiskDoc} {p : String} {ss : List String} {F : VE.Formula}
    (h : riskWordDef R p = some (ss, F)) : (riskExtEnv R).predicates p = some ss := by
  simp [riskExtEnv, h]

theorem sortOf_riskExtEnv (R : RiskDoc) (Γ : List String) (t : VE.Term) :
    t.sortOf (riskExtEnv R) Γ = t.sortOf (riskEnv R) Γ := by
  cases t <;> rfl

/-! ## Inlining (4.5) -/

theorem term_denote_withRisk (R : RiskDoc) (S : VE.Structure.{u}) (ρ : VE.Valuation S) (t : VE.Term) :
    t.denote (withRiskDefinitions R S) ρ = t.denote S ρ := by
  cases t <;> rfl

theorem withRisk_relation_some {R : RiskDoc} {S : VE.Structure.{u}} {p : String} {ss : List String}
    {F : VE.Formula} (hd : riskWordDef R p = some (ss, F)) (vs : List S.Carrier) :
    (withRiskDefinitions R S).relation p vs ↔ VE.TupleTyped S ss vs ∧ F.denote S (tupleVal vs) := by
  simp [withRiskDefinitions, hd]

/-- 4.5: inlining the two words is faithful on every structure admissible for `E_risk` (admissibility is
part of the claim, as in alt's `inline_faithful`). -/
theorem risk_inline_faithful (R : RiskDoc) (h : WellFormedRisk R = true) (φ : VE.Formula) (Γ : List String)
    (hφ : φ.WellFormed (riskExtEnv R) Γ) (S : VE.Structure.{u}) (hS : S.Admissible (riskEnv R))
    (ρ : VE.Valuation S) (hρ : VE.Valuation.Typed S Γ ρ) :
    (riskInline R φ).denote S ρ ↔ φ.denote (withRiskDefinitions R S) ρ := by
  have hv := riskValid_of_wellFormed R h
  induction φ generalizing Γ ρ with
  | top | bottom => exact Iff.rfl
  | unary p t =>
    obtain ⟨s, hp, _⟩ := hφ
    show (VE.Formula.unary p t).denote S ρ ↔ _
    cases hd : riskWordDef R p with
    | none =>
      simp only [VE.Formula.denote, term_denote_withRisk]
      simp [withRiskDefinitions, hd]
    | some d =>
      obtain ⟨ss, F⟩ := d
      rw [riskExtEnv_word hd] at hp
      cases hp
      have := riskWordDef_length hd
      simp at this
  | binary p t u =>
    obtain ⟨s, r, hp, ht, hu⟩ := hφ
    unfold riskInline
    cases hd : riskWordDef R p with
    | none =>
      simp only [VE.Formula.denote, term_denote_withRisk]
      simp [withRiskDefinitions, hd]
    | some d =>
      obtain ⟨ss, F⟩ := d
      rw [riskExtEnv_word hd] at hp
      cases hp
      rw [sortOf_riskExtEnv] at ht hu
      obtain ⟨v, hvt, hvd⟩ := VE.term_defined hS hρ ht
      obtain ⟨w, hwu, hwd⟩ := VE.term_defined hS hρ hu
      have hden : Denotes S ρ [u, t] [w, v] := by
        refine ⟨rfl, fun i h₁ _ => ?_⟩
        match i, h₁ with
        | 0, _ => exact hwu
        | 1, _ => exact hvt
      simp only
      rw [inst_denote S (riskEnv R) F [r, s] [u, t] ρ [w, v] (riskBody_wellFormed hv hd) rfl hden]
      simp only [VE.Formula.denote, term_denote_withRisk]
      constructor
      · intro hF
        exact ⟨v, w, hvt, hwu, (withRisk_relation_some hd [v, w]).mpr ⟨⟨hvd, hwd, trivial⟩, hF⟩⟩
      · rintro ⟨v', w', hv', hw', hr⟩
        rw [hvt] at hv'; rw [hwu] at hw'
        cases hv'; cases hw'
        exact ((withRisk_relation_some hd [v, w]).mp hr).2
  | eq t u =>
    simp only [riskInline, VE.Formula.denote, term_denote_withRisk]
    exact Iff.rfl
  | not a ih => exact not_congr (ih Γ hφ ρ hρ)
  | and a b ia ib => exact and_congr (ia Γ hφ.1 ρ hρ) (ib Γ hφ.2 ρ hρ)
  | or a b ia ib => exact or_congr (ia Γ hφ.1 ρ hρ) (ib Γ hφ.2 ρ hρ)
  | implies a b ia ib => exact imp_congr (ia Γ hφ.1 ρ hρ) (ib Γ hφ.2 ρ hρ)
  | all s a ih | ex s a ih =>
    simp only [riskInline, VE.Formula.denote] at ih ⊢
    first
    | exact forall_congr' fun v => imp_congr_right fun hd => ih (s :: Γ) hφ.2 (v :: ρ) (VE.typed_cons hρ hd)
    | exact exists_congr fun v => and_congr_right fun hd => ih (s :: Γ) hφ.2 (v :: ρ) (VE.typed_cons hρ hd)

/-! ## `less_worst` over structures satisfying the slot premises -/

def LessWorst (R : RiskDoc) (B : VE.Structure.{u}) (a' a : B.Carrier) : Prop :=
  (lessWorstF R).denote B (tupleVal [a', a])

theorem lessWorst_iff (R : RiskDoc) (B : VE.Structure.{u}) (a' a : B.Carrier) :
    LessWorst R B a' a ↔ ∃ h, B.domain R.alt.harm h ∧ ∃ s, B.domain R.sev s ∧
      B.relation mightName [a, h] ∧ B.relation classPred [h, s] ∧
      ∀ h', B.domain R.alt.harm h' → B.relation mightName [a', h'] →
        ∃ s', B.domain R.sev s' ∧ B.relation classPred [h', s'] ∧ B.relation moreSeverePred [s, s'] := by
  simp [LessWorst, lessWorstF, tupleVal, VE.Formula.denote, VE.Term.denote]


/-- 4.5: `less_worst` is irreflexive and transitive under the slot premises (functionality of `class`
and the order table). -/
theorem lessWorst_strict (R : RiskDoc) (h : WellFormedRisk R = true) (B : VE.Structure.{u})
    (hB : BaseAdmissibleRisk R B) :
    (∀ a, ¬ LessWorst R B a a) ∧
    (∀ a b c, LessWorst R B a b → LessWorst R B b c → LessWorst R B a c) := by
  have hv := riskValid_of_wellFormed R h
  -- `more_severe` is irreflexive and transitive on the severity domain.
  have ms_irrefl : ∀ s, B.domain R.sev s → ¬ B.relation moreSeverePred [s, s] := by
    intro s hs hr
    obtain ⟨c, hc, hx⟩ := sev_closed hB s hs
    exact hv.irrefl _ ((order_of hB hc hc hx hx).mp hr) rfl
  have ms_trans : ∀ s1 s2 s3, B.domain R.sev s1 → B.domain R.sev s2 → B.domain R.sev s3 →
      B.relation moreSeverePred [s1, s2] → B.relation moreSeverePred [s2, s3] →
      B.relation moreSeverePred [s1, s3] := by
    intro s1 s2 s3 h1 h2 h3 r1 r2
    obtain ⟨c1, hc1, hx1⟩ := sev_closed hB s1 h1
    obtain ⟨c2, hc2, hx2⟩ := sev_closed hB s2 h2
    obtain ⟨c3, hc3, hx3⟩ := sev_closed hB s3 h3
    exact (order_of hB hc1 hc3 hx1 hx3).mpr
      (hv.trans _ ((order_of hB hc1 hc2 hx1 hx2).mp r1) _ ((order_of hB hc2 hc3 hx2 hx3).mp r2) rfl)
  refine ⟨fun a hl => ?_, fun a b c h1 h2 => ?_⟩
  · obtain ⟨x, hx, s, hs, hm, hc, hall⟩ := (lessWorst_iff R B a a).mp hl
    obtain ⟨s', hs', hc', hr⟩ := hall x hx hm
    have := class_functional_of hB x s s' hx hs hs' hc hc'
    subst this
    exact ms_irrefl s hs hr
  · obtain ⟨x1, hx1, s1, hs1, hm1, hc1, hall1⟩ := (lessWorst_iff R B a b).mp h1
    obtain ⟨x2, hx2, s2, hs2, hm2, hc2, hall2⟩ := (lessWorst_iff R B b c).mp h2
    obtain ⟨s3, hs3, hc3, hr3⟩ := hall2 x1 hx1 hm1
    have := class_functional_of hB x1 s1 s3 hx1 hs1 hs3 hc1 hc3
    subst this
    refine (lessWorst_iff R B a c).mpr ⟨x2, hx2, s2, hs2, hm2, hc2, fun h' hh' hm' => ?_⟩
    obtain ⟨s', hs', hc', hr'⟩ := hall1 h' hh' hm'
    exact ⟨s', hs', hc', ms_trans s2 s1 s' hs2 hs1 hs' hr3 hr'⟩

/-! ## Profiles and a minimal alternative -/

/-- Every list of Booleans of length `n`. -/
def allBools : Nat → List (List Bool)
  | 0 => [[]]
  | n + 1 => (allBools n).flatMap fun l => [false :: l, true :: l]

theorem mem_allBools : ∀ l : List Bool, l ∈ allBools l.length
  | [] => by simp [allBools]
  | b :: l => by
    simp only [allBools, List.length_cons, List.mem_flatMap]
    exact ⟨l, mem_allBools l, by cases b <;> simp⟩

/-- A strict order on `α` whose left argument matters only through a profile with values in a finite list
has a minimal element on every nonempty set. -/
theorem exists_minimal {α : Type u} {β : Type} [DecidableEq β] (lt : α → α → Prop)
    (irrefl : ∀ a, ¬ lt a a) (trans : ∀ a b c, lt a b → lt b c → lt a c) (prof : α → β)
    (cong : ∀ x y z, prof x = prof y → lt x z → lt y z) :
    ∀ (n : Nat) (L : List β) (X : α → Prop), L.length ≤ n → (∀ x, X x → prof x ∈ L) → (∃ x, X x) →
      ∃ m, X m ∧ ¬ ∃ y, X y ∧ lt y m
  | 0, L, X, hl, hL, ⟨x, hx⟩ => by
    have := hL x hx
    rw [List.length_eq_zero_iff.mp (Nat.le_zero.mp hl)] at this
    cases this
  | n + 1, L, X, hl, hL, ⟨a, ha⟩ => by
    by_cases hmin : ∃ y, X y ∧ lt y a
    · let X' : α → Prop := fun x => X x ∧ lt x a
      have hL' : ∀ x, X' x → prof x ∈ L.erase (prof a) := by
        intro x ⟨hx, hlt⟩
        have hne : prof x ≠ prof a := fun he => irrefl a (cong x a a he hlt)
        exact (List.mem_erase_of_ne hne).mpr (hL x hx)
      have hlen : (L.erase (prof a)).length ≤ n := by
        rw [List.length_erase_of_mem (hL a ha)]
        omega
      obtain ⟨m, ⟨hm, hma⟩, hno⟩ := exists_minimal lt irrefl trans prof cong n (L.erase (prof a)) X' hlen hL' hmin
      refine ⟨m, hm, fun ⟨y, hy, hym⟩ => hno ⟨y, ⟨hy, trans y m a hym hma⟩, hym⟩⟩
    · exact ⟨a, ha, hmin⟩

section Profile
open Classical

/-- The profile of an element (4.5): for each class, whether it might reach a harm of that class, and
whether it might reach an unclassified harm. -/
noncomputable def profile (R : RiskDoc) (B : VE.Structure.{u}) (a : B.Carrier) : List Bool × Bool :=
  (R.classes.map fun c => decide (∃ h x, B.domain R.alt.harm h ∧ B.constant c = some x ∧
      B.relation mightName [a, h] ∧ B.relation classPred [h, x]),
    decide (∃ h, B.domain R.alt.harm h ∧ B.relation mightName [a, h] ∧
      ¬ ∃ s, B.domain R.sev s ∧ B.relation classPred [h, s]))

theorem profile_mem (R : RiskDoc) (B : VE.Structure.{u}) (a : B.Carrier) :
    profile R B a ∈ (allBools R.classes.length).flatMap (fun l => [(l, false), (l, true)]) := by
  apply List.mem_flatMap.mpr
  refine ⟨(profile R B a).1, ?_, ?_⟩
  · have := mem_allBools (profile R B a).1
    simpa [profile] using this
  · generalize profile R B a = p
    obtain ⟨l, b⟩ := p
    cases b <;> simp

theorem map_eq_pointwise {γ δ : Type _} {f g : γ → δ} : ∀ {l : List γ}, l.map f = l.map g → ∀ c ∈ l, f c = g c
  | [], _, _, hc => by cases hc
  | x :: l, h, c, hc => by
    simp only [List.map_cons, List.cons.injEq] at h
    rcases List.mem_cons.mp hc with rfl | hc
    · exact h.1
    · exact map_eq_pointwise h.2 c hc

/-- 4.5: `less_worst` depends on its left argument only through the profile. -/
theorem lessWorst_cong {R : RiskDoc} {B : VE.Structure.{u}} (hB : BaseAdmissibleRisk R B) (x y z : B.Carrier)
    (hp : profile R B x = profile R B y) (hl : LessWorst R B x z) : LessWorst R B y z := by
  obtain ⟨h, hh, s, hs, hm, hc, hall⟩ := (lessWorst_iff R B x z).mp hl
  refine (lessWorst_iff R B y z).mpr ⟨h, hh, s, hs, hm, hc, fun h' hh' hm' => ?_⟩
  simp only [profile, Prod.mk.injEq] at hp
  obtain ⟨hp1, hp2⟩ := hp
  by_cases hcl : ∃ s'', B.domain R.sev s'' ∧ B.relation classPred [h', s'']
  · obtain ⟨s'', hs'', hc''⟩ := hcl
    obtain ⟨c, hcm, hcx⟩ := sev_closed hB s'' hs''
    have hbit := map_eq_pointwise hp1 c hcm
    have hy : decide (∃ h x, B.domain R.alt.harm h ∧ B.constant c = some x ∧
        B.relation mightName [y, h] ∧ B.relation classPred [h, x]) = true :=
      decide_eq_true ⟨h', s'', hh', hcx, hm', hc''⟩
    rw [← hbit] at hy
    obtain ⟨h2, x2, hh2, hcx2, hm2, hc2⟩ := of_decide_eq_true hy
    rw [hcx] at hcx2
    cases hcx2
    obtain ⟨s', hs', hc', hr⟩ := hall h2 hh2 hm2
    have := class_functional_of hB h2 s'' s' hh2 hs'' hs' hc2 hc'
    subst this
    exact ⟨s'', hs'', hc'', hr⟩
  · have hy : decide (∃ h, B.domain R.alt.harm h ∧ B.relation mightName [y, h] ∧
        ¬ ∃ s, B.domain R.sev s ∧ B.relation classPred [h, s]) = true := decide_eq_true ⟨h', hh', hm', hcl⟩
    rw [← hp2] at hy
    obtain ⟨h2, hh2, hm2, hno⟩ := of_decide_eq_true hy
    obtain ⟨s', hs', hc', _⟩ := hall h2 hh2 hm2
    exact absurd ⟨s', hs', hc'⟩ hno

end Profile

/-- 4.5: some alternative of every chooser with an alternative is beaten by none. `less_worst` depends
only on profiles (the classes reached plus an unclassified flag), and there are finitely many. -/
theorem precaution_has_maximal (R : RiskDoc) (h : WellFormedRisk R = true) (B : VE.Structure.{u})
    (hB : BaseAdmissibleRisk R B) (r : B.Carrier) (hne : ∃ a, Avail (toAlt R) B a r) :
    ∃ a, Avail (toAlt R) B a r ∧ ¬ ∃ a', Avail (toAlt R) B a' r ∧ LessWorst R B a' a := by
  obtain ⟨irr, tr⟩ := lessWorst_strict R h B hB
  let L := (allBools R.classes.length).flatMap (fun l => [(l, false), (l, true)])
  exact exists_minimal (LessWorst R B) irr tr (profile R B) (lessWorst_cong hB) L.length L
    (fun a => Avail (toAlt R) B a r) (Nat.le_refl _) (fun a _ => profile_mem R B a) hne

end VE.Risk
