import ResponseShape.Encoders.Common

/-! The `quantity` mode (`Time.Wire.runCaseReported` with `Time.Document.extension`) against
`quantity.json#/row`. -/

namespace ResponseShape.Encoders.Quantity
open Lean ResponseShape ResponseShape.Skeletons
open VE.Time VE.Time.Wire

theorem runCount_fits (w : W6Env) (id : String) (j : Json) : OkFits Γ Skeletons.quantity (runCount w id j) := by
  unfold runCount
  okfits
  all_goals (try simp only [ok])
  all_goals fits

theorem runDocument_fits (w : W6Env) (id : String) (j : Json) :
    OkFits Γ Skeletons.quantity (Document.runDocument w id j) := by
  unfold Document.runDocument
  okfits
  all_goals (try simp only [ok, Document.claimJson])
  all_goals fits

theorem runCase_fits (j : Json) : OkFits Γ Skeletons.quantity (runCase j Document.extension) := by
  unfold runCase runConversion Document.extension noExtension
  simp only []
  okfits
  all_goals (try simp only [ok])
  all_goals first
    | with_reducible exact runCount_fits _ _ _
    | with_reducible exact runDocument_fits _ _ _
    | fits

theorem runCaseReported_fits (j : Json) :
    Fits Γ Skeletons.quantity (runCaseReported j Document.extension) := by
  unfold runCaseReported
  split
  · exact runCase_fits j _ ‹_›
  · fits

end ResponseShape.Encoders.Quantity
