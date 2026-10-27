# eff-20261027-1: the cold statement dump in parallel parts, and a regen timing log

No DRI signature is needed and no row is reserved for the DRI: there is no user-visible delta (tooling speed and
a measurement log only), so there is no DELTA.md. Trust +0 (no Lean, Rust or product-code change).

Source: `manage-agents/reviews/efficiency-daily-20261027.md`; PIPELINE-LIMITS L76 (the dump cache helps only when
no Lean file changed), L105 and L110 (the train's branch regen runs the same dump), L111 (this defect).

## Result

The stop rule passed, so the split is built. On the VM, at comparable load, the median cold dump fell from
**348.1 s to 89.0 s (−259.1 s)**. The Statements step fell from a median of 244.1 s to 16.0 s. The outputs were
byte-identical on all three trees, and the parts' peak RSS together (13.1 GB) stayed under lean/audit.py's own
parallel parts (24.5 GB).

`python3 docs/infra/eff-20261027-1/check.py` recomputes every row from the saved runs (`runs/*.json`, written by
`probe.py`). It exits nonzero when a row is missing, not `pass`, or disagrees with its runs. Its result is
`PASS: 10 rows`.

## Measurement (VM, 32 cores, VE_RUN_CACHE=off, scratch worktree, lean-prep.sh restored builds)

Each `lake env lean` ran under `/usr/bin/time -f '%e %M'`, which gives wall seconds and peak RSS (the same
max-RSS field as `-v`). The load is the 1-minute load average at the start of each run.

| run | tree | mode | total s | Statements s | Tree s | Statements peak RSS (sum) | load before |
|---|---|---|---|---|---|---|---|
| main-serial-1 | ab010c3f | serial | 348.2 | 252.6 | 49.3 | 1.68 GB | 22.3 |
| main-serial-2 | ab010c3f | serial | 288.6 | 214.9 | 38.4 | 1.67 GB | 50.9 |
| main-serial-3 | ab010c3f | serial | 348.1 | 244.1 | 44.0 | 1.68 GB | 39.1 |
| main-split8-1 | ab010c3f | 8 parts | 125.8 | 22.4 | 46.2 | 13.08 GB | 69.9 |
| main-split8-2 | ab010c3f | 8 parts | 77.4 | 14.1 | 32.5 | 13.08 GB | 38.9 |
| main-split8-3 | ab010c3f | 8 parts | 89.0 | 16.0 | 32.3 | 13.11 GB | 28.6 |
| parent-serial | a274d948 | serial | 317.1 | 241.2 | 26.9 | 1.68 GB | 24.5 |
| parent-split8 | a274d948 | 8 parts | 71.0 | 11.8 | 29.6 | 13.05 GB | 28.6 |
| ap3b-serial | a557ff88 | serial | 203.0 | 152.4 | 22.4 | 1.68 GB | 24.3 |
| ap3b-split8 | a557ff88 | 8 parts | 62.2 | 10.0 | 26.0 | 13.08 GB | 20.2 |
| main-audit | ab010c3f | `lean/audit.py --check`, 19 parts at once | 284.6 | — | — | 24.56 GB | 52.3 |

Each dump also ran 86 Alone runs (8 at a time). Their times are in `runs/*.json`.

| stop-rule row | bar | measured | result |
|---|---|---|---|
| S1 time | median cold dump ≥ 60 s faster at comparable load | 348.1 → 89.0 s (−259.1 s); median load at start: serial 39.1, split 38.9 | pass |
| S2 memory | the parts' peak RSS together ≤ lean/audit.py's parts | 13.11 GB ≤ 24.56 GB (each part 1.62-1.65 GB) | pass |
| S3 equality | every output byte-identical on 3 trees | main ab010c3f, a557ff88 (ap-3b merge), a274d948 (its first parent): serial = split = committed, sha256 in evidence.json | pass |
| S4 load | ≤ 12 cold dumps | 10 | pass |

The Statements run grows faster than its theorem count. One run over 6,625 theorems took 215-253 s, while each
of the 8 parts (~830 theorems, importing VE included) took 10-22 s. So the gain is about 14× on that step, not 8×.
The Tree run (one serial `import VE` predicate scan, 22-49 s) is now the largest Lean step of a cold dump. It
is the next lever, and this item does not touch it.

The scratch worktree was `/home/seyran/code/ve-eff-20261027-1-s-main`, detached. It was removed after the runs,
and so were the temporary output directories.

## What was built

| directive | commit | test |
|---|---|---|
| Statements run split into parallel parts. One place decides the count (`STATEMENT_PARTS = 8`, `statement_count()` = min(8, cores), with the reason in the comment). `statement_parts` makes contiguous near-equal parts and `print_statements` joins them in part order. One part is the old single run (`Statements` over `names.txt`). Every check of `dump_all` is unchanged. | 9d641bdc3 | `tests/test_lean_statements_parts.py` (5 tests) |
| A failed part fails the dump with its label and stderr (`run_lean`'s SystemExit, re-raised by `pool.map`). There is no partial output and no fallback. | 9d641bdc3 | `test_a_failed_part_fails_the_dump_with_its_label_and_output` |
| Dump cache keys and behaviour unchanged. The key includes `tools/lean_statements.py` and the modules it imports (`cache_store.py`), so the changed tool misses once. | 9d641bdc3 | `tests/test_lean_dump_cache.py` (selected, passed) |
| `RegenLog`: one JSON line per entry run (`t, mode, phase, entry, seconds, rc, head, worktree`) into `<git common dir>/ve-regen-log.jsonl`, through the one lookup `cache_store.git_common_directory`, which `cache_store.directory` now uses too. `VE_REGEN_LOG=off` turns it off and a path puts it elsewhere. A write failure is swallowed. Only the docstring describes it and no check reads it. | 9d641bdc3 | the 3 `test_*regen_log*` tests in `tests/test_regen_generated.py` |
| docs/TESTING.md paragraph, pointing to the docstring | 6133219a3, dc5bd7ab0 | — |
| `tests/history-dependent.json` regenerated with its own generator (the helper's name is in its `via`) | e5e89e234 | `tests/test_history_tests.py` |

Extra keys and choices beyond the directive:
- `phase` is `write`, `check` or `bootstrap`. `--resolve` runs both writers and checks. The `_Service` bootstrap
  (`lake build` and pins before a service user) is often where the build time of a `--write` after a Lean edit
  goes.
- `VE_REGEN_LOG=<path>` mirrors `VE_RUN_CACHE`, so tests can use `tmp_path`.
- The suite's only caller of regen's runs, `tests/test_regen_generated.py`, turns the log off with an autouse
  fixture. A first version did this in `tests/conftest.py`, which made test selection run all 467 units
  (BUILDER-CHECKLIST 9). Moving it brought selection down to 34 units.

## Orchestrator lines

- The regen log is at `$(git rev-parse --path-format=absolute --git-common-dir)/ve-regen-log.jsonl`. On the VM that
  is `/home/seyran/code/verifiable-english/.git/ve-regen-log.jsonl`, shared by every `ve-*` worktree. Each line
  has `{t (UTC ISO), mode (check|write|resolve), phase (write|check|bootstrap), entry, seconds, rc, head, worktree}`.
  Its first real line was written by this item's `--write --only history-tests` at 2026-10-27T17:08:45Z.
- Per-entry medians for the last 24 h:
  `jq -s 'map(select((.t|fromdateiso8601) > now-86400)) | group_by(.entry) | map({entry: .[0].entry, n: length, median_s: (map(.seconds)|sort|.[(length/2|floor)])}) | sort_by(-.median_s)' /home/seyran/code/verifiable-english/.git/ve-regen-log.jsonl`
- The same query split by phase, in Python:
  `python3 -c "import json,statistics as s,time,calendar,collections as c,sys; g=c.defaultdict(list); [g[(r['phase'],r['entry'])].append(r['seconds']) for r in map(json.loads,open(sys.argv[1])) if calendar.timegm(time.strptime(r['t'],'%Y-%m-%dT%H:%M:%SZ'))>time.time()-86400]; [print(p,e,len(v),s.median(v)) for (p,e),v in sorted(g.items(),key=lambda x:-s.median(x[1]))]" /home/seyran/code/verifiable-english/.git/ve-regen-log.jsonl`
- PIPELINE-LIMITS L111 can be marked as addressed by this item once it merges: the cold dump went from 348 s to
  89 s (median, VM). The merge train's branchregen (L105/L110) runs the same `lean-statements` entry, so it
  should drop by about 4 min per run on a Lean item. Use the log above to confirm that.

## Tests

- Selected tests (`mac-pytest.sh --select`, 34 units): the first run failed only
  `tests/test_history_tests.py`, on the stale generated `tests/history-dependent.json`. That file was regenerated
  in e5e89e234. After that, `tests/test_history_tests.py`, `tests/test_lean_statements_parts.py` and
  `tests/test_regen_generated.py` gave 88 passed. Every other selected unit had passed in the first run.
- The full gate was not run by me. The chain runs it on the final HEAD.
- Pre-existing failures on main (`main-known-red.txt`): none met in the selected units.

## Seeded bugs (Python only: the only product-adjacent language changed)

Each bug was planted, the named test failed (pytest exit 1, on an assertion), and the file was restored. They are
recorded in `docs/infra/eff-20261027-1/mutants.json` with `file` and `test` keys.

| id | file | bug | failing test |
|---|---|---|---|
| S1 | tools/lean_statements.py | a part boundary drops the last name of a part | test_parts_are_contiguous_and_cover_every_name_once_in_order |
| S2 | tools/lean_statements.py | a part boundary repeats the last name of a part | test_parts_are_contiguous_and_cover_every_name_once_in_order |
| S3 | tools/lean_statements.py | parts joined in the order they finish (`as_completed`) | test_parts_run_the_same_script_and_are_joined_in_part_order |
| S4 | tools/lean_statements.py | a failed part ignored (its output left out) | test_a_failed_part_fails_the_dump_with_its_label_and_output |
| S5 | tools/lean_statements.py | one part labelled `Statements0`, not the run of before | test_one_part_is_the_single_run_of_before |
| R1 | tools/regen_generated.py | log written even when VE_REGEN_LOG=off | test_the_regen_log_is_not_written_when_off |
| R2 | tools/regen_generated.py | an unwritable log raises | test_an_unwritable_regen_log_changes_neither_the_exit_code_nor_the_output |
| R3 | tools/regen_generated.py | the check phase not logged | test_the_regen_log_gets_one_line_per_entry_run_in_the_git_common_directory |

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. No Lean answer is read or relayed; this is tooling over `lake env lean` text.
2. Every deliverable built: PASS. See the directive table above (commits and tests). The diff has no copy of a Lean decision and no permanent report test (the evidence is checked by `check.py`, D4).
3. Tests can fail: PASS. Seeded bugs S1-S5 and R1-R3 are in `mutants.json`. `check.py` fails on a tampered row and on a missing run (tried on a copy).
4. Py/Lean/Rust agree: PASS for what applies. The serial and split outputs are byte-identical on 3 trees (evidence.json `output_sha256`, `check.py` rows E1-E3). No Rust or Lean is involved.
5. R8 binding: N.A. No relayed answer.
6. Gate evidence matches the final HEAD: PASS by process. The chain runs the gate on the final HEAD. The evidence here is saved measurements at fixed commits, with no live diff.
7. No unsigned item: PASS. There are no DELTA rows and trust is +0.
8. Every user-visible change in DELTA: N.A. There is no user-visible change. The three dump outputs are byte-identical (S3), and the log is a new file outside the tree.
9. Selection finds the tests: PASS. 34/467 units, which include `tests/test_lean_statements_parts.py`, `tests/test_regen_generated.py`, `tests/test_lean_dump_cache.py`, `tests/test_history_tests.py` and `tests/test_run_cache.py`. The `tests/history-dependent.json` drift was caught by the selection. The FULL selection caused by a conftest edit was fixed.
10. Lean statements and proofs: N.A. No Lean change.
11. Budgets, limits and deadlines: PASS. There are no sleeps or literal timeouts. The ordering test waits with `HANG_TIMEOUT` (`test_parts_run_the_same_script_and_are_joined_in_part_order`), and selection included `tests/test_hang_guards.py`.
12. No CPU or memory regression: PASS. The cold dump is 259 s faster (median). Peak memory grows from 1.7 GB to 13.1 GB, which is within lean/audit.py's own 24.6 GB on the same tree (row S2). There is no Rust or Lean code path change.
13. Test-removed trailers: N.A. No test was removed or renamed.
