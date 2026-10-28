import VE.Readings.SoftVerdicts
import VE.Defaults.Meaning

/-! Readings unless an exception applies (docs/spec/defeasible.md 3.9 and 7.4; plan 2.4, 3.5 and batch DF-3).

`dSem N` is RD-9's `xSem` with `Dflt_T` appended to each choice's `X`; a choice's conflict freedom is RD-9's strict one
together with the gate on the choice's soft document. RD-9's `foldG_*` theorems apply to it as stated: there is no
second fold. The replay (`replayVerdictsD`) is RD-9's `replayVerdictsSD` and, per chosen choice, the default evidence
decoded on the same `choiceLayeredG` source through `defaults-*`'s own view (`viewOn`), pair certificates
(`pairCertsOf`), collision (`collisionOf`) and certificate binding (`bindCertX`). The `default` member is present only
when the strict conflict fold is FREE (`DVerdicts.defaultMember`), so a default-fold CONFLICT comes from the gate
only (`readings_wire_default_conflict`). Enumerated route only (at most 64 choices). -/
namespace VE.Readings
open VE.Defaults
universe u

/-- A choice's soft document, as RD-9's `softXL` reads it. On the soft chain `choiceX N c` is its `softX` with
    `R = []`. -/
def choiceSoft (N : NDoc) (c : Choice) : VE.SoftNorms.SoftDoc := VE.Rights.correlate (choiceDoc N.D c).1

theorem choiceX_softX (N : NDoc) (c : Choice) :
    choiceX N c = VE.Defaults.softX (choiceU N c) (choiceSoft N c) [] := by
  simp [choiceX, softX, softXL, VE.Defaults.softX, choiceSoft, choiceU]

theorem choiceU_soften (N : NDoc) (c : Choice) : (choiceU N c).D = VE.SoftNorms.soften (choiceSoft N c) := rfl

/-- Per-choice results unless an exception applies: RD-9's `xSem` with `Dflt_T` appended; conflict freedom is the
    strict one together with the gate. -/
def dSem (N : NDoc) : ChoiceSem :=
  { xSem.{u} N (fun c => defaultX (choiceSoft N c) (choiceX N c)) with
    free := fun c => (VE.Readings.Wire.sdSem.{u} N).free c ∧ DefaultCoherent.{u} (choiceU N c) (choiceSoft N c) []
    notFree := fun c => (VE.Readings.Wire.sdSem.{0} N).notFree c ∨
      ¬ DefaultCoherent.{0} (choiceU N c) (choiceSoft N c) [] }

theorem dSem_entails (N : NDoc) (c : Choice) (Γ : List VE.Formula) (φ : VE.Formula) :
    (dSem.{u} N).entails c Γ φ ↔
      VE.NormDefaults.EntailsX.{u} (choiceU N c) (defaultX (choiceSoft N c) (choiceX N c))
        ((choiceDoc N.D c).2 ++ Γ) φ := Iff.rfl

/-- RD-9's fold theorems apply to `dSem` as stated (one instance shown). -/
example (N : NDoc) (A : Choice) (Γ : List VE.Formula) (φ : VE.Formula) (cs rs : List (Choice × ChoiceResult))
    (hr : RowsHoldG (dSem.{u} N) A Γ φ cs rs) (h : foldEntailment cs rs = .all) :
    ∀ c, (dSem.{u} N).compat c → (∀ x ∈ A, x ∈ c) → (dSem.{u} N).free c ∧ (dSem.{u} N).entails c Γ φ :=
  foldG_all_sound _ _ _ _ _ _ hr h

/-- With the strict conflict fold FREE, a default-fold CONFLICT comes from the gate only (DE7, never RD-9's
    contradiction wording). -/
theorem default_conflict_is_gate (N : NDoc) (A : Choice) (cs ds : List (Choice × ChoiceResult))
    (hcs : CoversG (VE.Readings.Wire.sdSem.{0} N) A cs)
    (hrs : ∀ x ∈ cs, HoldsG (VE.Readings.Wire.sdSem.{0} N) [] .bottom x.1 x.2)
    (hfree : foldConflict cs = .free)
    (hds : CoversG (dSem.{0} N) A ds) (hrd : ∀ x ∈ ds, HoldsG (dSem.{0} N) [] .bottom x.1 x.2)
    (hconf : foldConflict ds = .conflict) :
    ∃ c, Compatible N.D c ∧ (∀ x ∈ A, x ∈ c) ∧ ¬ DefaultCoherent.{0} (choiceU N c) (choiceSoft N c) [] := by
  obtain ⟨c, hc, hA, hn⟩ := foldG_conflict_sound _ _ _ hds hrd hconf
  have hf := foldG_conflict_free_sound _ _ _ hcs hrs hfree c hc hA
  refine ⟨c, hc, hA, ?_⟩
  rcases hn with hn | hn
  · exact absurd hf hn
  · exact hn

end VE.Readings
