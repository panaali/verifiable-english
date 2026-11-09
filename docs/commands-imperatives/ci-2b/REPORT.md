# ci-2b REPORT: command English has one owner (the statements, the wrapper, the relay and the deletions)

**Status:** deliverables (1) to (4) built and committed on `feature/ci-2b`; nothing cut (reviews/dri-decisions-20261109-ci-2b-size.md item 1). Review round 1 (7d1e1333c): its one A finding, F1, fixed ("Review fixes" below). HEAD: the commit that last changes this file.
**What changed:** `readInstruction_refused_classed` and `readInstruction_typed` as the spec states them (plus `hw`); the speech-source wrapper requires every resolved fence to decode to the role its kind reads (`Wire.roleFits`, review F1), so every resolved fence of a kind wrapping `instruction` is a command, and reads each through `readInstruction` (`commandFence_needs_context`); Python's `read_command` relays `english.command` and Python's command branch, `PROOF_TASK_ACT`, `act_verb` and `legend`'s scope sentences are deleted; the A/B over 24,208 pinned rows shows no forbidden row.
**Open:** none blocking. Follow-ups below (the ties pass, the fence cap's spec text, a Lean `many` text).
**Signatures:** none reserved. DELTA cites R1, R16 and the DRI's 2026-10-28 items 1, 2(a), 2(b) and 2026-11-09 (the fence cap) only.

FOLLOW-UP: ci-2b-ties an R16 ties pass for lean/VE/SpeechActs/Source/Run.lean's readSource and decodeSpeechSource (FOLLOW-UPS.md "## ci-2b")
FOLLOW-UP: ci-2b-many a Lean-written text for english.command's many outcome (needs Schemas/Command.lean and RunExamples.lean, held by ci-5)

Plan and spec: `docs/spec/commands-imperatives-PLAN.md` "CI-2" (lines 445-584) and `docs/spec/commands-imperatives.md`
section 6 (lines 574-781), on main. Statement gate: passed (reviews/dri-decisions-20261102-ci-0.md item 1).

## Deliverables

| Task item | Delivered | Evidence |
|---|---|---|
| (1) `readInstruction_refused_classed`, `readInstruction_typed` exactly as spec section 6 states them, `hw` beside `hd`, proved through ci-1b | yes, `lean/VE/Commands/RunSplit.lean` (770441040): the first from `refused_classed` and `guardOf_classed`, the second by cases on `proofTask`: `readCommand_typed` when it is `none`, `readInstruction_typed_of_facts` with `declared_of_decode hw hd` otherwise | `tests/test_ci2b_statements.py` (the spec-text check: both equal the spec's text whitespace-normalised, with `hw` the only addition; a changed statement fails); `python3 lean/audit.py`: "PASS: 789 source files; 8709 named theorem declarations audited …; only the declared standard axiom allowlist" |
| (1) the `_of` theorems | `readInstruction_refused_classed_of` and `readInstruction_typed_of_facts` stay in `Run.lean` as the lemmas the two proofs use; ci-2's shims `RunSplit.readInstruction_refused_classed_of_ci1b` and `typed_facts_are_ci1s` are deleted (the spec's statements replace them); the `declared` facts `#guard` stays and also checks `jsonWF?` | `lake build`: 1319 jobs, success |
| (2) `Source/Run.lean` reads every command fence through `readInstruction`; `commandFence_needs_context` | yes. `readSource` (the old body) first refuses a resolved fence whose decoded role is not the one its kind reads (`Wire.roleFits`: a kind wrapping `instruction` reads a command, `question` a question, `norm` a norm; review F1), then re-reads every resolved command fence under `commandContext`, the `english.command` request (`Run.decodeRequest`, so `jsonWF?` and the decoders are the mode's) of the payload's `reading_context` with the document's environment under its effective scope and its query records that name a declared `query` constant; one that differs is `InvalidInput: resolved speech fences`. `decodeSpeechSource` refuses a command fence (`hasCommandFence`, spec S34) with no context object, after every other check: `InvalidInput: command reading context` | `commandFence_needs_context` proved (audit above); `tests/test_command_relay.py` (12 test functions, 20 cases, relay, wrapper and documents); RunSplit.lean's `SourceExamples` `#guard`s |
| (3) `read_command`; `speech_document.py`; `command.read`; `relay_lint.py`; the `english.command` inventory rows; the relay gate's F4/F10 entries retired | yes. `read_command` = `command_request` (the `english.read` request's environment, overlay and lexicon producer, the unit, the wording, the query records; no proof-task selection) + `command_answer` (R8: `command_problem`) + Lean's outcome raised verbatim. `parse_speech` sends every wording of no question form to it; `_resolve_fences` sends the unit, the records and one vocabulary, and `SpeechSource` the reading context. Manifest `command.read` (`authority: lean-only`). `tools/relay_lint.py` needs no edit: `ve/backends/english_lean.py` is already a RELAYED module | `uv run python tools/relay_lint.py`: "PASS: 20 relayed module(s) …"; `tests/test_relay_binding_inventory.py`: 42 passed; `tools/relay_mutation_gate.py --route service:english.command`: "1126 mutants, 1126 refused, 0 allowed"; `tools/repo_map.py --check`: "PASS: 42 modes"; `repo_map.py route english.command` lists `command.read` and `read_command` |
| (4) the deletions, in the same change as (3) | yes (ee75d725e): `_command_candidates`, `parse_speech`'s `You may`, `Please`, coordination, proof-task and `text.endswith(".")` blocks, the scope sentences of `legend` (now Lean's lines from the source report), `PROOF_TASK_ACT`, `act_verb` (no caller left), the proof task's query selection in `speech_document.py`. `_sentence`, `_copular`, `_polar` and the `follows` selection stay | DELTA.md's deletion ledger |
| the A/B with ci-1's review F3 rows | yes: `evidence/ab.py` over `evidence/corpus.json.gz` (24,208 rows: every command wording the speech tests read on both sides, the Q1.4 corpus's 218 non-question wordings, F3's two rows, spec P2-P3″), run at 4c0a4e2bd | `ab.py check`: "A/B: no forbidden row"; `ab.json` counts `same` 24,165, `R1` 33, `b2` 9, `many` 1; `tests/test_ci2b_ab.py` |

Not delivered: none. The task's (1)-(4) are this item's; nothing moves to a ci-2c.

## Deviations and notes

1. **The frozen pre-switch parser.** `tests/frozen_speech/speech_acts.py` and `speech_document.py` imported the live
   `parse_speech`, so the frozen reference would have read commands through Lean. The deleted branch is kept verbatim
   as test data in `tests/frozen_speech/speech_english.py` (and the old `legend` in `speech_acts.py`), which the
   frozen checkers and the A/B's base read; the size ruling counts it as not authored.
2. **F5 (spec section 6).** `test_proof_task_wording_uses_an_act_both_linters_accept` moves from "tom is a cat" to
   "atlas is reviewed" (P1′), as the spec says; the 7 "tom is a cat" proof rows are b2 in the A/B.
3. **The query records the request carries.** `decodeRequest` (ci-2) refuses a record whose id is no declared `query`
   constant. A document's follows question may have such a record, so both `command_request` and `commandContext`
   keep only the records that name one (the records a proof task can name); the wrapper's re-read refuses any
   disagreement. This is a request projection, not a verdict: `test_a_fenced_proof_task_reads_the_documents_records`.
4. **`many`.** The answer has no Lean text for `many`; `read_command` raises `AmbiguousDerivation` with one line per
   reading, its act and Lean's paraphrase (DELTA row 3). A Lean text is the follow-up above.
5. **The retry.** `SpeechSource` calls the wrapper once without the fences' contents; on Lean's `NotImplemented:
   fenced English content` or `InvalidInput: command reading context` it resolves them and calls again with the
   reading context (`_UNRESOLVED`, matched on Lean's texts, which select the retry and are never shown).
6. **The legend.** `decide_source` now binds the source report's legend count to the row's scope (1 + addressee +
   definites, none repeated); the relay gate's B0 `*/legend` duplicate and empty paths are retired: `relay_mutation_gate.py --route call:ve.backends.speech_source:decide_source`: "2061 mutants, 1993 refused, 68 allowed", 0 failures.
7. **Limits (the common rule).** The fences Python resolves are charged against `VE.Limits.maxCases` in Lean before any
   is read (DELTA row 8, SIGNED 2026-11-09); the context is decoded once; each wording is read once under
   `readInstruction`'s 400-byte bound and `workBudget`; fence texts and needed ids are hashed. Fixture: 200 command
   fences read, 4097 refused (`test_command_fences_are_charged_before_they_are_read`; RunSplit.lean's `fenced` guards).
8. **The size ruling's `jsonWF?` condition.** No parser builds a tree `jsonWF?` refuses, so the fixture is Lean's:
   `RunExamples.lean:169` (F-raw, the mode) and RunSplit.lean's `commandContext` guard (the wrapper); S4 shows the
   first failing when `decodeRequest` drops the check.
9. **Two ci-2 comments** that said the wrapper and the relay binding were deferred (`Run.lean:83`,
   `Schemas/Command.lean`) now say what is delivered; `tests/test_commands_ci2_review.py` checks the new text.

Spec re-read: `readInstruction_refused_classed` and `readInstruction_typed` against `docs/spec/commands-imperatives.md:680-689` (by `test_ci2b_statements.py`); `commandFence_needs_context` against `:690-694` (identical); `hasCommandFence` against `:696-699` (S34: a unit or MIXED part with fence content whose kind wraps `instruction`); the error texts against plan `:455-458`; the BOUND/LEAN rows against spec `:766-771` (D9; the legend lines, code, class and text LEAN, the legend's count bound); the deletion ledger against spec `:744-764` and plan `:465-473`.

## Seeded bugs (`mutants.json`)

| Id | File | Bug | Fails |
|---|---|---|---|
| S1 | ve/backends/english_lean.py | `read_command` accepts a fill the request does not hold (the plan's Python seed) | `test_a_fill_the_request_does_not_hold_is_unavailable[fill0,fill1]`; `test_every_bound_field_mutant_is_unavailable[english.command]` |
| S2 | lean/VE/SpeechActs/Source/Run.lean | the wrapper reads a command fence without the context (`hasCommandFence` never true) | `test_a_command_fence_needs_the_reading_context` |
| S3 | lean/VE/SpeechActs/Source/Run.lean | the re-read takes any resolved command | `test_a_resolved_command_lean_does_not_read_is_refused[change0-2]` |
| S4 | lean/VE/Commands/Run.lean | `hw` dropped from the relay (`decodeRequest` without `jsonWF?`) | `RunExamples.lean:169` (the `jsonWF?` refusal fixture) |
| S5 | lean/VE/Commands/Read.lean (planted and restored; ci-5's file) | a deleted Python check with no Lean replacement (`You may` out of `prefixRefusal`) | `ab.py`'s `problems()`: the 5 `You may` rows are forbidden `code` rows |
| S6 | lean/VE/SpeechActs/Source/Run.lean | `commandContext` drops the query records | `test_a_fenced_proof_task_reads_the_documents_records` |
| S7 | lean/VE/SpeechActs/Source/Run.lean | the fence cap removed | RunSplit.lean's `fenced (maxCases + 1)` guard; `test_command_fences_are_charged_before_they_are_read` |
| S8 | lean/VE/SpeechActs/Source/Run.lean | review F1's role check removed: a fence resolved as a formula in place of a command, question or norm is dropped unread | RunSplit.lean's two formula guards; `test_a_fence_resolved_as_a_formula_in_place_of_its_role_is_refused` (10 of 10 fail, the 7 controls pass) |
| S9 | lean/VE/SpeechActs/Wire.lean | `kindTag` ignores the quoted wrapper (`kind`, not `innerKind kind`) | RunSplit.lean's formula guard and the attributed `click` guard |

Each was planted, shown failing, and restored (the same tests pass on the restored build). No Rust product code changed; review F1 changed Python product code only in `decide_source`'s docstring, so it has no Python seed.

## Trust

`uv run python tools/trust_map.py --check` (after review F1): "against 63b2b596f79a: K +0, S +0, D +92, G +2, tied +0,
unclassified +0, trusted +32 … PASS" with the allowances V +25 and V +7 (`VE/SpeechActs/Source/Run.lean`: `readSource`,
`decodeSpeechSource`; F1's +7 is the role check in `readSource`, and `Wire.lean`'s `kindTag`, `Role.tag`, `roleFits`
are D[R]), each SIGNED by standing ruling R16, in `docs/trust-baseline.json`; FOLLOW-UPS.md "## ci-2b" asks for the ties pass. R16's
mutants (`mac-pytest.sh --trustmut -- --max-mutants 1000 --json …/trust-mutants.json --test lean/VE/Commands/RunSplit.lean
--allow …/trust-mutants-allow.json`, at 37ef893ed, the final Lean tree after review F1): 2 definitions, 46 KILLED,
0 SURVIVOR, 0 UNKNOWN, 15 ALLOWED, 11 INVALID, 0 NOT RUN. Its first run after F1 (d3e16f607) had M027 and M031
(`take 1` of the role check's lists) ALLOWED under an older reason; RunSplit.lean's formula-second guard kills both. The first run (0 killed: no Lean check read the wrapper) led to RunSplit.lean's
`SourceExamples`; the 13 allowed are two equivalent `commands.isEmpty` mutants and mutants that do not elaborate.

## Tests

- After review F1 (`mac-pytest.sh --select -- --base 63b2b596f --run`, at 000085f8a, tree 912e4ab723, on ve-cloud-2):
  exit 0, 486 units recorded, 0 failed (`tests/test_command_relay.py`: 626 functions, exit 0); three weakly selected
  files over 120 s were deferred to the chain gate (`test_gate_collection.py`, `test_gate_collection_renumber.py`,
  `test_shape_binding_mutants.py`). `lake build` (1319 jobs) and `python3 lean/audit.py` PASS on that tree;
  `regen_generated.py --check`: "checked 37 entries"; `gate_collection.py --check --prebuilt`: "48 added, 0 removed by
  a trailer, 0 refused, 0 stale and 0 malformed trailers". PROBE F1 fails before the fix (`DID NOT RAISE VEError`) and
  passes after it.
- Selected tests on committed code (`MAC_PYTEST_NO_DEFER=1 mac-pytest.sh --select -- --base 63b2b596f --run`, at
  7b4a1becd, run ci-2b-7b4a1bec-t217961, 488 of 559 units): shards 1, 2, 3, 5 passed; shard 4 failed
  `tests/test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified` and
  `::test_every_lean_binding_has_a_probe` (RunSplit.lean unclassified; no `command.read` probe). Fixed in b50d3754d;
  rerun of exactly those ids (`mac-pytest.sh -- <ids>`): "2 passed".
- `uv run python tools/regen_generated.py --check`: "checked 37 entries" (one earlier run failed `question-codes`
  once and passed alone and on rerun). `tools/gate_collection.py --check --prebuilt`: "28 added, 0 removed by a
  trailer, 0 refused, 0 stale and 0 malformed trailers". `tools/select_tests.py --explain`: 488/559 units (the
  service schema, `english_lean.py` and the inventories reach most of the suite).
- None of main-known-red.txt's three rows is in this area. Not run, per the task: the full gate (the chain's), whole
  UDHR or constitution runs.

## Size and pilot bytes

`git diff --numstat 63b2b596f` (generated files, the saved corpus and A/B, and trust-mutants.json excluded): +1,371 /
-216. Of these, product lines are about 363 added (Source/Run.lean 82, english_lean.py 110, manifest 96,
speech_document.py 30, speech_english.py 15, speech_source.py 12, relay_mutation_gate.py 11, others 7), under the ~600
line; the rest are the statement gate, the ruling's condition tests and fixtures, the verbatim frozen copy (126) and
evidence (reviews/dri-decisions-20261109-ci-2b-size.md item 1). Pilot bytes: CI-1's +9 units / +273 B can now reach
a document through this wrapper (an estimate; nothing is claimed before a pilot audit).

## Review fixes (round 1, review of 7d1e1333c)

| Finding | Fix | Regression tests | Commits |
|---|---|---|---|
| F1 (A): an instruction fence resolved to non-command content was never read by Lean | One table in `Wire.lean` (`kindTag`, `Role.tag`, `roleFits`: the role each kind reads, by the kind it wraps); `readSource` refuses every resolved fence whose decoded role is not its kind's (`InvalidInput: resolved speech fences`), after `checkedDocument`. The class: plain, attributed, hedged and `MIXED`-part instruction fences, and question and norm fences, wherever they stand among the fences. False claims corrected: `Source/Run.lean`'s header and A2 comment, both manifest reasons, `decide_source`'s docstring, this report and DELTA's intro and row 6 | `tests/test_command_relay.py::test_a_fence_resolved_as_a_formula_in_place_of_its_role_is_refused` (10, PROBE F1 among them), `::test_every_instruction_fence_is_read_as_a_command` (6), `::test_every_resolved_fence_is_checked_for_its_role` (3), `::test_an_asserted_fence_resolved_as_a_formula_is_its_assertion`; RunSplit.lean's `SourceExamples` role guards; seeds S8, S9 | 52d164873, d3e16f607, 37ef893ed, a853d420e, 000085f8a |

F2 to F6 are C (follow-ups) and are left as the review files them. Not in F1's scope: a unit whose authored inline content (no
fence) is a formula under an instruction kind still decodes to no role, as on main. A refusal there would change
the verdict of an authored document, which needs a spec decision (3.2 rules only on misplaced command, question and
norm content).

## Next item

ci-3 (after ci-3a), ci-5's revision as its chain decides, then ci-4.

## Self-review against BUILDER-CHECKLIST

SELF-REVIEW: 1 A, 6 B, 8 C; fixed 15 (A: the query records' projection; B: product-side fence fixtures, `many` lines
naming each act, DELTA row 6's citation, the legend count binding, the CLI fixture, the fence charge; C: per-unit
request id, `hasContext`, `ab.py`'s commit and empty checks, the ledger's A/B counts, `_UNRESOLVED`'s place, the
docstring, and deviations 8 and the relay-lint line above).

1. Every Lean answer typed and contained: PASS. `relay_mutation_gate.py --route service:english.command`: 1126/1126 refused; `test_relay_binding_inventory.py` english.command rows (42 passed); `test_a_fill_the_request_does_not_hold_is_unavailable`.
2. Deliverables built, no rule broken: PASS. The table above; no Python copy of a Lean decision (the query projection, deviation 3, is a request projection Lean re-checks); `tests/test_ci2b_ab.py` reads saved evidence only.
3. Tests and gates can fail: PASS. `mutants.json` S1-S7; `trust-mutants.json` 0 SURVIVOR; `test_a_lost_code_or_quoted_name_or_new_reading_fails_the_check`.
4. Python, Lean and Rust agree: PASS. `ab.py check` over 24,208 rows (base = the frozen pre-switch parser); Rust reads no command English.
5. R8 binding: PASS. `command_problem`'s act, role, arity, fills, spans, query and legend count: `test_a_fill_the_request_does_not_hold_is_unavailable` (6 cases), the inventory fuzz.
6. Gate evidence on the final HEAD: PASS for what this item runs (regen 37 entries, lake build, audit, trust map at the final tree); the full gate is the chain's.
7. No unsigned item: PASS. Every DELTA Ruling cell cites R1, R16 or a DRI decision file with its item.
8. Every user-visible change in DELTA: PASS. The A/B's 43 changed rows (rows 2-5), the wrapper's refusals (6), the cap (8).
9. Test selection: PASS. 488/559 units; S1's failing tests are in the selection.
10. Statements say what is claimed: PASS. `tests/test_ci2b_statements.py` and its failing variants; S2 notes `commandFence_needs_context` is about `hasCommandFence`, whose definition the fixture checks.
11. Budgets and limits fail closed: PASS. `test_read_command_relays_lean_verbatim` (`limit` → `ResourceLimit`); `test_command_fences_are_charged_before_they_are_read`.
12. No CPU regression: PASS for the pilots (no UDHR or constitution path reads speech fences); a speech document makes one `english.command` call per command fence and one context decode in the wrapper (200 fences: `test_command_fences_are_charged_before_they_are_read`).
13. `Test-removed` trailers: PASS. `gate_collection.py --check --prebuilt`: 0 removed, 0 refused, 0 stale, 0 malformed.
14. Both directions, cited evidence, spec re-read: PASS. A question fence needs no context and a command fence does; one record reads and two are `QueryMismatch`; 200 fences read and 4097 refused; spec re-read listed above.
15. No overclaim, no silent cut, every check can fail, limits charged first: PASS. Nothing cut (size ruling); S1-S7; the fence charge precedes any read (S7).
