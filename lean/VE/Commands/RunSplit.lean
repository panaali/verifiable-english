import VE.Commands.RunExamples
import VE.SpeechActs.Source.Run

/-! The spec's two end-to-end statements of CI-2 (docs/spec/commands-imperatives.md section 6), as written there
with `hw` beside `hd` (reviews/dri-decisions-20261102-ci-1.md item 1), proved through ci-1b's `refused_classed`,
`guardOf_classed` and `readCommand_typed` (ci-2b). They replace ci-2's split (reviews/dri-decisions-20261104-ci-2.md
item 1): `readInstruction_refused_classed_of` and `readInstruction_typed_of_facts` stay in `Run.lean` as the lemmas
these proofs use. -/

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
    (h : readInstruction ctx s = .one r)
    (hE : D.E = ctx.se.ne.rv.environment) (hS : D.scope = ctx.sc) (hR : D.regulated = ctx.se.ne.regulated)
    (hk : VE.SpeechActs.scopeOk D = true)
    (hq : ∀ q ∈ ctx.queries, (q.id, "query") ∈ ctx.se.ne.rv.vocabulary.constants) :
    VE.SpeechActs.commandOk D (r.command u) = true := by
  cases ht : proofTask ctx s with
  | none =>
    rw [readInstruction_command ctx s ht] at h
    exact readCommand_typed ctx.se ctx.sc ctx.E ctx.L ctx.b s j r D u hw hd h hE hS hR hk
  | some _ =>
    exact readInstruction_typed_of_facts ctx s r D u (declared_of_decode hw hd) h hE hS hR hk hq

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

/-- Units `(id, kind, line, content)` laid end to end; a fenced unit (`content` none) reads its own line. -/
def payload (units : List (String × String × String × Option Json)) (resolved : List (String × Json))
    (ctx : Bool := true) (extra : List (String × Json) := []) : Json := Id.run do
  let mut start := 0
  let mut rows := #[]
  for (id, kind, line, content) in units do
    rows := rows.push (Json.mkObj [("id", .str id), ("span", toJson [start, start + line.utf8ByteSize]),
      ("kind", .str kind), ("meaning", .str "specified"), ("support", .str "none"),
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
-- The fences Python resolves, charged against `maxCases` before any is read (asserted fences, none resolved).
def fenced (n : Nat) : Json :=
  payload ((List.range n).map fun i => (s!"a{i}", "asserted", "Atlas is reviewed.\n", none)) [] (ctx := false)
#guard result (fenced VE.Limits.maxCases) == "NotImplemented: fenced English content"
#guard result (fenced (VE.Limits.maxCases + 1)) == s!"ResourceLimit: speech fences exceed {VE.Limits.maxCases}"

end SourceExamples

end VE.Commands
