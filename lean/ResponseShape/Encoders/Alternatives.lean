import ResponseShape.Encoders.Norms

/-! The `alternatives` mode (`Alternatives.Run.runCaseReported`) against `alternatives.json#/row`.
A case off the alternatives path is the norms mode's. -/

namespace ResponseShape.Encoders.Alternatives
open Lean ResponseShape ResponseShape.Skeletons
open VE.Alternatives VE.Alternatives.Run

theorem of_norms {v : Json} (h : Fits Γ Skeletons.norms v) : Fits Γ Skeletons.alternatives v := by
  refine Fits.altSub ?_ h
  alt_sub

theorem elaborate_fits (id : String) (src : Wire.AltSource) :
    Fits Γ Skeletons.alternatives (ok id (Wire.regenerated src)) := by
  unfold ok VE.Route.Wire.ok Wire.regenerated Wire.encodeNode Wire.labelled Wire.profileExists
    VE.Norms.Wire.regenerated profileWords profileDef
  simp only [List.filterMap_cons, List.filterMap_nil, String.reduceEq, ↓reduceIte, Bool.false_eq_true]
  fits

theorem chooser_fits (A : AltDoc) (M : VE.FiniteModel VE.Bridge.Entity) (r : VE.Bridge.Entity) :
    Fits Γ (skel% "alternatives.json#/$defs/chooser") (chooserReport A M r).1 := by
  unfold chooserReport ids
  simp only []
  fits

theorem validate_fits (id : String) (j : Json) : OkFits Γ Skeletons.alternatives (runValidate id j) := by
  unfold runValidate
  okfits
  all_goals (try simp only [ok, VE.Route.Wire.ok])
  all_goals fits
  all_goals exact chooser_fits _ _ _

theorem firstFailure_of_not_free (j : Json) (res : Replay.AltConflictReplay)
    (h : Replay.replayAltConflict j = .ok res) (hf : res.conflictFree = false) :
    (Replay.firstFailure res).isSome = true := by
  unfold Replay.replayAltConflict at h
  obtain ⟨src, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  cases h
  simp only [Replay.AltConflictReplay.conflictFree, altConflictFreeCheck, Replay.conflictCerts, List.length_map,
    beq_self_eq_true, Bool.true_and, List.all_eq_false] at hf
  obtain ⟨⟨t, c⟩, hm, hc⟩ := hf
  simp only [Replay.firstFailure, Option.isSome_map]
  rw [List.find?_isSome]
  exact ⟨(t, c), by simpa [Replay.conflictCerts] using hm, by cases c <;> simp_all⟩

theorem conflict_fits (id : String) (j : Json) : OkFits Γ Skeletons.alternatives (runConflict id j) := by
  unfold runConflict runConflictWitness
  okfits
  all_goals (try simp only [ok, VE.Route.Wire.ok])
  all_goals fits
  all_goals
    exfalso
    have := firstFailure_of_not_free j _ ‹Replay.replayAltConflict j = .ok _› (by simp_all)
    simp_all

theorem followable_fits (id : String) (j : Json) : OkFits Γ Skeletons.alternatives (runFollowable id j) := by
  unfold runFollowable
  okfits
  all_goals (try simp only [ok, VE.Route.Wire.ok])
  all_goals fits

theorem admission_fits (id reportId : String) (res : Admission.Admitted) :
    Fits Γ Skeletons.alternatives (encodeAdmitted id reportId res) := by
  unfold encodeAdmitted ok VE.Route.Wire.ok
  fits
  all_goals exact Common.claimJson_fits _

theorem runCase_fits (j : Json) : OkFits Γ Skeletons.alternatives (runCase j) := by
  unfold runCase
  okfits
  all_goals first
    | (unfold runAdmission; okfits; exact admission_fits _ _ _)
    | with_reducible exact elaborate_fits _ _
    | with_reducible exact validate_fits _ _
    | with_reducible exact conflict_fits _ _
    | with_reducible exact followable_fits _ _
    | (simp only [ok, VE.Route.Wire.ok]; fits)

theorem runCaseReported_fits (j : Json) : Fits Γ Skeletons.alternatives (runCaseReported j) := by
  unfold runCaseReported
  split
  · split
    · exact runCase_fits j _ ‹_›
    · fits
  · exact of_norms (Norms.runCaseReported_fits j)

end ResponseShape.Encoders.Alternatives
