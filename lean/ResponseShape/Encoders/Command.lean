import ResponseShape.Encoders.Common
import VE.Commands.Run

/-! The `english.command` mode (`VE.Commands.Run.caseReported`) against `english.command.json#/row`. -/
namespace ResponseShape.Encoders.Command
open Lean ResponseShape ResponseShape.Skeletons VE.Commands

variable {req : Json}

theorem readingJson_fits (q : Request) (k : Option Nat) (r : Reading) :
    Fits req (skel% "english.command.json#/$defs/reading") (Run.readingJson q k r) := by
  unfold Run.readingJson
  fits

theorem altIndexes_fits : ∀ (k : Nat) (alts : List Alt),
    ∀ x ∈ Run.altIndexes k (alts.map Run.altParts), Fits req (skel% "english.command.json#/$defs/alternative") x
  | _, [] => by simp [Run.altIndexes]
  | k, a :: rest => by
    intro x hx
    cases a with
    | shape sh rs =>
      simp only [List.map_cons, Run.altParts, Run.altIndexes, List.mem_cons] at hx
      rcases hx with rfl | hx
      · cases sh <;> simp only [Run.shapeName] <;> fits
      · exact altIndexes_fits _ rest x hx
    | form f =>
      simp only [List.map_cons, Run.altParts, Run.altIndexes, List.mem_cons] at hx
      rcases hx with rfl | hx
      · fits
      · exact altIndexes_fits _ rest x hx
    | purpose r p =>
      simp only [List.map_cons, Run.altParts, Run.altIndexes, List.mem_cons] at hx
      rcases hx with rfl | hx
      · fits
      · exact altIndexes_fits _ rest x hx

theorem encode_fits (q : Request) (o : StepOutcome) : Fits req Skeletons.englishCommand (Run.encode q o) := by
  unfold Run.encode VE.Route.Wire.ok
  cases o <;> simp only [Run.outcomeFields, List.cons_append, List.nil_append] <;>
    fits using readingJson_fits, altIndexes_fits

theorem caseReported_fits (j : Json) : Fits j Skeletons.englishCommand (Run.caseReported j) := by
  unfold Run.caseReported
  split
  · exact encode_fits _ _
  · fits

end ResponseShape.Encoders.Command
