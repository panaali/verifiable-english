import VE.Route.Admission
import VE.Norms.Admission
import VE.Readings.Wire

/-! Nonfactivity (purpose-explanation spec 3, plan D8a): the W2 kinds whose content no route reads as a premise or
a rule. A new file in route admission's namespace; `Route/Admission.lean` is not edited. -/

namespace VE.Route.Admission
open Lean

/-- A kind whose content is never a premise and never a rule. -/
def Kind.inert : Kind → Bool
  | .explanation | .exposition | .«example» | .analogy | .«meta» => true
  | _ => false

theorem Kind.inert_active (k : Kind) (h : k.inert = true) :
    k ≠ .asserted ∧ k ≠ .norm ∧ k ≠ .definition ∧ k.quoted = false := by
  cases k <;> simp_all [Kind.inert, Kind.quoted]

/-- Admission's leaf provenance: no admitted node names an inert unit, neither as the unit it formalises nor as the
    unit of a bridge leaf. -/
theorem inert_unnamed (D : Doc) (w : WireNode) (i : String)
    (hi : ∀ x ∈ D.units, x.id = i → x.kind.inert = true) (hw : NodeAdmitted D w) :
    w.unit ≠ some i ∧ ∀ a, parseLabel w.claim.label ≠ some (.bridge a i) := by
  have hA : ∀ φ, ¬ AssertedUnit D i φ := by
    rintro φ ⟨x, hx, he, hk, -⟩
    exact (Kind.inert_active _ (hi x hx he)).1 hk
  have hQ : ∀ a φ, ¬ QuotedUnit D a i φ := by
    rintro a φ ⟨x, hx, he, hq, -⟩
    simp [(Kind.inert_active _ (hi x hx he)).2.2.2] at hq
  unfold NodeAdmitted at hw
  split at hw
  · obtain ⟨hl, hw⟩ := hw
    refine ⟨fun h => hA _ (hw i h), fun a h => ?_⟩
    rw [hl] at h
    cases h
  · unfold LeafAdmitted at hw
    cases hp : parseLabel w.claim.label with
    | none => simp [hp] at hw
    | some l =>
      rw [hp] at hw
      simp only [ne_eq, Option.some.injEq]
      cases l with
      | asserted =>
        obtain ⟨u, hu, hau⟩ := hw
        refine ⟨fun he => ?_, fun a h => by cases h⟩
        rw [he] at hu
        cases hu
        exact hA _ hau
      | bridge a u =>
        obtain ⟨hwu, hq⟩ := hw
        have hne : u ≠ i := fun e => hQ a _ (e ▸ hq)
        refine ⟨?_, fun a' h => hne (Label.bridge.inj h).2⟩
        rcases hwu with h | h <;> simp [h, hne]
      | background g => exact ⟨by simp [hw.1], fun a h => by cases h⟩
      | cite b l => exact ⟨by simp [hw.1], fun a h => by cases h⟩
      | openTerm t => exact ⟨by simp [hw.1], fun a h => by cases h⟩
      | readings s v c => exact ⟨by simp [hw.1], fun a h => by cases h⟩
      | narrowing n => exact ⟨by simp [hw.1], fun a h => by cases h⟩

/-- The same for every node of an admitted document, so no assumption of its report comes from an inert unit. -/
theorem admit_inert (profiles : List String) (environment : Json) (rv : Wire.RouteVocabulary) (j : Json)
    (res : Admitted) (h : admitDocument profiles environment rv j = .ok res) (i : String)
    (hi : ∀ x ∈ res.doc.units, x.id = i → x.kind.inert = true) :
    ∀ w ∈ res.wires, w.unit ≠ some i ∧ ∀ a, parseLabel w.claim.label ≠ some (.bridge a i) :=
  fun w hw => inert_unnamed res.doc w i hi
    ((admit_report_sound.{0} profiles environment rv j res h).2.2.2.2.2.2.2.2.1 w hw)

/-- The norm-role table gives an inert kind no role: its norm content is never a rule. -/
theorem normRole_inert (k : Kind) (c : Json) (h : k.inert = true) :
    ∃ m, VE.Norms.Admission.normRole k c = .error m := by
  cases k <;> simp [Kind.inert] at h <;> exact ⟨_, rfl⟩

/-- The readings route never puts an inert unit's or candidate's content in force. -/
theorem inForce_inert (k : Kind) (s : String) (hs : renderKind k = .str s) (h : k.inert = true)
    (c : VE.Compose.Content) : VE.Readings.Wire.inForce (some s) c = false := by
  cases k <;> simp [Kind.inert] at h <;> simp [renderKind] at hs <;> subst hs <;> cases c <;>
    simp [VE.Readings.Wire.inForce, VE.Readings.Wire.rightsKinds]
end VE.Route.Admission
