-- ve-layer: 4 (the equality theorems of the layer-4 norms runner, which they import)
import VE.Acts.HookToday
import VE.Norms.Run

/-! The runners' equality theorems of the acts hook (kb-4a; docs/spec/kernel-boundary.md decisions 2 and 5, row KB-4).

`Today` keeps the norms mode's runners as they were before the hook (main `4a5d3460d3`, lean/VE/Norms/Run.lean),
over today's decoder `HookToday.Today.decodeFlagged`, frozen for these statements only. Their acts callees
(`Acts.Decode.flaggedSource`, `Acts.Run.normsSource`) are today's: each now passes `ActsHook.acts` to `decodeSource`,
which is today's decoder by `rfl` (`HookToday.decodeSource_acts`).

* `runCaseActsRouted_today`, `runCaseActs_today`: the acts-instantiated runners are today's runners, on every input
  (`rfl`).
* `runCase_plain`, `runAdmission_plain`: the plain runners are today's wherever the decoder meets no environment from
  which `acts@0` is read (the case's environment, and the one a `norms-elaborate` case decides over).
* `runAdmission_today`: the plain admission runner answers every input as before (admission refuses `acts@0` before
  it decodes, `envelopeGate_actsProfiles`).
* `runCaseRouted_today`: the norms mode's dispatch answers every input as before. -/
namespace VE.Acts.HookTwins
open Lean VE.Norms VE.Norms.Wire

namespace Today

/-- Today's `Norms.Run.decoderOf`, frozen. -/
def decoderOf (environment : Json) : SourceDecoder :=
  if VE.Norms.Run.underActs environment then VE.Acts.Decode.flaggedSource else HookToday.Today.decodeFlagged

/-- Today's `Norms.Run.runCaseRouted`, frozen. -/
def runCaseRouted (j : Json) : Except String Json :=
  if VE.Acts.Run.isElaborate j then VE.Acts.Run.runElaborate VE.Acts.Run.normsSource j
  else VE.Norms.Run.runCaseIn (decoderOf (j.getObjValD "environment")) j

/-- Today's `Norms.Run.runCase` and `Norms.Run.runAdmission`, frozen. -/
def runCase : Json → Except String Json := VE.Norms.Run.runCaseIn HookToday.Today.decodeFlagged
def runAdmission : String → Json → Json → Except String Json := VE.Norms.Run.runAdmissionIn HookToday.Today.decodeFlagged

end Today

/-! ## With `ActsHook.acts`: today's runners, on every input -/

theorem runCaseActsRouted_today (j : Json) : VE.Norms.Run.runCaseActsRouted j = Today.runCaseRouted j := rfl
theorem runCaseActs_today (j : Json) : VE.Norms.Run.runCaseActs j = Today.runCase j := rfl

/-! ## Two decoders that agree where a runner reads give the same answer -/

theorem bind_congr_ok {ε α β : Type} {x : Except ε α} {f g : α → Except ε β}
    (h : ∀ a, x = .ok a → f a = g a) : x >>= f = x >>= g := by
  cases x with
  | error e => rfl
  | ok a => exact h a rfl

theorem getObjValD_of_ok {j v : Json} {k : String} (h : j.getObjVal? k = .ok v) : j.getObjValD k = v := by
  simp only [Json.getObjValD, h]
  rfl

theorem ok_bind {ε α β : Type} (a : α) (f : α → Except ε β) : (Except.ok a : Except ε α) >>= f = f a := rfl
theorem error_bind {ε α β : Type} (e : ε) (f : α → Except ε β) : (Except.error e : Except ε α) >>= f = .error e := rfl

theorem admitDocumentIn_congr {d₁ d₂ : SourceDecoder} {environment : Json}
    (h : ∀ n, d₁ environment n = d₂ environment n) (document : Json) :
    Admission.admitDocumentIn d₁ environment document = Admission.admitDocumentIn d₂ environment document := by
  unfold Admission.admitDocumentIn
  simp only [h]

theorem runAdmissionIn_congr {d₁ d₂ : SourceDecoder} {environment : Json}
    (h : ∀ n, d₁ environment n = d₂ environment n) (id : String) (document : Json) :
    VE.Norms.Run.runAdmissionIn d₁ id environment document = VE.Norms.Run.runAdmissionIn d₂ id environment document := by
  unfold VE.Norms.Run.runAdmissionIn
  rw [admitDocumentIn_congr h]

theorem replayEntailmentIn_congr {d₁ d₂ : SourceDecoder} {j : Json}
    (h : ∀ n, d₁ (j.getObjValD "environment") n = d₂ (j.getObjValD "environment") n) :
    Flagged.replayEntailmentIn d₁ j = Flagged.replayEntailmentIn d₂ j := by
  unfold Flagged.replayEntailmentIn
  refine bind_congr_ok fun e he => ?_
  rw [getObjValD_of_ok he] at h
  simp only [h]

theorem replayConflictIn_congr {d₁ d₂ : SourceDecoder} {j : Json}
    (h : ∀ n, d₁ (j.getObjValD "environment") n = d₂ (j.getObjValD "environment") n) :
    Flagged.replayConflictIn d₁ j = Flagged.replayConflictIn d₂ j := by
  unfold Flagged.replayConflictIn
  refine bind_congr_ok fun e he => ?_
  rw [getObjValD_of_ok he] at h
  simp only [h]

theorem replayWitnessIn_congr {d₁ d₂ : SourceDecoder} {j : Json}
    (h : ∀ n, d₁ (j.getObjValD "environment") n = d₂ (j.getObjValD "environment") n) :
    Flagged.replayWitnessIn d₁ j = Flagged.replayWitnessIn d₂ j := by
  unfold Flagged.replayWitnessIn
  refine bind_congr_ok fun e he => ?_
  rw [getObjValD_of_ok he] at h
  simp only [h]

/-- `runCaseIn` reads its decoder only at the case's environment and, for `norms-elaborate`, at the environment that
case decides over. -/
theorem runCaseIn_congr {d₁ d₂ : SourceDecoder} {j : Json}
    (hE : ∀ n, d₁ (j.getObjValD "environment") n = d₂ (j.getObjValD "environment") n)
    (hD : ∀ e, VE.Compose.decidingEnvironment (j.getObjValD "environment") = .ok e → ∀ n, d₁ e n = d₂ e n) :
    VE.Norms.Run.runCaseIn d₁ j = VE.Norms.Run.runCaseIn d₂ j := by
  unfold VE.Norms.Run.runCaseIn
  rw [replayEntailmentIn_congr hE, replayConflictIn_congr hE, replayWitnessIn_congr hE]
  cases he : j.getObjVal? "environment" with
  | error m => simp only [error_bind]
  | ok E =>
    rw [getObjValD_of_ok he] at hE hD
    cases hd : VE.Compose.decidingEnvironment E with
    | error m => simp only [ok_bind, error_bind, hd, runAdmissionIn_congr hE]
    | ok e => simp only [ok_bind, hd, hD e hd, runAdmissionIn_congr hE]

/-! ## With `ActsHook.plain`: today's runners wherever no `acts@0` environment is decoded -/

theorem actsProfiles_nil_of_underActs {environment : Json} (h : VE.Norms.Run.underActs environment = false) :
    actsProfiles true environment = [] := by
  simpa [VE.Norms.Run.underActs] using h

theorem runCase_plain (j : Json) (hE : actsProfiles true (j.getObjValD "environment") = [])
    (hD : ∀ e, VE.Compose.decidingEnvironment (j.getObjValD "environment") = .ok e → actsProfiles true e = []) :
    VE.Norms.Run.runCase j = Today.runCase j :=
  runCaseIn_congr (fun n => HookToday.decodeFlagged_plain _ n hE)
    (fun e he n => HookToday.decodeFlagged_plain e n (hD e he))

theorem runAdmission_plain (id : String) (environment document : Json) (h : actsProfiles true environment = []) :
    VE.Norms.Run.runAdmission id environment document = Today.runAdmission id environment document :=
  runAdmissionIn_congr (fun n => HookToday.decodeFlagged_plain environment n h) id document

/-- Admission refuses, before it decodes, every environment from which `acts@0` is read: the envelope admits known
profiles only (`Route.Gate.decodeEnvelope_sound`), and `acts@0` is not one. -/
theorem envelopeGate_actsProfiles {environment : Json} (h : Admission.envelopeGate environment = .ok ()) :
    actsProfiles true environment = [] := by
  unfold Admission.envelopeGate at h
  obtain ⟨e, he, -⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨-, hp, ha⟩ := VE.Route.Gate.decodeEnvelope_sound _ _ he
  refine HookToday.actsProfiles_eq_nil true environment fun ps hps hmem => ?_
  rw [hp] at hps
  cases hps
  exact absurd (ha.2.1 _ hmem) (by decide)

/-- The plain admission runner answers every input as before: no caller relied on today's acceptance of `acts@0`. -/
theorem runAdmission_today (id : String) (environment document : Json) :
    VE.Norms.Run.runAdmission id environment document = Today.runAdmission id environment document := by
  cases hg : Admission.envelopeGate environment with
  | error m =>
    unfold VE.Norms.Run.runAdmission Today.runAdmission VE.Norms.Run.runAdmissionIn Admission.admitDocumentIn
    simp only [hg]
    rfl
  | ok u => exact runAdmission_plain id environment document (envelopeGate_actsProfiles hg)

/-- The norms mode's dispatch answers every input as before the acts hook: a case that reads `acts@0` (or an
`acts-elaborate` case) goes to today's runner itself, and every other case to the plain runner, which then decodes
no environment from which `acts@0` is read. -/
theorem runCaseRouted_today (j : Json) : VE.Norms.Run.runCaseRouted j = Today.runCaseRouted j := by
  unfold VE.Norms.Run.runCaseRouted
  split
  · rw [runCaseActsRouted_today]
  · rename_i hc
    simp only [Bool.or_eq_true, not_or, Bool.not_eq_true] at hc
    obtain ⟨⟨hEl, hU⟩, hDec⟩ := hc
    unfold Today.runCaseRouted Today.decoderOf
    rw [if_neg (by simp [hEl]), if_neg (by simp [hU])]
    refine runCase_plain j (actsProfiles_nil_of_underActs hU) fun e he => ?_
    apply actsProfiles_nil_of_underActs
    simpa [VE.Norms.Run.decidesActs, he] using hDec

end VE.Acts.HookTwins
