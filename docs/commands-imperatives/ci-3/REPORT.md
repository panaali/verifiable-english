# ci-3 report: steps, `Then` steps and conditions written first on the `english.command` route

No DELTA row reserves a DRI signature: rows 1-7 cite a signed decision or R3/R16.

Spec: docs/spec/commands-imperatives.md section 7 (the statement gate passed in reviews/dri-decisions-20261102-ci-0.md
item 1). Plan: commands-imperatives-PLAN.md "CI-3. Steps and conditions written first". Branch `feature/ci-3`, merged
with main at d3bb8bfbc (ci-2b and ci-3b in).

## Plan rows delivered

1. **`readInstruction` returns `StepOutcome`** (`lean/VE/Commands/Run.lean`): a proof task's outcome is
   `lift (.core s) false`, else `readStep`. `readInstruction_step` replaces `readInstruction_command`;
   `readInstruction_refused_classed_step` and `readInstruction_typed_step` are proved (no `sorry`, standard axioms).
   Every caller of the old `Outcome` is updated: the mode's encoder (`Run.encode`, `caseReported`),
   `readInstruction_refused_classed_of` and `readInstruction_typed_of_facts` (Run.lean), and after the main merge
   ci-2b's `RunSplit.readInstruction_typed` and the source wrapper's A2 re-read (`Source/Run.lean`,
   `.one r _`). Read.lean and Examples.lean are not touched.
2. **The stated order** (Run.lean): `stepCommands`, `stepCommands_policy`, `StepUnit`, `stepNames`, `lastStep`,
   `firstStep`, `antecedentOf`, `stepOrder`, `thenWithoutStep`, `stepOrder_forward`, with section 7's fixtures as
   `#guard`s in RunExamples.lean: the seven units -> [(u2.1, u2.2), (u2.2, u3), (u3, u5)] and `thenWithoutStep`
   [u6, u7]; uweb.tour.552_0 -> no pair and `ThenWithoutStep` for b; "Then click Ask." with no earlier instruction;
   the counterexample [a, b (2 steps, after a)] -> [(a, b.1), (b.1, b.2)]. `ThenWithoutStep` is in Texts.lean, class
   `VEError`.
   Finding (d), the reader's part: the first refusal wins with the step's code and text ("Click Ask, then add an
   exception or precedence." is `InvalidInput`, a guard). **Left to the translation writer:** the MIXED unit with a
   demand part per read step and a GAP part per refused step (its code from reading the step alone), and the stated
   order kept between read steps only. These are document facts, not reader outcomes (`StepOutcome` gains no
   constructor). OPEN O4 (the GAP part's owner when the step's object kind is not in section 12's table) and OPEN O8
   (the refusal's text naming the step) stay open; this item does not decide either.
3. **`surfaceKind`'s `if `/`then ` cases** (Wire.lean): `If <c>, <act verb> …` (the clause after the first comma) and
   `Then <act verb> …` are `instruction`. SA's (ββ) "If Alice must click Check then Atlas is reviewed." stays
   `asserted`. A/B on the pinned corpus: AB.md (12 files, 0 literals starting `if `/`then `, 0 flips).
   `paraphraseSteps` is in speech-acts (`lean/VE/SpeechActs/Run.lean`, S10: no second paraphrase table); section 7's two
   English lines are guards. The derived order in `lean/VE/SpeechActs/Source/Run.lean`: `stepUnits` and
   `thenFault`, the `ThenWithoutStep` document check after the core check, by each unit's effective kind
   (attributed, hedged and signed-choice instructions included). No unit field names an antecedent (O3, ruled in
   reviews/dri-decisions-20261102-ci-0.md item 5), so every authored `Then` instruction unit is refused.
4. **The `english.command` response shape**: `one` gains `after_previous`; `many` gains `alternatives`; new
   outcomes `steps` (readings and `paraphraseSteps`) and `mixed` (CI-7b's, written by no reader yet). Schema
   `lean/ResponseShape/Schemas/Command.lean` and encoder theorem `ResponseShape.Encoders.Command.encode_fits`
   (ROUTE-RECIPE steps 2-3).
   **Not delivered: the Python binding of `steps` and of a `many` of sequences.** It is cut to ci-3c
   (reviews/dri-decisions-20261109-ci-3-size.md item 2). After the main merge, ci-2b's relay
   (`ve/backends/english_lean.py`) reads `english.command`. It now refuses `steps`, `mixed` and a `many` whose
   alternatives are not one reading each at its own position as CheckerUnavailable (R8: unbound means unavailable),
   instead of raising `KeyError`. This is DELTA row 7, signed in reviews/dri-decisions-20261110-ci-3-relay.md item 1.
   ci-3c removes that refusal. The binding inventory classifies the new members; its bound-field fuzz rebinds a
   genuine `many`'s `alternatives`.

## Statements (section 7, whitespace normalised)

Every ci-3 definition and theorem equals section 7's text, with these exceptions:

- `readInstruction_typed_step` has `(hw : VE.Scope.JsonWF j)` beside `hd`: SIGNED by the DRI 2026-11-09,
  reviews/dri-decisions-20261109-ci-3.md item 1 (the guard that every ci-3 fixture environment passes `jsonWF?` is in
  RunExamples.lean).
- `readInstruction_typed_of_facts`' `h` is in the step form: SIGNED by the DRI 2026-11-09,
  reviews/dri-decisions-20261109-ci-3-step.md item 1.
- `readInstruction_refused_classed_of`: `Outcome.refused` became `StepOutcome.refused`, the type only. SIGNED by the
  DRI 2026-11-09, reviews/dri-decisions-20261109-ci-3-codes.md item 3.
- After the merge, `RunSplit.readInstruction_typed` (ci-2b, section 6) has `h` in section 7's step form and is proved
  by `readInstruction_typed_step`: SIGNED by the DRI 2026-11-10, reviews/dri-decisions-20261110-ci-3-typed.md item 1.
  `tests/test_ci2b_statements.py` checks section 6's text with only the `hw` and `h` substitutions.
  `RunSplit.readInstruction_refused_classed` keeps its text.

The `hb` hypotheses of `readStep`'s lemmas are ci-3a's and ci-3b's (their own rulings).

## Seeded bugs (each failed its test, then was restored; mutants.json has the file and the failing guard)

| Language | File | Bug | Failing test |
|---|---|---|---|
| Lean | lean/VE/Commands/Run.lean | `stepOrder` reversed | `stepOrder_forward` (Run.lean:718); with proofs sorried, RunExamples.lean:277 and 282 |
| Lean | lean/VE/Commands/Run.lean | `stepOrder` pairs a `Then` unit with the nearest earlier instruction unit | Run.lean:724; sorried: RunExamples.lean:277, 279 (uweb.tour.552_0) |
| Lean | lean/VE/Commands/Run.lean | `readInstruction` skips `proofTask` | Run.lean:449, 452, 625, 630; sorried: ci-1's proof-task guards (RunExamples.lean:104, 117, …) |
| Lean | lean/VE/SpeechActs/Wire.lean | `surfaceKind` reads "If … then …" without a comma as an instruction | RunExamples.lean:297 (the `webKind` guard, (ββ) stays `asserted`), 301 |
| Python | ve/backends/english_lean.py | the `steps` outcome relayed unbound | `tests/test_commands_steps.py::test_the_relay_refuses_a_sequence_it_does_not_bind_yet` |
| Python | ve/backends/english_lean.py | a `many`'s alternatives not bound to its readings | `tests/test_commands_steps.py::test_a_many_answer_s_alternatives_are_bound_to_its_readings` |

The task's fifth seeded bug ("the relay accepting a step reading not in the answer") belongs to the binding of
`steps`, which is ci-3c's. Here a `steps` answer is refused whole, which the first Python seed shows.

mutants.json lists 37 entries: 28 hand mutants, at least one in every new trusted definition, plus the 9 seeds above
(the Lean seeds both with and without sorried proofs). Each records the guard, proof or test that fails. Its line
numbers are on the merged tree.

## Trust

`tools/trust_map.py --check` against d3bb8bfbc650: K +0, S +0, trusted +89. That is VE/Commands/Run.lean +84,
VE/SpeechActs/Wire.lean +4 and VE/SpeechActs/Source/Run.lean +1. The allowance is in docs/trust-baseline.json, SIGNED
by standing ruling R16, and FOLLOW-UPS.md "## ci-3" asks for the ties pass. Fixture definitions are classified `T`
(tools/trust-classes.json).

Trust-mutants sweep: TM_RESULT

## Size

`git diff --numstat $(git merge-base HEAD main)`, generated files excluded: SIZE_LINE

## Tests

TESTS_LINE

## Pilot bytes (an estimate; nothing is claimed before a pilot audit)

The plan's estimate is +2 segments / 46 B for CI-3. "Then click Ask." and "Then click Check rule conflict." (tour.js)
now read as `one` with `after_previous`, and "Click Check rule conflict, then click Ask." reads as `steps`. In a
document, an authored `Then` unit is still `ThenWithoutStep` until O3 names an antecedent field. Through the Python
fence route, a sequence is CheckerUnavailable until ci-3c.

## Next

ci-4 (after this item and ci-3b); then ci-3c.

FOLLOW-UP: ci-3c english.command steps/many relay binding, inventory rows, fuzz test

SELF-REVIEW: SELF_REVIEW_LINE
