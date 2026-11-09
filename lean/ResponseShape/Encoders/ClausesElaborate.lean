import ResponseShape.Encoders.Common
import VE.RightClauses.Run

/-! The `clauses-elaborate` mode (`VE.RightClauses.Run.runCaseReported`) against `clauses-elaborate.json#/row`. -/
namespace ResponseShape.Encoders.ClausesElaborate
open Lean ResponseShape ResponseShape.Skeletons VE.RightClauses.Run

theorem elaborateCase_fits (j : Json) : OkFits j Skeletons.clausesElaborate (elaborateCase j) := by
  unfold elaborateCase labelledJson VE.Route.Wire.ok
  okfits
  all_goals fits

theorem runCaseReported_fits (j : Json) : Fits j Skeletons.clausesElaborate (runCaseReported j) := by
  unfold runCaseReported
  split
  · exact elaborateCase_fits j _ ‹_›
  · fits

end ResponseShape.Encoders.ClausesElaborate
