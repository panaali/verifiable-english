# AR-2: a narrow freeze (decision D2)

Branch `infra/arch-AR-2`, merge base `4ce477e1` (main, after the review-fix sync; `f98183bf` before it). Plan:
`docs/ARCHITECTURE-REVIEW-2026-10.md` 4.3 AR-2 on
`design/arch-review`; DRI decision D2 (`manage-agents/arch-dri-decisions.md`). Deltas: [DELTA.md](DELTA.md).
Measured numbers: `evidence/freeze.json` (from `measure.py`); tool checks: `evidence/checks.json`; selected tests:
`evidence/selected-tests.json`; seeded bugs: `evidence/mutants.json` (the recorded runs; the temporary mutant runner was removed under D4).
The review fixes are recorded under "Review fixes" below: the readings relay repair (`dfb53762e`) is reverted, and
main's lf-14d closes the same mutations.

## What changed

- **The frozen list** (`lean/VE/Route/frozen-sources.sha256`) keeps only the files D2 names: the 25 modules with K
  declarations in the trust map's side table `tools/trust-classes.json`, and the three frozen-contract decoders
  whose definitions are the `ve.core@0.1` identities. `VE/CertificateWire.lean` holds SHA-256, the restricted
  canonical JSON and the `ve-environment-v0`/`v0.1` and `ve-meaning-` digests. `VE/Json.lean` is the JSON reader
  whose values those digests hash. `VE/Order/Wire.lean` holds the `v0.1-order` identities. The list is
  `DECODERS` in `frozen.py`, and `tests/test_frozen_sources.py::test_each_decoder_defines_a_core_identity`
  checks that each file holds the identity code it is listed for.
  - `python3 VE/Route/frozen.py --write` (from `lean/`) generates the file, with a header. `frozen.py` checks the
    listed hashes, that the listed set is exactly K ∪ decoders, the file's form, and the unchanged `Main.lean`
    rule (`MAIN_BASE` and the two route lines are as before).
  - A new module needs no line unless it holds a K declaration.
- **One owner of the rule.** The pre-commit hook loads the staged `frozen.py` (as it already loads the staged
  `lean/audit.py`) and calls its `problems()`. Before, the hook had its own copy of the rule. A staged inventory,
  `frozen.py` or `tools/trust-classes.json` re-checks the whole list; any other commit re-hashes only the staged
  listed files.
- **`ve/question/LOCK.json`** loses its 12 module hashes. `{"format": "ve.question-lock@2", "question_version": 1}`
  remains, written by `tools/question_lock.py` from the service's export `ve/question/codes.json`. No Question
  module holds a K declaration, so none is frozen. Their compiled source hashes stay in `lean/declarations.txt`
  (checked by `tools/lean_statements.py --check` and `lean/audit.py`).
- **What replaces the broad freeze.** `tools/trust_changes.py --since BASE` (new) is the trust report's list of
  changed files. It lists every `lean/**/*.lean` file whose bytes differ from BASE's, with its K, S, D[V] and G[V]
  lines as `tools/trust_map.py` measures the current tree, and the changed files holding D[V] or G[V] lines, by
  class. A deleted file appears under its class at BASE. Because a line count misses code collapsed onto longer
  lines, it also lists as `widened` the changed files whose trusted lines grew wider than any line they had at
  BASE (review F3). It fails closed when the classification does not validate.
  Statement and predicate changes stay visible
  through `statements.txt` and `predicates.txt`.
- **`tools/wire_contract.py`** no longer writes or checks frozen-inventory lines for its generated modules (WC11
  still compares each generated module whole). The hook's wire check no longer watches or copies the inventory.
  `docs/spec/wire-contract.md` 4.3, 7.2 and L13 are amended to match.

## Measured outcome (`evidence/freeze.json`)

| Number | Before (base) | After (HEAD) |
|---|---:|---:|
| Frozen-list lines | 408 | 30 (28 files and a 2-line header) |
| Files hashed in the frozen list | 408 | 28 (25 K, 3 decoders) |
| Module hashes in `ve/question/LOCK.json` | 12 | 0 |

That is 380 files dropped and none added. The plan's "about 370 of 391 lines" was measured on `c24aeab2`; the list
has grown to 408 since.

Lean-source commits since 2026-09-26 (non-merge commits of the base that edit a `lean/**/*.lean` file): 676. Of
them, 346 (51.2%) edited the frozen list, and 27 (4.0%) touched one of the 28 files frozen now. This is the
retrospective form of the plan's outcome ("55% today; *estimate* under 10%"). The plan's forward measure, over
the two weeks after the merge, is the merge train's to take.

**Collision rule** (for the merge-train sync prompt): "conflict in `lean/VE/Route/frozen-sources.sha256`: take
`main`'s file, run `python3 VE/Route/frozen.py --write` from `lean/`" (`tools/regen_generated.py --write` runs the
same writer). Conflict in `ve/question/LOCK.json`: take either side, run `python3 tools/question_lock.py --write`.

## Files touched and the overlap check

Hand-written files touched: `lean/VE/Route/frozen.py`, `tools/hooks/precommit.py`, `tools/hooks/README.md`,
`tools/question_lock.py`, `tools/wire_contract.py`, `tools/trust_changes.py` (new), `docs/spec/wire-contract.md`,
`tests/test_precommit_hook.py`, `tests/test_wire_contract_lint.py`, `tests/test_wire_contract_s4_lean.py`,
`tests/test_frozen_sources.py` (new), and `docs/arch/AR-2/*`. Generated (R12): the frozen list,
`ve/question/LOCK.json`, `tools/gate-collection.json`.

The initial check against `git diff --name-only main...<branch>` for every unmerged `lean-first/*`,
`readings-defaults/*`, `question-answering/*` and `infra/*` branch found no overlap in those files. An earlier
gate repair of `tests/test_readings_defaults_rd8_report.py` is reverted: that test fails on main too
(`main-known-red.txt`) and belongs to its own fix item, so the branch takes main's file unchanged. Planned files
that overlapped during the AR-2 implementation were avoided:

- `tools/regen_generated.py`: arch-AR-1, arch-AR-3, arch-AR-4, eff-20261011-1, ts-B2, b14c, q2.
- `tools/trust_map.py`: arch-AR-4, b14b. The changed-files report is a new tool for this reason, not a
  `trust_map.py --since` option.
- `tools/gate.py`: arch-AR-3, arch-AR-4. `tools/batch_evidence.py`: arch-20261010-2, arch-AR-3, b14c, b14d.
- `tests/test_regen_generated.py`: arch-AR-1, arch-AR-3, eff-20261011-1. It passes unchanged:
  `frozen.inventory_text()` keeps its meaning.
- `tests/test_question_reading.py`: q2. It passes unchanged: `tools/question_lock.py` keeps its command line.
- `docs/TESTING.md`: ts-B2.

The frozen list (b14a–d, q2) and `ve/question/LOCK.json` (q2) are generated (R12).

After the review fixes, `git diff --stat main...HEAD` names only the files above and `docs/arch/AR-2/*`: the
reverted relay repair's files (`lean/ResponseShape*.lean`, `ve/backends/service_schema.py`,
`tools/relay-gate-allow.json`, the readings schema and its README, the ADR, `tests/test_architecture_docs.py`,
`tests/test_lean_service_schema.py`, `tests/test_relay_mutation_gate.py`) are main's.

## Follow-ups (not done here, because of the overlaps above)

1. `tools/regen_generated.py`'s `question-lock` note still reads "hashes lean/VE/Question/*.lean": change it to
   "the service's question version" once q2 and AR-3/AR-4 have merged.
2. Wire `tools/trust_changes.py --since <merge-base>` into the batch gate beside `trust_map.py --since`
   (`tools/batch_evidence.py` or `tools/gate.py`) after AR-3, AR-4 and AR-5a merge. Until then the batch gate
   (4.1 item 3) runs it by hand. AR-2's own run is in `evidence/checks.json`.
3. q2's evidence names `ve/question/LOCK.json` as relocked for its `Frames.lean` change (its DELTA row D3). After
   AR-2 a Question module edit no longer changes the lock, so that row's "relocked" note no longer applies after the
   merge. The q2 owner should know.
4. Not in AR-2's change list: the assurance manifest's decoder SHA-256 pins (`ve/assurance-manifest.json`
   `lean_decoders`) are another hash copy, which D2's "no other hash copy is kept" also covers. That file belongs
   to running lean-first work (4.2), so it is left for a later batch.

## Checks at the freeze-only head (`evidence/checks.json`, from `checks.py`)

All exit 0: `frozen.py`, `tools/question_lock.py`, `tools/trust_map.py --since f98183bf` (K +0, S +0, D +0, G +0,
tied +0, trusted +0), `trust_map.py --check`, `tools/lean_statements.py --check` (5,330 statements, nothing removed
or changed), `lean/audit.py --check` (5,780 theorems, standard axioms only) and `tools/regen_generated.py --check`
(24 entries). `tools/trust_changes.py --since f98183bf` lists no file, because AR-2 edits no `.lean` source.
`evidence/trust-changes-example-87323095.json` shows the report on a base with Lean changes: 16 files, of them
6 with D[V] lines and 15 with G[V] lines.

Plan 4.1 item 2 (`tools/lean_first_diff.py` over the corpora) was not run at the freeze-only head: that head changed
no `.lean` source or `ve/**/*.py` file, and nothing in `ve/` reads `ve/question/LOCK.json`. The final head changes
none either (the relay repair is reverted). Item 5 (English) does not apply.

`evidence/freeze.json` was remeasured after the sync with main. The files it reads (the frozen list, the question
lock and the trust table) are unchanged after that measurement.

## Tests

- While iterating: `tools/select_tests.py --base 11676c2c --run` at `f658025a`. All 369 test units were selected
  (the frozen list is an input of most Lean tests), with 0 failed. Also `tests/test_frozen_sources.py` (10 tests,
  new), `tests/test_precommit_hook.py` (61), `tests/test_wire_contract_lint.py` and
  `tests/test_wire_contract_s4_lean.py`.
- After syncing with main: `tools/select_tests.py --base f98183bf --run` selected 374 units; 372 completed,
  including 367 passes and five nonzero results (`evidence/selected-tests.json`). The Lean and Rust
  builds passed. The run stopped after five nonzero units: `test_assist.py`, `test_assist_invariants.py`,
  `test_english_evidence.py` and `test_readings_rd6b_differential.py` each reached the selector's 3,600-second
  timeout; `test_readings_defaults_rd8_report.py::test_review_fix_commit_chain_and_final_gate_target` failed
  because it expects eight-character Git hashes while this checkout's `%h` prints nine. That test fails on main
  too (`main-known-red.txt`, its own fix item); an earlier narrow correction of it here is reverted (see "Review
  fixes"). The selector also failed to write its test-map cache under the read-only
  `~/.cache/ve-testmap`; its completed-unit output is in `/tmp/ar2-selected.log`. A serial assist retry advanced
  but was interrupted under host load, so the four timeouts remain unresolved locally. The selected run did not
  finish the two queued units `test_soft_review_regressions.py` and `test_wire_gate_corpus.py`. A combined retry
  advanced through those files without failure output but was interrupted during the slow wire corpus; it has no
  final pass result (`evidence/selected-tests.json`).
- After the deleted-file class fix: `tests/test_frozen_sources.py` passed all 10 tests. The T3 mutant made
  `test_a_body_only_edit_of_a_dv_file_is_reported` fail, and the restored code passed it again.
- The chain's gate on `88b176656` failed on the RD-8 hash-width assertion and collection loss of a renamed
  pre-commit test; the chain's full release gate passed on `924c71dc`. The chain's gate on `50ff88b3` (the
  reviewed head, with the relay repair) failed `tests/test_question_reading.py` (review F1).
- Review fixes (below): at `e34060d4`, `mac-pytest.sh --select -- --base 4ce477e1 --run` selected all 376 units
  (no coverage map for the tree), built Lean, passed `lean/audit.py` (484 files, 5,784 theorems, standard axioms
  only) and ran every unit: **376 exited 0, none failed** (`evidence/selected-review-fix.txt`). That includes
  `tests/test_frozen_sources.py` with the new regression test, `tests/test_question_reading.py` (F1) and the three
  tests listed in `main-known-red.txt` (`test_lean_service.py`'s two sub-tick deadline tests and
  `test_readings_defaults_rd8_report.py`), which passed on that runner; they are pre-existing on main and not
  edited here. `lake build` also passed on the VM after the sync.
- `tools/regen_generated.py --check` passed all 24 entries; `tools/gate_collection.py --check` collected
  15,218 tests, with 12 added and none removed since the merge base `4ce477e1` (`evidence/generated-final.txt`).
  `tools/trust_map.py --since 4ce477e1` reports K, S, D, G, tied and trusted all +0, and
  `tools/trust_changes.py --since 4ce477e1` lists no changed Lean file and nothing widened
  (`evidence/trust-final.txt`).

## Seeded bugs (`evidence/mutants.json`; all killed, all removed)

All thirteen seeds are Python: the freeze-only implementation's eleven, and T4 and T5 from the review fix for F3.
No Lean or Rust source changes (the relay repair's Lean seeds R1–R4 went with it).

| Id | File | Behaviour | Failing test |
|---|---|---|---|
| F1 | `lean/VE/Route/frozen.py` | the list holds the K files | `tests/test_frozen_sources.py::test_the_list_is_the_k_files_and_the_core_decoders` |
| F2 | `lean/VE/Route/frozen.py` | an unhashed edit of a frozen file fails | `tests/test_frozen_sources.py::test_an_unhashed_edit_of_a_k_file_fails` |
| F3 | `lean/VE/Route/frozen.py` | a listed file that is neither K nor a decoder is refused | `tests/test_frozen_sources.py::test_a_new_k_module_must_be_listed_and_a_listed_file_must_be_frozen` |
| H1 | `tools/hooks/precommit.py` | a staged trust-class table re-checks the whole list | `tests/test_precommit_hook.py::test_frozen_guard_rejects_unlisted_modules_bad_inventory_and_main` |
| H2 | `tools/hooks/precommit.py` | the hook refuses an unhashed edit of a frozen file | `tests/test_precommit_hook.py::test_frozen_file_change_requires_an_inventory_update` |
| H3 | `tools/hooks/precommit.py` | a staged deletion of `Main.lean` is refused (found in self-review: the first version skipped the rule) | `tests/test_precommit_hook.py::test_frozen_guard_rejects_unlisted_modules_bad_inventory_and_main` |
| T1 | `tools/trust_changes.py` | a body-only edit of a D[V] file is reported | `tests/test_frozen_sources.py::test_a_body_only_edit_of_a_dv_file_is_reported` |
| T2 | `tools/trust_changes.py` | no report from a classification that does not validate | `tests/test_frozen_sources.py::test_the_report_fails_closed` |
| T3 | `tools/trust_changes.py` | a deleted G[V] file stays in the report under its base class | `tests/test_frozen_sources.py::test_a_body_only_edit_of_a_dv_file_is_reported` |
| T4 | `tools/trust_changes.py` | the width of trusted lines is measured (review F3) | `tests/test_frozen_sources.py::test_trusted_code_collapsed_onto_a_wider_line_is_reported` |
| T5 | `tools/trust_changes.py` | a file whose trusted lines grew wider than its base is listed as widened (review F3) | `tests/test_frozen_sources.py::test_trusted_code_collapsed_onto_a_wider_line_is_reported` |
| Q1 | `tools/question_lock.py` | a Question module edit needs no lock update | `tests/test_frozen_sources.py::test_an_edit_of_a_question_module_needs_no_lock_update` |
| W1 | `tools/wire_contract.py` | `--write` touches no frozen-inventory line | `tests/test_wire_contract_lint.py::test_l13_write_after_a_revision_changes_only_generated_files` |

## Relay mutation gate (`evidence/relay-gate-branch.json`)

The freeze-only head's sweep ran 39 routes and 109,195 mutants, with 133 failures inherited unchanged from main:
128 stale allow-list paths and five accepted readings-route mutations. AR-2 changes no relayed route, schema or
allow list. A repair of those failures inside AR-2 (`dfb53762e`) was reverted on review (F2): main's lf-14d
(`4667e8de6`) had already closed the five readings mutations, and the relay gate's remaining entries are main's.

## Review fixes (`arch-AR-2-review.final.md`)

- **F1** (pre-review gate failed `tests/test_question_reading.py`): the branch is synced with main `4ce477e1`, which
  holds runner-portability's fix (`dccd9cf5a`). `test_the_whole_question_is_bounded_by_the_modes_deadline` passes
  at the synced head. The full gate on the final HEAD is the merge train's (the user's instruction for this round
  forbids a local gate run), so PROBE F1 (a passed `gate-result.json` for HEAD) is left for that run.
- **F2** (relay repair outside AR-2's scope): `dfb53762e` is reverted, with its ADR note, keyword census entry and
  the RD-8 test edit, and the branch is synced with main. PROBE F2 passes: none of the six named files differs
  from main. The class is a batch editing hand-written files outside its plan: `git diff --stat main...HEAD` now
  lists only AR-2's planned files ("Files touched"). The probe compares HEAD with a moving main, and D4 (R11)
  keeps batch evidence out of permanent tests, so it is not a suite test; the merge train's overlap check
  repeats it.
- **F3** (trusted lines collapsed so the trust count reads +0): the line goes with the revert, and PROBE F3 passes
  (the longest line of `lean/ResponseShape.lean` is 132). The class is a line-count measure blind to code
  collapsed onto wider lines. `tools/trust_changes.py`, the D2 trust report, now gives each changed file the width
  of its widest trusted line and of its widest base line, and lists the files whose trusted lines grew wider
  (`widened`). Run on the reviewed tree `50ff88b3` against `f98183bf`, it lists `ResponseShape.lean` (290 > 132)
  and `ResponseShape/Skeleton.lean` (146 > 129). Regression test:
  `tests/test_frozen_sources.py::test_trusted_code_collapsed_onto_a_wider_line_is_reported`; seeded bugs T4, T5.
  `tools/trust_map.py` itself is not changed (overlap with arch-AR-4 and b14b, see above).

## Not done, and why

- The four follow-ups above, because of the overlap rule.
- The plan's forward outcome (the commit share over the two weeks after the merge) can only be measured after the
  merge.
- The full release gate on the final HEAD: the merge train runs it.

## Checklist and sibling lessons

- Checklist 1 (one owner): the freeze rule now lives in `frozen.py` alone; the hook calls it. The K set is read
  from the trust-class table, never copied. Checklist 11: the inventory parsers read the generated format only, and
  the changed-file detection compares git blob ids. Checklist 13: the seeded bugs above, and a constant-pass `frozen.py`
  (F2) fails. Checklist 14: the new tests write only under `tmp_path`, with no sleeps, and their subprocess waits
  use `HANG_TIMEOUT`. Checklist 16: the frozen list is generated, and a test checks that it equals K ∪ decoders.
  Checklist 22: see Tests. Checklist 23: DELTA.md.
- AR-9's F1 (the gate not on the final HEAD): the merge train gates the final committed HEAD.
- AR-9's F2 (an untyped relay field): AR-2 relays nothing; the readings relay is main's.
- AR-9's F3 (picked files overlap in-flight branches): after the revert, AR-2 touches only its planned files.

## Self-review against BUILDER-CHECKLIST

1. **N.A.** AR-2 changes no relayed answer, schema or decoder.
2. **PASS.** The freeze tests trace each changed rule to its owner (`frozen.py`, called by the hook); the overlap section names every shared hand-written file.
3. **PASS.** `evidence/mutants.json` records thirteen killed mutants in changed Python files, including constant-pass checks caught by `test_an_unhashed_edit_of_a_k_file_fails` and `test_trusted_code_collapsed_onto_a_wider_line_is_reported`.
4. **N.A.** No Lean, Python or Rust checker path changes.
5. **N.A.** No relayed field changes.
6. **DEFERRED to the merge train.** The full release gate on the final HEAD is the merge train's; this round's instructions forbid a local gate run. The selected tests, `lake build`, `lean/audit.py` and `regen_generated.py --check` ran on the final code (Tests).
7. **PASS.** `DELTA.md` records the D2/R11 tooling deltas; `test_frozen_sources.py` and `test_precommit_hook.py` cover them.
8. **PASS.** No user-visible checker delta; `tools/trust_map.py --since 4ce477e1` is +0 everywhere.
9. **PASS.** The selected run on the final code is recorded under Tests.
10. **N.A.** No response shape changes.
11. **N.A.** No budget, deadline or public operation changed.
12. **N.A.** No runtime path changes.
