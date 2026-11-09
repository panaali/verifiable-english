import VE.Commands.Steps
import VE.Commands.Examples

/-! The fixtures of docs/spec/commands-imperatives.md section 7 (CI-3, item ci-3a): `readStep` over `E_web`
("Fixtures (computed over `E_web`)"), the constructed aggregation rows, and finding (d)'s refused step. -/

namespace VE.Commands.StepsExamples

open Lean (Json)
open VE.Commands.Examples (E_web envOf obligation read lexOf web approvedDraft noReadingOutcome)
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

def noStep : StepOutcome := .refused "InvalidInput" "no single speech-act reading"

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
  | .refused code text => code == "NoDerivation" && (text.splitOn "'is approvable'").length > 1 &&
    step "If draft is approvable, click Ask." == .refused code text
  | _ => false
#guard step "Then click Use this wording under the one you mean." == noStep
#guard web "Click Use this wording under the one you mean." == noReadingOutcome
#guard step "If draft is approved, click Check rule conflict, then click Ask." == .refused "ConditionScope" conditionScopeText
#guard conditionScope == .refused "ConditionScope" conditionScopeText
#guard step "Click Ask, if draft is approved, then click Ask." == .refused "ConditionScope" conditionScopeText
#guard step "Review the meaning, if draft is approved, then click Ask." == conditionScope
#guard step "Add an exception or precedence, then check for a conflict in plain English." ==
  noStep
#guard step "Add an exception or precedence, then click Ask." == noStep
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
  noStep
#guard combineShapes ((List.range (readingsBound + 1)).map fun i => (.core (toString i), .one ask false)) == .limit
#guard match combineShapes ((List.range readingsBound).map fun i => (.core (toString i), .one ask false)) with
  | .many alts => alts.length == readingsBound
  | _ => false
#guard combineShapes [(.core "a", .one ask false), (.core "b", .refused "NoDerivation" "x")] == .one ask false
-- A `many` first step and a `one` second keep the second reading in every alternative.
#guard readingTuples [[reviewMeaning, reviewIt], [ask]] == [[reviewMeaning, ask], [reviewIt, ask]]
#guard readingTuples [[ask], [reviewMeaning, reviewIt]] == [[ask, reviewMeaning], [ask, reviewIt]]
#guard readingTuples [[ask], []] == []
-- A stopped step (budget 0 stops the condition) is `limit` unless a step refused.
#guard web "Click Ask." 0 == .one ask
#guard web "Click Ask, if draft is approved." 0 == .limit
#guard step "Click Ask, then click Ask, if draft is approved." 0 == .limit
#guard step "Add an exception or precedence, then click Ask, if draft is approved." 0 ==
  noStep
#guard step "Click Ask, if draft is approved, then add an exception or precedence." 0 ==
  noStep

/-! ## The product is charged before it is built (reviews/dri-decisions-20261109-ci-3a.md item 1) -/

/-- The first `n` spellings of `w` with its letters in either case, one obligation each: the wording `w` then has `n`
readings (64 is the most regulated predicates an environment declares). -/
def spellings (w : String) (n : Nat) : List (String × Json) := (List.range n).map fun i =>
  obligation s!"{w}{i}_required" ["user"]
    ("{0} " ++ String.mk ((w.toList.zipIdx).map fun (c, k) => if (i >>> k) % 2 == 1 then c.toUpper else c))

def spelled (preds : List (String × Json)) : Json := envOf ["user"] preds [("reader", "user")] "t" (some ("user", "reader")) []
def wideEnv : Json := spelled (spellings "review" 64)

#guard match read wideEnv "Review." with
  | .many rs => rs.length == readingsBound
  | _ => false
#guard productSize [[ask, check], [ask], []] == 0 && productSize [[ask, check], [ask, check, ask], [ask, check]] == 12
-- Eight steps of 64 readings: 64^8 products, `limit` without building one. Built eagerly it would not end, so it is
-- read only once the charge is installed and counts (a mutant sweep blanks a broken `@[csimp]`).
open Lean Elab Command in
#eval show CommandElabM Unit from do
  let installed := (Lean.Compiler.CSimp.ext.getState (← getEnv)).map.contains ``shapeOutcome
  let steps := if installed then 8 else 0
  unless installed && productSize (List.replicate steps (List.replicate readingsBound ask)) > maxCandidates do
    throwError "the product is not charged before it is built"
  unless readS wideEnv (", then ".intercalate (List.replicate steps "Review") ++ ".") == .limit do
    throwError "eight steps of 64 readings are not `limit`"
-- Two steps of 8 readings: exactly `readingsBound` complete alternatives.
#guard match readS (spelled (spellings "review" 8 ++ spellings "listen" 8)) "Review, then listen." with
  | .many alts => alts.length == readingsBound
  | _ => false
-- Two steps: 4096 products, within `maxCandidates`, more than `readingsBound` alternatives.
#guard readS wideEnv "Review, then review." == .limit

/-! ## The wording's bytes are charged before its shapes (reviews/dri-decisions-20261109-ci-3a-wording.md item 1) -/

-- About 6 KB with one `, ` every 3 bytes: about 2000 `preposed` shapes, never built.
#guard step ("If " ++ ", ".intercalate (List.replicate 2000 "a") ++ ", click Ask.") == .limit
-- Two steps that each read alone, 400 bytes and more in all: `limit`, where the uncharged body gives `steps`.
def padded : String := String.mk (List.replicate 380 ' ') ++ " click Ask"
#guard shapes ("Click Check rule conflict, then" ++ padded ++ ".") == [.seq ["Click Check rule conflict", padded.drop 1]]
#guard web (capitalise (padded.drop 1) ++ ".") == .one ask
#guard step ("Click Check rule conflict, then" ++ padded ++ ".") == .limit

/-! ## `lift`, `shapeAlts` and `reads` -/

#guard lift (.after "x") true (.one ask) == .one ask true
#guard lift (.core "x") false (.many [ask, check]) == .many [.shape (.core "x") [ask], .shape (.core "x") [check]]
#guard lift (.core "x") false .limit == .limit
#guard lift (.core "x") false (.refused "a" "b") == .refused "a" "b"
#guard shapeAlts (.core "x") (.one ask false) == [.shape (.core "x") [ask]]
#guard shapeAlts (.seq ["x", "y"]) (.steps [ask, check]) == [.shape (.seq ["x", "y"]) [ask, check]]
#guard shapeAlts (.core "x") .limit == [] && shapeAlts (.core "x") (.refused "a" "b") == []
-- Later batches' alternatives pass through `many` unchanged; `mixed` (CI-7b) is no completed shape alternative.
#guard let fs := [Form.command, .supposition, .permission, .conditionalClaim, .remark, .heading].map Alt.form
  shapeAlts (.core "x") (.many (fs ++ [.purpose ask "p"])) == fs ++ [.purpose ask "p"] &&
    shapeAlts (.core "x") (.mixed ask "p") == [] && combineShapes [(.core "x", .mixed ask "p")] == noStep
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
