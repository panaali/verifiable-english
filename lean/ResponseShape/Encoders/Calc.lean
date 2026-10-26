import ResponseShape.Encoders.Common
import VE.Calc.Run

/-! The `calc` mode (`VE.Calc.Run.runCaseReported`) against `calc.json#/row` (math-evidence spec 3.4). -/
namespace ResponseShape.Encoders.Calc
open Lean ResponseShape ResponseShape.Skeletons VE.Calc

variable {req : Json}

/-- A row: a decided outcome with no reason, or an unknown one with Lean's reason text. -/
theorem rowJson_fits (id : String) (r : Row) :
    Fits req (skel% "calc.json#/$defs/claim_row") (Run.rowJson id r) := by
  rcases r with ⟨_, o, _⟩
  unfold Run.rowJson
  rcases o with v | u
  · apply Fits.altHead
    cases v <;> fits
  · apply Fits.altTail; apply Fits.altHead
    rcases u with l | _ | _ | _ | _ | _
    · cases l <;> fits
    all_goals fits

theorem runCaseReported_fits (j : Lean.Json) :
    ResponseShape.Fits j ResponseShape.Skeletons.calc (VE.Calc.Run.runCaseReported j) := by
  unfold Run.runCaseReported
  split
  · fits
    obtain ⟨i, hi, rfl⟩ := List.mem_mapIdx.mp ‹_›
    exact rowJson_fits _ _
  · fits

end ResponseShape.Encoders.Calc
