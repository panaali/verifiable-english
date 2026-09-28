import VE.Discourse.Admission

/-! # The `ve_discourse_route` executable (docs/spec/discourse.md 9.7)

Each case is `{"id", "kind", "environment", "document", ...}`. A case uses the discourse path
when its environment declares `ve.discourse@1`, its kind starts with `discourse-`, or its
document is a `ve-document@2` (or carries a `discourse` block); every other case is delegated
unchanged to the `route` runner (`VE.Route.Run.runCase`), and a discourse input never falls
back after a failed discourse decode. Case kinds:

* `admission`: the `@2` document → `admitted`, `report`, `report_id` (the wrapper identity),
  `inner_report_id`, `document_id`, `kinds`, `references`, `presuppositions`, `pending`,
  `bound`, `validity`, `joint`;
* `discourse-resolve`: per bound unit the elaborated formula and its `meaning_id` or the
  validator's diagnostic; per mention its accessible elaborable targets;
* `discourse-validity`: the admission's validity verdicts;
* `discourse-joint`: the joint set (choices) or its diagnostic, and the joint disjunction. -/
namespace VE.Discourse.Run
open Lean
open VE.Bridge (stringField)

def usesDiscoursePath (j : Json) : Bool :=
  let env := j.getObjValD "environment"
  let profiles := (VE.Route.Gate.profilesOf env).toOption.getD []
  let kind := match j.getObjValD "kind" with
    | .str k => k.startsWith "discourse-"
    | _ => false
  let doc := j.getObjValD "document"
  profiles.contains discourseProfile || kind || formatOf doc == some "ve-document@2" ||
    (doc.getObjVal? "discourse").toBool

def fuelBudget : Nat := 5

/-- The route vocabulary of the base pair. -/
def baseVocabulary (environment : Json) : Except String VE.Route.Wire.RouteVocabulary := do
  let e ← VE.Route.Gate.decodeEnvelope (baseEnvironment environment)
  VE.Route.Run.decodeRouteVocabulary e

def targetJson (t : Target) : Json :=
  Json.mkObj ([("kind", .str (kindText t.kind))] ++
    (match t.name with | some n => [("name", .str n)] | none => []) ++
    (if t.members.isEmpty then [] else [("members", toJson t.members)]) ++
    (match t.pair with | some (a, b) => [("pair", toJson [a, b])] | none => []) ++
    (if t.units.isEmpty then [] else [("units", toJson t.units)]))

def carrierText : Option PresuppositionCarrier → String
  | some (.proved n) => "proved (" ++ n ++ ")"
  | some (.assumed u) => "assumed (" ++ u ++ ")"
  | none => "unresolved"

def encodeAdmission (id : String) (res : Admitted) : Except String Json := do
  let bp := res.doc.K.definitionsVersion
  let bound ← (boundUnits res.doc).eraseDups.filterMapM fun u => match res.bound u with
    | some A => pure (some (u, VE.Route.Wire.encodeFormula A))
    | none => pure none
  pure (VE.Route.Wire.ok id [("admitted", .bool true), ("report", reportJson res.base.report),
    ("report_id", .str res.reportId), ("document_id", .str res.documentId),
    ("definitions_version", .str bp),
    ("kinds", Json.arr res.base.kinds.toArray),
    ("bound", Json.mkObj bound),
    ("presuppositions", Json.mkObj ((presupMentions res.doc).map fun m =>
      (m.id, .str (presuppositionLine m (res.presuppositions m.id))))),
    ("pending", Json.arr (res.pending.map fun (u, d) => Json.arr #[.str u, .str d]).toArray),
    ("validity", Json.mkObj (res.doc.K.validity.map fun v =>
      (v.unit, .str ((res.validity v.unit).map verdictText |>.getD "none")))),
    ("self_truth", toJson res.selfTruth),
    ("statuses", Json.mkObj ((res.base.doc.units.map VE.Route.Admission.DocUnit.id).map fun u => (u, .str (statusOf res u)))),
    ("joint", match res.joint with
      | .ok cs => toJson cs.length
      | .error e => .str e)])

/-- The discourse document prepared for resolution (the part of `admit2` before W2). -/
def prepare (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary) (j : Json) :
    Except String DDoc := do
  wrapperOk profiles environment j
  let bp := baseProfiles profiles
  let prose ← stringField j "prose"
  let K₀ ← Wire.decodeManifest (← j.getObjVal? "discourse")
  let base₀ ← VE.Route.Admission.decodeDoc rv (bp.contains "data@0") j
  let base := { base₀ with literals := rv.literals, flags := rv.flags }
  let src : Wire.Source := ⟨prose, lex prose⟩
  let K ← Wire.toTokenSpans src base K₀
  pure ⟨rv.environment, base, K, Wire.sourceId prose, src.text base⟩

def runResolve (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary) (id : String) (j : Json) :
    Except String Json := do
  let D ← prepare profiles environment rv j
  let bp := baseProfiles profiles
  let envId ← VE.Route.Wire.environmentId bp (baseEnvironment environment)
  let units ← (boundUnits D).eraseDups.mapM fun u => match validate D u with
    | .ok A => do
      let mid ← VE.Route.Wire.meaningId bp envId (VE.Route.Wire.encodeFormula A)
      pure (u, Json.mkObj [("status", .str "resolved"), ("formula", VE.Route.Wire.encodeFormula A),
        ("meaning_id", .str mid)])
    | .error e => pure (u, Json.mkObj [("status", .str "error"), ("error", .str e)])
  let mentions := D.K.mentions.map fun m =>
    let slot : Slot := ⟨m.unit, m.span, m.form⟩
    (m.id, Json.mkObj [("accessible", Json.arr ((accCands D slot).map targetJson).toArray),
      ("recorded", targetJson m.target), ("accessible_recorded", .bool (accB D slot m.target))])
  let wf := match wellFormed D with
    | .ok _ => Json.str "ok"
    | .error e => Json.str e
  pure (VE.Route.Wire.ok id [("units", Json.mkObj units), ("mentions", Json.mkObj mentions),
    ("well_formed", wf), ("environment_id", .str envId),
    ("joint", match compatibleChoices D.K (activeSets D) 64 with
      | .ok cs => toJson cs.length
      | .error e => .str e)])

def runJoint (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary) (id : String) (j : Json) :
    Except String Json := do
  let D ← prepare profiles environment rv j
  let sets := activeSets D
  match compatibleChoices D.K sets 64 with
  | .ok cs => pure (VE.Route.Wire.ok id [("verdict", .str "COMPLETE"),
      ("choices", Json.arr (cs.map fun c => Json.arr (c.map fun (s, v, i) => Json.arr #[.str s, toJson v, toJson i]).toArray).toArray),
      ("joint", match joint sets cs with
        | some J => VE.Route.Wire.encodeFormula J
        | none => .null)])
  | .error e => pure (VE.Route.Wire.ok id [("verdict", .str (if e.startsWith "ResourceLimit" then "UNKNOWN" else "INVALID")),
      ("diagnostic", .str e)])

def runCase (j : Json) : Except String Json := do
  let id ← stringField j "id"
  let kind ← VE.Route.Run.caseKind j
  if !usesDiscoursePath j then return ← VE.Route.Run.runCase j
  let environment ← j.getObjVal? "environment"
  let profiles ← VE.Route.Gate.profilesOf environment
  let rv ← baseVocabulary environment
  let document ← j.getObjVal? "document"
  if kind == "admission" then
    let res ← admitDiscourse profiles environment rv document fuelBudget
    encodeAdmission id res
  else if kind == "discourse-validity" then
    let res ← admitDiscourse profiles environment rv document fuelBudget
    pure (VE.Route.Wire.ok id [("validity", Json.mkObj (res.doc.K.validity.map fun v =>
      (v.unit, .str ((res.validity v.unit).map verdictText |>.getD "none"))))])
  else if kind == "discourse-resolve" then runResolve profiles environment rv id document
  else if kind == "discourse-joint" then runJoint profiles environment rv id document
  else throw s!"UnsupportedProfile: case kind {kind} is not available on the discourse route"

def runCaseReported (j : Json) : Json :=
  if usesDiscoursePath j then
    match runCase j with
    | .ok result => result
    | .error message => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"), ("error", .str message)]
  else VE.Route.Run.runCaseReported j

def main (paths : List String) : IO UInt32 := do
  let input ← match paths with
    | [] | ["-"] => (← IO.getStdin).readToEnd
    | [path] => IO.FS.readFile path
    | _ =>
      (← IO.getStderr).putStrLn "usage: ve_discourse_route [cases.json|-]"
      return 2
  match VE.JsonInput.parseCases input with
  | .error message =>
    (← IO.getStderr).putStrLn message
    return 2
  | .ok cases =>
    let results := cases.mapIdx fun index c => match c with
      | .ok j => runCaseReported j
      | .error message => Json.mkObj [("status", .str "error"), ("case_index", toJson index), ("error", .str message)]
    (← IO.getStdout).putStrLn (Json.arr results).compress
    return if results.any (fun r => r.getObjValD "status" == .str "error") then 1 else 0

end VE.Discourse.Run
