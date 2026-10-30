# q1-4bb: one owner for the speech layer's Lean-routed prefixes

No DRI signature is needed or reserved. No answer changes, so there is no DELTA.md (no user-visible delta).

Item: FOLLOW-UP q1-4bb of docs/question-answering/q1-4b/REPORT.md ("Not delivered") and review q1-4b-review F2.
Plan: question-answering-PLAN.md 6.4 "Q1 and speech acts (Q1.4)" and Q1.4; speech-acts.md 2.1. Statement gate: none
(no theorem changes). This item implements the synthesis round 2 edits question-answering 4 ("Keep q1-4bb: move "Is"
into Lean's `speechPrefixes` and update `speech-acts.md` 2.1 and its polar row") and speech-acts 1 (the plan gains
the item: speech-acts-PLAN.md work item 6).

## The readers of `speechPrefixes` (deliverable 1, first step)

`grep -rn "speechPrefixes\|QUESTION_CALLERS" lean/VE ve tools tests rust`:

- Lean: `VE.Question.Run.codesCase` (the `{"export": "codes"}` answer's `callers`) and the `#guard` in
  `lean/VE/Question/Examples.lean`. No Lean decision reads it: `modalFields` reads `modalWords`, the reader reads
  `Caller.auxs`.
- Python: `ve/backends/english_lean.py` `read_question` checks only that `caller` is a key of `QUESTION_CALLERS`;
  `ve/speech_english.py` `_LEAN_PREFIXES` routes by it. `tools/question_codes.py` writes it to `ve/question/codes.json`.
- Rust: none.

Adding `"Is "` changes no decision, so there is one list, not a second one for the speech caller.

## Delivered

| Plan / task row | Commit | Evidence |
|---|---|---|
| (1) `"Is "` in Lean's exported list; `_LEAN_PREFIXES` reads the contract, with no literal left | fd7fa6c1f | `speechPrefixes := caseFrame :: modalWords.map (· ++ " ") ++ speechAuxiliaries.map (capitalise · ++ " ")` (`lean/VE/Question/Run.lean`), derived from the caller's fronted words, not a new literal; `#guard` at `Examples.lean:92`; `ve/question/codes.json` regenerated (`callers` gains `"Is "`); `_LEAN_PREFIXES = QUESTION_CALLERS[SPEECH_CALLER]`; tests `test_the_routed_prefixes_are_the_contracts` (identity with the contract), `test_the_speech_parser_keeps_no_prefix_of_its_own` (no string constant of `ve/speech_english.py` is a routed prefix) |
| (2) speech-acts.md 2.1, its polar rows and the doc comment describe main | fd7fa6c1f, the spec commit | 2.1: `<rest>` and the opaque-gloss rule are a which-question's; a polar or `Must`/`Can` wording is sent to Lean's `english.question` by Lean's list and its formula or refusal is Lean's; both polar rows name Lean's reading; the normalisation paragraph (old line 407) and the `OpaqueWording` row (old line 876) say the parser's gloss and name matching is a which-question's. The `speechPrefixes` doc comment no longer promises Q1.4b. |
| (3) q1-4b's differential and base-acceptance tests pass unchanged | none (no test edited but the prefix test) | `tests/test_speech_polar_lean.py` in the selected run below; the routed tuple is the same strings in the same order as before (`("Is it the case that ", "Must ", "Can ", "Is ")`, asserted by `test_the_routed_prefixes_are_the_contracts`), so `text.startswith(_LEAN_PREFIXES)` routes every wording as before |
| (4) seeded bugs | below | `docs/question-answering/q1-4bb/mutants.json` |

Not delivered here, as the task says: `Is this impossible?` read as `bottom`, and `LeanReading.rejection`'s
code-worded class (q1-4b's other FOLLOW-UPs; not this item).

The `english.question` codes export (`{"export": "codes"}`) now lists `"Is "` in `callers`. It is the relay's
contract, not a verdict or a diagnostic text; no `ve` command shows it.

## Seeded bugs (each restored)

| Language | File | Bug | Fails |
|---|---|---|---|
| Lean | `lean/VE/Question/Run.lean` | `speechPrefixes` without `"Is "` | `lake build VE.Question.Examples`: `error: VE/Question/Examples.lean:92:0` (the `speechPrefixes` `#guard`) |
| Python | `ve/speech_english.py` | stale literal beside the read: `(*QUESTION_CALLERS[SPEECH_CALLER], "Is ")` | `test_the_speech_parser_keeps_no_prefix_of_its_own`, `test_the_routed_prefixes_are_the_contracts` (`2 failed`) |
| Python | `ve/speech_english.py` | the read drops the fronted prefix: `QUESTION_CALLERS[SPEECH_CALLER][:3]` | `test_an_f2_wording_is_sent` (5 parametrisations failed, e.g. `[Is atlas reviewed?]`) |

No Rust product code changed.

## Trust

`uv run python tools/trust_map.py --check`: `VE/Question/Run.lean: trusted +2` (V +2, K +0, S +0). Recorded with
`--allow` as "SIGNED by standing ruling R6 (DRI-RULINGS.md), q1-4bb, 2026-10-30": the two lines replace the Python
literal `"Is "` this change deletes from `ve/speech_english.py`. No new trusted definition (`speechPrefixes` existed);
its mutant is the Lean seed above. No FOLLOW-UPS.md row (R6, not R16).

## Size and pilot bytes

`git diff --numstat $(git merge-base HEAD main)` outside generated files: 38 added, 23 removed (docs 17/12, Lean 7/5,
Python 14/6), plus this report and mutants.json. Pilot bytes expected to move: 0.

## Checks run

- `lake build` (full): `Build completed successfully (1164 jobs).`
- `python3 lean/audit.py`: `PASS: 673 source files; 7503 named theorem declarations audited`.
- `uv run python tools/regen_generated.py --write` once (`wrote 34 entries`), after building the Rust binary
  (`python3 tools/rust_build.py`, pinned; no Rust source changed).
- `uv run python tools/gate_collection.py --check --prebuilt`: `1 added, 0 removed by a trailer, 0 refused, 0 stale
  and 0 malformed trailers`.
- `tools/select_tests.py --base $(git merge-base HEAD main)`: 407 test files, `tests/test_speech_polar_lean.py` among them.
- Selected tests: SELECTED_RESULT

Spec re-read: the 2.1 paragraph and polar rows against `ve/speech_english.py:154-186` (`_LEAN_PREFIXES`, `_polar`: no
`warnings`, so no `OpaqueWording` on a polar wording) and `lean/VE/Question/Run.lean:191-197`; question-answering-PLAN.md
6.4 (byte-identical content; `Must` keeps `ModalQuestion`).

Next item: none named; Q2.1 follows the question-answering plan.

## Self-review against BUILDER-CHECKLIST

1. Typed and contained: N.A., no response shape or field changed (`callers` was already typed by `_question_contract`).
2. Deliverables: PASS, the Delivered table; no Python copy of a Lean decision (`test_the_speech_parser_keeps_no_prefix_of_its_own`).
3. Tests can fail: PASS, three seeded bugs above (Lean `#guard` Examples.lean:92; two pytest tests).
4. Agreement, valid inputs pass: PASS, q1-4b's differential `test_every_opening_verdict_row_is_read_as_ve_ask_reads_it`, `test_parse_speech_relays_every_routed_corpus_and_hunted_wording_unchanged` in the selected run.
5. R8 binding: N.A., no new field read from a Lean answer.
6. Gate on final HEAD: PASS, left to the chain (task rule); the selected run is on the committed tree.
7. No unsigned item: PASS, trust +2 under R6 (`docs/trust-baseline.json`); no DELTA row.
8. DELTA: PASS, none: the routed tuple is unchanged (`test_the_routed_prefixes_are_the_contracts`), q1-4b's delta tests pass unchanged.
9. Selection: PASS, `select_tests.py` selects `tests/test_speech_polar_lean.py`, which holds the tests the Python seeds fail.
10. Lean statements: N.A., no theorem changed.
11. Budgets fail closed: N.A., no budget or limit touched.
12. CPU/memory: N.A., a constant list of four strings.
13. Test-removed trailers: PASS, `gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed.
14. Both directions: PASS, `test_an_f2_wording_is_sent` (routed) and `test_a_wording_without_a_routed_prefix_is_not_sent` (not routed); claims cite commands above.
