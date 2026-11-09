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
      se.scope with
    | .error e => e == "InvalidInput: the request is not a well-formed JSON tree"
    | .ok _ => false
  | .error _ => false

end VE.Commands
