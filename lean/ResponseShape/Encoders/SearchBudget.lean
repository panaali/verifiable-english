import ResponseShape.Encoders.Common
import VE.SearchBudget.Run

namespace ResponseShape.Encoders.SearchBudget
open Lean ResponseShape ResponseShape.Skeletons

theorem runCase_fits (j : Json) :
    OkP (fun r => Fits j Skeletons.searchBudget r) (VE.SearchBudget.Run.runCase j) := by
  unfold VE.SearchBudget.Run.runCase VE.Route.Wire.ok
  okfits
  all_goals fits

theorem runCaseReported_fits (j : Json) :
    Fits j Skeletons.searchBudget (VE.SearchBudget.Run.runCaseReported j) := by
  unfold VE.SearchBudget.Run.runCaseReported
  split
  · exact runCase_fits j _ ‹_›
  · fits

end ResponseShape.Encoders.SearchBudget
