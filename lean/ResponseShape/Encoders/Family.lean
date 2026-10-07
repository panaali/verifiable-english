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

theorem bundle_fits (j : Json) : OkFits req Skeletons.bundle (FamilyBundle.bundleCase j) := by
  unfold FamilyBundle.bundleCase FamilyBundle.run
  okfits
  all_goals (try simp only [VE.Route.Wire.ok])
  all_goals fits

theorem familyNorms_fits (j : Json) : OkFits j Skeletons.familyNorms (FamilyNorms.runCase j) := by
  unfold FamilyNorms.runCase
  okfits
  all_goals read_kind
  all_goals (try simp only [VE.Route.Wire.ok, VE.Norms.Flagged.regenerated, VE.Norms.Wire.regenerated,
    List.map_cons, List.map_nil, String.reduceBEq, FamilyNorms.conflictCase])
  all_goals fits

theorem graph_reported (j : Json) : Fits j Skeletons.graph (Standalone.reported Family.graphMode j) := by
  unfold Standalone.reported; split
  · exact graph_fits j _ ‹_›
  · split <;> fits

theorem readings_reported (j : Json) : Fits j Skeletons.readings (Standalone.reported Family.readingsMode j) := by
  unfold Standalone.reported; split
  · exact readings_fits j _ ‹_›
  · split <;> fits

theorem bundle_reported (j : Json) : Fits j Skeletons.bundle (Standalone.reported FamilyBundle.bundleCase j) := by
  unfold Standalone.reported; split
  · exact bundle_fits j _ ‹_›
  · split <;> fits

theorem familyNorms_reported (j : Json) : Fits j Skeletons.familyNorms (FamilyNorms.runCaseReported j) := by
  unfold FamilyNorms.runCaseReported Standalone.reported; split
  · exact familyNorms_fits j _ ‹_›
  · split <;> fits

end ResponseShape.Encoders.Family
