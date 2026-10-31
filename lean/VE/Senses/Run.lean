import VE.Senses.Request
import VE.Senses.Decode
import VE.Senses.Version
import VE.EnglishGrammar.Run

/-! A one-shot admission boundary for the senses reader. The pack text reaches
`decodePackText` unchanged; every reading and projection decision is made by
`readDocument` (`readWithSenses` on a source with no defaults, `readDocument_source`), after E2's check
of the submitted lexicon (`documentRequest`). A request carries a `source`, or a document's English
`fences` in unit order (RD-8), and optional front-matter `defaults`. This runner is deliberately separate from the frozen S2
grammar implementation. -/

namespace VE.Senses.Run
open Lean VE.Senses VE.EnglishGrammar

def pairJson (p : String × Nat) : Json := Json.arr #[.str p.1, toJson p.2]

/-- A candidate, with the identities of its own projection when asked (`ids` of its resolving lines, plan 2.6). -/
def candidateJson (ids : Option (String → Json)) (c : Candidate) : Json := Json.mkObj
  ([("choice", Json.arr (c.choice.map pairJson).toArray), ("lines", .str c.lines),
   ("formula", c.formula.encode), ("mark", .bool c.mark)] ++ (ids.map fun f => ("identities", f c.lines)).toList)

/-- Unit `i` of a text whose body starts at sentence `k`: its sentence, and the state after it (spec 4.1, as
S2's `readingJson` gives it per reading); an open unit of a fence request also has its English (`text`, which
is `documentText`). -/
def unitJson (ids : Option (String → Json)) (text : Option (Nat → SenseUnit → String)) (k i : Nat) (u : SenseUnit) :
    Json := Json.mkObj
  ([("sentence", toJson (k + i)), ("candidates", Json.arr (u.candidates.map (candidateJson ids)).toArray),
    ("unresolved", toJson u.unresolved), ("referents", toJson u.after.referents),
    ("binder_seen", .bool u.after.binderSeen)] ++
    match u.formula, text with
    | some (f, mark), _ => [("formula", f.encode), ("mark", .bool mark)]
    | none, some t => if u.candidates.isEmpty then [] else [("text", .str (t (k + i) u))]
    | none, none => [])

/-- `fenceUnits` on the wire: a unit index, or `"line"` for a fence that is a preamble line (the transport
reads no JSON null). -/
def fenceJson : Option Nat → Json
  | some i => toJson i
  | none => .str "line"

def occurrenceJson (o : SenseOccurrence) : Json := Json.mkObj
  ([("sentence", toJson o.sentence), ("token_start", toJson o.start),
    ("token_stop", toJson o.stop), ("symbol", .str o.symbol),
    ("is_default", .bool o.isDefault)] ++
    match o.candidate with
    | some i => [("candidate", toJson i)]
    | none => [])

/-- The arguments of a fault (spec 2.6 and 4.1), under the names of `SenseFault`'s fields. -/
def faultFields : SenseFault → List (String × Json)
  | .invalidDictionary f => [("failure", Json.arr #[.str f.1, .str f.2.1, .str f.2.2])]
  | .unknownWord line word => [("details", Json.mkObj [("line", toJson line), ("word", .str word)])]
  | .unknownGloss line word gloss =>
    [("details", Json.mkObj [("line", toJson line), ("word", .str word), ("gloss", .str gloss)])]
  | .malformedPreamble line => [("details", Json.mkObj [("line", toJson line)])]
  | .preambleBudget line => [("details", Json.mkObj [("line", toJson line)])]
  | .repeatedDefault line word => [("details", Json.mkObj [("line", toJson line), ("word", .str word)])]
  | .preambleLate sentence => [("details", Json.mkObj [("sentence", toJson sentence)])]
  | .collision kind name sense =>
    [("details", Json.mkObj [("kind", .str kind), ("name", .str name), ("sense", .str sense)])]
  | .limit what => [("details", Json.mkObj [("what", .str what)])]
  | .tooManyCandidates sentence words =>
    [("details", Json.mkObj [("sentence", toJson sentence), ("words", toJson words)])]
  | .candidatesDiverge sentence words why =>
    [("details", Json.mkObj [("sentence", toJson sentence), ("words", toJson words),
      ("why", match why with
        | .referent x => Json.mkObj [("referent", .str x)]
        | .binder => .str "binder")])]
  | .quotedSense sentence word => [("details", Json.mkObj [("sentence", toJson sentence), ("word", .str word)])]

open VE.EnglishGrammar.Run in
/-- The fields of S2's outcomes as S2's authoring answer writes them (english-lean-s2.md 4.3): the code
with S2's text, the sentence, the two witness trees of an ambiguity and the lexicon failure; the sentence
index counts the preamble. `tests/test_senses_route.py` compares them with `ve_english_route`'s. With no
`source` (`refusalSource`) a refusal has no span, and a rejection has `rejectText`'s words. A sentence without a
reading over a source has `english.read`'s diagnosis over the request's own environment and lexicon
(`noReadingFields`, E2 spec 4.5). -/
def s2Fields (c : VE.EnglishGrammar.Run.Case) (source : Option String) :
    SensesOutcome → Except String (List (String × Json))
  | .lexical r => pure (status "rejected" ++ coded r.code (rejectText 0 r) ++
      ((source.bind (lexicalSpan · r)).toList.map fun s => ("span", spanJson s)))
  | .invalidGrammar g => pure (invalidFields "senses.read" c g)
  | .illTyped => pure (status "rejected" ++ coded "IllTyped" (illTypedText none))
  | .stopped i o tags =>
    let pos := [("sentence", toJson i)]
    match o with
    | .ok _ _ => throw "a stopped reading cannot be ok"
    | .noDerivation => pure ((match source with
        | some text => noReadingFields c text i
        | none => status "none" ++ coded "NoDerivation"
            s!"Sentence {i + 1} has no reading with the current vocabulary.") ++ pos)
    | .ambiguous t u => pure (status "many" ++ coded "Ambiguous"
        s!"Sentence {i + 1} can be read in more than one way. Two of the ways are shown." ++ pos ++
        [("witnesses", Json.arr #[treeJson tags t, treeJson tags u])])
    | .rejected r => pure (status "rejected" ++ coded r.code
        ((source.map (rejectionText · i r)).getD (rejectText i r)) ++ pos)
    | .budget => pure (budgetFields i)
  | .ok .. | .fault _ => throw "not an outcome of S2"

/-- The answer to a text of `count` sentences (`documentInput`'s); the units are its last sentences
(`readBody_good`). A fence request's admitted answer also maps each fence to its unit (`fenceUnits`), and its
open units carry `text`. A refusal over a `source` has E2's span and advice (`refusalExtras`). An admitted
answer also has the identities of its projection and the words its body uses (`admitted`), and each candidate
the identities of its own projection (`ids`). -/
def outcomeJson (c : VE.EnglishGrammar.Run.Case) (source : Option String) (count : Nat)
    (fences : Option (List (Option Nat))) (text : Nat → SenseUnit → String)
    (admitted : List (String × Json)) (ids : Option (String → Json)) (out : SensesOutcome) :
    Except String Json := do
  let (status, code) ← out.statusCode
  let common := [("status", .str status)] ++ (code.toList.map fun c => ("code", .str c))
  match out with
  | .ok units senses mixed unused P =>
    pure (Json.mkObj (common ++
      [("units", Json.arr (units.mapIdx (unitJson ids (fences.map fun _ => text) (count - units.length))).toArray),
       ("sense_map", Json.arr (senses.map occurrenceJson).toArray),
       ("mixed", toJson mixed), ("unused", toJson unused),
       ("environment", P.envJson)] ++ admitted ++
      (fences.toList.map fun fs => ("fences", Json.arr (fs.map fenceJson).toArray))))
  | .fault f => pure (Json.mkObj (common ++ faultFields f))
  | _ =>
    let fields ← s2Fields c source out
    unless fields.take 2 == common do throw "S2's status and code differ from the reader's"
    pure (Json.mkObj ((source.map (VE.EnglishGrammar.Run.refusalExtras c.E.profiles · fields)).getD fields))

/-- A fence's sentence without the line break that closes a document fence. -/
def fenceLine (f : String) : String := if f.endsWith "\n" then f.dropRight 1 else f

/-- The text a refusal's span and advice are over, as `ve senses check` reads it: the source, or a fence
request's fences joined by line breaks (`fenceLine`, RD-8). Front-matter defaults leave none: their lines are
not the author's text. -/
def refusalSource (A : Assignment) (t : SenseText) : Option String :=
  if A.defaults.isEmpty then
    some (match t with
      | .source s => s
      | .fences fs => "\n".intercalate (fs.map fenceLine))
  else none

/-- A rejection moved `bytes` and `sentences` on: its offset or sentence in a longer text. -/
def shiftReject (bytes sentences : Nat) : Reject → Reject
  | .badCharacter o => .badCharacter (bytes + o)
  | .openQuote o => .openQuote (bytes + o)
  | .badNumeral o => .badNumeral (bytes + o)
  | .badSpacing o => .badSpacing (bytes + o)
  | .emptySentence k => .emptySentence (sentences + k)
  | r => r

/-- A fence's lexical rejection `r` in `refusalSource`'s text: the first fence that does not lex has it, at
its offset and sentence in that fence. -/
def fenceReject (r : Reject) : Nat → Nat → List String → Reject
  | _, _, [] => r
  | bytes, j, f :: rest =>
    match lex f with
    | .error _ => shiftReject bytes j r
    | .ok _ => fenceReject r (bytes + (fenceLine f).utf8ByteSize + 1) (j + 1) rest

def decodeDictionary (j : Json) : Except String Dictionary := do
  let packs ← (← j.getObjVal? "packs").getArr?
  let decoded ← packs.toList.mapM fun p => do decodePackText (← p.getStr?)
  let own ← (← j.getObjVal? "own").getArr?
  pure ⟨decoded, ← own.toList.mapM decodeSense⟩

/-- Front-matter defaults, `{word: index}`, in the order of the words. -/
def decodeDefaults (j : Json) : Except String Assignment := do
  let o ← j.getObj?
  pure ⟨← o.toList.mapM fun (w, i) => do pure (w, ← natOf i)⟩

def has (j : Json) (k : String) : Bool := (j.getObjVal? k).toOption.isSome

/-- The first unresolved fence without a reading set, with its `text`. Lean alone decides whether an open
reading is admitted. -/
def uncoveredFence (text : Nat → SenseUnit → String) (count : Nat) (units : List SenseUnit)
    (mapped : List (Option Nat)) (ids allowed : List String) : Option (String × String) := Id.run do
  for (id, entry) in ids.zip mapped do
    if !allowed.contains id then
      if let some index := entry then
        if let some unit := units[index]? then
          if !unit.candidates.isEmpty then
            return some (id, text (count - units.length + index) unit)
  return none

/-- The refusal of a fence request's identities: one non-empty identity per fence, none repeated, and
reading-set units that are distinct fence identities. -/
def fenceIdsProblem (n : Nat) (ids allowed : List String) : Option String :=
  if ids.length != n then
    some s!"InvalidInput: {ids.length} fence identities are given for {n} English fences"
  else if ids.any (·.isEmpty) then some "InvalidInput: an English fence has an empty unit id"
  else if let some id := ids.find? (fun id => ids.count id > 1) then
    some s!"InvalidInput: unit id {id} names more than one English fence"
  else if let some id := allowed.find? (fun id => allowed.count id > 1) then
    some s!"InvalidInput: reading-set unit {id} is given more than once"
  else (allowed.find? (!ids.contains ·)).map fun id => s!"InvalidInput: reading-set unit {id} names no English fence"

/-- A lexicon as `english.read` receives one (`EnglishGrammar.Run.decodeLexicon`), naming the environment
`envId`. -/
def lexiconJson (envId : String) (L : Lexicon) : Json :=
  let pairs (l : List (String × String)) : Json := Json.arr (l.map fun (a, b) => Json.arr #[.str a, .str b]).toArray
  Json.mkObj [("format", .str VE.EnglishGrammar.Run.lexiconFormat), ("environment_id", .str envId),
    ("nouns", pairs L.nouns), ("letters", pairs L.letters), ("wordings", pairs L.wordings),
    ("negatives", pairs L.negatives),
    ("aliases", Json.arr (L.aliases.map fun (p, a, n) => Json.arr #[.str p, .str a, .bool n]).toArray),
    ("spellings", pairs L.spellings)]

/-- A projection's lexicon JSON and its identities (plan 2.6, 2.7): its environment's and its lexicon's, as
`english.read` computes them for a submitted environment and lexicon without an overlay (`decodeCase`), and the
grammar's of the request's profiles, which a projection does not change. -/
def projectionIds (c : VE.EnglishGrammar.Run.Case) (P : Projection) : Except String (Json × List (String × Json)) := do
  let envId ← VE.EnglishGrammar.Run.environmentId P.envJson
  let lexicon := lexiconJson envId P.lexicon
  pure (lexicon, [("environment_id", .str envId),
    ("lexicon_id", .str (← VE.CertificateWire.digest "ve-english-lexicon-v1\n" lexicon)),
    ("grammar_id", .str (← VE.EnglishGrammar.Run.grammarId c.E.profiles))])

/-- The projection of preamble `lines` over the `used` words (plan 2.6): the lines read as a document's preamble
is (`readPreamble`), every sentence a line, then `project`. `senses.project` and a candidate's identities both
reach `project` here. -/
def linesProjection (D : Dictionary) (c : VE.EnglishGrammar.Run.Case) (b : Nat) (lines : String)
    (used : List String) : Except String (Except SenseFault Projection) := do
  let sents ← if lines.isEmpty then pure [] else match lex lines with
    | .ok s => pure (s.toList.map (·.toList))
    | .error _ => throw "InvalidInput: the lines are not English sentences"
  match readPreamble D b sents with
  | .error f => pure (.error f)
  | .ok (A, k) =>
    if k < sents.length then throw s!"InvalidInput: sentence {k + 1} of the lines is not a preamble line"
    else pure (project D A c.E c.L used)

/-- The words of the dictionary a body uses, in the dictionary's order: those whose senses its projection
declares (`projectedSenses`). -/
def usedOf (P : Projection) : List String := (P.map.map (·.2.1.word)).eraseDups

/-- An admitted reading's identities (plan 2.7): S2's of its projection, without `overlay_digest`, with a source
request's `source_sha256`; the words its body uses; and each candidate's (`ids`), computed once per distinct
resolving lines by `linesProjection`, as `senses.project` computes them. -/
def admittedIds (D : Dictionary) (c : VE.EnglishGrammar.Run.Case) (b : Nat) (text : SenseText) :
    SensesOutcome → Except String (List (String × Json) × (String → Json))
  | .ok units _ _ _ P => do
    let used := usedOf P
    let (_, own) ← projectionIds c P
    let source := match text with
      | .source s => [("source_sha256", Json.str (VE.CertificateWire.sha256 s.toUTF8))]
      | .fences _ => []
    let table ← (units.flatMap fun u => u.candidates.map (·.lines)).eraseDups.mapM fun l => do
      match ← linesProjection D c b l used with
      | .ok Q => pure (l, Json.mkObj (← projectionIds c Q).2)
      | .error _ => throw "a candidate's resolving lines do not project"
    pure ([("identities", Json.mkObj (own ++ source ++ [("actions_version", .str VE.EnglishGrammar.Fixed.actionsVersion)])),
      ("used", toJson used)], fun l => (VE.Bridge.lookup table l).getD (Json.mkObj []))
  | _ => pure ([], fun _ => Json.mkObj [])

/-- A `senses.read` case. With `identified` (the route's runner, not the document mode's call) an admitted answer
carries its identities (`admittedIds`). -/
def readCase (j : Json) (identified : Bool := false) : Except String Json := do
  let fenced := has j "fences"
  VE.Bridge.exactFields j (["id", "environment", "lexicon", "packs", "own", "budget",
    if fenced then "fences" else "source"] ++
    (if fenced then ["fence_ids", "reading_set_units"] else []) ++
    (["overlay", "defaults"].filter (has j)))
  let id ← VE.Bridge.stringField j "id"
  let c ← VE.EnglishGrammar.Run.decodeCase j
  let D ← decodeDictionary j
  let text ← if has j "fences" then do pure (SenseText.fences (← VE.Bridge.strings (← j.getObjVal? "fences")))
    else do pure (SenseText.source (← VE.Bridge.stringField j "source"))
  let ids ← if fenced then VE.Bridge.strings (← j.getObjVal? "fence_ids") else pure []
  let allowed ← if fenced then VE.Bridge.strings (← j.getObjVal? "reading_set_units") else pure []
  if fenced then
    if let some problem := fenceIdsProblem (match text with | .fences fs => fs.length | _ => 0) ids allowed then
      throw problem
  let A ← if has j "defaults" then decodeDefaults (← j.getObjVal? "defaults") else pure ⟨[]⟩
  let budget ← VE.Senses.natOf (← j.getObjVal? "budget")
  let requestId ← VE.CertificateWire.digest "ve-senses-request-v1\n" j
  let out ← documentRequest D c.E c.L budget A text
  let (count, d, fences) := match documentInput D A text, text with
    | .ok (.ok (d, sents)), .fences fs => (sents.length, d, some (fenceUnits D budget d sents fs.length))
    | .ok (.ok (d, sents)), .source _ => (sents.length, d, none)
    | _, _ => (0, 0, none)
  let unitText := documentText D A d
  if let .ok units _ _ _ _ := out then
    if let some mapped := fences then
      if let some (unit, message) := uncoveredFence unitText count units mapped ids allowed then
        let result := Json.mkObj [("status", .str "rejected"), ("code", .str "Unresolved"),
          ("unit", .str unit), ("text", .str message)]
        return VE.Route.Wire.ok id [("result", Json.mkObj
          [("request_id", .str requestId), ("dictionary_id", .str (dictionaryId D)),
           ("senses_version", .str sensesVersion), ("reading", result)])]
  let out := match out, text with
    | .lexical r, .fences fs => if A.defaults.isEmpty then .lexical (fenceReject r 0 0 fs) else out
    | o, _ => o
  let (admitted, ids) ← if identified then do let (a, f) ← admittedIds D c budget text out; pure (a, some f)
    else pure ([], none)
  let result ← outcomeJson c (refusalSource A text) count fences unitText admitted ids out
  pure (VE.Route.Wire.ok id [("result", Json.mkObj
    [("request_id", .str requestId), ("dictionary_id", .str (dictionaryId D)),
     ("senses_version", .str sensesVersion), ("reading", result)])])

def runCaseReported (j : Json) : Json :=
  match readCase j true with
  | .ok row => row
  | .error message => Json.mkObj
      [("id", j.getObjValD "id"), ("status", .str "error"), ("error", .str message)]

/-- A fault of `senses.project`: its status and code as `senses.read` gives them, and its arguments. -/
def faultJson (f : SenseFault) : Json :=
  let status := match (SensesOutcome.fault f).statusCode with
    | .ok (status, _) => status
    | .error _ => "rejected"
  Json.mkObj ([("status", .str status), ("code", .str f.code)] ++ faultFields f)

/-- `senses.project` (plan 2.6, B6): the projection of the dictionary and the preamble `lines` over the `used`
words, distinct words of the dictionary, with its environment and lexicon JSON and their identities; or the
dictionary's or the lines' fault. The lexicon must be one `english.read` reads. -/
def projectCase (j : Json) : Except String Json := do
  VE.Bridge.exactFields j (["id", "environment", "lexicon", "packs", "own", "budget", "lines", "used"] ++
    (["overlay"].filter (has j)))
  let id ← VE.Bridge.stringField j "id"
  let c ← VE.EnglishGrammar.Run.decodeCase j
  let D ← decodeDictionary j
  let lines ← VE.Bridge.stringField j "lines"
  let used ← VE.Bridge.strings (← j.getObjVal? "used")
  if let some w := used.find? (!D.words.contains ·) then
    throw s!"InvalidInput: used word {w} is not a word of the dictionary"
  unless used.eraseDups.length == used.length do throw "InvalidInput: a used word is given more than once"
  unless c.L.policyOk c.E {} && c.L.valid c.E {} do throw "InvalidInput: english.read refuses the lexicon"
  let budget ← VE.Senses.natOf (← j.getObjVal? "budget")
  let result ← match D.failures (c.E.sorts.map (·.name)) with
    | f :: _ => pure (faultJson (.invalidDictionary f))
    | [] => do
      match ← linesProjection D c budget lines used with
      | .error f => pure (faultJson f)
      | .ok P => do
        let (lexicon, ids) ← projectionIds c P
        pure (Json.mkObj [("status", .str "ok"), ("environment", P.envJson), ("lexicon", lexicon),
          ("identities", Json.mkObj (ids ++ [("actions_version", .str VE.EnglishGrammar.Fixed.actionsVersion)]))])
  pure (VE.Route.Wire.ok id [("result", Json.mkObj
    [("dictionary_id", .str (dictionaryId D)), ("senses_version", .str sensesVersion), ("projection", result)])])

def projectCaseReported (j : Json) : Json :=
  match projectCase j with
  | .ok row => row
  | .error message => Json.mkObj
      [("id", j.getObjValD "id"), ("status", .str "error"), ("error", .str message)]

def main (args : List String) : IO UInt32 := do
  let input ← match args with
    | [] | ["-"] => (← IO.getStdin).readToEnd
    | [path] => IO.FS.readFile path
    | _ =>
      (← IO.getStderr).putStrLn "usage: ve_senses_route [cases.json|-]"
      return 2
  match VE.JsonInput.parseCases input with
  | .error message =>
    (← IO.getStderr).putStrLn message
    return 2
  | .ok cases =>
    let results := cases.mapIdx fun index c => match c with
      | .ok j => runCaseReported j
      | .error message => Json.mkObj
          [("status", .str "error"), ("case_index", toJson index), ("error", .str message)]
    (← IO.getStdout).putStrLn (Json.arr results).compress
    return if results.any (fun r => r.getObjValD "status" == .str "error") then 1 else 0

end VE.Senses.Run
