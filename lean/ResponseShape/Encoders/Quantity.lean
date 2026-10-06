import ResponseShape.Encoders.Common

/-! The `quantity` mode (`Time.Wire.runCaseReported` with `Time.Document.extension`) against
`quantity.json#/row`. -/

namespace ResponseShape.Encoders.Quantity
open Lean ResponseShape ResponseShape.Skeletons
open VE.Time VE.Time.Wire

variable {req : Json}

theorem runCount_fits (w : W6Env) (id : String) (j : Json) : OkFits req Skeletons.quantity (runCount w id j) := by
  unfold runCount
  okfits
  all_goals (try simp only [ok])
  all_goals fits

theorem runDocument_fits (w : W6Env) (id : String) (j : Json) :
    OkFits req Skeletons.quantity (Document.runDocument w id j) := by
  unfold Document.runDocument
  okfits
  all_goals (try simp only [ok, Document.claimJson])
  all_goals fits

theorem runCase_fits (j : Json) : OkFits j Skeletons.quantity (runCase j Document.extension) := by
  unfold runCase runConversion Document.extension noExtension
  simp only []
  okfits
  all_goals (try simp only [ok])
  all_goals first
    | with_reducible exact runCount_fits _ _ _
    | with_reducible exact runDocument_fits _ _ _
    | fits
  -- `value` and `evaluations` exactly beside a case with a model: the runner reads the case's `model`.
  all_goals first
    | exact CaseCond.path_ok ‹j.getObjVal? "model" = .ok _›
    | exact CaseCond.path_error ‹j.getObjVal? "environment" = .ok _› ‹j.getObjVal? "model" = .error _›

theorem runCaseReported_fits (j : Json) :
    Fits j Skeletons.quantity (runCaseReported j Document.extension) := by
  unfold runCaseReported
  split
  · exact runCase_fits j _ ‹_›
  · fits
    -- `valid` exactly beside a certificate case.
    all_goals case_cond

end ResponseShape.Encoders.Quantity
