# speed-vocabpar: the vocab mutants file elaborates its mutants in a pool

**Status: built. The stop rule passed on every row. No DRI signature is needed: there is no DELTA row, and trust is +0
(test code only).**

`tests/test_acts_vocab_mutants.py` no longer sets the wall time of a selected run. A module-scoped fixture finds the
items the session will run and elaborates their sources through a bounded pool of `lake env lean` processes. Each
test then reads its own result and asserts exactly what it asserted before. The same helper (`tests/lean_pool.py`)
is applied to `tests/test_acts_lexical_mutants.py`, which has the same pattern.

Under xdist (`tools/gate.py`, R2, the nightlies) and at width 1, no pool starts: every test makes today's
`_elaborate` call.

## Measurement (ve-mac-1, through mac-pytest.sh only)

All numbers come from `logs/` and are recomputed by `check.py`; `evidence.json` holds them.

- **Seconds** are pytest's own "in N s" for the file runs, and runner start to summary for the selected runs.
- **Load** is the Mac's 1/5/15-min load in `mac-pytest.jsonl`. It is sampled when mac-pytest.sh probes the runner,
  before any slot wait, so it can predate the run by up to 94 min. mac-pytest.sh's summary line does not print a
  load.

| run | tree | what | seconds | Mac load at probe | outcome |
|---|---|---|---|---|---|
| file-serial-1 | main ab010c3f0 | vocab file, `-p no:xdist` | 1119.84 | 36.55 36.24 39.87 | 643 passed |
| file-serial-2 | main ab010c3f0 | the same, again | 1588.78 | 47.09 41.18 36.53 | 643 passed |
| file-pool-1 | 2df3fd2a3 | vocab file, pool at 6 | 360.50 | 47.09 41.18 36.53 | 643 passed |
| file-pool-2 | 2df3fd2a3 | the same, again | 501.57 | 35.95 36.87 35.44 | 643 passed |
| lexical-serial | main ab010c3f0 | lexical file | 226.44 | 36.06 33.19 31.58 | 84 passed |
| lexical-pool | 2df3fd2a3 | lexical file, pool at 6 | 41.10 | 44.56 48.19 44.26 | 84 passed |
| seeded-serial | scratch: main's test files + 2 `#guard`s deleted | both files | 1724.81 | 45.53 43.16 43.89 | 5 failed, 722 passed |
| seeded-pool | scratch: 2df3fd2a3 + the same 2 deletions | both files | 584.17 | 42.31 34.74 32.11 | 5 failed, 722 passed |
| select-serial | 5a30735ab + `JOBS = 1` | `--select -- --base ab010c3f0 --run` | 1623 | 42.24 50.27 49.57 | 29 units; only test_lean_pool fails (see below) |
| select-pool | 5a30735ab | the same selected run | 783 | 36.87 47.96 47.25 | 29 units, all passed |

Inside the selected runs, the vocab unit took 1608.4 s at width 1 and 694.7 s with the pool. The lexical unit took
366.5 s and 144.4 s. With the pool, the run's longest unit is now `tests/test_wire_gate_corpus.py` (763.5 s).

The vocab file ran 8 times in all: the 4 file runs, the 2 seeded runs and the 2 selected runs. Three earlier
submissions were cancelled while they waited for a slot, before any test ran.

**Width 1 on the Mac.** mac-pytest.sh does not pass the caller's environment to the runner. So the width-1 selected
run used the same commit with `JOBS = 1` as an uncommitted edit, which is the same path as `VE_TEST_LEAN_JOBS=1`.
That edit makes 2 tests of `tests/test_lean_pool.py` fail, because they pin `JOBS > 1`. `check.py` requires those
to be the run's only failures.

## Stop rule: every row passes (`python3 docs/infra/speed-vocabpar/check.py` exits 0)

| row | measured | limit | pass |
|---|---|---|---|
| file with the pool vs serial, mean of each pair | 431.0 s / 1354.3 s = 0.318 | at most 0.5 | yes |
| whole selected run, width 1 minus pool | 1623 − 783 = 840 s | at least 300 s | yes |
| outcomes, vocab: pool vs serial | 643 node ids, all identical (all passed) | identical | yes |
| outcomes, lexical: pool vs serial | 84 node ids, all identical (all passed) | identical | yes |
| seeded, vocab (`#guard rawCap == 256 && stepBudget == 2100000 && maxReadings == 64` deleted) | the same 4 tests fail with and without the pool: `stepBudget-1000000`, `stepBudget-2100001`, `sweep-number-down-stepBudget-1`, `sweep-number-up-stepBudget-1` | identical, non-empty | yes |
| seeded, lexical (`#guard errS (chk [] 1 "{0} seek asylum,") == …` deleted) | the same 1 test fails with and without the pool: `guard-off-check-3` | identical, non-empty | yes |
| peak RSS of the pooled process tree | 3.38 GB (6 `lean` at once); serial 0.66 GB | under 8 GB | yes |

**Memory.** The runner runs only pytest, so memory was measured on the VM with `rss.py`, which samples the whole
process tree (pytest and every child). The run covered 43 tests (`-k "dropped or swapped"`) at width 6 and at width
1. The width-6 run reached the pool's full width (6 `lean` processes at once), and each process needs about 0.5
GB. On the same VM, the pooled subset took 63.7 s against 312.7 s serially (`logs/rss-*.log`).

**Seeded check.** The deleted guards were chosen so that at least one mutant survives: in the lexical file, only
`guard-off-check-3` is killed by exactly that one guard. Scratch worktrees `ve-vocabpar-base`, `-pool` and
`-scratch` were used and then removed.

## Default width: 6

6 is the worker budget a Mac slot gives one pytest run (`MAC_PYTEST_WORKERS`). With a selected run at width 6, the
vocab unit (694.7 s) ends before the longest other unit (`test_wire_gate_corpus.py`, 763.5 s), so a wider pool would
not shorten the run. Peak memory at 6 is 3.4 GB. The pool is busy only during the first elaborating test's setup:
about 6 to 8 min of the run (`--durations`: 359 s and 500 s).

## What was built (test code only)

| directive | delivered by | test |
|---|---|---|
| fixture + cache by source text; per-test result; missing → serial `_elaborate` | `tests/lean_pool.py` (`elaborate_selected`, `elaborate_all`, `result`); the `elaborated`/`elaborate` fixtures in both mutant files | `tests/test_lean_pool.py::test_a_result_missing_from_the_pool_is_the_tests_own_call` |
| only when not an xdist worker and width > 1; width 1 = today's path | `lean_pool.width`, `elaborate_selected` returns `{}` | `test_no_pool_starts_at_width_1_or_in_an_xdist_worker[width-1, xdist-worker, xdist-worker-with-a-width]` |
| selected items after `-k`/deselection, this module only | `lean_pool.selected` (`session.items`) | `test_the_pool_elaborates_exactly_the_modules_items_that_will_run` (nested pytest: `-k`, a deselected item, another module's `test_a`) |
| same arguments, cwd, HANG_TIMEOUT and env as `_elaborate` | the pool calls `partial(_elaborate, lake)` itself; `_elaborate` is unchanged | file-pool/seeded-pool outcome equality |
| a timeout in the pool = the serial outcome | `elaborate_all` keeps `TimeoutExpired`, `result` raises it | `test_a_timeout_in_the_pool_is_the_outcome_of_the_serial_call` |
| width: one named constant, VE_TEST_LEAN_JOBS overrides | `lean_pool.JOBS`, `width()` | `test_the_width_is_the_setting_else_the_default` |
| sources assembled exactly as the test does | each test and the pool call the same `_unmutated()` / `_mutant(name)` | the outcome equality above |
| lexical file too, with the same equality evidence | `tests/test_acts_lexical_mutants.py` | lexical-* and seeded-* rows |
| evidence + check.py | `evidence.json`, `check.py`, `logs/`, `rss.py` | `check.py` exits 0; it exits 1 on a deleted log, a changed outcome, a skipped test and a stale number (probed) |

Not touched: `tests/test_trust_mutants.py`, `tools/trust_mutants.py`, `tools/select_tests.py`, `tools/test_map.py`,
`tests/conftest.py`. No Lean, Rust, tool or product code changed; trust +0. `tests/history-dependent.json` was
regenerated with `tools/history_tests.py --write`, because `test_lean_pool.py` runs a nested pytest.

No DELTA.md: there is no user-visible delta. Only how long a test run takes changes, and every test's outcome stays
the same.

## Seeded bugs (Python, the only language changed)

`docs/infra/speed-vocabpar/mutants.json`, run by `uv run python tools/mutants.py docs/infra/speed-vocabpar/mutants.json`:
6 of 6 killed (`mutants-evidence.json`). Each bug is in `tests/lean_pool.py`.

- **VP1:** the finder returns every session item. Killed by `test_the_pool_elaborates_exactly_the_modules_items_that_will_run`.
- **VP2:** the xdist check is removed. Killed by `test_no_pool_starts_at_width_1_or_in_an_xdist_worker[xdist-worker]` and `[xdist-worker-with-a-width]`.
- **VP3:** a pool starts at width 1. Killed by `test_no_pool_starts_at_width_1_or_in_an_xdist_worker[width-1]`.
- **VP4:** a missing result raises instead of falling back to the serial call. Killed by `test_a_result_missing_from_the_pool_is_the_tests_own_call`.
- **VP5:** a timeout is read as a killed mutant (returncode 1). Killed by `test_a_timeout_in_the_pool_is_the_outcome_of_the_serial_call`.
- **VP6:** an unexpected exception is cached as a failed run. Killed by `test_a_result_missing_from_the_pool_is_the_tests_own_call`.

The `#guard` deletions above are the seeded check of equality for the Lean side. They are fixtures in a scratch
copy, not a product change.

## Orchestrator lines

- **Times.**
  - Vocab file on the Mac: serial 1119.8 s and 1588.8 s; with the pool 360.5 s and 501.6 s (0.32x).
  - Lexical file: 226.4 s → 41.1 s.
  - Whole selected run of this branch: 1623 s → 783 s, 14.0 min saved. The vocab unit inside it went from 1608 s to
    695 s.
- **Default width.** 6 (`tests/lean_pool.py` `JOBS`). Set `VE_TEST_LEAN_JOBS=1` for exactly the old serial path,
  or any N ≥ 1 for N at once; under xdist the width is always 1.
- **Setting the width on the Mac.** mac-pytest.sh does not forward the variable to ve-mac-1. To set it there, either:
  - `mac-pytest-job.sh` has to pass `VE_TEST_LEAN_JOBS` through (manage-agents; not edited here), or
  - the runner's environment has to set it.

  Locally, prefix the run: `VE_TEST_LEAN_JOBS=1 uv run python tools/select_tests.py --base … --run`.
- **heavy.json.** No regeneration is needed for this file:
  - heavy.json is per node at 10 s, and the slowest single vocab test was 4.36 s serially (`--durations`,
    file-serial-2).
  - The light tier runs under xdist, where the pool is off, so the file's nodes stay light, as they are now.
  - The only node that turns long is `test_the_unmutated_sources_elaborate_cleanly`, and only in a non-xdist run,
    where it carries the pool (about 6 to 8 min of setup). heavy.json does not measure non-xdist runs.
  - The runner order in select_tests already comes from the map's per-unit seconds.

## Not run

- **The full gate.** By instruction, the chain runs it on the final HEAD.
- **Mac memory.** The runner runs only pytest, so memory was measured on the VM.
- **Pre-existing failures.** None were met. `main-known-red.txt` lists only `test_lean_service.py` and rd8 report
  tests, which were not selected.

## Self-review against BUILDER-CHECKLIST

1. **N.A.** No Lean answer is relayed; test code only.
2. **PASS.** The directive table above. Each row has a commit and a test. The rule greps found:
   - no copy of a Lean decision;
   - no new permanent report test (`check.py` is a script, not a suite test, per D4);
   - none of the out-of-scope files (`tests/conftest.py`, `tools/select_tests.py`, `tools/test_map.py`, trust
     mutants) touched.
3. **PASS.**
   - Seeded bugs VP1–VP6: 6/6 killed (`tools/mutants.py`, `mutants-evidence.json`).
   - Seeded `#guard` deletions fail the same tests with and without the pool (seeded-* runs).
   - `check.py` fails on a missing log, a changed outcome, a skipped test and stale evidence (probed).
   - R16: N.A. (no Lean).
4. **PASS.** Base and HEAD side by side: per-node outcomes identical for both files, unseeded and seeded
   (`check.py` rows "outcomes" and "seeded").
5. **N.A.** There is no relay or binding. The pool's cache is keyed by the exact source text, and a miss falls back
   to the serial call (`test_a_result_missing_from_the_pool_is_the_tests_own_call`).
6. **PASS.**
   - The branch sits on main ab010c3f0 (merge base = main).
   - Every measured tree is named by its commit in the table, and its log is saved; no number reads a live git diff.
   - The gate runs on the final HEAD in the chain.
7. **PASS.** No DELTA rows, trust +0, no signature reserved. The stop-rule status is checked on each failing input
   (the `check.py` probes).
8. **PASS.** No user-visible output changes: identical test outcomes on 727 node ids; no product code is touched.
9. **PASS.**
   - The selection (29/467 units) contains both mutant files and `tests/test_lean_pool.py`.
   - Seeded: the width-1 edit to `tests/lean_pool.py` made the selected `tests/test_lean_pool.py` fail
     (select-serial).
10. **N.A.** No Lean statements.
11. **PASS.**
    - The pool keeps `_elaborate`'s HANG_TIMEOUT.
    - A timeout stays an error, never a pass or a kill (`test_a_timeout_in_the_pool_is_the_outcome_of_the_serial_call`, VP5).
    - No sleeps or literal waits: `tests/test_hang_guards.py` passes.
12. **PASS.** Memory measured: 3.38 GB peak at width 6 (`logs/rss-pool.json`). CPU: the same elaborations run, only
    6 at a time. Times are in this report, never in the suite.
13. **PASS.** No test was removed or renamed. `tools/gate_collection.py --check --prebuilt`: 7 added, 0 removed,
    0 refused, 0 stale, 0 malformed.

## Pre-review fix round 1 (gate on 44bdeded9)

- **Failure:** the chain's selected run failed one test,
  `tests/test_regen_generated.py::test_every_script_with_a_writing_mode_is_registered_or_excluded_with_a_reason`,
  because `check.py --write` made `check.py` a writer of a committed file that is not in the registry.
- **Fix:** `check.py` no longer writes any file. `--write` became `--print`, which prints the recomputed
  evidence to stdout (`--print > evidence.json` records it).
  - Registering the script in `NOT_REGENERATED` would have edited `tools/regen_generated.py`, and this item
    is test code only.
  - `evidence.json` is unchanged: `check.py --print` gives it byte for byte, and `check.py` still exits 0 on
    every row.
- **Tests:** the failed test passes. The selected tests were rerun for the fix.
