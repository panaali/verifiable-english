import ResponseShape.Encoders.Common
import VE.Question.Run

namespace ResponseShape.Encoders.Question
open Lean ResponseShape ResponseShape.Skeletons

theorem questionCase_fits (j : Json) :
    OkP (fun r => Fits j Skeletons.englishQuestion r) (VE.Question.Run.questionCase j) := by
  unfold VE.Question.Run.questionCase VE.Question.Run.codesCase VE.Route.Wire.ok
  okfits
  all_goals fits

theorem caseReported_fits (j : Json) : Fits j Skeletons.englishQuestion (VE.Question.Run.caseReported j) := by
  unfold VE.Question.Run.caseReported
  split
  · exact questionCase_fits j _ ‹_›
  · fits

end ResponseShape.Encoders.Question
