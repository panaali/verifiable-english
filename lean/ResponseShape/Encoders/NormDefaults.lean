import ResponseShape.Encoders.Norms

set_option maxHeartbeats 1000000

/-! The `norm-defaults` mode (`NormDefaults.Run.runCaseReported`) against `norm-defaults.json#/row`.
A case off the norm-defaults path is the norms mode's. -/

namespace ResponseShape.Encoders.NormDefaults
open Lean ResponseShape ResponseShape.Skeletons
open VE.NormDefaults VE.NormDefaults.Run

variable {req : Json}

/-- The norms mode's rows, off the norm-defaults path, are rows of this mode. -/
theorem of_norms {v : Json} (hp : usesNormDefaultsPath req = false) (h : Fits req Skeletons.norms v) :
    Fits req Skeletons.normDefaults v :=
  Fits.onCaseE (by simpa [CaseCond.holds, CaseDecider.fn] using hp) h

theorem firstFailure_of_not_free (j : Json) (res : Wire.ConflictReplayU) (h : Wire.replayConflictU j = .ok res)
    (hf : res.conflictFree = false) : (firstFailureU res).isSome = true := by
  unfold Wire.replayConflictU at h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨s, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  cases h
  simp only [Wire.ConflictReplayU.conflictFree, Wire.conflictFreeCheckU, List.length_map, beq_self_eq_true,
    Bool.true_and, List.all_eq_false] at hf
  obtain ⟨⟨t, c⟩, hm, hc⟩ := hf
  simp only [firstFailureU, Option.isSome_map]
  rw [List.find?_isSome]
  exact ⟨(t, c), hm, by cases c <;> simp_all⟩

/-- Every admission's kinds are its units' rendered kinds. -/
theorem admitDocument_kinds (environment document : Json) :
    OkP (fun res : Admission.Admitted => Common.KindsRendered res.kinds) (Admission.admitDocument environment document) := by
  unfold Admission.admitDocument
  okfits
  all_goals exact Common.kindsRendered_map _ _

theorem firstFailureX_of_not_free (L : Wire.LayeredU) (packages : Json) (hf : Wire.conflictFreeX L packages = false) :
    (Wire.firstFailureX L packages).isSome = true := by
  simp only [Wire.conflictFreeX, List.all_eq_false] at hf
  obtain ⟨t, hm, ht⟩ := hf
  simp only [Wire.firstFailureX, Option.isSome_map]
  rw [List.find?_isSome]
  exact ⟨t, hm, by simpa using ht⟩

theorem line_fits {U X cited translation} (l : Wire.LineU U X cited translation) :
    Fits req (skel% "norm-defaults.json#/$defs/report_line") l.toJson := by
  unfold Wire.LineU.toJson
  split <;> (try simp only [Wire.WitnessRow.toJson]) <;> fits

theorem layeredCase_fits (L : Wire.LayeredU) (id kind : String) (j : Json)
    (hi : VE.Bridge.stringField j "id" = .ok id)
    (hk : VE.Route.Run.caseKind j = .ok kind) (hp : usesNormDefaultsPath j = true) :
    OkP (fun o => ∀ a, o = some a → Fits j Skeletons.normDefaults a) (Wire.layeredCase L id kind j) := by
  unfold Wire.layeredCase
  okfits
  all_goals (try (intro a ha; cases ha))
  all_goals (try (intro a ha; injection ha with ha; subst ha))
  all_goals read_kind
  all_goals (try simp only [VE.Route.Wire.ok, Wire.layeredElaborate, Wire.regeneratedU, VE.Norms.Wire.regenerated,
    Wire.ReportG.toJson, Wire.conflictFields, Wire.statusFields, Wire.underJson, Wire.atomsJson])
  all_goals fits using line_fits
  all_goals try
    exfalso
    have := firstFailureX_of_not_free _ _ (by
      first | exact ‹Wire.conflictFreeX _ _ = false› | exact Bool.eq_false_iff.mpr ‹¬Wire.conflictFreeX _ _ = true›)
    simp_all

theorem runLayered_fits (id kind : String) (j : Json)
    (hi : VE.Bridge.stringField j "id" = .ok id)
    (hk : VE.Route.Run.caseKind j = .ok kind) (hp : usesNormDefaultsPath j = true) :
    OkFits j Skeletons.normDefaults (Wire.runLayered id kind j) := by
  unfold Wire.runLayered
  intro v hv
  obtain ⟨L, -, hv⟩ := VE.Order.ProfileGate.bind_ok hv
  obtain ⟨o, ho, hv⟩ := VE.Order.ProfileGate.bind_ok hv
  cases o with
  | none => cases hv
  | some a =>
    cases hv
    exact layeredCase_fits L id kind j hi hk hp _ ho _ rfl

/-- Every soft-branch admission's kinds are its units' rendered kinds. -/
theorem admitDocumentX_kinds (environment document : Json) :
    OkP (fun res : Admission.AdmittedX => Common.KindsRendered res.kinds)
      (Admission.admitDocumentX environment document) := by
  unfold Admission.admitDocumentX
  okfits
  all_goals exact Common.kindsRendered_map _ _

theorem softAdmission_fits (id reportId : String) (res : Admission.AdmittedX) (hk : Common.KindsRendered res.kinds) :
    Fits req (skel% "norm-defaults.json#/$defs/soft_admission") (Admission.encodeAdmittedX id reportId res) := by
  unfold Admission.encodeAdmittedX VE.Route.Wire.ok
  fits using Common.kind_fits hk
  all_goals exact Common.claimJson_fits _

theorem runAdmissionX_fits (id : String) (j environment document : Json)
    (hi : VE.Bridge.stringField j "id" = .ok id)
    (hk : VE.Route.Run.caseKind j = .ok "admission") (hp : usesNormDefaultsPath j = true) :
    OkFits j Skeletons.normDefaults (Admission.runAdmissionX id environment document) := by
  unfold Admission.runAdmissionX
  okfits
  read_kind
  fits_from softAdmission_fits _ _ _ (admitDocumentX_kinds _ _ _ ‹Admission.admitDocumentX _ _ = .ok _›)

theorem softCase_fits (id kind : String) (j : Json)
    (hi : VE.Bridge.stringField j "id" = .ok id)
    (hk : VE.Route.Run.caseKind j = .ok kind) (hp : usesNormDefaultsPath j = true) :
    OkP (fun o => ∀ a, o = some a → Fits j Skeletons.normDefaults a) (Admission.softCase id kind j) := by
  unfold Admission.softCase
  okfits
  all_goals (try (intro a ha; cases ha))
  all_goals (try (intro a ha; injection ha with ha; subst ha))
  · have hka : kind = "admission" := by simpa using ‹(kind == "admission") = true›
    subst hka
    exact runAdmissionX_fits id j _ _ hi hk hp _ ‹_›
  · read_kind
    simp only [VE.Route.Wire.ok]
    fits

theorem runCase_fits (j : Json) (hp : usesNormDefaultsPath j = true) :
    OkFits j Skeletons.normDefaults (runCase j) := by
  unfold runCase runOtherCase runAdmission
  simp only []
  okfits
  all_goals first
    | with_reducible exact OkP.of (Norms.runCase_fits _) fun _ => of_norms
    | with_reducible exact runLayered_fits _ _ _ ‹_› ‹_› hp
    | exact softCase_fits _ _ _ ‹_› ‹_› hp _ ‹_› _ rfl
    | skip
  all_goals read_kind
  all_goals (try contra)
  all_goals (try simp only [VE.Route.Wire.ok, encodeAdmitted, Wire.regeneratedU, VE.Norms.Wire.regenerated,
    Wire.ReportG.toJson, Wire.conflictFields, Wire.statusFields, Wire.underJson, Wire.atomsJson])
  all_goals fits using line_fits
  all_goals try exact Common.claimJson_fits _
  all_goals try exact Common.kind_fits (admitDocument_kinds _ _ _ ‹Admission.admitDocument _ _ = .ok _›) ‹_›
  -- Not conflict-free with no failing target: impossible (`firstFailure_of_not_free`).
  all_goals try
    exfalso
    have := firstFailure_of_not_free j _ ‹Wire.replayConflictU j = .ok _› (by simp_all)
    simp_all

theorem runCaseReported_fits (j : Json) (hj : CaseWF j) : Fits j Skeletons.normDefaults (runCaseReported j) := by
  unfold runCaseReported
  split
  · split
    · exact runCase_fits j ‹_› _ ‹_›
    · fits
  · exact of_norms (Bool.eq_false_iff.mpr ‹_›) (Norms.runCaseReported_fits j hj)

end ResponseShape.Encoders.NormDefaults
