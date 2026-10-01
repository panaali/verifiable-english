import VE.Attribution.Conservative

/-! Spec 9.2, the structure theorems of 4.5: non-factivity, non-closure, nested
independence, the five nested-content theorems on the holder-applied signed
atom, the identity theorems on canonical objects (digest and name conclusions
under the occurrence of both compared objects), and truth combinations over
unasserted keys. -/
namespace VE.Reports
open VE.Route (fol)
open VE.Definitions (forget hide)
universe u

/-- A formula node that occurs in a well-formed document is closed and typed over E. -/
theorem occurs_formula_wellFormed {D : ReportDoc} (hw : WF D) {q : VE.Formula}
    (ho : Occurs D (.formula q)) : q.WellFormed D.E [] :=
  (VE.check_iff_wellFormed D.E [] q).mp (nodeOk_of_occurs hw ho)

/-- 4.5: not factive. -/
theorem attitude_not_factive (D : ReportDoc) (h : WellFormedReports D = true) (u : Unit) (hu : u ∈ D.units)
    (hd c : String) (act : Act) (q : VE.Formula) (lit : Option String)
    (hb : u.content = .report hd act c (.formula q) lit)
    (S₀ : VE.Structure.{u}) (h₀ : S₀.Admissible D.E) (he : Expandable D S₀) (hn : ¬ q.denote S₀ []) :
    ∃ M : Source.{u} D, M.S = S₀ ∧ IntendedReports D M ∧ ¬ q.denote (interp D M) [] := by
  have hq : q.WellFormed D.E [] := occurs_formula_wellFormed (wf_of h)
    ⟨u, hu, by rw [hb]; exact body_mem_report⟩
  obtain ⟨M, hM, hi⟩ := source_over_any_structure D h S₀ h₀ he
  refine ⟨M, hM, hi, fun hq' => hn ?_⟩
  rw [← hM]
  exact (old_formula_invariant D h M q hq).mp hq'

/-- 4.5: belief is not closed under consequence. -/
theorem no_closure_under_consequence (D : ReportDoc) (h : WellFormedReports D = true) (hd c s : String)
    (P Q : VE.Formula)
    (hb : beliefsIn D hd c P (.implies P Q)) (hs : holderSort D hd = some s)
    (hQ : ⟨.believes, s, c, complementId D (.formula Q) none⟩ ∉ topKeys D)
    (S₀ : VE.Structure.{u}) (h₀ : S₀.Admissible D.E) (he : Expandable D S₀) :
    ∃ M : Source.{u} D, M.S = S₀ ∧ IntendedReports D M ∧
      ∀ v, ¬ M.J .believes s c (complementId D (.formula Q) none) v :=
  unreported_key_free D h S₀ h₀ he _ hQ

/-- 4.5: nested independence. -/
theorem nested_independent (D : ReportDoc) (h : WellFormedReports D = true) (u : Unit) (hu : u ∈ D.units)
    (h₁ h₂ c c' s₂ : String) (act : Act) (q : VE.Formula) (lit : Option String)
    (hb : u.content = .report h₁ act c (.report h₂ .believes c' (.formula q) none) lit)
    (hs₂ : holderSort D h₂ = some s₂)
    (hin : ⟨.believes, s₂, c', complementId D (.formula q) none⟩ ∉ topKeys D)
    (S₀ : VE.Structure.{u}) (h₀ : S₀.Admissible D.E) (he : Expandable D S₀) (hn : ¬ q.denote S₀ []) :
    ∃ M : Source.{u} D, M.S = S₀ ∧ IntendedReports D M ∧
      (∀ v, ¬ M.J .believes s₂ c' (complementId D (.formula q) none) v) ∧ ¬ q.denote (interp D M) [] := by
  have hq : q.WellFormed D.E [] := occurs_formula_wellFormed (wf_of h)
    ⟨u, hu, by rw [hb]; exact Content.nodes_trans body_mem_report body_mem_report⟩
  obtain ⟨M, hM, hi, hfree⟩ := unreported_key_free D h S₀ h₀ he _ hin
  refine ⟨M, hM, hi, hfree, fun hq' => hn ?_⟩
  rw [← hM]
  exact (old_formula_invariant D h M q hq).mp hq'

/-- The premise of a top-level unit is entailed by the report premises. -/
theorem premise_entailed {D : ReportDoc} {u' : Unit} (hu' : u' ∈ D.units) {φ : VE.Formula}
    (he : unitPremise D u' = some φ) : VE.Entails.{u} (envReports D) (premises D) φ :=
  fun _ _ hs => hs φ (unitPremise_mem hu' he)

/-- 4.5, nested contents: a top-level unit carrying the very node entails its atom. -/
theorem nested_positive_entailed (D : ReportDoc) (h : WellFormedReports D = true) (u u' : Unit)
    (hu : u ∈ D.units) (hu' : u' ∈ D.units) (n : Content)
    (hn : n ∈ u.content.nodes) (hr : n.isReport = true ∨ n.isAssessment = true) (hb' : u'.content = n)
    (φ : VE.Formula) (he : «elab» D n = some φ) :
    VE.Entails.{u} (envReports D) (premises D) φ :=
  premise_entailed hu' (by rw [unitPremise, hb', he])

/-- The opposite polarity at top level refutes the nested positive node (B₁₀). -/
theorem nested_positive_refuted (D : ReportDoc) (h : WellFormedReports D = true) (u u' : Unit)
    (hu : u ∈ D.units) (hu' : u' ∈ D.units) (n : Content)
    (hn : n ∈ u.content.nodes) (hr : n.isReport = true ∨ n.isAssessment = true)
    (hb' : u'.content = .negated n) (φ : VE.Formula) (he : «elab» D n = some φ) :
    VE.Entails.{u} (envReports D) (premises D) (.not φ) :=
  premise_entailed hu' (by rw [unitPremise, hb']; simp [«elab», he])

/-- A negated nested node `¬n` elaborates to `¬φ`: entailed when a top-level
unit denies `n` (B₁₁). -/
theorem nested_negated_entailed (D : ReportDoc) (h : WellFormedReports D = true) (u u' : Unit)
    (hu : u ∈ D.units) (hu' : u' ∈ D.units) (n : Content)
    (hn : .negated n ∈ u.content.nodes) (hr : n.isReport = true ∨ n.isAssessment = true)
    (hb' : u'.content = .negated n) (φ : VE.Formula) (he : «elab» D n = some φ) :
    VE.Entails.{u} (envReports D) (premises D) (.not φ) :=
  premise_entailed hu' (by rw [unitPremise, hb']; simp [«elab», he])

/-- … refuted when a top-level unit asserts `n` (`D_ω`). -/
theorem nested_negated_refuted (D : ReportDoc) (h : WellFormedReports D = true) (u u' : Unit)
    (hu : u ∈ D.units) (hu' : u' ∈ D.units) (n : Content)
    (hn : .negated n ∈ u.content.nodes) (hr : n.isReport = true ∨ n.isAssessment = true)
    (hb' : u'.content = n) (φ : VE.Formula) (he : «elab» D n = some φ) :
    VE.Entails.{u} (envReports D) (premises D) φ :=
  premise_entailed hu' (by rw [unitPremise, hb', he])

/-- The holder-applied atom of a report key `k` at a holder `hd` is free when no
positive top-level premise carries that atom at a holder co-denoting with `hd`.
The spec's conclusion reads `S₀.constant hd = some v` for `v : M.S.Carrier`,
which does not typecheck for an existential `M`; it reads `M.S.constant` here,
the same constant under `M.S = S₀` (lean/REPORTS.md, deviations). -/
theorem holder_atom_free (D : ReportDoc) (h : WellFormedReports D = true) (k : ReportKey) (hk : k ∈ keys D)
    (hd : String) (hs : holderSort D hd = some k.sort)
    (S₀ : VE.Structure.{u}) (h₀ : S₀.Admissible D.E) (he : Expandable D S₀)
    (hfree : ∀ h', .unary (reportName D k) (.const h') ∈ premises D → S₀.constant h' ≠ S₀.constant hd) :
    ∃ M : Source.{u} D, M.S = S₀ ∧ IntendedReports D M ∧
      ∀ v, M.S.constant hd = some v → ¬ M.J k.act k.sort k.ctx k.content v := by
  refine ⟨mkSource D (wf_of h) S₀ h₀ (fun _ _ => False) (fun _ _ => False), rfl,
    mkSource_intended D (wf_of h) S₀ h₀ he _ _, ?_⟩
  rintro v hv (ha | ⟨_, _, hf⟩)
  · obtain ⟨h₁, hp₁, hv₁⟩ := assertedJ_premise ha
    exact hfree h₁ hp₁ (by rw [hv₁]; exact hv.symm)
  · exact hf

/-! ## Identity theorems on canonical objects -/

theorem optField_inj {k : String} {l l' : Option String} (h : optField k l = optField k l') : l = l' := by
  cases l <;> cases l' <;> simp_all [optField]

theorem complementObject_inj {D : ReportDoc} {b b' : Content} {l l' : Option String}
    (h : complementObject D b l = complementObject D b' l') :
    canonicalObject D b = canonicalObject D b' ∧ l = l' := by
  have h' := CJson.o_inj h
  simp only [List.cons_append, List.nil_append, List.cons.injEq, Prod.mk.injEq, true_and] at h'
  exact ⟨h'.1, optField_inj h'.2⟩

theorem canonicalObject_formula_inj {D : ReportDoc} {φ ψ : VE.Formula}
    (h : canonicalObject D (.formula φ) = canonicalObject D (.formula ψ)) : φ = ψ := by
  have h' := CJson.o_inj h
  simp only [List.cons.injEq, Prod.mk.injEq, true_and, CJson.ast.injEq, and_true] at h'
  exact h'

theorem not_ne_self (q : VE.Formula) : VE.Formula.not q ≠ q := by
  intro h; have := congrArg sizeOf h; simp at this

theorem negation_scopes_distinct (D : ReportDoc) (h : WellFormedReports D = true) (hd₁ hd₂ c s : String)
    (q : VE.Formula)
    (hs₁ : holderSort D hd₁ = some s) (hs₂ : holderSort D hd₂ = some s)
    (ho : Occurs D (.report hd₁ .believes c (.formula (.not q)) none))
    (ho' : Occurs D (.report hd₂ .believes c (.formula q) none)) :
    complementObject D (.formula (.not q)) none ≠ complementObject D (.formula q) none ∧
    reportName D ⟨.believes, s, c, complementId D (.formula (.not q)) none⟩ ≠
      reportName D ⟨.believes, s, c, complementId D (.formula q) none⟩ := by
  have hobj : complementObject D (.formula (.not q)) none ≠ complementObject D (.formula q) none :=
    fun he => not_ne_self q (canonicalObject_formula_inj (complementObject_inj he).1)
  refine ⟨hobj, fun hn => hobj ?_⟩
  have hk := reportName_inj (wf_of h) (report_key_mem ho hs₁) (report_key_mem ho' hs₂) hn
  simp only [ReportKey.mk.injEq, true_and] at hk
  exact no_collision_complement D h _ _ _ _ ⟨_, _, _, ho⟩ ⟨_, _, _, ho'⟩ hk

theorem tense_keys_distinct (D : ReportDoc) (h : WellFormedReports D = true) (c c' : String)
    (hc : tenseOf D c ≠ tenseOf D c') (s q : String)
    (hk : ⟨.believes, s, c, q⟩ ∈ keys D) (hk' : ⟨.believes, s, c', q⟩ ∈ keys D) :
    reportName D ⟨.believes, s, c, q⟩ ≠ reportName D ⟨.believes, s, c', q⟩ := by
  intro hn
  have := reportName_inj (wf_of h) hk hk' hn
  simp only [ReportKey.mk.injEq, true_and, and_true] at this
  exact hc (by rw [this])

/-- Formula nodes over the author's E, the only bare formula nodes of a tree. -/
theorem content_structural (D : ReportDoc) (h : WellFormedReports D = true) (φ ψ : VE.Formula) :
    (canonicalObject D (.formula φ) = canonicalObject D (.formula ψ) ↔ canonical φ = canonical ψ) ∧
    (Occurs D (.formula φ) → Occurs D (.formula ψ) →
      (contentId D (.formula φ) = contentId D (.formula ψ) ↔ canonical φ = canonical ψ)) := by
  have hobj : canonicalObject D (.formula φ) = canonicalObject D (.formula ψ) ↔ canonical φ = canonical ψ :=
    ⟨canonicalObject_formula_inj, fun he => by
      simp only [canonical] at he; rw [he]⟩
  refine ⟨hobj, fun ho ho' => ⟨fun he => hobj.mp (no_collision D h _ _ ho ho' he), fun he => ?_⟩⟩
  simp only [canonical] at he
  rw [he]

theorem literal_paraphrase_distinct (D : ReportDoc) (h : WellFormedReports D = true) (b : Content)
    (l₁ l₂ : Option String) (hw : l₁ ≠ l₂) :
    complementObject D b l₁ ≠ complementObject D b l₂ ∧
    (OccursComplement D b l₁ → OccursComplement D b l₂ → complementId D b l₁ ≠ complementId D b l₂) := by
  have hobj : complementObject D b l₁ ≠ complementObject D b l₂ :=
    fun he => hw (complementObject_inj he).2
  exact ⟨hobj, fun ho ho' he => hobj (no_collision_complement D h _ _ _ _ ho ho' he)⟩

/-! ## Truth combinations over unasserted keys -/

/-- Truth combinations over unasserted keys, typed: only elements of the key's
sort are constrained. -/
theorem all_truth_combinations (D : ReportDoc) (h : WellFormedReports D = true) (ks : List ReportKey)
    (hk : ∀ k ∈ ks, k ∉ topKeys D) (f : ReportKey → Bool)
    (S₀ : VE.Structure.{u}) (h₀ : S₀.Admissible D.E) (he : Expandable D S₀) :
    ∃ M : Source.{u} D, M.S = S₀ ∧ IntendedReports D M ∧
      ∀ k ∈ ks, ∀ v, M.S.domain k.sort v → (M.J k.act k.sort k.ctx k.content v ↔ f k = true) := by
  refine ⟨mkSource D (wf_of h) S₀ h₀ (fun k _ => f k = true) (fun _ _ => False), rfl,
    mkSource_intended D (wf_of h) S₀ h₀ he _ _, fun k hks v hv => ?_⟩
  constructor
  · rintro (ha | ⟨_, _, hf⟩)
    · exact absurd (assertedJ_top ha) (hk k hks)
    · exact hf
  · intro hf
    exact Or.inr ⟨hk k hks, hv, hf⟩

theorem all_truth_combinations_assess (D : ReportDoc) (h : WellFormedReports D = true) (ks : List AssessKey)
    (hk : ∀ k ∈ ks, k ∉ topAKeys D)
    (f : AssessKey → Bool) (S₀ : VE.Structure.{u}) (h₀ : S₀.Admissible D.E) (he : Expandable D S₀) :
    ∃ M : Source.{u} D, M.S = S₀ ∧ IntendedReports D M ∧
      ∀ k ∈ ks, ∀ v, M.S.domain D.evidence v → (M.A k.j k.a k.content v ↔ f k = true) := by
  refine ⟨mkSource D (wf_of h) S₀ h₀ (fun _ _ => False) (fun k _ => f k = true), rfl,
    mkSource_intended D (wf_of h) S₀ h₀ he _ _, fun k hks v hv => ?_⟩
  constructor
  · rintro (ha | ⟨_, _, hf⟩)
    · exact absurd (assertedA_top ha) (hk k hks)
    · exact hf
  · intro hf
    exact Or.inr ⟨hk k hks, hv, hf⟩

end VE.Reports
