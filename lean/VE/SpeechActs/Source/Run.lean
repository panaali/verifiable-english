import VE.SpeechActs.Run
import VE.Discourse.Loader

/-! # The decoded-source wrapper and its records (docs/spec/speech-acts.md 3.2, 3.3, 3.5, 5, 6, 8.5)

The `speech-source` case kind reads a `ve-document@2` payload `{"metadata", "source", "fences"}` (the identity
payload of 3.5, as `Discourse.Loader.payload` builds it from a document text) and does what Python's experimental
`ve/speech_document.py` `SpeechSource` does, in its order:

* the front matter (`allowedMetadata`), the embedded environment through the speech decoder, the source;
* the units: `MIXED` parts (`Loader.partsOf`), the unit schema, spans partitioning the source bytes in whole UTF-8
  characters, kinds (W2's plus `binding`), supports, fence references, and every span's wording ASCII (3.2);
* fences ASCII; W2's open terms (`Loader.openTermNames`) and every unit's meaning (`Loader.meaningStatus`);
* reading sets: W2's formula-only sets through `Loader.compileSets`, the others as speech candidates (`speechSet`);
  narrowings (`Loader.narrowingIds`);
* the semantic core (`Run.checkedDocument`) over the units with their wordings, so every check of `Wire` runs;
* each stated unit status against W2's inference (`Loader.w2Status`), the derived `intended-reading` open term of
  every reading question (4.6), removable weights;
* the identities (`Loader.documentId`, `Loader.sourceId`), the coverage projection of 6 with its reconciliation;
* the answer, nomination and compliance records of 3.3, each replayed by the checkers `Run` already uses.

What is not done here (named, never a silent acceptance): English fences need the speech parser, which is Python's
English layer (`NotImplemented: fenced English content`); the claim graph is not admitted (P0 `admit_document` over
the projection, 8.5's `SpeechAdmitted`), as Python's wrapper never checks it either; a compliance record naming an
asserted `done` unit (external evidence) is rejected as Python rejects it (`QueryMismatch: <u>`), since no checker
derives the `done` predicate of an act. -/
namespace VE.SpeechActs.Source
open Lean
open VE.Bridge (stringField strings fields)
open VE.Route.Admission (token)
open VE.Discourse
open VE.Norms (Sat)
universe u

/-- The front-matter keys of a speech-act source (3.5): W2's, without `discourse`, with the query and record
lists. -/
def allowedMetadata : List String :=
  ["format", "environment", "units", "open_terms", "reading_sets", "narrowings", "weights", "graph", "lemmas",
   "queries", "answers", "compliance"]

def unitRequired : List String := ["id", "span", "kind", "meaning", "support"]
def unitOptional : List String := ["content", "surface", "meaning_id", "status"]
def partitionError : String := "unit spans must partition every source byte in order"

/-! ## Units -/

/-- One source unit (a `MIXED` part included) as the wrapper reads it. -/
structure SourceUnit where
  id : String
  span : Nat × Nat
  kind : Json
  meaning : Json
  content : Option Json
  /-- the span's sentence, ASCII and trimmed of ASCII whitespace (3.2, Python's `wording_text`) -/
  wording : String
  /-- the stated W2 status, if any -/
  explicit : Option Json
  /-- the `MIXED` parent, provenance only -/
  parent : Option String
  raw : Json

/-- One unit at byte `cursor` of `source` (Python's `SpeechSource` unit loop, in its order). -/
def readUnit (source : String) (fences : List (String × String)) (cursor : Nat) (seen : List String)
    (parent : Option String) (u : Json) : Except String SourceUnit := do
  let keys ← match u with
    | .obj kvs => pure (kvs.toList.map Prod.fst)
    | _ => throw "invalid unit schema"
  unless unitRequired.all keys.contains && keys.all (unitRequired ++ unitOptional).contains do
    throw "invalid unit schema"
  let id := ((u.getObjValD "id").getStr?).toOption.getD ""
  let (a, b) ← match u.getObjValD "span" with
    | .arr #[x, y] => match x.getNat?, y.getNat? with
      | .ok a, .ok b => pure (a, b)
      | _, _ => throw partitionError
    | _ => throw partitionError
  unless token id && !seen.contains id && a == cursor && cursor < b && b ≤ source.utf8ByteSize do
    throw partitionError
  let some text := String.fromUTF8? (source.toUTF8.extract a b) | throw "unit span cuts a UTF-8 character"
  let kind := u.getObjValD "kind"
  unless kind == .str "binding" do
    let _ ← VE.Route.Admission.decodeKind 16 kind
  unless Loader.supports.contains (((u.getObjValD "support").getStr?).toOption.getD "") do throw "invalid support"
  let content := (u.getObjVal? "content").toOption
  if let some c := content then
    if let .ok f := c.getObjVal? "fence" then
      unless f == .str id && (fences.map Prod.fst).contains id do throw "unit fence must match its id"
      unless u.getObjValD "surface" == .str "english" do throw "speech fence needs English surface"
  unless Wire.asciiWording text do throw Wire.nonAsciiWording
  pure ⟨id, (a, b), kind, u.getObjValD "meaning", content, Loader.byteStrip text,
    (u.getObjVal? "status").toOption, parent, u⟩

/-- Every unit in document order, a `MIXED` unit contributing its parts; the spans partition the source. -/
def readUnits (source : String) (fences : List (String × String)) (raw : List Json) :
    Except String (List SourceUnit) := do
  let mut units : Array SourceUnit := #[]
  let mut cursor := 0
  for u in raw do
    let parts ← Loader.partsOf u
    let parent : Option String := if parts == [u] then none else ((u.getObjValD "id").getStr?).toOption
    for p in parts do
      let x ← readUnit source fences cursor (units.toList.map (·.id)) parent p
      cursor := x.span.2
      units := units.push x
  unless cursor == source.utf8ByteSize do throw "unit spans do not partition all source bytes"
  pure units.toList

/-! ## Reading sets (W2's, with speech candidates retained) -/

/-- One validated reading-set version: its readings in source order, as JSON objects. -/
structure SetInfo where
  id : String
  unit : String
  version : Nat
  authored : Bool
  readings : List Json

/-- Python's `latest_reading_sets` over validated sets: per unit, the latest version. -/
def latestOf (sets : List SetInfo) (unit : String) : Option SetInfo :=
  sets.foldl (fun acc s => if s.unit == unit && (acc.all (·.version < s.version)) then some s else acc) none

/-- The keys of an object (none for any other JSON value). -/
def keysOf (j : Json) : List String := ((fields j).toOption.getD []).map Prod.fst

def isObj : Json → Bool
  | .obj _ => true
  | _ => false

def readingsOf (item : Json) : List Json :=
  match item.getObjValD "readings" with
  | .arr xs => xs.toList
  | _ => []

/-- A W2 set whose every reading is an asserted formula: W2 validates it itself (`validate_reading_sets`). -/
def ordinary (item : Json) : Bool :=
  (readingsOf item).all fun r => isObj r && r.getObjValD "kind" == .str "asserted" &&
    match r.getObjValD "content" with
    | .arr _ => true
    | _ => false

/-- A speech set's readings (Python's `_reading_sets` loop): the W2 schema, kinds, structured content of its kind,
the admission record and its distinguishing-model ids. Contents are checked as candidates by the core. -/
def speechReadings (item : Json) (readings : List Json) : Except String Unit := do
  if readings.any (!isObj ·) then throw "invalid reading"
  if item.getObjValD "status" == .str "authored" &&
      (readings.length != 1 || !(((item.getObjValD "signature").getStr?).toOption.any token)) then
    throw "authored reading needs one signed choice"
  if item.getObjValD "status" == .str "open" && (item.getObjVal? "signature").isOk then
    throw "open reading set cannot have an author signature"
  let ids := readings.map fun r => ((r.getObjValD "id").getStr?).toOption.getD ""
  unless ids.all token do throw "invalid reading"
  let mut seen : List String := []
  for r in readings do
    let keys := keysOf r
    let id := ((r.getObjValD "id").getStr?).toOption.getD ""
    unless keys.length == 5 && ["id", "kind", "meaning_id", "content", "admission"].all keys.contains &&
        !seen.contains id && (((r.getObjValD "meaning_id").getStr?).toOption.any token) do
      throw "invalid reading"
    seen := id :: seen
    let kind := r.getObjValD "kind"
    unless kind == .str "binding" do
      let _ ← VE.Route.Admission.decodeKind 16 kind
    match fields (r.getObjValD "content") with
    | .ok [(tag, _)] => unless Wire.contentKindOk kind tag do throw "invalid speech reading content"
    | _ => throw "invalid speech reading content"
    let admission := r.getObjValD "admission"
    let akeys := keysOf admission
    let why := ((admission.getObjValD "why").getStr?).toOption.getD ""
    unless akeys.length == 3 && ["who", "why", "distinguishing_models"].all akeys.contains &&
        (((admission.getObjValD "who").getStr?).toOption.any token) && !why.isEmpty &&
        isObj (admission.getObjValD "distinguishing_models") do
      throw "invalid reading admission"
    let models := (fields (admission.getObjValD "distinguishing_models")).toOption.getD []
    let others := ids.filter (· != id)
    unless models.length == others.eraseDups.length && others.all (fun o => (models.map Prod.fst).contains o) do
      throw "each other reading needs a distinguishing model id"
    unless models.all (fun (_, m) => (m.getStr?.toOption.any token)) do throw "invalid distinguishing model id"
  let referenced := (readings.flatMap fun r =>
    ((fields ((r.getObjValD "admission").getObjValD "distinguishing_models")).toOption.getD []).filterMap
      fun (_, m) => m.getStr?.toOption).eraseDups
  let supplied ← match item.getObjVal? "models" with
    | .ok (.obj kvs) => pure (kvs.toList.map Prod.fst)
    | .ok _ => throw "distinguishing models must be supplied by id"
    | .error _ => pure []
  unless supplied.length == referenced.length && referenced.all supplied.contains do
    throw "distinguishing models must be supplied by id"
  match item.getObjVal? "rejected_history" with
  | .ok (.arr _) | .error _ => pure ()
  | .ok _ => throw "invalid rejected reading history"

def setKeys : List String := ["id", "unit", "version", "status", "readings"]
def setOptional : List String := ["signature", "rejected_history", "models"]

/-- Python's `_reading_sets`: the shape of every set, W2's validation of the formula-only sets, then each speech set
against the versions and owners seen so far. The environment is the document's as written (before bindings). -/
def readingSets (se : Wire.SpeechEnvironment) (envId : String) (unitIds : List String) (j : Json) :
    Except String (List SetInfo) := do
  let items ← match j with
    | .arr xs => pure xs.toList
    | _ => throw "reading_sets must be a list"
  if items.any fun i => !isObj i || !(match i.getObjValD "readings" with | .arr _ => true | _ => false) then
    throw "invalid reading set"
  if items.any fun i => !(i.getObjValD "unit" matches .str _) || !(i.getObjValD "version").getInt?.isOk ||
      !(i.getObjValD "status" == .str "open" || i.getObjValD "status" == .str "authored") then
    throw Wire.readingSetsError
  -- A formula candidate's structure as the core reads it, before any set is validated.
  for i in items do
    for r in readingsOf i do
      if let .arr _ := r.getObjValD "content" then
        let _ ← VE.Bridge.decodeFormula 64 (r.getObjValD "content")
  let plain := items.filter ordinary
  let _ ← Loader.compileSets se.ne.rv se.profiles envId unitIds (.arr plain.toArray)
  let info := fun (i : Json) => (SetInfo.mk (((i.getObjValD "id").getStr?).toOption.getD "")
    (((i.getObjValD "unit").getStr?).toOption.getD "") (((i.getObjValD "version").getNat?).toOption.getD 0)
    (i.getObjValD "status" == .str "authored") (readingsOf i))
  let mut sets : List SetInfo := plain.map info
  for item in items do
    if ordinary item then continue
    let keys := keysOf item
    unless setKeys.all keys.contains && keys.all (setKeys ++ setOptional).contains do throw "invalid reading set"
    let s := info item
    unless token s.id && 1 ≤ s.version && !sets.any (fun o => o.id == s.id && o.version == s.version) do
      throw "invalid or duplicate reading set version"
    unless unitIds.contains s.unit do throw "invalid reading set unit or status"
    -- `owners` and `units` keep the last set seen for an id or a unit, as Python's dictionaries do.
    let owner := (sets.reverse.find? (·.id == s.id)).map (·.unit)
    let holder := (sets.reverse.find? (·.unit == s.unit)).map (·.id)
    if owner.any (· != s.unit) || holder.any (· != s.id) then
      throw "one reading set per source unit; versions must keep their unit"
    sets := sets ++ [s]
    unless 1 ≤ s.readings.length && s.readings.length ≤ 64 do throw "reading sets hold 1 to 64 readings"
    speechReadings item s.readings
  -- The validated sets in document order.
  pure (items.map info)

/-! ## Statuses and the coverage projection (6) -/

/-- The meaning's status word: `specified` or its one key (a meaning `Loader.meaningStatus` accepted). -/
def meaningWord (meaning : Json) : String :=
  match meaning with
  | .str s => s
  | .obj kvs => (kvs.toList.head?.map Prod.fst).getD ""
  | _ => ""

/-- W2's status of a unit (`Loader.w2Status`), its latest reading set deciding when it has one. -/
def unitStatus (u : SourceUnit) (latest : Option SetInfo) : String :=
  match latest with
  | some s => Loader.w2SetStatus s.authored (s.readings.all fun c => c.getObjValD "kind" == .str "asserted")
  | none => Loader.w2Status u.content.isSome (meaningWord u.meaning)

/-- Section 6's precedence U, R, O, C, else L, over the unit and its latest reading set. -/
def unitClass (u : SourceUnit) (latest : Option SetInfo) : String :=
  if meaningWord u.meaning == "unformalised" then "U"
  else match latest with
    | some s =>
      if !s.authored then "R"
      else if s.readings.all (fun c => c.getObjValD "kind" == .str "asserted") then "C" else "R"
    | none =>
      if meaningWord u.meaning == "open" then "O"
      else if u.content.isSome && meaningWord u.meaning == "specified" then "C" else "L"

/-- The fixed mapping of 6: CHECKED ↦ C; OPEN ↦ R, O or U; LABELLED ↦ L; UNFORMALISED ↦ U. -/
def reconciles (status cls : String) : Bool :=
  match status with
  | "CHECKED" => cls == "C"
  | "OPEN" => ["R", "O", "U"].contains cls
  | "LABELLED" => cls == "L"
  | "UNFORMALISED" => cls == "U"
  | _ => false

/-- One unit's coverage row. -/
structure Row where
  id : String
  bytes : Nat
  status : String
  cls : String

/-- Byte totals per key, in first-seen order. -/
def totals (key : Row → String) (rows : List Row) : List (String × Nat) :=
  rows.foldl (fun acc r => match acc.find? (·.1 == key r) with
    | some _ => acc.map fun (k, n) => if k == key r then (k, n + r.bytes) else (k, n)
    | none => acc ++ [(key r, r.bytes)]) []

def sumBytes (xs : List (String × Nat)) : Nat := (xs.map Prod.snd).sum

/-- A checked coverage projection: every row reconciles and both tables total the source bytes. -/
structure Coverage (sourceBytes : Nat) where
  rows : List Row
  reconciled : rows.all (fun r => reconciles r.status r.cls) = true
  byClass : sumBytes (totals Row.cls rows) = sourceBytes
  byStatus : sumBytes (totals Row.status rows) = sourceBytes

def coverage (sourceBytes : Nat) (units : List SourceUnit) (sets : List SetInfo) :
    Except String (Coverage sourceBytes) := do
  let rows := units.map fun u =>
    let latest := latestOf sets u.id
    (Row.mk u.id (u.span.2 - u.span.1) (unitStatus u latest) (unitClass u latest))
  for r in rows do
    unless reconciles r.status r.cls do throw s!"coverage reconciliation: {r.id} is {r.status} but class {r.cls}"
  if h : rows.all (fun r => reconciles r.status r.cls) = true then
    if hc : sumBytes (totals Row.cls rows) = sourceBytes then
      if hs : sumBytes (totals Row.status rows) = sourceBytes then pure ⟨rows, h, hc, hs⟩
      else throw "coverage: the status table does not total the source bytes"
    else throw "coverage: the class table does not total the source bytes"
  else throw "coverage reconciliation"

/-! ## The derived open term of a reading question (4.6) -/

/-- The regenerated `intended-reading.<u>` declaration (Python's `_expected_open_term`). -/
def expectedOpenTerm (scope : Scope) (q : Question) : Except String Json := do
  let some (_, by_) := scope.addressee | throw "UnboundSlot: you"
  let (set, version) := q.readingSet.getD ("", 0)
  let wording := s!"a candidate of {set} at version {version} by {by_}"
  pure (Json.mkObj [("name", .str s!"intended-reading.{q.unit}"), ("arguments", toJson [set]),
    ("version", toJson version), ("decided_by", .str by_), ("jurisdiction", .str scope.task),
    ("necessary", .arr #[]), ("sufficient", .arr #[]), ("precedents", .arr #[]),
    ("factors", toJson [s!"necessary: at least one nomination of {wording}",
      s!"sufficient: exactly one nomination of {wording}"])])

/-- Every reading question, asked or a reading question candidate of a unit's latest set version, carries its
derived open term among the declared ones. -/
def checkOpenTerms (dec : Wire.Decoded) (sets : List SetInfo) (terms : List Json) : Except String Unit := do
  let candidates := sets.filter (fun s => (latestOf sets s.unit).any (·.version == s.version)) |>.flatMap fun s =>
    s.readings.filterMap fun r => match fields (r.getObjValD "content") with
      | .ok [("question", q)] => (Wire.decodeQuestion s.unit q).toOption
      | _ => none
  for q in dec.D.questions ++ candidates do
    if q.mode == .reading then
      let expected ← expectedOpenTerm dec.D.scope q
      unless terms.any (fun t => t.getObjValD "name" == expected.getObjValD "name" && t == expected) do
        throw s!"InvalidInput: invalid question fields for {q.unit}"

/-! ## Records (3.3) -/

/-- An answer record replayed: the question, the record's line (5.3) and, for a certificate, its acceptance. -/
structure AnswerRecord (dec : Wire.Decoded) where
  q : Question
  mem : q ∈ dec.D.questions
  replay : Run.AnswerReplay dec.D q
  accepted : replay.accepted = true
  /-- the answer the record states -/
  stated : Answer

/-- A `follows` judgment or a proof task's compliance certificate replayed over `Π_q`. -/
structure QueryRecord (dec : Wire.Decoded) where
  unit : String
  qr : Query
  mem : qr ∈ dec.D.queries
  cert : VE.Tableau.Certificate
  accepted : VE.Tableau.checkCertificate (En dec.D) (queryPremises dec.D qr) qr.target cert = true
  status : Run.PremiseStatus dec.D (queryPremises dec.D qr)

/-- A recorded nomination (4.6): candidate `index` of the bound set version, by `agent`, on testimony. -/
structure Nomination where
  question : String
  set : String
  version : Nat
  index : Nat
  reading : String
  agent : String

/-- The premise-status evidence the case supplies for record `i` of `list` (5.3): `{"model"}` or
`{"inconsistent"}` for the exact list its certificate is checked over, found by an untrusted search outside the
document (`case.premise_status.<list>.<i>`); none is UNKNOWN. The document's records keep W2's schema. -/
def statusEvidence (evidence : Json) (list : String) (i : Nat) : Json :=
  match (evidence.getObjValD list).getObjVal? (toString i) with
  | .ok s => Json.mkObj [("premise_status", s)]
  | .error _ => Json.mkObj []

def recordKeys : List String := ["question", "by", "support", "evidence"]
def recordOptional : List String := ["answer", "conditional", "judgment"]
def nominationKeys : List String := ["question", "by", "support", "nominate"]

/-- The model id of a completed model (Python's `FiniteModel.model_id`): the digest of its normalized tables under
the document's environment identity. -/
def completedModelId (dec : Wire.Decoded) (j : Json) : String :=
  let D := dec.D
  match VE.Bridge.decodeModelData (VE.Norms.Replay.baseModelVocabulary dec.se.ne (policy D)) j,
      VE.Route.Wire.environmentId dec.se.profiles dec.se.canonical with
  | .ok d₀, .ok envId =>
    let d := Run.computeRegulated (policy D).T d₀
    let wire := Json.mkObj [("domains", Json.mkObj (d.domains.map fun (s, xs) => (s, toJson xs))),
      ("constants", Json.mkObj (d.constants.map fun (c, e) => (c, Json.str e.2))),
      ("relations", Json.mkObj (d.relations.map fun (p, rows) =>
        (p, Json.arr (rows.map fun row => Json.arr (row.map (Json.str ·.2)).toArray).toArray)))]
    (Loader.modelId dec.se.profiles envId wire).toOption.getD ""
  | _, _ => ""

/-- One answer record of a polar or which question (Python's `_answer_records`, in its order): the answer's shape
for the mode, the support and evidence kinds, the stated token, then the evidence replayed for exactly that token;
evidence that does not establish it is `AnswerMismatch`. -/
def answerRecord (dec : Wire.Decoded) (q : Question) (hq : q ∈ dec.D.questions) (record status : Json) :
    Except String (AnswerRecord dec) := do
  let D := dec.D
  let mismatch := s!"AnswerMismatch: {q.unit}"
  if (record.getObjVal? "answer").isOk == false || (record.getObjVal? "judgment").isOk then throw mismatch
  let raw := record.getObjValD "answer"
  let outside := s!"AnswerOutsideDomain: {q.unit}, {raw.compress}"
  let shapeOk : Bool := match q.mode, raw with
    | .whichOne, .obj _ => keysOf raw == ["one"]
    | .whichAll, .obj _ => keysOf raw == ["all"] &&
        (raw.getObjValD "all" matches .arr _)
    | .polar, _ => true
    | _, _ => false
  unless shapeOk do throw outside
  let ev := record.getObjValD "evidence"
  let path ← match record.getObjValD "support", keysOf ev with
    | .str "certificate", ["certificate"] => pure true
    | .str "model", ["model"] => pure false
    | _, _ => throw mismatch
  let a ← match Wire.decodeAnswer raw with
    | .ok a => pure a
    | .error _ => throw outside
  let ⟨φ, hφ⟩ ← match Run.tokenFormula D q a with
    | .ok r => pure r
    | .error _ => throw outside
  let replay ← if path then
      let cj := ev.getObjValD "certificate"
      if record.getObjValD "conditional" == .bool true then do
        let checked := premises D ++ [presupposition D q]
        let some c := (Run.boundCertificate dec checked φ cj).toOption | throw mismatch
        let s ← Run.decodePremiseStatus dec checked "m" status
        pure (Run.AnswerReplay.conditional a φ hφ c s)
      else do
        let some c := (Run.boundCertificate dec (premises D) (.and (presupposition D q) φ) cj).toOption |
          throw mismatch
        let s ← Run.decodePremiseStatus dec (premises D) "m" status
        pure (Run.AnswerReplay.certificate a φ hφ c s)
    else do
      let mj := ev.getObjValD "model"
      let m ← Run.decodeCheckedModel dec (premises D) mj
      -- Python's `evaluate_answer_model`: a false presupposition is reported; a stated answer the model refutes
      -- is a mismatch.
      if (presupposition D q).eval m.M [] && !φ.eval m.M [] then throw mismatch
      pure (Run.AnswerReplay.model (completedModelId dec mj) m)
  if h : replay.accepted = true then pure ⟨q, hq, replay, h, a⟩ else throw mismatch

/-- A `follows` judgment record, or a proof task's compliance certificate: a certificate for exactly
`Π_q ⊢ target`; one not accepted is `QueryMismatch: <q>`. -/
def queryRecord (dec : Wire.Decoded) (unit qid : String) (cj status : Json) : Except String (QueryRecord dec) := do
  let mismatch := s!"QueryMismatch: {qid}"
  let ⟨qr, hq⟩ ← match Run.findQuery dec.D qid with
    | .ok r => pure r
    | .error _ => throw mismatch
  let some c := (Run.boundCertificate dec (queryPremises dec.D qr) qr.target cj).toOption | throw mismatch
  let s ← Run.decodePremiseStatus dec (queryPremises dec.D qr) "m" status
  if h : VE.Tableau.checkCertificate (En dec.D) (queryPremises dec.D qr) qr.target c = true then
    pure ⟨unit, qr, hq, c, h, s⟩
  else throw mismatch

/-- The answer records, in order: answers, `follows` judgments and nominations. -/
structure Answers (dec : Wire.Decoded) where
  answers : List (AnswerRecord dec)
  judgments : List (QueryRecord dec)
  nominations : List Nomination

def answerRecords (dec : Wire.Decoded) (sets : List SetInfo) (evidence j : Json) :
    Except String (Answers dec) := do
  let records ← match j with
    | .arr xs => pure xs.toList
    | _ => throw "InvalidInput: answers"
  let mut out : Answers dec := ⟨[], [], []⟩
  for (record, index) in records.zipIdx do
    let status := statusEvidence evidence "answers" index
    let keys := keysOf record
    let bad := "InvalidInput: answer record"
    unless isObj record do throw bad
    if keys.contains "nominate" then
      -- 3.3: a nomination names a candidate index of the bound set at the bound version, on testimony.
      unless keys.length == 4 && nominationKeys.all keys.contains do throw bad
      let some agent := ((record.getObjValD "by").getStr?).toOption | throw bad
      unless token agent && record.getObjValD "support" == .str "testimony" do throw bad
      let some uid := ((record.getObjValD "question").getStr?).toOption | throw bad
      let some q := dec.D.questions.find? (·.unit == uid) | throw s!"AnswerMismatch: {uid}"
      unless q.mode == .reading do throw s!"AnswerMismatch: {uid}"
      let (set, version) := q.readingSet.getD ("", 0)
      let outside := s!"NominationOutsideSet: {uid}"
      let some i := ((record.getObjValD "nominate").getNat?).toOption | throw outside
      let some s := sets.find? (fun s => s.id == set && s.version == version) | throw outside
      let some r := s.readings[i]? | throw outside
      out := { out with nominations := out.nominations ++
        [⟨uid, set, version, i, ((r.getObjValD "id").getStr?).toOption.getD "", agent⟩] }
      continue
    unless recordKeys.all keys.contains && keys.all (recordKeys ++ recordOptional).contains do throw bad
    if let .ok flag := record.getObjVal? "conditional" then
      unless flag matches .bool _ do throw "InvalidInput: conditional"
    unless (((record.getObjValD "by").getStr?).toOption.any token) do throw bad
    let some uid := ((record.getObjValD "question").getStr?).toOption | throw bad
    let ⟨q, hq⟩ ← match Run.findQuestion dec.D uid with
      | .ok r => pure r
      | .error _ => throw s!"AnswerMismatch: {uid}"
    unless isObj (record.getObjValD "evidence") do throw s!"AnswerMismatch: {uid}"
    match q.mode with
    | .follows =>
      let ev := record.getObjValD "evidence"
      unless record.getObjValD "judgment" == .str "follows" && record.getObjValD "support" == .str "certificate" &&
          isObj ev && keysOf ev == ["certificate"] do
        throw "InvalidInput: judgment"
      let r ← queryRecord dec uid (q.query.getD "") (ev.getObjValD "certificate") status
      out := { out with judgments := out.judgments ++ [r] }
    | .reading => throw s!"NominationOutsideSet: {uid}"
    | _ =>
      let r ← answerRecord dec q hq record status
      out := { out with answers := out.answers ++ [r] }
  pure out

/-- The compliance records (Python's `_compliance_records`): a proof task's certificate for its pinned query. -/
def complianceRecords (dec : Wire.Decoded) (evidence j : Json) : Except String (List (QueryRecord dec)) := do
  let records ← match j with
    | .arr xs => pure xs.toList
    | _ => throw "InvalidInput: compliance"
  records.zipIdx.mapM fun (record, index) => do
    let bad := "InvalidInput: compliance record"
    let keys := keysOf record
    unless isObj record && keys.length == 2 && ["command", "evidence"].all keys.contains do throw bad
    let some uid := ((record.getObjValD "command").getStr?).toOption | throw bad
    let some c := dec.D.commands.find? (·.unit == uid) | throw bad
    let ev := record.getObjValD "evidence"
    unless isObj ev do throw bad
    let qid : Option String := match dec.D.E.predicates c.act with
      | some (_ :: ss) => ((ss.zip c.args).find? (·.1 == "query")).map Prod.snd
      | _ => none
    let some qid := qid | throw s!"QueryMismatch: {uid}"
    unless isObj ev && keysOf ev == ["certificate"] do throw s!"QueryMismatch: {uid}"
    queryRecord dec uid qid (ev.getObjValD "certificate") (statusEvidence evidence "compliance" index)

/-! ## The wrapper -/

/-- The decoded source (8.5): W2's identity payload retained verbatim, the units, the validated reading sets, the
semantic core, the coverage projection and the replayed records. -/
structure SpeechSource where
  payload : Json
  metadata : Json
  source : String
  fences : List (String × String)
  metadata_eq : metadata = payload.getObjValD "metadata"
  source_eq : source = Loader.sourceOf payload
  units : List SourceUnit
  sets : List SetInfo
  openTerms : List Json
  dec : Wire.Decoded
  cov : Coverage source.utf8ByteSize
  answers : Answers dec
  compliance : List (QueryRecord dec)

/-- W2's identity payload and the `ve-document@2` document id (3.5), from the retained payload alone. -/
def SpeechSource.identityPayload (src : SpeechSource) : Json :=
  Json.mkObj [("metadata", Loader.identityMetadata src.metadata), ("source", .str src.source),
    ("fences", src.payload.getObjValD "fences")]

def SpeechSource.documentId (src : SpeechSource) : Except String String :=
  VE.CertificateWire.digest "ve-document@2\n" src.identityPayload

/-- The unit object the core reads: the unit's own fields, its wording as `source` for an instruction or question
and for a unit with a signed choice (3.2). -/
def coreUnit (u : SourceUnit) (chosen : Bool) : Json :=
  let kept := ((fields u.raw).toOption.getD []).filter fun (k, _) =>
    ["id", "span", "kind", "meaning", "support", "content", "meaning_id"].contains k
  Json.mkObj (kept ++ if chosen || u.kind == .str "instruction" || u.kind == .str "question" then
    [("source", .str u.wording)] else [])

def decodeSpeechSource (payload evidence : Json) : Except String { src : SpeechSource // src.payload = payload } := do
  let fm := payload.getObjValD "metadata"
  let source := Loader.sourceOf payload
  let fences := Loader.fencesOf payload
  match fm with
  | .obj kvs =>
    unless fm.getObjValD "format" == .str "ve-document@2" && kvs.toList.all (allowedMetadata.contains ·.1) do
      throw "unsupported document format"
  | _ => throw "unsupported document format"
  let environment ← match fm.getObjValD "environment" with
    | e@(.obj _) => pure e
    | _ => throw "document needs an embedded environment"
  let se ← Wire.decodeSpeechEnvironmentFull environment
  let envId ← VE.Route.Wire.environmentId se.profiles se.canonical
  if source.isEmpty then throw "document source is empty"
  let raw ← match fm.getObjValD "units" with
    | .arr xs => if xs.isEmpty then throw "document needs units" else pure xs.toList
    | _ => throw "document needs units"
  let units ← readUnits source fences raw
  for (_, text) in fences do
    unless Wire.asciiWording text do throw Wire.nonAsciiWording
  let terms := Loader.optionalList fm "open_terms"
  let openNames ← Loader.openTermNames se.ne.rv terms
  for u in units do
    let _ ← Loader.meaningStatus openNames u.meaning
  let ids := units.map (·.id)
  let sets ← readingSets se envId ids (Loader.optionalList fm "reading_sets")
  let _ ← Loader.narrowingIds (sets.map fun s => (s.id, s.version,
    s.readings.map fun r => ((r.getObjValD "id").getStr?).toOption.getD "")) ids (Loader.optionalList fm "narrowings")
  let chosen := fun (u : SourceUnit) => (latestOf sets u.id).any (·.authored)
  -- An English fence needs the speech parser (Python's English layer); a fence a signed choice replaces does not.
  for u in units do
    if let some c := u.content then
      if (c.getObjVal? "fence").isOk && !chosen u then throw (Loader.notImplemented "fenced English content")
  let document := Json.mkObj ([("units", Json.arr (units.map fun u => coreUnit u (chosen u)).toArray)] ++
    (match fm.getObjVal? "queries" with
     | .ok q => [("queries", q)]
     | .error _ => []) ++
    (match fm.getObjVal? "reading_sets" with
     | .ok r => [("reading_sets", r)]
     | .error _ => []))
  let dec ← Run.checkedDocument environment document
  for u in units do
    if let some s := u.explicit then
      unless s == .str (unitStatus u (latestOf sets u.id)) do
        throw "unit status contradicts content, meaning, or active reading set"
  checkOpenTerms dec sets (match terms with | .arr ts => ts.toList | _ => [])
  unless fm.getObjValD "weights" matches .arr _ || !(fm.getObjVal? "weights").isOk do
    throw "invalid removable reading weights"
  let answers ← answerRecords dec sets evidence (Loader.optionalList fm "answers")
  let compliance ← complianceRecords dec evidence (Loader.optionalList fm "compliance")
  let cov ← coverage source.utf8ByteSize units sets
  pure ⟨⟨payload, fm, source, fences, rfl, rfl, units, sets, (match terms with | .arr ts => ts.toList | _ => []),
    dec, cov, answers, compliance⟩, rfl⟩

/-! ## The report -/

def premiseText {D : SpeechDoc} {checked : List VE.Formula} (s : Run.PremiseStatus D checked) : String := s.text

def answerJson {dec : Wire.Decoded} (r : AnswerRecord dec) : Json :=
  let (status, evidence) : String × String := match r.replay with
    | .certificate .. => ("supported", "certificate")
    | .conditional .. => ("supported given presupposition", "certificate")
    | .presuppositionFailed .. => ("PRESUPPOSITION-FAILED", "certificate")
    | .model _ m => (if (presupposition dec.D r.q).eval m.M [] then "evaluated" else "PRESUPPOSITION-FAILED", "model")
  Json.mkObj [("question", .str r.q.unit), ("status", .str status), ("evidence", .str evidence),
    ("answer", Wire.encodeAnswer r.stated), ("line", .str r.replay.line)]

def queryJson {dec : Wire.Decoded} (key : String) (r : QueryRecord dec) : Json :=
  Json.mkObj [(key, .str r.unit), ("query", .str r.qr.id),
    ("line", .str s!"{if key == "command" then "certificate: query " ++ r.qr.id ++ " (" else "follows (certificate; "}premises: {r.status.text})")]

/-- The nomination line of each asked reading question (5.3). -/
def nominationLines (src : SpeechSource) : List Json :=
  src.dec.D.questions.filter (·.mode == .reading) |>.map fun q =>
    let mine := src.answers.nominations.filter (·.question == q.unit)
    let line := match (mine.map (·.index)).eraseDups, mine.head? with
      | [i], some n => s!"{i} by {n.agent} (testimony)"
      | [], _ => "CLARIFICATION-OPEN (none)"
      | _, _ => "CLARIFICATION-OPEN (multiple)"
    Json.mkObj ([("question", .str q.unit), ("line", .str line)] ++
      match (mine.map (·.index)).eraseDups, mine.head? with
      | [_], some n => [("narrowing", Json.mkObj [("set", .str n.set), ("version", toJson n.version),
          ("keeps", toJson [n.reading]), ("by", .str n.agent), ("reason_spans", toJson [q.unit]),
          ("support", .str "testimony")])]
      | _, _ => [])

/-- The status text of 5.5 (the policy line needs the conflict check, `speech-conflict`). -/
def statusText (src : SpeechSource) : List String :=
  let D := src.dec.D
  let dormant := src.dec.units.filter (fun u => match u.role, Wire.activeCommand u with
    | .command _, none => true
    | _, _ => false)
  let asked := D.questions.filter (·.mode != .reading)
  let byCert := asked.filter fun q => src.answers.answers.any (fun r => r.q.unit == q.unit &&
      (match r.replay with | .certificate .. | .conditional .. => true | _ => false)) ||
    src.answers.judgments.any (·.unit == q.unit)
  let inModel := asked.filter fun q => !byCert.contains q && src.answers.answers.any (fun r => r.q.unit == q.unit &&
      (match r.replay with | .model _ m => (presupposition D r.q).eval m.M [] | _ => false))
  let failed := asked.filter fun q => !byCert.contains q && !inModel.contains q &&
    src.answers.answers.any (·.q.unit == q.unit)
  let unanswered := asked.length - byCert.length - inModel.length - failed.length
  let you := match D.scope.addressee with
    | some (_, c) => s!"you = {c}"
    | none => "you unbound"
  ["policy: UNKNOWN (no conflict evidence; see speech-conflict)",
   s!"scope: task {D.scope.task}; {you}; {D.scope.definites.length} definite bindings; " ++
     s!"{D.commands.length} commands active, {dormant.length} dormant",
   s!"questions: {byCert.length + inModel.length} answered ({byCert.length} by certificate, " ++
     s!"{inModel.length} in a model), {failed.length} presupposition failures, 0 unknown, {unanswered} unanswered",
   s!"compliance: {(src.compliance.map (·.unit)).eraseDups.length} of {D.commands.length} commands with evidence " ++
     s!"(0 external, {src.compliance.length} certificates)"]

def countsJson (xs : List (String × Nat)) : Json := Json.mkObj (xs.map fun (k, n) => (k, toJson n))

def report (src : SpeechSource) : List (String × Json) :=
  let dec := src.dec
  let latest := src.sets.filter fun s => (latestOf src.sets s.unit).any (·.version == s.version)
  [("document_id", .str (src.documentId.toOption.getD "")),
   ("source_id", .str (Loader.sourceId dec.se.profiles src.source))] ++ Run.elaborated dec ++
  [("units", Json.arr (src.cov.rows.map fun r => Json.mkObj ([("id", .str r.id), ("bytes", toJson r.bytes),
      ("status", .str r.status), ("class", .str r.cls)] ++
      match (src.units.find? (·.id == r.id)).bind (·.parent) with
      | some p => [("parent", .str p)]
      | none => [])).toArray),
   ("coverage", Json.mkObj [("bytes_by_class", countsJson (totals Row.cls src.cov.rows)),
      ("bytes_by_status", countsJson (totals Row.status src.cov.rows)),
      ("residual", Json.mkObj [("open_terms", toJson src.openTerms.length),
        ("unresolved_sets", toJson (latest.filter (!·.authored)).length)])]),
   ("answers", Json.arr ((src.answers.answers.map answerJson) ++
      (src.answers.judgments.map (queryJson "question"))).toArray),
   ("nominations", Json.arr (nominationLines src).toArray),
   ("compliance", Json.arr (src.compliance.map (queryJson "command")).toArray),
   ("status_text", toJson (statusText src))]

/-! ## The entry point -/

def runCase (j : Json) : Except String Json := do
  if (VE.Route.Run.caseKind j).toOption == some "speech-source" then
    let id ← stringField j "id"
    let src ← decodeSpeechSource (← j.getObjVal? "document") (j.getObjValD "premise_status")
    return VE.Route.Wire.ok id (report src.1)
  Run.runCase j

def runCaseReported (j : Json) : Json :=
  if (VE.Route.Run.caseKind j).toOption == some "speech-source" then
    match runCase j with
    | .ok result => result
    | .error message => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"), ("error", .str message)]
  else Run.runCaseReported j

def main (paths : List String) : IO UInt32 := do
  let input ← match paths with
    | [] | ["-"] => (← IO.getStdin).readToEnd
    | [path] => IO.FS.readFile path
    | _ =>
      (← IO.getStderr).putStrLn "usage: ve_speech_acts_route [cases.json|-]"
      return 2
  match VE.JsonInput.parseCases input with
  | .error message =>
    (← IO.getStderr).putStrLn message
    return 2
  | .ok cases =>
    let results := cases.mapIdx fun index c => match c with
      | .ok j => runCaseReported j
      | .error message => Json.mkObj [("status", .str "error"),
          ("case_index", toJson index), ("error", .str message)]
    (← IO.getStdout).putStrLn (Json.arr results).compress
    return if results.any (fun r => r.getObjValD "status" == .str "error") then 1 else 0

/-! ## Theorems -/

/-- The wrapper retains W2's identity payload verbatim: its metadata and source are the payload's, so the document id
of 3.5 is recomputed from the payload alone. -/
theorem source_retained (p e : Json) (src : { src : SpeechSource // src.payload = p })
    (_ : decodeSpeechSource p e = .ok src) :
    src.1.metadata = p.getObjValD "metadata" ∧ src.1.source = Loader.sourceOf p ∧
    src.1.documentId = VE.CertificateWire.digest "ve-document@2\n" (Json.mkObj [
      ("metadata", Loader.identityMetadata (p.getObjValD "metadata")), ("source", .str (Loader.sourceOf p)),
      ("fences", p.getObjValD "fences")]) := by
  obtain ⟨src, rfl⟩ := src
  exact ⟨src.metadata_eq, src.source_eq, by
    simp only [SpeechSource.documentId, SpeechSource.identityPayload, src.metadata_eq, src.source_eq]⟩

/-- The coverage projection (6) is a partition: every unit's class is the one its W2 status maps to, and both the
class table and the status table total the source byte count. -/
theorem coverage_partition (src : SpeechSource) :
    src.cov.rows.all (fun r => reconciles r.status r.cls) = true ∧
    sumBytes (totals Row.cls src.cov.rows) = src.source.utf8ByteSize ∧
    sumBytes (totals Row.status src.cov.rows) = src.source.utf8ByteSize :=
  ⟨src.cov.reconciled, src.cov.byClass, src.cov.byStatus⟩

/-- Every answer record of a decoded source is established by its evidence (3.3, 5.3): a certificate record makes its
stated answer an answer in every admissible model of the regenerated premises (conditionally on the presupposition
for a conditional record); a model record's answers are exactly `AnswersAt` in that model. -/
theorem answers_sound (src : SpeechSource) (r : AnswerRecord src.dec) (_ : r ∈ src.answers.answers) :
    (∀ a φ hφ c s, r.replay = .certificate a φ hφ c s →
      ∀ S : VE.Structure.{u}, S.Admissible (En src.dec.D) → Sat S (premises src.dec.D) →
        AnswersAt src.dec.D r.q S a) ∧
    (∀ a φ hφ c s, r.replay = .conditional a φ hφ c s →
      ∀ S : VE.Structure.{u}, S.Admissible (En src.dec.D) → Sat S (premises src.dec.D) →
        (presupposition src.dec.D r.q).denote S [] → AnswersAt src.dec.D r.q S a) ∧
    (∀ id m, r.replay = .model id m →
      ∀ a, answerEval src.dec.D r.q m.M a = true ↔ AnswersAt src.dec.D r.q m.M.asStructure a) := by
  have hwf := src.dec.wf
  refine ⟨fun a φ hφ c s he => ?_, fun a φ hφ c s he => ?_,
    fun id m _ a => model_answers src.dec.D hwf r.q r.mem m.M m.valid m.background m.sat a⟩
  · have ha := r.accepted
    rw [he] at ha
    exact support_sound src.dec.D hwf r.q r.mem a φ hφ c ha
  · have ha := r.accepted
    rw [he] at ha
    exact support_conditional_sound src.dec.D hwf r.q r.mem a φ hφ c ha

/-- Every `follows` judgment and every proof task's compliance certificate of a decoded source is entailment of the
query's target by its pinned premises `Π_q` (`follows_sound`); the certificate adds no premise to the document. -/
theorem query_records_sound (src : SpeechSource) (r : QueryRecord src.dec)
    (_ : r ∈ src.answers.judgments ∨ r ∈ src.compliance) :
    VE.Entails.{u} (En src.dec.D) (queryPremises src.dec.D r.qr) r.qr.target :=
  follows_sound src.dec.D src.dec.wf r.qr r.mem r.cert r.accepted

end VE.SpeechActs.Source
