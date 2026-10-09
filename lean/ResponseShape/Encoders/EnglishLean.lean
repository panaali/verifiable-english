import ResponseShape.Encoders.Common

namespace ResponseShape.Encoders.EnglishLean
open Lean ResponseShape ResponseShape.Skeletons

theorem ok_fits (j : Json) (id : String) (result : Json) :
    Fits j Skeletons.englishRead (VE.Route.Wire.ok id [("result", result)]) := by
  unfold VE.Route.Wire.ok
  fits

theorem readCase_fits (j : Json) :
    OkP (fun r => Fits j Skeletons.englishRead r) (VE.EnglishGrammar.Run.readCase j) := by
  unfold VE.EnglishGrammar.Run.readCase
  okfits
  all_goals first | exact ok_fits _ _ _ | fits

theorem read_fits (j : Json) : Fits j Skeletons.englishRead
    (VE.EnglishGrammar.Run.readCaseReported j) := by
  unfold VE.EnglishGrammar.Run.readCaseReported VE.EnglishGrammar.Run.runCaseReported
  simp only [show ("english.read" == "english.grammar") = false by decide,
    show ("english.read" == "english.check") = false by decide, Bool.false_eq_true, if_false]
  split
  · exact readCase_fits j _ ‹_›
  · fits

theorem grammar_fits (j : Json) : Fits j Skeletons.englishGrammar
    (VE.EnglishGrammar.Run.grammarCaseReported j) := by
  have case_fits : OkP (fun r => Fits j Skeletons.englishGrammar r)
      (VE.EnglishGrammar.Run.grammarCase j) := by
    unfold VE.EnglishGrammar.Run.grammarCase
    okfits
    all_goals first | exact ok_fits _ _ _ | fits
  unfold VE.EnglishGrammar.Run.grammarCaseReported VE.EnglishGrammar.Run.runCaseReported
  simp only [show ("english.grammar" == "english.grammar") = true by decide, if_true]
  split
  · exact case_fits _ ‹_›
  · fits

theorem check_fits (j : Json) : Fits j Skeletons.englishCheck
    (VE.EnglishGrammar.Run.checkCaseReported j) := by
  have case_fits : OkP (fun r => Fits j Skeletons.englishCheck r)
      (VE.EnglishGrammar.Run.checkCase j) := by
    unfold VE.EnglishGrammar.Run.checkCase
    okfits
    all_goals first | exact ok_fits _ _ _ | fits
  unfold VE.EnglishGrammar.Run.checkCaseReported VE.EnglishGrammar.Run.runCaseReported
  simp only [show ("english.check" == "english.grammar") = false by decide,
    show ("english.check" == "english.check") = true by decide, Bool.false_eq_true, if_false, if_true]
  split
  · exact case_fits _ ‹_›
  · fits

end ResponseShape.Encoders.EnglishLean
