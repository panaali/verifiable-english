import VE.Defaults.Meaning
import VE.Defaults.Examples

/-! DF-2's checks on decoded documents (docs/spec/defeasible.md 8.2): `softX` is the decoder's own `X` followed by
the other packs' premises; `SwitchesOff` and the least decisions `δ_B` read at one-element situations; and
`replacementSafe` exactly when the other packs name no decision and no unsaid table of a pair member (spec 8.2's row,
DF-π and DF-α). A situation's premises are read through RD-9's `eval` (`eval_withFill`), so each `Prop` here is
decided on a finite model. DF-π's two `example`s (spec 8.5) are df-2b. -/
namespace VE.Defaults.MeaningFixtures
open VE.Defaults VE.Defaults.Fixtures
open VE.NormDefaults (UDoc unsaidName withFill finFill FiniteFill)
open VE.NormDefaults.Wire (LayeredU)

instance denoteDec (U : UDoc) (M : VE.FiniteModel Entity) (F : FiniteFill U Entity) (φ : VE.Formula)
    (ρ : List Entity) : Decidable (φ.denote (withFill U M.asStructure (finFill M F)) ρ) :=
  decidable_of_iff _ (VE.NormDefaults.eval_withFill U M F φ ρ)

instance typedDec (U : UDoc) (M : VE.FiniteModel Entity) (F : FiniteFill U Entity) (ss : List String)
    (vs : List Entity) : Decidable (VE.TupleTyped (withFill U M.asStructure (finFill M F)) ss vs) :=
  decidable_of_iff _ ((VE.NormDefaults.mem_allTuples M ss vs).trans
    (VE.Norms.tupleTyped_relation M.asStructure _ ss vs).symm)

instance switchesDec (D : VE.SoftNorms.SoftDoc) (U : UDoc) (M : VE.FiniteModel Entity) (F : FiniteFill U Entity) :
    Decidable (SwitchesOff D (withFill U M.asStructure (finFill M F))) := by
  unfold SwitchesOff VE.Norms.Sat; infer_instance

instance leastDec (D : VE.SoftNorms.SoftDoc) (U : UDoc) (M : VE.FiniteModel Entity) (F : FiniteFill U Entity)
    (p : String) (vs : List Entity) : Decidable (leastDecisions D (withFill U M.asStructure (finFill M F)) p vs) := by
  unfold leastDecisions; infer_instance

/-- The one-element situation with the predicates `on` true and no gap filled. -/
abbrev sit (L : LayeredU) (on : List String) : VE.Structure.{0} :=
  withFill L.U (sitOf L on).asStructure (finFill (sitOf L on) (fillOf L []))

def a1 : List Entity := [elemOf "assistant"]

/-! ## `softX` -/

/-- One default rule with two stated sufficient conditions: two soft premises. -/
def dTwo : Except String LayeredU := layered (envJ [xReq, xPerm, baseJ "urgent", baseJ "calm"] strictSoft)
  [ruleJ "r1" "x_required" true (dfltJ [un "urgent", un "calm"])]
def rA : VE.Formula := .all "assistant" (.unary "urgent" (.var 0))
def rB : VE.Formula := .ex "assistant" (.unary "calm" (.var 0))

#guard holds dTwo fun L => L.X.length == 2 && softX L.U L.D [rA, rB] == L.X ++ [rA, rB]
#guard holds dα fun L => softX L.U L.D [] == L.X

/-! ## `SwitchesOff` -/

/-- A strict rule with two switches, so that `Dflt_T` is two switch premises. -/
def dSw : Except String LayeredU := layered (envJ [xReq, xPerm]
    r#"{"parties":["operator","user"],"outranking":{"mode":"strict"}}"#)
  [ruleJ "r0" "x_required" true ",\"alterable\":[\"operator\",\"user\"]"]
def offOf (L : LayeredU) (i : Nat) : String := ((VE.SoftNorms.offDecisions L.D).map (·.1)).getD i ""

#guard holds dSw fun L => (dfltLabelled L.D).length == 2 && decide (SwitchesOff L.D (sit L [])) &&
  !decide (SwitchesOff L.D (sit L [offOf L 0])) && !decide (SwitchesOff L.D (sit L [offOf L 1]))
#guard holds dε fun L => decide (SwitchesOff L.D (sit L [exc1])) && !decide (SwitchesOff L.D (sit L [offOf L 0]))

/-! ## The least decisions `δ_B` -/

#guard holds dTwo fun L => decide (leastDecisions L.D (sit L ["urgent"]) exc1 a1) &&
  decide (leastDecisions L.D (sit L ["calm"]) exc1 a1) && decide (leastDecisions L.D (sit L ["urgent", "calm"]) exc1 a1)
#guard holds dTwo fun L => !decide (leastDecisions L.D (sit L []) exc1 a1) &&
  !decide (leastDecisions L.D (sit L ["urgent"]) exc1 []) && !decide (leastDecisions L.D (sit L ["urgent"]) "a" a1) &&
  !decide (leastDecisions L.D (sit L ["urgent"]) "urgent" a1)
-- No switch is ever a least decision (DF-ε's switch, at a situation where it is on).
#guard holds dε fun L => !decide (leastDecisions L.D (sit L [offOf L 0]) (offOf L 0) a1)

/-! ## `replacementSafe` (spec 8.2: DF-π with `R = []` true, DF-α with `R = [∀a. excepted_r1(a)]` false) -/

/-- DF-π: DF-α with `x_permitted` also unspecified, so both members of the pair have unsaid tables. -/
def dπ : Except String LayeredU := layered (envJ [xReq,
    regJ "x_permitted" "[\"assistant\"]" "permission" "unspecified" ",\"act\":\"{0} do x\""] strictSoft)
  [ruleJ "r1" "x_required" true dfltJ]

#guard holds dπ fun L => replacementSafe L.U L.D [] && replacementSafe L.U L.D [rA] &&
  !replacementSafe L.U L.D [.all "assistant" (.unary (unsaidName "x_permitted") (.var 0))]
#guard holds dα fun L => replacementSafe L.U L.D [] && !replacementSafe L.U L.D [.all "assistant" (.unary exc1 (.var 0))]

end VE.Defaults.MeaningFixtures
