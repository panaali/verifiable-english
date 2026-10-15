import VE.Ask.Basic

/-! What a lead and a reason claim, proved from the rows' own `Holds` (docs/spec/question-answering.md 5.2; plan 4.1,
4.2, Q2.1): `lead_sound`, `reason_sound`, `reason_exact`, `split_counter`, `splitOk_sound`, and the agreement with
RD-3's per-choice result and fold, `lead_agrees` and `all_yes_iff_fold`. -/

namespace VE.Ask
open VE.Readings VE.NormDefaults
open VE.Norms (Sat restrictAll DocumentExpansion envAt size)
universe u

/-! ## The leads, one by one -/

theorem lead_yes {r : Row} (h : r.lead = .yes) :
    r.conflict = .free ∧ r.query = .proved ∧ r.premise = .model := by
  unfold Row.lead at h
  by_cases hc : r.conflict = .free <;> by_cases hq : r.query = .proved <;> by_cases hp : r.premise = .model <;>
    by_cases hn : r.negation = .proved <;> by_cases hr : r.query = .refuted <;> cases hs : r.split <;>
    simp_all

theorem lead_no {r : Row} (h : r.lead = .no) :
    r.conflict = .free ∧ r.query ≠ .proved ∧ r.negation = .proved ∧ r.premise = .model := by
  unfold Row.lead at h
  by_cases hc : r.conflict = .free <;> by_cases hq : r.query = .proved <;> by_cases hp : r.premise = .model <;>
    by_cases hn : r.negation = .proved <;> by_cases hr : r.query = .refuted <;> cases hs : r.split <;>
    simp_all

theorem lead_notSettled {r : Row} (h : r.lead = .notSettled) :
    r.conflict = .free ∧ r.query ≠ .proved ∧ r.negation ≠ .proved ∧ r.split = true := by
  unfold Row.lead at h
  by_cases hc : r.conflict = .free <;> by_cases hq : r.query = .proved <;> by_cases hp : r.premise = .model <;>
    by_cases hn : r.negation = .proved <;> by_cases hr : r.query = .refuted <;> cases hs : r.split <;>
    simp_all

theorem lead_notNecessarily {r : Row} (h : r.lead = .notNecessarily) :
    r.conflict = .free ∧ r.query = .refuted ∧ r.negation ≠ .proved ∧ r.split = false := by
  unfold Row.lead at h
  by_cases hc : r.conflict = .free <;> by_cases hq : r.query = .proved <;> by_cases hp : r.premise = .model <;>
    by_cases hn : r.negation = .proved <;> by_cases hr : r.query = .refuted <;> cases hs : r.split <;>
    simp_all

/-- An unknown lead: the conflict row is not free, or a proof without a premise model, or no evidence. -/
theorem lead_unknown {r : Row} (h : r.lead = .unknown) :
    r.conflict ≠ .free ∨ ((r.query = .proved ∨ r.negation = .proved) ∧ r.premise ≠ .model) ∨
      (r.query ≠ .proved ∧ r.negation ≠ .proved ∧ r.split = false ∧ r.query ≠ .refuted) := by
  unfold Row.lead at h
  by_cases hc : r.conflict = .free <;> by_cases hq : r.query = .proved <;> by_cases hp : r.premise = .model <;>
    by_cases hn : r.negation = .proved <;> by_cases hr : r.query = .refuted <;> cases hs : r.split <;>
    simp_all

theorem lead_sound : ∀ (N : NDoc) (ψ : VE.Formula) (r : Row), RowOk.{u} N ψ r → LeadHolds.{u} N ψ r := by
  intro N ψ r h
  obtain ⟨hc, hp, hq, hn, hs⟩ := h
  unfold LeadHolds
  cases hl : r.lead with
  | yes =>
    obtain ⟨h1, h2, h3⟩ := lead_yes hl
    rw [h1] at hc; rw [h2] at hq; rw [h3] at hp
    obtain ⟨_, he⟩ := hq
    rw [List.append_nil] at he
    exact ⟨hc, hp, he⟩
  | no =>
    obtain ⟨h1, _, h3, h4⟩ := lead_no hl
    rw [h1] at hc; rw [h3] at hn; rw [h4] at hp
    obtain ⟨_, he⟩ := hn
    rw [List.append_nil] at he
    exact ⟨hc, hp, he⟩
  | notSettled =>
    obtain ⟨h1, _, _, h4⟩ := lead_notSettled hl
    rw [h1] at hc
    exact ⟨hc, hs h4⟩
  | notNecessarily =>
    obtain ⟨h1, h2, _, _⟩ := lead_notNecessarily hl
    rw [h1] at hc; rw [h2] at hq
    obtain ⟨S, h1, h2, h3, h4⟩ := hq
    rw [List.append_nil] at h3
    exact ⟨hc, S, h1, h2, h3, h4⟩
  | unknown => trivial

/-! ## Reasons -/

theorem reason_exact : ∀ r : Row, r.lead = .unknown ↔ r.reason.isSome := by
  intro r
  unfold Row.reason
  by_cases h : r.lead = .unknown
  · simp only [h, bne_self_eq_false, Bool.false_eq_true, ↓reduceIte, true_iff]
    repeat' split
    all_goals rfl
  · simp [h]

/-- The reason a row names, by the fields it reads. -/
theorem reason_fields {r : Row} {x : Reason} (h : r.reason = some x) :
    (x = .conflict → r.conflict = .conflict) ∧
    (x = .inconsistent → r.conflict = .free ∧ r.premise = .inconsistent) ∧
    (x = .unchecked → r.conflict = .free ∧ (r.query = .proved ∨ r.negation = .proved)) := by
  unfold Row.reason Row.lead at h
  by_cases hc : r.conflict = .free <;> by_cases hk : r.conflict = .conflict <;>
    by_cases hq : r.query = .proved <;> by_cases hp : r.premise = .model <;>
    by_cases hi : r.premise = .inconsistent <;> by_cases hn : r.negation = .proved <;>
    by_cases hr : r.query = .refuted <;> cases hs : r.split <;> cases x <;> simp_all

theorem reason_sound : ∀ (N : NDoc) (ψ : VE.Formula) (r : Row) (x : Reason),
    RowOk.{u} N ψ r → r.reason = some x → ReasonHolds.{u} N ψ r x := by
  intro N ψ r x h hx
  obtain ⟨hc, hp, hq, hn, _⟩ := h
  obtain ⟨f1, f2, f3⟩ := reason_fields hx
  cases x with
  | conflict =>
    have h1 := f1 rfl
    rw [h1] at hc
    exact hc
  | inconsistent =>
    obtain ⟨_, h2⟩ := f2 rfl
    rw [h2] at hp
    exact hp
  | unchecked =>
    obtain ⟨h1, h2⟩ := f3 rfl
    rw [h1] at hc
    rcases h2 with h2 | h2
    · rw [h2] at hq
      obtain ⟨_, he⟩ := hq
      rw [List.append_nil] at he
      exact ⟨hc, Or.inl he⟩
    · rw [h2] at hn
      obtain ⟨_, he⟩ := hn
      rw [List.append_nil] at he
      exact ⟨hc, Or.inr he⟩
  | conflictUnchecked => trivial
  | noResult => trivial
  | tooMany => trivial

/-! ## The split -/

theorem split_counter : ∀ (U : UDoc) (Γ : List VE.Formula) (ψ : VE.Formula), SplitU U Γ ψ → CounterU U Γ ψ := by
  intro U Γ ψ h
  obtain ⟨B, F₁, F₂, S₁, S₂, _, e₂, _, a₂, _, x₂, _, s₂, _, n₂⟩ := h
  exact ⟨S₂, by rw [e₂]; exact a₂, by rw [e₂]; exact x₂, s₂, n₂⟩

/-- RD-3's `expansion_of_modelCheck` with the base equation its proof establishes: the expansion's base is exactly
    the checked model with its filling. RD-3's statement is not edited (plan Q2.1). -/
theorem expansion_of_modelCheck_base (U : UDoc) (h : WellFormedU U = true) (M : VE.FiniteModel VE.Bridge.Entity)
    (valid : M.Valid (envAt U.D 0)) (F : FiniteFill U VE.Bridge.Entity) (Γ : List VE.Formula) (φ : VE.Formula)
    (hΓ : ∀ a ∈ Γ, a.WellFormed (envAt (fill U) (size (fill U))) [])
    (hφ : φ.WellFormed (envAt (fill U) (size (fill U))) [])
    (hm : (modelCheckU U M F Γ φ).1 = true) (hl : VE.Readings.Wire.localFree U M F = true) :
    ∃ S : VE.Structure.{0}, restrictAll (fill U).T S = withFill U M.asStructure (finFill M F) ∧
      BaseAdmissibleU U (withFill U M.asStructure (finFill M F)) ∧
      DocumentExpansion (fill U) (withFill U M.asStructure (finFill M F)) S ∧ Sat S Γ ∧
      (φ.denote S [] ↔ (modelCheckU U M F Γ φ).2 = true) := by
  obtain ⟨hB, hΓs, hφs⟩ := modelCheckU_sound U h M valid F Γ φ hm
  have hcf := VE.Readings.Wire.conflictFree_of_localFree U h M F hl
  have hE := canonTyped_expansion h hB hcf
  have hr := hE.1
  have hv := VE.Norms.valid_of_wellFormed _ (fill_wellFormed U h)
  obtain ⟨_, hpa⟩ := (VE.Norms.documentExpansion_iff hv _ _ hB.1).mp hE
  obtain ⟨hA, _, hM, _⟩ := (VE.Norms.prefix_char hv _ (Nat.le_refl _) _).mp hpa
  have hden : ∀ ψ : VE.Formula, ψ.denote (restrictAll (fill U).T (canonTyped (fill U)
      (withFill U M.asStructure (finFill M F)))) [] ↔
      ψ.denote (withFill U M.asStructure (finFill M F)) [] := fun ψ => by
    rw [hr]
  have key : ∀ a : VE.Formula, a.WellFormed (envAt (fill U) (size (fill U))) [] →
      ((VE.Norms.subst (fill U).T (size (fill U)) a).denote (withFill U M.asStructure (finFill M F)) [] ↔
        a.denote (canonTyped (fill U) (withFill U M.asStructure (finFill M F))) []) := fun a hw =>
    (hden _).symm.trans (VE.Norms.subst_restrict_denote hv _ _ hA.1 (VE.Norms.agreesBelow_of_meanings hM) a [] hw []
      (VE.typed_empty _))
  exact ⟨_, hr, hB, hE, fun a ha => (key a (hΓ a ha)).mp (hΓs a ha), (key φ hφ).symm.trans hφs⟩

/-- A checked filled model as `ndModelOk` checks it, with its base equation. -/
theorem ndModelOk_base {N : NDoc} {c : Choice} (e : VE.Readings.Wire.NDEvidence N c) (ψ : VE.Formula)
    (m : VE.Readings.Wire.FilledModel (choiceU N c)) (v : Bool)
    (h : VE.Readings.Wire.ndModelOk N c [] ψ m v = true) :
    ∃ S : VE.Structure.{0},
      restrictAll (fill (choiceU N c)).T S = withFill (choiceU N c) m.M.asStructure (finFill m.M m.F) ∧
      BaseAdmissibleU (choiceU N c) (withFill (choiceU N c) m.M.asStructure (finFill m.M m.F)) ∧
      DocumentExpansion (fill (choiceU N c)) (withFill (choiceU N c) m.M.asStructure (finFill m.M m.F)) S ∧
      Sat S (choiceDoc N.D c).2 ∧ (ψ.denote S [] ↔ v = true) := by
  simp only [VE.Readings.Wire.ndModelOk, Bool.and_eq_true, beq_iff_eq, List.all_eq_true] at h
  obtain ⟨⟨⟨hw, hm⟩, hv⟩, hl⟩ := h
  have hw' : ∀ a ∈ ((choiceDoc N.D c).2 ++ []) ++ [ψ], a.WellFormed (VE.Readings.Wire.fullEnv N c) [] :=
    fun a ha => (VE.check_iff_wellFormed _ _ a).mp (hw a ha)
  obtain ⟨S, h0, h1, h2, h3, h4⟩ := expansion_of_modelCheck_base _ e.wfc m.M m.valid m.F _ ψ
    (fun a ha => hw' a (List.mem_append_left _ ha)) (hw' ψ (List.mem_append_right _ List.mem_cons_self)) hm hl
  rw [List.append_nil] at h3
  exact ⟨S, h0, h1, h2, h3, by rw [h4, hv]⟩

/-- The split check: one checked base model, two checked fillings with opposite values of ψ. -/
theorem splitOk_sound : ∀ (N : NDoc) (c : Choice) (e : VE.Readings.Wire.NDEvidence N c) (ψ : VE.Formula)
    (m₁ m₂ : VE.Readings.Wire.FilledModel (choiceU N c)), m₁.M = m₂.M →
    VE.Readings.Wire.ndModelOk N c [] ψ m₁ true = true → VE.Readings.Wire.ndModelOk N c [] ψ m₂ false = true →
    SplitU (choiceU N c) (choiceDoc N.D c).2 ψ := by
  intro N c e ψ m₁ m₂ hM h₁ h₂
  obtain ⟨S₁, e₁, a₁, x₁, s₁, d₁⟩ := ndModelOk_base e ψ m₁ true h₁
  obtain ⟨S₂, e₂, a₂, x₂, s₂, d₂⟩ := ndModelOk_base e ψ m₂ false h₂
  obtain ⟨M₁, v₁, F₁⟩ := m₁
  obtain ⟨M₂, v₂, F₂⟩ := m₂
  simp only at hM e₁ a₁ x₁ d₁ e₂ a₂ x₂ d₂
  subst hM
  exact ⟨M₁.asStructure, finFill M₁ F₁, finFill M₁ F₂, S₁, S₂, e₁, e₂, a₁, a₂, x₁, x₂, s₁, s₂, by simpa using d₁,
    by simpa using d₂⟩

/-! ## Agreement with RD-3's per-choice result and fold -/

theorem lead_agrees : ∀ r : Row,
    (r.lead = .yes → r.query = .proved) ∧
    (r.lead = .no ∨ r.lead = .notSettled ∨ r.lead = .notNecessarily → r.query ≠ .proved) := by
  intro r
  refine ⟨fun h => (lead_yes h).2.1, ?_⟩
  rintro (h | h | h)
  · exact (lead_no h).2.1
  · exact (lead_notSettled h).2.1
  · intro hq
    have := (lead_notNecessarily h).2.1
    rw [hq] at this
    cases this

theorem foldConflict_of_free {rs : List (Choice × ChoiceResult)} (hne : rs ≠ []) (h : ∀ x ∈ rs, x.2 = .free) :
    foldConflict rs = .free := by
  unfold foldConflict
  have h1 : rs.any (·.2 == .conflict) = false := by
    rw [List.any_eq_false]
    intro x hx
    simp [h x hx]
  have h2 : rs.all (·.2 == .free) = true := by
    rw [List.all_eq_true]
    intro x hx
    simp [h x hx]
  have h3 : rs.isEmpty = false := by simpa using hne
  simp [h1, h2, h3]

theorem all_yes_iff_fold : ∀ rs : List Row, rs ≠ [] → (∀ r ∈ rs, r.premise = .model) →
    ((∀ r ∈ rs, r.lead = .yes) ↔ foldEntailment (conflictRows rs) (queryRows rs) = .all) := by
  intro rs hne hm
  constructor
  · intro hy
    have hf : foldConflict (conflictRows rs) = .free := by
      apply foldConflict_of_free
      · simpa [conflictRows] using hne
      · intro x hx
        obtain ⟨r, hr, rfl⟩ := List.mem_map.mp hx
        exact (lead_yes (hy r hr)).1
    unfold foldEntailment
    have hq : (queryRows rs).all (·.2 == .proved) = true := by
      rw [List.all_eq_true]
      intro x hx
      obtain ⟨r, hr, rfl⟩ := List.mem_map.mp hx
      simp [(lead_yes (hy r hr)).2.1]
    have he : (queryRows rs).isEmpty = false := by simpa [queryRows] using hne
    simp [hf, hq, he]
  · intro h r hr
    obtain ⟨hf, _, hall⟩ := foldEntailment_all h
    obtain ⟨_, hfree⟩ := foldConflict_free hf
    have hc : r.conflict = .free := hfree (r.choice, r.conflict) (List.mem_map.mpr ⟨r, hr, rfl⟩)
    have hq : r.query = .proved := hall (r.choice, r.query) (List.mem_map.mpr ⟨r, hr, rfl⟩)
    simp [Row.lead, hc, hq, hm r hr]

end VE.Ask
