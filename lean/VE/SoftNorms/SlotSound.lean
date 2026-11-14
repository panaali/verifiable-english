import VE.SoftNorms.Run

/-! The wire theorems of the soft route's slot kinds `slot-certificate` and `slot-conflict` (kb-3, kernel
boundary 4.2).

Each states the whole answer as one equation: it is `slotCertificateAnswer`, `slotWitnessAnswer` or
`slotConflictAnswer` (`Run.lean`) of a successful slot replay of the case itself
(`VE.Compose.SlotWire`), of the case's own id, the request's `facts` sent, and, for the conflict-free
answer, the case's budget and, when it says a coherent situation is exhibited, the request's
`coherent_model` decoded and passing the soft background and every fact. So the answer's `valid` is
the replay's `SlotEntailmentReplay.valid`, its `verdict` is `CONFLICT` or `CONFLICT-FREE` exactly when the
replay's `conflict` or `conflictFree` is true, and the replay theorems (`slot_wire_acceptance`,
`slot_wire_conflict_sound`, `slot_wire_conflict_witness_sound`, `slot_wire_entailment_facts`,
`slot_wire_conflict_facts`) say what that means. -/
namespace VE.SoftNorms.Run
open Lean
open VE.Norms
open VE.SoftNorms.Wire
open VE.Compose.SlotWire
open VE.Order.ProfileGate (bind_ok)

theorem needFacts_ok {j : Json} {u : Unit} (h : needFacts j = .ok u) : (j.getObjVal? "facts").toBool = true := by
  unfold needFacts at h
  split at h
  · assumption
  · cases h

/-- The `slot-certificate` answer: from raw JSON, a successful answer is `slotCertificateAnswer` of the
case's id, a successful slot replay of the case and the case's open coherence labels. -/
theorem slot_wire_certificate (j answer : Json) (h : runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "slot-certificate") (hn : usesSoftPath j = true) :
    ∃ (id : String) (r : SlotEntailmentReplay) (openLabels : List String),
      VE.Bridge.stringField j "id" = .ok id ∧ (j.getObjVal? "facts").toBool = true ∧
      replaySlotEntailment j = .ok r ∧
      openAfterClassification r.src (j.getObjValD "environment") (j.getObjValD "norms") (j.getObjValD "pairs") =
        .ok openLabels ∧
      answer = slotCertificateAnswer id r openLabels := by
  unfold runCase at h
  obtain ⟨id, hid, h⟩ := bind_ok h
  obtain ⟨kind, hkind, h⟩ := bind_ok h
  have heq : kind = "slot-certificate" := by rw [hkind] at hk; cases hk; rfl
  subst heq
  simp only [hn, show ("slot-certificate" == "admission") = false from by decide, Bool.false_and,
    Bool.not_true, Bool.false_eq_true, ↓reduceIte] at h
  unfold runSoftKind at h
  simp only [show ("slot-certificate" == "soft-selected") = false from by decide,
    show ("slot-certificate" == "soft-rule") = false from by decide,
    show ("slot-certificate" == "soft-rules") = false from by decide,
    show ("slot-certificate" == "soft-elaborate") = false from by decide,
    show ("slot-certificate" == "soft-pairs") = false from by decide,
    show ("slot-certificate" == "soft-certificate") = false from by decide,
    show ("slot-certificate" == "soft-conflict") = false from by decide,
    show ("slot-certificate" == "slot-certificate") = true from by decide,
    Bool.false_and, Bool.false_eq_true, ↓reduceIte, pure_bind] at h
  obtain ⟨_, hf, h⟩ := bind_ok h
  obtain ⟨r, hr, h⟩ := bind_ok h
  obtain ⟨openLabels, ho, h⟩ := bind_ok h
  simp only [pure, Except.pure, Except.ok.injEq] at h
  exact ⟨id, r, openLabels, hid, needFacts_ok hf, hr, ho, h.symm⟩

/-- The `slot-conflict` answer: from raw JSON, a successful answer is, with a `witness`,
`slotWitnessAnswer` of a successful slot witness replay and the witness's tuple; without one,
`slotConflictAnswer` of a successful slot conflict replay, the case's open coherence labels and budget,
and an exhibit flag that is true only for a `coherent_model` in which the soft background and every fact
hold. -/
theorem slot_wire_conflict (j answer : Json) (h : runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "slot-conflict") (hn : usesSoftPath j = true) :
    ∃ id : String, VE.Bridge.stringField j "id" = .ok id ∧ (j.getObjVal? "facts").toBool = true ∧
      ((∃ (r : SlotWitnessReplay) (names : List String),
          (j.getObjVal? "witness").toBool = true ∧ replaySlotWitness j = .ok r ∧
          VE.Bridge.strings ((j.getObjValD "witness").getObjValD "tuple") = .ok names ∧
          answer = slotWitnessAnswer id r names) ∨
       (∃ (res : SlotConflictReplay) (openLabels : List String) (exhibit : Bool),
          (j.getObjVal? "witness").toBool = false ∧ replaySlotConflict j = .ok res ∧
          openAfterClassification res.src (j.getObjValD "environment") (j.getObjValD "norms")
            (j.getObjValD "pairs") = .ok openLabels ∧
          (exhibit = true → ∃ (M : VE.FiniteModel VE.Bridge.Entity) (hM : M.Valid (envAt (soften res.src.D) 0)),
            decodeModel res.src (Json.mkObj [("model", j.getObjValD "coherent_model")]) = .ok ⟨M, hM⟩ ∧
            VE.Compose.backgroundValidP res.src.D res.facts M = true) ∧
          answer = slotConflictAnswer id res openLabels ((j.getObjValD "budget").getNat?.toOption.getD 10000)
            exhibit)) := by
  unfold runCase at h
  obtain ⟨id, hid, h⟩ := bind_ok h
  obtain ⟨kind, hkind, h⟩ := bind_ok h
  have heq : kind = "slot-conflict" := by rw [hkind] at hk; cases hk; rfl
  subst heq
  simp only [hn, show ("slot-conflict" == "admission") = false from by decide, Bool.false_and,
    Bool.not_true, Bool.false_eq_true, ↓reduceIte] at h
  unfold runSoftKind at h
  simp only [show ("slot-conflict" == "soft-selected") = false from by decide,
    show ("slot-conflict" == "soft-rule") = false from by decide,
    show ("slot-conflict" == "soft-rules") = false from by decide,
    show ("slot-conflict" == "soft-elaborate") = false from by decide,
    show ("slot-conflict" == "soft-pairs") = false from by decide,
    show ("slot-conflict" == "soft-certificate") = false from by decide,
    show ("slot-conflict" == "soft-conflict") = false from by decide,
    show ("slot-conflict" == "slot-certificate") = false from by decide,
    show ("slot-conflict" == "slot-conflict") = true from by decide,
    Bool.false_and, Bool.true_and, Bool.false_eq_true, ↓reduceIte, pure_bind] at h
  refine ⟨id, hid, ?_⟩
  cases hw : (j.getObjVal? "witness").toBool
  · simp only [hw, Bool.false_eq_true, ↓reduceIte] at h
    obtain ⟨_, hf, h⟩ := bind_ok h
    obtain ⟨res, hres, h⟩ := bind_ok h
    obtain ⟨openLabels, ho, h⟩ := bind_ok h
    split at h
    · obtain ⟨⟨M, hM⟩, hd, h⟩ := bind_ok h
      simp only at h
      split at h
      · rename_i hb
        simp only [pure, Except.pure, Except.ok.injEq] at h
        exact ⟨needFacts_ok hf, .inr ⟨res, openLabels, true, rfl, hres, ho, fun _ => ⟨M, hM, hd, hb⟩, h.symm⟩⟩
      · cases h
    · simp only [pure, Except.pure, Except.ok.injEq] at h
      exact ⟨needFacts_ok hf, .inr ⟨res, openLabels, false, rfl, hres, ho, (fun he => nomatch he), h.symm⟩⟩
  · simp only [hw, ↓reduceIte] at h
    obtain ⟨_, hf, h⟩ := bind_ok h
    obtain ⟨r, hr, h⟩ := bind_ok h
    obtain ⟨names, hnames, h⟩ := bind_ok h
    simp only [pure, Except.pure, Except.ok.injEq] at h
    exact ⟨needFacts_ok hf, .inl ⟨r, names, rfl, hr, hnames, h.symm⟩⟩

end VE.SoftNorms.Run
