import VE.Attribution.Elaborate

/-! Spec 9.2, second half: the forced holder disequalities `neqs`, model
existence over any admissible old-language structure (`source_over_any_structure`
and its instances), existence of expansion, vocabulary conservativity and
`reports_no_leak`. -/
namespace VE.Reports
open VE.Route (fol)
open VE.Definitions (forget hide)
universe u

/-! ## `neqs` -/

theorem neqRow_eq_some {h P : String} {b x : VE.Formula} (hb : neqRow h P b = some x) :
    ∃ h', b = .not (.unary P (.const h')) ∧ x = .not (.eq (.const h) (.const h')) := by
  unfold neqRow at hb
  split at hb
  · rename_i P' h'
    split at hb
    · rename_i he; cases hb; subst he; exact ⟨h', rfl, rfl⟩
    · cases hb
  · cases hb

theorem mem_neqs {R : List VE.Formula} {x : VE.Formula} :
    x ∈ neqs R ↔ ∃ P h h', VE.Formula.unary P (.const h) ∈ R ∧ VE.Formula.not (.unary P (.const h')) ∈ R ∧
      x = .not (.eq (.const h) (.const h')) := by
  unfold neqs
  rw [List.mem_flatMap]
  constructor
  · rintro ⟨a, ha, hx⟩
    unfold neqsOf at hx
    split at hx
    · rename_i P h
      obtain ⟨b, hb, hbx⟩ := List.mem_filterMap.mp hx
      obtain ⟨h', rfl, rfl⟩ := neqRow_eq_some hbx
      exact ⟨P, h, h', ha, hb, rfl⟩
    · cases hx
  · rintro ⟨P, h, h', hp, hn, rfl⟩
    exact ⟨_, hp, List.mem_filterMap.mpr ⟨_, hn, by simp [neqRow]⟩⟩

/-- A structure satisfying a signed list satisfies the disequalities it forces. -/
theorem neqs_sat_of_sat (S : VE.Structure.{u}) (R : List VE.Formula) (hR : fol.Sat S R) :
    fol.Sat S (neqs R) := by
  intro x hx
  obtain ⟨P, h, h', hp, hn, rfl⟩ := mem_neqs.mp hx
  have h1 : (VE.Formula.unary P (.const h)).denote S [] := hR _ hp
  have h2 : ¬ (VE.Formula.unary P (.const h')).denote S [] := hR _ hn
  show ¬ _
  rintro ⟨v, hv, hv'⟩
  obtain ⟨w, hw, hr⟩ := (denote_atom S P h).mp h1
  simp only [VE.Term.denote] at hv hv'
  rw [hv] at hw; cases hw
  exact h2 ((denote_atom S P h').mpr ⟨v, hv', hr⟩)

/-- The disequalities read constants only. -/
theorem neqs_denote_congr {R : List VE.Formula} {x : VE.Formula} (hx : x ∈ neqs R)
    (S : VE.Structure.{u}) (rel : String → List S.Carrier → Prop) :
    x.denote { S with relation := rel } [] ↔ x.denote S [] := by
  obtain ⟨P, h, h', _, _, rfl⟩ := mem_neqs.mp hx
  exact Iff.rfl

theorem uniform_neqs (R : List VE.Formula) (hu : UniformPolarity R) : neqs R = [] := by
  apply List.eq_nil_iff_forall_not_mem.mpr
  intro x hx
  obtain ⟨P, h, h', hp, hn, _⟩ := mem_neqs.mp hx
  exact hu ⟨P, h, h', hp, hn⟩

/-- 4.4: the hypothesis of every model-existence theorem is trivial for a
positive document. -/
theorem positive_uniform (D : ReportDoc) (h : WellFormedReports D = true) (hp : Positive D) :
    UniformPolarity (premises D) := by
  have hw := wf_of h
  rintro ⟨P, h, h', _, hn⟩
  obtain ⟨u, hu, hpu⟩ := mem_premises.mp hn
  rcases unit_shape hw hu with
    ⟨_, _, _, _, _, _, _, _, hp'⟩ | ⟨_, _, _, _, _, _, hp'⟩ |
    ⟨_, _, _, _, _, _, hc, _, _⟩ | ⟨_, _, _, _, hc, _, _⟩
  · rw [hp'] at hpu; cases hpu
  · rw [hp'] at hpu; cases hpu
  · exact hp u hu ⟨_, hc⟩
  · exact hp u hu ⟨_, hc⟩

theorem neqs_wellFormed (D : ReportDoc) (h : WellFormedReports D = true) (R : List VE.Formula)
    (hR : ∀ a ∈ R, SignedAtom D a) : ∀ a ∈ neqs R, a.WellFormed D.E [] := by
  intro x hx
  obtain ⟨P, h₁, h₂, hp, hn, rfl⟩ := mem_neqs.mp hx
  obtain ⟨r, _, g, ⟨s, hs, hg⟩, he⟩ := hR _ hp
  obtain ⟨r', _, g', ⟨s', hs', hg'⟩, he'⟩ := hR _ hn
  rcases he with he | he
  · rcases he' with he' | he'
    · cases he'
    · simp only [VE.Formula.unary.injEq, VE.Term.const.injEq, VE.Formula.not.injEq] at he he'
      obtain ⟨rfl, rfl⟩ := he
      obtain ⟨rfl, rfl⟩ := he'
      rw [hs] at hs'; cases hs'
      exact ⟨s, hg, hg'⟩
  · cases he

theorem positive_expandable (D : ReportDoc) (h : WellFormedReports D = true) (hp : Positive D)
    (S₀ : VE.Structure.{u}) : Expandable D S₀ := by
  unfold Expandable
  rw [uniform_neqs _ (positive_uniform D h hp)]
  intro _ hx; nomatch hx

/-! ## A source model over any admissible structure -/

/-- The holders a positive top-level report unit asserts at key `k`. -/
def AssertedJ (D : ReportDoc) (S₀ : VE.Structure.{u}) (k : ReportKey) (v : S₀.Carrier) : Prop :=
  ∃ x ∈ D.units, ∃ h b lit, x.content = .report h k.act k.ctx b lit ∧ holderSort D h = some k.sort ∧
    complementId D b lit = k.content ∧ S₀.constant h = some v

/-- The evidence contexts a positive top-level assessment unit asserts at key `k`. -/
def AssertedA (D : ReportDoc) (S₀ : VE.Structure.{u}) (k : AssessKey) (v : S₀.Carrier) : Prop :=
  ∃ x ∈ D.units, ∃ b r, x.content = .assessment k.j k.a b ∧ contentId D b = k.content ∧
    recordOf D k.a = some r ∧ S₀.constant r.context = some v

theorem assertedJ_top {D : ReportDoc} {S₀ : VE.Structure.{u}} {k : ReportKey} {v : S₀.Carrier}
    (ha : AssertedJ D S₀ k v) : k ∈ topKeys D := by
  obtain ⟨x, hx, h, b, lit, hc, hs, hq, _⟩ := ha
  refine List.mem_filterMap.mpr ⟨x, hx, ?_⟩
  rw [hc]
  simp [topReportKeyOf, reportKeyOf, hs, hq]

theorem assertedA_top {D : ReportDoc} {S₀ : VE.Structure.{u}} {k : AssessKey} {v : S₀.Carrier}
    (ha : AssertedA D S₀ k v) : k ∈ topAKeys D := by
  obtain ⟨x, hx, b, r, hc, hq, _, _⟩ := ha
  refine List.mem_filterMap.mpr ⟨x, hx, ?_⟩
  rw [hc]
  simp [topAssessKeyOf, assessKeyOf, hq]

/-- The premise of an asserting unit. -/
theorem assertedJ_premise {D : ReportDoc} {S₀ : VE.Structure.{u}} {k : ReportKey} {v : S₀.Carrier}
    (ha : AssertedJ D S₀ k v) :
    ∃ h, VE.Formula.unary (reportName D k) (.const h) ∈ premises D ∧ S₀.constant h = some v := by
  obtain ⟨x, hx, h, b, lit, hc, hs, hq, hv⟩ := ha
  refine ⟨h, unitPremise_mem hx ?_, hv⟩
  simp [unitPremise, hc, «elab», hs, hq]

theorem assertedA_premise {D : ReportDoc} {S₀ : VE.Structure.{u}} {k : AssessKey} {v : S₀.Carrier}
    (ha : AssertedA D S₀ k v) :
    ∃ r : Assessment, recordOf D k.a = some r ∧
      VE.Formula.unary (assessName D k) (.const r.context) ∈ premises D ∧ S₀.constant r.context = some v := by
  obtain ⟨x, hx, b, r, hc, hq, hr, hv⟩ := ha
  refine ⟨r, hr, unitPremise_mem hx ?_, hv⟩
  simp [unitPremise, hc, «elab», hr, hq]

/-- The source model over `S₀` whose relations hold exactly at the asserted
holders on the keys some top-level unit asserts or denies, and are `g` (on the
key's sort) elsewhere. -/
def mkSource (D : ReportDoc) (hw : WF D) (S₀ : VE.Structure.{u}) (h₀ : S₀.Admissible D.E)
    (gJ : ReportKey → S₀.Carrier → Prop) (gA : AssessKey → S₀.Carrier → Prop) : Source.{u} D where
  S := S₀
  J act s c q v := AssertedJ D S₀ ⟨act, s, c, q⟩ v ∨
    (⟨act, s, c, q⟩ ∉ topKeys D ∧ S₀.domain s v ∧ gJ ⟨act, s, c, q⟩ v)
  A j a q v := AssertedA D S₀ ⟨j, a, q⟩ v ∨ (⟨j, a, q⟩ ∉ topAKeys D ∧ S₀.domain D.evidence v ∧ gA ⟨j, a, q⟩ v)
  J_typed := by
    rintro act s c q v (⟨x, _, h, b, lit, _, hs, _, hv⟩ | ⟨_, hd, _⟩)
    · obtain ⟨v', hv', hd⟩ := const_exists h₀ (holderSort_const hs)
      rw [hv] at hv'; cases hv'; exact hd
    · exact hd
  A_typed := by
    rintro j a q v (⟨x, _, b, r, _, _, hr, hv⟩ | ⟨_, hd, _⟩)
    · obtain ⟨v', hv', hd⟩ := const_exists h₀ (recordOf_context hw hr)
      rw [hv] at hv'; cases hv'; exact hd
    · exact hd

theorem mkSource_intended (D : ReportDoc) (hw : WF D) (S₀ : VE.Structure.{u}) (h₀ : S₀.Admissible D.E)
    (he : Expandable D S₀) (gJ : ReportKey → S₀.Carrier → Prop) (gA : AssessKey → S₀.Carrier → Prop) :
    IntendedReports D (mkSource D hw S₀ h₀ gJ gA) := by
  intro u hu
  rcases unit_shape hw hu with
    ⟨hd, act, c, b, lit, s, hc, hs, hp⟩ | ⟨j, x, b, r, hc, hr, hp⟩ |
    ⟨hd, act, c, b, lit, s, hc, hs, hp⟩ | ⟨j, x, b, r, hc, hr, hp⟩ <;> rw [hc]
  · intro s' hs' v hv
    rw [hs] at hs'; cases hs'
    exact Or.inl ⟨u, hu, hd, b, lit, hc, hs, rfl, hv⟩
  · intro r' hr' v hv
    rw [hr] at hr'; cases hr'
    exact Or.inl ⟨u, hu, b, r, hc, rfl, hr, hv⟩
  · intro hall
    obtain ⟨v₀, hv₀, _⟩ := const_exists h₀ (holderSort_const hs)
    rcases hall s hs v₀ hv₀ with ha | ⟨hnt, _, _⟩
    · obtain ⟨h₁, hp₁, hv₁⟩ := assertedJ_premise ha
      have hn : VE.Formula.not (.unary (reportName D ⟨act, s, c, complementId D b lit⟩) (.const hd)) ∈
          premises D := unitPremise_mem hu hp
      have hneq := he _ (mem_neqs.mpr ⟨_, h₁, hd, hp₁, hn, rfl⟩)
      exact hneq ⟨v₀, hv₁, hv₀⟩
    · apply hnt
      refine List.mem_filterMap.mpr ⟨u, hu, ?_⟩
      rw [hc]; simp [topReportKeyOf, reportKeyOf, hs]
  · intro hall
    obtain ⟨v₀, hv₀, _⟩ := const_exists h₀ (recordOf_context hw hr)
    rcases hall r hr v₀ hv₀ with ha | ⟨hnt, _, _⟩
    · obtain ⟨r₁, hr₁, hp₁, hv₁⟩ := assertedA_premise ha
      rw [hr] at hr₁; cases hr₁
      have hn : VE.Formula.not (.unary (assessName D ⟨j, x, contentId D b⟩) (.const r.context)) ∈
          premises D := unitPremise_mem hu hp
      have hneq := he _ (mem_neqs.mpr ⟨_, r.context, r.context, hp₁, hn, rfl⟩)
      exact hneq ⟨v₀, hv₁, hv₀⟩
    · apply hnt
      refine List.mem_filterMap.mpr ⟨u, hu, ?_⟩
      rw [hc]; simp [topAssessKeyOf, assessKeyOf]

/-- 4.2: every admissible old-language structure that satisfies the forced
disequalities underlies a source model of D. -/
theorem source_over_any_structure (D : ReportDoc) (h : WellFormedReports D = true) (S₀ : VE.Structure.{u})
    (h₀ : S₀.Admissible D.E) (he : Expandable D S₀) :
    ∃ M : Source.{u} D, M.S = S₀ ∧ IntendedReports D M :=
  ⟨mkSource D (wf_of h) S₀ h₀ (fun _ _ => False) (fun _ _ => False), rfl,
    mkSource_intended D (wf_of h) S₀ h₀ he _ _⟩

/-- … and only such a structure does. -/
theorem source_over_any_structure_iff (D : ReportDoc) (h : WellFormedReports D = true) (S₀ : VE.Structure.{u})
    (h₀ : S₀.Admissible D.E) :
    (∃ M : Source.{u} D, M.S = S₀ ∧ IntendedReports D M) ↔ Expandable D S₀ := by
  constructor
  · rintro ⟨M, rfl, hi⟩
    have hs := ((reports_elaboration_faithful D h M h₀).2).mpr hi
    intro x hx
    exact (neqs_denote_congr hx M.S _).mp (neqs_sat_of_sat _ _ hs x hx)
  · exact source_over_any_structure D h S₀ h₀

/-- … and with any key that no top-level unit asserts or denies interpreted as empty. -/
theorem unreported_key_free (D : ReportDoc) (h : WellFormedReports D = true) (S₀ : VE.Structure.{u})
    (h₀ : S₀.Admissible D.E) (he : Expandable D S₀) (k : ReportKey) (hk : k ∉ topKeys D) :
    ∃ M : Source.{u} D, M.S = S₀ ∧ IntendedReports D M ∧ ∀ v, ¬ M.J k.act k.sort k.ctx k.content v := by
  refine ⟨mkSource D (wf_of h) S₀ h₀ (fun _ _ => False) (fun _ _ => False), rfl,
    mkSource_intended D (wf_of h) S₀ h₀ he _ _, ?_⟩
  rintro v (ha | ⟨_, _, hf⟩)
  · exact hk (assertedJ_top ha)
  · exact hf

/-! ## Expansion (4.4) -/

theorem expansion_exists (D : ReportDoc) (h : WellFormedReports D = true) (S₀ : VE.Structure.{u})
    (h₀ : S₀.Admissible D.E) (he : Expandable D S₀) :
    ∃ S', forget (names D) S' = S₀ ∧ S'.Admissible (envReports D) ∧ fol.Sat S' (premises D) := by
  obtain ⟨M, rfl, hi⟩ := source_over_any_structure D h S₀ h₀ he
  obtain ⟨ha, hs⟩ := reports_elaboration_faithful D h M h₀
  exact ⟨interp D M, forget_interp D h M h₀, ha, hs.mpr hi⟩

theorem expansion_exists_iff (D : ReportDoc) (h : WellFormedReports D = true) (S₀ : VE.Structure.{u})
    (h₀ : S₀.Admissible D.E) :
    (∃ S', forget (names D) S' = S₀ ∧ S'.Admissible (envReports D) ∧ fol.Sat S' (premises D)) ↔
      Expandable D S₀ := by
  constructor
  · rintro ⟨S', rfl, _, hs⟩ x hx
    exact (neqs_denote_congr hx S' _).mpr (neqs_sat_of_sat S' _ hs x hx)
  · exact expansion_exists D h S₀ h₀

/-! ## Conservativity (4.4) -/

theorem forget_denote {D : ReportDoc} (hw : WF D) (S' : VE.Structure.{u}) (a : VE.Formula)
    (ha : a.WellFormed D.E []) : a.denote (forget (names D) S') [] ↔ a.denote S' [] :=
  VE.Definitions.denote_congr D.E S' _ (fun r _ _ hr => by
    simp [not_mem_names_of_pred hw hr]) a [] [] ha

theorem admissible_envReports_of_old {D : ReportDoc} (hw : WF D) {S : VE.Structure.{u}}
    (hS : S.Admissible D.E) : S.Admissible (envReports D) := by
  refine ⟨fun c s hc => hS.1 c s hc, fun p vs hp => ?_⟩
  obtain ⟨ss, hss, ht⟩ := hS.2 p vs hp
  exact ⟨ss, envReports_pred_of_old hw hss, ht⟩

/-- reports_old_language_conservative: the vocabulary extension, unconditional. -/
theorem reports_old_language_conservative (D : ReportDoc) (h : WellFormedReports D = true)
    (Γ : List VE.Formula) (φ : VE.Formula)
    (hΓ : ∀ a ∈ Γ, a.WellFormed D.E []) (hφ : φ.WellFormed D.E []) :
    VE.Entails.{u} (envReports D) Γ φ ↔ VE.Entails.{u} D.E Γ φ := by
  have hw := wf_of h
  constructor
  · intro he S hS hs
    exact he S (admissible_envReports_of_old hw hS) hs
  · intro he S' hS hs
    apply (forget_denote hw S' φ hφ).mp
    exact he _ (restrictJ_admissible D h S' hS) (fun a ha => (forget_denote hw S' a (hΓ a ha)).mpr (hs a ha))

/-- The expansion of `S₀` by the holders a signed list asserts. -/
def expandBy (D : ReportDoc) (R : List VE.Formula) (S₀ : VE.Structure.{u}) : VE.Structure.{u} :=
  { S₀ with relation := fun r vs =>
      if r ∈ names D then ∃ h v, VE.Formula.unary r (.const h) ∈ R ∧ S₀.constant h = some v ∧ vs = [v]
      else S₀.relation r vs }

theorem expandBy_old {D : ReportDoc} (hw : WF D) (R : List VE.Formula) (S₀ : VE.Structure.{u})
    (a : VE.Formula) (ha : a.WellFormed D.E []) : a.denote (expandBy D R S₀) [] ↔ a.denote S₀ [] :=
  VE.Definitions.denote_congr D.E S₀ _ (fun r _ _ hr => by
    simp [not_mem_names_of_pred hw hr]) a [] [] ha

/-- Removing signed report premises: they change old-language verdicts by
exactly the disequalities they force. -/
theorem reports_no_leak (D : ReportDoc) (h : WellFormedReports D = true) (Γ : List VE.Formula)
    (φ : VE.Formula) (hΓ : ∀ a ∈ Γ, a.WellFormed D.E []) (hφ : φ.WellFormed D.E [])
    (R : List VE.Formula) (hR : ∀ a ∈ R, SignedAtom D a) :
    VE.Entails.{u} (envReports D) (Γ ++ R) φ ↔ VE.Entails.{u} D.E (Γ ++ neqs R) φ := by
  have hw := wf_of h
  constructor
  · intro he S₀ h₀ hs
    have hsΓ : ∀ a ∈ Γ, a.denote S₀ [] := fun a ha => hs a (List.mem_append_left _ ha)
    have hsN : ∀ a ∈ neqs R, a.denote S₀ [] := fun a ha => hs a (List.mem_append_right _ ha)
    apply (expandBy_old hw R S₀ φ hφ).mp
    apply he
    · refine ⟨fun c s hc => h₀.1 c s hc, fun p vs hp => ?_⟩
      by_cases hn : p ∈ names D
      · have hp' : ∃ h v, VE.Formula.unary p (.const h) ∈ R ∧ S₀.constant h = some v ∧ vs = [v] := by
          simpa [expandBy, hn] using hp
        obtain ⟨hd, v, hm, hv, rfl⟩ := hp'
        obtain ⟨r, _, g, ⟨s, hs, hg⟩, he'⟩ := hR _ hm
        rcases he' with he' | he'
        · simp only [VE.Formula.unary.injEq, VE.Term.const.injEq] at he'
          obtain ⟨rfl, rfl⟩ := he'
          obtain ⟨v', hv', hd'⟩ := h₀.1 _ _ hg
          rw [hv] at hv'; cases hv'
          exact ⟨[s], hs, hd', trivial⟩
        · cases he'
      · have hp' : S₀.relation p vs := by simpa [expandBy, hn] using hp
        obtain ⟨ss, hss, ht⟩ := h₀.2 p vs hp'
        exact ⟨ss, by rw [envReports_pred_old hn]; exact hss,
          (VE.Route.Examples.tupleTyped_relation S₀ _ ss vs).mpr ht⟩
    · intro a ha
      rcases List.mem_append.mp ha with ha | ha
      · exact (expandBy_old hw R S₀ a (hΓ a ha)).mpr (hsΓ a ha)
      · obtain ⟨r, hr, g, ⟨s, _, hg⟩, rfl | rfl⟩ := hR a ha
        · obtain ⟨v, hv, _⟩ := h₀.1 _ _ hg
          refine (denote_atom _ r g).mpr ⟨v, hv, ?_⟩
          show if r ∈ names D then _ else _
          rw [if_pos hr]
          exact ⟨g, v, ha, hv, rfl⟩
        · intro hat
          obtain ⟨v, hv, hrel⟩ := (denote_atom _ r g).mp hat
          have hrel' : ∃ h v', VE.Formula.unary r (.const h) ∈ R ∧ S₀.constant h = some v' ∧ [v] = [v'] := by
            simpa [expandBy, hr] using hrel
          obtain ⟨h₁, v₁, hm₁, hv₁, hvv⟩ := hrel'
          simp only [List.cons.injEq, and_true] at hvv
          subst hvv
          exact hsN _ (mem_neqs.mpr ⟨r, h₁, g, hm₁, ha, rfl⟩) ⟨v, hv₁, hv⟩
  · intro he S' hS hs
    have hsΓ : ∀ a ∈ Γ, a.denote S' [] := fun a ha => hs a (List.mem_append_left _ ha)
    have hsR : fol.Sat S' R := fun a ha => hs a (List.mem_append_right _ ha)
    apply (forget_denote hw S' φ hφ).mp
    apply he _ (restrictJ_admissible D h S' hS)
    intro a ha
    rcases List.mem_append.mp ha with ha | ha
    · exact (forget_denote hw S' a (hΓ a ha)).mpr (hsΓ a ha)
    · exact (neqs_denote_congr ha S' _).mpr (neqs_sat_of_sat S' R hsR a ha)

theorem reports_no_leak_uniform (D : ReportDoc) (h : WellFormedReports D = true) (Γ : List VE.Formula)
    (φ : VE.Formula) (hΓ : ∀ a ∈ Γ, a.WellFormed D.E []) (hφ : φ.WellFormed D.E [])
    (R : List VE.Formula) (hR : ∀ a ∈ R, SignedAtom D a) (hu : UniformPolarity R) :
    VE.Entails.{u} (envReports D) (Γ ++ R) φ ↔ VE.Entails.{u} D.E Γ φ := by
  rw [reports_no_leak D h Γ φ hΓ hφ R hR, uniform_neqs R hu, List.append_nil]

end VE.Reports
