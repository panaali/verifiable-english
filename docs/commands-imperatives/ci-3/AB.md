# ci-3 A/B: `surfaceKind` flips and the `english.command` reader

Saved by `uv run python docs/commands-imperatives/ci-3/ab.py docs/commands-imperatives/ci-3/AB.json` (its docstring
says what each side is). Classes b1, b2 and b3 are DRI 2026-10-28 item 2(b)
(reviews/dri-decisions-20261028-commands-imperatives.md): b1 a section 7 wording from refused to read, b2 read ->
refused, b3 a `choiceKindConflicts` flip that adds a conflict. Class rr is refused -> refused with another code or
text, signed by reviews/dri-decisions-20261109-ci-3-codes.md item 1. No row is a previously read wording that reads
differently. The `surfaceKind` if/then cases remove a conflict as a class (a signed `instruction` choice on a
condition-first or `Then` instruction wording), signed by reviews/dri-decisions-20261109-ci-3-step.md item 2; 0
corpus rows have that shape (below).

## `surfaceKind` ((iii)), on the pinned corpus

12 files (tests/test_speech_acts.py, tests/test_speech_acts_acts0.py, tests/test_speech_acts_conformance.py, tests/test_speech_acts_lean.py, tests/test_speech_polar_lean.py, tests/test_speech_source_lean.py, tests/test_speech_source_relay.py, tests/test_speech_source_switch.py, tests/frozen_speech/__init__.py, tests/frozen_speech/speech_acts.py, tests/frozen_speech/speech_document.py, docs/question-answering/q1-4/evidence/speech_ab.py): 0 string literals
whose normalised text starts `if ` or `then `, the only texts the new cases can change (every other path of
`surfaceKind` is main's). So no signed choice in the corpus flips: 0 b3 rows and 0 corpus rows of the removed-conflict
class. SA's (ββ) premise "If Alice must
click Check then Atlas is reviewed." has no comma and stays `asserted` (`RunExamples.lean`, `webKind` guard).

## The reader: 99 fixture wordings, each over `E_web`

Base: main's entry (`proofTask`, else `readCommand`), lifted with `lift (.core s) false`; head: `readInstruction`.
Every wording is read over `E_web` with no query record (not in its own fixture's environment), so the CI-2 proof
rows and the CI-5 `acts@0` rows are refused on both sides here; their own environments are checked by their
unchanged `#guard`s (RunExamples, Examples). 88 rows are unchanged; 11 change:

| # | Wording | Class | Base | Head |
|---|---|---|---|---|
| 1 | Click Ask, if draft is approved, then add an exception or precedence. | rr | `refused "NoDerivation" "The condition has no reading with the current vocabulary. Unknown English phrase 'then…` | `refused "ConditionScope" "a condition with a sequence of steps: write one sentence per step, with the conditio…` |
| 2 | Click Ask, if draft is approved, then click Ask. | rr | `refused "NoDerivation" "The condition has no reading with the current vocabulary. Unknown English phrase 'then…` | `refused "ConditionScope" "a condition with a sequence of steps: write one sentence per step, with the conditio…` |
| 3 | Click Ask, then click Ask, if draft is approved. | rr | `refused "InvalidInput" "no single speech-act reading"` | `refused "ConditionScope" "a condition with a sequence of steps: write one sentence per step, with the conditio…` |
| 4 | Click Check rule conflict, then click Ask. | b1 | `refused "InvalidInput" "no single speech-act reading"` | `steps [{ force := require, act := "click_check_required", fills := [], guard := VE.Formula.top }, { force := r…` |
| 5 | If draft is approvable, click Ask. | rr | `refused "InvalidInput" "no single speech-act reading"` | `refused "NoDerivation" "The condition has no reading with the current vocabulary. Unknown English phrase 'is a…` |
| 6 | If draft is approved, click Ask. | b1 | `refused "InvalidInput" "no single speech-act reading"` | `one { force := require, act := "click_ask_required", fills := [], guard := VE.Formula.unary "approved" (VE.Ter…` |
| 7 | If draft is approved, click Check rule conflict, then click Ask. | rr | `refused "InvalidInput" "no single speech-act reading"` | `refused "ConditionScope" "a condition with a sequence of steps: write one sentence per step, with the conditio…` |
| 8 | Review the meaning, if draft is approved, then click Ask. | rr | `refused "AmbiguousDerivation" "multiple declared acts match"` | `refused "ConditionScope" "a condition with a sequence of steps: write one sentence per step, with the conditio…` |
| 9 | Review the meaning, then click Ask. | b1 | `refused "InvalidInput" "no single speech-act reading"` | `many [Alt.shape (Shape.seq ["Review the meaning", "click Ask"]) [{ force := require, act := "review_meaning_re…` |
| 10 | Then click Ask. | b1 | `refused "InvalidInput" "no single speech-act reading"` | `one { force := require, act := "click_ask_required", fills := [], guard := VE.Formula.top } true` |
| 11 | Then click Check rule conflict. | b1 | `refused "InvalidInput" "no single speech-act reading"` | `one { force := require, act := "click_check_required", fills := [], guard := VE.Formula.top } true` |

Every b1 row is a `#guard` of `lean/VE/Commands/RunExamples.lean` (section 7's fixtures through the mode), pinned
by `tests/test_commands_steps.py::test_each_b1_row_is_a_route_fixture_that_reads`. Every rr row is a row of `abRefused` in the same file (refused through the mode with its exact code, text and class), pinned by `::test_each_rr_row_is_a_route_fixture_refused_with_its_code`. The rr rows are section 7's own
outcomes (`ConditionScope` for a condition with a sequence; `NoDerivation` for "If draft is approvable, click Ask.",
equal to `readCommand` of "Click Ask, if draft is approvable.", `preposed_eq`'s other direction).

## Document refusals (the speech-source wrapper), class b2

Not reader rows: two document checks of `lean/VE/SpeechActs/Source/Run.lean` refuse sources that main accepts, read ->
refused, nothing newly accepted (DELTA.md rows 3 and 8).

| # | Document | Class | Base | Head |
|---|---|---|---|---|
| D1 | an instruction unit (by effective kind) of the `Then <x>.` shape | b2 | accepted | `ThenWithoutStep: … (unit <id>)` |
| D2 | a unit or `MIXED` unit with an instruction part and a `, then ` wording whose parts are not, in order, the steps of `readStep` of the whole wording (review F2) | b2 | accepted | `InvalidInput: a sequence of steps is one instruction unit whose parts are its steps, each with its step's command (unit <id>)`; `InvalidInput: command reading context` without the context |

D2's in-order form is accepted as before. Fixtures: `lean/VE/Commands/RunSplit.lean` (SourceExamples) and
`tests/test_commands_steps.py`. Finding (d)'s translation form (a demand part and a GAP part for a refused step) is
refused by D2 in this wrapper; the translation writer's GAP part stays with OPEN O4/O8 (REPORT).
