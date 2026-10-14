# AR-4: the trust budget as a ratchet

This batch implements row AR-4 of the architecture plan `docs/ARCHITECTURE-REVIEW-2026-10.md` (branch
`design/arch-review`, section 4.3), under DRI decision D3 (`manage-agents/arch-dri-decisions.md`, standing ruling
R11). Its starting budget is signed by standing ruling R15 (DELTA row 1).

## What changed

- **`docs/trust-baseline.json`** now holds only `budget` (K, S and untied [V], as the merge train last measured
  them on `main`) and `allowances`. Each allowance has the fields `class`, `lines`, `reason`, `signature` and
  `commit`. The allowances are the history, and none is ever removed. The per-file tables, `section11`, `totals`,
  `history` and `signed` are gone. `migrate_baseline.py` wrote the file from the merge base's file, last at the
  merge base `9f40783b` when AR-4 last synced with `main` on 2026-10-14. It reuses `trust_map.from_history`, so the
  history has one owner.
- **`tools/trust_map.py`** has four modes:
  - `--check` measures the head. Its base is `git merge-base HEAD main`. On main's tip the base is the first
    parent, or HEAD itself while a merge is uncommitted, as in `tools/regen_generated.py --resolve`. `--since REV`
    sets the base by hand. The tool measures the base's committed `lean/` and side table now (`measure_rev`). The
    cap of each class is the base's lines plus the allowances the head's file adds to the base's (`introduced`).
    The check fails on any excess, on a removed allowance, and on a malformed or duplicated allowance. A deletion
    lowers the cap at once, without waiting for the merge train's `--write`.
  - `--allow --reason TEXT --signed SIGNATURE` appends one allowance per class that grew past the cap. This is the
    branch's step, and the signature is required. One rule (`signature_problems`) decides what a signature is, for
    `--signed`, for the file and for the allowances a change introduces: it names the DRI (or a standing ruling of
    DRI-RULINGS.md) and is not marked unsigned or pending. The migration's `unsigned: ...` label is accepted only
    on an allowance the base already has.
  - `--write` sets `budget := measured` after the check passes. It refuses on any branch but `main`, because it is
    the merge train's step.
  - `--files PATH` writes the per-file counts to a file for the gate record, never into the tree.
    `files_problems` is their schema.
- **`tools/gate.py`** runs `trust_map.py --files` after the Lean build, in a full gate and in a rerun, and keeps
  the counts as the record's `trust`. Missing counts, or counts that fail `files_problems`, fail the gate.
- **`tools/batch_evidence.py`** gains the shared checks of a gate record's trust counts (`gate_trust_problems`) and
  of an R13 pair, a failed full gate and its same-commit serial rerun (`rerun_pair_problems`). With the existing
  `gate_record_problems`, they check any value and return problems, never raise (recheck F7).
- **`tools/batch_scope.py`** writes a batch's scope from git (`git_scope`: commits `base..head` without merges,
  changed paths with renames as a delete and an add) and checks a saved one against git (`scope_problems`: the base
  is the merge base with `main`, and the commits and paths are exactly git's). `report.py` writes and checks
  `evidence/scope.json` with it.
- **`main`'s readers of the old file** (DELTA row 7): the `ve-generated` merge driver derives `totals` and `budget`
  only from per-file counts, so it merges AR-4's file (which has none) by value instead of crashing on it
  (`tools/regen_generated.py`, `DERIVED_FROM`); `tools/architecture_numbers.py` measures the trust classes of the
  commit with `trust_map.measure_rev`; the RD-6b report test reads the history from the allowances.
- **Fixtures** are in `tests/test_trust_ratchet.py`, which runs the tool over small git histories:
  - ten new untied V lines fail without an allowance and pass with one;
  - an allowance the base already has is inherited, and a copy of it is refused;
  - deleting trusted lines lowers the budget at the merge;
  - two branches that each add an allowance merge through the `ve-generated` driver (json strategy) with no
    conflict on totals;
  - an uncommitted merge on `main` is checked against HEAD;
  - an allowance is never removed;
  - every allowance field is typed;
  - the committed file passes its check.
- **`tests/test_consolidation_tools.py`**: its trust-map parts are moved to the new format.

## Measured outcome

<!-- BEGIN GENERATED AR-4 METRICS -->
Measured with `tools/trust_map.py` at `6b3e1879` against the merge base `9f40783b`:

| Class | Recorded at the base | Measured at the base | Measured at the head | Starting budget |
|---|---:|---:|---:|---:|
| K | 997 | 997 | 997 | 997 |
| S | 9,788 | 9,788 | 9,788 | 9,788 |
| V | 37,495 | 37,495 | 37,495 | 37,495 |

`docs/trust-baseline.json`: 13,551 lines at the base, 500 at the head (keys before: comment, totals, budget, signed, history, section11, files; 484 per-file rows and 286 `section11` rows left the tree).
History: 52 entries, 51 distinct, became 70 allowances (one per class that grew); 6 carry a DRI signature, 64 were rebaselines with a reason before AR-4.
`trust_map.py --check` at the head: exit 0; allowances introduced: 0, removed: 0.
Commits (`9f40783b..6b3e1879 --no-merges`): 39; files changed: 26, none under `ve/`, `lean/` or `rust/`: yes.
Seeded bugs: 22, each killed by its named test: yes.
<!-- END GENERATED AR-4 METRICS -->

The file is 500 lines: 10 for the comment and the budget, plus 7 for each of the 70 allowances the history became
(13,051 lines fewer than at the base; the plan estimated "about 12,600" deleted and the file "under 300 lines" when
the history had 35 entries). The file keeps `json.dumps` indent 1, because the `ve-generated` merge driver
reproduces only a standard indent; a denser layout would be rewritten at every merge. The file grows by 7 lines per
signed allowance.

Every number above comes from `report.py --collect`. `report.py --check` first checks each saved file against its
writer's schema (budget, migration, scope, seeded bugs), then holds these claims to the saved evidence:
- the check passes;
- the head measures the same as the base;
- the starting budget is the measured base, DELTA row 1 states it, and its Ruling cell is R15's signature quoting it;
- the file holds the comment, the budget and the allowances, and nothing else;
- no file under `ve/`, `lean/` or `rust/` changed;
- every seeded bug was killed, each changed product file under `tools/` has one, and they ran on the evidence
  commit's files;
- the saved scope is git's (`batch_scope.scope_problems`);
- the evidence commit, and with `--gate` the gated commit, differ from HEAD only under `docs/arch/AR-4/`;
- with `--gate GATE.json [RERUN.json]`: the full gate of the final HEAD passed (or, under R13, failed only tests
  its serial rerun passed), and every record carries per-file trust counts whose budget is the evidence head's.

Under D4, `report.py --check` runs at the batch gate and in the merge train; there is no report test. No gate
record is kept in the tree: the chain runs the full gate on the final HEAD and passes its record with `--gate`.

## Reading of the plan

- **The starting budget (DELTA row 1)** is signed by standing ruling R15: the value `tools/trust_map.py` measures
  at AR-4's merge base with `main` when it merges. After the syncs of 2026-10-14 that is K 997, S 9,788, V 37,495
  at `9f40783b`. R15 signs a newly measured value when every rise since `5479466f` comes from a reviewed merge on
  `main`; the budget changed since only through the `approved by review` merges row 1 lists. If AR-4 syncs
  with `main` again and the value changes, `report.py --check` fails until row 1 quotes the new value.
- **"Reads the merge base's budget"**: the tool does not trust the recorded number. It measures the base's tree,
  which gives the same value whenever the merge train's `--write` has run. When the recorded number is stale, the
  measured one is the true starting point, and D3 says the budget falls automatically. The tool prints a `note:`
  line when the two differ.
- **"The merge train writes `budget := measured` when the measurement is lower"**: `--write` writes the
  measurement whenever the check passes. The measurement is then at most the base plus the signed allowances of the
  merge, so a higher value is exactly the signed growth. Writing it keeps the recorded budget equal to `main`'s
  measured tree, and that is the cap used outside a git work tree.

## Coordination (plan 4.2)

Files touched: `tools/trust_map.py`, `tools/gate.py`, `tools/batch_scope.py`, `tools/batch_evidence.py`,
`tools/regen_generated.py`, `tools/architecture_numbers.py`, `docs/trust-baseline.json`, `docs/merge-tooling.md`,
the tests named above and `docs/arch/AR-4/*`. Overlaps were checked at the start of the batch and on 2026-10-11
against every `lean-first/*`, `readings-defaults/*`, `question-answering/*` and `infra/*` branch; trial merges of
the files edited after the first review (`tools/gate.py`, `tests/test_gate_rerun.py`, `tests/test_gate_integrity.py`,
`tools/regen_generated.py`, `docs/merge-tooling.md`) had no conflict.

**Sync with `main` (2026-10-14, `8594f1d0`, then `9f40783b`).** `docs/trust-baseline.json` was the only content
conflict, and `tools/gate-collection.json` (deleted on `main` by AR-3) took the deletion. Each time the budget file
was rewritten by `migrate_baseline.py MAIN` (the last evidence is `evidence/migration.json`); `trust_map.py --check`
passed after each merge commit.

**Syncing AR-4 with `main` again** (the merge train's sync, while `main` still has the format before AR-4):
`git merge main` conflicts in `docs/trust-baseline.json`. Resolve it by running
`uv run python docs/arch/AR-4/migrate_baseline.py MERGE_HEAD` (it rewrites the file from main's: the budget is
main's measured tree, every history entry an allowance), `python3 tools/trust_map.py --check`, commit the merge,
then `report.py --collect`, `--render`, and set DELTA rows 1 and 2 to the new evidence (row 1 quotes the measured
value under R15) before `report.py --check`. The Follow-up 3 crash of `merge_json` on a deleted key is fixed on `main` (`_text` of `_MISSING`).

**Collision rule.** "Conflict in `docs/trust-baseline.json`: run `python3 tools/regen_generated.py --resolve`. Its
json strategy keeps both sides' allowances. If the file still conflicts, the branch's file predates AR-4 (it has
`totals`, `history` or `files`). In that case, take `main`'s file, then run `python3 tools/trust_map.py --allow
--reason '<the branch's history entry>' --signed '<R6 (DRI-RULINGS.md) when its conditions hold, else the DRI's
signature>'` without `--since`. The base is then the merge base, or HEAD during the merge train's uncommitted
merge. Finally run `python3 tools/regen_generated.py --check --only trust-tables`."

**Merge-train step.** After each merge into `main`, run `python3 tools/trust_map.py --write`. It sets the recorded
budget to the measurement and refuses if the check fails. Commit the file if it changed.

## Follow-ups

1. The `trust-tables` entry of `tools/regen_generated.py` could run `trust_map.py --write` as the merge train's
   writer.
2. `tools/batch_evidence.py --check` (evidence.toml batches) does not yet require trust counts in a gate record:
   gate records saved before AR-4 have none. A batch gated after AR-4 merges can opt in through
   `gate_trust_problems`.

## Seeded bugs

The 22 mutants in `mutants.json` were run with `uv run python tools/mutants.py docs/arch/AR-4/mutants.json
--evidence docs/arch/AR-4/evidence/mutants.json`, last on the final tools after the sync. They are in every product
file under `tools/` that changed (Python; no Lean or Rust changed). Each made its named test fail and was then
restored:

| Id | Behaviour broken | Test that failed |
|---|---|---|
| M1 | growth needs no allowance up to 10 lines | `test_ten_untied_lines_need_a_signed_allowance` |
| M2 | inherited allowances count again | `test_an_allowance_the_base_has_is_not_this_changes` |
| M3 | cap from the recorded budget, not the measured base | `test_deleting_trusted_lines_lowers_the_budget_at_the_merge` |
| M4 | an uncommitted merge on main is checked against HEAD^1 | `test_an_uncommitted_merge_on_main_is_checked_against_head` |
| M5 | removed allowances accepted | `test_an_allowance_is_never_removed` |
| M6 | `--write` allowed on a branch | `test_ten_untied_lines_need_a_signed_allowance` |
| M7 | blank or non-string signature accepted | `test_every_allowance_field_is_typed`, `test_budget_check_needs_a_signed_allowance` |
| M8 | a duplicated allowance accepted | `test_an_allowance_the_base_has_is_not_this_changes` |
| M9 | extra keys (per-file tables) accepted in the file | `test_the_file_holds_only_the_budget_and_allowances[data3]` |
| M10 | the duplicated history entry kept twice | `test_history_becomes_allowances` |
| M11 | a new allowance with the migration's `unsigned: ...` label grants growth (F4) | `test_review_f4_probe` |
| M12 | any non-blank text is a signature (F4) | `test_a_new_allowance_without_the_dris_signature_grants_nothing` |
| M13 | per-file trust counts that do not add up are accepted (F2) | `tests/test_gate_trust.py::test_a_gate_without_valid_trust_counts_fails` |
| M14 | the gate does not keep the trust counts (F2) | `tests/test_gate_trust.py::test_every_gate_records_the_per_file_trust_counts` |
| M15 | a gate whose `--files` wrote nothing passes (F2) | `tests/test_gate_trust.py::test_a_gate_without_valid_trust_counts_fails` |
| M16 | a saved scope's commits are not compared with git (F3) | `tests/test_batch_scope.py::test_every_change_to_a_scope_is_a_problem_never_a_crash` |
| M17 | a saved scope's base need not be the merge base (F3) | `tests/test_batch_scope.py::test_a_scope_collected_against_another_base_is_a_problem` |
| M18 | a gate record's trust counts of another tree are accepted (F7) | `tests/test_gate_trust.py::test_genuine_gate_records_pass_the_shared_checks` |
| M19 | an R13 rerun of another commit is accepted (F7) | `tests/test_gate_trust.py::test_every_retyped_node_of_a_gate_record_is_a_problem_never_a_crash` |
| M20 | a boolean failure count passes as an integer (F7) | `tests/test_gate_trust.py::test_every_retyped_node_of_a_gate_record_is_a_problem_never_a_crash` |
| M21 | the merge driver recomputes AR-4's budget from per-file counts it does not have (sync) | `tests/test_regen_generated.py::test_trust_merge_of_the_ar4_budget_file_keeps_main_budget_and_both_allowances` |
| M22 | the map reads trust totals from the budget file (sync) | `tests/test_architecture_docs.py::test_measure_on_a_small_tree` |

## Tests and gate

- No file under `ve/`, `lean/` or `rust/` changed, so gate items 2, 3 and 5 of plan 4.1 have nothing to compare.
- **Full gate: not run here.** The chain runs `tools/gate.py` on the final HEAD (Mac test runner, VM fallback),
  then `report.py --check --gate <its record>` (and the R13 rerun's record after it, naming the retried tests).
  The earlier failed full gate of `5ac95cc3`, its R13 rerun, stage log and chunk run predated the review fixes and
  had no trust counts; they are deleted (DRI note of 2026-10-14).
- This round (looprecheck2 and the DRI note), on the synced branch:
  - `lake build`: success, 887 jobs. `python lean/audit.py`: PASS, 483 source files, 5,784 named theorems.
  - Selected tests (`select_tests --base 8594f1d0 --run`, before the second sync, 376 units; the Mac runner's setup failed, so it ran on
    the VM): 288 units ran before the one-hour limit. 285 passed. `tests/test_nested_pytest.py` failed on a
    fault of this round's first code (a hand-copied stage tuple, now the gate's `RERUNNABLE`) and passed after the
    fix. `tests/test_architecture_docs.py::test_stale_statement[9]` fails on `main` too (the map names
    `NormsMain.lean`, `RightsMain.lean` and `RiskMain.lean`, which `main` does not have).
    `tests/test_readings_defaults_rd8_report.py::test_review_fix_commit_chain_and_final_gate_target` compares
    8-character `%h` hashes, and `c3d86995` now needs 9 characters in the shared object store, so it fails on any
    checkout of this repository. The other 86 units, minus `tests/test_wire_gate_corpus.py`, ran next: 3,041
    passed and one failed, `tests/test_readings_rd6b_differential.py::test_generated_documents_agree_on_both_routes[2]`,
    a Lean CPU deadline (`CheckerUnavailable`, 5.09 s) under host load. It passed on a serial rerun.
    `tools/test_layer_policy.py`: 39 tests, OK.
    `tests/test_wire_gate_corpus.py` ran last on its own: 8 passed in 21 minutes.
  - Seeded bugs: 22/22 killed (`evidence/mutants.json`).
  - After the second sync (`9f40783b`, which changed only English-runner Lean and tests on `main`): `lake build`
    888 jobs, `lean/audit.py` PASS (484 files), `trust_map.py --check` PASS. The test files of AR-4's changes, the merge's and
    `tests/test_english_runner_root.py` (12 files, `-n 8`): 611 passed, and `test_stale_statement[9]` failed as on
    `main`.
  - `report.py --check`: exit 0, with the note that no gate record was given.

## Review fixes

### First review (`arch-AR-4-review.final.md`)

- **F1 (B)**: the starting budget needed the DRI's signature (now R15's, see the loop recheck 2 below).
- **F2 (B)**: every gate records the per-file trust counts, and a gate without valid counts fails. The writer
  (`--files`), the gate that keeps them, and every reader of the record check them with the writer's own schema,
  `files_problems`.
- **F3 (B)**: a saved scope is recomputed from git, not trusted (`tools/batch_scope.py`), and the evidence checker
  binds the gated commit and the evidence commit to HEAD.
- **F4 (B)**: one signature rule applies to every way an allowance enters: `--allow --signed`, the file, and the
  allowances a change introduces. The migration's label, and any text marked unsigned or pending, grant nothing.

### Loop recheck 1 (`arch-AR-4-looprecheck1.final.md`)

- **F5 (B):** `report.py --check` validates the saved scope through `batch_scope.scope_problems` before reading
  path entries or rendering metrics.
- **F6 (B):** `trust_map.files_problems` checks the exact keys and non-negative integer types of both aggregate
  records (`tests/test_trust_ratchet.py::test_review_f6_probe_rejects_float_budget`, `tests/test_gate_trust.py`).

### Loop recheck 2 (`arch-AR-4-looprecheck2.final.md`) and the DRI note of 2026-10-14

- **F1:** AR-4 synced with `main` (`8594f1d0`, then `9f40783b`). DELTA row 1 states the value measured at that merge base,
  K 997, S 9,788, V 37,495, and its Ruling cell reads `SIGNED by standing ruling R15 (DRI-RULINGS.md): K 997,
  S 9,788, V 37,495`. `report.py --check` requires exactly that text quoting the evidence's measured value, and
  passes.
- **F2:** the gate writes the trust counts (since the first review). The stale saved gate records are deleted, not
  kept as evidence. The final-HEAD gate's record is checked with `--check --gate`: a record without trust counts is
  refused ("the gate record has no per-file trust counts").
- **F7 (B):** the class is "a malformed evidence file crashes the evidence checker". Every saved file is now
  checked against its writer's schema before use (`budget_shape`, `migration_shape`, `batch_scope.scope_problems`,
  `batch_evidence.mutant_problems`), gate records by the shared `tools/batch_evidence.py` checks, and anything they
  miss fails closed in `problems()`. The recheck's probe replaced `gate-full-failed.json`, which is now deleted and
  never read, so its literal form no longer reaches a gate check. The same input through `--gate` (`{}`) is refused
  with "a full gate record names no gated commit", and so are invalid JSON and a record without trust counts.
  Permanent regressions are on the shared checks (D4 allows no report test):
  `tests/test_gate_trust.py::test_review_f7_probe_a_malformed_gate_record_is_refused` (`{}`, `[]`, null, 7, true,
  a string, a list 10,000 deep) and `::test_every_retyped_node_of_a_gate_record_is_a_problem_never_a_crash`
  (every node of genuine `tools/gate.py` records retyped). The latter found a list-valued failure stage raising
  `TypeError` in the first version of the R13 check, fixed before the evidence was collected. An ad-hoc pass
  retyping every node of `budget.json` and `migration.json` gave 345 specific problems, no fall-through to the
  fail-closed handler, and 26 accepted same-type values that only the rendered block uses (and `--check`
  compares that block).
- **D4:** `tests/test_ar4_report.py` is removed; its scope cases are covered by `report.py --check` and
  `tests/test_batch_scope.py`. The evidence directory is under 1 MB.

### Open after the fixes

- **The full gate on the final HEAD** (the chain, then `report.py --check --gate`).
