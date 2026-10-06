import ResponseShape.Encoders.Norms

/-! The `norm-defaults` mode (`NormDefaults.Run.runCaseReported`) against `norm-defaults.json#/row`.
A case off the norm-defaults path is the norms mode's. -/

namespace ResponseShape.Encoders.NormDefaults
open Lean ResponseShape ResponseShape.Skeletons
open VE.NormDefaults VE.NormDefaults.Run

variable {req : Json}

/-- The norms mode's rows, off the norm-defaults path, are rows of this mode. -/
theorem of_norms {v : Json} (hp : usesNormDefaultsPath req = false) (h : Fits req Skeletons.norms v) :
    Fits req Skeletons.normDefaults v :=
  Fits.onCaseE (by simpa [CaseCond.holds, CaseDecider.fn] using hp) h

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

/-- Every admission's kinds are its units' rendered kinds. -/
theorem admitDocument_kinds (environment document : Json) :
    OkP (fun res : Admission.Admitted => Common.KindsRendered res.kinds) (Admission.admitDocument environment document) := by
  unfold Admission.admitDocument
  okfits
  all_goals exact Common.kindsRendered_map _ _

theorem runCase_fits (j : Json) (hp : usesNormDefaultsPath j = true) :
    OkFits j Skeletons.normDefaults (runCase j) := by
  unfold runCase runOtherCase runAdmission
  simp only []
  okfits
  all_goals read_kind
  all_goals (try contra)
  all_goals (try simp only [VE.Route.Wire.ok, encodeAdmitted, Wire.regeneratedU, VE.Norms.Wire.regenerated])
  all_goals fits
  all_goals try exact Common.claimJson_fits _
  all_goals try exact Common.kind_fits (admitDocument_kinds _ _ _ ‹Admission.admitDocument _ _ = .ok _›) ‹_›
  -- Not conflict-free with no failing target: impossible (`firstFailure_of_not_free`).
  all_goals
    exfalso
    have := firstFailure_of_not_free j _ ‹Wire.replayConflictU j = .ok _› (by simp_all)
    simp_all

theorem runCaseReported_fits (j : Json) (hj : CaseWF j) : Fits j Skeletons.normDefaults (runCaseReported j) := by
  unfold runCaseReported
  split
  · split
    · exact runCase_fits j ‹_› _ ‹_›
    · fits
  · exact of_norms (Bool.eq_false_iff.mpr ‹_›) (Norms.runCaseReported_fits j hj)

end ResponseShape.Encoders.NormDefaults
