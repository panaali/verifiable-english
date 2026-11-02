import ResponseShape.Encoders.Common
import VE.EnglishGrammar.JudgmentLines

/-! The `judgment-line` mode (`VE.EnglishGrammar.JudgmentLines.runCaseReported`) against `judgment-line.json#/row`. -/
namespace ResponseShape.Encoders.JudgmentLine
open Lean ResponseShape ResponseShape.Skeletons VE.EnglishGrammar

variable {req : Json}

theorem lineCase_fits (j : Json) : OkFits j Skeletons.judgmentLine (JudgmentLines.lineCase j) := by
  unfold JudgmentLines.lineCase JudgmentLines.recordJson VE.Route.Wire.ok
  okfits
  all_goals fits

theorem runCaseReported_fits (j : Json) : Fits j Skeletons.judgmentLine (JudgmentLines.runCaseReported j) := by
  unfold JudgmentLines.runCaseReported
  split
  · exact lineCase_fits j _ ‹_›
  · fits

end ResponseShape.Encoders.JudgmentLine
