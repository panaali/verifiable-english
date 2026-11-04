import VE.Commands.Run
import VE.Commands.Examples
import VE.Senses.Run

/-! The fixtures of docs/spec/commands-imperatives.md section 6 through the `english.command` mode: the proof task's
rows P1′ to P8, O1's text, O2's readings, O7's budget, O10's byte bound, the request echo, `jsonWF?`'s refusal. -/

namespace VE.Commands.RunExamples

open Lean (Json toJson)
open VE.Commands.Examples
open VE.EnglishGrammar (workBudget)
open VE.SpeechActs.Wire (readingsBound)

/- A refusal keeps every diagnostic field, and the translation entry point uses that formatter unchanged
when there is no overlay failure. This catches field loss at either list-producing boundary. -/
#guard
  let E : VE.EnglishGrammar.Env := { sorts := [], predicates := [], constants := [] }
  let L : VE.EnglishGrammar.Lexicon :=
    { nouns := [], letters := [], wordings := [], negatives := [], aliases := [], spellings := [] }
  let c : VE.EnglishGrammar.Run.Case := ⟨E, {}, L, none, []⟩
  let fields := VE.EnglishGrammar.Run.translationOf c "x." .notOneSentence
  let source := "x."
  let expected := VE.EnglishGrammar.Run.translationOf c source
    (VE.EnglishGrammar.translateRequest E {} L VE.Commands.maxCandidates workBudget source)
  fields.map Prod.fst == ["status", "code", "text", "class"] &&
    expected.length > 1 &&
    VE.EnglishGrammar.Run.translation c VE.Commands.maxCandidates source == expected

/-- An obligation with its permission dual. -/
def withDual (name : String) (args : List String) (act dual : String) : String × Json :=
  (name, Json.mkObj [("arguments", toJson args), ("description", .str name), ("regulated", Json.mkObj
    [("role", .str "obligation"), ("default", .str "deny"), ("act", .str act), ("permission", .str dual)])])

/-- F0's proof-task part: `reviewed(service)`, the proof predicate, a command with a fill, a prohibition. -/
def proofEnv (you : Option (String × String) := some ("user", "alice")) (extra : List (String × Json) := [])
    (consts : List (String × String) := []) : Json :=
  envOf ["user", "control", "service", "query", "token"]
    ([obligation "click_required" ["user", "control"] "{0} click {1}",
      withDual "submit_required" ["user", "query"] Texts.proofAct "submit_permitted",
      permission "submit_permitted" ["user", "query"] Texts.proofAct,
      permission "share_permitted" ["user", "token"] "{0} share {1}",
      predEntry "reviewed" ["service"] none (some "{0} is reviewed")] ++ extra)
    ([("alice", "user"), ("bob", "user"), ("check", "control"), ("atlas", "service"), ("beacon", "service"),
     ("q1", "query"), ("q2", "query"), ("token1", "token")] ++ consts) "t1" you [("the token", "token1")]

def lexJson (env : Json) : Json :=
  match lexOf env with
  | .ok (_, L) => VE.Senses.Run.lexiconJson
      ((VE.EnglishGrammar.Run.environmentId (VE.EnglishGrammar.displayJson env (Json.mkObj []))).toOption.getD "") L
  | .error _ => .null

def record (i : String) (t : VE.Formula) : Json :=
  Json.mkObj [("id", .str i), ("premises", Json.arr #[]), ("target", Json.mkObj [("ast", VE.Route.Wire.encodeFormula t)])]

def request (s : String) (qs : List (String × VE.Formula) := []) (env : Json := proofEnv) (id : String := "r1")
    (unit : String := "u1") : Json :=
  Json.mkObj [("id", .str id), ("environment", env), ("lexicon", lexJson env), ("unit", .str unit),
    ("wording", .str s), ("queries", Json.arr (qs.map fun (i, t) => record i t).toArray)]

def result (j : Json) : Json := (Run.caseReported j).getObjValD "result"
def get (j : Json) (k : String) : Json := (result j).getObjValD k

/-- The answer is the refusal `code: text`. -/
def refuses (j : Json) (code text : String) : Bool :=
  get j "outcome" == .str "refused" && get j "code" == .str code && get j "text" == .str text

def atlasReviewed : VE.Formula := .unary "reviewed" (.const "atlas")
def beaconReviewed : VE.Formula := .unary "reviewed" (.const "beacon")
def proveAtlas : String := "Prove that atlas is reviewed using these premises."

def proofOne (q : String) : Json :=
  Json.mkObj [("command", Json.mkObj [("force", .str "require"), ("act", .str "submit_required"),
      ("args", toJson [q]), ("guard", VE.Route.Wire.encodeFormula .top)]),
    ("fills", Json.arr #[Json.mkObj [("constant", .str q), ("words", .str q), ("span", .null)]]),
    ("query", .str q), ("paraphrase", .str s!"In this task, you are required to submit a proof of {q}.")]

/-- Each answer is `encode` of `readInstruction` on its decoded request (`caseReported_eq`). -/
def encodes (j : Json) : Bool :=
  match Run.decodeRequest j with
  | .ok q => Run.caseReported j == Run.encode q (readInstruction q.ctx q.s)
  | .error _ => false

/-! ## P1′ to P8 through the mode; O1: `QueryMismatch`'s text is the request's unit -/

#guard get (request proveAtlas [("q1", atlasReviewed)]) "reading" == proofOne "q1"
#guard refuses (request proveAtlas) "QueryMismatch" "u1"
#guard refuses (request proveAtlas [("q1", beaconReviewed)] (unit := "u7")) "QueryMismatch" "u7"
#guard refuses (request proveAtlas [("q1", atlasReviewed), ("q2", atlasReviewed)]) "QueryMismatch" "u1"
#guard get (request proveAtlas [("q1", beaconReviewed), ("q2", atlasReviewed)]) "reading" == proofOne "q2"
#guard refuses (request proveAtlas [("q1", atlasReviewed)]
    (env := proofEnv (extra := [withDual "submitx_required" ["service", "query"] Texts.proofAct "submitx_permitted",
      permission "submitx_permitted" ["service", "query"] Texts.proofAct])))
  "MissingObligationRole" Texts.proofAct
#guard refuses (request "Prove that atlas is wonderful using these premises." [("q1", atlasReviewed)]) "NoDerivation"
  "The sentence to prove has no reading with the current vocabulary. Unknown English phrase 'is wonderful'. Nearest declared wordings: 'control'; 'query'; 'token'."
#guard get (request "Click Check." [("q1", atlasReviewed)]) "reading" == Json.mkObj [("command", Json.mkObj
    [("force", .str "require"), ("act", .str "click_required"), ("args", toJson ["check"]),
     ("guard", VE.Route.Wire.encodeFormula .top)]),
  ("fills", Json.arr #[Json.mkObj [("constant", .str "check"), ("words", .str "check"), ("span", toJson [6, 11])]]),
  ("query", .null), ("paraphrase", .str "In this task, you are required to click check.")]
#guard refuses (request proveAtlas [("q1", atlasReviewed)] (env := proofEnv none)) "UnboundSlot" "you"
#guard refuses (request "Click Check." (env := proofEnv none)) "UnboundSlot" "you"
#guard get (request "Submit a proof of q1.") "reading" == Json.mkObj [("command", Json.mkObj
    [("force", .str "require"), ("act", .str "submit_required"), ("args", toJson ["q1"]),
     ("guard", VE.Route.Wire.encodeFormula .top)]),
  ("fills", Json.arr #[Json.mkObj [("constant", .str "q1"), ("words", .str "q1"), ("span", toJson [18, 20])]]),
  ("query", .null), ("paraphrase", .str "In this task, you are required to submit a proof of q1.")]

/-- A context over a decoded request, its records replaced. -/
def ctxOf (j : Json) (qs : List QueryRecord) (b : Nat := workBudget) : Option Context :=
  (Run.decodeRequest j).toOption.map fun q => { q.ctx with queries := qs, b }

-- P4 over `E_web` (no proof predicate), and P8 at budget 0.
#guard ((ctxOf (request "x" (env := E_web)) [⟨"q1", approvedDraft⟩]).map fun c =>
  readInstruction c "Prove that draft is approved using these premises.") ==
    some (.refused "MissingObligationRole" "{0} submit a proof of {1}")
#guard ((ctxOf (request "x") [⟨"q1", atlasReviewed⟩] 0).map (readInstruction · proveAtlas)) == some .limit

/-! ## O7: the budget is `workBudget`; O10: a proof wording over 400 bytes is `limit` before it is read -/

#guard ((Run.decodeRequest (request proveAtlas)).toOption.map (·.ctx.b)) == some workBudget
def proveSpaced (n : Nat) : String := "Prove that atlas" ++ "".pushn ' ' (n - 50) ++ " is reviewed using these premises."
#guard [(proveSpaced 400).utf8ByteSize, (proveSpaced 401).utf8ByteSize] == [400, 401]
#guard get (request (proveSpaced 400) [("q1", atlasReviewed)]) "outcome" == .str "one"
#guard get (request (proveSpaced 401) [("q1", atlasReviewed)]) "outcome" == .str "limit"

/-! ## O2: an ambiguous sentence lists one proof reading per reading that is exactly one record's target -/

def goProof : Json :=
  envOf ["user", "query"]
    [obligation "go_a_required" ["user"] "{0} go", obligation "go_b_required" ["user"] "{0} Go",
     withDual "submit_required" ["user", "query"] Texts.proofAct "submit_permitted",
     permission "submit_permitted" ["user", "query"] Texts.proofAct]
    [("reader", "user"), ("q1", "query"), ("q2", "query"), ("q3", "query")] "t" (some ("user", "reader")) []

def proveGo : String := "Prove that reader must go using these premises."
def proofOf (q : String) : Reading := ⟨.require, "submit_required", [⟨q, q⟩], .top⟩

#guard (Run.decodeRequest (request proveGo [("q1", goA), ("q2", goB)] (env := goProof))).toOption.map (fun q =>
  readInstruction q.ctx q.s) == some (.many [proofOf "q1", proofOf "q2"])
#guard refuses (request proveGo [("q1", goA)] (env := goProof)) "QueryMismatch" "u1"
#guard refuses (request proveGo [("q1", goA), ("q2", goA), ("q3", goB)] (env := goProof)) "QueryMismatch" "u1"
#guard ((get (request proveGo [("q1", goA), ("q2", goB)] (env := goProof)) "readings").getArr?.toOption.map
  (·.size)) == some 2

/-- `n` distinct targets, each one record's: `many` up to `readingsBound`, then `limit`. -/
def targets (n : Nat) : List VE.Formula := (List.range n).map fun i => .unary "reviewed" (.const s!"c{i}")
#guard [2, readingsBound, readingsBound + 1].map (fun n => (ctxOf (request "x") ((targets n).zipIdx.map fun (t, i) =>
  ⟨s!"q{i}", t⟩)).map fun c => match proofMany c (targets n) with
    | .many rs => rs.length
    | _ => 0) == [some 2, some readingsBound, some 0]

/-! ## The request: echoed id, unit and legend; refusals before reading -/

def youBob : Json := proofEnv (some ("user", "bob"))
#guard get (request "Click Check." (id := "r2") (unit := "u2") (env := youBob)) "unit" == .str "u2"
#guard (Run.caseReported (request "Click Check." (id := "r2") (unit := "u2") (env := youBob))).getObjValD "id" == .str "r2"
#guard get (request "Click Check.") "legend" ==
  toJson ["This document is task t1.", "In this task, you are alice.", "In this task, the token is token1."]
#guard get (request "Click Check." (env := youBob)) "legend" ==
  toJson ["This document is task t1.", "In this task, you are bob.", "In this task, the token is token1."]
#guard (get (request "  Do not share the token.") "reading").getObjValD "fills" ==
  Json.arr #[Json.mkObj [("constant", .str "token1"), ("words", .str "the token"), ("span", toJson [15, 24])]]
#guard ((get (request "Review the meaning." (env := E_web)) "readings").getArr?.toOption.map (·.size)) == some 2

/-- A tree no JSON parser builds (`Scope/Examples.lean`'s F-raw), as the environment. -/
def rawEnv : Json := .obj ⟨⟨Std.DTreeMap.Internal.Impl.inner 2 "a" (.bool true) .leaf (.inner 1 "0" (.bool false) .leaf .leaf)⟩⟩
#guard (Run.caseReported ((request "Click Check.").setObjVal! "environment" rawEnv)).getObjValD "error" ==
  .str "InvalidInput: the request is not a well-formed JSON tree"
#guard (Run.caseReported ((request "Click Check.").setObjVal! "lexicon" (lexJson E_web))).getObjValD "status" == .str "error"
#guard (Run.caseReported (request proveAtlas [("q1", atlasReviewed), ("q1", beaconReviewed)])).getObjValD "error" ==
  .str "InvalidInput: duplicate query"
#guard (Run.caseReported (request proveAtlas [("atlas", atlasReviewed)])).getObjValD "error" == .str "InvalidInput: query"

/-! ## R16's mutants: each field of the answer, each record and the proof predicate's place -/

#guard refuses (request "Please prove that atlas is reviewed using these premises." [("q1", atlasReviewed)])
  "InvalidInput" "please needs author approval"
#guard [get (request proveAtlas) "class", get (request "Prove that atlas is wonderful using these premises.") "class"] ==
  [.str "VEError", .str "SyntaxError"]
#guard [get (request (proveSpaced 401)) "text", get (request "Click Check.") "wording"] ==
  [.str Texts.limitText, .str "Click Check."]
#guard get (request proveGo [("q1", goA), ("q2", goB)] (env := goProof)) "outcome" == .str "many"
#guard get (request "Review the meaning." (env := E_web)) "outcome" == .str "many"
#guard [[("q1", atlasReviewed), ("atlas", beaconReviewed)], [("atlas", beaconReviewed), ("q1", atlasReviewed)]].all
  fun qs => (Run.caseReported (request proveAtlas qs)).getObjValD "error" == .str "InvalidInput: query"
#guard (Run.caseReported (request proveAtlas [("atlas", atlasReviewed)] (id := "r9"))).getObjValD "id" == .str "r9"
#guard get (request proveAtlas [("zq", atlasReviewed)] (env := proofEnv (consts := [("zq", "query")]))) "reading" ==
  proofOne "zq"
-- The proof predicate first among the regulated declarations.
#guard ((ctxOf (request "x") [⟨"q1", atlasReviewed⟩]).map fun c =>
  readInstruction { c with se := { c.se with ne := { c.se.ne with regulated := c.se.ne.regulated.reverse } } }
    proveAtlas) == some (.one (proofOf "q1"))

#guard [request proveAtlas [("q1", atlasReviewed)], request proveAtlas, request "Click Check." (env := youBob),
  request proveGo [("q1", goA), ("q2", goB)] (env := goProof), request (proveSpaced 401),
  request "You may share the token."].all encodes

end VE.Commands.RunExamples
