import VE.Commands.RunExamples

/-! The split of reviews/dri-decisions-20261104-ci-2.md item 1: `readInstruction_refused_classed_of` and
`readInstruction_typed_of_facts` take ci-1b's statements and ci-1's facts, no stronger hypothesis. -/

namespace VE.Commands.RunSplit

open VE.SpeechActs (Scope)
open VE.SpeechActs.Wire (SpeechEnvironment decodeSpeechEnvironmentFull)
open VE.EnglishGrammar (Env Lexicon)

/-- Condition (i): with ci-1b's `refused_classed` (spec section 3) and `guardOf_classed` (`Read.lean` at df2dee88b),
each as written, the spec's `readInstruction_refused_classed` holds as stated. -/
theorem readInstruction_refused_classed_of_ci1b
    (refused_classed : ∀ (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat) (s code text : String),
      readCommand se sc E L b s = .refused code text → (Texts.classOf code).isSome = true)
    (guardOf_classed : ∀ (se : SpeechEnvironment) (E : Env) (L : Lexicon) (b : Nat) (c code text : String),
      guardOf se E L b c = .error (.unread code text) → (Texts.classOf code).isSome = true)
    (ctx : Context) (s code text : String) (h : readInstruction ctx s = .refused code text) :
    (Texts.classOf code).isSome = true :=
  readInstruction_refused_classed_of ctx s code text (refused_classed ctx.se ctx.sc ctx.E ctx.L ctx.b s)
    (guardOf_classed ctx.se ctx.E ctx.L ctx.b) h

/-- `readInstruction_typed_of_facts`' `hf` is ci-1's `readCommand_typed_of_facts` premise, passed on unchanged. -/
theorem typed_facts_are_ci1s (ctx : Context) (s : String) (r : Reading) (D : VE.SpeechActs.SpeechDoc) (u : String)
    (hf : declared ctx.se = true) (h : readCommand ctx.se ctx.sc ctx.E ctx.L ctx.b s = .one r)
    (hE : D.E = ctx.se.ne.rv.environment) (hS : D.scope = ctx.sc) (hR : D.regulated = ctx.se.ne.regulated)
    (hk : VE.SpeechActs.scopeOk D = true) : VE.SpeechActs.commandOk D (r.command u) = true :=
  readCommand_typed_of_facts ctx.se ctx.sc ctx.E ctx.L ctx.b s r D u hf h hE hS hR hk

/-! Condition (ii): ci-1's facts hold of the web fixture's and this item's decoded environments. -/

#guard [Examples.E_web, RunExamples.proofEnv, RunExamples.youBob, RunExamples.goProof].all fun j =>
  match decodeSpeechEnvironmentFull j with
  | .ok se => declared se
  | .error _ => false

end VE.Commands.RunSplit
