import VE.Service.Standalone
import VE.Discourse.Admission

/-! # The `document` service mode: the `ve-document@1` wrapper (docs/LEAN-FIRST-PLAN.md, row 16a)

A case is `{"id", "document"}`, the document text Python's `ve/document.py` reads. The mode does what
`load_document` and the wrapper part of `check_document` (`_report`: the claim graph's admission and the
narrowing choices, then `coverage`) do, in their order and with their texts: the front matter, the fences, the
units and their spans, `MIXED` parts, every unit's content, meaning and status, the open terms, the reading sets
with their status fold, the couplings and completions gates, lemmas, narrowings and removable weights, the graph's
W2 admission, the identities, and the coverage tables with their residual counts. The steps it shares with the
discourse route are `VE.Discourse.Loader`'s, read in their `python` mode; every formula is checked by the `check`
mode's typed decoder with Python's typing texts (`formulaCheck`).

What the mode cannot decide yet is `CheckerUnavailable`, never a verdict (`unavailable`): a `ve-document@2`
document (the discourse route's), front matter outside the restricted JSON reader (`null`, a negative,
fractional or out-of-range number, a duplicate key, `NaN`), an environment outside the plain `ve.core@0.2`
envelope or with a profile outside `ownedProfiles` (each such profile's loader adds checks and coverage lines its
own Lean route owns), regulated or norm content, fenced English or strict content, a distinguishing model the
Lean model decoder refuses, and a claim graph the Lean admission route defers. -/
namespace VE.Service.Document
open Lean
open VE.Discourse
open VE.Bridge (stringField fields)
open VE.Route.Admission (token)

def unavailable (what : String) : String := "CheckerUnavailable: " ++ what

/-- The profiles whose document semantics this mode owns: the FOL family with the statement layers whose
`load_document` steps and coverage lines are the plain wrapper's. A document listing any other profile is
`CheckerUnavailable` before its environment is decoded (its own loader would add checks this mode lacks). -/
def ownedProfiles : List String :=
  ["data@0", "definitions@0", "documents@1", "norms@0", "relational-fol@0", "time@0"]

/-- The keys of the plain `ve.core@0.2` envelope (`Route.Gate.decodeEnvelope`). -/
def envelopeKeys : List String := ["language", "profiles", "spec_revision", "vocabulary"]

/-- `listed_profiles`: the profiles of environment JSON when they are a list of strings, else none. -/
def listedProfiles (environment : Json) : List String :=
  (VE.Route.Gate.profilesOf environment).toOption.getD []

/-! ## The front matter -/

/-- Whether Python's JSON reader may read a front matter the restricted reader refuses: Lean's own JSON
parser reads it (`null`, numbers outside the natural numbers, duplicate keys, a lone surrogate), or it names
one of Python's non-standard constants. An over-approximation: it only turns a rejection into
`CheckerUnavailable`. -/
def pythonMayRead (front : String) : Bool :=
  (Json.parse front).isOk || ["NaN", "Infinity"].any fun t => (front.splitOn t).length > 1

def frontJson (front : String) : Except String Json :=
  match VE.JsonInput.parse front with
  | .ok j => .ok j
  | .error e =>
    let text := Loader.frontJsonError e
    if text == "invalid JSON front matter" && pythonMayRead front then
      .error (unavailable "front matter outside the restricted JSON reader (null, a negative, fractional or large number, a duplicate key)")
    else .error text

/-- `_split` with `is_discourse_text` first: the metadata keys, the couplings and completions gates, then the
body. -/
def split (t : String) : Except String Loader.Split := do
  let (front, body) ← Loader.frontText t
  let fm ← frontJson front
  if fm.getObjValD "format" == .str "ve-document@2" then
    throw (unavailable "a ve-document@2 document is admitted by the discourse route")
  let _ ← Loader.checkMetadata Loader.documentMetadata fm
  let listed := listedProfiles (fm.getObjValD "environment")
  if (fm.getObjVal? "couplings").isOk && !(listed.contains "rights@0" || listed.contains "readings@1") then
    throw "UnsupportedProfile: rights@0 is required for couplings"
  if (fm.getObjVal? "completions").isOk && !listed.contains "norm-defaults@0" then
    throw "UnsupportedProfile: norm-defaults@0 is required for completions"
  let (source, fences) ← Loader.bodyOf (Loader.linesOf body) (python := true)
  pure ⟨fm, source, fences⟩

/-! ## The environment -/

/-- The checked environment of a document and what its checks read. -/
structure Env where
  json : Json
  checked : Standalone.Validated
  rv : VE.Route.Wire.RouteVocabulary
  profiles : List String
  envId : String

def Env.data (E : Env) : Bool := E.profiles.contains "data@0"

/-- `base_environment`, the profile gate (before any decoding, so an unowned profile is never rejected by a
decoder that does not read it), then the envelope decoder. -/
def environmentOf (environment : Json) : Except String Env := do
  match environment.getObjValD "profiles" with
  | .arr ps => if ps.contains (.str VE.Discourse.discourseProfile) then
      throw "UnsupportedProfile: ve.discourse@1 requires ve-document@2"
  | _ => pure ()
  if Standalone.isLegacy environment then
    throw (unavailable "a document over a ve.core@0 or ve.core@0.1 environment needs its legacy route")
  if let some p := (listedProfiles environment).find? (!ownedProfiles.contains ·) then
    throw (unavailable s!"document checks under {p} need its Lean profile route")
  let keys := ((fields environment).toOption.getD []).map Prod.fst
  if let some k := keys.find? (!envelopeKeys.contains ·) then
    throw (unavailable s!"the environment block {k} needs its Lean route's decoder")
  let checked ← Standalone.validated environment
  let e := checked.envelope
  unless e.family == .fol do
    throw (unavailable s!"document checks on the {e.family.name} family need its Lean route")
  let predicates ← fields (← e.vocabulary.getObjVal? "predicates")
  if e.profiles.contains "norms@0" && predicates.any (fun (_, entry) => (entry.getObjVal? "regulated").isOk) then
    throw (unavailable "regulated predicates need the Lean norms route")
  let rv ← VE.Route.Run.decodeRouteVocabulary e
  pure ⟨environment, checked, rv, e.profiles, ← Standalone.environmentIdOf e.profiles environment⟩

/-- `formula_from_data` over the document's environment: the `check` mode's typed decoder, its rejection named as
Python names it. -/
def formulaCheck (E : Env) (ast : Json) : Except String Unit :=
  match Standalone.decodeTyped E.checked ast true with
  | .ok () => .ok ()
  | .error message => .error ((TypingDiagnostic.diagnose E.profiles E.checked.envelope.vocabulary [ast]).getD message)

/-- A checked formula and its `meaning_id`. -/
def formulaOf (E : Env) (ast : Json) : Except String (VE.Formula × String) := do
  formulaCheck E ast
  let f ← VE.Route.Wire.decodeClosed E.rv.environment ast E.data
  pure (f, ← VE.Route.Wire.meaningId E.profiles E.envId (VE.Route.Wire.encodeFormula f))

/-! ## Units -/

structure SourceUnit where
  id : String
  span : Nat × Nat
  kind : Json
  meaning : Json
  support : String
  status : String
  parent : Option String
  content : Option VE.Formula := none
  explicit : Option String := none

def kindName (kind : Json) : String :=
  match kind with
  | .str s => s
  | .arr xs => (xs[0]?.getD Json.null).getStr?.toOption.getD ""
  | _ => ""

/-- `_content` for the owned profiles: the unit's checked formula and `meaning_id`, or the reason it has none
here. -/
def contentOf (E : Env) (fences : List (String × String)) (u : Json) (id : String) (content : Json) :
    Except String (VE.Formula × String) := do
  let one := "unit content must bind one formula or norm"
  let (key, value) ← match content with
    | .obj kvs => match kvs.toList with
      | [kv] => pure kv
      | _ => throw one
    | _ => throw one
  if key == "quantity" then throw "UnsupportedProfile: quantity content requires ve-units@1"
  if key == "norm" then
    if E.profiles.contains "norms@0" then throw (unavailable "norm content needs the Lean norms route")
    throw "UnsupportedProfile: norms@0 is required"
  if ["right", "right_lines", "limitation", "bar"].contains key then throw "UnsupportedProfile: rights@0 is required"
  if key == "ast" then return ← formulaOf E value
  unless key == "fence" && value == .str id do throw "unit fence must match its id"
  unless (fences.map Prod.fst).contains id do throw "missing VE fence"
  unless u.getObjValD "surface" == .str "english" || u.getObjValD "surface" == .str "strict" do
    throw "fenced content needs english or strict surface"
  throw (unavailable "fenced English or strict content needs the Lean surface parser")

/-- `load_document`'s checks of one unit at byte `cursor`, in Python's order. -/
def sourceUnit (E : Env) (source : String) (fences : List (String × String)) (openNames : List String)
    (cursor : Nat) (seen parents : List String) (parent : Option String) (u : Json) : Except String SourceUnit := do
  let keys ← (fields u).mapError (fun _ => "invalid unit schema")
  let names := keys.map Prod.fst
  let required := ["id", "span", "kind", "meaning", "support"]
  unless required.all names.contains &&
      names.all (required ++ ["content", "surface", "meaning_id", "status"]).contains do
    throw "invalid unit schema"
  let id := (u.getObjValD "id").getStr?.toOption.getD ""
  unless token id && !seen.contains id && !parents.contains id do
    throw "duplicate or invalid unit id"
  let (a, b) ← (Loader.spanOf (u.getObjValD "span")).mapError
    (fun _ => "unit spans must partition every source byte in order")
  unless a == cursor && cursor < b && b ≤ source.utf8ByteSize do
    throw "unit spans must partition every source byte in order"
  if Loader.cutsCharacter source a b then throw "unit span cuts a UTF-8 character"
  let kind := u.getObjValD "kind"
  let _ ← VE.Route.Admission.decodeKind 16 kind
  let meaning := u.getObjValD "meaning"
  let meaningStatus ← Loader.meaningStatus openNames meaning (python := true)
  let support := (u.getObjValD "support").getStr?.toOption.getD ""
  unless Loader.supports.contains support do throw "invalid support"
  let compiled ← match u.getObjVal? "content" with
    | .ok content => some <$> contentOf E fences u id content
    | .error _ => pure none
  if let .arr xs := kind then
    if xs[0]? == some (.str "unformalised") && meaning != Json.mkObj [("unformalised", xs[1]?.getD .null)] then
      throw s!"InvalidInput: unformalised kind reason does not match meaning of {id}"
  if meaningStatus == "unformalised" && compiled.isSome then
    throw "unformalised unit cannot assert content"
  if let (.ok stated, some (_, mid)) := (u.getObjVal? "meaning_id", compiled) then
    unless stated == .str mid do throw "unit meaning id does not match content"
  let explicit ← match u.getObjVal? "status" with
    | .ok (.str s) => if Loader.statuses.contains s then pure (some s) else throw "invalid unit status"
    | .ok _ => throw "invalid unit status"
    | .error _ => pure none
  pure { id, span := (a, b), kind, meaning, support, parent, explicit,
         content := compiled.map Prod.fst, status := Loader.w2Status compiled.isSome meaningStatus }

/-- `_parts` interleaved with the unit loop, as Python's generator runs: a `MIXED` part is checked against its
parent's cursor, then compiled, before the next part is read; the parent's end is checked after its last part. -/
def unitsOf (E : Env) (source : String) (fences : List (String × String)) (openNames : List String)
    (raw : List Json) : Except String (List SourceUnit) := do
  let parents ← Loader.mixedParents raw
  let mut units : Array SourceUnit := #[]
  let mut cursor := 0
  for u in raw do
    match ← Loader.mixedOf u with
    | none =>
      let unit ← sourceUnit E source fences openNames cursor (units.toList.map (·.id)) parents none u
      units := units.push unit
      cursor := unit.span.2
    | some ((a, b), parts) =>
      let parent := (u.getObjValD "id").getStr?.toOption
      let mut inner := a
      for p in parts do
        Loader.partOk inner p
        let unit ← sourceUnit E source fences openNames cursor (units.toList.map (·.id)) parents parent p
        units := units.push unit
        cursor := unit.span.2
        inner := unit.span.2
      unless inner == b do throw Loader.partitionText
  unless cursor == source.utf8ByteSize do throw "unit spans do not partition all source bytes"
  pure units.toList

/-! ## Coverage -/

def addCount (xs : List (String × Nat)) (name : String) (n : Nat) : List (String × Nat) :=
  if xs.any (·.1 == name) then xs.map (fun (k, v) => (k, if k == name then v + n else v))
  else xs ++ [(name, n)]

def counts (units : List SourceUnit) (key : SourceUnit → String) : List (String × Nat) :=
  units.foldl (fun acc u => addCount acc (key u) (u.span.2 - u.span.1)) []

def reasons (units : List SourceUnit) : List (String × Nat) :=
  units.foldl (fun acc u => match u.meaning.getObjVal? "unformalised" with
    | .ok (.str reason) => addCount acc reason 1
    | _ => acc) []

def countJson (xs : List (String × Nat)) : Json :=
  Json.mkObj (xs.map fun (k, v) => (k, toJson v))

/-- The labels of the graph's nodes, as `coverage` reads them: string labels of object nodes. -/
def graphLabels (front : Json) : List String :=
  match (front.getObjValD "graph").getObjValD "nodes" with
  | .arr xs => xs.toList.filterMap fun n => match n with
    | .obj _ => (n.getObjValD "label").getStr?.toOption
    | _ => none
  | _ => []

/-- `coverage`'s residual counts for the owned profiles. -/
def residual (front : Json) (units : List SourceUnit) : List (String × Nat) :=
  let count (key : String) := match front.getObjValD key with
    | .arr xs => xs.toList
    | _ => []
  [("open_terms", (count "open_terms").length),
   ("assumptions", (units.filter (·.support == "assumption")).length),
   ("bridge_leaves", ((graphLabels front).filter (·.startsWith "bridge:accepts(")).length),
   ("unresolved_reading_sets", ((count "reading_sets").filter (·.getObjValD "status" == .str "open")).length)]

def unitJson (u : SourceUnit) : Json :=
  Json.mkObj ([("id", .str u.id), ("span", toJson [u.span.1, u.span.2]),
    ("kind", u.kind), ("meaning", u.meaning), ("support", .str u.support),
    ("status", .str u.status)] ++
    (u.parent.toList.map fun p => ("parent_id", .str p)))

/-- The coverage object of `coverage(doc)`. -/
def coverageJson (front : Json) (units : List SourceUnit) (sourceBytes : Nat) : Json :=
  let rest := residual front units
  Json.mkObj [("source_bytes", toJson sourceBytes), ("accounted_bytes", toJson sourceBytes),
    ("coverage_percent", toJson (100 : Nat)), ("bytes_by_kind", countJson (counts units (kindName ∘ SourceUnit.kind))),
    ("bytes_by_status", countJson (counts units SourceUnit.status)), ("unformalised_reasons", countJson (reasons units)),
    ("residual", countJson rest), ("residual_total", toJson ((rest.map Prod.snd).sum))]

/-! ## The claim graph -/

/-- The graph's node labels as `_report` parses them: `parse_label` of an object node's label. -/
def parsedLabels (graph : Json) : List VE.Route.Admission.Label :=
  match graph.getObjValD "nodes" with
  | .arr xs => xs.toList.filterMap fun n => match n with
    | .obj _ => (n.getObjValD "label").getStr?.toOption.bind VE.Route.Admission.parseLabel
    | _ => none
  | _ => []

/-- `_report`'s claim-graph part for the owned profiles: the reading checks of the graph's labels, W2 admission
(the route's `admission`), then `_check_narrowing_choices` over the admitted report's labels. -/
def admitGraph (E : Env) (front graph : Json) (units : List SourceUnit) (all active : List (FrontSet × List Bool))
    (openNames narrowings : List String) : Except String Unit := do
  let nodes := match graph.getObjValD "nodes" with
    | .arr xs => xs.toList
    | _ => []
  -- `_unresolved_norm_reading`: an active reading of kind `norm` (every reading here has content).
  let normReading := active.any fun (s, _) => s.readings.any fun (r, _) =>
    (((front.getObjValD "reading_sets").getArr?.toOption.getD #[]).toList.any fun j =>
      j.getObjValD "id" == .str s.id && j.getObjValD "version" == toJson s.version &&
      ((j.getObjValD "readings").getArr?.toOption.getD #[]).toList.any fun c =>
        c.getObjValD "id" == .str r && c.getObjValD "kind" == .str "norm")
  if normReading && nodes.any (fun n => ((n.getObjValD "label").getStr?.toOption.getD "").startsWith "layer:norms:") then
    throw "non-assertion norm reading admission needs an elaborator"
  for label in parsedLabels graph do
    if let .readings set version _ := label then
      match active.find? fun (s, _) => s.id == set && s.version == version with
      | none => throw "graph cites a stale or unknown reading set version"
      | some (_, kinds) => unless kinds.all id do throw "non-assertion reading admission needs an elaborator"
  let document := Loader.admissionObject (units.map fun u => (u.id, u.span, u.kind, u.content)) active graph
    front openNames narrowings
  let answer ← match VE.Route.Run.runAdmit E.profiles E.json E.rv "admission"
      (Json.mkObj [("document", document)]) with
    | .ok a => pure a
    | .error e => if e.startsWith "UnsupportedProfile" then throw (unavailable ("claim graph: " ++ e)) else throw e
  let labels := (((answer.getObjValD "report").getObjValD "assumptions").getArr?.toOption.getD #[]).toList.filterMap
    fun a => (a.getObjValD "label").getStr?.toOption
  let parsed := labels.filterMap VE.Route.Admission.parseLabel
  let sets := ((front.getObjValD "narrowings").getArr?.toOption.getD #[]).toList
  for n in sets do
    let nid := (n.getObjValD "id").getStr?.toOption.getD ""
    unless labels.contains ("narrowing:" ++ nid) do continue
    let set := (n.getObjValD "set").getStr?.toOption.getD ""
    let version := (n.getObjValD "version").getNat?.toOption.getD 0
    let keeps := ((n.getObjValD "keeps").getArr?.toOption.getD #[]).toList
    let readings := match all.find? fun (s, _) => s.id == set && s.version == version with
      | some (s, _) => s.readings.map Prod.fst
      | none => []
    for label in parsed do
      if let .readings s v (some i) := label then
        if s == set && v == version then
          unless keeps.contains (.str (readings.getD i "")) do
            throw "reading choice conflicts with narrowing"

/-! ## The case -/

/-- The checked document: its identities, its source and units, and what its coverage reads. -/
structure Checked where
  documentId : String
  sourceId : String
  source : String
  units : List SourceUnit
  front : Json

def check (text : String) : Except String Checked := do
  let doc ← split text
  let front := doc.front
  if doc.source.isEmpty then throw "document source is empty"
  let environment := front.getObjValD "environment"
  unless environment matches .obj _ do throw "document needs an embedded environment"
  let E ← environmentOf environment
  if ["contexts", "assessments", "bridges", "scoped"].any (front.getObjVal? · |>.isOk) then
    throw "unknown document metadata"
  let openNames ← Loader.openTermNames E.rv (Loader.optionalList front "open_terms") (python := true)
    (data := E.data) (formula := some (formulaCheck E))
  let raw ← match front.getObjValD "units" with
    | .arr xs => if xs.isEmpty then throw "document needs units" else pure xs.toList
    | _ => throw "document needs units"
  let units ← unitsOf E doc.source doc.fences openNames raw
  unless doc.fences.isEmpty do throw "unbound VE fence"
  let unitIds := units.map (·.id)
  let all ← Loader.compileSets E.rv E.profiles E.envId unitIds (Loader.optionalList front "reading_sets")
    (python := true) (formula := formulaCheck E)
    (modelRefused := some (unavailable "a distinguishing model the Lean model decoder refuses"))
  let active := Loader.activeOf all
  let units := units.map fun u => { u with status := Loader.foldStatus active u.id u.status }
  if units.any (fun u => u.explicit.any (· != u.status)) then
    throw "unit status contradicts content, meaning, or active reading set"
  Loader.checkLemmas front
  for u in units do
    if u.kind == .str "asserted" && u.content.isNone && !(all.any (·.1.unit == u.id)) then
      throw "asserted unit needs content or a reading set"
  let narrowings ← Loader.narrowingIds (all.map fun (s, _) => (s.id, s.version, s.readings.map Prod.fst))
    unitIds (Loader.optionalList front "narrowings") (python := true)
  Loader.checkWeights front
  if let .ok graph := front.getObjVal? "graph" then
    admitGraph E front graph units all active openNames narrowings
  pure ⟨← Loader.documentId (Loader.payload doc (Json.mkObj [])), Loader.sourceId E.profiles doc.source,
    doc.source, units, front⟩

def encode (id : String) (c : Checked) : Json :=
  VE.Route.Wire.ok id [("document_id", .str c.documentId), ("source_id", .str c.sourceId),
    ("source", .str c.source), ("units", toJson (c.units.map unitJson)),
    ("coverage", coverageJson c.front c.units c.source.utf8ByteSize)]

def documentCase (j : Json) : Except String Json := do
  let id ← stringField j "id"
  let text ← stringField j "document"
  pure (encode id (← check text))

def runCaseReported (j : Json) : Json := Standalone.reported documentCase j

end VE.Service.Document
