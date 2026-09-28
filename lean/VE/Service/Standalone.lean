import VE.Norms.Wire
import VE.Core.Wire
import VE.Route.Run

/-! Standalone service validation and identity endpoints. These wrap the same
decoders used by the route; successful model answers require a checked model. -/
namespace VE.Service.Standalone
open Lean

def validatedEnvironment (environment : Json) : Except String VE.Route.Gate.Envelope := do
  let e ← VE.Route.Gate.decodeEnvelope environment
  let predicates ← VE.Bridge.fields (← e.vocabulary.getObjVal? "predicates")
  if e.profiles.contains "norms@0" &&
      predicates.any (fun (_, entry) => (entry.getObjVal? "regulated").isOk) then
    -- The norms decoder strips and then checks the regulated extension.
    let _ ← VE.Norms.Wire.decodeNormsEnvironment environment
    pure e
  else
    match e.family with
    | .closureNary =>
      let _ ← VE.Core.Bridge.decodeEnvironment environment
      pure e
    | .order =>
      let _ ← VE.Route.Wire.decodeOrderVocabulary e.vocabulary
      pure e
    | .fol | .closure =>
      let _ ← VE.Route.Run.decodeRouteVocabulary e
      pure e

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
  let e ← validatedEnvironment environment
  match e.family with
  | .closureNary =>
    let v ← VE.Core.Bridge.decodeEnvironment environment
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
