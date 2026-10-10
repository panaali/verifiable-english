import ResponseShape.Encoders.Common

namespace ResponseShape.Encoders.Document
open Lean ResponseShape ResponseShape.Skeletons

theorem meaning_fits (j : Json) (m : VE.Service.Document.Meaning) :
    Fits j (skel% "document.json#/$defs/meaning") m.json := by
  cases m <;> simp only [VE.Service.Document.Meaning.json] <;> fits

theorem unit_fits (j : Json) (u : VE.Service.Document.RowUnit) :
    Fits j (skel% "document.json#/$defs/unit") (VE.Service.Document.unitJson u) := by
  cases h : u.parent <;> cases hc : u.content <;> cases hm : u.meaningId <;>
    simp [VE.Service.Document.unitJson, h, hc, hm] <;> fits using meaning_fits
  all_goals exact Common.renderKind_fits u.kind

/-- The alternatives route's coverage line fits the document schema's `block_coverage` (its cells as relayed,
with the document's own narrowings). -/
theorem block_coverage_fits (j : Json) (A : VE.Alternatives.AltDoc) (environment units narrowings : Json) :
    Fits j (skel% "document.json#/$defs/block_coverage")
      (VE.Alternatives.Wire.coverage A environment units narrowings) := by
  unfold VE.Alternatives.Wire.coverage
  fits
  case h_2 x completion item heq hx =>
    simp only [List.mem_flatMap, List.mem_filterMap] at hx
    rcases hx with ⟨action, _, harm, _, h⟩
    split at h <;> simp only [Option.some.injEq, reduceCtorEq] at h
    subst_vars
    fits
    all_goals
      split at heq <;> simp only [Option.some.injEq, reduceCtorEq] at heq
      subst_vars
      fits

/-- The cells the row relays are the line's `alternatives` field. -/
theorem cells_fits (j : Json) (b : VE.Service.Document.BlockCoverage) :
    Fits j (skel% "document.json#/$defs/cells") (b.line.getObjValD "alternatives") := by
  have hk : b.line.getObjVal? "alternatives" = .ok (b.line.getObjValD "alternatives") := by
    show (VE.Alternatives.Wire.coverage b.doc b.environment b.units b.narrowings).getObjVal? "alternatives" =
      .ok ((VE.Alternatives.Wire.coverage b.doc b.environment b.units b.narrowings).getObjValD "alternatives")
    unfold VE.Alternatives.Wire.coverage
    rfl
  exact Fits.getObjVal (block_coverage_fits j b.doc b.environment b.units b.narrowings) hk

theorem coverage_fits (j front : Json) (units : List VE.Service.Document.SourceUnit) (n : Nat)
    (block : Option VE.Service.Document.BlockCoverage) :
    Fits j (skel% "document.json#/$defs/coverage") (VE.Service.Document.coverageJson front units n block) := by
  unfold VE.Service.Document.coverageJson
  split <;> fits using cells_fits

theorem document_fits (j : Json) : OkFits j Skeletons.document (VE.Service.Document.documentCase j) := by
  unfold VE.Service.Document.documentCase VE.Service.Document.encode
  okfits
  all_goals (try simp only [VE.Route.Wire.ok])
  all_goals (try fits using coverage_fits)
  all_goals
    apply Fits.arrOf
    intro x hx
    simp only [show (toJson : Json → Json) = id from rfl, Array.map_id,
      List.mem_toArray, List.mem_map] at hx
    obtain ⟨u, _, rfl⟩ := hx
    exact unit_fits j u

theorem runCaseReported_fits (j : Json) :
    Fits j Skeletons.document (VE.Service.Document.runCaseReported j) := by
  unfold VE.Service.Document.runCaseReported VE.Service.Standalone.reported
  split
  · exact document_fits j _ ‹_›
  · fits

end ResponseShape.Encoders.Document
