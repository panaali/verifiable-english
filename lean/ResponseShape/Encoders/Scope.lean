import ResponseShape.Encoders.Common
import VE.Scope.Run

/-! The `scope` mode (`VE.Scope.Run.runCaseReported`) against `scope.json#/row` (docs/spec/scope.md 5.3). -/
namespace ResponseShape.Encoders.Scope
open Lean ResponseShape ResponseShape.Skeletons VE.Scope

variable {req : Json}

theorem explainCase_fits (j : Json) : OkFits j Skeletons.scope (Run.explainCase j) := by
  unfold Run.explainCase VE.Route.Wire.ok
  okfits
  all_goals fits
  all_goals (rename_i h r hr x hx
             exact Fits.strIn (by simpa [effectWords, effectWord] using Run.explainWithin_effect h r hr x hx))

theorem runCaseReported_fits (j : Json) : Fits j Skeletons.scope (VE.Scope.Run.runCaseReported j) := by
  unfold Run.runCaseReported
  split
  · exact explainCase_fits j _ ‹_›
  · fits

end ResponseShape.Encoders.Scope
