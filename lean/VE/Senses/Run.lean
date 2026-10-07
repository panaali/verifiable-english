import VE.EnglishGrammar.SensesRequest
import VE.Senses.Decode
import VE.EnglishGrammar.Run

/-! A one-shot admission boundary for the senses reader. The pack text reaches
`decodePackText` unchanged; every reading and projection decision is made by
`readWithSenses`. This runner is deliberately separate from the frozen S2
grammar implementation. -/

namespace VE.Senses.Run
open Lean VE.Senses VE.EnglishGrammar

def pairJson (p : String × Nat) : Json := Json.arr #[.str p.1, toJson p.2]

def candidateJson (c : Candidate) : Json := Json.mkObj
  [("choice", Json.arr (c.choice.map pairJson).toArray), ("lines", .str c.lines),
   ("formula", c.formula.encode), ("mark", .bool c.mark)]

/-- Unit `i` of a text whose body starts at sentence `k`: its sentence, and the state after it (spec 4.1, as
S2's `readingJson` gives it per reading). -/
def unitJson (k i : Nat) (u : SenseUnit) : Json := Json.mkObj
  ([("sentence", toJson (k + i)), ("candidates", Json.arr (u.candidates.map candidateJson).toArray),
    ("unresolved", toJson u.unresolved), ("referents", toJson u.after.referents),
    ("binder_seen", .bool u.after.binderSeen)] ++
    match u.formula with
    | some (f, mark) => [("formula", f.encode), ("mark", .bool mark)]
    | none => [])

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
index counts the preamble. `tests/test_senses_route.py` compares them with `ve_english_route`'s. -/
def s2Fields (c : VE.EnglishGrammar.Run.Case) (source : String) :
    SensesOutcome → Except String (List (String × Json))
  | .lexical r => pure (status "rejected" ++ coded r.code (rejectText 0 r) ++
      ((lexicalSpan source r).toList.map fun s => ("span", spanJson s)))
  | .invalidGrammar g => pure (invalidFields "senses.read" c g)
  | .illTyped => pure (status "rejected" ++ coded "IllTyped" (illTypedText none))
  | .stopped i o tags =>
    let pos := [("sentence", toJson i)]
    match o with
    | .ok _ _ => throw "a stopped reading cannot be ok"
    | .noDerivation => pure (status "none" ++ coded "NoDerivation"
        s!"Sentence {i + 1} has no reading with the current vocabulary." ++ pos)
    | .ambiguous t u => pure (status "many" ++ coded "Ambiguous"
        s!"Sentence {i + 1} can be read in more than one way. Two of the ways are shown." ++ pos ++
        [("witnesses", Json.arr #[treeJson tags t, treeJson tags u])])
    | .rejected r => pure (status "rejected" ++ coded r.code (rejectionText source i r) ++ pos)
    | .budget => pure (budgetFields i)
  | .ok .. | .fault _ => throw "not an outcome of S2"

/-- The answer to a text of `count` sentences (`lex`'s); the units are its last sentences (`readBody_good`). -/
def outcomeJson (c : VE.EnglishGrammar.Run.Case) (source : String) (count : Nat) (out : SensesOutcome) :
    Except String Json := do
  let (status, code) ← out.statusCode
  let common := [("status", .str status)] ++ (code.toList.map fun c => ("code", .str c))
  match out with
  | .ok units senses mixed unused P =>
    pure (Json.mkObj (common ++
      [("units", Json.arr (units.mapIdx (unitJson (count - units.length))).toArray),
       ("sense_map", Json.arr (senses.map occurrenceJson).toArray),
       ("mixed", toJson mixed), ("unused", toJson unused),
       ("environment", P.envJson)]))
  | .fault f => pure (Json.mkObj (common ++ faultFields f))
  | _ =>
    let fields ← s2Fields c source out
    unless fields.take 2 == common do throw "S2's status and code differ from the reader's"
    pure (Json.mkObj (VE.EnglishGrammar.Run.refusalExtras c.E.profiles source fields))

def decodeDictionary (j : Json) : Except String Dictionary := do
  let packs ← (← j.getObjVal? "packs").getArr?
  let decoded ← packs.toList.mapM fun p => do decodePackText (← p.getStr?)
  let own ← (← j.getObjVal? "own").getArr?
  pure ⟨decoded, ← own.toList.mapM decodeSense⟩

def readCase (j : Json) : Except String Json := do
  VE.Bridge.exactFields j ((["id", "environment", "lexicon", "packs", "own", "source", "budget"] ++
    if (j.getObjVal? "overlay").toOption.isSome then ["overlay"] else []))
  let id ← VE.Bridge.stringField j "id"
  let c ← VE.EnglishGrammar.Run.decodeCase j
  let D ← decodeDictionary j
  let source ← VE.Bridge.stringField j "source"
  let budget ← VE.Senses.natOf (← j.getObjVal? "budget")
  let requestId ← VE.CertificateWire.digest "ve-senses-request-v1\n" j
  let count := match lex source with
    | .ok sents => sents.size
    | .error _ => 0
  let result ← outcomeJson c source count (sensesRequest D c.E c.L budget source)
  pure (VE.Route.Wire.ok id [("result", Json.mkObj
    [("request_id", .str requestId), ("dictionary_id", .str (dictionaryId D)), ("reading", result)])])

def runCaseReported (j : Json) : Json :=
  match readCase j with
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
