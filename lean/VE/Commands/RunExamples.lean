import VE.Commands.Run
import VE.Commands.Examples
import VE.Senses.Run
import VE.SpeechActs.Source.Run
import VE.Commands.StepsExamples

/-! The fixtures of docs/spec/commands-imperatives.md section 6 through the `english.command` mode: the proof task's
rows P1′ to P8, O1's text, O2's readings, O7's budget, O10's byte bound, the request echo, `jsonWF?`'s refusal. -/

namespace VE.Commands.RunExamples

open Lean (Json toJson)
open VE.Commands.Examples
open VE.EnglishGrammar (workBudget)
open VE.SpeechActs.Wire (readingsBound decodeSpeechEnvironmentFull)

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
  readInstruction q.ctx q.s) == some (.many [.shape (.core proveGo) [proofOf "q1"], .shape (.core proveGo) [proofOf "q2"]])
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
    proveAtlas) == some (.one (proofOf "q1") false)

#guard [request proveAtlas [("q1", atlasReviewed)], request proveAtlas, request "Click Check." (env := youBob),
  request proveGo [("q1", goA), ("q2", goB)] (env := goProof), request (proveSpaced 401),
  request "You may share the token."].all encodes

/-! ## CI-5 through the mode: one simple `acts@0` act each; the answer is `encode` of the reader's -/

#guard Examples.choiceRows.all fun (s, a) =>
  let q := request s (env := Examples.E_acts)
  encodes q && (get q "reading").getObjValD "command" == Json.mkObj [("force", .str "require"), ("act", .str a),
    ("args", toJson ([] : List String)), ("guard", VE.Route.Wire.encodeFormula .top)]
#guard (Run.caseReported (request "Click Check and save." (env := Examples.actsEnv Examples.clickSave (some [])))).getObjValD
  "error" == .str "InvalidInput: act phrase for click_required joins acts with 'and' outside a fixed phrase"

/-! ## CI-3 through the mode (section 7): steps, `Then` steps, conditions written first, the stated order -/

def webGet (s k : String) : Json := get (request s (env := E_web)) k
def actOf (j : Json) : Json := (j.getObjValD "command").getObjValD "act"
def spans (j : Json) : List Json := ((j.getObjValD "fills").getArr?.toOption.getD #[]).toList.map (·.getObjValD "span")
def readingsOf (j : Json) : List Json := ((j.getObjValD "readings").getArr?.toOption.getD #[]).toList

-- `readInstruction` is `readStep` outside the proof task (`readInstruction_step`), and the proof task's `lift`.
#guard ((ctxOf (request "x" (env := E_web)) []).map fun c =>
  [readInstruction c "Then click Ask.", readInstruction c "Click Check rule conflict, then click Ask."]) ==
  some [.one ⟨.require, "click_ask_required", [], .top⟩ true,
    .steps [⟨.require, "click_check_required", [], .top⟩, ⟨.require, "click_ask_required", [], .top⟩]]
#guard [webGet "Then click Ask." "outcome", webGet "Then click Ask." "after_previous", actOf (webGet "Then click Ask." "reading"),
  actOf (webGet "Then click Check rule conflict." "reading"), webGet "Click Ask." "after_previous"] ==
  [.str "one", .bool true, .str "click_ask_required", .str "click_check_required", .bool false]
-- The two English lines of section 7: speech-acts' `paraphrase` and `paraphraseSteps`.
#guard (webGet "If draft is approved, click Ask." "reading").getObjValD "paraphrase" ==
  .str "In this task, you are required to click Ask, where the stated condition holds."
#guard webGet "Click Check rule conflict, then click Ask." "paraphrase" == .str ("In this task, you are required to do " ++
  "these in order: first click Check rule conflict, then click Ask. The order is stated; VE does not reason about it.")
#guard (readingsOf (result (request "Click Check rule conflict, then click Ask." (env := E_web)))).map actOf ==
  [.str "click_check_required", .str "click_ask_required"]
-- Spans point into the whole wording: past `If <c>, `, `Then ` and `, then `, and leading spaces.
#guard spans (get (request "If atlas is reviewed, click Check.") "reading") == [toJson [28, 33]]
#guard spans (get (request "Then click Check.") "reading") == [toJson [11, 16]]
#guard (readingsOf (result (request "  Click Check, then do not share the token."))).map spans == [[toJson [8, 13]], [toJson [33, 42]]]
#guard get (request "  Click Check, then do not share the token.") "paraphrase" == .str ("In this task, you are " ++
  "required to do these in order: first click check, then do not share the token. The order is stated; VE does not reason about it.")
-- `many` over two sequences: every reading, and each alternative's shape and positions.
#guard webGet "Review the meaning, then click Ask." "alternatives" == toJson [
  Json.mkObj [("shape", .str "seq"), ("readings", toJson [0, 1])], Json.mkObj [("shape", .str "seq"), ("readings", toJson [2, 3])]]
#guard (readingsOf (result (request "Review the meaning, then click Ask." (env := E_web)))).map spans == [[], [], [toJson [7, 18]], []]
#guard webGet "Review the meaning." "alternatives" == toJson [
  Json.mkObj [("shape", .str "core"), ("readings", toJson [0])], Json.mkObj [("shape", .str "core"), ("readings", toJson [1])]]
#guard [webGet "If draft is approved, click Check rule conflict, then click Ask." "code",
  webGet "If draft is approved, click Check rule conflict, then click Ask." "class",
  webGet "Click Ask, then add an exception or precedence." "code"] == [.str "ConditionScope", .str "VEError", .str "InvalidInput"]
-- AB.md's refused -> refused rows (class rr; reviews/dri-decisions-20261109-ci-3-codes.md item 1, whose condition
-- keeps each one a guard here): each refused through the mode with its exact code, text and class (`ConditionScope`'s
-- `VEError`; the condition reader's `NoDerivation` is a `SyntaxError`, as for a condition written after the command).
-- tests/test_commands_steps.py ties every rr row of AB.json to its row of this table.
def csText : String :=
  "a condition with a sequence of steps: write one sentence per step, with the condition on each step or on the first only"
def abRefused : List (String × String × String × String) := [
  ("Click Ask, if draft is approved, then add an exception or precedence.", "ConditionScope", "VEError", csText),
  ("Click Ask, if draft is approved, then click Ask.", "ConditionScope", "VEError", csText),
  ("Click Ask, then click Ask, if draft is approved.", "ConditionScope", "VEError", csText),
  ("If draft is approvable, click Ask.", "NoDerivation", "SyntaxError", "The condition has no reading with the " ++
    "current vocabulary. Unknown English phrase 'is approvable'. Nearest declared wordings: 'is approved'; 'assistant'; 'calls'."),
  ("If draft is approved, click Check rule conflict, then click Ask.", "ConditionScope", "VEError", csText),
  ("Review the meaning, if draft is approved, then click Ask.", "ConditionScope", "VEError", csText)]
#guard abRefused.all fun (s, code, cls, text) => refuses (request s (env := E_web)) code text && webGet s "class" == .str cls
#guard webGet "Click Ask, if draft is approvable." "class" == .str "SyntaxError"
#guard [request "Then click Ask." (env := E_web), request "Click Check rule conflict, then click Ask." (env := E_web),
  request "Review the meaning, then click Ask." (env := E_web), request "  Click Check, then do not share the token."].all encodes

-- A step's spans start past its leading spaces (readCommand trims them).
#guard spans (get (request "Then  click Check.") "reading") == [toJson [12, 17]] &&
  spans (get (request "If atlas is reviewed,  click Check.") "reading") == [toJson [29, 34]] &&
  (readingsOf (result (request "Click Check, then  click Check."))).map spans == [[toJson [6, 11]], [toJson [25, 30]]]
-- The charges through the mode (ci-3a's fixtures): 400 bytes read and 401 are `limit`; about 6 KB of `preposed`
-- splits is `limit` before any shape is built; `readingsBound` complete sequence alternatives are written in full.
#guard [get (request (StepsExamples.twoSteps 358) (env := E_web)) "outcome",
  get (request (StepsExamples.twoSteps 359) (env := E_web)) "outcome",
  get (request ("If " ++ ", ".intercalate (List.replicate 2000 "a") ++ ", click Ask.") (env := E_web)) "outcome"] ==
  [.str "steps", .str "limit", .str "limit"]
#guard let q := request "Review, then listen." (env := StepsExamples.spelled
    (StepsExamples.spellings "review" 8 ++ StepsExamples.spellings "listen" 8))
  encodes q && ((get q "alternatives").getArr?.toOption.map (·.size)) == some readingsBound &&
    ((get q "readings").getArr?.toOption.map (·.size)) == some (2 * readingsBound)

/-! The stated order (finding (c)): the seven-unit list, the pilot pattern uweb.tour.552_0, a `Then` unit with no
earlier instruction unit, and the two-step counterexample. -/

-- reviews/dri-decisions-20261109-ci-3.md item 1: `readInstruction_typed_step`'s `hw` holds of every ci-3 fixture
-- environment (`rawEnv`, the counterexample, fails `jsonWF?` above).
#guard [E_web, proofEnv, youBob, goProof].all VE.Scope.jsonWF?

def su (id : String) (ins : Bool := true) (steps : Nat := 1) (after : Bool := false) (a : Option String := none) :
    StepUnit := ⟨id, ins, steps, after, a⟩
def seven : List StepUnit := [su "u1", su "u2" (steps := 2), su "u3" (after := true) (a := some "u2"), su "u4" (ins := false),
  su "u5" (after := true) (a := some "u3"), su "u6" (after := true), su "u7" (after := true) (a := some "u4")]
#guard stepOrder seven == [("u2.1", "u2.2"), ("u2.2", "u3"), ("u3", "u5")]
#guard thenWithoutStep seven == ["u6", "u7"]
#guard stepOrder [su "a", su "b" (after := true) (a := some "x")] == [] &&
  thenWithoutStep [su "a", su "b" (after := true) (a := some "x")] == ["b"]
#guard thenWithoutStep [su "t" (after := true)] == ["t"] && stepOrder [su "t" (after := true)] == []
#guard stepNames [su "a", su "b" (steps := 2) (after := true) (a := some "a")] == ["a", "b.1", "b.2"] &&
  stepOrder [su "a", su "b" (steps := 2) (after := true) (a := some "a")] == [("a", "b.1"), ("b.1", "b.2")]
#guard [lastStep (su "b" (steps := 3)), firstStep (su "b" (steps := 3)), lastStep (su "a"), firstStep (su "a")] ==
  ["b.3", "b.1", "a", "a"]
#guard (stepCommands "u9" [⟨.require, "a", [], .top⟩, ⟨.forbid, "b", [], .top⟩]).map (fun c => (c.unit, c.act)) ==
  [("u9.1", "a"), ("u9.2", "b")]
#guard [Texts.classOf "ConditionScope", Texts.classOf "ThenWithoutStep"] == [some "VEError", some "VEError"]

/-! `surfaceKind`'s CI-3 cases ((iii)): `If <c>, <verb> …` and `Then <verb> …` are instructions; SA's (ββ) premise,
an `if` sentence with no comma, stays asserted, as do clauses that do not start with an act verb. -/

def webKind (s : String) : String :=
  match decodeSpeechEnvironmentFull E_web with
  | .ok se => VE.SpeechActs.Wire.surfaceKind se.ne.regulated s
  | .error _ => ""
#guard ["If draft is approved, click Ask.", "Then click Ask.", "  then  CLICK Check rule conflict.", "Click Ask.",
  "If Alice must click Check then Atlas is reviewed.", "If draft is approved, the meaning is reviewed.",
  "Then the draft is approved.", "If draft is approved, click Ask?"].map webKind ==
  ["instruction", "instruction", "instruction", "instruction", "asserted", "asserted", "asserted", "question"]
#guard match decodeSpeechEnvironmentFull E_web with
  | .ok se => ["If draft is approved, click Ask.", "Then click Ask."].all fun w =>
      VE.SpeechActs.Wire.choiceKindConflicts se.ne.regulated (.str "asserted") w &&
      !VE.SpeechActs.Wire.choiceKindConflicts se.ne.regulated (.str "instruction") w
  | .error _ => false

/-! The document check (finding (c), O3): an authored `Then` instruction unit is `ThenWithoutStep`, by its kind,
attributed instructions included; a `Then` wording of another kind, or an instruction that is no `Then` step, is not. -/

def srcUnit (id : String) (kind : Json) (w : String) : VE.SpeechActs.Source.SourceUnit :=
  ⟨id, (0, 0), kind, .null, none, w, none, none, .null⟩
def attributed : Json := toJson [Json.str "attributed", .str "alice", .str "says", .str "instruction"]
#guard VE.SpeechActs.Source.thenFault (·.kind) "" [srcUnit "a" (.str "instruction") "Click Ask.",
    srcUnit "b" (.str "instruction") "Then click Ask."] ==
  some ("ThenWithoutStep: a Then step names no earlier instruction step as its antecedent; write the steps in one " ++
    "sentence, joined by ', then ' (unit b)")
#guard [VE.SpeechActs.Source.thenFault (·.kind) "" [srcUnit "a" (.str "asserted") "Then the draft is approved."],
  VE.SpeechActs.Source.thenFault (·.kind) "" [srcUnit "a" (.str "instruction") "Click Check rule conflict, then click Ask."]] ==
  [none, none]
#guard (VE.Route.Admission.decodeKind 16 attributed).isOk &&
  (VE.SpeechActs.Source.thenFault (·.kind) "" [srcUnit "q" attributed "Then click Ask."]).isSome
-- The effective kind decides: an asserted unit with a signed `instruction` choice is a `Then` step; the reverse is not.
#guard (VE.SpeechActs.Source.thenFault (fun _ => .str "instruction") "" [srcUnit "c" (.str "asserted") "Then click Ask."]).isSome &&
  (VE.SpeechActs.Source.thenFault (fun _ => .str "asserted") "" [srcUnit "c" (.str "instruction") "Then click Ask."]).isNone


/-! R16 fixtures for the trust-mutant survivors of ci-3's sweep (docs/commands-imperatives/ci-3/trust-mutants.json):
more than one space after a cut, a third step, a wording with two shapes, the outcomes no reader writes yet
(`mixed`, a `purpose` alternative), a unit of no step and an antecedent named at the end of the list. -/

#guard [spans (get (request "Then   click Check.") "reading"),
  spans (get (request "If atlas is reviewed,   click Check.") "reading")] == [[toJson [13, 18]], [toJson [30, 35]]]
#guard (readingsOf (result (request "Click Check, then   click Check, then do not share the token."))).map spans ==
  [[toJson [6, 11]], [toJson [26, 31]], [toJson [51, 60]]]
-- Two shapes: two preposed cuts give no single shape; a `Then` step's shape is its `after` cut, never the `seq` one.
#guard Run.oneShape "If atlas is reviewed, click Check, then click Check." false == none &&
  Run.oneShape "Then click Check, then click Check." true == some (.after "click Check, then click Check")
def ck : Reading := ⟨.require, "click_required", [⟨"check", "check"⟩], .top⟩
/-- `outcomeFields` of `o` for the request of `s`, also for an outcome `readInstruction` does not give for `s`. -/
def fieldsOf (s : String) (o : StepOutcome) : Json :=
  match Run.decodeRequest (request s) with
  | .ok q => Json.mkObj (Run.outcomeFields q o)
  | .error _ => .null
#guard spans ((fieldsOf "Then click Check, then click Check." (.one ck true)).getObjValD "reading") == [toJson [11, 16]]
#guard (readingsOf (fieldsOf "Then click Check, then click Check." (.steps [ck, ck]))).all (spans · != [Json.null])
#guard [(fieldsOf "Click Check." (.mixed ck "to pass")).getObjValD "outcome",
  (fieldsOf "Click Check." (.mixed ck "to pass")).getObjValD "purpose",
  actOf ((fieldsOf "Click Check." (.mixed ck "to pass")).getObjValD "reading")] ==
  [.str "mixed", .str "to pass", .str "click_required"]
#guard (Run.altParts (.purpose ck "to pass")).2.length == 1
#guard stepNames [su "z" (steps := 0)] == ["z"] && lastStep (su "z" (steps := 0)) == "z" &&
  firstStep (su "z" (steps := 0)) == "z"
#guard antecedentOf [su "a"] 1 (su "b" (after := true) (a := some "a")) == some (su "a")
-- The named antecedent, not the nearest earlier instruction unit.
#guard stepOrder [su "a", su "b", su "t" (after := true) (a := some "a")] == [("a", "t")]
-- `If <c>, <verb> …` reads the clause after the first comma only.
#guard webKind "If draft is approved, the meaning is reviewed, click Ask." == "asserted"

end VE.Commands.RunExamples
