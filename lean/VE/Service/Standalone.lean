import VE.Norms.Wire
import VE.Core.Wire
import VE.Route.Run

/-! Standalone service validation and identity endpoints. These wrap the same
decoders used by the route; successful model answers require a checked model. -/
namespace VE.Service.Standalone
open Lean

/-- The `regulated` extension checked as `Norms.Wire.decodeNormsEnvironment`
checks it, on any family: Python validates it in the environment constructor,
whichever checker family the envelope selects. -/
def checkRegulated (predicates : List (String × Json)) : Except String Unit := do
  let regs ← predicates.filterMapM fun (p, entry) => do
    match entry.getObjVal? "regulated" with
    | .error _ => pure none
    | .ok raw =>
      if (entry.getObjVal? "defined").isOk then
        throw s!"RegulatedDefinedPredicate: {p}"
      if (entry.getObjVal? "functional").isOk || (entry.getObjVal? "total").isOk then
        throw s!"RegulatedFlag: {p}"
      let args ← VE.Bridge.strings (← entry.getObjVal? "arguments")
      some <$> VE.Norms.Wire.decodeRegulated p args raw
  if regs.length > 64 then throw "ResourceLimit: regulated predicates"
  VE.Norms.actChecks regs

/-- A gated envelope and the environment JSON its family decoders read: the
submitted one, with any `regulated` extension removed after it is checked.
Identities are computed over the submitted JSON. -/
structure Validated where
  envelope : VE.Route.Gate.Envelope
  decodable : Json

def validateFamily (e : VE.Route.Gate.Envelope) (environment : Json) : Except String Unit :=
  match e.family with
  | .closureNary => do
    let _ ← VE.Core.Bridge.decodeEnvironment environment
    pure ()
  | .order => do
    let _ ← VE.Route.Wire.decodeOrderVocabulary e.vocabulary
    pure ()
  | .fol | .closure => do
    let _ ← VE.Route.Run.decodeRouteVocabulary e
    pure ()

/-- Remove the named fields from every predicate entry. -/
def stripPredicates (e : VE.Route.Gate.Envelope) (environment : Json) (names : List String) :
    Except String Validated := do
  let predicates ← VE.Bridge.fields (← e.vocabulary.getObjVal? "predicates")
  let stripped ← predicates.mapM fun (p, entry) => do
    pure (p, Json.mkObj ((← VE.Bridge.fields entry).filter (fun f => !names.contains f.1)))
  let vocabulary := e.vocabulary.setObjVal! "predicates" (Json.mkObj stripped)
  pure ⟨{ e with vocabulary }, environment.setObjVal! "vocabulary" vocabulary⟩

/-- With `typing`, the core family's decoder, which has no `defined` or data
flag fields, reads each predicate by its argument sorts alone: typing does not
depend on those fields, which Python has already validated. Validation and
model modes do not use this relaxation. -/
def validated (environment : Json) (typing : Bool := false) : Except String Validated := do
  let e ← VE.Route.Gate.decodeEnvelope environment
  let predicates ← VE.Bridge.fields (← e.vocabulary.getObjVal? "predicates")
  let mut v : Validated := ⟨e, environment⟩
  if e.profiles.contains "norms@0" &&
      predicates.any (fun (_, entry) => (entry.getObjVal? "regulated").isOk) then
    -- Check the regulated extension, then strip it: the family decoders see
    -- regulated predicates as ordinary ones.
    checkRegulated predicates
    v ← stripPredicates v.envelope v.decodable ["regulated"]
  if typing && e.family == .closureNary then
    v ← stripPredicates v.envelope v.decodable ["defined", "functional", "total"]
  validateFamily v.envelope v.decodable
  pure v

def validatedEnvironment (environment : Json) : Except String VE.Route.Gate.Envelope :=
  (·.envelope) <$> validated environment

def environmentCase (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let environment ← j.getObjVal? "environment"
  let e ← validatedEnvironment environment
  let environmentId ← VE.Route.Wire.environmentId e.profiles environment
  pure (VE.Route.Wire.ok id [("environment_id", .str environmentId),
    ("profiles", toJson e.profiles), ("family", .str e.family.name)])

/-- Python sorts relation rows by typed tuple order. In the order family,
`$int` cells compare numerically even though they travel as strings. -/
def rowLE : List String → List Json → List Json → Bool
  | [], _, _ => true
  | sort :: sorts, x :: xs, y :: ys =>
    let left := x.getStr?.toOption.getD ""
    let right := y.getStr?.toOption.getD ""
    let ordering := if sort == "$int" then
      compare (left.toInt?.getD 0) (right.toInt?.getD 0)
      else compare left right
    if ordering == .eq then rowLE sorts xs ys else ordering == .lt
  | _, _, _ => true

/-- Domain order is semantic and is retained. The model decoder checks row
uniqueness and types before this normalisation is used for identity. -/
def normalizedModel (environment j : Json) : Except String Json := do
  let relations ← VE.Bridge.fields (← j.getObjVal? "relations")
  let predicates ← VE.Bridge.fields (← (← environment.getObjVal? "vocabulary").getObjVal? "predicates")
  let sorted ← relations.mapM fun (name, rows) => do
    let array ← rows.getArr?
    let entry ← match VE.Bridge.lookup predicates name with
      | some value => pure value
      | none => throw "unknown relation in model identity"
    let sorts ← VE.Bridge.strings (← entry.getObjVal? "arguments")
    pure (name, Json.arr ((array.toList.mergeSort (fun a b =>
      rowLE sorts (a.getArr?.toOption.getD #[]).toList
        (b.getArr?.toOption.getD #[]).toList)).toArray))
  pure (j.setObjVal! "relations" (Json.mkObj sorted))

def modelCase (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let environment ← j.getObjVal? "environment"
  let model ← j.getObjVal? "model"
  let checked ← validated environment
  let e := checked.envelope
  match e.family with
  | .closureNary =>
    let v ← VE.Core.Bridge.decodeEnvironment checked.decodable
    let _ ← VE.Core.Wire.decodeModel v model
    pure ()
  | .order =>
    let v ← VE.Route.Wire.decodeOrderVocabulary e.vocabulary
    let _ ← VE.Route.Wire.decodeOrderModel v model
    pure ()
  | .fol | .closure =>
    let v ← VE.Route.Run.decodeRouteVocabulary e
    let _ ← VE.Route.Wire.decodeDataModel v model
    pure ()
  let environmentId ← VE.Route.Wire.environmentId e.profiles environment
  let modelId ← VE.CertificateWire.digest
    s!"ve-model-{VE.Route.Wire.identityVersion e.profiles}\n"
    (Json.mkObj [("environment_id", .str environmentId),
      ("model", ← normalizedModel environment model)])
  pure (VE.Route.Wire.ok id [("valid", .bool true), ("model_id", .str modelId)])

/-- A standalone typing request accepts one closed formula or a document of
closed formulas. The family decoder performs the same typed AST check used by
its route. -/
def checkCase (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let environment ← j.getObjVal? "environment"
  let ast ← j.getObjVal? "ast"
  let checked ← validated environment (typing := true)
  let e := checked.envelope
  let items ← ast.getArr?
  let formula := match items[0]? with
    | some (.str _) => true
    | _ => false
  match e.family with
  | .fol =>
    let rv ← VE.Route.Run.decodeRouteVocabulary e
    if formula then
      let _ ← VE.Route.Wire.decodeClosed rv.environment ast (e.profiles.contains "data@0")
      pure ()
    else
      let _ ← VE.Route.Wire.decodeFormulas rv.environment ast (e.profiles.contains "data@0")
      pure ()
  | .closure =>
    let rv ← VE.Route.Run.decodeRouteVocabulary e
    if formula then
      let a ← VE.Closure.Bridge.decodeFormula 64 ast
      unless a.check rv.environment [] do throw "ill-typed or unbound formula"
    else
      let _ ← VE.Closure.Bridge.decodeFormulas rv.environment ast
      pure ()
  | .closureNary =>
    let v ← VE.Core.Bridge.decodeEnvironment checked.decodable
    if formula then
      let a ← VE.Core.Bridge.decodeFormula 64 ast
      VE.Core.Bridge.checkFormula v.environment a "formula"
    else
      let _ ← VE.Core.Bridge.decodeFormulas v.environment ast
      pure ()
  | .order =>
    let v ← VE.Route.Wire.decodeOrderVocabulary e.vocabulary
    if formula then
      let a ← VE.Order.Wire.decodeFormula 64 ast
      unless a.check v.vocabulary.environment [] do throw "ill-typed or unbound formula"
    else
      let _ ← VE.Order.Wire.decodeFormulas v.vocabulary.environment ast
      pure ()
  let envId ← VE.Route.Wire.environmentId e.profiles environment
  let meaningId ← VE.Route.Wire.meaningId e.profiles envId ast
  pure (VE.Route.Wire.ok id [("well_typed", .bool true), ("meaning_id", .str meaningId)])

/-- Source and meaning identities derive their domain from a checked
environment. Claim and edge bindings use their fixed v1 domains. -/
def identityCase (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let kind ← VE.Bridge.stringField j "kind"
  let value ← if kind == "source" then do
      let source ← VE.Bridge.stringField j "source"
      let version ← match j.getObjVal? "environment" with
        | .ok environment => do
          let e ← validatedEnvironment environment
          pure (VE.Route.Wire.identityVersion e.profiles)
        | .error _ => pure "v0"
      pure (VE.CertificateWire.sha256 (s!"ve-source-{version}\n" ++ source).toUTF8)
    else if kind == "meaning" then do
      let environment ← j.getObjVal? "environment"
      let e ← validatedEnvironment environment
      let environmentId ← VE.Route.Wire.environmentId e.profiles environment
      VE.Route.Wire.meaningId e.profiles environmentId (← j.getObjVal? "ast")
    else if kind == "model" then do
      let row ← modelCase j
      VE.Bridge.stringField row "model_id"
    else if kind == "claim" then do
      let payload ← j.getObjVal? "payload"
      let names := (← VE.Bridge.fields payload).map Prod.fst
      unless names == ["environment_id", "meaning_id", "source_id"] ||
          names == ["environment_id", "label", "meaning_id", "source_id"] do
        throw "invalid claim identity payload"
      VE.CertificateWire.digest "ve-claim-v1\n" payload
    else if kind == "edge" then do
      let payload ← j.getObjVal? "payload"
      VE.Bridge.exactFields payload
        ["version", "environment_id", "name", "premises", "conclusion"]
      VE.CertificateWire.digest "ve-deduction-v1\n" payload
    else throw s!"unknown identity kind {kind}"
  pure (VE.Route.Wire.ok id [("kind", .str kind), ("identity_id", .str value)])

def reported (run : Json → Except String Json) (j : Json) : Json :=
  match run j with
  | .ok result => result
  | .error message => Json.mkObj [("id", j.getObjValD "id"),
      ("status", .str "error"), ("error", .str message)]

end VE.Service.Standalone
