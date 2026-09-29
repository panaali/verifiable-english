import VE.Norms.Wire
import VE.Route.Run

/-! Plain route cases on environments with `regulated` declarations, on every
checker family (the migration plan's stage 2c).

Python validates the `regulated` extension in the environment constructor
whichever family the envelope selects; the frozen family decoders reject the
field. Here the extension is validated exactly as `Wire.decodeNormsEnvironment`
validates it, removed, and the case is delegated to the unchanged route:

* `background`: the route's regenerated Background followed by the profile
  premise of each declared pair (Python's generator order: flags, definitions,
  literals, profile);
* `evaluate` and `countermodel`: the route's answer, provided the model
  satisfies every profile premise, else `InvalidModel(profile)`, as Python's
  `validate_background` reports it.

Neither answer carries an environment identity, so decoding the reduced
environment binds nothing. Certificate cases are not delegated: a certificate
binds the submitted environment and its Background. -/
namespace VE.Norms.Plain
open Lean
open VE.Bridge (fields strings)

/-- Every `regulated` declaration, checked as the norms decoder checks it. -/
def decodeRegulatedAll (predicates : List (String × Json)) : Except String (List Regulated) := do
  let regs ← predicates.filterMapM fun (p, entry) => do
    match entry.getObjVal? "regulated" with
    | .error _ => pure none
    | .ok raw =>
      if (entry.getObjVal? "defined").isOk then
        throw s!"RegulatedDefinedPredicate: {p}"
      if (entry.getObjVal? "functional").isOk || (entry.getObjVal? "total").isOk then
        throw s!"RegulatedFlag: {p}"
      let args ← strings (← entry.getObjVal? "arguments")
      some <$> Wire.decodeRegulated p args raw
  if regs.length > 64 then throw "ResourceLimit: regulated predicates"
  actChecks regs
  pure regs

/-- The environment without the `regulated` field of any predicate. -/
def strip (environment : Json) (predicates : List (String × Json)) : Except String Json := do
  let vocabulary ← environment.getObjVal? "vocabulary"
  let stripped ← predicates.mapM fun (p, entry) => do
    pure (p, Json.mkObj ((← fields entry).filter (·.1 != "regulated")))
  pure (environment.setObjVal! "vocabulary" (vocabulary.setObjVal! "predicates" (Json.mkObj stripped)))

def isPlainKind (kind : String) : Bool :=
  kind == "background" || kind == "evaluate" || kind == "countermodel"

/-- Python `_valid_profile`: each required relation is contained in its permission. -/
def profileOk (T : Tree) (model : Json) : Except String Unit := do
  let relations ← fields (← model.getObjVal? "relations")
  let rows (name : String) : Except String (Array Json) :=
    match VE.Bridge.lookup relations name with
    | some value => value.getArr?
    | none => pure #[]
  for pr in pairs T do
    let permitted ← rows pr.perm
    unless (← rows pr.req).all permitted.contains do
      throw s!"InvalidModel(profile): required relation {pr.req} exceeds permission {pr.perm}"

def run (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let kind ← VE.Route.Run.caseKind j
  let environment ← j.getObjVal? "environment"
  let e ← VE.Route.Gate.decodeEnvelope environment
  let predicates ← fields (← e.vocabulary.getObjVal? "predicates")
  let T : Tree := ⟨← decodeRegulatedAll predicates, [], []⟩
  let result ← VE.Route.Run.runCase (j.setObjVal! "environment" (← strip environment predicates))
  if kind == "background" then
    let profile := (pairPremises T).map VE.Route.Wire.encodeFormula
    let background := (← (← result.getObjVal? "background").getArr?) ++ profile.toArray
    let generators := (← (← result.getObjVal? "generators").getArr?) ++
      (profile.map (fun _ => Json.str "profile")).toArray
    return VE.Route.Wire.ok id [("background", .arr background), ("premises", .arr background),
      ("generators", .arr generators)]
  profileOk T (← j.getObjVal? "model")
  pure result

end VE.Norms.Plain
