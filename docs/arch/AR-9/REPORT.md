# AR-9 report: split the assist modules

Plan: `docs/ARCHITECTURE-REVIEW-2026-10.md` (branch `design/arch-review`), section 4.3, AR-9; gate
4.1 item 1. Branch `infra/arch-AR-9`. No Lean change. No user-visible change (`DELTA.md`).

## Outcome

Every number in the outcome block is rendered by `report.py` from `evidence/` and checked by
`check_evidence.py` at the batch gate, outside the permanent test suite (D4).

<!-- BEGIN GENERATED AR-9 METRICS -->
- Measured: base `5479466f`, head `e0cbab24` (clean `ve/`).
- `ve/assist/recovery.py` 1,359 lines -> `recovery.py` 348, `recovery_journal.py` 194, `recovery_replay.py` 245, `recovery_commands.py` 661.
- `ve/assist/session.py` 1,338 lines -> `session.py` 436, `session_state.py` 234, `session_proposals.py` 281, `session_views.py` 441.
- Largest assist file: `ve/assist/recovery_commands.py`, 661 lines; files over 700: 0.
- Base definitions syntax-identical at head: 156/163; identical once seam calls are read as the module names: 163/163; through a seam: 7 (`RecoveryService.verify_ledger`, `RecoveryService._undo`, `RecoveryService._resolve_pending`, `RecoveryService.approve`, `RecoveryService._approve`, `RecoveryService._approval`, `RecoveryService.approval_valid`).
- Names the two modules defined that they no longer provide: 0.
- Function-level imports in `ve/assist/`: 25 before, 25 after.
- Seeded faults: 5/5 caught by every named test (9 failing runs); after restoring, 9/9 runs pass.
- Selected test units at `f1ab8177`: 360/360 passed.
- Saved scope: `5479466f..eb433e5b --no-merges`, 14 commit(s): `eb433e5b`, `f1ab8177`, `6ddfe8b2`, `7b44a234`, `9d82676d`, `e0cbab24`, `727f7fa4`, `7759894a`, `8101a733`, `16383a2f`, `7f137b63`, `cb10ebb9`, `27339266`, `9ab9127d`.
- Full gate at `eb433e5b`: passed; 14,363 passed, 92 skipped, 0 failed; 36 Rust tests passed.
<!-- END GENERATED AR-9 METRICS -->

The function-level import count is unchanged on purpose: those imports are read when the
function runs, so a test that replaces `ve.english.parse_english_with_metadata` reaches them.
Moving them to module level would change that, which a pure move must not do.

## What moved where

`RecoveryService` is `class RecoveryService(_Journal, _Replay, _Commands)`; `AssistSession` is
`class AssistSession(_Ledger, _Proposals, _Views)`. Each member is defined in exactly one of these
classes (`test_every_member_has_one_owner`).

| Module | Holds |
|---|---|
| `recovery.py` | construction, the five seams, the command runner (`_command`, `_command_uncached`, `_legacy_command`, `_budget`), the replay loop (`_replay`, `_replay_uncached`, `_replay_inner`), `request_proposer`; re-exports every name below |
| `recovery_journal.py` | `RECOVERY_VERSION`, `Unit`, `_Observations`, `_InvalidLedger`, `_digest`, `_canonical`, `LEDGER_KEYS`, `DIVERGED`; `_Journal`: derived state, seal, events, `to_ledger` |
| `recovery_replay.py` | `_Replay`: `_derived`, `from_ledger`, `verify_ledger`, approval obligations and revalidation (`_approval`, `_catalogue_complete`, `approval_valid`, `_approval_valid`, `_approval_still_valid`) |
| `recovery_commands.py` | limits, `STATES`, `COMMANDS`, the adapter protocols, `nearest_wordings`; `_Commands`: every command and its transition, and the W2/W3 adapter calls |
| `session.py` | construction, parsing, `paraphrase_formula`, the decisions (`_decide`, `_check`, `_entails`, `_validity`, the Lean replays), dispatch (`apply`); re-exports every name below |
| `session_state.py` | formats, options, `AssistError`, `LedgerReplayError`, formula helpers, `Node`; `_Ledger`: `log_rejection`, `to_ledger`, `from_ledger`, recorded model calls |
| `session_proposals.py` | `_Proposals`: freeze, add, accept, rewrite, remove, declare, check_step, premise suggestions, waive, compare, propose, record_usage |
| `session_views.py` | `_Views`: node and target views, `describe_model`, show, sentences, vocabulary, status and its analyses, usage, export |

Two constraints decided the split beyond the plan's three themes per module:

- **The assurance manifest.** Six reviewed broad handlers are keyed by `file:Class.method`, and
  four in-flight branches edit the manifest, so these methods stay where the keys name them
  (`DELTA.md`). That is why the command runner, `_replay_inner` and `request_proposer` stay in
  `recovery.py`, and `apply` and `paraphrase_formula` in `session.py`.
- **Names tests replace.** The assist tests replace names on the `recovery` and `session`
  modules. Moved recovery code reaches them through five seams (`DELTA.md` item 1). Session
  code that reads them (`_decide`, `_check`, `_entails`) stays in `session.py`.

## Coordination (plan 4.2)

Files touched: `ve/assist/recovery.py`, `ve/assist/session.py`, six new `ve/assist/*_*.py`,
`tests/test_assist_split.py`, `tests/conftest.py`, `tools/gate-collection.json`,
`docs/arch/AR-9/`. At the start, and again on 2026-10-11 after each sync with `main` (`96887019`,
then `5479466f`, which merged AR-8), `git diff --name-only main...<branch>` for every branch matching `lean-first/*`,
`readings-defaults/*`, `question-answering/*` and `infra/*` named no file AR-9 touches except the
generated `tools/gate-collection.json`, which is not an overlap (R12). The later
`tests/conftest.py` repair was checked against the same branch set and has no overlap. One branch,
`lean-first/b13b`, changes `tests/test_assist_invariants.py`; AR-9 leaves that file unchanged, as
the plan's fixture requires.

The gate exposed a test fixture regression in `test_interrupted_gate_cannot_record_pass`:
it mocks toolchain setup, so the isolated nested gate has no Lean binary for its new trace
preflight and stops before the interruption the test injects. Its owning test file overlaps
`infra/arch-AR-3`, `infra/arch-AR-4`, and `infra/oom-rootcause`. A narrow fixture in the
non-overlapping `tests/conftest.py` bypasses only that trace lookup for these three test cases;
the production gate still performs it. All three pass in the gate's isolated pytest environment.

**Merge resolution rule** for the one shared inventory (R12): conflict in
`tools/gate-collection.json`: run `uv run python tools/regen_generated.py --resolve` after
`git merge --no-commit`, then `git commit --no-edit`. The sync with `main` used this rule.

## Tests

- `tests/test_assist_split.py` (51 tests): every name the two modules defined is still
  importable from them and is the defining module's object; no moved module binds a name the
  facade owns; each recovery seam reads the facade's name when called; the session decisions
  stay on `AssistSession` in `session.py`; every member has one owner; the six manifest-reviewed
  methods are where the manifest names them.
- `docs/arch/AR-9/check_evidence.py`: this report's block equals `report.py`'s rendering of
  saved evidence, and the evidence is consistent (clean, complete, every fault caught, gate on
  the saved scope). It reads only `evidence/`, never live git. It runs directly at the batch
  gate, outside pytest collection as D4 requires. `tools/batch_evidence.py` does not apply yet:
  it requires corpus comparison and latency evidence that 4.1 item 2 does not ask of AR-9.
- `evidence/selected.json` records each of the 360 selected test units at `f1ab8177`; every
  unit exited 0. The selector could not write its final map to the sandbox's read-only default
  cache, so the already recorded unit results were checked and saved with `test_map.build_map`
  and `test_map.write_map` under `/tmp/ar9-testmap`. `check_evidence.py` checks the saved unit
  outcomes at the batch gate.
- Unchanged and passing: `tests/test_assist.py`, `test_assist_deadline.py`,
  `test_assist_invariants.py`, `test_assist_recovery.py`, `test_assist_recovery_replay.py`,
  `test_b17_owner.py`, `test_assurance_manifest.py`. The corrected selected run and the final
  full gate include these files; their saved counts are in the outcome block.

## Seeded faults (`seed_faults.py`, `evidence/mutants.json`)

All five are Python, the only language whose product code AR-9 changes.

| Fault | File | Claim | Failing tests |
|---|---|---|---|
| `recovery` stops re-exporting `nearest_wordings` | `ve/assist/recovery.py` | names | `test_every_name_..._importable_from_it[ve.assist.recovery-nearest_wordings]`; `test_assist_recovery.py` (import error) |
| `session` stops re-exporting `config_digest` | `ve/assist/session.py` | names | `..._importable_from_it[ve.assist.session-config_digest]`; `test_assist.py::test_astra6_deleted_propose_event_detected_after_metadata_edit` |
| replay imports and calls its own `evaluate` | `ve/assist/recovery_replay.py` | seams | `test_moved_code_does_not_bind_the_names_the_facade_owns[ve.assist.recovery_replay]`; `test_assist_deadline.py::test_situation_evaluation_is_inside_approval_deadline[evaluate]` |
| the deadline seam binds `OPERATION_SECONDS` at import | `ve/assist/recovery.py` | seams | `test_each_recovery_seam_reads_the_facade_name_when_called[OPERATION_SECONDS-_operation_seconds]` |
| `RecoveryService` shadows `_Journal._expect` with a no-op | `ve/assist/recovery.py` | one owner | `test_every_member_has_one_owner[RecoveryService]`; `test_assist_recovery.py::test_ledger_json_restore_and_revision_guard` |

Each fault was removed by the script; every named test passes again afterwards.

## Gate and what was not run

- A gate left running by the expired prior session was still checking `727f7fa4` when this
  continuation committed `e0cbab24`; its saved `gate-result.json` correctly failed source
  identity and does not cover this work. The subsequent gate on `e0cbab24` reached the Python
  suite, but its temporary scratch directory disappeared during the run. That incomplete run
  was interrupted; it produced no usable gate result. The next gate
  attempt at `9d82676d` stopped at clean-tree preflight because its new output filename was
  untracked; no build or test stage ran. The final gate used eight workers on committed
  `eb433e5b` with the ignored `gate-result.json` path and passed.
- The full gate on `7b44a234` passed Lean build/audit and Rust build/tests, then recorded
  14,360 Python passes, 92 skips, and three failures in the same gate interruption test.
  `--rerun-failed` reproduced the three failures in the isolated environment. The fixture
  repair above makes those cases pass there. An initial selected run then found that the
  fixture's static import edge masked one selector mutation; replacing it with the test
  module's existing `gate` reference restored that mutation check. The corrected selected
  run passed all 360 units; its cache save was recovered as recorded above.
- 4.1 item 1: the full gate (`tools/gate.py`) ran on the final code commit; its result is
  `evidence/gate.json` and the scope `evidence/scope.json` (`measure.py --scope`, from the
  merge-base with `main`, `--no-merges`), saved in a later commit that changes only
  `docs/arch/AR-9/`. `split.json` is measured from the same merge-base; `main` changed no file
  under `ve/assist/` and no `tests/test_assist*.py` between the plan's base `c24aeab2` and it, so
  the comparison is the plan's.
- 4.1 item 2 does not apply: the plan's AR-9 row says assist has no corpus in the A/B and its
  tests are the gate. `tools/lean_first_diff.py` was not run.
- 4.1 item 3 does not apply: no Lean file changed, so no `lake build` difference, no statement
  or trust-map change. The Lean build used for the tests was copied from a worktree with the same
  `lean/` tree and confirmed with `lake build`.
- 4.1 item 5 does not apply: no English module changed.

## Build checklist

Lines 1 to 6, 8 to 10, 15 and 17 to 19 cover wires, relayed answers, parsers, verdicts, Lean and
English, none of which AR-9 changes. Line 7: every deadline test in `test_assist_deadline.py`
passes unchanged; the seams keep each injected delay inside its budget. Line 11: the new tests
and `measure.py` read Python with `ast`, not regular expressions. Line 12: the ledger replay tests
pass unchanged. Line 13: five seeded faults, above. Line 14: the new tests write nothing; the
fault script restores every file it changes. Line 16: the list of names the modules defined is
pinned in the test and generated from the base syntax tree in `split.json`; the reviewed handler
list is read from the manifest. Line 20: the outcome block is generated and tested. Line 21:
every acceptance item is AGENT; none is HUMAN or EXTERNAL. Line 22: selected tests while
iterating, then the passing full gate on the repaired committed HEAD. Line 23: no user-visible
delta (`DELTA.md`).

## Follow-ups

- `session_state._constants_of` has no caller (it had none before the split either). AR-9 moves
  it unchanged; deleting it is a separate change.
