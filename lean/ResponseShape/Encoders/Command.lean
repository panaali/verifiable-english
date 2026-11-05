import ResponseShape.Encoders.Common
import VE.Commands.Run

/-! The `english.command` mode (`VE.Commands.Run.caseReported`) against `english.command.json#/row`. -/
namespace ResponseShape.Encoders.Command
open Lean ResponseShape ResponseShape.Skeletons VE.Commands

variable {req : Json}

theorem readingJson_fits (q : Request) (r : Reading) :
    Fits req (skel% "english.command.json#/$defs/reading") (Run.readingJson q r) := by
  unfold Run.readingJson
  fits

theorem encode_fits (q : Request) (o : Outcome) : Fits req Skeletons.englishCommand (Run.encode q o) := by
  unfold Run.encode VE.Route.Wire.ok
  cases o <;> simp only [Run.outcomeFields, List.cons_append, List.nil_append] <;> fits using readingJson_fits

theorem caseReported_fits (j : Json) : Fits j Skeletons.englishCommand (Run.caseReported j) := by
  unfold Run.caseReported
  split
  · exact encode_fits _ _
  · fits

end ResponseShape.Encoders.Command
