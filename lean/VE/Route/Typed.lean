import VE.Core.Bridge
import VE.Core.Layers
import VE.Route.Wire

/-! The typed check of formulas, family by family (`check`, and `legacy` on the frozen envelopes): the one
function both the standalone typing service (`VE.Service.Standalone.decodeTyped`) and the English reader's typed
check (`VE.EnglishGrammar.typedCheck`) call, so the two cannot read one environment differently. `check` takes the gated
envelope of its typing view; `typingEnvironment` is the part of that view every caller shares: the core family's
decoder has no `defined` or data flag fields, so typing reads each of its predicates by its argument sorts
alone (Python validated the layers when it built the environment). -/

namespace VE.Route.Typed
open Lean

/-- The FOL/closure vocabulary; `defined` declarations need `definitions@0`. -/
def routeVocabulary (e : Gate.Envelope) : Except String Wire.RouteVocabulary := do
  let rv ← Wire.decodeVocabulary e.profiles e.vocabulary
  unless rv.definitions.isEmpty || e.profiles.contains "definitions@0" do
    throw "defined declarations require the definitions@0 profile"
  pure rv

/-- An envelope and its environment with the named fields removed from every predicate entry. -/
def stripPredicates (e : Gate.Envelope) (environment : Json) (names : List String) :
    Except String (Gate.Envelope × Json) := do
  let predicates ← VE.Bridge.fields (← e.vocabulary.getObjVal? "predicates")
  let stripped ← predicates.mapM fun (p, entry) => do
    pure (p, Json.mkObj ((← VE.Bridge.fields entry).filter (fun f => !names.contains f.1)))
  let vocabulary := e.vocabulary.setObjVal! "predicates" (Json.mkObj stripped)
  pure ({ e with vocabulary }, environment.setObjVal! "vocabulary" vocabulary)

/-- The environment typing decodes: on the core family, without the layer fields. -/
def typingEnvironment (e : Gate.Envelope) (environment : Json) : Except String (Gate.Envelope × Json) :=
  if e.family == .closureNary then stripPredicates e environment VE.Core.Layers.layerFields
  else pure (e, environment)

/-- The family decoder's typed check of one closed formula (`formula`) or a document of closed formulas, over
the envelope of a typing environment. Python's AST limits hold on every family, counted across a document; the
closure, core and order single-formula decoders check depth only. -/
def check (e : Gate.Envelope) (environment ast : Json) (formula : Bool) : Except String Unit := do
  VE.Route.AstLimit.check (← if formula then pure [ast] else (·.toList) <$> ast.getArr?)
  match e.family with
  | .fol =>
    let rv ← routeVocabulary e
    if formula then
      let _ ← Wire.decodeClosed rv.environment ast (e.profiles.contains "data@0")
      pure ()
    else
      let _ ← Wire.decodeFormulas rv.environment ast (e.profiles.contains "data@0")
      pure ()
  | .closure =>
    let rv ← routeVocabulary e
    if formula then
      let a ← VE.Closure.Bridge.decodeFormula 64 ast
      unless a.check rv.environment [] do throw "ill-typed or unbound formula"
    else
      let _ ← VE.Closure.Bridge.decodeFormulas rv.environment ast
      pure ()
  | .closureNary =>
    let v ← VE.Core.Bridge.decodeEnvironment environment
    if formula then
      let a ← VE.Core.Bridge.decodeFormula 64 ast
      VE.Core.Bridge.checkFormula v.environment a "formula"
    else
      let _ ← VE.Core.Bridge.decodeFormulas v.environment ast
      pure ()
  | .order =>
    let v ← Wire.decodeOrderVocabulary e.vocabulary
    if formula then
      let a ← VE.Order.Wire.decodeFormula 64 ast
      unless a.check v.vocabulary.environment [] do throw "ill-typed or unbound formula"
    else
      let _ ← VE.Order.Wire.decodeFormulas v.vocabulary.environment ast
      pure ()

/-- The frozen pre-route envelopes: the typed check of a document of formulas under `ve.core@0` (v0) or
`ve.core@0.1` (closure, or order with exactly the order profiles), with the profiles Python reports and the
identity domain version. -/
def legacy (environment asts : Json) : Except String (List String × String) := do
  let language ← VE.Bridge.stringField environment "language"
  if language == "ve.core@0" then
    let v ← VE.Bridge.decodeEnvironment environment
    let _ ← VE.Bridge.decodeDocument v.environment asts
    pure (["relational-fol@0"], "v0")
  else if language == "ve.core@0.1" then
    if environment.getObjValD "profiles" == toJson ["order@0", "relational-fol@0"] then
      let v ← VE.Order.Wire.decodeEnvironment environment
      let _ ← VE.Order.Wire.decodeFormulas v.environment asts
      pure (["order@0", "relational-fol@0"], "v0.1-order")
    else
      let v ← VE.Closure.Bridge.decodeEnvironment environment
      let _ ← VE.Closure.Bridge.decodeFormulas v.environment asts
      pure (["closure@0", "relational-fol@0"], "v0.1")
  else throw "UnsupportedProfile: Unsupported language"

end VE.Route.Typed
