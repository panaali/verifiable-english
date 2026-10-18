import ResponseShape.Encoders.Common

/-! The family modes `graph` and `readings` (`Service.Family`), `bundle` (`Service.FamilyBundle`) and
`family-norms` (`Service.FamilyNorms`) against their row shapes. -/

namespace ResponseShape.Encoders.Family
open Lean ResponseShape ResponseShape.Skeletons
open VE.Service

variable {req : Json}

theorem answer_fits {F C : Type} {wf : F → Bool} {valid : C → List F → F → Bool} (id : String)
    (c : Family.Checked F C wf valid) : Fits req Skeletons.graph (Family.answer id c) := by
  unfold Family.answer VE.Route.Wire.ok
  fits

theorem graph_fits (j : Json) : OkFits req Skeletons.graph (Family.graphMode j) := by
  unfold Family.graphMode Family.graphCase Graph.graphCase
  okfits
  all_goals (try simp only [VE.Route.Wire.ok])
  all_goals fits using answer_fits

theorem readings_fits (j : Json) : OkFits req Skeletons.readings (Family.readingsMode j) := by
  unfold Family.readingsMode Family.readingsCase Readings.readingsCase Family.readings
  okfits
  all_goals (try simp only [VE.Route.Wire.ok])
  all_goals fits

theorem readingsChoices_check_fits {F C M : Type} (ctx : Family.Ctx F C M)
    (valid : C → List F → F → Bool) (refutes : M → List F → F → Bool)
    (j : Json) :
    OkFits j Skeletons.readingsChoices (ReadingsChoices.check ctx valid refutes j) := by
  unfold ReadingsChoices.check
  okfits
  all_goals (try simp only [VE.Route.Wire.ok])
  all_goals fits

theorem readingsChoices_fits (j : Json) :
    OkFits j Skeletons.readingsChoices (ReadingsChoices.run j) := by
  unfold ReadingsChoices.run ReadingsChoices.plan
  okfits
  all_goals (try simp only [VE.Route.Wire.ok])
  all_goals first | exact readingsChoices_check_fits _ _ _ j | fits

theorem bundle_fits (j : Json) : OkFits req Skeletons.bundle (FamilyBundle.bundleCase j) := by
  unfold FamilyBundle.bundleCase FamilyBundle.run
  okfits
  all_goals (try simp only [VE.Route.Wire.ok])
  all_goals fits

private def familyNormsGenericFits {F : Type} (R : VE.Norms.Family.Reader F) (j : Json) :
    OkFits j Skeletons.familyNorms (FamilyNorms.genericCase R j) := by
  unfold FamilyNorms.genericCase
  okfits
  all_goals read_kind
  all_goals (try simp only [VE.Route.Wire.ok])
  all_goals (skel_norm; apply Fits.altTail; apply Fits.altTail; apply Fits.altHead)
  all_goals (first
    | (apply Fits.onCaseT (by case_cond))
    | (apply Fits.onCaseE (by case_cond); apply Fits.onCaseT (by case_cond))
    | (apply Fits.onCaseE (by case_cond); apply Fits.onCaseE (by case_cond);
       apply Fits.onCaseT (by case_cond))
    | (apply Fits.onCaseE (by case_cond); apply Fits.onCaseE (by case_cond);
       apply Fits.onCaseE (by case_cond); apply Fits.onCaseT (by case_cond)))
  all_goals fits

private def familyNormsFolFits (j : Json) :
    OkFits j Skeletons.familyNorms (FamilyNorms.folCase j) := by
  unfold FamilyNorms.folCase
  okfits
  all_goals read_kind
  all_goals (try simp only [VE.Route.Wire.ok, VE.Norms.Flagged.regenerated, VE.Norms.Wire.regenerated,
    List.map_cons, List.map_nil, String.reduceBEq, FamilyNorms.conflictCase])
  all_goals fits

theorem familyNorms_fits (j : Json) : OkFits j Skeletons.familyNorms (FamilyNorms.runCase j) := by
  unfold FamilyNorms.runCase
  split
  · exact familyNormsFolFits j
  · unfold FamilyNorms.genericRun
    split
    all_goals first | exact familyNormsGenericFits _ j | exact OkP.error

theorem graph_reported (j : Json) : Fits j Skeletons.graph (Standalone.reported Family.graphMode j) := by
  unfold Standalone.reported; split
  · exact graph_fits j _ ‹_›
  · fits

theorem readings_reported (j : Json) : Fits j Skeletons.readings (Standalone.reported Family.readingsMode j) := by
  unfold Standalone.reported; split
  · exact readings_fits j _ ‹_›
  · fits

theorem readingsChoices_reported (j : Json) :
    Fits j Skeletons.readingsChoices (Standalone.reported ReadingsChoices.run j) := by
  unfold Standalone.reported; split
  · exact readingsChoices_fits j _ ‹_›
  · fits

theorem bundle_reported (j : Json) : Fits j Skeletons.bundle (Standalone.reported FamilyBundle.bundleCase j) := by
  unfold Standalone.reported; split
  · exact bundle_fits j _ ‹_›
  · fits

theorem familyNorms_reported (j : Json) : Fits j Skeletons.familyNorms (FamilyNorms.runCaseReported j) := by
  unfold FamilyNorms.runCaseReported Standalone.reported; split
  · exact familyNorms_fits j _ ‹_›
  · fits

end ResponseShape.Encoders.Family
