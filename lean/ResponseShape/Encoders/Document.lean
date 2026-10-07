import ResponseShape.Encoders.Common

namespace ResponseShape.Encoders.Document
open Lean ResponseShape ResponseShape.Skeletons

theorem unit_fits (j : Json) (u : VE.Service.Document.Unit) :
    Fits j (skel% "document.json#/$defs/unit") (VE.Service.Document.unitJson u) := by
  cases h : u.parent <;> simp [VE.Service.Document.unitJson, h] <;> fits

theorem document_fits (j : Json) : OkFits j Skeletons.document (VE.Service.Document.documentCase j) := by
  unfold VE.Service.Document.documentCase
  okfits
  all_goals (try simp only [VE.Route.Wire.ok])
  all_goals (try fits)
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
