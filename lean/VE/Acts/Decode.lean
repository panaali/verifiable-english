import VE.Acts.Elaborate
import VE.Acts.Wire

/-! The decoder after AP-3 (docs/spec/act-phrases.md 6.4): the decoded source, unchanged, and beside it the elaborated
document and its map.

Elaboration runs after `decodeSourceU` has decoded the document and recovered its `unspecified` completions (SR6),
so the source and its binding proofs are untouched. Each act of the decoded document is read once by `checkAct`
(deterministic, so its tree is the decoder's answer): a lexical act gives no tree, a joined act its one meaning.

No route calls `decodeElaboratedU` yet, and the norms decoder's hook still admits lexical acts only, so every decoded
document has `D.acts = []` and elaborates to itself (`decodeElaboratedU_lexical`). The hook, the `acts` block's
frames and the entry points switch together (ap-3db).
-/

namespace VE.Acts.Decode
open Lean VE.Acts VE.NormDefaults

/-- The decoded source, unchanged, and beside it the elaborated document and its map. -/
structure ElaboratedU where
  s : VE.NormDefaults.Wire.SourceU
  D : ActsDoc
  hU : D.U = s.U
  U' : VE.NormDefaults.UDoc
  M : SplitMap
  hE : elaborateMap D = .ok (U', M)

/-- Each joined act of `U` and its one meaning (`checkAct` under the fixed phrases `fx` and the frames `V`). -/
def actsOf (fx : List String) (V : Vocab) (U : UDoc) : Except String (List (String × Act)) :=
  U.D.T.regulated.filterMapM fun r => match r.act with
    | some a => do
      let (_, A) ← VE.Acts.Wire.checkAct fx V r.name r.sorts.length (.str a)
      pure (A.map (r.name, ·))
    | none => pure none

/-- The decoded source `s`, elaborated: `V` and `fixed` from the `acts` block, each joined act's tree from `checkAct`,
    `declared := (declaredNames environment).length`; then `elaborateMap D`. Without `acts@0` no act is read. -/
def elaborateSource (environment : Json) (s : VE.NormDefaults.Wire.SourceU) : Except String ElaboratedU := do
  let fx ← VE.Norms.Wire.actsFixed (VE.Norms.Wire.actsProfiles true environment) environment
  -- the `acts` block's frames are refused by the norms decoder until the hook reads joined acts (ap-3db)
  let V : Vocab := ⟨[], []⟩
  let acts ← if s.src.ne.profiles.contains "acts@0" then actsOf fx V s.U else pure []
  let D : ActsDoc := ⟨s.U, V, fx, acts, (VE.NormDefaults.Wire.declaredNames environment).length⟩
  match h : elaborateMap D with
  | .ok (U', M) => pure ⟨s, D, rfl, U', M, h⟩
  | .error e => throw e

/-- `decodeSourceU`; then `D`: `V` and `fixed` from the `acts` block, each joined act's tree from `checkAct` (which is
    deterministic, so it is the decoder's answer), `declared := (declaredNames environment).length`; then
    `elaborateMap D`. -/
def decodeElaboratedU (environment norms : Json) : Except String ElaboratedU :=
  VE.NormDefaults.Wire.decodeSourceU environment norms >>= elaborateSource environment

/-! ### Theorems (6.4) -/

theorem elaborateSource_s {environment : Json} {s : VE.NormDefaults.Wire.SourceU} {e : ElaboratedU}
    (h : elaborateSource environment s = .ok e) : e.s = s := by
  unfold elaborateSource at h
  simp only [bind, Except.bind] at h
  repeat' split at h
  all_goals first | (cases h; done) | (simp only [pure, Except.pure, Except.ok.injEq] at h; subst h; rfl)

theorem decodeElaboratedU_source {environment norms : Lean.Json} {e : ElaboratedU}
    (h : decodeElaboratedU environment norms = .ok e) :
    VE.NormDefaults.Wire.decodeSourceU environment norms = .ok e.s := by
  unfold decodeElaboratedU at h
  cases hs : VE.NormDefaults.Wire.decodeSourceU environment norms with
  | error err => rw [hs] at h; cases h
  | ok s => rw [hs] at h; exact congrArg _ (elaborateSource_s h).symm

theorem decodeElaboratedU_wellFormed {environment norms : Lean.Json} {e : ElaboratedU}
    (h : decodeElaboratedU environment norms = .ok e) : VE.NormDefaults.WellFormedU e.U' = true :=
  (elaborateMap_ok e.hE).2.2.2.2.1

/-- A document whose acts are all lexical elaborates to itself (AP-3's "byte-identical to AP-1" test). -/
theorem decodeElaboratedU_lexical {environment norms : Lean.Json} {e : ElaboratedU}
    (h : decodeElaboratedU environment norms = .ok e) (hl : e.D.acts = []) : e.U' = e.s.U ∧ e.M = ⟨[], []⟩ := by
  have hs : splitAtoms e.D = fun _ => none := funext fun p => by simp [splitAtoms, hl]
  obtain ⟨_, _, hU, hM, _⟩ := elaborateMap_ok e.hE
  rw [hs, splitDoc_none] at hU
  rw [hs] at hM
  exact ⟨hU.trans e.hU, hM.trans (by simp [splitMap, partsOf])⟩

end VE.Acts.Decode
