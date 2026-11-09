# ci-3 A/B: `surfaceKind` flips and the `english.command` reader

Saved by `uv run python docs/commands-imperatives/ci-3/ab.py docs/commands-imperatives/ci-3/AB.json` (its docstring
says what each side is). Classes are DRI 2026-10-28 item 2(b) (reviews/dri-decisions-20261028-commands-imperatives.md):
b1 a section 7 wording from refused to read, b2 the refusing direction (a refusal whose code changes is b2, as in
ci-5's DELTA row 6), b3 a `choiceKindConflicts` flip that adds a conflict. No row is a previously read wording that
reads differently, and none removes a conflict: nothing stops the batch.

## `surfaceKind` ((iii)), on the pinned corpus

12 files (tests/test_speech_acts.py, tests/test_speech_acts_acts0.py, tests/test_speech_acts_conformance.py, tests/test_speech_acts_lean.py, tests/test_speech_polar_lean.py, tests/test_speech_source_lean.py, tests/test_speech_source_relay.py, tests/test_speech_source_switch.py, tests/frozen_speech/__init__.py, tests/frozen_speech/speech_acts.py, tests/frozen_speech/speech_document.py, docs/question-answering/q1-4/evidence/speech_ab.py): 0 string literals
whose normalised text starts `if ` or `then `, the only texts the new cases can change (every other path of
`surfaceKind` is main's). So no signed choice flips: 0 b3 rows, 0 removed conflicts. SA's (ββ) premise "If Alice must
click Check then Atlas is reviewed." has no comma and stays `asserted` (`RunExamples.lean`, `webKind` guard).

## The reader: 96 fixture wordings, each over `E_web`

Base: main's entry (`proofTask`, else `readCommand`), lifted with `lift (.core s) false`; head: `readInstruction`.
Every wording is read over `E_web` with no query record (not in its own fixture's environment), so the CI-2 proof
rows and the CI-5 `acts@0` rows are refused on both sides here; their own environments are checked by their
unchanged `#guard`s (RunExamples, Examples). 85 rows are unchanged; 11 change:

| # | Wording | Class | Base | Head |
|---|---|---|---|---|
| 1 | Click Ask, if draft is approved, then add an exception or precedence. | b2 | `refused "NoDerivation" "The condition has no reading with the current vocabulary. Unknown English phrase 'then…` | `refused "ConditionScope" "a condition with a sequence of steps: write one sentence per step, with the conditio…` |
| 2 | Click Ask, if draft is approved, then click Ask. | b2 | `refused "NoDerivation" "The condition has no reading with the current vocabulary. Unknown English phrase 'then…` | `refused "ConditionScope" "a condition with a sequence of steps: write one sentence per step, with the conditio…` |
| 3 | Click Ask, then click Ask, if draft is approved. | b2 | `refused "InvalidInput" "no single speech-act reading"` | `refused "ConditionScope" "a condition with a sequence of steps: write one sentence per step, with the conditio…` |
| 4 | Click Check rule conflict, then click Ask. | b1 | `refused "InvalidInput" "no single speech-act reading"` | `steps [{ force := require, act := "click_check_required", fills := [], guard := VE.Formula.top }, { force := r…` |
| 5 | If draft is approvable, click Ask. | b2 | `refused "InvalidInput" "no single speech-act reading"` | `refused "NoDerivation" "The condition has no reading with the current vocabulary. Unknown English phrase 'is a…` |
| 6 | If draft is approved, click Ask. | b1 | `refused "InvalidInput" "no single speech-act reading"` | `one { force := require, act := "click_ask_required", fills := [], guard := VE.Formula.unary "approved" (VE.Ter…` |
| 7 | If draft is approved, click Check rule conflict, then click Ask. | b2 | `refused "InvalidInput" "no single speech-act reading"` | `refused "ConditionScope" "a condition with a sequence of steps: write one sentence per step, with the conditio…` |
| 8 | Review the meaning, if draft is approved, then click Ask. | b2 | `refused "AmbiguousDerivation" "multiple declared acts match"` | `refused "ConditionScope" "a condition with a sequence of steps: write one sentence per step, with the conditio…` |
| 9 | Review the meaning, then click Ask. | b1 | `refused "InvalidInput" "no single speech-act reading"` | `many [Alt.shape (Shape.seq ["Review the meaning", "click Ask"]) [{ force := require, act := "review_meaning_re…` |
| 10 | Then click Ask. | b1 | `refused "InvalidInput" "no single speech-act reading"` | `one { force := require, act := "click_ask_required", fills := [], guard := VE.Formula.top } true` |
| 11 | Then click Check rule conflict. | b1 | `refused "InvalidInput" "no single speech-act reading"` | `one { force := require, act := "click_check_required", fills := [], guard := VE.Formula.top } true` |

Every b1 row is a `#guard` of `lean/VE/Commands/RunExamples.lean` (section 7's fixtures through the mode), pinned
by `tests/test_commands_steps.py::test_each_b1_row_is_a_route_fixture_that_reads`. The b2 rows are section 7's own
outcomes (`ConditionScope` for a condition with a sequence; `NoDerivation` for "If draft is approvable, click Ask.",
equal to `readCommand` of "Click Ask, if draft is approvable.", `preposed_eq`'s other direction).
