# AR-4: the trust budget as a ratchet

This batch implements row AR-4 of the architecture plan `docs/ARCHITECTURE-REVIEW-2026-10.md` (branch
`design/arch-review`, section 4.3), under DRI decision D3 (`manage-agents/arch-dri-decisions.md`, standing ruling
R11).

## What changed

- **`docs/trust-baseline.json`** now holds only `budget` (K, S and untied [V], as the merge train last measured
  them on `main`) and `allowances`. Each allowance has the fields `class`, `lines`, `reason`, `signature` and
  `commit`. The allowances are the history, and none is ever removed. The per-file tables, `section11`, `totals`,
  `history` and `signed` are gone. The migration was run once, by `migrate_baseline.py` at the base. It reuses
  `trust_map.from_history`, so the history has one owner.
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
- **`tools/batch_scope.py`** writes a batch's scope from git (`git_scope`: commits `base..head` without merges,
  changed paths with renames as a delete and an add) and checks a saved one against git (`scope_problems`: the base
  is the merge base with `main`, and the commits and paths are exactly git's). `report.py` writes and checks
  `evidence/scope.json` with it.
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
Measured with `tools/trust_map.py` at `81760f3a` against the merge base `96887019`:

| Class | Recorded at the base | Measured at the base | Measured at the head | Starting budget |
|---|---:|---:|---:|---:|
| K | 997 | 997 | 997 | 997 |
| S | 9,791 | 9,791 | 9,791 | 9,791 |
| V | 36,765 | 36,765 | 36,765 | 36,765 |

`docs/trust-baseline.json`: 13,230 lines at the base, 367 at the head (keys before: comment, totals, budget, signed, history, section11, files; 479 per-file rows and 286 `section11` rows left the tree).
History: 35 entries, 34 distinct, became 51 allowances (one per class that grew); 6 carry a DRI signature, 45 were rebaselines with a reason before AR-4.
`trust_map.py --check` at the head: exit 0; allowances introduced: 0, removed: 0.
Commits (`96887019..81760f3a --no-merges`): 26; files changed: 26, none under `ve/`, `lean/` or `rust/`: yes.
Seeded bugs: 17, each killed by its named test: yes.
Full gate at `5ac95cc3`: 14,353 Python passed, 92 skipped or xfailed, 1 failed; 36 native Rust passed.
R13 serial rerun at `5ac95cc3`: 288 passed, 0 failed; tests/test_question_reading.py::test_the_cli_prints_leans_words_with_its_exit_code[A6c] passed on rerun.
<!-- END GENERATED AR-4 METRICS -->

The plan estimated "about 12,600 lines" deleted, and 12,863 were. It also estimated the file at "under 300 lines";
it is 367. That is 10 lines for the comment and the budget, plus 7 lines for each of the 51 allowances the history
became. The file keeps `json.dumps` indent 1, because the `ve-generated` merge driver reproduces only a standard
indent; a denser layout would be rewritten at every merge. The file grows by 7 lines per signed allowance.

Every number above comes from `report.py --collect`. `report.py --check` holds these claims to the saved evidence:
- the check passes;
- the head measures the same as the base;
- the starting budget is the measured base, and DELTA row 1 states it and carries the DRI's signature quoting it;
- the file holds the comment, the budget and the allowances, and nothing else;
- no file under `ve/`, `lean/` or `rust/` changed;
- every seeded bug was killed, each changed product file under `tools/` has one, and they ran on the evidence
  commit's files;
- the saved scope is git's (`batch_scope.scope_problems`);
- the gated commit and the evidence commit differ from HEAD only under `docs/arch/AR-4/`;
- the full gate and its rerun record per-file trust counts that match the evidence head.

Under D4, `report.py --check` runs at the batch gate and in the merge train. No permanent report test was added.

## Reading of the plan

- **The starting budget needs the DRI's signature (DELTA row 1).** D3 in `arch-dri-decisions.md` still says "at
  most 35,892 V", and the base measures V 36,765. The plan corrects this in two places. Section 5 says "the DRI
  re-signs the value measured at AR-4's base". The gate line of row AR-4 says the check passes "after the DRI signs
  the starting budget". So this batch does not count the value as signed by R11. The file and the trust check need
  no change either way: the check caps the head at the measured base whether or not the value is signed.
  This is a HUMAN item; its owner is the DRI. `report.py --check` fails until it is done. To sign, replace the
  Ruling cell of DELTA row 1 with a signature that quotes the value of that row, in the form `SIGNED by the DRI:
  K 997, S 9,791, V 36,765, <date>, <where it is recorded>`. If AR-4 syncs with `main` first, the row's value
  becomes V 36,902 (see "Syncing AR-4 itself with `main`"), and that is the value to sign. A signature of the
  other value does not pass.

- **"Reads the merge base's budget"**: the tool does not trust the recorded number. It measures the base's tree,
  which gives the same value whenever the merge train's `--write` has run. When the recorded number is stale, the
  measured one is the true starting point, and D3 says the budget falls automatically. The tool prints a `note:`
  line when the two differ.
- **"The merge train writes `budget := measured` when the measurement is lower"**: `--write` writes the
  measurement whenever the check passes. The measurement is then at most the base plus the signed allowances of the
  merge, so a higher value is exactly the signed growth. Writing it keeps the recorded budget equal to `main`'s
  measured tree, and that is the cap used outside a git work tree.

## Coordination (plan 4.2)

Files touched: `tools/trust_map.py`, `docs/trust-baseline.json`, `tests/test_trust_ratchet.py`,
`tests/test_consolidation_tools.py`, `docs/arch/AR-4/*` and the shared inventory `tools/gate-collection.json`
(89 test IDs added; `tests/test_consolidation_tools.py::test_rebaseline_needs_a_reason_for_growth` removed, replaced
by `test_rewrite_never_absorbs_growth`, since `--write --reason` no longer exists). These were checked against
`git diff --name-only main...<branch>` for every `lean-first/*`, `readings-defaults/*`, `question-answering/*` and
`infra/*` branch, first at the start of the batch and again on 2026-10-11 at 17:40 UTC, against `main` at
`5479466f`. Since the first check, `readings-defaults/rd6b` and `infra/arch-AR-8` have merged into `main`. The
second check found:

- **`docs/trust-baseline.json`** is also edited by `question-answering/q2`, `lean-first/b13b` and
  `lean-first/b16d`, in the format used before AR-4. It is a generated inventory, so under R12 it is not an
  overlap, and it needs the collision rule below. `main` itself changed it after AR-4's base, through rd6b (three
  history entries, V 36,765 → 36,902). AR-4's own sync with `main` is covered below.
- **`tests/test_consolidation_tools.py`** is also edited by `infra/arch-20261010-1` (AR-1). A trial merge is clean,
  because the hunks are apart.
- **Edited after the review (findings F2 and F4, Follow-ups 1 and 2).** These files are also edited by other
  branches. Trial merges (`git merge-tree`) of AR-4's head on 2026-10-12 were checked against each of them:
  - `tools/gate.py` (AR-3, `infra/ts-B5`): no conflict.
  - `tests/test_gate_rerun.py`, `tests/test_gate_integrity.py` (AR-3, `infra/oom-rootcause`): no conflict.
  - `tools/regen_generated.py` (AR-1, AR-3, AR-5a, `infra/eff-20261011-1`): the one-line `trust-tables` note; no
    conflict.
  - `docs/merge-tooling.md` (AR-1, AR-3): no conflict.
  - The scope check is a new file, `tools/batch_scope.py`. AR-5a (`infra/arch-20261010-2`) adds a different
    `scope_problems` to `tools/batch_evidence.py`, so AR-4 leaves that file alone. Only the generated
    `tools/gate-collection.json` conflicts with AR-3 (R12: regenerate).

**Collision rule.** "Conflict in `docs/trust-baseline.json`: run `python3 tools/regen_generated.py --resolve`. Its
json strategy keeps both sides' allowances. If the file still conflicts, or `--resolve` exits with an error (Follow-up
3), the branch's file predates AR-4 (it has
`totals`, `history` or `files`). In that case, take `main`'s file, then run `python3 tools/trust_map.py --allow
--reason '<the branch's history entry>' --signed '<R6 (DRI-RULINGS.md) when its conditions hold, else the DRI's
signature>'` without `--since`. The base is then the merge base, or HEAD during the merge train's uncommitted
merge. Finally run `python3 tools/regen_generated.py --check --only trust-tables`."

"Conflict in `tools/gate-collection.json`: take `main`'s file and run `uv run python tools/regen_generated.py
--write --only gate-collection`. If AR-1 has deleted the file, take the deletion."

**Syncing AR-4 itself with `main`.** `main` still has the file in the format used before AR-4, and rd6b added
three history entries to it after AR-4's base. `git merge main` therefore conflicts in `docs/trust-baseline.json`.
`tools/regen_generated.py --resolve` cannot resolve it: it crashes on it (Follow-up 3), so the train's
generated-only path stops there. Resolve it this way:
1. `git checkout --ours docs/trust-baseline.json`.
2. Run `uv run python docs/arch/AR-4/migrate_baseline.py MAIN`, where MAIN is the commit being merged. It rewrites
   the file from MAIN's file: the budget is MAIN's measured tree, and every history entry becomes an allowance.
   It also saves `evidence/migration.json` for MAIN.
3. Run `python3 tools/trust_map.py --check`.
4. Commit the merge. Then run `report.py --collect` and `--render`, and commit the evidence.
5. In DELTA rows 1 and 2, update the starting budget and the allowance counts to the numbers in the new evidence.
   Row 1 is the value the DRI signs (DELTA row 1): sign the value at the synced base, not the one at `96887019`.

Trial run on 2026-10-11, merging `main` at `5479466f` into a scratch copy of this branch: `docs/trust-baseline.json`
was the only conflict. After steps 1–3, the budget was K 997, S 9,791, V 36,902, with 55 allowances (49 of them
unsigned rebaselines from before AR-4). `--check` passed, with exit code 0.

**Merge-train step.** After each merge into `main`, run `python3 tools/trust_map.py --write`. It sets the recorded
budget to the measurement and refuses if the check fails. Commit the file if it changed.

## Follow-ups

1. Done after the review: the `trust-tables` note and `docs/merge-tooling.md` now name `--allow --reason
   --signed`. Still open: the `trust-tables` entry could run `trust_map.py --write` as the merge train's writer.
2. Done after the review (F2): `tools/gate.py` records the per-file counts.
3. `tools/regen_generated.py`'s `merge_json` (line 337 on `main` at `5479466f`) crashes with `TypeError: Object of
   type object is not JSON serializable` when one side deletes a key and the other side changes it. Building the
   `Conflict` message calls `_text` on the `_MISSING` sentinel. It should raise `Conflict`. This is a bug on `main`,
   not one AR-4 introduces. AR-4 only makes it show: AR-4 deletes `history` and `totals`, which other branches still
   change.

## Seeded bugs

The 17 mutants in `mutants.json` were run with `uv run python tools/mutants.py docs/arch/AR-4/mutants.json
--evidence docs/arch/AR-4/evidence/mutants.json`, last on the tools after the review fixes. They are in
`tools/trust_map.py`, `tools/gate.py` and `tools/batch_scope.py`, the product code that changed (Python; no Lean or
Rust changed; `tools/regen_generated.py` changed only a note's text). Each made its named test fail and was then
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

## Tests and gate

- While iterating: `tests/test_trust_ratchet.py` and `tests/test_consolidation_tools.py` (373 passed before this
  round's additions, then the selected tests).
- Gate items 2, 3 and 5 of plan 4.1 have nothing to compare, because no file under `ve/`, `lean/` or `rust/`
  changed.
- Earlier verification on `e25a7773` passed the build, audit, native tests and Python collection, but the full
  gate was interrupted during its suite by a two-hour tool limit (`evidence/gate-stages.log`). Its suite was then
  run in 16 foreground chunks: 14,355 passed, 0 failed, and 91 skipped or xfailed across all 14,446 selected
  cases (`evidence/suite-chunks.json`). A full-gate attempt on `75b25445` also passed the pre-suite stages but
  reached a one-hour shell timeout during pytest (exit 124).
- **Final gate under standing ruling R13:** `tools/gate.py --workers 24` ran on clean commit `5ac95cc3`. The
  full gate completed all six required stages: Lean build and audit, Rust build and 36 native tests, and the
  Python suite with its gate plugin, pinned collection and optional-test policy. It collected 14,447 tests,
  selected 14,446 (one live test deselected), and recorded 14,353 passed, 92 skipped or xfailed, and one failed
  (`evidence/gate-full-failed.json`). The sole failure was
  `tests/test_question_reading.py::test_the_cli_prints_leans_words_with_its_exit_code[A6c]`: under host load,
  `english.question` exceeded its 5.09278 s CPU deadline and returned `CheckerUnavailable`.
- `tools/gate.py --workers 1 --rerun-failed` then reran `tests/test_question_reading.py` on the same clean commit.
  All 288 tests passed, including A6c; the result is `rerun-passed` with no failures
  (`evidence/gate-result.json`). R13 counts the full gate plus its same-commit serial rerun as passed. The
  recorded rerun reused the full gate's successful Lean audit and native Rust test stages. This A6c test has one
  known rerun in this batch; no second rerun of it was found in the week's reports.

## Review fixes (`arch-AR-4-review.final.md`)

Each finding was fixed as a class:
- **F1 (B)** is a HUMAN item; its owner is the DRI. No agent can sign the starting budget. DELTA row 1 states the
  value: K 997, S 9,791, V 36,765, or V 36,902 after a sync with `main`. `report.py --check` now fails until that
  row carries the DRI's signature quoting its value (see "Reading of the plan"). So neither value can pass unsigned,
  and a sync that changes the value needs a new signature.
- **F2 (B)**: every gate records the per-file trust counts, and a gate without valid counts fails. The class covers
  all three places that handle the counts: the writer (`--files`), the gate that keeps them, and every reader of the
  record. All three check them with the writer's own schema, `files_problems`. `report.py --check` requires them in
  both saved gate records. The saved records predate the fix, so the probe still fails on them; see "Open after
  the fixes".
- **F3 (B)**: a saved scope is recomputed from git, not trusted. That covers the commits, the changed paths, the
  base, and the types and keys, in `tools/batch_scope.py`. The evidence checker also binds the gated commit and the
  evidence commit to HEAD. Before the fix, nothing tied the gate to the code it covered.
- **F4 (B)**: one signature rule applies to every way an allowance enters: `--allow --signed`, the file, and the
  allowances a change introduces. The migration's label, and any text marked unsigned or pending, grant nothing.

Probes: F2, F3 and F4 each failed before the fix. F3 and F4 pass after it. F4's probe is
`tests/test_trust_ratchet.py::test_review_f4_probe`. F3's probe reads AR-4's saved evidence, so under D4 it stays a
`report.py --check` claim. Its class is tested by `tests/test_batch_scope.py`. F2's probe reads the saved full-gate
record, which predates the fix, so it still fails until the next full gate is saved.

### Tests run for the fixes

- `lake build`: success, 881 jobs. `python lean/audit.py`: PASS, 479 files and 5,196 theorems.
- `tools/select_tests.py --run` selected 27 units. 25 test files passed, including
  `tests/test_consolidation_tools.py`, `tests/test_trust_ratchet.py`, `tests/test_gate*.py` and
  `tests/test_batch_scope.py`.
  - `tools/test_layer_policy.py` failed one subtest, `test_documented_python_layers_match_policy` (layer 4:
    `ask`). It fails the same way at the merge base `96887019`, so AR-4 did not cause it.
  - `tests/test_wire_gate_corpus.py` did not finish within the one-hour limit, nor in a separate 50-minute run
    with 8 workers, on a host running other worktrees' full gates. It was selected only because it lists the
    `docs/arch/AR-4/` directory. It reruns the soft-norms and contract tests, and AR-4 does not touch them.
- Seeded bugs: 17/17 killed (`evidence/mutants.json`).

### Open after the fixes

- **HUMAN (the DRI):** sign the starting budget (F1).
- **Not run here: the full gate on the final HEAD.** The worker instructions leave it to the merge train's branch
  verify and the nightly suite. The saved full gate (`5ac95cc3`) and its rerun predate these fixes, which changed
  `tools/` and `tests/`, and the records have no trust counts. So `report.py --check` fails on them by design. To
  close it, run `tools/gate.py` on the final HEAD, save the record and any R13 rerun as
  `evidence/gate-full-failed.json` and `evidence/gate-result.json` (or adapt `problems()` to a clean pass), then
  run `report.py --collect`, `--render` and `--check`.
- AR-5a's `scope_problems` (`infra/arch-20261010-2`, `tools/batch_evidence.py`) checks only the shape of a saved
  scope, not git. That is the class of F3. When it merges, it should call `tools/batch_scope.scope_problems`.
