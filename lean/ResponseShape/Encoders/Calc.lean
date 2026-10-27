import ResponseShape.Encoders.Common
import VE.Calc.Run

/-! The `calc` mode (`VE.Calc.Run.runCaseReported`) against `calc.json#/row` (math-evidence spec 3.4). -/
namespace ResponseShape.Encoders.Calc
open Lean ResponseShape ResponseShape.Skeletons VE.Calc

variable {req : Json}

/-- A decoded case names a software convention when its object has a `software` member. -/
theorem decode_software (j : Json) :
    OkP (fun r : Case × String × List String => (CaseCond.lacks "software").holds j = false → r.1.software.isSome)
      (Wire.decode j) := by
  unfold Wire.decode
  okfits
  all_goals intro hl
  all_goals first | rfl | (cases j <;> simp_all [CaseCond.holds, Json.getObjVal?, Except.toBool])

set_option hygiene false in
/-- A claim row (sides, display and tie) or a follows row, each decided with no reason or unknown with Lean's
reason text: the four alternatives of `claim_row`, in order. -/
macro "row_fits" : tactic => `(tactic|(
  unfold Run.rowJson
  cases k <;> rcases o with v | u
  · apply Fits.altHead
    cases v <;> simp only [Run.kind, Run.claimFields, List.cons_append, List.nil_append] <;> fits
  · apply Fits.altTail; apply Fits.altHead
    rcases u with l | _ | _ | _ | _ | _
    · cases l <;> simp only [Run.kind, Run.claimFields, List.cons_append, List.nil_append] <;> fits
    all_goals simp only [Run.kind, Run.claimFields, List.cons_append, List.nil_append] <;> fits
  · apply Fits.altTail; apply Fits.altTail; apply Fits.altHead
    cases v <;> simp only [Run.kind, Run.claimFields, List.append_nil] <;> fits
  · apply Fits.altTail; apply Fits.altTail; apply Fits.altTail; apply Fits.altHead
    rcases u with l | _ | _ | _ | _ | _
    · cases l <;> simp only [Run.kind, Run.claimFields, List.append_nil] <;> fits
    all_goals simp only [Run.kind, Run.claimFields, List.append_nil] <;> fits))

/-- A row: a decided outcome with no reason, or an unknown one with Lean's reason text. -/
theorem rowJson_fits (id : String) (named : String → Option String) (σ : String → Val) (k : Check) (r : Row) :
    Fits req (skel% "calc.json#/$defs/claim_row") (Run.rowJson id named σ k r) := by
  rcases r with ⟨_, o, _⟩
  row_fits

/-- The same, with the reproduction `"unknown"` of a case under a software convention. -/
theorem rowJson_fits_software (id : String) (named : String → Option String) (σ : String → Val) (k : Check) (r : Row)
    (h : r.reproduction.isSome) :
    Fits req (skel% "calc.json#/$defs/claim_row_software") (Run.rowJson id named σ k r) := by
  rcases r with ⟨_, o, p⟩
  cases p with
  | none => cases h
  | some _ => row_fits

/-- A case without `software` has rows without a reproduction; one with it, rows whose reproduction is unknown. -/
theorem runCaseReported_fits (j : Lean.Json) :
    ResponseShape.Fits j ResponseShape.Skeletons.calc (VE.Calc.Run.runCaseReported j) := by
  unfold Run.runCaseReported
  cases hl : (CaseCond.lacks "software").holds j
  · refine Fits.onCaseE hl ?_
    split
    · rename_i hd
      have hs := decode_software j _ hd hl
      fits
      obtain ⟨i, hi, rfl⟩ := List.mem_mapIdx.mp ‹_›
      refine rowJson_fits_software _ _ _ _ _ ?_
      simpa [Run.row] using hs
    · fits
  · refine Fits.onCaseT hl ?_
    split
    · fits
      obtain ⟨i, hi, rfl⟩ := List.mem_mapIdx.mp ‹_›
      exact rowJson_fits _ _ _ _ _
    · fits

end ResponseShape.Encoders.Calc
