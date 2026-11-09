import VE.Commands.Steps
import VE.Commands.Examples

/-! The fixtures of docs/spec/commands-imperatives.md section 7 (CI-3, item ci-3a): `readStep` over `E_web`
("Fixtures (computed over `E_web`)"), the constructed aggregation rows, and finding (d)'s refused step. -/

namespace VE.Commands.StepsExamples

open Lean (Json)
open VE.Commands.Examples (E_web read lexOf web approvedDraft noReadingOutcome)
open VE.SpeechActs.Wire (decodeSpeechEnvironmentFull readingsBound)
open VE.EnglishGrammar (workBudget)

/-- A wording's step outcome over the environment `j` and its own scope. A fixture that does not decode is its error. -/
def readS (j : Json) (s : String) (b : Nat := workBudget) : StepOutcome :=
  match decodeSpeechEnvironmentFull j, lexOf j with
  | .ok se, .ok (E, L) => readStep se se.scope E L b s
  | .error e, _ | _, .error e => .refused "fixture" e

def step (s : String) (b : Nat := workBudget) : StepOutcome := readS E_web s b

/-- `reads` over `E_web`; a fixture that does not decode reads nothing. -/
def readsWeb (sh : Shape) : Bool :=
  match decodeSpeechEnvironmentFull E_web, lexOf E_web with
  | .ok se, .ok (E, L) => reads se se.scope E L workBudget sh
  | _, _ => false

def ask : Reading := ⟨.require, "click_ask_required", [], .top⟩
def check : Reading := ⟨.require, "click_check_required", [], .top⟩
def reviewMeaning : Reading := ⟨.require, "review_meaning_required", [], .top⟩
def reviewIt : Reading := ⟨.require, "review_required", [⟨"meaning1", "the meaning"⟩], .top⟩

def conditionScopeText : String :=
  "a condition with a sequence of steps: write one sentence per step, with the condition on each step or on the first only"

/-! ## The shapes, the capital and `, then ` -/

#guard capitalise "click Ask" == "Click Ask"
#guard capitalise "" == ""
#guard hasThen "  Click Ask, then click Ask.  " && !hasThen "Click Ask then click Ask." && !hasThen "Click Ask."
#guard shapes "Click Ask." == [.core "Click Ask."]
#guard shapes "Click Ask" == [.core "Click Ask"]
#guard shapes "Then click Ask." == [.after "click Ask"]
#guard shapes "If draft is approved, click Ask." == [.preposed "draft is approved" "click Ask"]
#guard shapes "If draft is approved, click Check rule conflict, then click Ask." ==
  [.preposed "draft is approved" "click Check rule conflict, then click Ask",
   .preposed "draft is approved, click Check rule conflict" "then click Ask"]
#guard shapes "Click Check rule conflict, then click Ask." == [.seq ["Click Check rule conflict", "click Ask"]]
#guard shapes "If draft is approved." == [.core "If draft is approved."]
#guard shapes "A, then b, then c, then d, then e, then f, then g, then h, then i." ==
  [.core "A, then b, then c, then d, then e, then f, then g, then h, then i."]

/-! ## Fixtures (computed over `E_web`) -/

#guard step "Then click Ask." == .one ask true
#guard step "Then click Check rule conflict." == .one check true
#guard step "Click Check rule conflict, then click Ask." == .steps [check, ask]
#guard step "If draft is approved, click Ask." == .one ⟨.require, "click_ask_required", [], approvedDraft⟩ false
#guard match web "Click Ask, if draft is approved." with
  | .one r => step "If draft is approved, click Ask." == .one r false
  | _ => false
#guard match web "Click Ask, if draft is approvable." with
  | .refused code text => code == "NoDerivation" && step "If draft is approvable, click Ask." == .refused code text
  | _ => false
#guard step "Then click Use this wording under the one you mean." == .refused "InvalidInput" "no single speech-act reading"
#guard web "Click Use this wording under the one you mean." == noReadingOutcome
#guard step "If draft is approved, click Check rule conflict, then click Ask." == .refused "ConditionScope" conditionScopeText
#guard conditionScope == .refused "ConditionScope" conditionScopeText
#guard step "Click Ask, if draft is approved, then click Ask." == .refused "ConditionScope" conditionScopeText
#guard step "Add an exception or precedence, then check for a conflict in plain English." ==
  .refused "InvalidInput" "no single speech-act reading"
#guard step "Add an exception or precedence, then click Ask." == .refused "InvalidInput" "no single speech-act reading"
#guard step "Click Check rule conflict." == .one check false
#guard web "Review the meaning." == .many [reviewMeaning, reviewIt]
#guard step "Review the meaning, then click Ask." == .many
  [.shape (.seq ["Review the meaning", "click Ask"]) [reviewMeaning, ask],
   .shape (.seq ["Review the meaning", "click Ask"]) [reviewIt, ask]]
#guard step "Review the meaning." == .many [.shape (.core "Review the meaning.") [reviewMeaning],
  .shape (.core "Review the meaning.") [reviewIt]]

/-! ## Constructed aggregation fixtures for CI-3 -/

-- One complete shape outcome beside a `limit` is `limit`; two beside one are `many` with both.
#guard combineShapes [(.core "a", .one ask false), (.core "b", .limit)] == .limit
#guard combineShapes [(.core "a", .one ask false), (.core "b", .one check true), (.core "c", .limit)] ==
  .many [.shape (.core "a") [ask], .shape (.core "b") [check]]
#guard combineShapes [(.seq ["a", "b"], .steps [check, ask]), (.core "c", .refused "NoDerivation" "x")] ==
  .steps [check, ask]
#guard combineShapes [(.core "a", .refused "NoDerivation" "x"), (.core "b", conditionScope)] == conditionScope
#guard combineShapes [(.core "a", .refused "NoDerivation" "x"), (.core "b", .refused "InvalidInput" "y")] ==
  .refused "InvalidInput" "no single speech-act reading"
#guard combineShapes ((List.range (readingsBound + 1)).map fun i => (.core (toString i), .one ask false)) == .limit
-- A `many` first step and a `one` second keep the second reading in every alternative.
#guard readingTuples [[reviewMeaning, reviewIt], [ask]] == [[reviewMeaning, ask], [reviewIt, ask]]
#guard readingTuples [[ask], [reviewMeaning, reviewIt]] == [[ask, reviewMeaning], [ask, reviewIt]]
#guard readingTuples [[ask], []] == []
-- A stopped step (budget 0 stops the condition) is `limit` unless a step refused.
#guard web "Click Ask." 0 == .one ask
#guard web "Click Ask, if draft is approved." 0 == .limit
#guard step "Click Ask, then click Ask, if draft is approved." 0 == .limit
#guard step "Add an exception or precedence, then click Ask, if draft is approved." 0 ==
  .refused "InvalidInput" "no single speech-act reading"
#guard step "Click Ask, if draft is approved, then add an exception or precedence." 0 ==
  .refused "InvalidInput" "no single speech-act reading"

/-! ## `lift`, `shapeAlts` and `reads` -/

#guard lift (.after "x") true (.one ask) == .one ask true
#guard lift (.core "x") false (.many [ask, check]) == .many [.shape (.core "x") [ask], .shape (.core "x") [check]]
#guard lift (.core "x") false .limit == .limit
#guard lift (.core "x") false (.refused "a" "b") == .refused "a" "b"
#guard shapeAlts (.core "x") (.one ask false) == [.shape (.core "x") [ask]]
#guard shapeAlts (.seq ["x", "y"]) (.steps [ask, check]) == [.shape (.seq ["x", "y"]) [ask, check]]
#guard shapeAlts (.core "x") .limit == [] && shapeAlts (.core "x") (.refused "a" "b") == []
#guard readsWeb (.seq ["Review the meaning", "click Ask"]) && readsWeb (.after "click Ask")
#guard !readsWeb (.seq ["Add an exception or precedence", "click Ask"]) && !readsWeb (.core "Then click Ask.")

/-! ## Finding (d): a sequence with a refused step; the step outcomes are read alone (O8: code checked only) -/

#guard shapes "Click Ask, then add an exception or precedence." == [.seq ["Click Ask", "add an exception or precedence"]]
#guard ["Click Ask", "add an exception or precedence"].map (fun x => web (capitalise x ++ ".")) ==
  [.one ask, noReadingOutcome]
#guard match step "Click Ask, then add an exception or precedence." with
  | .refused code _ => code == "InvalidInput"
  | _ => false

end VE.Commands.StepsExamples
