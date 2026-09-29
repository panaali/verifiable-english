import VE.Attribution.Route

/-! Spec 9.3, scoped checks (5.1): a consequence among selected reported
contents, computed at the payloads' own environment under its own route
Background, is a report line and never a premise; a quoted package's
definition premises stay local; an inconsistent payload set makes nothing
outside vacuous. -/
namespace VE.Reports
open VE.Route (fol)
open VE.Route.Background (literals)
universe u

/-- 5.1: at the payloads' environment under its own route background, at every universe. -/
theorem scoped_consequence_sound (D : ReportDoc) (h : WellFormedReports D = true) (s : ScopedCheck)
    (hs : s ∈ D.«scoped») (Eq : Pinned) (ps : List VE.Formula)
    (hp : payloadFormulas D s = some (Eq, ps)) (c : VE.Tableau.Certificate)
    (acc : VE.Tableau.checkCertificate Eq (background Eq ++ ps) s.conclusion c = true) :
    VE.Entails.{u} Eq (background Eq ++ ps) s.conclusion :=
  VE.Tableau.checkCertificate_sound _ _ _ c acc

theorem scoped_witness_sound {α : Type u} [DecidableEq α] (D : ReportDoc) (h : WellFormedReports D = true)
    (s : ScopedCheck) (hs : s ∈ D.«scoped») (Eq : Pinned) (ps : List VE.Formula)
    (hp : payloadFormulas D s = some (Eq, ps)) (Mo : VE.FiniteModel α)
    (valid : Mo.Valid Eq) (hb : ∀ a ∈ background Eq, a.eval Mo [] = true)
    (hps : ∀ a ∈ ps, a.eval Mo [] = true) (hn : s.conclusion.eval Mo [] = false) :
    ¬ VE.Entails.{u} Eq (background Eq ++ ps) s.conclusion := by
  apply VE.countermodel_sound Mo valid
  simp only [VE.countermodelCheck, Bool.and_eq_true, List.all_eq_true, Bool.not_eq_true']
  refine ⟨fun a ha => ?_, hn⟩
  rcases List.mem_append.mp ha with ha | ha
  · exact hb a ha
  · exact hps a ha

theorem scoped_free_canonicalObject (D : ReportDoc) :
    canonicalObject { D with «scoped» := [] } = canonicalObject D := by
  funext x; induction x <;> simp_all [canonicalObject, contextObject, recordObject, contextOf, recordOf]

theorem scoped_free_contentId (D : ReportDoc) : contentId { D with «scoped» := [] } = contentId D := by
  funext x; simp only [contentId, digestOf, identityVersion, scoped_free_canonicalObject]

theorem scoped_free_complementId (D : ReportDoc) : complementId { D with «scoped» := [] } = complementId D := by
  funext b l; simp only [complementId, complementObject, digestOf, identityVersion, scoped_free_canonicalObject]

theorem scoped_free_keys (D : ReportDoc) : keys { D with «scoped» := [] } = keys D := by
  have : reportKeyOf { D with «scoped» := [] } = reportKeyOf D := by
    funext x; cases x <;> simp [reportKeyOf, holderSort, scoped_free_complementId]
  simp only [keys, allNodes, this]

theorem scoped_free_akeys (D : ReportDoc) : akeys { D with «scoped» := [] } = akeys D := by
  have : assessKeyOf { D with «scoped» := [] } = assessKeyOf D := by
    funext x; cases x <;> simp [assessKeyOf, scoped_free_contentId]
  simp only [akeys, allNodes, this]

theorem scoped_free_elab (D : ReportDoc) : «elab» { D with «scoped» := [] } = «elab» D := by
  funext x
  induction x <;> simp_all [«elab», holderSort, recordOf, reportName, assessName, scoped_free_keys,
    scoped_free_akeys, scoped_free_complementId, scoped_free_contentId]

/-- A scoped check is not in Γ and not in E_reports. -/
theorem scoped_not_premise (D : ReportDoc) (h : WellFormedReports D = true) :
    premises D = premises { D with «scoped» := [] } ∧ envReports D = envReports { D with «scoped» := [] } :=
  ⟨by
    have : unitPremise { D with «scoped» := [] } = unitPremise D := by
      funext u; simp only [unitPremise, scoped_free_elab]
    simp only [premises, this],
   by simp only [envReports, keyOf, reportName, assessName, scoped_free_keys, scoped_free_akeys]⟩

/-- A definition premise is a universally closed or plain conjunction, never a
negation or an atom. -/
theorem def_premise_shape (d : VE.Definitions.Def) :
    (∃ s b, d.premise = .all s b) ∨ (∃ a b, d.premise = .and a b) := by
  unfold VE.Definitions.Def.premise
  cases d.args with
  | nil => exact Or.inr ⟨_, _, rfl⟩
  | cons s ss => exact Or.inl ⟨_, _, rfl⟩

/-- A quoted package's definition premises are local to the check: none is
inserted into the document's checked list. -/
theorem scoped_background_local (D : ReportDoc) (h : WellFormedReports D = true) (Eq : Pinned)
    (ds : List VE.Definitions.Def) (st : Option VE.Formula)
    (hq : Occurs D (.definition Eq ds st)) (Γ : List VE.Formula) :
    ∀ a ∈ VE.Definitions.expand ds, a ∉ literals D.lits ++ premises D ∧ (a ∈ checkedList D Γ → a ∈ Γ) := by
  have hw := wf_of h
  intro a ha
  obtain ⟨d, _, rfl⟩ := List.mem_map.mp ha
  have hnot : d.premise ∉ literals D.lits ++ premises D := by
    intro hm
    rcases List.mem_append.mp hm with hm | hm
    · obtain ⟨p, _, hp⟩ := List.mem_map.mp hm
      rcases def_premise_shape d with ⟨_, _, he⟩ | ⟨_, _, he⟩ <;> rw [he] at hp <;> cases hp
    · obtain ⟨u, hu, hp⟩ := mem_premises.mp hm
      rcases def_premise_shape d with ⟨_, _, he⟩ | ⟨_, _, he⟩ <;> rw [he] at hp <;>
      rcases unit_shape hw hu with ⟨_, _, _, _, _, _, _, _, hp'⟩ | ⟨_, _, _, _, _, _, hp'⟩ |
        ⟨_, _, _, _, _, _, _, _, hp'⟩ | ⟨_, _, _, _, _, _, hp'⟩ <;> rw [hp'] at hp <;> cases hp
  refine ⟨hnot, fun hm => ?_⟩
  unfold checkedList at hm
  rcases List.mem_append.mp hm with hm | hm
  · exact absurd hm hnot
  · exact hm

theorem quoted_inconsistency_local (D : ReportDoc) (h : WellFormedReports D = true) (s : ScopedCheck)
    (hs : s ∈ D.«scoped») (Eq : Pinned) (ps : List VE.Formula)
    (hp : payloadFormulas D s = some (Eq, ps)) (c : VE.Tableau.Certificate)
    (acc : VE.Tableau.checkCertificate Eq (background Eq ++ ps) .bottom c = true) :
    (∀ S : VE.Structure.{u}, S.Admissible Eq → fol.Sat S (background Eq) → ¬ fol.Sat S ps) ∧
    ∀ S₀ : VE.Structure.{u}, S₀.Admissible D.E → Expandable D S₀ →
      ∃ M : Source.{u} D, M.S = S₀ ∧ IntendedReports D M := by
  have he : VE.Entails.{u} Eq (background Eq ++ ps) .bottom := VE.Tableau.checkCertificate_sound _ _ _ c acc
  refine ⟨fun S hS hb hps => he S hS (fun a ha => ?_), fun S₀ h₀ hx => source_over_any_structure D h S₀ h₀ hx⟩
  rcases List.mem_append.mp ha with ha | ha
  · exact hb a ha
  · exact hps a ha

end VE.Reports
