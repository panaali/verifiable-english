import ResponseShape.Encoders.Common
import VE.Senses.Run

/-! The `senses.project` mode (`VE.Senses.Run.projectCaseReported`) against `senses.project.json#/row`. -/
namespace ResponseShape.Encoders.SensesProject
open Lean ResponseShape ResponseShape.Skeletons VE.Senses

variable {req : Json}

/-- A fault's status is `budget` or `rejected` (`SensesOutcome.statusCode`), with its arguments. -/
theorem faultJson_fits (f : SenseFault) :
    Fits req (skel% "senses.project.json#/$defs/projection") (Run.faultJson f) := by
  cases f <;> simp only [Run.faultJson, SensesOutcome.statusCode, Run.faultFields, pure, Except.pure, List.cons_append,
    List.nil_append] <;> (try split) <;> fits

/-- A projection's lexicon JSON names its environment, and its identities are those three. -/
theorem projectionIds_ok {c : VE.EnglishGrammar.Run.Case} {P : Projection} {r : Json × List (String × Json)}
    (h : Run.projectionIds c P = .ok r) : ∃ envId lid gid : String, r = (Run.lexiconJson envId P.lexicon,
      [("environment_id", .str envId), ("lexicon_id", .str lid), ("grammar_id", .str gid)]) := by
  unfold Run.projectionIds at h
  obtain ⟨envId, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨lid, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨gid, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  cases h
  exact ⟨_, _, _, rfl⟩

theorem projectCase_fits (j : Json) : OkFits j Skeletons.sensesProject (Run.projectCase j) := by
  unfold Run.projectCase VE.Route.Wire.ok
  okfits
  all_goals (try (rename_i h; with_reducible obtain ⟨_, _, _, rfl⟩ := projectionIds_ok h; simp only [Run.lexiconJson]))
  all_goals first | (fits; done) | fits using faultJson_fits

theorem projectCaseReported_fits (j : Json) : Fits j Skeletons.sensesProject (Run.projectCaseReported j) := by
  unfold Run.projectCaseReported
  split
  · exact projectCase_fits j _ ‹_›
  · fits

end ResponseShape.Encoders.SensesProject
