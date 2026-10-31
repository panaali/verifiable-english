import ResponseShape.Encoders.Norms
import VE.NormDefaults.PacksLegacy

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
    VE.NormDefaults.Packs.elaborateArrays, VE.NormDefaults.Packs.labelledJson, List.append_nil, Wire.ReportG.toJson, Wire.conflictFields, Wire.statusFields, Wire.underJson, Wire.atomsJson])
  all_goals fits using line_fits
  all_goals try
    exfalso
    have := firstFailureX_of_not_free _ _ (by
      first | exact ‹Wire.conflictFreeX _ _ = false› | exact Bool.eq_false_iff.mpr ‹¬Wire.conflictFreeX _ _ = true›)
    simp_all

/-! A9′ (docs/spec/premise-packs.md 2.7): `layered_elaborate` is closed, and `layeredCase_fits` holds for every
`LayeredU` because the keys `Packs.elaborateArrays` writes are `soft` and `rights` whatever the packs
(`Packs.elaborateArrays_keys`). Read from the shape itself: it has every key the layered elaborate writes for a
further-pack list, and no further pack's id, so a further pack's entry needs its own shape row (AT-2). -/
#guard
  let keys : List String := match ResponseShape.Schemas.NormDefaults.layered_elaborate with
    | .node _ kws => kws.flatMap fun (k : ResponseShape.Shape) => match k with
      | .object ps (some (.bool false)) => ps.map (fun (p : String × ResponseShape.Shape) => p.1)
      | _ => []
    | _ => []
  let further : List VE.NormDefaults.Packs.Pack :=
    ["soft", "weighing", "events"].map (⟨·, .constraint, [], [], [], []⟩)
  ["soft", "rights", "base_environment"].all keys.contains &&
    (VE.NormDefaults.Packs.elaborateArrays further).all (keys.contains ·.1) &&
    !VE.NormDefaults.Packs.packOrder.any (fun i => i != "soft" && i != "rights" && keys.contains i)

/-- The kind table's dispatch answers what the row it finds answers. -/
theorem dispatch_okP {α : Type} (rows : List (Packs.KindRow α)) (ids : List String) (L : α) (id kind : String)
    (j : Json) {P : Json → Prop} (h : ∀ r ∈ rows, r.kind = kind → OkP P (r.run L id j)) :
    OkP (fun o => ∀ a, o = some a → P a) (Packs.dispatch rows ids L id kind j) := by
  unfold Packs.dispatch
  split
  · exact OkP.pure (fun _ h => by cases h)
  · rename_i r hf
    have hr := h r (List.mem_of_find?_eq_some hf) (by simpa using List.find?_some hf)
    have hm : OkP (fun o => ∀ a, o = some a → P a) (some <$> r.run L id j) :=
      OkP.mapOf hr (fun a ha b hb => by cases hb; exact ha)
    split
    · exact OkP.ite (fun _ => hm) (fun _ => OkP.throw)
    · exact hm

/-- A checked collision is the request's, and names a colliding pair. -/
theorem collides_named (x : VE.Defaults.Wire.CoherenceReplay) (h : x.collides = true) :
    ∃ w P Q, x.collision = some w ∧
      (VE.SoftNorms.collidingPairs x.v.L.D).find? (fun p => p.1.name == w.m && p.2.name == w.n) = some (P, Q) := by
  unfold VE.Defaults.Wire.CoherenceReplay.collides at h
  split at h
  · rename_i w hw
    unfold VE.Defaults.collisionCheck at h
    split at h
    · cases h
    · rename_i P Q hf
      exact ⟨w, P, Q, hw, hf⟩
  · cases h

open VE.Defaults.Wire in
theorem defaultsCase_fits (v : DefaultsView) (id kind : String) (j : Json)
    (hi : VE.Bridge.stringField j "id" = .ok id)
    (hk : VE.Route.Run.caseKind j = .ok kind) (hp : usesNormDefaultsPath j = true) :
    OkP (fun o => ∀ a, o = some a → Fits j Skeletons.normDefaults a) (defaultsCase v id kind j) := by
  unfold defaultsCase
  repeat' (apply OkP.ite <;> intro _)
  all_goals first
    | (refine OkP.map (fun x a ha => ?_); cases ha)
    | (apply OkP.pure; intro a ha; cases ha)
  all_goals read_kind
  all_goals simp only [VE.Route.Wire.ok, elaborateFields, coherenceFields, collisionFields, certFields, modelFields, situationJson,
    CoherenceReplay.verdict, CertReplay.verdict, ModelReplay.verdict, PairStatus.label, basisLabel, formLabel,
    entityIds, VE.NormDefaults.Wire.witnessRow]
  · fits
  · by_cases h1 : x.coherent = true
    · simp only [h1, ↓reduceIte, String.reduceBEq]; fits
    by_cases h2 : x.collides = true
    · obtain ⟨w, P, Q, hw, hf⟩ := collides_named x h2
      simp only [h1, h2, hw, hf, ↓reduceIte, Bool.false_eq_true, String.reduceBEq]; fits
    · simp only [h1, h2, ↓reduceIte, Bool.false_eq_true, String.reduceBEq]; fits
  · by_cases h : (x.certOk && x.coherent && x.modelOk) = true <;>
      simp only [h, ↓reduceIte, Bool.false_eq_true, String.reduceBEq, beq_self_eq_true] <;> fits
  · by_cases h : x.ok = true <;> simp only [h, ↓reduceIte, Bool.false_eq_true] <;> fits

theorem layeredKindCase_fits (L : Wire.LayeredU) (id kind : String) (j : Json)
    (hi : VE.Bridge.stringField j "id" = .ok id)
    (hk : VE.Route.Run.caseKind j = .ok kind) (hp : usesNormDefaultsPath j = true) :
    OkP (fun o => ∀ a, o = some a → Fits j Skeletons.normDefaults a) (Wire.layeredKindCase L id kind j) := by
  refine dispatch_okP _ _ L id kind j (fun r hr hrk => ?_)
  rcases List.mem_append.mp hr with hr | hr
  · obtain ⟨k, -, rfl⟩ := List.mem_map.mp hr
    cases hrk
    refine OkP.bind (fun o ho => ?_)
    cases o with
    | none => exact OkP.throw
    | some a => exact OkP.pure (layeredCase_fits L id _ j hi hk hp _ ho _ rfl)
  · obtain ⟨k, -, rfl⟩ := List.mem_map.mp hr
    cases hrk
    refine OkP.bind (fun v _ => OkP.bind (fun o ho => ?_))
    cases o with
    | none => exact OkP.throw
    | some a => exact OkP.pure (defaultsCase_fits v id _ j hi hk hp _ ho _ rfl)

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
    exact layeredKindCase_fits L id kind j hi hk hp _ ho _ rfl

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
    VE.Norms.Run.wordingsJson, Wire.ReportG.toJson, Wire.conflictFields, Wire.statusFields, Wire.underJson, Wire.atomsJson])
  all_goals fits using line_fits
  all_goals try exact Common.claimJson_fits _
  all_goals try exact Common.kind_fits (admitDocument_kinds _ _ _ ‹Admission.admitDocument _ _ = .ok _›) ‹_›
  -- Not conflict-free with no failing target: impossible (`firstFailure_of_not_free`).
  all_goals try
    exfalso
    have := firstFailure_of_not_free j _ ‹Wire.replayConflictU j = .ok _› (by simp_all)
    simp_all

theorem runGated_fits (j : Json) (hp : usesNormDefaultsPath j = true) :
    OkFits j Skeletons.normDefaults (runGated j) := by
  unfold runGated
  split
  · exact OkP.error
  · split
    · exact OkP.error
    · exact runCase_fits j hp

theorem runCaseReported_fits (j : Json) (hj : CaseWF j) : Fits j Skeletons.normDefaults (runCaseReported j) := by
  unfold runCaseReported
  split
  · split
    · exact runGated_fits j ‹_› _ ‹_›
    · fits
  · exact of_norms (Bool.eq_false_iff.mpr ‹_›) (Norms.runCaseReported_fits j hj)

end ResponseShape.Encoders.NormDefaults
