import VE.Alternatives.Decl

/-! Inlining (docs/spec/alternatives.md 4.3, 7.2): what inlining keeps and
changes, that inlined formulas are base formulas without profile words, and
`inline_faithful` (W3's `faithful` is the model, not a dependency). -/
namespace VE.Alternatives
open VE.Norms
universe u

/-! ## The facts of a well-formed block -/

/-- The conditions `altSemanticCheck` records, as propositions. -/
structure AltValid (A : AltDoc) : Prop where
  wf : WellFormed (inlineTree A) = true
  chooserSort : A.alt.chooser ∈ A.E.sorts
  actionSort : A.alt.action ∈ A.E.sorts
  harmSort : A.alt.harm ∈ A.E.sorts
  chooser_ne_action : A.alt.chooser ≠ A.alt.action
  chooser_ne_harm : A.alt.chooser ≠ A.alt.harm
  action_ne_harm : A.alt.action ≠ A.alt.harm
  reserved : ∀ w ∈ profileWords, A.E.predicates w = none
  roles : ∀ x ∈ roleSorts A.alt, (envAt (inlineTree A) 0).predicates x.2.1 = some x.2.2
  performed : performedOk A = true
  fulfil : ∀ f ∈ A.alt.fulfilments, fulfilmentOk A f = true
  premises : ∀ a ∈ A.Γ, a.WellFormed (envAt (inlineTree A) 0) []

theorem altValid_of_wellFormed (A : AltDoc) (h : WellFormedAlt A = true) : AltValid A := by
  have hc := altSemanticCheck_of_wellFormed A h
  simp only [altSemanticCheck, Bool.and_eq_true] at hc
  obtain ⟨⟨⟨⟨⟨⟨⟨⟨⟨hwf, hs⟩, hd1⟩, hd2⟩, hd3⟩, hres⟩, hroles⟩, hperf⟩, hful⟩, hΓ⟩ := hc
  simp only [List.all_eq_true, List.mem_cons, List.not_mem_nil, or_false, forall_eq_or_imp, forall_eq,
    List.contains_iff_mem] at hs
  simp only [bne_iff_ne, ne_eq] at hd1 hd2 hd3
  simp only [List.all_eq_true, beq_iff_eq] at hres hroles hΓ
  simp only [List.all_eq_true] at hful
  refine ⟨hwf, hs.1, hs.2.1, hs.2.2, hd1, hd2, hd3, hres, hroles, hperf, hful, ?_⟩
  intro a ha
  exact (VE.check_iff_wellFormed _ _ a).mp (hΓ a ha)

theorem hide_some {E : VE.Environment} {ns : List String} {p : String} {ss : List String}
    (h : (hide E ns).predicates p = some ss) : E.predicates p = some ss ∧ p ∉ ns := by
  simp only [hide] at h
  by_cases hp : p ∈ ns
  · simp [hp] at h
  · simp only [hp, if_false] at h
    exact ⟨h, hp⟩

section Facts
variable {A : AltDoc} (hv : AltValid A)
include hv

theorem base_available : (envAt (inlineTree A) 0).predicates A.alt.available = some [A.alt.action, A.alt.chooser] :=
  hv.roles ("available", A.alt.available, [A.alt.action, A.alt.chooser]) (by simp [roleSorts])

theorem base_leadsTo : (envAt (inlineTree A) 0).predicates A.alt.leadsTo = some [A.alt.action, A.alt.harm] :=
  hv.roles ("leads_to", A.alt.leadsTo, [A.alt.action, A.alt.harm]) (by simp [roleSorts])

theorem base_inaction {p : String} (hp : A.alt.inaction = some p) :
    (envAt (inlineTree A) 0).predicates p = some [A.alt.action] :=
  hv.roles ("inaction", p, _) (by simp [roleSorts, hp])

theorem base_taken {p : String} (hp : A.alt.taken = some p) :
    (envAt (inlineTree A) 0).predicates p = some [A.alt.action] :=
  hv.roles ("taken", p, _) (by simp [roleSorts, hp])

theorem base_proximate {p : String} (hp : A.alt.proximate = some p) :
    (envAt (inlineTree A) 0).predicates p = some [A.alt.action, A.alt.harm] :=
  hv.roles ("proximate", p, _) (by simp [roleSorts, hp])

theorem E_available : A.E.predicates A.alt.available = some [A.alt.action, A.alt.chooser] :=
  (hide_some (base_available hv)).1

theorem E_leadsTo : A.E.predicates A.alt.leadsTo = some [A.alt.action, A.alt.harm] :=
  (hide_some (base_leadsTo hv)).1

/-- 4.1(2): `available` and `leads_to` are different predicates (their sorts differ). -/
theorem available_ne_leadsTo : A.alt.available ≠ A.alt.leadsTo := by
  intro he
  have h1 := E_available hv
  rw [he, E_leadsTo hv] at h1
  simp only [Option.some.injEq, List.cons.injEq, and_true, true_and] at h1
  exact hv.chooser_ne_harm h1.symm

theorem available_not_layer : A.alt.available ∉ layerNames (inlineTree A).T :=
  (hide_some (base_available hv)).2

theorem leadsTo_not_layer : A.alt.leadsTo ∉ layerNames (inlineTree A).T :=
  (hide_some (base_leadsTo hv)).2

end Facts

/-! ## Typing of the bodies -/

theorem avoidableF_wellFormed {E : VE.Environment} {A : AltEnv}
    (ha : E.predicates A.available = some [A.action, A.chooser])
    (hl : E.predicates A.leadsTo = some [A.action, A.harm]) (hs : A.action ∈ E.sorts) :
    (avoidableF A).WellFormed E [A.chooser, A.harm] := by
  simp [avoidableF, VE.Formula.WellFormed, VE.Term.sortOf, ha, hl, hs]

theorem unavoidableF_wellFormed {E : VE.Environment} {A : AltEnv}
    (ha : E.predicates A.available = some [A.action, A.chooser])
    (hl : E.predicates A.leadsTo = some [A.action, A.harm]) (hs : A.action ∈ E.sorts) :
    (unavoidableF A).WellFormed E [A.chooser, A.harm] :=
  ⟨by simp [VE.Formula.WellFormed, VE.Term.sortOf, ha, hs], avoidableF_wellFormed ha hl hs⟩

theorem allowsF_wellFormed {E : VE.Environment} {A : AltEnv}
    (ha : E.predicates A.available = some [A.action, A.chooser])
    (hl : E.predicates A.leadsTo = some [A.action, A.harm]) (hs : A.action ∈ E.sorts)
    (hc : A.chooser ∈ E.sorts) :
    (allowsF A).WellFormed E [A.harm, A.action] := by
  simp [allowsF, VE.Formula.WellFormed, VE.Term.sortOf, ha, hl, hs, hc]

theorem preventsF_wellFormed {E : VE.Environment} {A : AltEnv}
    (ha : E.predicates A.available = some [A.action, A.chooser])
    (hl : E.predicates A.leadsTo = some [A.action, A.harm]) (hs : A.action ∈ E.sorts)
    (hc : A.chooser ∈ E.sorts) :
    (preventsF A).WellFormed E [A.harm, A.action] := by
  simp [preventsF, VE.Formula.WellFormed, VE.Term.sortOf, ha, hl, hs, hc]

theorem profileDef_some {A : AltEnv} {p : String} {ss : List String} {F : VE.Formula}
    (h : profileDef A p = some (ss, F)) :
    (ss = [A.harm, A.chooser] ∧ (F = avoidableF A ∨ F = unavoidableF A)) ∨
      (ss = [A.action, A.harm] ∧ (F = allowsF A ∨ F = preventsF A)) := by
  unfold profileDef at h
  split at h
  · cases h; exact Or.inl ⟨rfl, Or.inl rfl⟩
  split at h
  · cases h; exact Or.inl ⟨rfl, Or.inr rfl⟩
  split at h
  · cases h; exact Or.inr ⟨rfl, Or.inl rfl⟩
  split at h
  · cases h; exact Or.inr ⟨rfl, Or.inr rfl⟩
  · cases h

theorem profileDef_length {A : AltEnv} {p : String} {ss : List String} {F : VE.Formula}
    (h : profileDef A p = some (ss, F)) : ss.length = 2 := by
  rcases profileDef_some h with ⟨rfl, _⟩ | ⟨rfl, _⟩ <;> rfl

theorem body_wellFormed {A : AltDoc} (hv : AltValid A) {p : String} {ss : List String} {F : VE.Formula}
    (h : profileDef A.alt p = some (ss, F)) : F.WellFormed A.E ss.reverse := by
  have ha := E_available hv
  have hl := E_leadsTo hv
  rcases profileDef_some h with ⟨rfl, rfl | rfl⟩ | ⟨rfl, rfl | rfl⟩
  · exact avoidableF_wellFormed ha hl hv.actionSort
  · exact unavoidableF_wellFormed ha hl hv.actionSort
  · exact allowsF_wellFormed ha hl hv.actionSort hv.chooserSort
  · exact preventsF_wellFormed ha hl hv.actionSort hv.chooserSort

theorem extEnv_predicates_none {A : AltDoc} {p : String} (h : profileDef A.alt p = none) :
    (extEnv A).predicates p = A.E.predicates p := by
  simp [extEnv, h]

theorem extEnv_predicates_some {A : AltDoc} {p : String} {ss : List String} {F : VE.Formula}
    (h : profileDef A.alt p = some (ss, F)) : (extEnv A).predicates p = some ss := by
  simp [extEnv, h]

theorem sortOf_extEnv (A : AltDoc) (Γ : List String) (t : VE.Term) :
    t.sortOf (extEnv A) Γ = t.sortOf A.E Γ := by
  cases t <;> rfl

/-- The predicates a well-formed formula mentions are declared. -/
theorem wf_preds {E : VE.Environment} : ∀ {a : VE.Formula} {Γ : List String}, a.WellFormed E Γ →
    ∀ p ∈ preds a, (E.predicates p).isSome
  | .top, _, _, _, hp | .bottom, _, _, _, hp | .eq _ _, _, _, _, hp => by simp [preds] at hp
  | .unary q _, _, ⟨_, hq, _⟩, p, hp => by simp only [preds, List.mem_singleton] at hp; subst hp; simp [hq]
  | .binary q _ _, _, ⟨_, _, hq, _⟩, p, hp => by
    simp only [preds, List.mem_singleton] at hp; subst hp; simp [hq]
  | .not a, _, h, p, hp => wf_preds (a := a) h p hp
  | .all _ a, _, h, p, hp | .ex _ a, _, h, p, hp => wf_preds (a := a) h.2 p hp
  | .and a b, _, h, p, hp | .or a b, _, h, p, hp | .implies a b, _, h, p, hp => by
    rcases List.mem_append.mp hp with hp | hp
    · exact wf_preds h.1 p hp
    · exact wf_preds h.2 p hp

/-! ## Theorems -/

/-- 4.1 ⇒ W1 well-formedness of the inlined document. -/
theorem alternatives_wellFormed (A : AltDoc) (h : WellFormedAlt A = true) :
    WellFormed (inlineTree A) = true :=
  (altValid_of_wellFormed A h).wf

/-- What inlining changes and what it keeps. -/
theorem inlineTree_shape (A : AltDoc) (_h : WellFormedAlt A = true) :
    (inlineTree A).E = A.E ∧ (inlineTree A).lits = A.lits ∧ (inlineTree A).T.regulated = A.T.regulated ∧
    (inlineTree A).T.nodes = A.T.nodes.map (fun N =>
      { N with guard := inline A N.guard, carveOuts := N.carveOuts.map (inline A) }) :=
  ⟨rfl, rfl, rfl, rfl⟩

theorem inline_wellFormed {A : AltDoc} (hv : AltValid A) :
    ∀ (φ : VE.Formula) (Γ : List String), φ.WellFormed (extEnv A) Γ → (inline A φ).WellFormed A.E Γ
  | .top, _, _ | .bottom, _, _ => trivial
  | .unary p t, Γ, ⟨s, hp, ht⟩ => by
    show (VE.Formula.unary p t).WellFormed A.E Γ
    cases hd : profileDef A.alt p with
    | none => exact ⟨s, by rw [← extEnv_predicates_none hd]; exact hp, by rw [← sortOf_extEnv]; exact ht⟩
    | some d =>
      obtain ⟨ss, F⟩ := d
      rw [extEnv_predicates_some hd] at hp
      cases hp
      have := profileDef_length hd
      simp at this
  | .binary p t u, Γ, ⟨s, r, hp, ht, hu⟩ => by
    unfold inline inlineWith
    cases hd : profileDef A.alt p with
    | none =>
      exact ⟨s, r, by rw [← extEnv_predicates_none hd]; exact hp, by rw [← sortOf_extEnv]; exact ht,
        by rw [← sortOf_extEnv]; exact hu⟩
    | some d =>
      obtain ⟨ss, F⟩ := d
      rw [extEnv_predicates_some hd] at hp
      cases hp
      refine inst_wellFormed A.E A.E rfl rfl (fun _ _ h => h) F Γ [r, s] [u, t] rfl ?_ (body_wellFormed hv hd)
      intro i h₁ _
      match i, h₁ with
      | 0, _ => rw [← sortOf_extEnv]; exact hu
      | 1, _ => rw [← sortOf_extEnv]; exact ht
  | .eq t u, Γ, ⟨s, ht, hu⟩ => ⟨s, by rw [← sortOf_extEnv]; exact ht, by rw [← sortOf_extEnv]; exact hu⟩
  | .not a, Γ, h => inline_wellFormed hv a Γ h
  | .and a b, Γ, h | .or a b, Γ, h | .implies a b, Γ, h =>
    ⟨inline_wellFormed hv a Γ h.1, inline_wellFormed hv b Γ h.2⟩
  | .all s a, Γ, h | .ex s a, Γ, h => ⟨h.1, inline_wellFormed hv a (s :: Γ) h.2⟩

/-- Inlined formulas are formulas over `E` and mention no profile word (the tree has no
fulfilment atoms, 1.3). -/
theorem inline_base (A : AltDoc) (h : WellFormedAlt A = true) (φ : VE.Formula) (Γ : List String)
    (hφ : φ.WellFormed (extEnv A) Γ) :
    (inline A φ).WellFormed A.E Γ ∧ ∀ w ∈ profileWords, w ∉ VE.Norms.preds (inline A φ) := by
  have hv := altValid_of_wellFormed A h
  have hw := inline_wellFormed hv φ Γ hφ
  refine ⟨hw, fun w hw' hm => ?_⟩
  have := wf_preds hw w hm
  rw [hv.reserved w hw'] at this
  cases this

theorem term_denote_withDefinitions (A : AltDoc) (S : VE.Structure.{u}) (ρ : VE.Valuation S) (t : VE.Term) :
    t.denote (withDefinitions A S) ρ = t.denote S ρ := by
  cases t <;> rfl

theorem tupleTyped_withDefinitions (A : AltDoc) (S : VE.Structure.{u}) (ss : List String) (vs : List S.Carrier) :
    VE.TupleTyped (withDefinitions A S) ss vs ↔ VE.TupleTyped S ss vs :=
  tupleTyped_relation S _ ss vs

theorem binary_withDefinitions (A : AltDoc) (S : VE.Structure.{u}) (ρ : VE.Valuation S) (p : String)
    (t w : VE.Term) :
    (VE.Formula.binary p t w).denote (withDefinitions A S) ρ ↔
      ∃ v v', t.denote S ρ = some v ∧ w.denote S ρ = some v' ∧ (withDefinitions A S).relation p [v, v'] := by
  simp only [VE.Formula.denote, term_denote_withDefinitions]
  exact Iff.rfl

theorem withDefinitions_relation_some {A : AltDoc} {S : VE.Structure.{u}} {p : String} {ss : List String}
    {F : VE.Formula} (hd : profileDef A.alt p = some (ss, F)) (vs : List S.Carrier) :
    (withDefinitions A S).relation p vs ↔ VE.TupleTyped S ss vs ∧ F.denote S (tupleVal vs) := by
  simp [withDefinitions, hd]

/-- 4.3: inlining is faithful to the definitional reading, on structures admissible for `E`. -/
theorem inline_faithful (A : AltDoc) (h : WellFormedAlt A = true) (φ : VE.Formula) (Γ : List String)
    (hφ : φ.WellFormed (extEnv A) Γ) (S : VE.Structure.{u}) (hS : S.Admissible A.E)
    (ρ : VE.Valuation S) (hρ : VE.Valuation.Typed S Γ ρ) :
    (inline A φ).denote S ρ ↔ φ.denote (withDefinitions A S) ρ := by
  have hv := altValid_of_wellFormed A h
  induction φ generalizing Γ ρ with
  | top | bottom => exact Iff.rfl
  | unary p t =>
    obtain ⟨s, hp, _⟩ := hφ
    show (VE.Formula.unary p t).denote S ρ ↔ _
    cases hd : profileDef A.alt p with
    | none =>
      simp only [VE.Formula.denote, term_denote_withDefinitions]
      simp [withDefinitions, hd]
    | some d =>
      obtain ⟨ss, F⟩ := d
      rw [extEnv_predicates_some hd] at hp
      cases hp
      have := profileDef_length hd
      simp at this
  | binary p t u =>
    obtain ⟨s, r, hp, ht, hu⟩ := hφ
    unfold inline inlineWith
    cases hd : profileDef A.alt p with
    | none =>
      simp only [VE.Formula.denote, term_denote_withDefinitions]
      simp [withDefinitions, hd]
    | some d =>
      obtain ⟨ss, F⟩ := d
      rw [extEnv_predicates_some hd] at hp
      cases hp
      rw [sortOf_extEnv] at ht hu
      obtain ⟨v, hvt, hvd⟩ := VE.term_defined hS hρ ht
      obtain ⟨w, hwu, hwd⟩ := VE.term_defined hS hρ hu
      have hden : Denotes S ρ [u, t] [w, v] := by
        refine ⟨rfl, fun i h₁ _ => ?_⟩
        match i, h₁ with
        | 0, _ => exact hwu
        | 1, _ => exact hvt
      simp only
      rw [inst_denote S A.E F [r, s] [u, t] ρ [w, v] (body_wellFormed hv hd) rfl hden,
        binary_withDefinitions]
      constructor
      · intro hF
        refine ⟨v, w, hvt, hwu, (withDefinitions_relation_some hd [v, w]).mpr ⟨⟨hvd, hwd, trivial⟩, hF⟩⟩
      · rintro ⟨v', w', hv', hw', hr⟩
        rw [hvt] at hv'; rw [hwu] at hw'
        cases hv'; cases hw'
        exact ((withDefinitions_relation_some hd [v, w]).mp hr).2
  | eq t u =>
    simp only [inline, inlineWith, VE.Formula.denote, term_denote_withDefinitions]
    exact Iff.rfl
  | not a ih =>
    exact not_congr (ih Γ hφ ρ hρ)
  | and a b ia ib => exact and_congr (ia Γ hφ.1 ρ hρ) (ib Γ hφ.2 ρ hρ)
  | or a b ia ib => exact or_congr (ia Γ hφ.1 ρ hρ) (ib Γ hφ.2 ρ hρ)
  | implies a b ia ib => exact imp_congr (ia Γ hφ.1 ρ hρ) (ib Γ hφ.2 ρ hρ)
  | all s a ih | ex s a ih =>
    simp only [inline, inlineWith, VE.Formula.denote] at ih ⊢
    first
    | exact forall_congr' fun v => imp_congr_right fun hd => ih (s :: Γ) hφ.2 (v :: ρ) (VE.typed_cons hρ hd)
    | exact exists_congr fun v => and_congr_right fun hd => ih (s :: Γ) hφ.2 (v :: ρ) (VE.typed_cons hρ hd)

end VE.Alternatives
