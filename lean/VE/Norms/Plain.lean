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
  kind == "background" || kind == "evaluate" || kind == "countermodel" || kind == "certificate"

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

/-- The FOL route's certificate branch over `background`, bound to the
submitted `environment`; acceptance is `VE.Tableau.checkCertificate` over
`background ++ premises` (`VE.Tableau.checkCertificate_sound`). -/
def folCertificate (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary)
    (background : List VE.Formula) (id : String) (j : Json) : Except String Json := do
  let E := rv.environment
  let data := profiles.contains "data@0"
  let premisesJson ← j.getObjVal? "premises"
  let _ ← VE.Route.Wire.formulasJson premisesJson (some (← j.getObjVal? "conclusion"))
  let ps ← VE.Route.Wire.decodeFormulas E premisesJson data
  let c ← VE.Route.Wire.decodeClosed E (← j.getObjVal? "conclusion") data
  VE.Route.Wire.nodeLimit ((c :: ps).map VE.Bridge.formulaNodes)
  let certificate ← VE.CertificateWire.decodeCertificate (← j.getObjVal? "certificate")
  VE.Route.Wire.bindingOk profiles environment
    (background.map VE.Route.Wire.encodeFormula ++ (← premisesJson.getArr?).toList)
    (← j.getObjVal? "conclusion") certificate.environment_id certificate.premise_meaning_ids
    certificate.conclusion_meaning_id
  if VE.Route.Steps.fol certificate.trace > VE.Route.Steps.limit j then throw VE.Route.Steps.stepLimit
  return VE.Route.Wire.ok id [("valid", .bool (VE.Tableau.checkCertificate E (background ++ ps) c certificate)),
    ("background", toJson background.length)]

/-- The closure route's certificate branch over `background` (embedded), bound
to the submitted `environment` (`VE.Closure.Tableau.checkCertificate_sound`). -/
def closureCertificate (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary)
    (background : List VE.Formula) (id : String) (j : Json) : Except String Json := do
  let E := rv.environment
  let data := profiles.contains "data@0"
  let premisesJson ← j.getObjVal? "premises"
  let _ ← VE.Route.Wire.formulasJson premisesJson (some (← j.getObjVal? "conclusion"))
  let ps ← VE.Closure.Bridge.decodeFormulas E premisesJson
  if data && ps.any VE.Route.Wire.closureUsesStringBinder then
    throw "$string quantification requires data stage 2"
  let c ← VE.Closure.Bridge.decodeFormula 64 (← j.getObjVal? "conclusion")
  if data && VE.Route.Wire.closureUsesStringBinder c then
    throw "$string quantification requires data stage 2"
  unless c.check E [] do throw "ill-typed or unbound conclusion"
  VE.Route.Wire.nodeLimit ((c :: ps).map VE.Closure.Bridge.formulaNodes)
  let certificate ← VE.CertificateWire.decodeClosureCertificate (← j.getObjVal? "certificate")
  VE.Route.Wire.bindingOk profiles environment
    (background.map VE.Route.Wire.encodeFormula ++ (← premisesJson.getArr?).toList)
    (← j.getObjVal? "conclusion") certificate.environment_id certificate.premise_meaning_ids
    certificate.conclusion_meaning_id
  if VE.Route.Steps.closure certificate.trace > VE.Route.Steps.limit j then
    throw VE.Route.Steps.stepLimit
  return VE.Route.Wire.ok id [("valid", .bool (VE.Closure.Tableau.checkCertificate E
      (background.map VE.Closure.embed ++ ps) c certificate)), ("background", toJson background.length)]

/-- A certificate case over the environment without the validated extension,
bound to the submitted one: the family's Background, then the profile premises. -/
def certificate (profiles : List String) (environment stripped : Json) (T : Tree)
    (extra : List VE.Formula) (id : String) (j : Json) : Except String Json := do
  let e ← VE.Route.Gate.decodeEnvelope stripped
  let profile := pairPremises T ++ extra
  match e.family with
  | .fol =>
    let rv ← VE.Route.Run.decodeRouteVocabulary e
    folCertificate profiles environment rv ((VE.Route.Wire.fullBackground rv).map Prod.fst ++ profile) id j
  | .closure =>
    let rv ← VE.Route.Run.decodeRouteVocabulary e
    closureCertificate profiles environment rv
      ((VE.Route.Wire.fullBackground rv).map Prod.fst ++ profile) id j
  | .closureNary =>
    if VE.Core.Layers.usesLayers stripped then
      let base ← VE.Core.Layers.background e.profiles stripped
      VE.Core.Layers.coreCertificate profiles environment (← VE.Core.Layers.coreEnvironment stripped)
        (base ++ profile) id j
    else
      let v ← VE.Core.Bridge.decodeEnvironment stripped
      VE.Core.Layers.coreCertificate profiles environment stripped
        (VE.Route.Background.literals (VE.Core.Wire.literals v) ++ profile) id j
  | .order =>
    unless profile.isEmpty do
      throw (VE.Route.Gate.unsupported "profile pairs on the order family are deferred")
    VE.Route.Wire.runOrder profiles environment (← VE.Route.Wire.decodeOrderVocabulary e.vocabulary)
      id "certificate" j

/-- Statement-layer profiles whose declarations Plain removes before decoding:
`reports@0` (the reports block, constant verbalisations), `soft-norms@0` (the
soft block, `instruction_of`), `rights@0` (the rights block) and
`speech-acts@0` (the `speech_acts` scope block). None of them declares
vocabulary or constrains a model. Identities keep the submitted environment. -/
def statementLayers : List String := ["reports@0", "soft-norms@0", "rights@0", "speech-acts@0"]

def layered (environment : Json) : Bool :=
  match environment.getObjValD "profiles" with
  | .arr ps => ps.any (fun p => statementLayers.any (p == .str ·))
  | _ => false

def reduced (environment : Json) : Except String Json := do
  let environment := Json.mkObj ((← fields environment).filter (·.1 != "speech_acts"))
  let profiles := (← VE.Route.Gate.profilesOf environment).filter (!statementLayers.contains ·)
  let vocabulary ← environment.getObjVal? "vocabulary"
  let constants ← (← fields (← vocabulary.getObjVal? "constants")).mapM fun (c, entry) => do
    pure (c, Json.mkObj ((← fields entry).filter (·.1 != "verbalisation")))
  let predicates ← (← fields (← vocabulary.getObjVal? "predicates")).mapM fun (p, entry) => do
    pure (p, Json.mkObj ((← fields entry).filter (·.1 != "instruction_of")))
  let rest := (← fields vocabulary).filter (fun kv => kv.1 != "reports" && kv.1 != "soft" && kv.1 != "rights")
  pure ((environment.setObjVal! "profiles" (toJson profiles)).setObjVal! "vocabulary"
    (((Json.mkObj rest).setObjVal! "constants" (Json.mkObj constants)).setObjVal! "predicates"
      (Json.mkObj predicates)))

/-- The premises a validated soft document adds to Background, followed by
those a correlated rights document adds, as the case carries them (a trusted
composition point: they are not environment data; the Lean soft and rights
routes regenerate them). Each is a closed FOL formula. -/
def softPremises (E : VE.Environment) (j : Json) : Except String (List VE.Formula) := do
  match j.getObjVal? "soft_premises" with
  | .error _ => pure []
  | .ok ps => (← ps.getArr?).toList.mapM fun a => do
    let f ← VE.Bridge.decodeFormula 64 a
    unless f.check E [] do throw "ill-typed or unbound soft premise"
    pure f

def run (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let kind ← VE.Route.Run.caseKind j
  let submitted ← j.getObjVal? "environment"
  let profiles ← VE.Route.Gate.profilesOf submitted
  let environment ← if layered submitted then reduced submitted else pure submitted
  let e ← VE.Route.Gate.decodeEnvelope environment
  let predicates ← fields (← e.vocabulary.getObjVal? "predicates")
  let T : Tree := ⟨← decodeRegulatedAll predicates, [], []⟩
  let stripped ← strip environment predicates
  if kind == "certificate" then
    let extra ← if !(j.getObjVal? "soft_premises").isOk then pure []
      else if e.family == .fol then
        softPremises (← VE.Route.Run.decodeRouteVocabulary (← VE.Route.Gate.decodeEnvelope stripped)).environment j
      else throw (VE.Route.Gate.unsupported "soft premises outside the FOL family are deferred")
    return ← certificate profiles submitted stripped T extra id j
  let result ← VE.Route.Run.runCase (j.setObjVal! "environment" stripped)
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
