import ResponseShape.Encoders.Norms

/-! The `alternatives` mode (`Alternatives.Run.runCaseReported`) against `alternatives.json#/row`.
A case off the alternatives path is the norms mode's. -/

namespace ResponseShape.Encoders.Alternatives
open Lean ResponseShape ResponseShape.Skeletons
open VE.Alternatives VE.Alternatives.Run

variable {req : Json}

/-- The norms mode's rows, off the alternatives path, are rows of this mode. -/
theorem of_norms {v : Json} (hp : usesAltPath req = false) (h : Fits req Skeletons.norms v) :
    Fits req Skeletons.alternatives v :=
  Fits.onCaseE (by simpa [CaseCond.holds, CaseDecider.fn] using hp) h

/-- Every Background premise label of the alternatives document is one of the four. -/
theorem premiseLabels_mem (A : AltDoc) : ∀ s ∈ altPremiseLabels A,
    s ∈ ["alternatives:own", "alternatives:one_taken", "alternatives:one_inaction", "alternatives:proximate"] := by
  intro s hs
  simp only [altPremiseLabels, List.mem_cons, List.mem_append, List.mem_map] at hs
  rcases hs with rfl | ((⟨_, _, rfl⟩ | ⟨_, _, rfl⟩) | ⟨_, _, rfl⟩) <;> decide

theorem premiseLabels_fits (A : AltDoc) :
    Fits req (.arr [] (.strIn ["alternatives:own", "alternatives:one_taken", "alternatives:one_inaction",
      "alternatives:proximate"])) (toJson (altPremiseLabels A)) :=
  Fits.toJsonStrs (premiseLabels_mem A)

theorem labelled_fits {A : AltDoc} {p : String × VE.Formula} (h : p ∈ (altPremiseLabels A).zip (altPremises A)) :
    Fits req (.strIn ["alternatives:own", "alternatives:one_taken", "alternatives:one_inaction",
      "alternatives:proximate"]) (.str p.1) :=
  Fits.strIn (premiseLabels_mem A _ (List.of_mem_zip h).1)

theorem elaborate_fits (id : String) (src : Wire.AltSource) :
    Fits req (skel% "alternatives.json#/$defs/elaborate") (ok id (Wire.regenerated src)) := by
  unfold ok VE.Route.Wire.ok Wire.regenerated Wire.encodeNode Wire.labelled Wire.profileExists
    VE.Norms.Wire.regenerated profileWords profileDef
  simp only [List.filterMap_cons, List.filterMap_nil, String.reduceEq, ↓reduceIte, Bool.false_eq_true]
  fits using labelled_fits

theorem fields_obj {j : Json} {fs : VE.Bridge.Fields} (h : VE.Bridge.fields j = .ok fs) : ∃ m, j = .obj m := by
  cases j <;> first | exact ⟨_, rfl⟩ | (simp [VE.Bridge.fields, Json.getObj?] at h; cases h)

theorem optString_isSome {raw : Json} {k : String} {t : Option String} (h : Wire.optString raw k = .ok t) :
    t.isSome = (raw.getObjVal? k).toBool := by
  unfold Wire.optString at h
  split at h
  · rename_i hk; cases h; rw [hk]; rfl
  · rename_i hk; cases h; rw [hk]; rfl
  · cases h

set_option maxHeartbeats 4000000 in
/-- The decoded block's `taken` is set exactly when the block has the field `taken`. -/
theorem decodeBlock_taken (raw : Json) :
    OkP (fun b : Wire.Block => b.alt.taken.isSome = CaseCond.objectHas raw ["taken"]) (Wire.decodeBlock raw) := by
  unfold Wire.decodeBlock
  okfits
  all_goals
    obtain ⟨m, hm⟩ := fields_obj ‹VE.Bridge.fields raw = .ok _›
    simp only []
    rw [optString_isSome ‹Wire.optString raw "taken" = .ok _›, CaseCond.objectHas_one hm]

theorem decodeAltSource_taken (environment norms premises : Json) :
    OkP (fun src : Wire.AltSource => src.A.alt.taken.isSome = CaseCond.objectHas environment ["alternatives", "taken"])
      (Wire.decodeAltSource environment norms premises) := by
  unfold Wire.decodeAltSource
  okfits
  all_goals
    simp only []
    rw [CaseCond.objectHas_cons ‹environment.getObjVal? "alternatives" = .ok _›]
    exact decodeBlock_taken _ _ ‹Wire.decodeBlock _ = .ok _›

/-- The decoded document's `taken` is set exactly when the case's `environment.alternatives` has
the field `taken` (the condition of `alternatives.json#/$defs/chooser`). -/
theorem sourceOf_taken (j : Json) :
    OkP (fun src : Wire.AltSource =>
      src.A.alt.taken.isSome = (CaseCond.path ["environment", "alternatives", "taken"]).holds j)
      (Replay.sourceOf j) := by
  unfold Replay.sourceOf
  okfits
  refine OkP.of (decodeAltSource_taken _ _ _) fun src h => ?_
  rw [CaseCond.holds_path_cons ‹j.getObjVal? "environment" = .ok _›]
  exact h

theorem chooser_fits (A : AltDoc) (M : VE.FiniteModel VE.Bridge.Entity) (r : VE.Bridge.Entity)
    (hA : A.alt.taken.isSome = (CaseCond.path ["environment", "alternatives", "taken"]).holds req) :
    Fits req (skel% "alternatives.json#/$defs/chooser") (chooserReport A M r).1 := by
  unfold chooserReport ids
  simp only []
  fits
  -- `violations` and `breaches` exactly beside a case whose block names `taken`.
  all_goals first
    | exact hA ▸ ‹A.alt.taken.isSome = true›
    | exact hA ▸ Bool.eq_false_iff.mpr ‹¬ A.alt.taken.isSome = true›

theorem validate_fits (id : String) (j : Json) (hp : usesAltPath j = true)
    (hK : j.getObjValD "kind" = .str "alt-validate") : OkFits j Skeletons.alternatives (runValidate id j) := by
  unfold runValidate
  okfits
  all_goals (try simp only [ok, VE.Route.Wire.ok])
  all_goals fits
  all_goals exact chooser_fits _ _ _ (sourceOf_taken j _ ‹Replay.sourceOf j = .ok _›)

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

theorem conflict_fits (id : String) (j : Json) {w : Json} (hobj : j.getObjVal? "id" = .ok w)
    (hp : usesAltPath j = true) (hK : j.getObjValD "kind" = .str "alt-conflict") :
    OkFits j Skeletons.alternatives (runConflict id j) := by
  unfold runConflict runConflictWitness
  okfits
  all_goals (try simp only [ok, VE.Route.Wire.ok])
  all_goals fits
  all_goals
    exfalso
    have := firstFailure_of_not_free j _ ‹Replay.replayAltConflict j = .ok _› (by simp_all)
    simp_all

theorem followable_fits (id : String) (j : Json) {w : Json} (hobj : j.getObjVal? "id" = .ok w)
    (hp : usesAltPath j = true) (hK : j.getObjValD "kind" = .str "alt-followable") :
    OkFits j Skeletons.alternatives (runFollowable id j) := by
  unfold runFollowable
  okfits
  all_goals (try simp only [ok, VE.Route.Wire.ok])
  all_goals fits

/-- Every admission's kinds are its units' rendered kinds. -/
theorem admitDocument_kinds (environment document : Json) :
    OkP (fun res : Admission.Admitted => Common.KindsRendered res.kinds) (Admission.admitDocument environment document) := by
  unfold Admission.admitDocument
  okfits
  all_goals exact Common.kindsRendered_map _ _

theorem admission_fits (id reportId : String) (res : Admission.Admitted) (hk : Common.KindsRendered res.kinds) :
    Fits req (skel% "alternatives.json#/$defs/admission") (encodeAdmitted id reportId res) := by
  unfold encodeAdmitted ok VE.Route.Wire.ok
  fits using Common.kind_fits hk
  all_goals exact Common.claimJson_fits _

theorem runCase_fits (j : Json) (hp : usesAltPath j = true) : OkFits j Skeletons.alternatives (runCase j) := by
  unfold runCase
  okfits
  all_goals read_kind
  all_goals first
    | (unfold runAdmission; okfits; fits_from admission_fits _ _ _ (admitDocument_kinds _ _ _ ‹Admission.admitDocument _ _ = .ok _›))
    | fits_from elaborate_fits _ _
    | exact validate_fits _ _ hp ‹_›
    | exact conflict_fits _ _ ‹_› hp ‹_›
    | exact followable_fits _ _ ‹_› hp ‹_›
    | (simp only [ok, VE.Route.Wire.ok]; fits using premiseLabels_fits)

theorem runCaseReported_fits (j : Json) (hj : CaseWF j) : Fits j Skeletons.alternatives (runCaseReported j) := by
  unfold runCaseReported
  split
  · split
    · exact runCase_fits j ‹_› _ ‹_›
    · fits
  · exact of_norms (Bool.eq_false_iff.mpr ‹_›) (Norms.runCaseReported_fits j hj)

end ResponseShape.Encoders.Alternatives
