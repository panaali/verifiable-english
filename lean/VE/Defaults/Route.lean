import VE.Defaults.Wire
import VE.NormDefaults.PacksLegacy

/-! The layered route's kind table with defeasible's row (docs/spec/premise-packs.md 2.10; plan DF-1a; DRI DF4).

`Defaults/Wire.lean` imports `NormDefaults/Layered.lean`, so the table with the `defaults-*` row, and `runLayered`,
which dispatches over it, sit here, after both (df-1ac deviation 1). The table is today's four rows (`legacyRows`) and
the four `defaults-*` kinds as one entry of its construction (`defaultsRows`): each needs the `soft` pack and answers
by `defaultsCase` on `viewOf`, the view through the route's own `decodeLayered`. Every other kind is dispatched as
before (`layeredKindCase_other`). -/
namespace VE.NormDefaults.Wire
open Lean

def defaultsKinds : List String := ["defaults-elaborate", "defaults-coherence", "defaults-certificate", "defaults-model"]

/-- Defeasible's row (DF4): the four kinds, each needing the soft pack, answered by `defaultsCase` (spec 7.2). -/
def defaultsRows : List (Packs.KindRow LayeredU) := defaultsKinds.map fun k =>
  ⟨k, some "soft", fun _ id j => do
    match ← VE.Defaults.Wire.defaultsCase (← VE.Defaults.Wire.viewOf j) id k j with
    | some a => pure a
    | none => throw "unreachable"⟩

/-- The layered route's kind table. -/
def layeredRows : List (Packs.KindRow LayeredU) := legacyRows ++ defaultsRows

def layeredKindCase (L : LayeredU) (id kind : String) (j : Json) : Except String (Option Json) :=
  Packs.dispatch layeredRows (L.packs.map (·.id)) L id kind j

/-- No answer of another kind changes: a kind outside the row is dispatched by today's rows (`kindCase`, equal to
    `layeredCase` by `Packs.kindCase_eq`). -/
theorem layeredKindCase_other (L : LayeredU) (id kind : String) (j : Json) (hk : kind ∉ defaultsKinds) :
    layeredKindCase L id kind j = kindCase L id kind j := by
  have hf : defaultsRows.find? (·.kind == kind) = none := by
    simp only [defaultsKinds, List.mem_cons, List.not_mem_nil, or_false, not_or] at hk
    obtain ⟨h1, h2, h3, h4⟩ := hk
    simp [defaultsRows, defaultsKinds, Ne.symm h1, Ne.symm h2, Ne.symm h3, Ne.symm h4]
  simp only [layeredKindCase, kindCase, Packs.dispatch, layeredRows, List.find?_append, hf, Option.or_none]

/-- A `norm-defaults-*` or `defaults-*` case on the soft or rights branch. -/
def runLayered (id kind : String) (j : Json) : Except String Json := do
  let L ← decodeLayered j
  match ← layeredKindCase L id kind j with
  | some a => pure a
  | none => throw s!"UnsupportedProfile: case kind {kind} is not available on the {L.route} norm-defaults branch"

end VE.NormDefaults.Wire
