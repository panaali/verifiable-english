import VE.Senses.Request
import VE.Senses.Decode
import VE.Senses.Version
import VE.Senses.Flip
import VE.Senses.Texts
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

def occurrenceJson (o : SenseOccurrence) (extra : List (String × Json) := []) : Json := Json.mkObj
  ([("sentence", toJson o.sentence), ("token_start", toJson o.start),
    ("token_stop", toJson o.stop), ("symbol", .str o.symbol),
    ("is_default", .bool o.isDefault)] ++
    (match o.candidate with
    | some i => [("candidate", toJson i)]
    | none => []) ++ extra)

/-- An occurrence's bytes in a source whose sentences `lexSpans` gives as `spans`, after `d` rendered defaults:
from its first token's first byte to the end of its last token, exclusive as `lexSpans`'s are (plan B6, sn-b6c). -/
def byteSpan (spans : Array (Array Spanned)) (d : Nat) (o : SenseOccurrence) : Option (Nat × Nat) := do
  let sent ← spans[o.sentence - d]?
  pure ((← sent[o.start]?).2.1, (← sent[o.stop - 1]?).2.2)

/-- A sense-map entry of a route answer: the gloss of its sense (plan 2.8, hover) and, over a source, its bytes. -/
def senseEntryJson (P : Projection) (spans : Option (Array (Array Spanned))) (d : Nat) (o : SenseOccurrence) :
    Json :=
  occurrenceJson o (((P.map.find? (·.1 == o.symbol)).map fun x => ("gloss", Json.str x.2.1.gloss)).toList ++
    ((spans.bind (byteSpan · d o)).toList.flatMap fun (a, z) => [("byte_start", toJson a), ("byte_stop", toJson z)]))

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
the identities of its own projection (`ids`). On a route answer (`texts`) every open unit has its `text`, each
sense-map entry is `entry`'s, and `extra` (the texts of 3.2, sn-b6c) is added. -/
def outcomeJson (c : VE.EnglishGrammar.Run.Case) (source : Option String) (count : Nat)
    (fences : Option (List (Option Nat))) (text : Nat → SenseUnit → String)
    (admitted : List (String × Json)) (ids : Option (String → Json)) (out : SensesOutcome)
    (texts : Bool := false) (entry : SenseOccurrence → Json := (occurrenceJson ·))
    (extra : List (String × Json) := []) : Except String Json := do
  let (status, code) ← out.statusCode
  let common := [("status", .str status)] ++ (code.toList.map fun c => ("code", .str c))
  match out with
  | .ok units senses mixed unused P =>
    pure (Json.mkObj (common ++
      [("units", Json.arr (units.mapIdx (unitJson ids (if texts || fences.isSome then some text else none)
          (count - units.length))).toArray),
       ("sense_map", Json.arr (senses.map entry).toArray),
       ("mixed", toJson mixed), ("unused", toJson unused),
       ("environment", P.envJson)] ++ admitted ++
      (fences.toList.map fun fs => ("fences", Json.arr (fs.map fenceJson).toArray)) ++ extra))
  | .fault f => pure (Json.mkObj (common ++ faultFields f ++ extra))
  | _ =>
    let fields ← s2Fields c source out
    unless fields.take 2 == common do throw "S2's status and code differ from the reader's"
    pure (Json.mkObj ((source.map (VE.EnglishGrammar.Run.refusalExtras c.E.profiles · fields)).getD fields ++ extra))

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

/-- The projection as the wire gives it: its environment JSON with the request's profile list as written. The
reader decides without the document layers (`VE.Compose.decidingEnvironment`), and every identity reads the list
as written (`VE.Compose.documentLayers`). -/
def _root_.VE.Senses.Projection.written (environment : Json) (P : Projection) : Projection :=
  match environment.getObjVal? "profiles" with
  | .ok ps => { P with envJson := P.envJson.setObjVal! "profiles" ps }
  | .error _ => P

/-- An outcome whose projection the wire gives (`Projection.written`). -/
def _root_.VE.Senses.SensesOutcome.written (environment : Json) : SensesOutcome → SensesOutcome
  | .ok units senses mixed unused P => .ok units senses mixed unused (P.written environment)
  | o => o

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

/-- The first `k` sentences of a source as written (plan B6, the preamble lines): each from its first token's
first byte to its terminator's last (`lexSpans`). -/
def writtenLines (s : String) (k : Nat) : List String :=
  match lexSpans s with
  | .error _ => []
  | .ok sents => (sents.extract 0 k).toList.filterMap fun sent => do
    let first ← sent[0]?
    let last ← sent.back?
    pure (s.extract ⟨first.2.1⟩ ⟨last.2.2 + 1⟩)

/-- A flip model's table in the existing model wire form (`VE.Bridge.decodeModelData`). -/
def flipModelJson (m : FlipModel) : Json :=
  Json.mkObj [("complete", .bool true), ("domains", Json.mkObj (m.domains.map fun (s, xs) => (s, toJson xs))),
    ("constants", Json.mkObj (m.constants.map fun (c, x) => (c, .str x))),
    ("relations", Json.mkObj (m.relations.map fun (p, rows) => (p, toJson rows)))]

/-- A flip model on the wire: the unit's sentence, the pair, its status, and for a distinguishing model the senses
it makes true, the two candidates' values under it and the model in the existing model wire form. -/
def flipJson (start : Nat) : (Nat × Nat × Nat) × Flip → Json
  | ((k, i, j), f) => Json.mkObj ([("sentence", toJson (start + k)), ("first", toJson i), ("second", toJson j)] ++
    match f with
    | .distinguished on a b m => [("status", .str "distinguished"), ("true", toJson on),
        ("values", Json.arr #[.bool a, .bool b]), ("model", flipModelJson m)]
    | .undistinguished => [("status", .str "undistinguished")]
    | .unknown => [("status", .str "unknown")])

/-- An admitted reading's identities (plan 2.7): S2's of its projection, without `overlay_digest`, with a source
request's `source_sha256` and the preamble lines it wrote (the sentences before the body, which is the last of the
`count` sentences read, after `d` rendered defaults); the words its body uses; the flip models of its open units
(`flipsOf`); and each candidate's identities (`ids`), computed once per distinct resolving lines by `linesProjection`, as
`senses.project` computes them, with the request's `environment` profile list as written (`Projection.written`). -/
def admittedIds (D : Dictionary) (c : VE.EnglishGrammar.Run.Case) (environment : Json) (b count d : Nat)
    (text : SenseText) : SensesOutcome → Except String (List (String × Json) × (String → Json))
  | .ok units _ _ _ P => do
    let start := count - units.length
    let used := usedOf P
    let (_, own) ← projectionIds c P
    let (source, preamble) := match text with
      | .source s => ([("source_sha256", Json.str (VE.CertificateWire.sha256 s.toUTF8))],
          [("preamble", toJson (writtenLines s (start - d)))])
      | .fences _ => ([], [])
    let table ← (units.flatMap fun u => u.candidates.map (·.lines)).eraseDups.mapM fun l => do
      match ← linesProjection D c b l used with
      | .ok Q => pure (l, Json.mkObj (← projectionIds c (Q.written environment)).2)
      | .error _ => throw "a candidate's resolving lines do not project"
    pure ([("identities", Json.mkObj (own ++ source ++ [("actions_version", .str VE.EnglishGrammar.Fixed.actionsVersion)])),
      ("used", toJson used)] ++ preamble ++ [("flips", Json.arr ((flipsOf P units).map (flipJson start)).toArray)],
      fun l => (VE.Bridge.lookup table l).getD (Json.mkObj []))
  | _ => pure ([], fun _ => Json.mkObj [])

/-- What the texts of 3.2 read, by `readSents`'s steps over the text's sentences: the preamble's assignment and
its line count, the body, its used words and its projection. -/
def bodyOf (D : Dictionary) (c : VE.EnglishGrammar.Run.Case) (b : Nat) (sents : List (Array Tok)) :
    Option (Assignment × Nat × List (Array Tok) × List String × Projection) := do
  let (A, k) ← (readPreamble D b (sents.map (·.toList))).toOption
  let body := sents.drop k
  let used := usedWords D (body.map (·.toList))
  pure (A, k, body, used, ← (project D A c.E c.L used).toOption)

/-- An admitted reading's warnings (plan 2.8): a `Mixed` warning per word of `mixed`, with each sense's gloss and
the sentences of its occurrences in resolved units, then an `Unneeded` warning per line of a word with one sense. -/
def warningsJson (D : Dictionary) (d : Nat) (A : Option Assignment) (P : Projection) (occ : List SenseOccurrence)
    (mixed : List (String × List String)) : Json :=
  let warning (code w t : String) := Json.mkObj [("code", .str code), ("word", .str w), ("text", .str t)]
  let uses (id : String) : String × List Nat :=
    ((((P.map.find? (·.1 == id)).map (·.2.1.gloss)).getD id),
     ((occ.filter fun o => o.symbol == id && o.candidate.isNone).map (·.sentence - d)).eraseDups)
  Json.arr ((mixed.map fun (w, ids) => warning "Mixed" w (mixedText w (List.map uses ids))) ++
    ((A.map (unneeded D)).getD []).map fun w => warning "Unneeded" w (unneededText w)).toArray

/-- The texts of an answer (spec 3.2, plan 2.8; sn-b6c), `d` rendered defaults first: a fault's `text`
(`UnknownGloss`, `TooManyCandidates`, a one-word `CandidatesDiverge`), the `NoSenseFits` hint beside S2's `none` for
a sentence with one unresolved word, and an admitted reading's `Mixed` and `Unneeded` warnings. -/
def textsJson (D : Dictionary) (c : VE.EnglishGrammar.Run.Case) (b d : Nat)
    (body : Option (Assignment × Nat × List (Array Tok) × List String × Projection)) :
    SensesOutcome → List (String × Json)
  | .fault (.unknownGloss line w g) => [("text", .str (unknownGlossText D line w g))]
  | .fault (.tooManyCandidates i ws) => [("text", .str (tooManyText (i - d) ws))]
  | .fault (.candidatesDiverge i [w] why) => (do
      let (A, k, sents, used, P) ← body
      let (g1, g2) ← divergeGlosses D A c.E c.L used P b k i sents w why
      pure ("text", Json.str (divergeText (i - d) w g1 g2 why))).toList
  | .stopped i .noDerivation _ =>
    match (do let (A, k, sents, _, _) ← body; pure (unresolvedIn D A (← sents[i - k]?).toList)) with
    | some [w] => [("hint", Json.mkObj [("code", .str "NoSenseFits"), ("text", .str (noSenseFitsText D (i - d) w))])]
    | _ => []
  | .ok _ occ mixed _ P => [("warnings", warningsJson D d (body.map (·.1)) P occ mixed)]
  | _ => []

/-- Lean's preamble line for a requested word and gloss (plan B7, `ve senses resolve`): the line of the sense of
`w` whose gloss is `g` (`lineOf`), or `UnknownWord` or `UnknownGloss`. -/
def lineJson (D : Dictionary) (w g : String) : Json :=
  Json.mkObj ([("word", Json.str w), ("gloss", .str g)] ++
    match (D.sensesOf w).find? (·.gloss == g) with
    | some s => [("text", .str (lineOf w s))]
    | none => [("code", .str (if (D.sensesOf w).isEmpty then "UnknownWord" else "UnknownGloss"))])

/-- The re-read of a rendering of candidate `j` of the unit at `sentence` (plan 2.8;
reviews/dri-decisions-20261101-sn-b7b8-reread.md item 1): the rendering, one sentence, read by the senses reader
(`readOne`, without S2's policy) under the candidate's own projection (its lines over the body's `used` words, as
its identities are computed) from the state before the unit. `same` when it reads with no quoted sense to the
candidate's formula and mark, `unknown` when the budget ends, else `different`. -/
def rereadJson (D : Dictionary) (c : VE.EnglishGrammar.Run.Case) (b start : Nat) (used : List String)
    (units : List SenseUnit) (sentence j : Nat) (rendering : String) : Except String Json := do
  let some u := (if sentence < start then none else units[sentence - start]?)
    | throw "InvalidInput: the re-read names no unit of the answer"
  let some cand := u.candidates[j]? | throw "InvalidInput: the re-read names no candidate of its unit"
  let Q ← match ← linesProjection D c b cand.lines used with
    | .ok Q => pure Q
    | .error _ => throw "a candidate's resolving lines do not project"
  let outcome := match lex rendering, grammarFault Q with
    | .ok #[w], none =>
      match readOne Q (stateBefore units (sentence - start)) b w with
      | .ok (some (t, F, m, _)) => if F == cand.formula && m == cand.mark && (quotedSenseOf Q t).isNone
          then "same" else "different"
      | .error .budget => "unknown"
      | _ => "different"
    | _, _ => "different"
  pure (Json.mkObj [("sentence", toJson sentence), ("candidate", toJson j), ("outcome", .str outcome)])

/-- A `senses.read` case. With `identified` (the route's runner, not the document mode's call) an admitted answer
carries its identities (`admittedIds`) and its environment's profile list as written (`Projection.written`). -/
def readCase (j : Json) (identified : Bool := false) : Except String Json := do
  let fenced := has j "fences"
  VE.Bridge.exactFields j (["id", "environment", "lexicon", "packs", "own", "budget",
    if fenced then "fences" else "source"] ++
    (if fenced then ["fence_ids", "reading_set_units"] else ["line", "reread"].filter (has j)) ++
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
  let (count, d, fences, sents) := match documentInput D A text, text with
    | .ok (.ok (d, sents)), .fences fs => (sents.length, d, some (fenceUnits D budget d sents fs.length), sents)
    | .ok (.ok (d, sents)), .source _ => (sents.length, d, none, sents)
    | _, _ => (0, 0, none, [])
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
  let environment := j.getObjValD "environment"
  let out := if identified then out.written environment else out
  let (admitted, ids) ← if identified then do
      let (a, f) ← admittedIds D c environment budget count d text out; pure (a, some f)
    else pure ([], none)
  let result ← if identified then do
      let body := bodyOf D c budget sents
      let spans := match text with
        | .source s => (lexSpans s).toOption
        | .fences _ => none
      let reread ← match out, j.getObjVal? "reread" with
        | .ok units _ _ _ P, .ok r => do
          VE.Bridge.exactFields r ["sentence", "candidate", "rendering"]
          pure [("reread", ← rereadJson D c budget (count - units.length) (usedOf P) units
            (← VE.Senses.natOf (← r.getObjVal? "sentence")) (← VE.Senses.natOf (← r.getObjVal? "candidate"))
            (← VE.Bridge.stringField r "rendering"))]
        | _, _ => pure []
      let entry := match out with
        | .ok _ _ _ _ P => senseEntryJson P spans d
        | _ => (occurrenceJson ·)
      outcomeJson c (refusalSource A text) count fences unitText admitted ids out true entry
        (textsJson D c budget d body out ++ reread)
    else outcomeJson c (refusalSource A text) count fences unitText admitted ids out
  let line ← match j.getObjVal? "line" with
    | .ok l => do
      VE.Bridge.exactFields l ["word", "gloss"]
      pure [("line", lineJson D (← VE.Bridge.stringField l "word") (← VE.Bridge.stringField l "gloss"))]
    | .error _ => pure []
  pure (VE.Route.Wire.ok id [("result", Json.mkObj
    ([("request_id", .str requestId), ("dictionary_id", .str (dictionaryId D)),
     ("senses_version", .str sensesVersion), ("reading", result)] ++ line))])

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
        let P := P.written (j.getObjValD "environment")
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
