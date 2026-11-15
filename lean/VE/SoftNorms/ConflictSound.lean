import VE.SoftNorms.ElaborateSound

/-! The wire theorems of the soft route's `soft-conflict` kind (kernel boundary; kb-10c).

`Wire.soft_wire_conflict_sound` and `Wire.soft_wire_conflict_witness_sound` are about the replays
`replaySoftConflict` and `replaySoftWitness`. This file ties them to the answer of the subject
`runCase`: a `soft-conflict` answer whose `verdict`, read by key as a client reads it, is
`CONFLICT-FREE` comes from a package replay that accepted every target certificate, and one whose
verdict is `CONFLICT` comes from a witness replay whose target formula holds at the witness tuple.
The two cannot both be answered for one document (`soft_wire_conflict_exclusive`).

What CONFLICT-FREE means here is `SoftConflictFree`: no two rules on the same act conflict over any
base model of `Background_base′`, which includes the open coherence premises; the answer's
`conditional_on` names the open premises the certificates used. These theorems say nothing about the
other fields (`status_text`, `conditional_on`, `coherent_exhibit`, `budget`, `targets`, `detail`,
`target`, `witness_kind`), and nothing about an `UNKNOWN` answer. -/

namespace VE.SoftNorms.Run
open Lean
open VE.Norms
open VE.SoftNorms.Wire
open VE.Order.ProfileGate (bind_ok)

/-- The `verdict` of a `Wire.ok` answer whose first field is the verdict, when no later field
binds `verdict` again. -/
theorem ok_verdict (id v : String) (rest : List (String × Json)) (hr : "verdict" ∉ rest.map (·.1)) :
    (VE.Route.Wire.ok id (("verdict", .str v) :: rest)).getObjValD "verdict" = .str v := by
  unfold VE.Route.Wire.ok
  have hl : [("id", Json.str id), ("status", Json.str "ok")] ++ ("verdict", Json.str v) :: rest =
      [("id", Json.str id), ("status", Json.str "ok"), ("verdict", Json.str v)] ++ rest := rfl
  rw [hl]
  have hd : ([("id", Json.str id), ("status", Json.str "ok"), ("verdict", Json.str v)].map (·.1)).Nodup := by
    simp
  have hg := mkObj_get_append (k := "verdict") (v := Json.str v) hd (by simp) hr
  simp only [Json.getObjValD, hg]
  rfl

/-- What a successful `soft-conflict` answer is, read at its `verdict`: with a `witness` field,
the verdict of a successful witness replay (`CONFLICT` exactly when the target formula holds at the
tuple, else `UNKNOWN`); without one, the verdict of a successful package replay (`CONFLICT-FREE`
exactly when every target certificate is accepted, else `UNKNOWN`). -/
theorem soft_conflict_verdict (j answer : Json) (h : runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "soft-conflict") (hn : usesSoftPath j = true) :
    ((j.getObjVal? "witness").toBool = true ∧
      ∃ (src : SoftSource) (w : SoftWitnessData src), replaySoftWitness j = .ok ⟨src, w⟩ ∧
        answer.getObjValD "verdict" = .str (if w.conflict then "CONFLICT" else "UNKNOWN")) ∨
    ((j.getObjVal? "witness").toBool = false ∧
      ∃ res : SoftConflictReplay, replaySoftConflict j = .ok res ∧
        answer.getObjValD "verdict" = .str (if res.conflictFree then "CONFLICT-FREE" else "UNKNOWN")) := by
  unfold runCase at h
  obtain ⟨id, _, h⟩ := bind_ok h
  obtain ⟨kind, hkind, h⟩ := bind_ok h
  have heq : kind = "soft-conflict" := by rw [hkind] at hk; cases hk; rfl
  subst heq
  simp only [hn, show ("soft-conflict" == "admission") = false from by decide, Bool.false_and,
    Bool.not_true, Bool.false_eq_true, ↓reduceIte] at h
  unfold runSoftKind at h
  simp only [show ("soft-conflict" == "soft-selected") = false from by decide,
    show ("soft-conflict" == "soft-rule") = false from by decide,
    show ("soft-conflict" == "soft-rules") = false from by decide,
    show ("soft-conflict" == "soft-elaborate") = false from by decide,
    show ("soft-conflict" == "soft-pairs") = false from by decide,
    show ("soft-conflict" == "soft-certificate") = false from by decide,
    show ("soft-conflict" == "soft-conflict") = true from by decide,
    Bool.true_and, Bool.false_eq_true, ↓reduceIte, pure_bind] at h
  cases hw : (j.getObjVal? "witness").toBool
  · simp only [hw, Bool.false_eq_true, ↓reduceIte] at h
    obtain ⟨res, hres, h⟩ := bind_ok h
    obtain ⟨openLabels, _, h⟩ := bind_ok h
    refine .inr ⟨rfl, res, hres, ?_⟩
    have hdetail : "verdict" ∉ ((match firstFailure res with
        | some d => if res.conflictFree then [] else [("detail", Json.str d)]
        | none => []) : List (String × Json)).map (·.1) := by
      split
      · split <;> simp
      · simp
    split at h
    · obtain ⟨_, _, h⟩ := bind_ok h
      split at h
      · cases h
        exact ok_verdict _ _ _ (by simpa using hdetail)
      · cases h
    · cases h
      exact ok_verdict _ _ _ (by simpa using hdetail)
  · simp only [hw, ↓reduceIte] at h
    obtain ⟨⟨src, w⟩, hr, h⟩ := bind_ok h
    obtain ⟨names, _, h⟩ := bind_ok h
    simp only [pure, Except.pure, Except.ok.injEq] at h
    refine .inl ⟨rfl, src, w, hr, ?_⟩
    rw [← h]
    refine ok_verdict _ _ _ ?_
    cases w.conflict <;> simp

/-- (1) The soft route's CONFLICT-FREE: a `soft-conflict` case without a `witness` field whose
answer's `verdict` reads `CONFLICT-FREE` was answered from a package replay that accepted every
target certificate (`conflictFree = true`). Hence the case's own decoder reads a well-formed soft
document that is conflict-free over every base model of `Background_base′`
(`Wire.soft_wire_conflict_sound`). -/
theorem soft_wire_conflict_free (j answer : Json) (h : runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "soft-conflict") (hn : usesSoftPath j = true)
    (hw : (j.getObjVal? "witness").toBool = false)
    (hverdict : answer.getObjValD "verdict" = .str "CONFLICT-FREE") :
    ∃ res : SoftConflictReplay, replaySoftConflict j = .ok res ∧ res.conflictFree = true ∧
      decodeSoftSource (j.getObjValD "environment") (j.getObjValD "norms") = .ok res.src ∧
      WellFormedSoft res.src.D = true ∧ SoftConflictFree.{0} res.src.D := by
  rcases soft_conflict_verdict j answer h hk hn with ⟨hw', _⟩ | ⟨_, res, hres, hv⟩
  · rw [hw] at hw'; cases hw'
  · have hc : res.conflictFree = true := by
      cases hcf : res.conflictFree
      · rw [hcf] at hv; rw [hv] at hverdict; simp at hverdict
      · rfl
    exact ⟨res, hres, hc, soft_wire_conflict_sound j res hres hc⟩

/-- (2) The soft route's CONFLICT: a `soft-conflict` case with a `witness` field whose answer's
`verdict` reads `CONFLICT` was answered from a witness replay whose target formula holds at the
typed tuple (`conflict = true`). Hence the case's own decoder reads a document that the witness
model shows is not conflict-free, with a strict collision or a pair conflict
(`Wire.soft_wire_conflict_witness_sound`). -/
theorem soft_wire_conflict_witness (j answer : Json) (h : runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "soft-conflict") (hn : usesSoftPath j = true)
    (hw : (j.getObjVal? "witness").toBool = true)
    (hverdict : answer.getObjValD "verdict" = .str "CONFLICT") :
    ∃ (src : SoftSource) (w : SoftWitnessData src), replaySoftWitness j = .ok ⟨src, w⟩ ∧ w.conflict = true ∧
      decodeSoftSource (j.getObjValD "environment") (j.getObjValD "norms") = .ok src ∧
      ¬ VE.Norms.ConflictFree (soften src.D) w.M.asStructure ∧ ¬ SoftConflictFree.{0} src.D ∧
      (¬ NoStrictCollision src.D w.M.asStructure ∨ ¬ NoHardPairConflict src.D w.M.asStructure) := by
  rcases soft_conflict_verdict j answer h hk hn with ⟨_, src, w, hr, hv⟩ | ⟨hw', _⟩
  · have hc : w.conflict = true := by
      cases hcf : w.conflict
      · rw [hcf] at hv; rw [hv] at hverdict; simp at hverdict
      · rfl
    exact ⟨src, w, hr, hc, soft_wire_conflict_witness_sound j src w hr hc⟩
  · rw [hw] at hw'; cases hw'

/-- (3) One soft document is never answered both ways: of two `soft-conflict` cases over the same
environment and norms, if one answer's `verdict` reads `CONFLICT-FREE`, the other's does not read
`CONFLICT`, whichever of the two carries a `witness` field. -/
theorem soft_wire_conflict_exclusive (j₁ j₂ a₁ a₂ : Json)
    (h₁ : runCase j₁ = .ok a₁) (hk₁ : VE.Route.Run.caseKind j₁ = .ok "soft-conflict")
    (hn₁ : usesSoftPath j₁ = true)
    (h₂ : runCase j₂ = .ok a₂) (hk₂ : VE.Route.Run.caseKind j₂ = .ok "soft-conflict")
    (hn₂ : usesSoftPath j₂ = true)
    (he : j₁.getObjValD "environment" = j₂.getObjValD "environment")
    (hn : j₁.getObjValD "norms" = j₂.getObjValD "norms")
    (hv₁ : a₁.getObjValD "verdict" = .str "CONFLICT-FREE") :
    a₂.getObjValD "verdict" ≠ .str "CONFLICT" := by
  intro hv₂
  have hfree : ∃ src : SoftSource,
      decodeSoftSource (j₁.getObjValD "environment") (j₁.getObjValD "norms") = .ok src ∧
      SoftConflictFree.{0} src.D := by
    rcases soft_conflict_verdict j₁ a₁ h₁ hk₁ hn₁ with ⟨hw, _, w, _, hv⟩ | ⟨hw, _⟩
    · rw [hv] at hv₁; cases hc : w.conflict <;> simp [hc] at hv₁
    · obtain ⟨res, _, _, hd, _, hs⟩ := soft_wire_conflict_free j₁ a₁ h₁ hk₁ hn₁ hw hv₁
      exact ⟨res.src, hd, hs⟩
  have hnot : ∃ src : SoftSource,
      decodeSoftSource (j₂.getObjValD "environment") (j₂.getObjValD "norms") = .ok src ∧
      ¬ SoftConflictFree.{0} src.D := by
    rcases soft_conflict_verdict j₂ a₂ h₂ hk₂ hn₂ with ⟨hw, _⟩ | ⟨hw, res, _, hv⟩
    · obtain ⟨src, _, _, _, hd, _, hs, _⟩ := soft_wire_conflict_witness j₂ a₂ h₂ hk₂ hn₂ hw hv₂
      exact ⟨src, hd, hs⟩
    · rw [hv] at hv₂; cases hc : res.conflictFree <;> simp [hc] at hv₂
  obtain ⟨s₁, hd₁, hs₁⟩ := hfree
  obtain ⟨s₂, hd₂, hs₂⟩ := hnot
  rw [he, hn, hd₂] at hd₁
  cases hd₁
  exact hs₂ hs₁

end VE.SoftNorms.Run
