import ResponseShape.Encoders.SoftNorms

/-! The `rights` mode (`Rights.Run.runCaseReported`) against `rights.json#/row`. A case off the
rights path is the soft-norms mode's. -/

namespace ResponseShape.Encoders.Rights
open Lean ResponseShape ResponseShape.Skeletons
open VE.Rights VE.Rights.Run VE.Rights.Wire

variable {req : Json}

theorem of_softNorms {v : Json} (h : Fits req Skeletons.softNorms v) : Fits req Skeletons.rights v := by
  refine Fits.altSub ?_ h
  alt_sub

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

theorem elaborate_fits (id : String) (D : RightsDoc) (env : Json) :
    Fits req (skel% "rights.json#/$defs/elaborate") (VE.Route.Wire.ok id (regenerated D env)) := by
  unfold VE.Route.Wire.ok regenerated VE.SoftNorms.Wire.regenerated VE.SoftNorms.Wire.bgEntry generatedKeys
    lineJson nodeJson narrowingsJson distinctionJson
  simp only [List.filter_cons, List.filter_nil, String.reduceBNe, Bool.false_eq_true, ↓reduceIte]
  fits
  all_goals try first
    | exact (labelled_contra (limLabels_nonempty D) ‹_› ‹_›).elim
    | exact (labelled_contra (SoftNorms.softLabelled_nonempty _) ‹_› ‹_›).elim

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

theorem runRightsKind_fits (id kind : String) (j : Json) :
    OkFits req Skeletons.rights (runRightsKind id kind j) := by
  unfold runRightsKind
  simp only []
  okfits
  all_goals first
    | (unfold runAdmission; okfits; fits_as "rights.json#/$defs/admission"; exact admission_fits _ _ _)
    | (fits_as "rights.json#/$defs/elaborate"; with_reducible exact elaborate_fits _ _ _)
    | (fits_as "rights.json#/$defs/projections"
       have h := projections_fits (req := req) id _ j _ ‹projectionsResult _ j = .ok _›
       simp only [VE.Route.Wire.ok, List.cons_append, List.nil_append] at h
       exact h)
    | (fits_as "rights.json#/$defs/bar"; with_reducible exact bar_fits _ _ _ _ _)
    | skip
  all_goals (try simp only [VE.Route.Wire.ok])
  all_goals fits
  -- Not conflict-free with no failing target: impossible (`firstFailure_of_not_free`).
  all_goals
    exfalso
    have := firstFailure_of_not_free j _ ‹replayRightsConflict j = .ok _› (by simp_all)
    simp_all

theorem runCase_fits (j : Json) : OkFits req Skeletons.rights (runCase j) := by
  unfold runCase
  okfits
  · exact OkP.of (SoftNorms.runCase_fits j) fun _ => of_softNorms
  · exact runRightsKind_fits _ _ _

theorem runCaseReported_fits (j : Json) : Fits j Skeletons.rights (runCaseReported j) := by
  unfold runCaseReported
  split
  · split
    · exact runCase_fits j _ ‹_›
    · fits
  · exact of_softNorms (SoftNorms.runCaseReported_fits j)

end ResponseShape.Encoders.Rights
