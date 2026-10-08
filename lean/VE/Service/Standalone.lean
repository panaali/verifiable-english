import VE.Norms.Plain
import VE.Core.Wire
import VE.Core.Layers
import VE.Core.Surface
import VE.Closure.Surface
import VE.Order.Surface
import VE.Route.Run
import VE.Service.TypingDiagnostic
import VE.Service.ParseDiagnostic
import VE.Risk.Wire
import VE.Time.Wire
import VE.Compose.Dispatch
import VE.Alternatives.Wire
import VE.SpeechActs.Wire
import VE.Attribution.Wire
import VE.SoftNorms.Phases
import VE.Rights.Wire
import VE.Readings.Wire
import VE.NormDefaults.Wire

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

private def naryDefined (environment : Json) : List String :=
  (VE.Core.Layers.predicatesOf environment).filterMap fun (p, entry) =>
    if VE.Core.Layers.arity entry > 2 && (entry.getObjVal? "defined").isOk then some p else none

private def usedPredicates : VE.Core.Formula → List String
  | .top | .bottom | .eq _ _ => []
  | .unary p _ | .binary p _ _ | .atom p _ | .reachNamed _ p _ _ => [p]
  | .not a | .all _ a | .ex _ a => usedPredicates a
  | .and a b | .or a b | .implies a b => usedPredicates a ++ usedPredicates b
  | .reachBody _ _ a _ _ => usedPredicates a

private def visitDefinition (deps : List (String × List String)) (name : String)
    (stack : List String) (fuel : Nat) : Except String Unit := do
  if stack.contains name then throw s!"DependencyCycle: {name}"
  match fuel with
  | 0 => throw s!"DependencyCycle: {name}"
  | n + 1 =>
    for p in (VE.Bridge.lookup deps name).getD [] do
      if (VE.Bridge.lookup deps p).isSome then
        visitDefinition deps p (name :: stack) n

/-- Check n-ary definition bodies in the core family before Python constructs
their retained batch-14 tables. Unary and binary bodies use `decodeLayers`. -/
private def checkNaryDefinitions (environment : Json) : Except String Unit := do
  let core ← VE.Core.Layers.coreEnvironment environment
  let v ← VE.Core.Bridge.decodeEnvironment core
  let predicates ← VE.Bridge.fields (← (← environment.getObjVal? "vocabulary").getObjVal? "predicates")
  let mut deps : List (String × List String) := []
  for (p, entry) in predicates do
    if VE.Core.Layers.arity entry > 2 then
      if let .ok payload := entry.getObjVal? "defined" then
        VE.Bridge.exactFields payload ["arguments", "body"]
        let args ← VE.Bridge.strings (← payload.getObjVal? "arguments")
        unless args == (← VE.Bridge.strings (← entry.getObjVal? "arguments")) do
          throw "definition argument sorts differ"
        let body ← VE.Core.Bridge.decodeFormula 64 (← payload.getObjVal? "body")
        unless body.check v.environment args.reverse do
          throw "the body is not a typed formula over the symbols below it"
        deps := (p, usedPredicates body) :: deps
  for (p, _) in deps do
    visitDefinition deps p [] (deps.length + 1)

private def checkDataFlagFields (profiles : List String)
    (predicates : List (String × Json)) : Except String Unit := do
  for (_, entry) in predicates do
    if !profiles.contains "data@0" &&
        ((entry.getObjVal? "functional").isOk || (entry.getObjVal? "total").isOk) then
      throw "UnsupportedProfile: Predicate flags require data@0"
    for field in ["functional", "total"] do
      if let .ok value := entry.getObjVal? field then
        if !value.getBool?.isOk then throw s!"{field} must be a Boolean"

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
      if pythonReserved.contains name then
        throw s!"DuplicateDeclaration: Schema identifier '{name}' is reserved"
  let predicates ← VE.Bridge.fields (← e.vocabulary.getObjVal? "predicates")
  let mut v : Validated := { envelope := e, decodable := environment }
  if e.profiles.contains "norms@0" &&
      predicates.any (fun (_, entry) => (entry.getObjVal? "regulated").isOk) then
    -- Check the regulated extension, then strip it: the family decoders see
    -- regulated predicates as ordinary ones.
    checkRegulated predicates
    v ← stripPredicates v.envelope v.decodable ["regulated"]
  checkDataFlagFields e.profiles predicates
  if typing && e.family == .closureNary then
    v ← stripPredicates v.envelope v.decodable ["defined", "functional", "total"]
  else if e.family == .closureNary && VE.Core.Layers.usesLayers v.decodable then
    -- The core decoder has neither layer: they are validated over the FOL
    -- projection by the FOL route's decoders, as the core route does. An n-ary
    -- defined predicate is outside the projection, so nothing here would check
    -- its body or compute its table.
    if !(naryDefined v.decodable).isEmpty then
      checkNaryDefinitions v.decodable
    let _ ← VE.Core.Layers.decodeLayers e.profiles v.decodable
    let layered := v.decodable
    v ← stripPredicates v.envelope v.decodable VE.Core.Layers.layerFields
    v := { v with layers := some layered }
  validateFamily v.envelope v.decodable
  pure v

def validatedEnvironment (environment : Json) : Except String VE.Route.Gate.Envelope :=
  (·.envelope) <$> validated environment

/-- The public environment endpoint follows the composed profile head. Each
statement layer validates its own declarations; the core decoder handles the
remaining families. `todayGate` is the single gate for the full registry. -/
def validatedComposedEnvironment (environment : Json) : Except String VE.Route.Gate.Envelope := do
  let rawProfiles := (VE.Bridge.strings (environment.getObjValD "profiles")).toOption.getD []
  if rawProfiles.contains "norm-defaults@0" && !rawProfiles.contains "norms@0" then
    let _ ← VE.Compose.todayGate rawProfiles
    pure ()
  let named := (VE.Route.Gate.profilesOf environment).toOption.getD []
  let empty := Json.arr #[]
  if named.contains "risk@0" || (environment.getObjVal? "risk").isOk then
    let _ ← VE.Risk.Wire.decodeRiskSource environment
      (Json.mkObj [("norms", empty), ("units", empty)])
    pure ()
  else if named.contains "alternatives@0" || (environment.getObjVal? "alternatives").isOk then
    let _ ← VE.Alternatives.Wire.decodeAltSource environment empty empty .environment
    pure ()
  else if named.contains "speech-acts@0" || (environment.getObjVal? "speech_acts").isOk then
    let _ ← VE.SpeechActs.Wire.decodeSpeechEnvironmentFull environment
    pure ()
  else if named.contains "reports@0" then
    let _ ← VE.Reports.Wire.decodeEnvironment environment
    pure ()
  else if (environment.getObjVal? "unit_schema").isOk || (environment.getObjVal? "units").isOk then
    let _ ← VE.Time.Wire.decodeEnvironment environment
    pure ()
  else if named.contains "readings@1" then
    let _ ← VE.Readings.Wire.decodeEnvironment environment
    pure ()
  else if named.contains "rights@0" then
    let frame ← if named.contains "norm-defaults@0" then
      VE.NormDefaults.Wire.placeholderJson environment else pure environment
    let _ ← VE.Rights.Wire.decodeRightsEnvironment frame
    pure ()
  else if named.contains "soft-norms@0" then
    let frame ← if named.contains "norm-defaults@0" then
      VE.NormDefaults.Wire.placeholderJson environment else pure environment
    match VE.SoftNorms.Phases.checkSource frame empty with
    | .ok _ => pure ()
    | .error f => throw f.message
  else if named.contains "norms@0" &&
      (named.contains "closure@0" || named.contains "nary@0" || named.contains "order@0") then
    let frame ← if named.contains "norm-defaults@0" then
      VE.NormDefaults.Wire.placeholderJson environment else pure environment
    let _ ← validated frame
    pure ()
  else if named.contains "norms@0" then
    let predicates ← VE.Bridge.fields (← (← environment.getObjVal? "vocabulary").getObjVal? "predicates")
    if !named.contains "norm-defaults@0" &&
        predicates.any (fun (_, entry) => (entry.getObjVal? "regulated").isOk) &&
        (VE.NormDefaults.Wire.unspecifiedNames environment).isEmpty then
      checkRegulated predicates
    let _ ← VE.NormDefaults.Wire.decodeEnvironmentU environment
    pure ()
  else
    let _ ← validated environment
    pure ()
  let ps ← VE.Route.Gate.profilesOf environment
  if ps.contains "readings@1" then
    let _ ← VE.Compose.dispatch ps
    pure ()
  else VE.Compose.todayGate ps
  let family := if ps.contains "order@0" then VE.Route.Gate.Family.order
    else if ps.contains "nary@0" then .closureNary
    else if ps.contains "closure@0" then .closure else .fol
  pure ⟨ps, family, ← environment.getObjVal? "vocabulary"⟩

/-- A model's tables use the checker vocabulary, including profile words, but
its identity stays bound to the complete submitted environment. The owning
profile decoders validate the source before these projections are used. -/
def modelEnvironment (environment : Json) : Except String Json := do
  let ps ← VE.Route.Gate.profilesOf environment
  let mut view := environment
  if ps.contains "risk@0" then view ← VE.Risk.Wire.riskNormsView view ps
  else if ps.contains "alternatives@0" then view ← VE.Alternatives.Wire.normsView view ps
  if (view.getObjVal? "unit_schema").isOk then view ← VE.Time.Wire.eraseEnvironment view
  if ps.contains "readings@1" then view ← VE.Readings.Wire.stripReadings view
  if ps.contains "norm-defaults@0" then view ← VE.NormDefaults.Wire.placeholderJson view
  typingReduced view

def identityEnvironment (environment : Json) (profiles : List String) : Except String Json :=
  if profiles.contains "speech-acts@0" then
    VE.SpeechActs.Wire.canonicalEnvironmentJson environment
  else pure environment

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

/-- A malformed language value with a frozen-family `profiles` envelope is
decoded against the legacy field shape before any profile extension route. -/
private def frozenFamilyProfiles (environment : Json) : Bool :=
  let profiles := (VE.Bridge.strings (environment.getObjValD "profiles")).toOption.getD []
  !profiles.isEmpty && profiles.all
    (["relational-fol@0", "closure@0", "nary@0", "order@0"].contains)

def decodeLegacy (environment : Json) : Except String Legacy := do
  let language ← VE.Bridge.stringField environment "language"
  if language == "ve.core@0" then
    match VE.Bridge.decodeEnvironment environment with
    | .ok v => pure (.v0 v)
    | .error message => throw message
  else if language == "ve.core@0.1" then
    if environment.getObjValD "profiles" == toJson ["order@0", "relational-fol@0"] then
      match VE.Order.Wire.decodeEnvironment environment with
      | .ok v => pure (.order v)
      | .error message =>
        if message == "unsupported order environment version/profiles" then
          throw s!"UnsupportedProfile: {message}"
        else throw message
    else if (VE.Route.Gate.profilesOf environment).toOption.getD [] |>.contains "order@0" then
      throw "UnsupportedProfile: unsupported order environment version/profiles"
    else pure (.closure (← VE.Closure.Bridge.decodeEnvironment environment))
  else do
    VE.Bridge.exactFields environment ["language", "profile", "spec_revision", "vocabulary"]
    throw "UnsupportedProfile: Unsupported language"

def legacyEnvironmentId (l : Legacy) (environment : Json) : Except String String :=
  VE.CertificateWire.digest s!"ve-environment-{l.version}\n" environment

def legacyMeaningId (l : Legacy) (envId : String) (ast : Json) : Except String String :=
  VE.CertificateWire.digest s!"ve-meaning-{l.version}\n"
    (Json.mkObj [("environment_id", .str envId), ("ast", ast)])

def environmentCase (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let environment ← j.getObjVal? "environment"
  if isLegacy environment ||
      (environment.getObjValD "language" != .str "ve.core@0.2" &&
        ((environment.getObjVal? "profile").isOk || frozenFamilyProfiles environment)) then
    let l ← decodeLegacy environment
    let envId ← legacyEnvironmentId l environment
    -- v0 names its one profile in `profile`; ve.core@0.1 lists `profiles`.
    return VE.Route.Wire.ok id ([("environment_id", .str envId)] ++
      (match l with
       | .v0 _ => [("profile", environment.getObjValD "profile")]
       | _ => [("profiles", environment.getObjValD "profiles")]) ++ [("family", .str l.family)])
  let e ← validatedComposedEnvironment environment
  let environmentId ← environmentIdOf e.profiles (← identityEnvironment environment e.profiles)
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

private def modelError (message : String) : String :=
  if message.startsWith "ResourceLimit:" || message.startsWith "InvalidModel" then message
  else s!"InvalidModel: {message}"

private def longModelAtom : Json → Bool
  | .str value => value.utf8ByteSize > 64
  | _ => false

private def longModelString (model : Json) : Bool :=
  let domains := (VE.Bridge.fields (model.getObjValD "domains")).toOption.getD []
  let constants := (VE.Bridge.fields (model.getObjValD "constants")).toOption.getD []
  let relations := (VE.Bridge.fields (model.getObjValD "relations")).toOption.getD []
  domains.any (fun (_, values) =>
      (values.getArr?.toOption.getD #[]).toList.any longModelAtom) ||
    constants.any (fun (_, value) => longModelAtom value) ||
    relations.any (fun (_, tuples) =>
      (tuples.getArr?.toOption.getD #[]).toList.any (fun row =>
        (row.getArr?.toOption.getD #[]).toList.any longModelAtom))

def legacyModelCase (id : String) (environment model : Json) (j : Json) : Except String Json := do
  let l ← decodeLegacy environment
  let decoded : Except String Unit := do match l with
  | .v0 v | .closure v =>
    let _ ← VE.Bridge.decodeModel v model
    pure ()
  | .order v =>
    let _ ← VE.Order.Wire.decodeValidModel v model
    pure ()
  match decoded with
  | .ok () => pure ()
  | .error message =>
    if message == "invalid local identifier" && longModelString model then
      throw "ResourceLimit: local ID exceeds 64 ASCII bytes"
    throw (modelError message)
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
  let _ ← validatedComposedEnvironment environment
  unless model.getObj?.isOk do
    throw "InvalidModel: object expected"
  let modelEnv ← modelEnvironment environment
  let checked ← validated modelEnv
  let e := checked.envelope
  match e.family with
  | .closureNary =>
    let v ← VE.Core.Bridge.decodeEnvironment checked.decodable
    match checked.layers with
    | none =>
      let _ ← (VE.Core.Wire.decodeModel v model).mapError modelError
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
      let derived := naryDefined layered
      if relations.any (fun (p, _) => derived.contains p) then
        throw "InvalidModel: supplied table for a defined predicate"
      let core ← VE.Core.Layers.withPredicates checked.decodable
        ((VE.Core.Layers.predicatesOf checked.decodable).filter (fun (p, _) => !derived.contains p))
      let modelVocabulary ← if derived.isEmpty then pure v else VE.Core.Bridge.decodeEnvironment core
      let _ ← (VE.Core.Wire.decodeModel modelVocabulary
        (model.setObjVal! "relations" (Json.mkObj (relations ++ tables)))).mapError modelError
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
  let predicates ← VE.Bridge.fields (← (← modelEnv.getObjVal? "vocabulary").getObjVal? "predicates")
  if predicates.any (fun (_, entry) => (entry.getObjVal? "regulated").isOk) then
    VE.Norms.Plain.profileOk ⟨← VE.Norms.Plain.decodeRegulatedAll predicates, [], []⟩ model
  let originalProfiles ← VE.Route.Gate.profilesOf environment
  let environmentId ← environmentIdOf originalProfiles
    (← identityEnvironment environment originalProfiles)
  let modelId ← VE.CertificateWire.digest
    s!"ve-model-{VE.Route.Wire.identityVersion originalProfiles}\n"
    (Json.mkObj [("environment_id", .str environmentId),
      ("model", ← normalizedModel modelEnv model)])
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
  -- W6: either extension field selects the quantity decoder, which owns typing, erasure and
  -- the three identities (Lean-first batch 9).
  if (environment.getObjVal? "unit_schema").isOk || (environment.getObjVal? "units").isOk then
    let w ← VE.Time.Wire.decodeEnvironment environment
    let a ← VE.Time.Wire.decodeQuantity w (← j.getObjVal? "quantity")
    return VE.Route.Wire.ok id [("well_typed", .bool true),
      ("meaning_id", .str a.meaningId), ("Q", a.Q), ("core", a.core),
      ("environment_id", .str w.environmentId),
      ("target_environment_id", .str w.targetId)]
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
        pure (fs.map VE.Order.Surface.formulaJson, some (VE.Order.Surface.print fs))
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
      pure (fs.map VE.Order.Surface.formulaJson, some (VE.Order.Surface.print fs))
  VE.Route.AstLimit.check asts
  pure (VE.Route.Wire.ok id ([("ast", Json.arr asts.toArray)] ++
    match canonical with
    | some text => [("canonical", .str text)]
    | none => []))

/-! Model diagnostics are emitted by a pointer-carrying decoder. The model
tables are validated here in the frozen Python order; the family decoder still
constructs and checks the typed model after these checks succeed. A fault is
located when it is discovered, never reconstructed from its message. -/
structure ModelFault where
  message : String
  path : String

private def modelFault (path message : String) : Except ModelFault α :=
  .error ⟨message, path⟩

private def tableFields (value : Json) (expected : List String) (path : String) :
    Except ModelFault Unit := do
  match VE.Bridge.exactFieldsQuoted value expected with
  | .ok () => pure ()
  | .error message => modelFault path s!"InvalidModel: {message}"

private def modelAtom (value : Json) (path : String) : Except ModelFault String := do
  let .str word := value | modelFault path "InvalidModel: local ID must match [a-z][a-z0-9_]*"
  unless VE.Surface.identifier word do
    modelFault path "InvalidModel: local ID must match [a-z][a-z0-9_]*"
  if word.utf8ByteSize > 64 then modelFault path "ResourceLimit: local ID exceeds 64 ASCII bytes"
  pure word

private def modelCell (order : Bool) (sort : String) (value : Json) (path : String) :
    Except ModelFault String := do
  if order && sort == "$int" then
    let .str word := value |
      modelFault path "InvalidModel: integer values must be canonical decimal strings"
    match VE.Order.Wire.decodeInt word with
    | .ok _ => pure word
    | .error message =>
      if message.startsWith "ResourceLimit:" then modelFault path message
      else modelFault path "InvalidModel: integer values must be canonical decimal strings"
  else modelAtom value path

private def environmentFields (value : Json) (expected : List String) (path : String) :
    Except ModelFault Unit := do
  match VE.Bridge.exactFieldsQuoted value expected with
  | .ok () => pure ()
  | .error message => modelFault path message

/-- Location-aware vocabulary shape decoding shared by the public environment
and model endpoints. The family decoder performs all remaining semantic checks. -/
private def locatedEnvironmentFields (environment : Json) : Except ModelFault Unit := do
  let .ok vocabulary := environment.getObjVal? "vocabulary" |
    modelFault "" "object expected"
  unless vocabulary.getObj?.isOk do modelFault "" "object expected"
  let profiles := (VE.Bridge.strings (environment.getObjValD "profiles")).toOption.getD []
  let reports := profiles.contains "reports@0"
  -- Statement-layer blocks live beside the base vocabulary. Their owning
  -- decoders validate the blocks; this decoder locates faults in base fields.
  let extensions := [("reports@0", "reports"), ("soft-norms@0", "soft"),
    ("rights@0", "rights")]
  let present := extensions.filterMap fun (profile, field) =>
    if profiles.contains profile && (vocabulary.getObjVal? field).isOk then some field else none
  environmentFields vocabulary (["sorts", "predicates", "constants"] ++ present) "/vocabulary"
  let sorts := vocabulary.getObjValD "sorts"
  let predicates := vocabulary.getObjValD "predicates"
  let constants := vocabulary.getObjValD "constants"
  let .ok sortEntries := VE.Bridge.fields sorts | modelFault "" "sorts must be an object"
  let .ok predicateEntries := VE.Bridge.fields predicates |
    modelFault "" "predicates must be an object"
  let .ok constantEntries := VE.Bridge.fields constants |
    modelFault "" "constants must be an object"
  if sortEntries.length > 32 || predicateEntries.length > 256 then
    modelFault "" "ResourceLimit: Vocabulary exceeds sort or predicate limit"
  match VE.Bridge.checkVocabularyNames sortEntries predicateEntries constantEntries with
  | .ok () => pure ()
  | .error message => modelFault "" message
  let sortNames := sortEntries.map Prod.fst
  let order := profiles.contains "order@0"
  let flagged := profiles.contains "data@0"
  let nary := profiles.contains "nary@0"
  if reports && (vocabulary.getObjVal? "reports").isOk then
    environmentFields (vocabulary.getObjValD "reports") ["holders", "evidence"]
      "/vocabulary/reports"
  for (name, entry) in sortEntries do
    let path := s!"/vocabulary/sorts/{name}"
    let optional := if (entry.getObjVal? "verbalisation").isOk then ["verbalisation"] else []
    environmentFields entry (["description"] ++ optional) path
    if let .ok words := entry.getObjVal? "verbalisation" then
      environmentFields words ["singular", "plural"] s!"{path}/verbalisation"
      for field in ["singular", "plural"] do
        match VE.Bridge.displayString (words.getObjValD field) with
        | .ok () => pure ()
        | .error message => modelFault "" message
    match VE.Bridge.description entry with
    | .ok () => pure ()
    | .error message => modelFault "" message
  for (name, entry) in predicateEntries do
    let path := s!"/vocabulary/predicates/{name}"
    let optional := ["defined", "functional", "total", "regulated", "argument_units",
      "instruction_of", "verbalisation", "negative_verbalisation"]
    let present := optional.filter (fun key => (entry.getObjVal? key).isOk)
    environmentFields entry (["arguments", "description"] ++ present) path
    let arguments := entry.getObjValD "arguments"
    let maximum := if nary then 6 else 2
    let .arr cells := arguments |
      modelFault "" s!"Predicate arguments must be an array of one to {maximum} sort identifiers"
    unless cells.size ≥ 1 && cells.size ≤ maximum do
      modelFault "" s!"Predicate arguments must be an array of one to {maximum} sort identifiers"
    -- The family decoder owns the reserved built-in sort's signature
    -- diagnostic ("invalid signature" in stage one). Ordinary unknown
    -- names use the shared quoted-name validator.
    if !((!flagged && cells.contains (.str "$string")) ||
        (!order && cells.contains (.str "$int"))) then
      match VE.Bridge.argumentSorts arguments (fun sort =>
          sortNames.contains sort || (order && sort == "$int") ||
          (flagged && sort == "$string")) with
      | .ok _ => pure ()
      | .error message => modelFault "" message
    if let .ok defined := entry.getObjVal? "defined" then
      environmentFields defined ["arguments", "body"] s!"{path}/defined"
    match VE.Bridge.description entry with
    | .ok () => pure ()
    | .error message => modelFault "" message
  for (name, entry) in constantEntries do
    let path := s!"/vocabulary/constants/{name}"
    let literal := entry.getObjValD "sort" == .str "$string"
    let description := if !literal || (entry.getObjVal? "description").isOk then ["description"] else []
    let optional := ["unit", "verbalisation"].filter (fun key => (entry.getObjVal? key).isOk)
    environmentFields entry (["sort"] ++ description ++ optional) path
    match VE.Bridge.constantSort entry (fun sort =>
        sortNames.contains sort || (order && sort == "$int") || sort == "$string") with
    | .ok _ => pure ()
    | .error message => modelFault "" message

private def locatedModelTables (environment model : Json) : Except ModelFault Unit := do
  let .ok vocabulary := environment.getObjVal? "vocabulary" |
    modelFault "/environment/vocabulary" "InvalidInput: missing vocabulary"
  let .ok sorts := VE.Bridge.fields (vocabulary.getObjValD "sorts") |
    modelFault "/environment/vocabulary/sorts" "InvalidInput: object expected"
  let .ok predicates := VE.Bridge.fields (vocabulary.getObjValD "predicates") |
    modelFault "/environment/vocabulary/predicates" "InvalidInput: object expected"
  let .ok constants := VE.Bridge.fields (vocabulary.getObjValD "constants") |
    modelFault "/environment/vocabulary/constants" "InvalidInput: object expected"
  -- A declared literal (or a stage-two string argument) adds the built-in
  -- model domain, exactly as RouteVocabulary.modelVocabulary does.
  let hasStrings := constants.any (fun (_, entry) =>
    entry.getObjValD "sort" == .str "$string") ||
    predicates.any (fun (_, entry) =>
      (VE.Bridge.strings (entry.getObjValD "arguments")).toOption.getD [] |>.contains "$string")
  let sortNames := sorts.map Prod.fst ++ (if hasStrings then ["$string"] else [])
  let predicateNames := (predicates.filter (fun (_, entry) =>
    !(entry.getObjVal? "defined").isOk)).map Prod.fst
  let constantNames := constants.map Prod.fst
  tableFields model ["complete", "domains", "constants", "relations"] ""
  unless model.getObjValD "complete" == .bool true do
    modelFault "/complete" "InvalidModel: complete must be the Boolean true"
  let domains := model.getObjValD "domains"
  let values := model.getObjValD "constants"
  let relations := model.getObjValD "relations"
  for (name, table) in [("domains", domains), ("constants", values), ("relations", relations)] do
    unless table.getObj?.isOk do modelFault s!"/{name}" "InvalidModel: expected an object"
  tableFields domains sortNames "/domains"
  tableFields values constantNames "/constants"
  let .ok relationFields := VE.Bridge.fields relations |
    modelFault "/relations" "InvalidModel: expected an object"
  -- A supplied definition table is rejected by the definitions layer, whose
  -- semantic diagnostic is rooted at the model rather than a JSON cell.
  if relationFields.any (fun (name, _) =>
      (predicates.any fun (p, entry) => p == name && (entry.getObjVal? "defined").isOk)) then
    return ()
  tableFields relations predicateNames "/relations"
  -- Static limits precede cell decoding in all families.
  for sort in sortNames do
    if let .arr cells := domains.getObjValD sort then
      if cells.size > 1000 then modelFault s!"/domains/{sort}" "ResourceLimit: domain exceeds entity limit"
  let total := relationFields.foldl (fun count (_, rows) =>
    match rows with | .arr cells => count + cells.size | _ => count) 0
  if total > 100000 then modelFault "/relations" "ResourceLimit: model exceeds total relation tuple limit"
  let mut decodedDomains : List (String × List String) := []
  for sort in sortNames do
    let .arr cells := domains.getObjValD sort |
      modelFault s!"/domains/{sort}" "InvalidModel: domain must be an array"
    let mut decoded : List String := []
    for (cell, index) in cells.toList.zipIdx do
      decoded := (← modelAtom cell s!"/domains/{sort}/{index}") :: decoded
    unless VE.Route.Decode.distinct decoded do
      modelFault s!"/domains/{sort}" "InvalidModel: duplicate domain entity"
    decodedDomains := (sort, decoded) :: decodedDomains
  let order := (environment.getObjValD "profiles" |>.getArr?.toOption.getD #[]).contains (.str "order@0")
  for (name, entry) in constants do
    let sort := (entry.getObjValD "sort").getStr?.toOption.getD ""
    let path := s!"/constants/{name}"
    let word ← modelCell order sort (values.getObjValD name) path
    if !(order && sort == "$int") && !((VE.Bridge.lookup decodedDomains sort).getD []).contains word then
      modelFault path "InvalidModel: constant denotes an entity outside its sort"
  for (name, entry) in predicates do
    if !predicateNames.contains name then continue
    let path := s!"/relations/{name}"
    let .arr rows := relations.getObjValD name |
      modelFault path "InvalidModel: relation must be an array"
    let signature := (VE.Bridge.strings (entry.getObjValD "arguments")).toOption.getD []
    let mut decodedRows : List (List String) := []
    for (row, index) in rows.toList.zipIdx do
      let rowPath := s!"{path}/{index}"
      let .arr cells := row | modelFault rowPath "InvalidModel: relation tuple has wrong arity"
      unless cells.size == signature.length do
        modelFault rowPath "InvalidModel: relation tuple has wrong arity"
      -- Decode every cell before checking membership. The frozen decoder
      -- reports a malformed later cell before a dangling earlier entity.
      let decoded ← (signature.zip cells.toList).zipIdx.mapM fun ((sort, cell), cellIndex) =>
        let cellPath := s!"{rowPath}/{cellIndex}"
        modelCell order sort cell cellPath
      for ((sort, word), cellIndex) in (signature.zip decoded).zipIdx do
        let cellPath := s!"{rowPath}/{cellIndex}"
        if !(order && sort == "$int") && !((VE.Bridge.lookup decodedDomains sort).getD []).contains word then
          modelFault cellPath "InvalidModel: relation tuple contains a dangling or wrong-sort entity"
      decodedRows := decoded :: decodedRows
    unless VE.Route.Decode.distinct decodedRows do
      modelFault path "InvalidModel: duplicate relation tuple"

/-- The public table decoder returns the location found by the validator.
Neither its message nor its path is rewritten after the failure. -/
def checkedModelTables (environment model : Json) : Except ModelFault Unit :=
  locatedModelTables environment model

theorem checkedModelTables_error_preserved (environment model : Json)
    (fault : ModelFault) (h : locatedModelTables environment model = .error fault) :
    checkedModelTables environment model = .error fault := h

/-- Checked examples of the pointer-carrying decoder, including faults in a
table shape and a nested cell. The `ModelFault` type makes path mandatory. -/
private def modelPathOf (result : Except ModelFault Unit) : String :=
  match result with | .ok _ => "" | .error fault => fault.path

#guard modelPathOf (checkedModelTables
  (Json.mkObj [("vocabulary", Json.mkObj [("sorts", Json.mkObj [("item", .null)]),
    ("predicates", Json.mkObj []), ("constants", Json.mkObj [])])])
  (Json.mkObj [("complete", .bool true), ("domains", Json.mkObj [("item", .str "i")]),
    ("constants", Json.mkObj []), ("relations", Json.mkObj [])])) == "/domains/item"

def reported (run : Json → Except String Json) (j : Json) : Json :=
  match run j with
  | .ok result => result
  | .error message => Json.mkObj [("id", j.getObjValD "id"),
      ("status", .str "error"), ("error", .str message)]

def reportedFault (j : Json) (fault : ModelFault) : Json :=
  Json.mkObj ([("id", j.getObjValD "id"), ("status", .str "error"),
    ("error", .str fault.message)] ++
    if fault.path.isEmpty then [] else [("path", .str fault.path)])

/-- Keep the owning family's diagnostic text while carrying the location found
by the shared vocabulary shape decoder. Only a reported rejection gets a path. -/
def withVocabularyPath (j result : Json) (fault : ModelFault) : Json :=
  match result.getObjVal? "error" with
  | .ok (.str message) =>
    if fault.path.isEmpty then result else reportedFault j ⟨message, fault.path⟩
  | _ => result

/-- Profile shape precedes vocabulary decoding. The base route owns its profile
combination; statement and wrapper routes keep their owning decoder's fault
precedence. -/
private def earlyProfileGate (environment : Json) : Except String Unit := do
  if environment.getObjValD "language" == .str "ve.core@0.2" then
    if (environment.getObjVal? "profiles").isOk then
      let profiles ← VE.Route.Gate.profilesOf environment
      if VE.Compose.todayHead profiles == .frozen &&
          !(profiles.any VE.Compose.wrapperProfiles.contains) &&
          !profiles.contains "time@0" then
        VE.Compose.todayGate profiles

/-- Only the four frozen checker families have their entire vocabulary shape
owned by the location decoder. Composed routes inspect their own envelope and
must retain that route's diagnostic precedence. -/
private def locationOwnedEnvironment (environment : Json) : Bool :=
  environment.getObjValD "language" == .str "ve.core@0.2" &&
    frozenFamilyProfiles environment

/-- Check the frozen outer envelope with its owning decoder while ignoring
vocabulary contents. This preserves outer-field, profile and revision order. -/
private def legacyHeaderAccepted (environment : Json) : Bool :=
  let emptyVocabulary := Json.mkObj [("sorts", Json.mkObj []),
    ("predicates", Json.mkObj []), ("constants", Json.mkObj [])]
  (decodeLegacy (environment.setObjVal! "vocabulary" emptyVocabulary)).isOk

/-- A legacy vocabulary path is meaningful only after its outer envelope
passes the frozen decoder. -/
def reportedLegacyEnvironment (j environment : Json) : Json :=
  let result := reported environmentCase j
  if !legacyHeaderAccepted environment then result
  else
    match locatedEnvironmentFields environment with
    | .error fault =>
      if fault.message.startsWith "UnknownSymbol: Undeclared predicate argument sort:" then
        reportedFault j fault
      else withVocabularyPath j result fault
    | .ok () => result

def reportedOtherEnvironment (j environment : Json) : Json :=
  if !isLegacy environment then reported environmentCase j
  else reportedLegacyEnvironment j environment

def reportedEnvironment (j : Json) : Json :=
  match j.getObjVal? "environment" with
  | .error _ => reported environmentCase j
  | .ok environment =>
    if !locationOwnedEnvironment environment then
      -- Composed families own their envelope and field precedence. For a
      -- valid profile gate, the path-carrying vocabulary decoder supplies
      -- the shared unknown-argument diagnostic before the family decoder.
      if environment.getObjValD "language" == .str "ve.core@0.2" &&
          (earlyProfileGate environment).isOk then
        match locatedEnvironmentFields environment with
        | .error fault =>
          if fault.message.startsWith "UnknownSymbol: Undeclared predicate argument sort:" then
            reportedFault j fault
          else withVocabularyPath j (reported environmentCase j) fault
        | .ok () => reported environmentCase j
      else reportedOtherEnvironment j environment
    else
      match earlyProfileGate environment with
      | .error message => reportedFault j ⟨message, ""⟩
      | .ok () =>
        match locatedEnvironmentFields environment with
        | .ok () => reported environmentCase j
        | .error fault => reportedFault j fault

def reportedModel (j : Json) : Json :=
  let checkedEnvironment := reportedEnvironment j
  if checkedEnvironment.getObjValD "status" == .str "error" then
    reportedFault j ⟨(checkedEnvironment.getObjValD "error").getStr?.toOption.getD "",
      (checkedEnvironment.getObjValD "path").getStr?.toOption.getD ""⟩
  else
    let located := do
      let environment ← j.getObjVal? "environment"
      let model ← j.getObjVal? "model"
      if !isLegacy environment then
        let _ ← validatedComposedEnvironment environment
        pure ()
      let view ← if isLegacy environment then pure environment else modelEnvironment environment
      pure (environment, model, view)
    match located with
    | .ok (_, model, view) =>
      match checkedModelTables view model with
      | .ok () => reported modelCase j
      | .error fault => reportedFault j fault
    | .error _ =>
      match j.getObjVal? "environment" with
      | .error _ => reported modelCase j
      | .ok environment =>
        match earlyProfileGate environment with
        | .error message => reportedFault j ⟨message, ""⟩
        | .ok () =>
          if !locationOwnedEnvironment environment then reported modelCase j
          else
            match locatedEnvironmentFields environment with
            | .ok () => reported modelCase j
            | .error fault => reportedFault j fault

/-- A raw strict parse may succeed while the family's typing check rejects.
In that case the existing diagnostic walker names the first typing fault. -/
def rawParseAst (environment : Json) (source : String) : Option (List Json) := Id.run do
  let chars := source.toList
  let fuel := chars.length + 1
  if isLegacy environment then
    let .ok l := decodeLegacy environment | return none
    return match l with
      | .v0 v => (VE.Surface.parseStatements v.environment fuel chars).map
          (·.map VE.Route.Wire.encodeFormula)
      | .closure v => (VE.Closure.Surface.parseStatements v.environment fuel chars).map
          (·.map encodeClosure)
      | .order v => (VE.Order.Surface.parseStatements v.environment fuel chars).map
          (·.map VE.Order.Surface.formulaJson)
  let .ok checked := validated environment | return none
  let e := checked.envelope
  return match e.family with
    | .fol => do
      let rv ← (VE.Route.Run.decodeRouteVocabulary e).toOption
      (VE.Surface.parseStatements rv.environment fuel chars).map (·.map VE.Route.Wire.encodeFormula)
    | .closure => do
      let rv ← (VE.Route.Run.decodeRouteVocabulary e).toOption
      (VE.Closure.Surface.parseStatements rv.environment fuel chars).map (·.map encodeClosure)
    | .closureNary => do
      let v ← (VE.Core.Bridge.decodeEnvironment checked.decodable).toOption
      (VE.Core.Surface.parseStatements v.environment fuel chars).map (·.map encodeCore)
    | .order => do
      let v ← (VE.Route.Wire.decodeOrderVocabulary e.vocabulary).toOption
      (VE.Order.Surface.parseStatements v.vocabulary.environment fuel chars).map
        (·.map VE.Order.Surface.formulaJson)

/-- A diagnostic and span for a source the checked family parser rejected. -/
def parseRejection (j : Json) (message : String) : Option (String × String × ParseDiagnostic.Error) := do
  guard (message == "SyntaxError: the source is not accepted by the Lean surface parser" ||
      message == "ResourceLimit: source identifier exceeds 64 bytes" ||
      message == "ResourceLimit: formula depth exceeds 64" ||
      message == "ResourceLimit: AST node count")
  let source ← (j.getObjValAs? String "source").toOption
  let environment ← (j.getObjVal? "environment").toOption
  let vocabulary ← (environment.getObjVal? "vocabulary").toOption
  let profiles := match (environment.getObjVal? "profiles").toOption with
    | some value => (VE.Bridge.strings value).toOption.getD []
    | none => [(environment.getObjValAs? String "profile").toOption.getD ""]
  let signature ← (TypingDiagnostic.decodeSignature profiles vocabulary).toOption
  let diagnostic := match source.toList.findIdx? (fun c => c.toNat > 127) with
    | some pos => some (⟨"SyntaxError", "VE semantic syntax must be ASCII", pos, pos + 1⟩ : ParseDiagnostic.Error)
    | none => ParseDiagnostic.scan signature source (profiles.contains "order@0")
        (profiles.contains "closure@0") (profiles.contains "nary@0")
  if let some error := diagnostic then
    return (error.code ++ ": " ++ error.message, source, error)
  let asts ← rawParseAst environment source
  let text ← TypingDiagnostic.diagnose profiles vocabulary asts
  let entire : ParseDiagnostic.Error := ⟨"", "", 0, source.length⟩
  return (text, source, entire)

/-- Accepted AST and canonical text come from `parseCase`; rejected syntax
gets the Lean diagnostic with its source span. -/
def reportedParse (j : Json) : Json :=
  match parseCase j with
  | .ok result => result
  | .error message =>
    match parseRejection j message with
    | some (text, source, diagnostic) => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"),
        ("error", .str text), ("span", ParseDiagnostic.span source diagnostic)]
    | none => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"),
        ("error", .str message)]

end VE.Service.Standalone
