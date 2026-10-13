import ResponseShape.Encoders.SoftNorms

/-! The `rights` mode (`Rights.Run.runCaseReported`) against `rights.json#/row`. A case off the
rights path is the soft-norms mode's. -/

namespace ResponseShape.Encoders.Rights
open Lean ResponseShape ResponseShape.Skeletons
open VE.Rights VE.Rights.Run VE.Rights.Wire

variable {req : Json}

/-- Every newly generated rights predicate has the environment's predicate-entry shape. -/
theorem generated_entries_fit (D : RightsDoc) :
    ∀ p ∈ genEntries D,
      Fits req (skel% "common.json#/$defs/environment_predicate") p.2 := by
  intro p hp
  by_cases hb : D.bars = []
  · simp only [genEntries, hb, ↓reduceIte, List.append_nil, List.mem_append, List.mem_map] at hp
    rcases hp with ⟨a, _, he⟩ | ⟨a, _, he⟩
    · rw [← congrArg Prod.snd he]
      exact Common.generatedEntry_fits _ _ _
    · rw [← congrArg Prod.snd he]
      exact Common.generatedEntry_fits _ _ _
  · simp only [genEntries, hb, ↓reduceIte, List.mem_append, List.mem_map] at hp
    rcases hp with hp | ⟨a, _, he⟩
    · rcases hp with ⟨a, _, he⟩ | ⟨a, _, he⟩
      · rw [← congrArg Prod.snd he]
        exact Common.generatedEntry_fits _ _ _
      · rw [← congrArg Prod.snd he]
        exact Common.generatedEntry_fits _ _ _
    · rw [← congrArg Prod.snd he]
      exact Common.generatedEntry_fits _ _ _

/-- The rights elaboration's environment field is its rights prime environment. -/
theorem regenerated_environment (D : RightsDoc) (env : Json) :
    (regenerated D env).lookup "environment_prime" =
      some ((primeJsonR D env).toOption.getD .null) := by
  rfl

/-- The soft-norms mode's rows, off the rights path, are rows of this mode. -/
theorem of_softNorms {v : Json} (hp : usesRightsPath req = false) (h : Fits req Skeletons.softNorms v) :
    Fits req Skeletons.rights v :=
  Fits.onCaseE (by simpa [CaseCond.holds, CaseDecider.fn] using hp) h

/-- Every limitation premise label is a nonempty `rights:limitation:...` label. -/
theorem limLabels_nonempty (D : RightsDoc) : ∀ x ∈ limPremisesLabelled D, x.1.isEmpty = false := by
  intro x hx
  simp only [limPremisesLabelled, List.mem_filterMap] at hx
  obtain ⟨k, _, hk⟩ := hx
  unfold keyPremise at hk
  split at hk
  · cases hk
  · split at hk
    · cases hk
    · cases hk
      simp +decide [isEmpty_append, toString]

theorem labelled_contra {l : List (String × VE.Formula)} {x : String × VE.Formula}
    (hl : ∀ y ∈ l, y.1.isEmpty = false) (hx : x ∈ l) (h : x.1.isEmpty = true) : False := by
  simp [hl x hx] at h

theorem firstFailure_of_not_free (j : Json) (res : RightsConflictReplay) (h : replayRightsConflict j = .ok res)
    (hf : res.conflictFree = false) : (firstFailure res).isSome = true := by
  unfold replayRightsConflict at h
  obtain ⟨env, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨src, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  cases h
  simp only [RightsConflictReplay.conflictFree, rightsConflictFreeCheck, List.length_map, beq_self_eq_true,
    Bool.true_and, List.all_eq_false] at hf
  obtain ⟨⟨t, c⟩, hm, hc⟩ := hf
  simp only [firstFailure, Option.isSome_map]
  rw [List.find?_isSome]
  exact ⟨(t, c), hm, by cases c <;> simp_all⟩

theorem elaborate_fits (id : String) (D : RightsDoc) (env doc : Json) (openNames : List String) :
    Fits req (skel% "rights.json#/$defs/elaborate")
      (VE.Route.Wire.ok id (regenerated D env ++ [("unit_open", unitStatuses D openNames doc)])) := by
  unfold VE.Route.Wire.ok regenerated VE.SoftNorms.Wire.regeneratedCore VE.SoftNorms.Wire.bgEntry generatedKeys
    lineJson nodeJson narrowingsJson distinctionJson
  simp only [List.filter_cons, List.filter_nil, String.reduceBNe, Bool.false_eq_true, ↓reduceIte]
  fits using SoftNorms.decisionKeyJson_fits
  all_goals try first
    | exact Fits.rightsEnvironment D env (generated_entries_fit D)
        (fun p _ => Common.decisionEntry_fits p.2) rfl
    | exact (labelled_contra (limLabels_nonempty D) ‹_› ‹_›).elim
    | exact (labelled_contra (SoftNorms.softLabelledIn_nonempty _ _ _) ‹_› ‹_›).elim

theorem projections_fits (id : String) (src : RightsSource) (j : Json) :
    OkP (fun l => Fits req (skel% "rights.json#/$defs/projections") (VE.Route.Wire.ok id l)) (projectionsResult src j) := by
  unfold projectionsResult
  okfits
  simp only [VE.Route.Wire.ok, entryJson]
  fits

theorem bar_fits (id : String) (src : RightsSource) (environment document certs : Json) :
    Fits req (skel% "rights.json#/$defs/bar") (VE.Route.Wire.ok id (barResult src environment document certs)) := by
  unfold VE.Route.Wire.ok barResult
  simp only []
  fits

theorem admission_fits (id reportId : String) (res : Admission.Admitted) :
    Fits req (skel% "rights.json#/$defs/admission") (encodeAdmitted id reportId res) := by
  unfold encodeAdmitted VE.Route.Wire.ok
  fits
  all_goals exact Common.claimJson_fits _

theorem runRightsKind_fits (id kind : String) (j : Json) {w : Json} (hobj : j.getObjVal? "id" = .ok w)
    (hp : usesRightsPath j = true) (hK : KindRead "evaluate" j kind) :
    OkFits j Skeletons.rights (runRightsKind id kind j) := by
  unfold runRightsKind
  simp only []
  rcases hK with hK | ⟨hK, hd⟩
  all_goals (try subst hd)
  all_goals okfits
  all_goals kind_norm
  all_goals first
    | (unfold runAdmission; okfits; fits_from admission_fits _ _ _)
    | fits_from elaborate_fits _ _ _ _ _
    | (have h := projections_fits (req := j) id _ j _ ‹projectionsResult _ j = .ok _›
       simp only [VE.Route.Wire.ok, List.cons_append, List.nil_append] at h
       fits_from h)
    | fits_from bar_fits _ _ _ _ _
    | ((try simp only [VE.Route.Wire.ok]); fits)
  -- Not conflict-free with no failing target: impossible (`firstFailure_of_not_free`).
  all_goals
    exfalso
    have := firstFailure_of_not_free j _ ‹replayRightsConflict j = .ok _› (by simp_all)
    simp_all

theorem runCase_fits (j : Json) (hp : usesRightsPath j = true) : OkFits j Skeletons.rights (runCase j) := by
  unfold runCase
  okfits
  all_goals first
    | (exfalso; simp_all; done)
    | read_kind
  all_goals first
    | exact runRightsKind_fits _ _ _ ‹_› hp (KindRead.of_str ‹_›)
    | exact runRightsKind_fits _ _ _ ‹_› hp (Or.inr ⟨‹_›, rfl⟩)

theorem runCaseReported_fits (j : Json) (hj : CaseWF j) : Fits j Skeletons.rights (runCaseReported j) := by
  unfold runCaseReported
  split
  · split
    · exact runCase_fits j ‹_› _ ‹_›
    · fits
  · exact of_softNorms (Bool.eq_false_iff.mpr ‹_›) (SoftNorms.runCaseReported_fits j hj)

end ResponseShape.Encoders.Rights
