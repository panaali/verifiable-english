import VE.Senses.Read
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

def unitJson (u : SenseUnit) : Json := Json.mkObj
  ([("candidates", Json.arr (u.candidates.map candidateJson).toArray),
    ("unresolved", toJson u.unresolved)] ++
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

def outcomeJson (out : SensesOutcome) : Except String Json := do
  let (status, code) ← out.statusCode
  let common := [("status", .str status)] ++ (code.toList.map fun c => ("code", .str c))
  let fields := match out with
    | .ok units senses mixed unused P =>
      [("units", Json.arr (units.map unitJson).toArray),
       ("sense_map", Json.arr (senses.map occurrenceJson).toArray),
       ("mixed", toJson mixed), ("unused", toJson unused),
       ("environment", P.envJson)]
    | .fault (.invalidDictionary f) => [("failure", toJson (f.1, f.2.1, f.2.2))]
    | .fault _ | .lexical _ | .invalidGrammar _ | .stopped _ _ | .illTyped => []
  pure (Json.mkObj (common ++ fields))

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
  let result ← outcomeJson (readWithSenses D c.E c.L budget source)
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
