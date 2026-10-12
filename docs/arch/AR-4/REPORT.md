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
    branch's step, and the signature is required.
  - `--write` sets `budget := measured` after the check passes. It refuses on any branch but `main`, because it is
    the merge train's step.
  - `--files PATH` writes the per-file counts to a file for the gate record, never into the tree.
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
Measured with `tools/trust_map.py` at `c41af506` against the merge base `96887019`:

| Class | Recorded at the base | Measured at the base | Measured at the head | Starting budget |
|---|---:|---:|---:|---:|
| K | 997 | 997 | 997 | 997 |
| S | 9,791 | 9,791 | 9,791 | 9,791 |
| V | 36,765 | 36,765 | 36,765 | 36,765 |

`docs/trust-baseline.json`: 13,230 lines at the base, 367 at the head (keys before: comment, totals, budget, signed, history, section11, files; 479 per-file rows and 286 `section11` rows left the tree).
History: 35 entries, 34 distinct, became 51 allowances (one per class that grew); 6 carry a DRI signature, 45 were rebaselines with a reason before AR-4.
`trust_map.py --check` at the head: exit 0; allowances introduced: 0, removed: 0.
Commits (`96887019..c41af506 --no-merges`): 11; files changed: 14, none under `ve/`, `lean/` or `rust/`: yes.
Seeded bugs: 10, each killed by its named test: yes.
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
- the starting budget is the measured base;
- the file holds the comment, the budget and the allowances, and nothing else;
- no file under `ve/`, `lean/` or `rust/` changed;
- every seeded bug was killed on this `trust_map.py`.

Under D4, `report.py --check` runs at the batch gate and in the merge train. No permanent report test was added.

## Reading of the plan

- **The starting budget needs the DRI's signature (DELTA row 1).** D3 in `arch-dri-decisions.md` still says "at
  most 35,892 V", and the base measures V 36,765. The plan corrects this in two places. Section 5 says "the DRI
  re-signs the value measured at AR-4's base". The gate line of row AR-4 says the check passes "after the DRI signs
  the starting budget". So this batch does not count the value as signed by R11. The file and the check need no
  change either way: the check caps the head at the measured base whether or not the value is signed.

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
- **Avoided.** These files are stale after AR-4, but other branches edit them, so this batch left them alone (see
  Follow-ups):
  - `tools/regen_generated.py`, edited by AR-1 (`infra/arch-AR-1`, `infra/arch-20261010-1`), AR-3 and AR-5a
    (`infra/arch-20261010-2`);
  - `docs/merge-tooling.md`, edited by AR-1 and AR-3;
  - `tools/gate.py`, edited by AR-3 and `infra/ts-B5`.

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

## Follow-ups (not done here: other branches edit the files)

1. `tools/regen_generated.py:102` (`trust-tables` note) and `docs/merge-tooling.md:56` still tell people to use
   `trust_map.py --write --reason`. It is now `--allow --reason --signed`, and `--write` is the merge train's.
   An old command now fails with a usage error ("--reason and --signed go with --allow"), so it cannot rebaseline
   silently. The `trust-tables` entry could also run `trust_map.py --write` as the merge train's writer.
2. `tools/gate.py` should write `trust_map.py --files` into the gate record (the git note that
   `tools/batch_evidence.py` reads). The producer exists; only the call is missing.
3. `tools/regen_generated.py`'s `merge_json` (line 337 on `main` at `5479466f`) crashes with `TypeError: Object of
   type object is not JSON serializable` when one side deletes a key and the other side changes it. Building the
   `Conflict` message calls `_text` on the `_MISSING` sentinel. It should raise `Conflict`. This is a bug on `main`,
   not one AR-4 introduces. AR-4 only makes it show: AR-4 deletes `history` and `totals`, which other branches still
   change.

## Seeded bugs

The ten mutants in `mutants.json` were run with `uv run python tools/mutants.py docs/arch/AR-4/mutants.json
--evidence docs/arch/AR-4/evidence/mutants.json`. Every one is in `tools/trust_map.py`, the only product code that
changed (Python; no Lean or Rust changed). Each made its named test fail and was then restored:

| Id | Behaviour broken | Test that failed |
|---|---|---|
| M1 | growth needs no allowance up to 10 lines | `test_ten_untied_lines_need_a_signed_allowance` |
| M2 | inherited allowances count again | `test_an_allowance_the_base_has_is_not_this_changes` |
| M3 | cap from the recorded budget, not the measured base | `test_deleting_trusted_lines_lowers_the_budget_at_the_merge` |
| M4 | an uncommitted merge on main is checked against HEAD^1 | `test_an_uncommitted_merge_on_main_is_checked_against_head` |
| M5 | removed allowances accepted | `test_an_allowance_is_never_removed` |
| M6 | `--write` allowed on a branch | `test_ten_untied_lines_need_a_signed_allowance` |
| M7 | blank signature accepted | `test_every_allowance_field_is_typed[-signature]`, `test_budget_check_needs_a_signed_allowance` |
| M8 | a duplicated allowance accepted | `test_an_allowance_the_base_has_is_not_this_changes` |
| M9 | extra keys (per-file tables) accepted in the file | `test_the_file_holds_only_the_budget_and_allowances[data3]` |
| M10 | the duplicated history entry kept twice | `test_history_becomes_allowances` |

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
