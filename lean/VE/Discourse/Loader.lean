import VE.Discourse.Manifest
import VE.Route.Run

/-! # Loading a `ve-document` text (docs/spec/discourse.md 3.1 to 3.3, document.md)

The discourse route reads the same bytes as the Python loader (`ve/document.py`): a
`ve-document@1` or `@2` text is JSON front matter between two `---` lines, then a body whose
lines outside ```` ```ve <unit> ```` fences are the source. `splitText` separates the three
parts exactly as `_split`/`_body` do; `loadFront` checks the front matter the way
`load_document` does, for the part of the format the Lean route implements, and translates it
into the W2 admission object (`_check_document`'s `admission` dictionary: units with their AST
content, the graph, lemmas, open-term names, the active all-assertion reading sets, narrowing
ids), the active reading sets with their statuses and reading ids, and each unit's W2 status.

What the Lean route does not implement is `NotImplemented: <feature>`, never a rejection of the
document (4.7: an import whose check cannot complete is `unconfirmed`): fenced English or
strict content, norm content, `MIXED` units, distinguishing models of reading sets, a document
without a claim graph, and JSON `null`, which the restricted parser does not read. Decoding, hashing and display remain named
trust boundaries (3.4). -/
namespace VE.Discourse.Loader
open Lean
open VE.Bridge (stringField strings fields)
open VE.Route.Admission (token)

def notImplemented (feature : String) : String := "NotImplemented: " ++ feature

def maxDocumentBytes : Nat := 4000000

/-- A split document text: the front matter, the source and the fences (unit id, text). -/
structure Split where
  front : Json
  source : String
  fences : List (String × String)

/-- Lines with their line breaks (`bytes.splitlines(keepends=True)` on `\n`). -/
def linesOf (s : String) : List String :=
  match (s.splitOn "\n").reverse with
  | [] => []
  | last :: rest => (rest.reverse.map (· ++ "\n")) ++ (if last.isEmpty then [] else [last])

/-- `_body`: the lines outside ```` ```ve <id> ```` fences are the source. -/
def bodyOf : List String → Except String (String × List (String × String))
  | [] => .ok ("", [])
  | l :: ls =>
    if l.startsWith "```ve " then
      let uid := (l.drop 6).trim
      match ls.findIdx? (fun x => x.trim == "```") with
      | none => .error "unclosed VE fence"
      | some k => do
        let (src, fs) ← bodyOf (ls.drop (k + 1))
        if !token uid || (fs.map Prod.fst).contains uid then throw "invalid or duplicate VE fence"
        pure (src, (uid, String.join (ls.take k)) :: fs)
    else do
      let (src, fs) ← bodyOf ls
      pure (l ++ src, fs)
termination_by xs => xs.length
decreasing_by all_goals simp_wf <;> omega

def formats : List String := ["ve-document@1", "ve-document@2"]

def allowedMetadata (format : String) : List String :=
  ["format", "environment", "units", "open_terms", "reading_sets", "narrowings", "weights", "graph", "lemmas"] ++
    (if format == "ve-document@2" then ["discourse"] else [])

/-- `_split`: front matter, body, fences. -/
def splitText (t : String) : Except String Split := do
  unless t.utf8ByteSize ≤ maxDocumentBytes do throw "document byte budget exceeded"
  unless t.startsWith "---\n" do throw "ve-document@1 needs JSON front matter"
  match (t.drop 4).splitOn "\n---\n" with
  | front :: rest@(_ :: _) =>
    let fm ← match VE.JsonInput.parse front with
      | .ok m => pure m
      | .error e => throw (if e.startsWith "ResourceLimit" then e else "invalid JSON front matter")
    let keys ← match fm with
      | .obj kvs => pure (kvs.toList.map Prod.fst)
      | _ => throw "unsupported document format"
    let format := (fm.getObjValD "format").getStr?.toOption.getD ""
    unless formats.contains format do throw "unsupported document format"
    unless keys.all (allowedMetadata format).contains do throw "unknown document metadata"
    let (source, fences) ← bodyOf (linesOf ("\n---\n".intercalate rest))
    pure ⟨fm, source, fences⟩
  | _ => throw "unclosed JSON front matter"

/-- The loaded document object the discourse route admits: the identity payload of
document.md (`metadata`, `source`, `fences`) and the sibling files an import may name. -/
def payload (s : Split) (files : Json) : Json :=
  Json.mkObj [("metadata", s.front), ("source", .str s.source),
    ("fences", Json.mkObj (s.fences.map fun (u, t) => (u, Json.str t))), ("files", files)]

/-- A payload object (as opposed to a W2 admission object). -/
def isPayload (j : Json) : Bool := (j.getObjVal? "metadata").toBool && !(j.getObjVal? "format").toBool

def metaOf (j : Json) : Json := j.getObjValD "metadata"
def sourceOf (j : Json) : String := (j.getObjValD "source").getStr?.toOption.getD ""
def filesOf (j : Json) : List (String × String) :=
  match j.getObjValD "files" with
  | .obj kvs => kvs.toList.filterMap fun (k, v) => v.getStr?.toOption.map (k, ·)
  | _ => []

/-- The front matter without removable weights. -/
def identityMetadata (m : Json) : Json :=
  match m with
  | .obj kvs => Json.mkObj (kvs.toList.filter fun (k, _) => k != "weights")
  | _ => m

/-- `document_id`: sha256(format "\n" canonical({"metadata", "source", "fences"})) (document.md,
discourse.md 3.3), the Python loader's identity. -/
def documentId (j : Json) : Except String String := do
  let format ← stringField (metaOf j) "format"
  VE.CertificateWire.digest (format ++ "\n") (Json.mkObj [("metadata", identityMetadata (metaOf j)),
    ("source", .str (sourceOf j)), ("fences", j.getObjValD "fences")])

/-- `source_id`: sha256("ve-source-<identity version>\n" + source) under the base profiles. -/
def sourceId (profiles : List String) (source : String) : String :=
  VE.CertificateWire.sha256 (("ve-source-" ++ VE.Route.Wire.identityVersion profiles ++ "\n" ++ source).toUTF8)

/-! ## The front matter -/

def supports : List String :=
  ["assumption", "certificate", "observation", "calculation", "statistical", "testimony", "adapter", "none"]

def statuses : List String := ["CHECKED", "OPEN", "LABELLED", "UNFORMALISED"]

/-- `_meaning`: the meaning status of a unit. -/
def meaningStatus (openNames : List String) (j : Json) : Except String String := do
  match j with
  | .str "specified" => pure "specified"
  | .obj _ =>
    match ← fields j with
    | [("contextual", .str d)] => if d.isEmpty then throw "invalid meaning status" else pure "contextual"
    | [("open", .arr xs)] => do
      let names ← xs.toList.mapM Json.getStr?
      unless !names.isEmpty && names.all openNames.contains do throw "invalid meaning status"
      pure "open"
    | [("unformalised", .str r)] => if token r then pure "unformalised" else throw "invalid meaning status"
    | _ => throw "invalid meaning status"
  | _ => throw "invalid meaning status"

/-- One compiled unit of the front matter. -/
structure Unit₀ where
  id : String
  span : Nat × Nat
  kind : Json
  content : Option VE.Formula
  status : String
  explicit : Option String

def spanOf (j : Json) : Except String (Nat × Nat) := do
  match (← j.getArr?).toList with
  | [a, b] => pure (← a.getNat?, ← b.getNat?)
  | _ => throw "unit spans must partition every source byte in order"

/-- The byte range `[a, b)` of the source is whole UTF-8 characters. -/
def cutsCharacter (source : String) (a b : Nat) : Bool :=
  (String.fromUTF8? (source.toUTF8.extract a b)).isNone

/-- `load_document`'s unit checks, in order, for one unit at byte `cursor`. -/
def compileUnit (rv : VE.Route.Wire.RouteVocabulary) (profiles : List String) (envId : String)
    (source : String) (openNames : List String) (cursor : Nat) (u : Json) : Except String Unit₀ := do
  let keys ← match u with
    | .obj kvs => pure (kvs.toList.map Prod.fst)
    | _ => throw "invalid unit schema"
  if (u.getObjValD "status").getStr?.toOption == some "MIXED" then throw (notImplemented "MIXED units")
  let required := ["id", "span", "kind", "meaning", "support"]
  unless required.all keys.contains && keys.all (required ++ ["content", "surface", "meaning_id", "status"]).contains do
    throw "invalid unit schema"
  let id ← stringField u "id"
  unless token id do throw "duplicate or invalid unit id"
  let (a, b) ← spanOf (← u.getObjVal? "span")
  unless a == cursor && cursor < b && b ≤ source.utf8ByteSize do
    throw "unit spans must partition every source byte in order"
  if cutsCharacter source a b then throw "unit span cuts a UTF-8 character"
  let kind ← u.getObjVal? "kind"
  let _ ← VE.Route.Admission.decodeKind 16 kind
  let meaning ← meaningStatus openNames (← u.getObjVal? "meaning")
  let support ← stringField u "support"
  unless supports.contains support do throw "invalid support"
  let data := profiles.contains "data@0"
  let (content, mid) ← match u.getObjVal? "content" with
    | .error _ => pure (none, none)
    | .ok c => match ← fields c with
      | [("ast", ast)] => do
        let f ← VE.Route.Wire.decodeClosed rv.environment ast data
        let mid ← VE.Route.Wire.meaningId profiles envId (VE.Route.Wire.encodeFormula f)
        pure (some f, some mid)
      | [("norm", _)] => throw (notImplemented "norm content")
      | [("fence", _)] => throw (notImplemented "fenced English or strict content")
      | _ => throw "unit content must bind one formula or norm"
  if meaning == "unformalised" && content.isSome then throw "unformalised unit cannot assert content"
  match kind with
  | .arr xs => if xs[0]? == some (.str "unformalised") && meaning != "unformalised" then
      throw "unformalised kind needs unformalised meaning"
  | _ => pure ()
  match u.getObjVal? "meaning_id" with
  | .ok m => if some (← m.getStr?) != mid then throw "unit meaning id does not match content"
  | .error _ => pure ()
  let explicit ← match u.getObjVal? "status" with
    | .ok s => do
      let s ← s.getStr?
      unless statuses.contains s do throw "invalid unit status"
      pure (some s)
    | .error _ => pure none
  let status := if content.isSome && meaning == "specified" then "CHECKED"
    else if meaning == "open" then "OPEN"
    else if meaning == "unformalised" then "UNFORMALISED" else "LABELLED"
  pure ⟨id, (a, b), kind, content, status, explicit⟩

def compileUnits (rv : VE.Route.Wire.RouteVocabulary) (profiles : List String) (envId : String)
    (source : String) (openNames : List String) : Nat → List Json → Except String (List Unit₀)
  | cursor, [] => if cursor == source.utf8ByteSize then .ok [] else .error "unit spans do not partition all source bytes"
  | cursor, u :: us => do
    let x ← compileUnit rv profiles envId source openNames cursor u
    let rest ← compileUnits rv profiles envId source openNames x.span.2 us
    if (rest.map Unit₀.id).contains x.id then throw "duplicate or invalid unit id"
    pure (x :: rest)

/-- `validate_open_terms`: the declared open-term names. -/
def openTermNames (rv : VE.Route.Wire.RouteVocabulary) (j : Json) : Except String (List String) := do
  let items ← match j with
    | .arr xs => pure xs.toList
    | _ => throw "open_terms must be a list"
  items.foldlM (fun seen item => do
    let keys ← match item with
      | .obj kvs => pure (kvs.toList.map Prod.fst)
      | _ => throw "invalid open-term schema"
    let schema := ["name", "arguments", "decided_by", "necessary", "sufficient", "factors", "precedents",
      "jurisdiction", "version"]
    unless keys.length == schema.length && schema.all keys.contains do throw "invalid open-term schema"
    let name ← stringField item "name"
    unless token name && !seen.contains name do throw "duplicate or invalid open term"
    let args ← strings (← item.getObjVal? "arguments")
    unless args.all token && args.eraseDups.length == args.length do throw "invalid open-term arguments"
    unless token (← stringField item "decided_by") && token (← stringField item "jurisdiction") do
      throw "open term needs a decision role and jurisdiction"
    let v ← (← item.getObjVal? "version").getNat?
    unless 1 ≤ v do throw "invalid open-term version"
    for field in ["necessary", "sufficient"] do
      let fs ← match ← item.getObjVal? field with
        | .arr xs => pure xs.toList
        | _ => throw s!"{field} must be a list"
      for f in fs do let _ ← VE.Bridge.decodeFormula 64 f; pure ()
    let factors ← strings (← item.getObjVal? "factors")
    let precedents ← strings (← item.getObjVal? "precedents")
    unless factors.all (!·.isEmpty) && precedents.all (!·.isEmpty) do
      throw "invalid open-term factors or precedents"
    pure (seen ++ [name])) []

/-! ## Distinguishing models (their identity is Python's `model_id`) -/

def sortedStrings (xs : List String) : List String := xs.mergeSort fun a b => decide (a ≤ b)

def tupleLe : List String → List String → Bool
  | [], _ => true
  | _ :: _, [] => false
  | a :: as, b :: bs => if a < b then true else if a == b then tupleLe as bs else false

/-- The normalized model of `model_id`: domains and relation tuples sorted. -/
def normalizedModel (m : Json) : Except String Json := do
  let ds ← (← fields (← m.getObjVal? "domains")).mapM fun (s, v) => do
    pure (s, Json.arr ((sortedStrings (← strings v)).map Json.str).toArray)
  let rs ← (← fields (← m.getObjVal? "relations")).mapM fun (p, v) => do
    let ts ← (← v.getArr?).toList.mapM strings
    pure (p, Json.arr ((ts.mergeSort tupleLe).map fun t => Json.arr (t.map Json.str).toArray).toArray)
  pure (Json.mkObj [("complete", .bool true), ("domains", Json.mkObj ds),
    ("constants", ← m.getObjVal? "constants"), ("relations", Json.mkObj rs)])

/-- `model_id`: the digest of the normalized model under the environment identity. -/
def modelId (profiles : List String) (envId : String) (m : Json) : Except String String := do
  VE.CertificateWire.digest ("ve-model-" ++ VE.Route.Wire.identityVersion profiles ++ "\n")
    (Json.mkObj [("environment_id", .str envId), ("model", ← normalizedModel m)])

/-- One reading of a reading set: its id, kind, content and admission record. -/
def compileReading (rv : VE.Route.Wire.RouteVocabulary) (profiles : List String) (envId : String)
    (ids : List String) (r : Json) : Except String (String × Bool × VE.Formula × List (String × String)) := do
  let keys ← match r with
    | .obj kvs => pure (kvs.toList.map Prod.fst)
    | _ => throw "invalid reading"
  let schema := ["id", "kind", "meaning_id", "content", "admission"]
  unless keys.length == schema.length && schema.all keys.contains do throw "invalid reading"
  let id ← stringField r "id"
  let kind ← r.getObjVal? "kind"
  let _ ← VE.Route.Admission.decodeKind 16 kind
  let mid ← stringField r "meaning_id"
  unless token mid do throw "invalid reading meaning id"
  let f ← VE.Route.Wire.decodeClosed rv.environment (← r.getObjVal? "content") (profiles.contains "data@0")
  unless (← VE.Route.Wire.meaningId profiles envId (VE.Route.Wire.encodeFormula f)) == mid do
    throw "reading meaning id does not match content"
  let admission ← r.getObjVal? "admission"
  let akeys ← match admission with
    | .obj kvs => pure (kvs.toList.map Prod.fst)
    | _ => throw "invalid reading admission"
  unless akeys.length == 3 && ["who", "why", "distinguishing_models"].all akeys.contains do
    throw "invalid reading admission"
  unless token (← stringField admission "who") && !(← stringField admission "why").isEmpty do
    throw "invalid reading admission"
  let models ← match ← admission.getObjVal? "distinguishing_models" with
    | .obj kvs => pure kvs.toList
    | _ => throw "invalid reading admission"
  let others := ids.filter (· != id)
  unless models.length == others.length && others.all (fun o => (models.map Prod.fst).contains o) do
    throw "each other reading needs a distinguishing model id"
  let pairs ← models.mapM fun (o, m) => do
    let mid ← m.getStr?
    unless token mid do throw "invalid distinguishing model id"
    pure (o, mid)
  pure (id, kind == .str "asserted", f, pairs)

/-- `validate_reading_sets` and `active_reading_sets`: the active sets (the latest version per
unit) with their status and readings. -/
def compileSets (rv : VE.Route.Wire.RouteVocabulary) (profiles : List String) (envId : String)
    (unitIds : List String) (j : Json) : Except String (List (FrontSet × List Bool)) := do
  let items ← match j with
    | .arr xs => pure xs.toList
    | _ => throw "reading_sets must be a list"
  let all ← items.foldlM (fun (acc : List (FrontSet × List Bool)) item => do
    let keys ← match item with
      | .obj kvs => pure (kvs.toList.map Prod.fst)
      | _ => throw "invalid reading set"
    let required := ["id", "unit", "version", "status", "readings"]
    unless required.all keys.contains && keys.all (required ++ ["signature", "rejected_history", "models"]).contains do
      throw "invalid reading set"
    let id ← stringField item "id"
    let version ← (← item.getObjVal? "version").getNat?
    unless token id && 1 ≤ version && !(acc.any fun (s, _) => s.id == id && s.version == version) do
      throw "invalid or duplicate reading set version"
    let unit ← stringField item "unit"
    let status ← stringField item "status"
    unless unitIds.contains unit && (status == "authored" || status == "open") do
      throw "invalid reading set unit or status"
    unless acc.all (fun (s, _) => (s.id == id) == (s.unit == unit)) do
      throw "one reading set per source unit; versions must keep their unit"
    let readings ← match ← item.getObjVal? "readings" with
      | .arr xs => pure xs.toList
      | _ => throw "reading sets hold 1 to 64 readings"
    unless 1 ≤ readings.length && readings.length ≤ 64 do throw "reading sets hold 1 to 64 readings"
    let signed := (item.getObjVal? "signature").toOption.bind (·.getStr?.toOption)
    if status == "authored" && (readings.length != 1 || !(signed.any token)) then
      throw "authored reading needs one signed choice"
    if status == "open" && (item.getObjVal? "signature").toBool then
      throw "open reading set cannot have an author signature"
    let ids ← readings.mapM fun r => stringField r "id"
    unless ids.all token && ids.eraseDups.length == ids.length do throw "duplicate or invalid reading id"
    let compiled ← readings.mapM (compileReading rv profiles envId ids)
    let models ← match item.getObjVal? "models" with
      | .ok (.obj kvs) => pure kvs.toList
      | .ok _ => throw "distinguishing models must be supplied by id"
      | .error _ => pure []
    let referenced := (compiled.flatMap fun (_, _, _, ps) => ps.map Prod.snd).eraseDups
    unless models.length == referenced.length && referenced.all (fun m => (models.map Prod.fst).contains m) do
      throw "distinguishing models must be supplied by id"
    let decoded ← models.mapM fun (name, data) => do
      let M ← VE.Route.Wire.decodeModel rv data
      unless (← modelId profiles envId data) == name do throw "distinguishing model id does not match model"
      pure (name, M)
    for (_, _, f, ps) in compiled do
      for (other, mid) in ps do
        match compiled.find? (·.1 == other), decoded.find? (·.1 == mid) with
        | some (_, _, g, _), some (_, M) =>
          if f.eval M [] == g.eval M [] then throw "distinguishing model does not separate readings"
        | _, _ => throw "each other reading needs a distinguishing model id"
    match item.getObjVal? "rejected_history" with
    | .ok (.arr _) | .error _ => pure ()
    | .ok _ => throw "invalid rejected reading history"
    pure (acc ++ [(⟨id, unit, version, status, compiled.map fun (i, _, f, _) => (i, f)⟩, compiled.map (·.2.1))]))
    []
  pure all

/-- `active_reading_sets`: only the latest version of each unit's set. -/
def activeOf (all : List (FrontSet × List Bool)) : List (FrontSet × List Bool) :=
  all.filter fun (s, _) => !all.any fun (o, _) => o.unit == s.unit && o.version > s.version

/-- `validate_narrowings`: the narrowing ids. -/
def narrowingIds (all : List FrontSet) (unitIds : List String) (j : Json) : Except String (List String) := do
  let items ← match j with
    | .arr xs => pure xs.toList
    | _ => throw "narrowings must be a list"
  items.foldlM (fun ids item => do
    let keys ← match item with
      | .obj kvs => pure (kvs.toList.map Prod.fst)
      | _ => throw "invalid narrowing"
    let schema := ["id", "set", "version", "keeps", "by", "reason_spans"]
    unless keys.length == schema.length && schema.all keys.contains do throw "invalid narrowing"
    let id ← stringField item "id"
    unless token id && !ids.contains id && token (← stringField item "by") do throw "invalid narrowing id or author"
    let set ← stringField item "set"
    let version ← (← item.getObjVal? "version").getNat?
    let rs ← match all.find? (fun r => r.id == set && r.version == version) with
      | some rs => pure rs
      | none => throw "narrowing cites unknown reading set version"
    let keeps ← strings (← item.getObjVal? "keeps")
    unless !keeps.isEmpty && keeps.all (rs.readings.map Prod.fst).contains do throw "narrowing must keep named readings"
    let spans ← strings (← item.getObjVal? "reason_spans")
    unless !spans.isEmpty && spans.all unitIds.contains do throw "narrowing needs cited source units"
    pure (ids ++ [id])) []

/-- The loaded front matter: its format, the W2 admission object, the active reading sets and
each unit's W2 status (with its explicit status, if any). -/
structure Front where
  format : String
  w2 : Json
  sets : List FrontSet
  status : List (String × String)
  explicit : List (String × String)

def optionalList (front : Json) (key : String) : Json :=
  match front.getObjVal? key with
  | .ok v => v
  | .error _ => .arr #[]

/-- `load_document` and the admission object of `_check_document`, for a front matter under
the base profiles `profiles` with environment identity `envId`. -/
def loadFront (rv : VE.Route.Wire.RouteVocabulary) (profiles : List String) (envId : String)
    (front : Json) (source : String) (fences : List (String × String)) : Except String Front := do
  let format ← stringField front "format"
  if source.isEmpty then throw "document source is empty"
  let _ ← match front.getObjVal? "environment" with
    | .ok (.obj _) => pure ()
    | _ => throw "document needs an embedded environment"
  let openNames ← openTermNames rv (optionalList front "open_terms")
  let unitsJ ← match front.getObjVal? "units" with
    | .ok (.arr xs) => if xs.isEmpty then throw "document needs units" else pure xs.toList
    | _ => throw "document needs units"
  let units ← compileUnits rv profiles envId source openNames 0 unitsJ
  unless fences.isEmpty do throw (notImplemented "fenced English or strict content")
  let all ← compileSets rv profiles envId (units.map Unit₀.id) (optionalList front "reading_sets")
  let active := activeOf all
  let status := units.map fun x => (x.id, match active.find? (·.1.unit == x.id) with
    | some (rs, kinds) => if rs.status == "authored" && kinds.all id then "CHECKED" else "OPEN"
    | none => x.status)
  match front.getObjVal? "lemmas" with
  | .ok (.arr _) | .error _ => pure ()
  | .ok _ => throw "lemmas must be a list"
  for x in units do
    if x.kind == .str "asserted" && x.content.isNone && !(all.any (·.1.unit == x.id)) then
      throw "asserted unit needs content or a reading set"
  let narrowings ← narrowingIds (all.map Prod.fst) (units.map Unit₀.id) (optionalList front "narrowings")
  match optionalList front "weights" with
  | .arr ws => for w in ws.toList do
      match w with
      | .obj kvs => unless kvs.toList.length == 3 && ["set", "by", "values"].all (fun k => (kvs.toList.map Prod.fst).contains k) do
          throw "invalid removable reading weights"
      | _ => throw "invalid removable reading weights"
  | _ => throw "invalid removable reading weights"
  let activeUnits := active.map (·.1.unit)
  let w2units := units.map fun x => Json.mkObj ([("id", Json.str x.id),
      ("span", Json.arr #[toJson x.span.1, toJson x.span.2]), ("kind", x.kind)] ++
    match x.content with
    | some f => if activeUnits.contains x.id then [] else [("content", VE.Route.Wire.encodeFormula f)]
    | none => [])
  let w2sets := (active.filter fun (_, kinds) => kinds.all id).map fun (rs, _) => Json.mkObj [
    ("id", .str rs.id), ("version", toJson rs.version),
    ("readings", Json.arr (rs.readings.map fun (_, f) => VE.Route.Wire.encodeFormula f).toArray)]
  -- a document without a claim graph is loaded but not admitted by Python (document.md); W2
  -- admission, which this route runs, needs a graph: the route abstains, it never rejects one
  let graph ← match front.getObjVal? "graph" with
    | .ok g => pure [("graph", g)]
    | .error _ => throw (notImplemented "a document without a claim graph")
  let w2 := Json.mkObj ([("units", Json.arr w2units.toArray)] ++ graph ++
    [("lemmas", optionalList front "lemmas"), ("open_terms", Json.arr (openNames.map Json.str).toArray),
     ("reading_sets", Json.arr w2sets.toArray), ("narrowings", Json.arr (narrowings.map Json.str).toArray)])
  pure ⟨format, w2, active.map Prod.fst, status,
    units.filterMap fun x => x.explicit.map (x.id, ·)⟩

/-- The explicit statuses agree with the loaded ones (after groups, for `@2`). -/
def explicitOk (status explicit : List (String × String)) : Except String Unit :=
  if explicit.all fun (u, s) => (status.find? (·.1 == u)).map Prod.snd == some s then .ok ()
  else .error "unit status contradicts content, meaning, or active reading set"

def fencesOf (j : Json) : List (String × String) :=
  match j.getObjValD "fences" with
  | .obj kvs => kvs.toList.filterMap fun (k, v) => v.getStr?.toOption.map (k, ·)
  | _ => []

/-- The front matter of a payload object. -/
def loadPayload (rv : VE.Route.Wire.RouteVocabulary) (profiles : List String) (envId : String) (j : Json) :
    Except String Front :=
  loadFront rv profiles envId (metaOf j) (sourceOf j) (fencesOf j)

end VE.Discourse.Loader
