import ResponseShape.Encoders.Common

/-! The `quantity` mode (`Time.Wire.runCaseReported` with `Time.Document.extension`) against
`quantity.json#/row`. -/

namespace ResponseShape.Encoders.Quantity
open Lean ResponseShape ResponseShape.Skeletons
open VE.Time VE.Time.Wire

variable {req : Json}

theorem runCount_fits (w : W6Env) (id : String) (j : Json) (hK : req.getObjValD "kind" = .str "count") :
    OkFits req Skeletons.quantity (runCount w id j) := by
  unfold runCount
  okfits
  all_goals (try simp only [ok])
  all_goals fits

theorem runDocument_fits (w : W6Env) (id : String) (j : Json) (hK : req.getObjValD "kind" = .str "document") :
    OkFits req Skeletons.quantity (Document.runDocument w id j) := by
  unfold Document.runDocument
  okfits
  all_goals (try simp only [ok, Document.claimJson])
  all_goals fits using Common.renderKind_fits

/-- The kind `Time.Wire.runCase` reads: the case's `kind` string, else `admission`. -/
theorem kind_read {j w : Json} {k' kind : String} (hobj : j.getObjVal? k' = .ok w)
    (h : (match j.getObjVal? "kind" with
      | .ok k => k.getStr?
      | .error _ => (pure "admission" : Except String String)) = .ok kind) : KindRead "admission" j kind := by
  split at h
  · exact .inl (CaseCond.getObjValD_of_str ‹_› h)
  · cases h
    exact .inr ⟨CaseCond.lacks_of_error hobj ‹_›, rfl⟩

/-- The rows of one kind the runner read (`hK` gives it). -/
macro "quantity_rows" : tactic =>
  `(tactic|(okfits <;> kind_subst <;> (try simp only [ok]) <;>
    first
      | with_reducible exact runCount_fits _ _ _ ‹_›
      | with_reducible exact runDocument_fits _ _ _ ‹_›
      | fits))

/-- `value` and `evaluations` exactly beside a case with a model (`CaseCond.path ["model"]`): the
runner reads the case's `model` (`case_cond` finds the runner's `j.getObjVal? "model"`). -/
theorem runCase_fits (j : Json) : OkFits j Skeletons.quantity (runCase j Document.extension) := by
  unfold runCase runConversion Document.extension noExtension
  simp only []
  with_reducible apply OkP.bind
  intro id hid
  obtain ⟨_, hobj⟩ := Common.stringField_obj hid
  split
  · rename_i hkj
    with_reducible apply OkP.bind
    intro kind hs
    have hK := CaseCond.getObjValD_of_str hkj hs
    quantity_rows
  · rename_i hkj
    have hK := CaseCond.lacks_of_error hobj hkj
    quantity_rows

theorem runCaseReported_fits (j : Json) :
    Fits j Skeletons.quantity (runCaseReported j Document.extension) := by
  unfold runCaseReported
  split
  · exact runCase_fits j _ ‹_›
  · fits
    -- `valid` exactly beside a certificate case.
    all_goals case_cond

end ResponseShape.Encoders.Quantity
