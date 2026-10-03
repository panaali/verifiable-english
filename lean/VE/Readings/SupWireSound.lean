import VE.Readings.SupAll
import VE.Readings.SupWire

/-! The wire theorems of S2a (docs/spec/composition-s2.md 8.5). A replayed `readings-certificate` case whose
conflict certificates check (`slot_conflict_free`) and whose certificate checks on `sup D` proves its conclusion in
every situation of every compatible reading that takes the assumed candidates (`superpose_all`); a replayed
`readings-model` case whose model checks and falsifies the conclusion is a countermodel in the reading its atoms
encode (`superpose_countermodel`). -/
namespace VE.Readings.Wire
open VE.Readings
open VE.Norms (envAt size Sat)
open VE.SoftNorms (soften circ)
open VE.Rights (correlate)
open VE.Compose (slotConflictFreeCheck)
universe u

theorem readings_wire_all_sound (j : Lean.Json) (r : CertificateReplay) (_h : replayCertificate j = .ok r)
    (hc : slotConflictFreeCheck (correlate (sup r.D).1) (slotUnder r.D r.assumed) r.conflictCerts = true)
    (ha : supCertificateCheck r.D r.assumed r.Γ r.φ r.cert = true) :
    ∀ c, Compatible r.D c → (∀ x ∈ r.assumed, x ∈ c) → ∀ B : VE.Structure.{u},
      VE.Rights.BaseAdmissibleR (choiceDoc r.D c).1 B →
      Sat (expand (choiceDoc r.D c).1 B) ((choiceDoc r.D c).2 ++ r.Γ) →
      r.φ.denote (expand (choiceDoc r.D c).1 B) [] := by
  intro c hcc hAc B hB hp
  have hcf := VE.Compose.slot_conflict_free.{u} _ (sup_wellFormed r.D r.sp).2 _ _ hc
  exact superpose_all r.D r.wf r.soft r.sp r.assumed r.hA hcf r.Γ r.φ r.hΓ r.hφ r.cert ha c hcc hAc B hB hp

theorem readings_wire_model_sound (j : Lean.Json) (r : ModelReplay) (_h : replayModel j = .ok r)
    (hm : supModelCheck r.D r.assumed r.Γ r.M = true)
    (hn : (circ (correlate (sup r.D).1) r.φ).eval r.M [] = false) :
    ∃ c, Compatible r.D c ∧ (∀ x ∈ r.assumed, x ∈ c) ∧ Encodes r.D c r.M.asStructure ∧
      VE.Rights.BaseAdmissibleR (choiceDoc r.D c).1 (pull r.D c r.M.asStructure) ∧
      Sat (expand (choiceDoc r.D c).1 (pull r.D c r.M.asStructure)) ((choiceDoc r.D c).2 ++ r.Γ) ∧
      ¬ r.φ.denote (expand (choiceDoc r.D c).1 (pull r.D c r.M.asStructure)) [] :=
  superpose_countermodel r.D r.wf r.soft r.sp r.assumed r.Γ r.φ r.hΓ r.hφ r.M r.valid hm hn

end VE.Readings.Wire
