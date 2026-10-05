import ResponseShape.Encoders.Common

/-! The `risk-eval` mode (`Risk.Eval.runCaseReported`) against `risk-eval.json#/row`. -/

namespace ResponseShape.Encoders.RiskEval
open Lean ResponseShape ResponseShape.Skeletons
open VE.Risk VE.Risk.Eval

variable {req : Json}

theorem condition_fits (R : RiskDoc) (qs : List Quantity) (b : Box) (j : Json) :
    Fits req (skel% "risk-eval.json#/$defs/result") (evalCondition R qs b j) := by
  unfold evalCondition
  fits

theorem evalCase_fits (j : Json) :
    OkP (fun r => Fits req (.arr [] (skel% "risk-eval.json#/$defs/result")) r) (evalCase j) := by
  unfold evalCase
  okfits
  apply Fits.arrOf
  elems_split
  intro c _
  exact condition_fits _ _ _ _

theorem runCaseReported_fits (j : Json) : Fits j Skeletons.riskEval (runCaseReported j) := by
  unfold runCaseReported
  split
  · fits
    exact evalCase_fits j _ ‹_›
  · fits

end ResponseShape.Encoders.RiskEval
