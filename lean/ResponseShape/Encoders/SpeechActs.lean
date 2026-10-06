import ResponseShape.Encoders.Norms

/-! The `speech-acts` mode (`SpeechActs.Run.runCaseReported`) against `speech-acts.json#/row`. A
case off the speech-acts path is the norms mode's. -/

namespace ResponseShape.Encoders.SpeechActs
open Lean ResponseShape ResponseShape.Skeletons
open VE.SpeechActs VE.SpeechActs.Run

variable {req : Json}

/-- The norms mode's rows, off the speech-acts path, are rows of this mode. -/
theorem of_norms {v : Json} (hp : usesSpeechPath req = false) (h : Fits req Skeletons.norms v) :
    Fits req Skeletons.speechActs v :=
  Fits.onCaseE (by simpa [CaseCond.holds, CaseDecider.fn] using hp) h

/-- A question's fields are its mode's (`questionJson` per `Mode`). -/
theorem question_fits (D : SpeechDoc) (q : Question) (m : String) :
    Fits req (skel% "speech-acts.json#/$defs/question") ((questionJson D q).setObjVal! "meaning_id" (.str m)) := by
  obtain ⟨u, mode, body, sort, domain, query, rs⟩ := q
  cases mode <;> simp only [questionJson, Wire.modeName, List.cons_append, List.nil_append] <;> fits

theorem elaborate_fits (id : String) (dec : Wire.Decoded) :
    Fits req (skel% "speech-acts.json#/$defs/elaborate") (VE.Route.Wire.ok id (elaborated dec)) := by
  unfold VE.Route.Wire.ok elaborated Wire.encodeScope encodeNode VE.Norms.Wire.regenerated
  simp only []
  fits using question_fits

theorem firstFailure_of_not_free (j : Json) (res : ConflictCase) (h : replayConflict j = .ok res)
    (hf : res.conflictFree = false) : (firstFailure res).isSome = true := by
  unfold replayConflict at h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨dec, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  cases h
  simp only [ConflictCase.conflictFree, VE.Norms.conflictFreeCheck, List.length_map, beq_self_eq_true,
    Bool.true_and, List.all_eq_false] at hf
  obtain ⟨⟨t, c⟩, hm, hc⟩ := hf
  simp only [firstFailure, Option.isSome_map]
  rw [List.find?_isSome]
  exact ⟨(t, c), hm, by cases c <;> simp_all⟩

theorem runCase_fits (j : Json) (hp : usesSpeechPath j = true) : OkFits j Skeletons.speechActs (runCase j) := by
  unfold runCase
  simp only []
  okfits
  all_goals first
    | (exfalso; simp_all; done)
    | read_kind
  all_goals (try contra)
  all_goals first
    | fits_from elaborate_fits _ _
    | ((try simp only [VE.Route.Wire.ok]); fits)
  -- Not conflict-free with no failing target: impossible (`firstFailure_of_not_free`).
  all_goals
    exfalso
    have := firstFailure_of_not_free j _ ‹replayConflict j = .ok _› (by simp_all)
    simp_all

theorem runCaseReported_fits (j : Json) (hj : CaseWF j) : Fits j Skeletons.speechActs (runCaseReported j) := by
  unfold runCaseReported
  split
  · split
    · exact runCase_fits j ‹_› _ ‹_›
    · fits
  · exact of_norms (Bool.eq_false_iff.mpr ‹_›) (Norms.runCaseReported_fits j hj)

end ResponseShape.Encoders.SpeechActs
