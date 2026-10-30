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

/-- A tie flag: true, false or null (`ResponseShape.Schemas.Calc.flag`). -/
theorem tie_fits (t : Option Bool) :
    Fits req (.alt [.lit (.bool true), .lit (.bool false), .lit .null]) (t.elim .null Json.bool) := by
  rcases t with _ | _ | _
  · exact Fits.alt (by simp) (Fits.lit .null)
  · exact Fits.alt (by simp) (Fits.lit (.bool false))
  · exact Fits.alt (by simp) (Fits.lit (.bool true))

/-- A replayed step has exactly one of the two typed forms. -/
theorem stepJson_fits (st : Step) : Fits req (skel% "calc.json#/$defs/step") (Run.stepJson st) := by
  cases st <;> simp only [Run.stepJson] <;> fits

set_option hygiene false in
/-- A claim row (sides, display and tie) that holds or fails, is undefined, or is unknown with Lean's reason text, or
a follows row with its evidence: the seven alternatives of `claim_row`, in order. -/
macro "row_fits" : tactic => `(tactic|(
  unfold Run.rowJson
  cases k <;> rcases o with v | u
  · cases v
    · apply Fits.altHead; simp only [Run.kind, Run.claimFields, List.cons_append, List.nil_append, List.append_nil]; fits
      all_goals exact tie_fits _
    · apply Fits.altHead; simp only [Run.kind, Run.claimFields, List.cons_append, List.nil_append, List.append_nil]; fits
      all_goals exact tie_fits _
    · apply Fits.altTail; apply Fits.altHead
      simp only [Run.kind, Run.claimFields, List.cons_append, List.nil_append, List.append_nil]; fits
      all_goals exact tie_fits _
  · apply Fits.altTail; apply Fits.altTail; apply Fits.altHead
    rcases u with l | _ | _ | _ | _ | _
    · cases l <;> simp only [Run.kind, Run.claimFields, List.cons_append, List.nil_append, List.append_nil] <;> fits <;> exact tie_fits _
    all_goals simp only [Run.kind, Run.claimFields, List.cons_append, List.nil_append, List.append_nil] <;> fits <;> exact tie_fits _
  · cases v with
    | holds =>
      cases s with
      | nothing => simp [Shown.matches] at h
      | counterexample _ => simp [Shown.matches] at h
      | certificate steps =>
        cases steps with
        | nil => simp [Shown.matches] at h
        | cons st rest =>
          apply Fits.altTail; apply Fits.altTail; apply Fits.altTail; apply Fits.altHead
          simp only [Run.kind, Run.claimFields, Run.shownJson, List.append_nil, List.nil_append]; fits
          all_goals exact stepJson_fits _
    | fails =>
      cases s with
      | nothing => simp [Shown.matches] at h
      | certificate _ => simp [Shown.matches] at h
      | counterexample κ =>
        apply Fits.altTail; apply Fits.altTail; apply Fits.altTail; apply Fits.altTail; apply Fits.altHead
        simp only [Run.kind, Run.claimFields, Run.shownJson, List.append_nil, List.nil_append]; fits
    | undefined =>
      cases s with
      | nothing =>
        apply Fits.altTail; apply Fits.altTail; apply Fits.altTail; apply Fits.altTail; apply Fits.altTail
        apply Fits.altHead
        simp only [Run.kind, Run.claimFields, Run.shownJson, List.append_nil, List.nil_append]; fits
      | certificate _ => simp [Shown.matches] at h
      | counterexample _ => simp [Shown.matches] at h
  · cases s with
    | nothing =>
      apply Fits.altTail; apply Fits.altTail; apply Fits.altTail; apply Fits.altTail; apply Fits.altTail
      apply Fits.altTail; apply Fits.altHead
      simp only [Run.kind, Run.claimFields, Run.shownJson, List.append_nil, List.nil_append]
      rcases u with l | _ | _ | _ | _ | _
      · cases l <;> fits
      all_goals fits
    | certificate _ => simp [Shown.matches] at h
    | counterexample _ => simp [Shown.matches] at h))

/-- A row: a decided outcome with no reason, or an unknown one with Lean's reason text. -/
theorem rowJson_fits (ds : List Decl) (id : String) (named : String → Option String)
    (σ : String → Val) (k : Check) (r : Row)
    (h : match k with | .claim _ => True | .follows .. => Shown.matches r.outcome r.shown = true) :
    Fits req (skel% "calc.json#/$defs/claim_row") (Run.rowJson ds id named σ k r) := by
  rcases r with ⟨_, o, s, p⟩
  row_fits

/-- The same, with the reproduction `"unknown"` of a case under a software convention. -/
theorem rowJson_fits_software (ds : List Decl) (id : String) (named : String → Option String)
    (σ : String → Val) (k : Check) (r : Row)
    (h : r.reproduction.isSome)
    (hm : match k with | .claim _ => True | .follows .. => Shown.matches r.outcome r.shown = true) :
    Fits req (skel% "calc.json#/$defs/claim_row_software") (Run.rowJson ds id named σ k r) := by
  rcases r with ⟨_, o, s, p⟩
  cases p with
  | none => cases h
  | some _ =>
    rename_i p
    have h := hm
    row_fits

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
      refine rowJson_fits_software _ _ _ _ _ _ ?_ ?_
      · simpa [Run.row] using hs
      · exact Run.row_matches _ _
    · fits
  · refine Fits.onCaseT hl ?_
    split
    · fits
      obtain ⟨i, hi, rfl⟩ := List.mem_mapIdx.mp ‹_›
      exact rowJson_fits _ _ _ _ _ _ (Run.row_matches _ _)
    · fits

end ResponseShape.Encoders.Calc
