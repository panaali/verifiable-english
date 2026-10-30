import ResponseShape.Encoders.Quantity
import VE.Cardinality.Run

/-! The `cardinality` mode (`VE.Cardinality.Run.runCaseReported`) against `cardinality.json#/row`
(docs/spec/quantities.md 4.3). -/
namespace ResponseShape.Encoders.Cardinality
open Lean ResponseShape ResponseShape.Skeletons VE.Cardinality

variable {req : Json}

theorem regionsJson_fits (R : RegionData) (table : List (String × String × Region)) :
    Fits req (skel% "cardinality.json#/$defs/regions") (Run.regionsJson R table) := by
  unfold Run.regionsJson
  simp only [toJson, List.toJson, Array.toJson, List.map_toArray, List.map_map]
  fits

theorem problemJson_fits (ep : List VE.Time.QFormula × VE.Time.QFormula)
    (ids : List (String × String) × (String × String)) :
    Fits req (skel% "cardinality.json#/$defs/problem") (Run.problemJson ep ids) := by
  unfold Run.problemJson
  fits

theorem erasedJson_fits (w : CardEnv) (ps : List CFormula) (c : CFormula) :
    OkFits req (skel% "cardinality.json#/$defs/problem") (Run.erasedJson w ps c) := by
  unfold Run.erasedJson
  okfits
  exact problemJson_fits _ _

/-- The runner answers a certificate row only for the kind `certificate`. -/
theorem certificate_kind {j : Json} {kind : String} (hK : j.getObjValD "kind" = .str kind)
    (h1 : (kind == "admission" || kind == "certificate" || kind == "document") = true)
    (hd : ¬(kind == "document") = true) (h2 : ¬(kind == "admission") = true) :
    (CaseCond.kind "certificate").holds j = true := by
  simp only [Bool.or_eq_true, beq_iff_eq] at h1 h2 hd
  obtain rfl := (h1.resolve_right hd).resolve_left h2
  simp only [CaseCond.holds, hK]
  rfl

set_option hygiene false in
/-- An admission, certificate or document row, by the kind the runner read (the case's `kind` string, else `admission`). -/
macro "cardinality_rows" : tactic =>
  `(tactic|(okfits <;> kind_subst <;> (try simp only [VE.Time.Wire.ok, Run.statementJson]) <;>
    (try fits using regionsJson_fits) <;>
    first
      | exact problemJson_fits _ _
      | exact certificate_kind hK (by assumption) (by assumption) (by assumption)
      | exact absurd (by decide) ‹¬("admission" == "admission") = true›))

theorem runCase_fits (j : Json) : OkFits j Skeletons.cardinality (Run.runCase j) := by
  unfold Run.runCase
  simp only []
  with_reducible apply OkP.bind
  intro id hid
  obtain ⟨_, hobj⟩ := Common.stringField_obj hid
  split
  · rename_i hkj
    with_reducible apply OkP.bind
    intro kind hs
    have hK := CaseCond.getObjValD_of_str hkj hs
    cardinality_rows
  · rename_i hkj
    have hK := CaseCond.lacks_of_error hobj hkj
    cardinality_rows

theorem runCaseReported_fits (j : Json) :
    Fits j Skeletons.cardinality (VE.Cardinality.Run.runCaseReported j) := by
  unfold Run.runCaseReported
  split
  · exact runCase_fits j _ ‹_›
  · fits
    -- `valid` exactly beside a certificate case.
    all_goals case_cond

end ResponseShape.Encoders.Cardinality
