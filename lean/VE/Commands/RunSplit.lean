import VE.Commands.RunExamples
import VE.SpeechActs.Source.Run

/-! The spec's two end-to-end statements of CI-2 (docs/spec/commands-imperatives.md section 6), as written there
with `hw` beside `hd` (reviews/dri-decisions-20261102-ci-1.md item 1), proved through ci-1b's `refused_classed` and
`guardOf_classed` (ci-2b). Since CI-3, `readInstruction` returns `StepOutcome` (section 7): `readInstruction_typed`'s
premise `h` takes section 7's step form and the theorem is `readInstruction_typed_step` (ci-3). They replace ci-2's
split (reviews/dri-decisions-20261104-ci-2.md item 1): `readInstruction_refused_classed_of` and
`readInstruction_typed_of_facts` stay in `Run.lean` as the lemmas these proofs use. -/

namespace VE.Commands

open VE.SpeechActs (Scope)
open VE.SpeechActs.Wire (decodeSpeechEnvironmentFull)

theorem readInstruction_refused_classed (ctx : Context) (s code text : String)
    (h : readInstruction ctx s = .refused code text) : (Texts.classOf code).isSome = true :=
  readInstruction_refused_classed_of ctx s code text (refused_classed ctx.se ctx.sc ctx.E ctx.L ctx.b s)
    (guardOf_classed ctx.se ctx.E ctx.L ctx.b) h

theorem readInstruction_typed (j : Lean.Json) (ctx : Context) (r : Reading) (D : VE.SpeechActs.SpeechDoc) (u : String)
    (hw : VE.Scope.JsonWF j)
    (hd : VE.SpeechActs.Wire.decodeSpeechEnvironmentFull j = .ok ctx.se)
    (h : (∃ x, readInstruction ctx s = StepOutcome.one r x) ∨
      ∃ rs, readInstruction ctx s = StepOutcome.steps rs ∧ r ∈ rs)
    (hE : D.E = ctx.se.ne.rv.environment) (hS : D.scope = ctx.sc) (hR : D.regulated = ctx.se.ne.regulated)
    (hk : VE.SpeechActs.scopeOk D = true)
    (hq : ∀ q ∈ ctx.queries, (q.id, "query") ∈ ctx.se.ne.rv.vocabulary.constants) :
    VE.SpeechActs.commandOk D (r.command u) = true :=
  readInstruction_typed_step j ctx r D u hw hd h hE hS hR hk hq

/-! ci-1's facts hold of the web fixture's and ci-2's decoded environments (each passes `jsonWF?`, so
`declared_of_decode` applies to them). -/

#guard [Examples.E_web, RunExamples.proofEnv, RunExamples.youBob, RunExamples.goProof].all fun j =>
  VE.Scope.jsonWF? j && match decodeSpeechEnvironmentFull j with
  | .ok se => declared se
  | .error _ => false

/-! The source wrapper discharges `hw` as the mode does: its reading context goes through `Run.decodeRequest`, whose
`jsonWF?` refuses a tree no parser builds (F-raw, here as the context's lexicon) before any decoder reads it. -/

#guard match decodeSpeechEnvironmentFull RunExamples.proofEnv with
  | .ok se => match VE.SpeechActs.Source.commandContext
      (Lean.Json.mkObj [("reading_context", Lean.Json.mkObj [("lexicon", RunExamples.rawEnv)])]) RunExamples.proofEnv
      se se.scope with
    | .error e => e == "InvalidInput: the request is not a well-formed JSON tree"
    | .ok _ => false
  | .error _ => false

/-! ## The source wrapper's A2 reading (ci-2b): R16's fixtures for `readSource` and `decodeSpeechSource`

A `ve-document@2` payload over `proofEnv` whose units are command fences (`Click Check.`, `Do not share the token.`),
resolved as Lean reads them, with the reading context Python sends (the lexicon of the environment under its
effective scope). -/

namespace SourceExamples

open Lean (Json toJson)
open VE.SpeechActs.Source (decodeSpeechSource readingContextText)

def env : Json := RunExamples.proofEnv

/-- The lexicon of `env` under its effective scope, as `ve/speech_document.py` exports it. -/
def context : Json :=
  match decodeSpeechEnvironmentFull env with
  | .ok se => Json.mkObj [("lexicon", RunExamples.lexJson (env.setObjVal! "speech_acts"
      (VE.SpeechActs.Wire.encodeScope se.scope)))]
  | .error _ => .null

def click : Json := Json.mkObj [("force", .str "require"), ("act", .str "click_required"), ("args", toJson ["check"]),
  ("guard", toJson ["top"])]
def share : Json := Json.mkObj [("force", .str "forbid"), ("act", .str "share_permitted"), ("args", toJson ["token1"]),
  ("guard", toJson ["top"])]

/-- Units `(id, kind, line, content)` laid end to end (a `kind` that is JSON text, a nested kind, is parsed); a fenced unit (`content` none) reads its own line. -/
def payload (units : List (String × String × String × Option Json)) (resolved : List (String × Json))
    (ctx : Bool := true) (extra : List (String × Json) := []) : Json := Id.run do
  let mut start := 0
  let mut rows := #[]
  for (id, kind, line, content) in units do
    rows := rows.push (Json.mkObj [("id", .str id), ("span", toJson [start, start + line.utf8ByteSize]),
      ("kind", (Json.parse kind).toOption.getD (.str kind)), ("meaning", .str "specified"), ("support", .str "none"),
      ("content", content.getD (Json.mkObj [("fence", .str id)]))] |>.setObjVal! "surface" (.str "english"))
    start := start + line.utf8ByteSize
  Json.mkObj ([("metadata", Json.mkObj ([("format", .str "ve-document@2"), ("environment", env),
      ("units", .arr rows)] ++ extra)),
    ("source", .str (String.join (units.map (·.2.2.1)))),
    ("fences", Json.mkObj (units.filterMap fun (id, _, line, c) => if c.isNone then some (id, .str line) else none))] ++
    (if resolved.isEmpty then [] else
      [("resolved_fences", Json.mkObj (resolved.map fun (id, c) => (id, Json.mkObj [("command", c)])))]) ++
    if ctx then [("reading_context", context)] else [])

def two : List (String × String × String × Option Json) :=
  [("c1", "instruction", "Click Check.\n", none), ("c2", "instruction", "Do not share the token.\n", none)]

def result (p : Json) : String :=
  match decodeSpeechSource p .null with
  | .ok _ => "ok"
  | .error e => e

def mismatch : String := "InvalidInput: resolved speech fences"

#guard result (payload two [("c1", click), ("c2", share)]) == "ok"
#guard result (payload two [("c1", click), ("c2", share)] (ctx := false)) == readingContextText
#guard result (payload two [("c1", share), ("c2", share)]) == mismatch
#guard result (payload two [("c1", click), ("c2", click)]) == mismatch
#guard result (payload [("c1", "instruction", "Click Nothing.\n", none)] [("c1", click)]) == mismatch
-- No fence: no reading context is needed.
#guard result (payload [("c1", "instruction", "Click Check.\n", some (Json.mkObj [("command", click)]))] []
  (ctx := false)) == "ok"
-- Without the context the command is not read: a later fault of the document is the one reported.
#guard result (payload two [("c1", click), ("c2", share)] (ctx := false) (extra := [("weights", .num 5)])) ==
  "invalid removable reading weights"
-- 3.2 (ci-2b F1): a resolved fence decodes to the role its kind reads (`Wire.roleFits`). A fence of a kind wrapping
-- `instruction` resolved as a formula is refused, never dropped unread: plain, attributed, hedged and a `MIXED` part;
-- so is a question or norm fence resolved as a formula. An attributed command is still read (and dormant).
def resolving (p : Json) (resolved : List (String × Json)) : Json :=
  p.setObjVal! "resolved_fences" (Json.mkObj resolved)
def formula : Json := Json.mkObj [("ast", toJson ["top"])]
def attributed : String := "[\"attributed\", \"bob\", \"says\", \"instruction\"]"
def hedged : String := "[\"hedged\", \"likely\", \"instruction\"]"
def one (kind line : String) : List (String × String × String × Option Json) := [("c1", kind, line, none)]
/-- `p` with its units as the `CHECKED` parts of one `MIXED` unit `m`. -/
def mixed (p : Json) : Json :=
  let md := p.getObjValD "metadata"
  let parts := match md.getObjValD "units" with
    | .arr us => Json.arr (us.map (·.setObjVal! "status" (.str "CHECKED")))
    | j => j
  md.setObjVal! "units" (Json.arr #[Json.mkObj [("id", .str "m"),
      ("span", toJson [0, (p.getObjValD "source").getStr?.toOption.getD "" |>.utf8ByteSize]),
      ("status", .str "MIXED"), ("parts", parts)]]) |> p.setObjVal! "metadata"
#guard result (payload (one "instruction" "Click Check.\n") [("c1", click)]) == "ok"
#guard [one "instruction" "Click Check.\n", one attributed "Click Check.\n", one hedged "Click Check.\n",
    one "question" "Is atlas reviewed?\n", one "norm" "Click Check.\n"].all fun units =>
  result (resolving (payload units []) [("c1", formula)]) == mismatch
#guard result (mixed (payload two [("c1", click), ("c2", share)])) == "ok"
#guard result (mixed (resolving (payload two []) [("c1", formula), ("c2", Json.mkObj [("command", share)])])) ==
  mismatch
-- Every resolved fence is checked, not only the first: the formula second.
#guard result (resolving (payload two []) [("c1", Json.mkObj [("command", click)]), ("c2", formula)]) == mismatch
#guard result (payload (one attributed "Click Check.\n") [("c1", click)]) == "ok"
#guard result (payload (one attributed "Click Check.\n") [("c1", share)]) == mismatch
-- An asserted fence resolved as a formula is its assertion.
#guard result (resolving (payload (one "asserted" "Atlas is reviewed.\n") [] (ctx := false)) [("c1", formula)]) ==
  "ok"
-- ci-3: the `ThenWithoutStep` check reads each unit's own effective kind: an instruction `Then` unit after an asserted
-- one is refused, and so is an asserted `Then` unit with a signed `instruction` choice after an instruction.
def cmd : Json := Json.mkObj [("command", click)]
def signed (u : String) : Json := Json.mkObj [("id", .str "rs"), ("unit", .str u), ("version", toJson 1),
  ("status", .str "authored"), ("signature", .str "author"), ("readings", toJson [Json.mkObj [("id", .str "r"),
    ("kind", .str "instruction"), ("meaning_id", .str "candidate"), ("content", cmd), ("admission",
      Json.mkObj [("who", .str "author"), ("why", .str "reproducer"), ("distinguishing_models", Json.mkObj [])])]])]
def thenText : String := "ThenWithoutStep: a Then step names no earlier instruction step as its antecedent; " ++
  "write the steps in one sentence, joined by ', then ' (unit t)"
#guard result (payload [("a", "asserted", "Atlas is reviewed.\n", some formula),
  ("t", "instruction", "Then click Check.\n", some cmd)] [] (ctx := false)) == thenText
#guard [result (payload [("c1", "instruction", "Click Check.\n", some cmd), ("t", "asserted", "Then click Check.\n",
    some formula)] [] (ctx := false) (extra := [("reading_sets", toJson [signed "t"])])),
  result (payload [("t", "asserted", "Then click Check.\n", some formula), ("c1", "instruction", "Click Check.\n",
    some cmd)] [] (ctx := false) (extra := [("reading_sets", toJson [signed "t"])])),
  result (payload [("c1", "instruction", "Click Check.\n", some cmd), ("t", "asserted", "Then click Check.\n",
    some formula)] [] (ctx := false))] == [thenText, thenText, "ok"]
-- ci-3 (review F2): the document form of a sequence is one instruction unit whose `MIXED` parts are its steps; each
-- part's command (explicit, resolved or chosen) is checked against `readStep` of the whole wording, under the reading
-- context. Reversed steps are refused for plain, attributed and hedged parts, and for a chosen part; a unit carrying
-- one command for a two-step wording, a sequence with a non-instruction part, and one with no context are refused.
def seqText (m : String) : String :=
  s!"{Texts.sequenceParts.1}: {Texts.sequenceParts.2} (unit {m})"
def seqUnits (k : String) (c1 c2 : Json) : List (String × String × String × Option Json) :=
  [("a", k, "Click Check", some (Json.mkObj [("command", c1)])),
   ("b", k, ", then do not share the token.\n", some (Json.mkObj [("command", c2)]))]
#guard result (mixed (payload (seqUnits "instruction" share click) [] (ctx := false))) == readingContextText
#guard ["instruction", attributed, hedged].all fun k =>
  result (mixed (payload (seqUnits k share click) [])) == seqText "m" &&
    result (mixed (payload (seqUnits k click share) [])) == "ok"
#guard result (payload [("u", "instruction", "Click Check, then do not share the token.\n", some cmd)] []) == seqText "u"
#guard result (mixed (payload [("a", "instruction", "Click Check", some cmd),
  ("b", "asserted", ", then do not share the token.\n", some formula)] [])) == seqText "m"
#guard result (mixed (payload [("a", "instruction", "Click Check", some cmd), ("b", "instruction", ", then click Check", some cmd),
  ("c", "instruction", ", then do not share the token.\n", some (Json.mkObj [("command", share)]))] [])) == "ok" &&
  result (mixed (payload [("a", "instruction", "Click Check", some cmd), ("b", "instruction",
    ", then click Check, then do not share the token.\n", some cmd)] [])) == seqText "m"
-- A chosen part is read through its signed choice: reversed, the sequence is refused; in order, the sequence check
-- passes and the parts' stated status is the next fault.
#guard result (mixed (payload [("a", "asserted", "Click Check", some formula), ("b", "instruction",
    ", then do not share the token.\n", some cmd)] [] (extra := [("reading_sets", toJson [signed "a"])]))) == seqText "m" &&
  result (mixed (payload [("a", "asserted", "Click Check", some formula), ("b", "instruction",
    ", then do not share the token.\n", some (Json.mkObj [("command", share)]))] []
    (extra := [("reading_sets", toJson [signed "a"])]))) != seqText "m"
-- The stated order is derived content of the decoded source: the sequence's consecutive steps.
#guard (match decodeSpeechSource (mixed (payload (seqUnits "instruction" click share) [])) .null with
  | .ok s => s.1.stepOrder
  | .error _ => []) == [("m.1", "m.2")]
#guard (match decodeSpeechSource (payload two [("c1", click), ("c2", share)]) .null with
  | .ok s => (s.1.stepOrder, s.1.sequences.length)
  | .error _ => ([("", "")], 1)) == ([], 0)
-- The fences Python resolves, charged against `maxCases` before any is read (asserted fences, none resolved).
def fenced (n : Nat) : Json :=
  payload ((List.range n).map fun i => (s!"a{i}", "asserted", "Atlas is reviewed.\n", none)) [] (ctx := false)
#guard result (fenced VE.Limits.maxCases) == "NotImplemented: fenced English content"
#guard result (fenced (VE.Limits.maxCases + 1)) == s!"ResourceLimit: speech fences exceed {VE.Limits.maxCases}"

end SourceExamples

end VE.Commands
