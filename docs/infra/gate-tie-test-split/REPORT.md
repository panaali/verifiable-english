# gate-tie-test-split: the committed-tie mutation loop as 16 tests

Status: built; selected tests run on the committed final code (result below); the chain gate is still to run on the final HEAD.
What changed: `tests/test_consolidation_tools.py::test_mutated_committed_ties_are_reported_or_rejected` now runs as 16 parametrized chunks
plus a partition test. `tools/test-durations.json` and `tools/test-chunks.json` now record the chunks.
Longest piece on VM1, same host, run one after the other (MEASURED): 2,946.6 s for today's single test, 275.9 s for the longest chunk.
Open items: none. No DELTA rows, no DRI signature reserved, trust +0 (no Lean or trusted file changed).

SIZE: 0 product, 42 tests, 37 other hand-written lines (two measured-data JSON rows, 19 + 18 diff lines); plus this report and its evidence.

## Deliverables

| # | task line | delivered by | test / evidence |
|---|---|---|---|
| 1 | split the loop over `targets` into K about 16 independent tests, by a stable rule; the two whole-tree preliminary asserts run once per worker; each chunk asserts `assert_sound_or_rejected` for exactly its targets and variants | commit 45489d0579: `CHUNKS = 16`; chunk i holds the targets whose index in the sorted `targets` is i mod 16 (`committed_cases`); the preliminary asserts and the sub-tree are in the module-scoped fixture `committed_ties` | `test_mutated_committed_ties_are_reported_or_rejected[0..15]`: 16 passed (evidence/vm1-new.durations.txt). The fixture's setup runs once: only `[0]` has a setup line (6.50 s); the other 15 setups are under 0.005 s |
| 2 | partition test: the chunks together cover every (target, variant) pair exactly once, and no chunk is empty | `test_committed_tie_chunks_partition_every_mutation` | It builds the unsplit loop's pairs without the chunk rule and compares them, as a sorted list of JSON keys, with the 16 chunks' pairs put together. Seeded bugs S1–S3 below |
| 3 | measure per-chunk seconds on VM1 (`--durations`), longest chunk against today's single test on the same host | section "Measurement" | evidence/vm1-*.txt |
| 4 | update or remove the "never" row of tools/test-chunks.json if it no longer holds | commit 129ac3515d: the row is replaced by `chunk_table.py`'s row for a new whole-file serial run (never: false, max_chunks 4, best cut 75%) | evidence/chunk_table.md; `tests/test_test_chunks.py` 59 passed |

Nothing is skipped or weakened. Each chunk runs the same `assert_sound_or_rejected(decls, files, mutate(table, module, name, variant), proved, predicates, ...)` call as before, on the same sub-tree. The chunks use the same `entry_variants(..., tying[:1])`. The two `problems == [] and not unsound(...)` asserts and `len(targets) > len(tying)` moved unchanged into the fixture.

The chunks do the same total work as the single test: their call seconds sum to 2,991.6 s, against 2,946.6 s for the single test (+1.5%). A setup error in the fixture fails all 16 chunks and the partition test.

## Measurement (MEASURED, VM1 = multi-agent-lab, x86_64, 32 CPUs; `-n 0`, one process)

Script: evidence/vm1-measure.sh. Its output, with load averages and UTC times, is in evidence/vm1-measure.out. The two runs ran one after the other on the same host:

- **Chunks, at HEAD 45489d0579** (`pytest -n 0 -k test_mutated_committed_ties --durations=0`; evidence/vm1-new.durations.txt):
  - 16 passed, 2,998.36 s wall.
  - Per-chunk call seconds: [0] 275.91, [1] 257.03, [8] 181.47, [12] 179.04, [3] 178.67, [11] 177.77, [6] 176.86, [13] 176.73, [14] 176.66, [9] 176.06, [5] 174.45, [4] 174.30, [7] 172.92, [10] 172.78, [2] 171.89, [15] 169.03.
  - Fixture setup: 6.50 s, on [0] only.
  - Load average at start: 2.42.
- **Today's single test, main's file** (`git show main:tests/test_consolidation_tools.py`, copied to a temporary `tests/test_zz_main_consolidation_tmp.py` and deleted afterwards; evidence/vm1-old.durations.txt):
  - 1 passed: 2,946.64 s call, 5.67 s setup, 2,952.73 s wall.
  - Load average: 1.53 at the start, 3.77 at the end.
- **Result:** the longest chunk takes 275.9 s against 2,946.6 s for the single test, 9.4% of it, about 10.7× shorter.
- **Whole file, for row 4** (`mac-pytest.sh -- -n 0 -v -p no:cacheprovider --durations=0 --durations-min=0 tests/test_consolidation_tools.py`, as eff-20261030-1's measure.sh; evidence/vm1-whole-file.*):
  - The Mac test runner sent the run to the VM ("running on the VM instead (local)" in the log).
  - 304 passed in 3,773.12 s.
  - Its largest node is [5] at 307.5 s. For about 3 minutes of this run, seeded bug S4 ran one chunk ([5]) on the same host, so [5]'s figure may include that contention.
  - `chunk_table.py` gives k=4 at 957.6 s, a best cut of 75% (evidence/chunk_table.md).

## Data files changed (measured data, not generated; owners are named in their `source` fields)

- **tools/test-durations.json** (commit 5e5d1ebb19):
  - Change: the single test's entry (1,185.6 s) is replaced by 16 chunk entries. Each takes a share of the 1,185.6 s in proportion to its call seconds in the VM1 chunk run: 67.0–109.3 s each, summing to 1,185.6. The `source` field says so and marks these figures as an ESTIMATE until a gate measures the chunks.
  - Why: without these entries the scheduler (`tools/test_schedule.py`) would treat the 16 new ids as unrecorded tests of 0.06 s each, so one worker could take all 16 in one bulk run.
  - With them, the chunks are head tests (≥ 5 s), and `gate_shards` still weighs the file at its old total. `tests/test_test_schedule.py` + `tests/test_gate_durations.py`: 68 passed.
- **tools/test-chunks.json:** the 10-30 row said "one node is 290.0 of its 357.7 s … no split ends before it". After the split no single node holds most of the file, so the row no longer held. The row now comes from the whole-file run above, through `docs/infra/eff-20261030-1/chunk_table.py --data`.
  - Effect: in a selected run, `tools/select_tests.py` (`chunk_counts`) may now split this file into up to 4 processes when the coverage map records it above 500 s. Each process repeats the 19.0 s of file setup.
  - Row sel-consolidation-chunk was waiting on this one. It can now re-measure the file on Actions against the 2,300-s line.

## Test-removed

The old unparametrized ID is no longer collected. `tools/gate_collection.py --check --prebuilt` refused it until the trailer was added. The trailer is in the report commit:
`Test-removed: tests/test_consolidation_tools.py::test_mutated_committed_ties_are_reported_or_rejected — split into its 16 parametrized chunks [0]..[15] (same function, same assertions)`.

## Seeded bugs (each restored; `git status` clean after each)

| id | file | bug | failing test |
|---|---|---|---|
| S1 drop | tests/test_consolidation_tools.py (`committed_cases`) | `index % (CHUNKS + 1) == chunk`: targets with index ≡ 16 mod 17 are in no chunk | `test_committed_tie_chunks_partition_every_mutation` (list comparison fails, 1 failed) |
| S2 duplicate | same | `index % CHUNKS in (chunk, (chunk + 1) % CHUNKS)`: every target in two chunks | same (list comparison fails) |
| S3 empty chunk | same | `index % (CHUNKS - 1) == chunk`: every pair still covered, chunk 15 empty | same (`assert all(chunks)` fails) |
| S4 a chunk still checks the tool | tools/trust_map.py `classify_tree` (not changed by this item; the only product code the chunks test) | the anchor set took every named declaration (dropped `and is_anchor(*result)`) | `test_mutated_committed_ties_are_reported_or_rejected[5]`: "VE.Numbers.tenPow=None: passed while ['VE.Numbers.tieAt: VE.Numbers.tieAt_iff ties it to nothing the report counts as trusted']" (1 failed in 185.6 s) |

This item changes no product code in Lean, Python or Rust (tests and measured-data JSON only), so there is no per-language product mutant. S4 is in Python product code, to show that the split tests still fail on a soundness bug.

## Notes for the DRI

- **Gate scheduling** (`tools/test_schedule.py`, unchanged): it hands out the file of a long test in batches, and no batch runs longer than the longest recorded test in the run. That test is now `test_asimov_extended.py::test_rerun_sample_equals_the_committed_results` at 954.3 s. So in a full gate the 16 chunks go to about 2 workers rather than 16 (ESTIMATE from `head_batches`), and the floor of the run is about 954 s of the old 1,185.6-s scale. In a shard or selected run without that test, the cap is lower, so the chunks spread over more workers. Spreading them further means changing the scheduler, which is outside this test-structure item.
- **gate_shards** assigns whole files to shards (`tools/gate_shards.py plan`), so all 16 chunks stay in one shard. There, the shard's xdist workers spread them as above, and the shard plan's weight for the file is unchanged.
- The arm-leg and ve-cloud-2 after-figures are for the decider's re-measure from the logs once this merges (reviews/dri-decisions-20261113-train-legs.md). This report does not claim them.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer or relay touched.
2. PASS: the four deliverables are in the table above, each with its commit and test. `git diff main...HEAD` has no Python copy of a Lean decision and no new report test.
3. PASS: seeded bugs S1–S4 fail `test_committed_tie_chunks_partition_every_mutation` and `test_mutated_committed_ties_are_reported_or_rejected[5]`.
4. N.A.: no Python/Lean/Rust behaviour changed; the chunks pass on HEAD (16 passed, evidence/vm1-new.durations.txt).
5. N.A.: no binding.
6. PASS: the selected run happens on the committed final HEAD (below). The chain runs the gate.
7. PASS: no DELTA row, no trust growth (no Lean file changed: `git diff --stat main...HEAD`).
8. N.A.: no user-visible output changed (test structure and scheduling data only).
9. PASS: `tools/select_tests.py` selects tests/test_consolidation_tools.py for this change (final selected run below).
10. N.A.: no Lean statement.
11. N.A.: no budget or deadline code. The new tests have no sleep and no timeout.
12. PASS: total work is unchanged within 1.5% (2,991.6 s summed over the chunks vs 2,946.6 s, VM1); one fixture setup per worker.
13. PASS: Test-removed trailer for the old ID. `tools/gate_collection.py --check --prebuilt` was rerun after the commit (result below).
14. PASS: in both directions, the partition test passes on HEAD and fails on S1–S3. Every timing above cites its evidence file. Spec re-read: the task's DO (1)–(4) against prompts/task-gate-tie-test-split.txt.
15. PASS: overclaim words checked: "nothing is skipped" (the same call and inputs, diff of `tests/test_consolidation_tools.py`); "once per worker" (setup lines in evidence/vm1-new.durations.txt). Nothing deferred. The partition test's guard can fail (S1–S3).
