import VE.Discourse.Admission

/-! # The `ve_discourse_route` executable (docs/spec/discourse.md 9.7)

Each case is `{"id", "kind", "document", "files"?, "environment"?, ...}`. A `ve-document`
case's `document` is the document text itself, the bytes the Python loader reads; its
environment is the one its front matter embeds (a case `environment`, when present, must be
that one) and `files` maps the sibling file names an import's `bytes` may name to their texts.
A case uses the discourse path when its document is such a text, its environment declares
`ve.discourse@1`, or its kind starts with `discourse-`; every other case is delegated unchanged
to the `route` runner (`VE.Route.Run.runCase`), and a discourse input never falls back after a
failed discourse decode. Case kinds:

* `admission`: `admitted` (`true`, or `UNKNOWN` when the joint set exceeds its budget and every
  reading-dependent verdict is UNKNOWN, 4.1(8)), `reading_verdicts`, `report`, `report_id` (the
  wrapper identity), `inner_report_id`, `document_id`, `source_id`, `environment_id`, `kinds`,
  `references`, `presuppositions`, `pending`, `bound`, `meaning_ids`, `validity`, `statuses`,
  `joint` (the number of compatible choices, or the budget's diagnostic) and, when the joint set
  completed, `joint_choices` and `joint_formula` (as `discourse-joint`'s `choices` and `joint`);
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
  let text := match j.getObjValD "document" with
    | .str _ => true
    | _ => false
  text || profiles.contains discourseProfile || kind

def fuelBudget : Nat := 5

/-- A case's document, loaded, and its environment: a document text brings its own. -/
def loadCase (j : Json) : Except String (Json × Json) := do
  match ← j.getObjVal? "document" with
  | .str t => do
    let s ← Loader.splitText t
    let env := s.front.getObjValD "environment"
    if let .ok e := j.getObjVal? "environment" then
      unless e == env do throw "InvalidInput: the case environment is not the document's"
    let files := match j.getObjVal? "files" with
      | .ok f => f
      | .error _ => Json.mkObj []
    pure (Loader.payload s files, env)
  | d => pure (d, ← j.getObjVal? "environment")

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

def admittedJson (res : Admitted) : Json :=
  if (readingVerdicts res).isEmpty then .bool true else .str "UNKNOWN"

/-- The compatible choices on the wire: per choice, `[set, version, reading index]` for each
active open set, in document order. -/
def choicesJson (cs : List Choice) : Json :=
  Json.arr (cs.map fun c => Json.arr (c.map fun (s, v, i) => Json.arr #[.str s, toJson v, toJson i]).toArray).toArray

/-- The joint disjunction `Joint(K)` of the compatible choices (4.8), or `[]` when there is none. -/
def jointJson (sets : List VE.Route.Admission.ReadingSet) (cs : List Choice) : Json :=
  match joint sets cs with
  | some J => VE.Route.Wire.encodeFormula J
  | none => Json.arr #[]

/-- A completed joint set's choices and disjunction, the fields the Python relay displays and
hands to the premise check (it never enumerates them itself); nothing when the set hit its budget. -/
def jointFields (res : Admitted) : List (String × Json) :=
  match res.joint with
  | .ok cs => [("joint_choices", choicesJson cs), ("joint_formula", jointJson (activeSets res.doc) cs)]
  | .error _ => []

def encodeAdmission (id : String) (res : Admitted) : Except String Json := do
  let bound ← (boundUnits res.doc).eraseDups.filterMapM fun u => match res.bound u with
    | some A => pure (some (u, VE.Route.Wire.encodeFormula A))
    | none => pure none
  pure (VE.Route.Wire.ok id <| [("admitted", admittedJson res),
    ("reading_verdicts", Json.mkObj ((readingVerdicts res).map fun (k, v) => (k, .str v))),
    ("report", reportJson res.base.report),
    ("report_id", .str res.reportId), ("inner_report_id", .str res.innerReportId),
    ("document_id", .str res.documentId), ("source_id", .str res.doc.sourceId),
    ("environment_id", .str res.environmentId),
    ("definitions_version", .str res.doc.K.definitionsVersion),
    ("kinds", Json.arr res.base.kinds.toArray),
    ("references", res.references),
    ("bound", Json.mkObj bound),
    ("meaning_ids", Json.mkObj (res.boundIds.map fun (u, m) => (u, .str m))),
    ("presuppositions", Json.mkObj ((presupMentions res.doc).map fun m =>
      (m.id, .str (presuppositionLine m (res.presuppositions m.id))))),
    ("pending", Json.arr (res.pending.map fun (u, d) => Json.arr #[.str u, .str d]).toArray),
    ("validity", Json.mkObj (res.claims.map fun v =>
      (v.unit, .str ((res.validity v.unit).map verdictText |>.getD "none")))),
    ("self_truth", toJson res.selfTruth),
    ("statuses", Json.mkObj ((res.base.doc.units.map VE.Route.Admission.DocUnit.id).map fun u => (u, .str (statusOf res u)))),
    ("joint", match res.joint with
      | .ok cs => toJson cs.length
      | .error e => .str e)] ++ jointFields res)

def runResolve (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary) (id : String) (j : Json) :
    Except String Json := do
  let P ← prepare profiles environment rv j
  let D := P.doc
  let bp := baseProfiles profiles
  let envId := P.environmentId
  let units ← (boundUnits D).eraseDups.mapM fun u => match validate D u with
    | .ok A => do
      let mid ← VE.Route.Wire.meaningId bp envId (VE.Route.Wire.encodeFormula A)
      pure (u, Json.mkObj [("status", .str "resolved"), ("formula", VE.Route.Wire.encodeFormula A),
        ("meaning_id", .str mid)])
    | .error e => pure (u, Json.mkObj [("status", .str "error"), ("error", .str e)])
  let mentions := D.K.mentions.map fun m =>
    let slot : Slot := ⟨m.unit, m.span, m.form⟩
    (m.id, Json.mkObj ([("accessible", Json.arr ((accCands D slot).map targetJson).toArray),
      ("recorded", targetJson m.target), ("accessible_recorded", .bool (accB D slot m.target))] ++
      match m.pin with
      | some v => [("pin", toJson v)]
      | none => []))
  let wf := match wellFormed D with
    | .ok _ => Json.str "ok"
    | .error e => Json.str e
  pure (VE.Route.Wire.ok id [("units", Json.mkObj units), ("mentions", Json.mkObj mentions),
    ("well_formed", wf), ("environment_id", .str envId), ("source_id", .str D.sourceId),
    ("joint", match compatibleChoices D.K (activeSets D) 64 with
      | .ok cs => toJson cs.length
      | .error e => .str e)])

def runJoint (profiles : List String) (environment : Json) (rv : VE.Route.Wire.RouteVocabulary) (id : String) (j : Json) :
    Except String Json := do
  let P ← prepare profiles environment rv j
  let D := P.doc
  let sets := activeSets D
  match compatibleChoices D.K sets 64 with
  | .ok cs => pure (VE.Route.Wire.ok id [("verdict", .str "COMPLETE"),
      ("choices", choicesJson cs), ("joint", jointJson sets cs)])
  | .error e => pure (VE.Route.Wire.ok id [("verdict", .str (if e.startsWith "ResourceLimit" then "UNKNOWN" else "INVALID")),
      ("diagnostic", .str e)])

def runCase (j : Json) : Except String Json := do
  let id ← stringField j "id"
  let kind ← VE.Route.Run.caseKind j
  if !usesDiscoursePath j then return ← VE.Route.Run.runCase j
  let (document, environment) ← loadCase j
  let profiles ← VE.Route.Gate.profilesOf environment
  let rv ← baseVocabulary environment
  if kind == "admission" then
    let res ← admitDiscourse profiles environment rv document fuelBudget
    encodeAdmission id res
  else if kind == "discourse-validity" then
    let res ← admitDiscourse profiles environment rv document fuelBudget
    pure (VE.Route.Wire.ok id [("validity", Json.mkObj (res.claims.map fun v =>
      (v.unit, .str ((res.validity v.unit).map verdictText |>.getD "none"))))])
  else if kind == "discourse-resolve" then runResolve profiles environment rv id document
  else if kind == "discourse-joint" then runJoint profiles environment rv id document
  else throw s!"UnsupportedProfile: case kind {kind} is not available on the discourse route"

/-- A successful `admission` answer is exactly the encoding of a checked discourse admission of
the case's own document (loaded with its files) under its environment's declared profiles and
the base-pair vocabulary. -/
def DiscourseAdmissionAnswer (id : String) (j answer : Json) : Prop :=
  ∃ document environment profiles rv res, loadCase j = .ok (document, environment) ∧
    VE.Route.Gate.profilesOf environment = .ok profiles ∧ baseVocabulary environment = .ok rv ∧
    admitDiscourse profiles environment rv document fuelBudget = .ok res ∧ encodeAdmission id res = .ok answer

/-- The public entry point: a successful `admission` answer on the discourse path is the encoding
of a checked discourse admission whose results satisfy the admission theorems. -/
theorem discourse_wire_acceptance (j answer : Json) (h : runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "admission") (hd : usesDiscoursePath j = true) :
    ∃ id, VE.Bridge.stringField j "id" = .ok id ∧ DiscourseAdmissionAnswer id j answer := by
  unfold runCase at h
  obtain ⟨id, hid, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨kind, hkind, h⟩ := VE.Order.ProfileGate.bind_ok h
  have heq : kind = "admission" := by rw [hkind] at hk; cases hk; rfl
  subst kind
  simp only [hd, Bool.not_true, Bool.false_eq_true, if_false] at h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨⟨document, environment⟩, hl, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨profiles, hp, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨rv, hrv, h⟩ := VE.Order.ProfileGate.bind_ok h
  simp only [beq_self_eq_true, if_true] at h
  obtain ⟨res, hres, h⟩ := VE.Order.ProfileGate.bind_ok h
  exact ⟨id, hid, document, environment, profiles, rv, res, hl, hp, hrv, hres, h⟩

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
