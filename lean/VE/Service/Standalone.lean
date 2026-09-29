import VE.Norms.Plain
import VE.Core.Wire
import VE.Core.Layers
import VE.Route.Run
import VE.Service.TypingDiagnostic

/-! Standalone service validation and identity endpoints. These wrap the same
decoders used by the route; successful model answers require a checked model. -/
namespace VE.Service.Standalone
open Lean

/-- The `regulated` extension checked as `Norms.Wire.decodeNormsEnvironment`
checks it, on any family: Python validates it in the environment constructor,
whichever checker family the envelope selects. -/
def checkRegulated (predicates : List (String × Json)) : Except String Unit := do
  let _ ← VE.Norms.Plain.decodeRegulatedAll predicates
  pure ()

/-- A gated envelope and the environment JSON its family decoders read: the
submitted one, with any `regulated` extension removed after it is checked.
Identities are computed over the submitted JSON. -/
structure Validated where
  envelope : VE.Route.Gate.Envelope
  decodable : Json
  /-- On the core family with `definitions@0` or `data@0` layer fields: the
  environment with those fields, from which `Core.Layers` decodes them. -/
  layers : Option Json := none

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
  pure { envelope := { e with vocabulary }, decodable := environment.setObjVal! "vocabulary" vocabulary }

/-- A `reports@0` environment as its FOL family reads it for typing: the
profile, the `reports` block and constant verbalisations removed (the route
decoder the attribution decoder delegates to sees the same vocabulary). -/
def reportsReduced (environment : Json) : Except String Json := do
  let vocabulary ← environment.getObjVal? "vocabulary"
  let constants ← VE.Bridge.fields (← vocabulary.getObjVal? "constants")
  let constants ← constants.mapM fun (c, entry) => do
    pure (c, Json.mkObj ((← VE.Bridge.fields entry).filter (·.1 != "verbalisation")))
  let profiles := (← VE.Route.Gate.profilesOf environment).erase "reports@0"
  let fields := (← VE.Bridge.fields vocabulary).filter (·.1 != "reports")
  pure ((environment.setObjVal! "profiles" (toJson profiles)).setObjVal! "vocabulary"
    ((Json.mkObj fields).setObjVal! "constants" (Json.mkObj constants)))

/-- An `alternatives@0` environment as typing reads it: the block removed and
its four profile words declared over the block's role sorts (Python's
`Environment` overlay), the profile removed. -/
def alternativesReduced (environment : Json) : Except String Json := do
  let block ← environment.getObjVal? "alternatives"
  let chooser ← VE.Bridge.stringField block "chooser"
  let action ← VE.Bridge.stringField block "action"
  let harm ← VE.Bridge.stringField block "harm"
  let word := fun (args : List String) => Json.mkObj [("arguments", toJson args),
    ("description", .str "alternatives@0 profile word")]
  let vocabulary ← environment.getObjVal? "vocabulary"
  let predicates ← VE.Bridge.fields (← vocabulary.getObjVal? "predicates")
  let words := [("avoidable", word [harm, chooser]), ("unavoidable", word [harm, chooser]),
    ("allows", word [action, harm]), ("prevents", word [action, harm])]
  let profiles := (← VE.Route.Gate.profilesOf environment).erase "alternatives@0"
  let fields := (← VE.Bridge.fields environment).filter (·.1 != "alternatives")
  pure (((Json.mkObj fields).setObjVal! "profiles" (toJson profiles)).setObjVal! "vocabulary"
    (vocabulary.setObjVal! "predicates" (Json.mkObj (predicates ++ words))))

/-- The environment typing decodes: statement-layer profiles that add no typing
constraint removed (`reports@0`, `soft-norms@0`, `alternatives@0` with its
profile words declared). -/
def typingReduced (environment : Json) : Except String Json := do
  let profiles := (VE.Route.Gate.profilesOf environment).toOption.getD []
  let mut env := environment
  if profiles.contains "reports@0" then env ← reportsReduced env
  if profiles.contains "alternatives@0" then env ← alternativesReduced env
  if profiles.contains "soft-norms@0" then
    -- The soft block and `instruction_of` fields declare parties and ranks,
    -- never argument sorts.
    let vocabulary ← env.getObjVal? "vocabulary"
    let predicates ← (← VE.Bridge.fields (← vocabulary.getObjVal? "predicates")).mapM fun (p, entry) => do
      pure (p, Json.mkObj ((← VE.Bridge.fields entry).filter (·.1 != "instruction_of")))
    let fields := (← VE.Bridge.fields vocabulary).filter (·.1 != "soft")
    env := (env.setObjVal! "profiles" (toJson (profiles.filter (fun p =>
      p != "soft-norms@0" && p != "reports@0" && p != "alternatives@0")))).setObjVal! "vocabulary"
      ((Json.mkObj fields).setObjVal! "predicates" (Json.mkObj predicates))
  pure env

/-- With `typing`, the core family's decoder, which has no `defined` or data
flag fields, reads each predicate by its argument sorts alone, and a `reports@0`
environment is read without its statement-layer profiles (`typingReduced`): typing
depends on none of these, and Python has
already validated them. Validation and model modes do not use these relaxations. -/
def validated (environment : Json) (typing : Bool := false) : Except String Validated := do
  -- Typing only: other modes keep the gate's refusal of these statement profiles.
  let environment ← if typing then typingReduced environment else pure environment
  let e ← VE.Route.Gate.decodeEnvelope environment
  let predicates ← VE.Bridge.fields (← e.vocabulary.getObjVal? "predicates")
  let mut v : Validated := { envelope := e, decodable := environment }
  if e.profiles.contains "norms@0" &&
      predicates.any (fun (_, entry) => (entry.getObjVal? "regulated").isOk) then
    -- Check the regulated extension, then strip it: the family decoders see
    -- regulated predicates as ordinary ones.
    checkRegulated predicates
    v ← stripPredicates v.envelope v.decodable ["regulated"]
  if typing && e.family == .closureNary then
    v ← stripPredicates v.envelope v.decodable ["defined", "functional", "total"]
  else if e.family == .closureNary && VE.Core.Layers.usesLayers v.decodable then
    -- The core decoder has neither layer: they are validated over the FOL
    -- projection by the FOL route's decoders, as the core route does.
    let _ ← VE.Core.Layers.decodeLayers e.profiles v.decodable
    let layered := v.decodable
    v ← stripPredicates v.envelope v.decodable VE.Core.Layers.layerFields
    v := { v with layers := some layered }
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

/-- Python's model identity normalisation (`ve/model.py` `_normalized`): each
domain's entities and each relation's rows sorted. The model decoder checks
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
  let domains ← VE.Bridge.fields (← j.getObjVal? "domains")
  let domains ← domains.mapM fun (name, values) => do
    let array ← values.getArr?
    pure (name, Json.arr ((array.toList.mergeSort (fun a b =>
      decide ((a.getStr?.toOption.getD "") ≤ (b.getStr?.toOption.getD "")))).toArray))
  pure ((j.setObjVal! "relations" (Json.mkObj sorted)).setObjVal! "domains" (Json.mkObj domains))

def modelCase (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let environment ← j.getObjVal? "environment"
  let model ← j.getObjVal? "model"
  let checked ← validated environment
  let e := checked.envelope
  match e.family with
  | .closureNary =>
    let v ← VE.Core.Bridge.decodeEnvironment checked.decodable
    match checked.layers with
    | none =>
      let _ ← VE.Core.Wire.decodeModel v model
      pure ()
    | some layered =>
      -- As `Core.Layers.run`: the FOL projection of the model with its flags
      -- checked and defined tables computed, then the core model with them.
      let rv ← VE.Core.Layers.decodeLayers e.profiles layered
      let names := (← VE.Core.Layers.folPredicates layered).map Prod.fst
      let M ← VE.Route.Wire.decodeDataModel rv (← VE.Core.Layers.folModel names model)
      let tables := (VE.Definitions.names rv.definitions).map fun p =>
        (p, VE.Core.Layers.tableJson (M.relations p))
      let relations ← VE.Bridge.fields (← model.getObjVal? "relations")
      let _ ← VE.Core.Wire.decodeModel v (model.setObjVal! "relations" (Json.mkObj (relations ++ tables)))
      pure ()
  | .order =>
    let v ← VE.Route.Wire.decodeOrderVocabulary e.vocabulary
    let _ ← VE.Route.Wire.decodeOrderModel v model
    pure ()
  | .fol | .closure =>
    let v ← VE.Route.Run.decodeRouteVocabulary e
    let _ ← VE.Route.Wire.decodeDataModel v model
    pure ()
  -- The norms profile generator last, as Python's `validate_background` orders
  -- it: each required relation within its permission (`Plain.profileOk`).
  let predicates ← VE.Bridge.fields (← (← environment.getObjVal? "vocabulary").getObjVal? "predicates")
  if predicates.any (fun (_, entry) => (entry.getObjVal? "regulated").isOk) then
    VE.Norms.Plain.profileOk ⟨← VE.Norms.Plain.decodeRegulatedAll predicates, [], []⟩ model
  let environmentId ← VE.Route.Wire.environmentId e.profiles environment
  let modelId ← VE.CertificateWire.digest
    s!"ve-model-{VE.Route.Wire.identityVersion e.profiles}\n"
    (Json.mkObj [("environment_id", .str environmentId),
      ("model", ← normalizedModel environment model)])
  pure (VE.Route.Wire.ok id [("valid", .bool true), ("model_id", .str modelId)])

/-- A standalone typing request accepts one closed formula or a document of
closed formulas. The family decoder performs the same typed AST check used by
its route. -/
def decodeTyped (checked : Validated) (ast : Json) (formula : Bool) : Except String Unit := do
  let e := checked.envelope
  -- Python's AST limits hold on every family, counted across a document; the
  -- closure, core and order single-formula decoders check depth only.
  VE.Route.AstLimit.check (← if formula then pure [ast] else (·.toList) <$> ast.getArr?)
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

/-- The frozen pre-route envelopes: `ve.core@0` (v0) and `ve.core@0.1`
(closure, or order with exactly the order profiles). Returns the profiles
Python reports and the identity domain version. -/
def legacyTyped (environment ast : Json) (formula : Bool) :
    Except String (List String × String) := do
  let language ← VE.Bridge.stringField environment "language"
  let asts := if formula then Json.arr #[ast] else ast
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

def legacyCheckCase (id : String) (environment ast : Json) (formula : Bool) (items : List Json) :
    Except String Json := do
  let (_, version) ← match legacyTyped environment ast formula with
    | .ok result => pure result
    | .error message =>
      let profiles := if environment.getObjValD "language" == .str "ve.core@0" then ["relational-fol@0"]
        else match environment.getObjValD "profiles" with
          | .arr ps => ps.toList.filterMap (·.getStr?.toOption)
          | _ => []
      if message.startsWith "UnsupportedProfile" then throw message
      throw ((TypingDiagnostic.diagnose profiles (environment.getObjValD "vocabulary")
        (if formula then [ast] else items)).getD message)
  let envId ← VE.CertificateWire.digest s!"ve-environment-{version}\n" environment
  let meaningId ← VE.CertificateWire.digest s!"ve-meaning-{version}\n"
    (Json.mkObj [("environment_id", .str envId), ("ast", ast)])
  pure (VE.Route.Wire.ok id [("well_typed", .bool true), ("meaning_id", .str meaningId)])

def checkCase (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let environment ← j.getObjVal? "environment"
  let ast ← j.getObjVal? "ast"
  if environment.getObjValD "language" != Json.str "ve.core@0.2" then
    let items ← ast.getArr?
    return ← legacyCheckCase id environment ast
      (match items[0]? with | some (Json.str _) => true | _ => false) items.toList
  let checked ← validated environment (typing := true)
  let e := checked.envelope
  let items ← ast.getArr?
  let formula := match items[0]? with
    | some (.str _) => true
    | _ => false
  -- The verdict is the decoder's; a typing rejection is named as Python names it.
  match decodeTyped checked ast formula with
  | .ok () => pure ()
  | .error message =>
    throw ((TypingDiagnostic.diagnose e.profiles e.vocabulary
      (if formula then [ast] else items.toList)).getD message)
  -- Identities bind the submitted environment and profiles.
  let profiles ← VE.Route.Gate.profilesOf environment
  let envId ← VE.Route.Wire.environmentId profiles environment
  let meaningId ← VE.Route.Wire.meaningId profiles envId ast
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
