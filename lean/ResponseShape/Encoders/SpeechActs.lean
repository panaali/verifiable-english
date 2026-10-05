import ResponseShape.Encoders.Norms

/-! The `speech-acts` mode (`SpeechActs.Run.runCaseReported`) against `speech-acts.json#/row`. A
case off the speech-acts path is the norms mode's. -/

namespace ResponseShape.Encoders.SpeechActs
open Lean ResponseShape ResponseShape.Skeletons
open VE.SpeechActs VE.SpeechActs.Run

theorem of_norms {v : Json} (h : Fits Γ Skeletons.norms v) : Fits Γ Skeletons.speechActs v := by
  refine Fits.altSub ?_ h
  alt_sub

theorem elaborate_fits (id : String) (dec : Wire.Decoded) :
    Fits Γ (skel% "speech-acts.json#/$defs/elaborate") (VE.Route.Wire.ok id (elaborated dec)) := by
  unfold VE.Route.Wire.ok elaborated Wire.encodeScope encodeNode questionJson VE.Norms.Wire.regenerated
  simp only []
  fits

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

theorem runCase_fits (j : Json) : OkFits Γ Skeletons.speechActs (runCase j) := by
  unfold runCase
  simp only []
  okfits
  all_goals first
    | (fits_as "speech-acts.json#/$defs/elaborate"; with_reducible exact elaborate_fits _ _)
    | exact OkP.of (Norms.runCase_fits j) fun _ => of_norms
    | skip
  all_goals (try simp only [VE.Route.Wire.ok])
  all_goals fits
  -- Not conflict-free with no failing target: impossible (`firstFailure_of_not_free`).
  all_goals
    exfalso
    have := firstFailure_of_not_free j _ ‹replayConflict j = .ok _› (by simp_all)
    simp_all

theorem runCaseReported_fits (j : Json) : Fits Γ Skeletons.speechActs (runCaseReported j) := by
  unfold runCaseReported
  split
  · split
    · exact runCase_fits j _ ‹_›
    · fits
  · exact of_norms (Norms.runCaseReported_fits j)

end ResponseShape.Encoders.SpeechActs
