import VE.Attribution.Structure

/-! Spec 9.3, the route: P0's FOL route at `E_reports` (`Layer.id`, whose
`Intended` is `True`) with the signed report premises as document premises,
composed with `reports_elaboration_faithful` for the meaning, with
`reports_no_leak` for the old-language reading, and with finite witness
decoding for countermodels. -/
namespace VE.Reports
open VE.Route (fol)
open VE.Route.Background (StringAdmissible LiteralsDistinct literals literalsValid folLayer EntailsString)
open VE.Definitions (forget hide)
universe u

/-- The reports route is the FOL route at E_reports: P0's `Layer.id`. -/
theorem reportsRoute_premises (D : ReportDoc) : (reportsRoute.{u} D).premises () = [] := rfl

theorem entails_congr_mem {E : VE.Environment} {l l' : List VE.Formula} {φ : VE.Formula}
    (hl : ∀ a, a ∈ l ↔ a ∈ l') : VE.Entails.{u} E l φ ↔ VE.Entails.{u} E l' φ :=
  ⟨fun h S hS hs => h S hS (fun a ha => hs a ((hl a).mp ha)),
   fun h S hS hs => h S hS (fun a ha => hs a ((hl a).mpr ha))⟩

/-- The literal distinctness premises are old-language formulas. -/
theorem literals_wellFormed {D : ReportDoc} (hw : WF D) : ∀ a ∈ literals D.lits, a.WellFormed D.E [] := by
  intro a ha
  obtain ⟨p, hp, rfl⟩ := List.mem_map.mp ha
  obtain ⟨h1, h2, _⟩ := VE.Route.Background.mem_pairs hp
  have e1 := hw.lits _ ((VE.Route.Background.mem_sortStrings _ _).mp h1)
  have e2 := hw.lits _ ((VE.Route.Background.mem_sortStrings _ _).mp h2)
  simp only [beq_iff_eq] at e1 e2
  exact ⟨VE.Route.Background.stringSort, e1, e2⟩

/-- 4.4: fol_route_acceptance at E_reports with Γ_reports ++ Γ as the document
premises, then transported to source models by reports_elaboration_faithful_out
and reports_elaboration_faithful. -/
theorem reports_route_acceptance (D : ReportDoc) (h : WellFormedReports D = true) (hn : D.lits.Nodup)
    (Γ : List VE.Formula) (φ : VE.Formula) (c : VE.Tableau.Certificate)
    (accepted : VE.Tableau.checkCertificate (envReports D) (checkedList D Γ) φ c = true) :
    VE.Entails.{u} (envReports D) (checkedList D Γ) φ ∧
    EntailsString.{u} (envReports D) D.lits (premises D ++ Γ) φ ∧
    (∀ S' : VE.Structure.{u}, StringAdmissible (envReports D) D.lits S' →
       IntendedReports D (restrictJ D S') → fol.Sat S' Γ → φ.denote S' []) ∧
    (∀ M : Source.{u} D, StringAdmissible D.E D.lits M.S → IntendedReports D M →
       fol.Sat (interp D M) Γ → φ.denote (interp D M) []) := by
  have hw := wf_of h
  have he : VE.Entails.{u} (envReports D) (checkedList D Γ) φ :=
    VE.Tableau.checkCertificate_sound _ _ φ c accepted
  have hs : EntailsString.{u} (envReports D) D.lits (premises D ++ Γ) φ :=
    (VE.Route.Background.fol_route_acceptance (envReports D) D.lits hn (premises D ++ Γ) φ c
      (by simpa [checkedList, List.append_assoc] using accepted)).2
  refine ⟨he, hs, ?_, ?_⟩
  · intro S' hS hi hΓ
    have hp := (reports_elaboration_faithful_out D h S' hS.1).mpr hi
    exact hs S' hS (fun a ha => (List.mem_append.mp ha).elim (hp a) (hΓ a))
  · intro M hM hi hΓ
    obtain ⟨ha, hf⟩ := reports_elaboration_faithful D h M hM.1
    exact hs (interp D M) ⟨ha, hM.2⟩ (fun a hm => (List.mem_append.mp hm).elim (hf.mpr hi a) (hΓ a))

/-- The old-language reading: for Γ and φ over E the signed report atoms add
exactly the disequalities they force. -/
theorem reports_route_acceptance_base (D : ReportDoc) (h : WellFormedReports D = true) (hn : D.lits.Nodup)
    (Γ : List VE.Formula) (φ : VE.Formula) (c : VE.Tableau.Certificate)
    (accepted : VE.Tableau.checkCertificate (envReports D) (checkedList D Γ) φ c = true)
    (hΓ : ∀ a ∈ Γ, a.WellFormed D.E []) (hφ : φ.WellFormed D.E []) :
    VE.Entails.{u} D.E (literals D.lits ++ neqs (premises D) ++ Γ) φ ∧
    EntailsString.{u} D.E D.lits (neqs (premises D) ++ Γ) φ := by
  have hw := wf_of h
  have he := (reports_route_acceptance.{u} D h hn Γ φ c accepted).1
  have hΓ' : ∀ a ∈ literals D.lits ++ Γ, a.WellFormed D.E [] := fun a ha =>
    (List.mem_append.mp ha).elim (literals_wellFormed hw a) (hΓ a)
  have he' : VE.Entails.{u} (envReports D) ((literals D.lits ++ Γ) ++ premises D) φ :=
    (entails_congr_mem (fun a => by simp [checkedList, or_comm])).mp he
  have hb := (reports_no_leak D h _ φ hΓ' hφ (premises D) (premises_signed D h)).mp he'
  have hb' : VE.Entails.{u} D.E (literals D.lits ++ neqs (premises D) ++ Γ) φ :=
    (entails_congr_mem (fun a => by simp [or_comm])).mp hb
  refine ⟨hb', ?_⟩
  exact (VE.Route.Background.fol_route_entails_iff D.E D.lits hn _ φ).mp (by simpa [List.append_assoc] using hb')

/-- A positive document, or one whose old-language premises already entail the
disequalities, recovers the plain old-language statement. -/
theorem reports_route_acceptance_base_positive (D : ReportDoc) (h : WellFormedReports D = true)
    (hn : D.lits.Nodup) (Γ : List VE.Formula) (φ : VE.Formula) (c : VE.Tableau.Certificate)
    (accepted : VE.Tableau.checkCertificate (envReports D) (checkedList D Γ) φ c = true)
    (hΓ : ∀ a ∈ Γ, a.WellFormed D.E []) (hφ : φ.WellFormed D.E [])
    (hp : Positive D ∨ ∀ a ∈ neqs (premises D), VE.Entails.{u} D.E (literals D.lits ++ Γ) a) :
    VE.Entails.{u} D.E (literals D.lits ++ Γ) φ ∧ EntailsString.{u} D.E D.lits Γ φ := by
  have hb := (reports_route_acceptance_base.{u} D h hn Γ φ c accepted hΓ hφ).1
  have he : VE.Entails.{u} D.E (literals D.lits ++ Γ) φ := by
    intro S hS hs
    apply hb S hS
    intro a ha
    simp only [List.mem_append] at ha
    rcases ha with (ha | ha) | ha
    · exact hs a (List.mem_append_left _ ha)
    · rcases hp with hp | hp
      · rw [uniform_neqs _ (positive_uniform D h hp)] at ha; nomatch ha
      · exact hp a ha S hS hs
    · exact hs a (List.mem_append_right _ ha)
  exact ⟨he, (VE.Route.Background.fol_route_entails_iff D.E D.lits hn Γ φ).mp he⟩

/-- A checked finite countermodel over E_reports refutes the route statement and
decodes to a source model of the document in which Γ holds and φ fails. -/
theorem reports_route_countermodel {α : Type u} [DecidableEq α] (D : ReportDoc) (h : WellFormedReports D = true)
    (hn : D.lits.Nodup) (Γ : List VE.Formula) (φ : VE.Formula)
    (Mo : VE.FiniteModel α) (valid : Mo.Valid (envReports D)) (hl : literalsValid Mo D.lits = true)
    (checked : VE.countermodelCheck Mo (premises D ++ Γ) φ = true) :
    ¬ EntailsString.{u} (envReports D) D.lits (premises D ++ Γ) φ ∧
    ¬ VE.Entails.{u} (envReports D) (checkedList D Γ) φ ∧
    ∃ M : Source.{u} D, IntendedReports D M ∧ fol.Sat (interp D M) Γ ∧ ¬ φ.denote (interp D M) [] := by
  obtain ⟨h1, h2⟩ := VE.Route.Background.fol_route_countermodel (envReports D) D.lits hn Mo valid hl
    (premises D ++ Γ) φ checked
  obtain ⟨hp, hc⟩ := (VE.countermodelCheck_iff Mo _ φ).mp checked
  refine ⟨h1, by simpa [checkedList, List.append_assoc] using h2, restrictJ D Mo.asStructure, ?_, ?_, ?_⟩
  · exact (reports_elaboration_faithful_out D h _ valid).mp
      (fun a ha => hp a (List.mem_append_left _ ha))
  · rw [interp_restrict_eq D h _ valid]
    exact fun a ha => hp a (List.mem_append_right _ ha)
  · rw [interp_restrict_eq D h _ valid]
    exact hc

end VE.Reports
