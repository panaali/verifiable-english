import ResponseShape.Encoders.Norms

/-! The `norm-defaults` mode (`NormDefaults.Run.runCaseReported`) against `norm-defaults.json#/row`.
A case off the norm-defaults path is the norms mode's. -/

namespace ResponseShape.Encoders.NormDefaults
open Lean ResponseShape ResponseShape.Skeletons
open VE.NormDefaults VE.NormDefaults.Run

variable {req : Json}

theorem of_norms {v : Json} (h : Fits req Skeletons.norms v) : Fits req Skeletons.normDefaults v := by
  refine Fits.altSub ?_ h
  alt_sub

theorem firstFailure_of_not_free (j : Json) (res : Wire.ConflictReplayU) (h : Wire.replayConflictU j = .ok res)
    (hf : res.conflictFree = false) : (firstFailureU res).isSome = true := by
  unfold Wire.replayConflictU at h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨s, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  cases h
  simp only [Wire.ConflictReplayU.conflictFree, Wire.conflictFreeCheckU, List.length_map, beq_self_eq_true,
    Bool.true_and, List.all_eq_false] at hf
  obtain ⟨⟨t, c⟩, hm, hc⟩ := hf
  simp only [firstFailureU, Option.isSome_map]
  rw [List.find?_isSome]
  exact ⟨(t, c), hm, by cases c <;> simp_all⟩

theorem firstFailureX_of_not_free (L : Wire.LayeredU) (packages : Json) (hf : Wire.conflictFreeX L packages = false) :
    (Wire.firstFailureX L packages).isSome = true := by
  simp only [Wire.conflictFreeX, List.all_eq_false] at hf
  obtain ⟨t, hm, ht⟩ := hf
  simp only [Wire.firstFailureX, Option.isSome_map]
  rw [List.find?_isSome]
  exact ⟨t, hm, by simpa using ht⟩

theorem line_fits {U X cited translation} (l : Wire.LineU U X cited translation) :
    Fits req (skel% "norm-defaults.json#/$defs/report_line") l.toJson := by
  unfold Wire.LineU.toJson
  split <;> (try simp only [Wire.WitnessRow.toJson]) <;> fits

theorem runLayered_fits (id kind : String) (j : Json) :
    OkFits req Skeletons.normDefaults (Wire.runLayered id kind j) := by
  unfold Wire.runLayered
  okfits
  all_goals (try simp only [VE.Route.Wire.ok, Wire.layeredElaborate, Wire.regeneratedU, VE.Norms.Wire.regenerated,
    Wire.ReportG.toJson])
  all_goals fits using line_fits
  all_goals
    exfalso
    have := firstFailureX_of_not_free _ _ (by
      first | exact ‹Wire.conflictFreeX _ _ = false› | exact Bool.eq_false_iff.mpr ‹¬Wire.conflictFreeX _ _ = true›)
    simp_all

theorem runCase_fits (j : Json) : OkFits req Skeletons.normDefaults (runCase j) := by
  unfold runCase runOtherCase runAdmission
  simp only []
  okfits
  all_goals first
    | with_reducible exact OkP.of (Norms.runCase_fits _) fun _ => of_norms
    | with_reducible exact runLayered_fits _ _ _
    | skip
  all_goals (try simp only [VE.Route.Wire.ok, encodeAdmitted, Wire.regeneratedU, VE.Norms.Wire.regenerated,
    Wire.ReportG.toJson])
  all_goals fits using line_fits
  all_goals try exact Common.claimJson_fits _
  -- Not conflict-free with no failing target: impossible (`firstFailure_of_not_free`).
  all_goals
    exfalso
    have := firstFailure_of_not_free j _ ‹Wire.replayConflictU j = .ok _› (by simp_all)
    simp_all

theorem runCaseReported_fits (j : Json) : Fits j Skeletons.normDefaults (runCaseReported j) := by
  unfold runCaseReported
  split
  · split
    · exact runCase_fits j _ ‹_›
    · fits
  · exact of_norms (Norms.runCaseReported_fits j)

end ResponseShape.Encoders.NormDefaults
