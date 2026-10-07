import VE.Norms.Run

/-! The norms route's `norms-certificate` answer at the public entry
`Norms.Run.runCase` (docs/CONSOLIDATION-PLAN.md step 2a, the norms corollary
named by step 1b): an answer whose `valid` field is `true` means the case's
replay decoded and the checker accepted, so `Flagged.norms_flagged_acceptance`
holds of it, for the source decoded from the case's own environment and
norms. -/
namespace VE.Norms.RunSound
open Lean
open VE.Norms.Flagged
open VE.Order.ProfileGate (bind_ok)
universe u

theorem valid_field (id : String) (b : Bool) (n m : Json) :
    (VE.Route.Wire.ok id [("valid", .bool b), ("background", n), ("layers", m)]).getObjValD "valid" =
      .bool b := rfl

theorem valid_field_steps (id : String) (b : Bool) (n m s : Json) :
    (VE.Route.Wire.ok id [("valid", .bool b), ("background", n), ("layers", m), ("steps", s)]).getObjValD "valid" =
      .bool b :=
  rfl

/-- The `norms-certificate` branch of `Norms.Run.runCase`: the answer's `valid`
field is the checker's verdict on the replayed case. -/
theorem runCase_certificate (j answer : Json) (h : Run.runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "norms-certificate") :
    ∃ r, replayEntailment j = .ok r ∧ answer.getObjValD "valid" = .bool (valid r) := by
  unfold Run.runCase at h
  obtain ⟨id, _, h⟩ := bind_ok h
  obtain ⟨kind, hkind, h⟩ := bind_ok h
  have heq : kind = "norms-certificate" := by rw [hkind] at hk; cases hk; rfl
  subst kind
  simp only [show ("norms-certificate" == "admission") = false from rfl,
    show ("norms-certificate" == "norms-elaborate") = false from rfl,
    beq_self_eq_true, Bool.false_and, Bool.false_eq_true, ↓reduceIte, pure_bind] at h
  obtain ⟨r, hr, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  split at h
  · cases h
  cases h
  exact ⟨r, hr, valid_field_steps _ _ _ _ _⟩

/-- At the public entry, a `norms-certificate` answer whose `valid` field is
`true` means, for the document decoded from the case's environment and norms,
(1) the conclusion holds in every admissible structure satisfying the flag
premises, the direct semantics, the definitions, the profile,
`Background_base` and the premises; and (2) with no flag declared and the
document conflict-free, the conclusion holds in every base-admissible structure
satisfying the premises (`Flagged.norms_flagged_acceptance`). -/
theorem norms_wire_certificate_acceptance (j answer : Json) (h : Run.runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "norms-certificate")
    (hv : answer.getObjValD "valid" = .bool true) :
    ∃ r : Replay.EntailmentReplay, replayEntailment j = .ok r ∧
    Wire.decodeSource (j.getObjValD "environment") (j.getObjValD "norms") (flags := true) = .ok r.src ∧
    (∀ S : VE.Structure.{u}, S.Admissible (envAt r.src.D (size r.src.D)) →
      Sat S (flagPremises r.src) → holdsCatala r.src.D.T S →
      definitionsHold r.src.D S → profileHold r.src.D S → Sat S (backgroundBase r.src.D) →
      Sat S r.premises → r.conclusion.denote S []) ∧
    (flagPremises r.src = [] →
      (∀ B : VE.Structure.{u}, BaseAdmissible r.src.D B → ConflictFree r.src.D B) →
      (∀ a ∈ r.premises, a.WellFormed (envAt r.src.D 0) []) → r.conclusion.WellFormed (envAt r.src.D 0) [] →
      ∀ B : VE.Structure.{u}, BaseAdmissible r.src.D B → Sat B r.premises → r.conclusion.denote B []) := by
  obtain ⟨r, hr, hval⟩ := runCase_certificate j answer h hk
  rw [hval] at hv
  have hvr : valid r = true := by cases hb : valid r <;> simp_all
  exact ⟨r, hr, norms_flagged_acceptance j r hr hvr⟩

end VE.Norms.RunSound
