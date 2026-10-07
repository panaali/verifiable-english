import VE.Senses.Document
import VE.Senses.Decode
import VE.EnglishGrammar.Run

/-! A one-shot admission boundary for the senses reader. The pack text reaches
`decodePackText` unchanged; every reading and projection decision is made by
`readDocument` (`readWithSenses` on a source with no defaults, `readDocument_source`). A
request carries a `source`, or a document's English `fences` in unit order (RD-8), and
optional front-matter `defaults`. This runner is deliberately separate from the frozen S2
grammar implementation. -/

namespace VE.Senses.Run
open Lean VE.Senses VE.EnglishGrammar

def pairJson (p : String × Nat) : Json := Json.arr #[.str p.1, toJson p.2]

def candidateJson (c : Candidate) : Json := Json.mkObj
  [("choice", Json.arr (c.choice.map pairJson).toArray), ("lines", .str c.lines),
   ("formula", c.formula.encode), ("mark", .bool c.mark)]

/-- Unit `i` of a text whose body starts at sentence `k`: its sentence, and the state after it (spec 4.1, as
S2's `readingJson` gives it per reading); an open unit also has its English (`unresolvedText`). -/
def unitJson (D : Dictionary) (k i : Nat) (u : SenseUnit) : Json := Json.mkObj
  ([("sentence", toJson (k + i)), ("candidates", Json.arr (u.candidates.map candidateJson).toArray),
    ("unresolved", toJson u.unresolved), ("referents", toJson u.after.referents),
    ("binder_seen", .bool u.after.binderSeen)] ++
    match u.formula with
    | some (f, mark) => [("formula", f.encode), ("mark", .bool mark)]
    | none => if u.candidates.isEmpty then [] else [("text", .str (unresolvedText D (k + i) u))])

/-- `fenceUnits` on the wire: a unit index, or null for a fence that is a preamble line. -/
def fenceJson : Option Nat → Json
  | some i => toJson i
  | none => .null

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
def s2Fields (c : VE.EnglishGrammar.Run.Case) : SensesOutcome → Except String (List (String × Json))
  | .lexical r => pure (status "rejected" ++ coded r.code (rejectText 0 r))
  | .invalidGrammar g => pure (invalidFields c g)
  | .illTyped => pure (status "rejected" ++ coded "IllTyped" illTypedText)
  | .stopped i o tags =>
    let pos := [("sentence", toJson i)]
    match o with
    | .ok _ _ => throw "a stopped reading cannot be ok"
    | .noDerivation => pure (status "none" ++ coded "NoDerivation"
        s!"Sentence {i + 1} has no reading with the current vocabulary." ++ pos)
    | .ambiguous t u => pure (status "many" ++ coded "Ambiguous"
        s!"Sentence {i + 1} can be read in more than one way. Two of the ways are shown." ++ pos ++
        [("witnesses", Json.arr #[treeJson tags t, treeJson tags u])])
    | .rejected r => pure (status "rejected" ++ coded r.code (rejectText i r) ++ pos)
    | .budget => pure (budgetFields i)
  | .ok .. | .fault _ => throw "not an outcome of S2"

/-- The answer to a text of `count` sentences (`documentInput`'s); the units are its last sentences
(`readBody_good`). A fence request's admitted answer also maps each fence to its unit (`fenceUnits`). -/
def outcomeJson (c : VE.EnglishGrammar.Run.Case) (D : Dictionary) (count : Nat) (fences : Option (List (Option Nat)))
    (out : SensesOutcome) : Except String Json := do
  let (status, code) ← out.statusCode
  let common := [("status", .str status)] ++ (code.toList.map fun c => ("code", .str c))
  match out with
  | .ok units senses mixed unused P =>
    pure (Json.mkObj (common ++
      [("units", Json.arr (units.mapIdx (unitJson D (count - units.length))).toArray),
       ("sense_map", Json.arr (senses.map occurrenceJson).toArray),
       ("mixed", toJson mixed), ("unused", toJson unused),
       ("environment", P.envJson)] ++
      (fences.toList.map fun fs => ("fences", Json.arr (fs.map fenceJson).toArray))))
  | .fault f => pure (Json.mkObj (common ++ faultFields f))
  | _ =>
    let fields ← s2Fields c out
    unless fields.take 2 == common do throw "S2's status and code differ from the reader's"
    pure (Json.mkObj fields)

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

def readCase (j : Json) : Except String Json := do
  VE.Bridge.exactFields j (["id", "environment", "lexicon", "packs", "own", "budget",
    if has j "fences" then "fences" else "source"] ++ (["overlay", "defaults"].filter (has j)))
  let id ← VE.Bridge.stringField j "id"
  let c ← VE.EnglishGrammar.Run.decodeCase j
  let D ← decodeDictionary j
  let text ← if has j "fences" then do pure (SenseText.fences (← VE.Bridge.strings (← j.getObjVal? "fences")))
    else do pure (SenseText.source (← VE.Bridge.stringField j "source"))
  let A ← if has j "defaults" then decodeDefaults (← j.getObjVal? "defaults") else pure ⟨[]⟩
  let budget ← VE.Senses.natOf (← j.getObjVal? "budget")
  let requestId ← VE.CertificateWire.digest "ve-senses-request-v1\n" j
  let out ← readDocument D c.E c.L budget A text
  let (count, fences) := match documentInput D A text, text with
    | .ok (.ok (d, sents)), .fences fs => (sents.length, some (fenceUnits D budget d sents fs.length))
    | .ok (.ok (_, sents)), .source _ => (sents.length, none)
    | _, _ => (0, none)
  let result ← outcomeJson c D count fences out
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
