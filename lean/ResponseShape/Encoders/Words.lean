import ResponseShape.Encoders.Common
import VE.Words.Run

/-! The `words` mode (`VE.Words.Run.caseReported`) against `words.json#/row`. -/
namespace ResponseShape.Encoders.Words
open Lean ResponseShape ResponseShape.Skeletons VE.Words.Run

theorem wordsCase_fits (j : Json) : OkFits j Skeletons.words (wordsCase j) := by
  unfold wordsCase VE.Route.Wire.ok
  okfits
  all_goals fits

theorem caseReported_fits (j : Json) : Fits j Skeletons.words (caseReported j) := by
  unfold caseReported
  split
  · exact wordsCase_fits j _ ‹_›
  · fits

end ResponseShape.Encoders.Words
