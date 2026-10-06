import ResponseShape.Encoders.Common

/-! The `risk-eval` mode (`Risk.Eval.runCaseReported`) against `risk-eval.json#/row`. -/

namespace ResponseShape.Encoders.RiskEval
open Lean ResponseShape ResponseShape.Skeletons
open VE.Risk VE.Risk.Eval

variable {req : Json}

/-- The witness is an object exactly when the condition is possible (`witnessE`). -/
theorem possible_fits (b : Box) (c : Cond) :
    Fits req (skel% "risk-eval.json#/$defs/result")
      (Json.mkObj [("possible", .bool (possibleE b c)), ("certain", .bool (certainE b c)),
        ("witness", match witnessE b c with
          | some v => Json.mkObj (b.entries.map fun e => (e.name, toJson (v e.name)))
          | none => .null)]) := by
  unfold witnessE
  cases possibleE b c <;> simp only [Bool.false_eq_true, ↓reduceIte] <;> fits

theorem condition_fits (R : RiskDoc) (qs : List Quantity) (b : Box) (j : Json) :
    Fits req (skel% "risk-eval.json#/$defs/result") (evalCondition R qs b j) := by
  unfold evalCondition
  split
  · fits
  · split
    · fits
    · split
      · fits
      · fits
      · exact possible_fits b _

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
