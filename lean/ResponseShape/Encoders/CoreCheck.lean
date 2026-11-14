import ResponseShape.Encoders.Document
import VE.Service.CoreCheck

/-! The document mode's entry (`VE.Service.CoreCheck.runCaseReported`, kb-2a-b) against `document.json`: a routed
document's answer (its view and the kernel's rows) and its refusal rows marked `lowering`, and every other case's row
(`Document.runCaseReported`, unchanged). -/
namespace ResponseShape.Encoders.CoreCheck
open Lean ResponseShape ResponseShape.Skeletons
open VE.Service.CoreCheck

theorem statement_fits (j : Json) (st : VE.Service.CoreDocument.Statement) :
    Fits j (skel% "document.json#/$defs/core_statement") (statementJson st) := by
  unfold statementJson
  cases st.origin.reading <;> cases st.body <;>
    simp only [Option.toList, List.map_nil, List.map_cons, List.nil_append, List.cons_append, List.singleton_append]
  all_goals fits

theorem statements_fits (j : Json) (units : List VE.Service.Document.SourceUnit)
    (docs : List (VE.Service.CoreDocument.Choice × VE.Service.CoreDocument.CoreDoc)) :
    Fits j (skel% "document.json#/$defs/core_statements") (statementsJson units docs) := by
  unfold statementsJson
  fits
  all_goals exact statement_fits j _

theorem choices_fits (j : Json) (docs : List (VE.Service.CoreDocument.Choice × VE.Service.CoreDocument.CoreDoc)) :
    Fits j (skel% "document.json#/$defs/core_choices") (choicesJson docs) := by
  unfold choicesJson
  fits

theorem view_fits (j : Json) (I : Inputs)
    (docs : List (VE.Service.CoreDocument.Choice × VE.Service.CoreDocument.CoreDoc)) (st : List (String × VE.Kernel.DocumentFold.Status)) :
    Fits j (skel% "document.json#/$defs/core_view") (viewOf I docs st) := by
  unfold viewOf VE.Service.Document.encodeFields
  by_cases hj : I.d.judged <;> simp only [hj, ↓reduceIte, Bool.false_eq_true, List.cons_append, List.nil_append,
    List.append_nil]
  all_goals fits using Document.coverage_fits, Document.usage_fits, Document.lines_fits, Document.undeclared_fits,
    choices_fits, statements_fits
  all_goals
    apply Fits.arrOf
    intro x hx
    simp only [show (toJson : Json → Json) = id from rfl, Array.map_id, List.mem_toArray, List.mem_map] at hx
    obtain ⟨u, _, rfl⟩ := hx
    exact Document.unit_fits j u

/-- The rows member of `carry`. -/
def rowsJson (rows : List VE.Kernel.Row) : Json :=
  Json.arr (rows.map fun r => Json.mkObj [("case", r.case),
    match r.result with
    | .ok a => ("answer", a)
    | .error e => ("refused", Json.str e)]).toArray

theorem fold_eq (v : List (String × VE.Kernel.DocumentFold.Status) → Json) (t : List VE.Kernel.DocumentFold.UnitRow) (req : Json)
    (rows : List VE.Kernel.Row) :
    VE.Kernel.DocumentFold.fold v t req rows =
      Json.mkObj [("view", v (VE.Kernel.DocumentFold.statuses t rows)), ("rows", rowsJson rows)] := rfl

theorem fold_get (v : List (String × VE.Kernel.DocumentFold.Status) → Json) (t : List VE.Kernel.DocumentFold.UnitRow) (req : Json)
    (rows : List VE.Kernel.Row) :
    (VE.Kernel.DocumentFold.fold v t req rows).getObjValD "view" = v (VE.Kernel.DocumentFold.statuses t rows) ∧
      (VE.Kernel.DocumentFold.fold v t req rows).getObjValD "rows" = rowsJson rows := by
  have hn : ([("view", v (VE.Kernel.DocumentFold.statuses t rows)), ("rows", rowsJson rows)].map (·.1)).Nodup := by
    simp
  have hv := VE.Calc.Run.mkObj_get _ "view" _ hn (List.mem_cons_self ..)
  have hr := VE.Calc.Run.mkObj_get _ "rows" _ hn (List.mem_cons_of_mem _ (List.mem_cons_self ..))
  rw [fold_eq]
  exact ⟨by simp only [Json.getObjValD, hv]; rfl, by simp only [Json.getObjValD, hr]; rfl⟩

theorem answer_fits (j a : Json) (h : answer j = .ok a) : Fits j Skeletons.document a := by
  obtain ⟨p, _, _, _, _, rows, _, _, rfl⟩ := document_core_sound j a h
  rw [(fold_get _ _ _ _).1, (fold_get _ _ _ _).2]
  simp only [VE.Route.Wire.ok, rowsJson, List.cons_append, List.nil_append]
  fits using view_fits
  done

theorem runCaseReported_fits (j : Json) : Fits j Skeletons.document (VE.Service.CoreCheck.runCaseReported j) := by
  unfold VE.Service.CoreCheck.runCaseReported
  split
  · split
    · exact answer_fits j _ ‹_›
    · simp only []
      split
      · exact Document.runCaseReported_fits j
      split
      · unfold VE.Service.Document.locatedRow
        split <;> (try unfold VE.Service.ParseDiagnostic.span) <;> rw [setObjVal_mkObj] <;>
          simp only [List.cons_append, List.nil_append] <;> fits
      · unfold VE.Service.Standalone.reported
        simp only []
        rw [setObjVal_mkObj]
        simp only [List.cons_append, List.nil_append]
        fits
  · exact Document.runCaseReported_fits j

end ResponseShape.Encoders.CoreCheck
