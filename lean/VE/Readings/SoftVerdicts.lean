import VE.Readings.SoftWire
import VE.Readings.VerdictsWire

/-! `readings-verdicts` under the soft completion (docs/spec/rd-9-soft-chain.md 4.4 and 6.9; plan SC-5).

The replay is RD-3's (`replayND`) on the soft chain: the document admitted (`admitSD`), at most 64 compatible
choices, the ones taking `assumed`, `sdChoiceText` on each, and each choice's evidence decoded on its own
`choiceLayeredG` source (`xEvidenceOf`) as `XEvidence (choiceU N c) (choiceX N c)`. The rows are `XEvidence`'s, so
`x_rowsHold` gives the generic fold theorems at `sdSem` (`readings_wire_sd_verdicts_*`). The answer is
`ndVerdictsAnswer`'s, `decided_units` included (1.12). -/
namespace VE.Readings.Wire
open Lean
open VE.Readings
open VE.Norms (envAt size)
open VE.NormDefaults (fill)
universe u

/-- The per-choice semantics of the soft completion: each choice's filled document with its `Soft_T`. -/
def sdSem (N : NDoc) : ChoiceSem := xSem.{u} N (choiceX N)

theorem sdSem_normsShaped (N : NDoc) (hn : normsShaped N.D = true) (Γ : List VE.Formula) (φ : VE.Formula)
    (c : Choice) (r : ChoiceResult) : HoldsG (sdSem.{u} N) Γ φ c r ↔ HoldsG (ndSem.{u} N) Γ φ c r := by
  have hX : choiceX N = fun _ => [] := funext (choiceX_normsShaped N hn)
  rw [sdSem, hX]
  exact xSem_nil N Γ φ c r

structure SDVerdicts where
  r : AdmittedSD
  x : XVerdicts
  hN : x.N = r.N
  hX : x.Xf = choiceX r.N

/-- The evidence of each choice of `l`, in order, or the first refusal. -/
def mapSigma {β : Choice → Type} : (l : List Choice) → ((c : Choice) → c ∈ l → Except String (β c)) →
    Except String {ps : List ((c : Choice) × β c) // ps.map (·.1) = l}
  | [], _ => pure ⟨[], rfl⟩
  | c :: l, f => do
    let b ← f c List.mem_cons_self
    let rest ← mapSigma l (fun c' h => f c' (List.mem_cons_of_mem _ h))
    pure ⟨⟨c, b⟩ :: rest.1, by simp [rest.2]⟩

/-- One choice's evidence on the soft chain (4.4): `sdChoiceText` none (else its text), then the evidence decoded on
    the choice's `choiceLayeredG` source, its `X` well formed by the source's third conjunct. -/
def sdEvidenceOf (r : AdmittedSD) (c : Choice) (e premisesJ conclusionJ : Json) (Γ : List VE.Formula)
    (φ : VE.Formula) : Except String (XEvidence (choiceU r.N c) (choiceX r.N c) × List PieceNote) :=
  match ht : sdChoiceText r.b.a.re r.N c with
  | some err => .error err
  | none =>
    have hw : VE.NormDefaults.WellFormedU (choiceU r.N c) = true :=
      wellFormedU_of_ndDocTextG (Option.map_eq_none_iff.mp (option_or_none ht).2)
    match choiceLayeredG r.b r.N c hw r.hN with
    | .error err => .error err
    | .ok L =>
      let (ev, notes) := xEvidenceOf r.b.a.re.lowerJson L.1 L.2.2.2 (choiceDoc r.N.D c).2 e premisesJ conclusionJ Γ φ
      .ok (castXE L.2.1 L.2.2.1 ev, notes)

/-- 4.4 on an admitted document: `supReady`, at most 64 compatible choices, the ones taking `A` (some, else
    `ReadingsUnsatisfiable`), and each one's evidence (`sdEvidenceOf`). -/
def replaySD (r : AdmittedSD) (question : String) (A : Choice) (j : Json) : Except String SDVerdicts := do
  if hr : supReady r.N.D = true then
    if hle : (choices r.N.D).length ≤ maxChoices then
      let chosen := chosenOf r.N.D A
      if chosen.isEmpty then throw (untakenText r.N.D A)
      let (Γ, φ) ← VE.Readings.Run.queryFormulas (fullEnv r.N (chosen.headD [])) question j
      let evidence := VE.Readings.Run.evidenceList j
      let premisesJ := match j.getObjValD "premises" with | .null => Json.arr #[] | p => p
      let ps ← mapSigma (β := fun c => XEvidence (choiceU r.N c) (choiceX r.N c) × List PieceNote) chosen
        (fun c _ => sdEvidenceOf r c (VE.Readings.Run.entryFor evidence c) premisesJ (j.getObjValD "conclusion") Γ φ)
      pure ⟨r, ⟨r.N, choiceX r.N, A, Γ, φ, hr, hle, ps.1.map (fun p => ⟨p.1, p.2.1⟩), by
          simp only [List.map_map, Function.comp_def]
          exact ps.2, ps.1.map (·.2.2)⟩, rfl, rfl⟩
    else throw "readings-verdicts: more than 64 compatible readings"
  else throw "InvalidInput: readings document is not well-formed"

/-- 4.4. -/
def replayVerdictsSD (j : Lean.Json) : Except String SDVerdicts := do
  let r ← admitSD (← j.getObjVal? "environment") (← j.getObjVal? "document")
  replaySD r (← VE.Bridge.stringField j "question") (← decodeChoice (j.getObjValD "assumed")) j

theorem sd_rowsHold (y : SDVerdicts) :
    RowsHoldG (sdSem.{u} y.r.N) y.x.A y.x.Γ y.x.φ y.x.conflictRows y.x.queryRows := by
  obtain ⟨r, ⟨N, Xf, A, Γ, φ, ready, hle, evs, hevs, notes⟩, hN, hX⟩ := y
  dsimp only at hN hX ⊢
  subst hN hX
  exact x_rowsHold.{u} ⟨r.N, choiceX r.N, A, Γ, φ, ready, hle, evs, hevs, notes⟩

theorem sd_premiseRowsHold (y : SDVerdicts) :
    CoversG (sdSem.{u} y.r.N) y.x.A y.x.premiseRows ∧
      ∀ z ∈ y.x.premiseRows, HoldsG (sdSem.{u} y.r.N) [] .bottom z.1 z.2 := by
  obtain ⟨r, ⟨N, Xf, A, Γ, φ, ready, hle, evs, hevs, notes⟩, hN, hX⟩ := y
  dsimp only at hN hX ⊢
  subst hN hX
  exact x_premiseRowsHold.{u} ⟨r.N, choiceX r.N, A, Γ, φ, ready, hle, evs, hevs, notes⟩

/-! ### The wire theorems: every verdict a replayed case folds to is its generic fold theorem's conclusion -/

theorem readings_wire_sd_verdicts_all (j : Lean.Json) (y : SDVerdicts) (h : replayVerdictsSD j = .ok y)
    (hv : foldEntailment y.x.conflictRows y.x.queryRows = .all) :
    ∀ c, Compatible y.r.N.D c → (∀ z ∈ y.x.A, z ∈ c) →
      VE.NormDefaults.Wire.ConflictFreeX.{u} (choiceU y.r.N c) (choiceX y.r.N c) ∧
      VE.NormDefaults.EntailsX.{u} (choiceU y.r.N c) (choiceX y.r.N c) ((choiceDoc y.r.N.D c).2 ++ y.x.Γ) y.x.φ := by
  have _ := h
  exact foldG_all_sound _ _ _ _ _ _ (sd_rowsHold y) hv

theorem readings_wire_sd_verdicts_none (j : Lean.Json) (y : SDVerdicts) (h : replayVerdictsSD j = .ok y)
    (hv : foldEntailment y.x.conflictRows y.x.queryRows = .none) :
    ∀ c, Compatible y.r.N.D c → (∀ z ∈ y.x.A, z ∈ c) →
      VE.NormDefaults.Wire.ConflictFreeX.{u} (choiceU y.r.N c) (choiceX y.r.N c) ∧
      CounterX (choiceU y.r.N c) (choiceX y.r.N c) ((choiceDoc y.r.N.D c).2 ++ y.x.Γ) y.x.φ := by
  have _ := h
  exact foldG_none_sound _ _ _ _ _ _ (sd_rowsHold.{u} y) hv

theorem readings_wire_sd_verdicts_some (j : Lean.Json) (y : SDVerdicts) (h : replayVerdictsSD j = .ok y)
    (hv : foldEntailment y.x.conflictRows y.x.queryRows = .some) :
    (∀ c, Compatible y.r.N.D c → (∀ z ∈ y.x.A, z ∈ c) →
      VE.NormDefaults.Wire.ConflictFreeX.{u} (choiceU y.r.N c) (choiceX y.r.N c)) ∧
    (∃ c, Compatible y.r.N.D c ∧ (∀ z ∈ y.x.A, z ∈ c) ∧
      VE.NormDefaults.EntailsX.{u} (choiceU y.r.N c) (choiceX y.r.N c) ((choiceDoc y.r.N.D c).2 ++ y.x.Γ) y.x.φ) ∧
    (∃ c, Compatible y.r.N.D c ∧ (∀ z ∈ y.x.A, z ∈ c) ∧
      CounterX (choiceU y.r.N c) (choiceX y.r.N c) ((choiceDoc y.r.N.D c).2 ++ y.x.Γ) y.x.φ) := by
  have _ := h
  exact foldG_some_sound _ _ _ _ _ _ (sd_rowsHold y) hv

theorem readings_wire_sd_verdicts_conflict_free (j : Lean.Json) (y : SDVerdicts) (h : replayVerdictsSD j = .ok y)
    (hv : foldConflict y.x.conflictRows = .free) :
    ∀ c, Compatible y.r.N.D c → (∀ z ∈ y.x.A, z ∈ c) →
      VE.NormDefaults.Wire.ConflictFreeX.{u} (choiceU y.r.N c) (choiceX y.r.N c) := by
  have _ := h
  obtain ⟨hc, _, hr, _⟩ := sd_rowsHold.{u} y
  exact foldG_conflict_free_sound _ _ _ hc hr hv

theorem readings_wire_sd_verdicts_conflict (j : Lean.Json) (y : SDVerdicts) (h : replayVerdictsSD j = .ok y)
    (hv : foldConflict y.x.conflictRows = .conflict) :
    ∃ c, Compatible y.r.N.D c ∧ (∀ z ∈ y.x.A, z ∈ c) ∧
      ¬ VE.NormDefaults.Wire.ConflictFreeX.{0} (choiceU y.r.N c) (choiceX y.r.N c) := by
  have _ := h
  obtain ⟨hc, _, hr, _⟩ := sd_rowsHold.{0} y
  exact foldG_conflict_sound _ _ _ hc hr hv

theorem readings_wire_sd_verdicts_model (j : Lean.Json) (y : SDVerdicts) (h : replayVerdictsSD j = .ok y)
    (hv : foldPremises y.x.premiseRows = .model) :
    ∃ c, Compatible y.r.N.D c ∧ (∀ z ∈ y.x.A, z ∈ c) ∧
      ConsistentX (choiceU y.r.N c) (choiceX y.r.N c) (choiceDoc y.r.N.D c).2 := by
  have _ := h
  obtain ⟨hc, hr⟩ := sd_premiseRowsHold.{0} y
  exact foldG_premises_model_sound _ _ _ hc hr hv

theorem readings_wire_sd_verdicts_inconsistent (j : Lean.Json) (y : SDVerdicts) (h : replayVerdictsSD j = .ok y)
    (hv : foldPremises y.x.premiseRows = .inconsistent) :
    ∀ c, Compatible y.r.N.D c → (∀ z ∈ y.x.A, z ∈ c) →
      VE.NormDefaults.Wire.ConflictFreeX.{u} (choiceU y.r.N c) (choiceX y.r.N c) ∧
      VE.NormDefaults.EntailsX.{u} (choiceU y.r.N c) (choiceX y.r.N c) (choiceDoc y.r.N.D c).2 .bottom := by
  have _ := h
  obtain ⟨hc, hr⟩ := sd_premiseRowsHold.{u} y
  simpa only [sdSem, xSem, List.append_nil] using foldG_premises_inconsistent_sound _ _ _ hc hr hv

end VE.Readings.Wire

namespace VE.Readings.Run
open Lean
open VE.Readings
open VE.Readings.Wire
open VE.Norms (envAt size)
open VE.NormDefaults (fill)

/-- `readings-verdicts` under the soft completion (4.4): RD-3's request (`verdictsRequest`), the document admitted
    (`admitSDOf`), the replay (`replaySD`), and RD-3's answer with `decided_units` (`ndVerdictsAnswer`, 1.12). Beyond
    64 compatible choices only the evidence's own choices are checked, each on its `replayChoiceAtS` source. `b` is
    the case's one admission. -/
def runVerdictsSD (id : String) (b : Admitted2) (j : Json) : Except String Json := do
  let q ← verdictsRequest b j
  let r ← admitSDOf b
  let D := r.N.D
  if (choices D).isEmpty then throw (unsatText D)
  if (choices D).length ≤ maxChoices then
    let y ← replaySD r q.question q.A j
    return ndVerdictsAnswer id q.question (j.getObjValD "document") D q.A q.named (some (xInfos y.x)) [] q.dead
  -- Beyond 64: only a checked countermodel says anything (not ALL).
  let over := overInfos D q.A q.evidence (fun c e =>
    match replayChoiceAtS r c with
    | .ok x =>
      match queryFormulas (envAt (fill x.L.U) (size (fill x.L.U))) q.question j with
      | .ok (Γ, φ) =>
        let (ev, notes) := xEvidenceOf r.b.a.re.lowerJson x.L x.hXw (choiceDoc D c).2 e q.premisesJ q.conclusionJ Γ φ
        some (rowInfoOf c ev (choiceDoc D c).2 Γ φ notes)
      | .error _ => none
    | .error _ => none)
  return ndVerdictsAnswer id q.question (j.getObjValD "document") D q.A q.named none over q.dead

end VE.Readings.Run
