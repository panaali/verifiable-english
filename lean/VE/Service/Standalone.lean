import VE.Norms.Plain
import VE.Core.Wire
import VE.Core.Layers
import VE.Core.Surface
import VE.Closure.Surface
import VE.Order.Surface
import VE.Route.Run
import VE.Service.TypingDiagnostic
import VE.Risk.Wire

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

/-- A `risk@0` environment as typing reads it (docs/spec/english-lean-s3.md 2.3): the risk declarations
removed exactly as `Risk.Wire.riskNormsView` removes them (the `risk` block, `unit_schema`, `units`, each
predicate's `argument_units`, each constant's `unit` and `verbalisation`), the `alternatives` block kept, the
profile dropped, and the severity sort, its classes and the five risk predicates declared with the signatures
of Python's `Environment` (`ve/environment.py:668–680`). Applied before `alternativesReduced`, while the block
still names the role sorts. -/
def riskReduced (environment : Json) : Except String Json := do
  let ps ← VE.Route.Gate.profilesOf environment
  let block ← environment.getObjVal? "alternatives"
  let severity ← (← environment.getObjVal? "risk").getObjVal? "severity"
  let sort ← VE.Bridge.stringField severity "sort"
  let classes ← VE.Bridge.strings (← severity.getObjVal? "classes")
  let action ← VE.Bridge.stringField block "action"
  let harm ← VE.Bridge.stringField block "harm"
  let view ← VE.Risk.Wire.riskNormsView environment ps
  let view := (view.setObjVal! "alternatives" block).setObjVal! "profiles" (toJson (ps.erase "risk@0"))
  let vocabulary ← view.getObjVal? "vocabulary"
  let sorts ← VE.Bridge.fields (← vocabulary.getObjVal? "sorts")
  let constants ← VE.Bridge.fields (← vocabulary.getObjVal? "constants")
  let predicates ← VE.Bridge.fields (← vocabulary.getObjVal? "predicates")
  let word := fun (args : List String) => Json.mkObj [("arguments", toJson args),
    ("description", .str "risk@0 generated word")]
  let words := [("risk__might_lead_to", word [action, harm]), ("risk__class", word [harm, sort]),
    ("risk__more_severe", word [sort, sort]), ("risk__or_worse", word [harm, sort]),
    ("risk__less_worst", word [action, action])]
  let severityClasses := classes.map fun c => (c, Json.mkObj [("sort", .str sort),
    ("description", .str "risk severity class")])
  pure (view.setObjVal! "vocabulary" (((vocabulary.setObjVal! "sorts"
    (Json.mkObj (sorts ++ [(sort, Json.mkObj [("description", .str "risk severity")])]))).setObjVal! "constants"
    (Json.mkObj (constants ++ severityClasses))).setObjVal! "predicates" (Json.mkObj (predicates ++ words))))

/-- The environment typing decodes: statement-layer profiles that add no typing
constraint removed (`reports@0`, `soft-norms@0`, `rights@0`, `speech-acts@0`
with its `speech_acts` scope block, `alternatives@0` with its profile words
declared). -/
def typingReduced (environment : Json) : Except String Json := do
  let profiles := (VE.Route.Gate.profilesOf environment).toOption.getD []
  let mut env := environment
  if profiles.contains "reports@0" then env ← reportsReduced env
  if profiles.contains "alternatives@0" then env ← alternativesReduced env
  if profiles.contains "speech-acts@0" || profiles.contains "rights@0" then
    -- The speech-act scope names addressees and definites and the rights
    -- layer's declarations are ordinary vocabulary: neither constrains typing.
    let fields := (← VE.Bridge.fields env).filter (·.1 != "speech_acts")
    let vocabulary ← env.getObjVal? "vocabulary"
    let vocabulary := Json.mkObj ((← VE.Bridge.fields vocabulary).filter (·.1 != "rights"))
    env := ((Json.mkObj fields).setObjVal! "profiles" (toJson ((← VE.Route.Gate.profilesOf env).filter
      (fun p => p != "speech-acts@0" && p != "rights@0")))).setObjVal! "vocabulary" vocabulary
  if profiles.contains "soft-norms@0" then
    -- The soft block and `instruction_of` fields declare parties and ranks,
    -- never argument sorts.
    let vocabulary ← env.getObjVal? "vocabulary"
    let predicates ← (← VE.Bridge.fields (← vocabulary.getObjVal? "predicates")).mapM fun (p, entry) => do
      pure (p, Json.mkObj ((← VE.Bridge.fields entry).filter (·.1 != "instruction_of")))
    let fields := (← VE.Bridge.fields vocabulary).filter (·.1 != "soft")
    env := (env.setObjVal! "profiles" (toJson (profiles.filter (fun p =>
      p != "soft-norms@0" && p != "reports@0" && p != "alternatives@0" && p != "rights@0" &&
      p != "speech-acts@0")))).setObjVal! "vocabulary"
      ((Json.mkObj fields).setObjVal! "predicates" (Json.mkObj predicates))
  pure env

/-- The environment identity, over the environment as Python stores it
(`Environment.to_dict`): regulated act phrases in canonical form, as the norms
route binds them (`Norms.Wire.canonicalEnvironmentJson`). -/
def environmentIdOf (profiles : List String) (environment : Json) : Except String String := do
  VE.Route.Wire.environmentId profiles (← VE.Norms.Wire.canonicalEnvironmentJson environment)

/-- Python's `RESERVED` words the frozen surface list (`Surface.reserved`,
which every family decoder checks) lacks: `no`, a definitions keyword. -/
def pythonReserved : List String := ["no"]

/-- With `typing`, the core family's decoder, which has no `defined` or data
flag fields, reads each predicate by its argument sorts alone, and a `reports@0`
environment is read without its statement-layer profiles (`typingReduced`): typing
depends on none of these, and Python has
already validated them. Validation and model modes do not use these relaxations. -/
def validated (environment : Json) (typing : Bool := false) : Except String Validated := do
  -- Typing only: other modes keep the gate's refusal of these statement profiles.
  let environment ← if typing then typingReduced environment else pure environment
  let e ← VE.Route.Gate.decodeEnvelope environment
  for kind in ["sorts", "predicates", "constants"] do
    for (name, _) in ← VE.Bridge.fields (← e.vocabulary.getObjVal? kind) do
      if pythonReserved.contains name then throw s!"invalid or reserved declaration: {name}"
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
    -- projection by the FOL route's decoders, as the core route does. An n-ary
    -- defined predicate is outside the projection, so nothing here would check
    -- its body or compute its table.
    if (VE.Core.Layers.predicatesOf v.decodable).any (fun (_, entry) =>
        (entry.getObjVal? "defined").isOk && VE.Core.Layers.arity entry > 2) then
      throw (VE.Route.Gate.unsupported "n-ary definitions on the core family are deferred")
    let _ ← VE.Core.Layers.decodeLayers e.profiles v.decodable
    let layered := v.decodable
    v ← stripPredicates v.envelope v.decodable VE.Core.Layers.layerFields
    v := { v with layers := some layered }
  validateFamily v.envelope v.decodable
  pure v

def validatedEnvironment (environment : Json) : Except String VE.Route.Gate.Envelope :=
  (·.envelope) <$> validated environment

/-! ## The frozen pre-route envelopes -/

/-- A frozen pre-route envelope, decoded by its frozen decoder: `ve.core@0`
(v0), or `ve.core@0.1` (closure, or order with exactly the order profiles). -/
inductive Legacy where
  | v0 (v : VE.Bridge.Vocabulary)
  | closure (v : VE.Bridge.Vocabulary)
  | order (v : VE.Order.Vocabulary)

/-- Python's identity domain (`Environment.identity_version`). -/
def Legacy.version : Legacy → String
  | .v0 _ => "v0"
  | .closure _ => "v0.1"
  | .order _ => "v0.1-order"

def Legacy.family : Legacy → String
  | .v0 _ => "fol"
  | .closure _ => "closure"
  | .order _ => "order"

def isLegacy (environment : Json) : Bool :=
  environment.getObjValD "language" == .str "ve.core@0" ||
    environment.getObjValD "language" == .str "ve.core@0.1"

def decodeLegacy (environment : Json) : Except String Legacy := do
  let language ← VE.Bridge.stringField environment "language"
  if language == "ve.core@0" then pure (.v0 (← VE.Bridge.decodeEnvironment environment))
  else if language == "ve.core@0.1" then
    if environment.getObjValD "profiles" == toJson ["order@0", "relational-fol@0"] then
      pure (.order (← VE.Order.Wire.decodeEnvironment environment))
    else pure (.closure (← VE.Closure.Bridge.decodeEnvironment environment))
  else throw "UnsupportedProfile: Unsupported language"

def legacyEnvironmentId (l : Legacy) (environment : Json) : Except String String :=
  VE.CertificateWire.digest s!"ve-environment-{l.version}\n" environment

def legacyMeaningId (l : Legacy) (envId : String) (ast : Json) : Except String String :=
  VE.CertificateWire.digest s!"ve-meaning-{l.version}\n"
    (Json.mkObj [("environment_id", .str envId), ("ast", ast)])

def environmentCase (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let environment ← j.getObjVal? "environment"
  if isLegacy environment then
    let l ← decodeLegacy environment
    let envId ← legacyEnvironmentId l environment
    -- v0 names its one profile in `profile`; ve.core@0.1 lists `profiles`.
    return VE.Route.Wire.ok id ([("environment_id", .str envId)] ++
      (match l with
       | .v0 _ => [("profile", environment.getObjValD "profile")]
       | _ => [("profiles", environment.getObjValD "profiles")]) ++ [("family", .str l.family)])
  let e ← validatedEnvironment environment
  let environmentId ← environmentIdOf e.profiles environment
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

/-- An already-identified model (Python's `FiniteModel`) carries the identities
it claims; each must be the recomputed one. -/
def checkClaimed (j : Json) (environmentId modelId : String) : Except String Unit := do
  if let .ok claimed := j.getObjVal? "claimed" then
    VE.Bridge.exactFields claimed ["environment_id", "model_id"]
    unless (← VE.Bridge.stringField claimed "environment_id") == environmentId do
      throw "InvalidModel: model belongs to a different environment"
    unless (← VE.Bridge.stringField claimed "model_id") == modelId do
      throw "InvalidModel: model identity does not match its contents"

def legacyModelCase (id : String) (environment model : Json) (j : Json) : Except String Json := do
  let l ← decodeLegacy environment
  match l with
  | .v0 v | .closure v =>
    let _ ← VE.Bridge.decodeModel v model
    pure ()
  | .order v =>
    let _ ← VE.Order.Wire.decodeValidModel v model
    pure ()
  let environmentId ← legacyEnvironmentId l environment
  let modelId ← VE.CertificateWire.digest s!"ve-model-{l.version}\n"
    (Json.mkObj [("environment_id", .str environmentId),
      ("model", ← normalizedModel environment model)])
  checkClaimed j environmentId modelId
  pure (VE.Route.Wire.ok id [("valid", .bool true), ("model_id", .str modelId)])

def modelCase (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let environment ← j.getObjVal? "environment"
  let model ← j.getObjVal? "model"
  if isLegacy environment then return ← legacyModelCase id environment model j
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
  let environmentId ← environmentIdOf e.profiles environment
  let modelId ← VE.CertificateWire.digest
    s!"ve-model-{VE.Route.Wire.identityVersion e.profiles}\n"
    (Json.mkObj [("environment_id", .str environmentId),
      ("model", ← normalizedModel environment model)])
  checkClaimed j environmentId modelId
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
  let envId ← environmentIdOf profiles environment
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
      let environmentId ← environmentIdOf e.profiles environment
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

/-- Python's Background of a ve.core@0.2 FOL-family environment, in generator
order: the route's flags, definitions and literals, then the profile premise of
each declared norms pair, as `Norms.Plain` regenerates it. -/
def folBackground (environment : Json) (rv : VE.Route.Wire.RouteVocabulary) :
    Except String (List (VE.Formula × String)) := do
  let predicates ← VE.Bridge.fields (← (← environment.getObjVal? "vocabulary").getObjVal? "predicates")
  let T : VE.Norms.Tree := ⟨← VE.Norms.Plain.decodeRegulatedAll predicates, [], []⟩
  pure (VE.Route.Wire.fullBackground rv ++ (VE.Norms.pairPremises T).map (·, "profile"))

/-! ## Parsing -/

def encodeKind : VE.Closure.Kind → Json
  | .plus => .str "plus"
  | .star => .str "star"

/-- A closure-family formula on the wire (Python `_to_data`). -/
def encodeClosure : VE.Closure.Formula → Json
  | .top => Json.arr #[.str "top"]
  | .bottom => Json.arr #[.str "bottom"]
  | .unary p t => Json.arr #[.str "unary", .str p, VE.Route.Wire.encodeTerm t]
  | .binary p t u => Json.arr #[.str "binary", .str p, VE.Route.Wire.encodeTerm t, VE.Route.Wire.encodeTerm u]
  | .eq t u => Json.arr #[.str "eq", VE.Route.Wire.encodeTerm t, VE.Route.Wire.encodeTerm u]
  | .not a => Json.arr #[.str "not", encodeClosure a]
  | .and a b => Json.arr #[.str "and", encodeClosure a, encodeClosure b]
  | .or a b => Json.arr #[.str "or", encodeClosure a, encodeClosure b]
  | .implies a b => Json.arr #[.str "implies", encodeClosure a, encodeClosure b]
  | .all s a => Json.arr #[.str "forall", .str s, encodeClosure a]
  | .ex s a => Json.arr #[.str "exists", .str s, encodeClosure a]
  | .reachNamed k p t u => Json.arr #[.str "reach", encodeKind k, Json.arr #[.str "named", .str p],
      VE.Route.Wire.encodeTerm t, VE.Route.Wire.encodeTerm u]
  | .reachBody k s a t u => Json.arr #[.str "reach", encodeKind k,
      Json.arr #[.str "body", .str s, encodeClosure a], VE.Route.Wire.encodeTerm t, VE.Route.Wire.encodeTerm u]

def encodeCoreKind : VE.Core.Kind → Json
  | .plus => .str "plus"
  | .star => .str "star"

/-- A core-family (closure + n-ary) formula on the wire (Python `_to_data`). -/
def encodeCore : VE.Core.Formula → Json
  | .top => Json.arr #[.str "top"]
  | .bottom => Json.arr #[.str "bottom"]
  | .unary p t => Json.arr #[.str "unary", .str p, VE.Route.Wire.encodeTerm t]
  | .binary p t u => Json.arr #[.str "binary", .str p, VE.Route.Wire.encodeTerm t, VE.Route.Wire.encodeTerm u]
  | .atom p ts => Json.arr #[.str "atom", .str p, Json.arr (ts.map VE.Route.Wire.encodeTerm).toArray]
  | .eq t u => Json.arr #[.str "eq", VE.Route.Wire.encodeTerm t, VE.Route.Wire.encodeTerm u]
  | .not a => Json.arr #[.str "not", encodeCore a]
  | .and a b => Json.arr #[.str "and", encodeCore a, encodeCore b]
  | .or a b => Json.arr #[.str "or", encodeCore a, encodeCore b]
  | .implies a b => Json.arr #[.str "implies", encodeCore a, encodeCore b]
  | .all s a => Json.arr #[.str "forall", .str s, encodeCore a]
  | .ex s a => Json.arr #[.str "exists", .str s, encodeCore a]
  | .reachNamed k p t u => Json.arr #[.str "reach", encodeCoreKind k, Json.arr #[.str "named", .str p],
      VE.Route.Wire.encodeTerm t, VE.Route.Wire.encodeTerm u]
  | .reachBody k s a t u => Json.arr #[.str "reach", encodeCoreKind k,
      Json.arr #[.str "body", .str s, encodeCore a], VE.Route.Wire.encodeTerm t, VE.Route.Wire.encodeTerm u]

/-- Python's source cap (`MAX_SOURCE_BYTES`). -/
def maxSourceBytes : Nat := 65536

/-- A standalone parse (the plan's `parse` and `normalize` modes as one case).
The family's surface parser, which also types every statement, decides whether
`source` is accepted. The answer carries the parsed document on the wire (within
Python's AST limits) and, where the family has a printer, its canonical text.
Over a `definitions@0` environment defined predicates read as declared
predicates; the definitions surface sugar (`no`, `every … that is`, `iff`,
`define`) is in no Lean surface parser, so a source using it is rejected. -/
def parseCase (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let environment ← j.getObjVal? "environment"
  let source ← VE.Bridge.stringField j "source"
  let rejected := "SyntaxError: the source is not accepted by the Lean surface parser"
  -- The frozen runners' source limits (`Bridge.sourceIdentifierBudget`, the
  -- order surface's numeral cap), checked before parsing.
  let limits := fun (order : Bool) => do
    unless source.utf8ByteSize ≤ maxSourceBytes do
      throw s!"ResourceLimit: source exceeds {maxSourceBytes} bytes"
    unless VE.Bridge.sourceIdentifierBudget source do
      throw "ResourceLimit: source identifier exceeds 64 bytes"
    if order && VE.Order.Surface.oversizedNumeral source then throw "ResourceLimit: numeral length"
  if isLegacy environment then
    let l ← decodeLegacy environment
    limits (match l with | .order _ => true | _ => false)
    let (asts, canonical) ← match l with
      | .v0 v => do
        let some fs := VE.Surface.parse v.environment source | throw rejected
        pure (fs.map VE.Route.Wire.encodeFormula, some (VE.Surface.print fs))
      | .closure v => do
        let some fs := VE.Closure.Surface.parse v.environment source | throw rejected
        pure (fs.map encodeClosure, some (VE.Closure.Surface.print fs))
      | .order v => do
        let some fs := VE.Order.Surface.parse v.environment source | throw rejected
        pure (fs.map VE.Order.Surface.formulaJson, none)
    VE.Route.AstLimit.check asts
    return VE.Route.Wire.ok id ([("ast", Json.arr asts.toArray)] ++
      match canonical with
      | some text => [("canonical", .str text)]
      | none => [])
  let checked ← validated environment
  let e := checked.envelope
  limits (e.family == .order)
  let (asts, canonical) ← match e.family with
    | .fol => do
      let rv ← VE.Route.Run.decodeRouteVocabulary e
      let some fs := VE.Surface.parse rv.environment source | throw rejected
      pure (fs.map VE.Route.Wire.encodeFormula, some (VE.Surface.print fs))
    | .closure => do
      let rv ← VE.Route.Run.decodeRouteVocabulary e
      let some fs := VE.Closure.Surface.parse rv.environment source | throw rejected
      pure (fs.map encodeClosure, some (VE.Closure.Surface.print fs))
    | .closureNary => do
      let v ← VE.Core.Bridge.decodeEnvironment checked.decodable
      let some fs := VE.Core.Surface.parse v.environment source | throw rejected
      pure (fs.map encodeCore, some (VE.Core.Surface.print fs))
    | .order => do
      let v ← VE.Route.Wire.decodeOrderVocabulary e.vocabulary
      let some fs := VE.Order.Surface.parse v.vocabulary.environment source | throw rejected
      pure (fs.map VE.Order.Surface.formulaJson, none)
  VE.Route.AstLimit.check asts
  pure (VE.Route.Wire.ok id ([("ast", Json.arr asts.toArray)] ++
    match canonical with
    | some text => [("canonical", .str text)]
    | none => []))

def reported (run : Json → Except String Json) (j : Json) : Json :=
  match run j with
  | .ok result => result
  | .error message => Json.mkObj [("id", j.getObjValD "id"),
      ("status", .str "error"), ("error", .str message)]

end VE.Service.Standalone
