# eff-tests: test-suite efficiency fixes (2026-10-10)

Branch `infra/eff-tests`, based on main `c24aeab2`. It applies items 1, 2, 6 and 8 of
`manage-agents/reviews/test-and-redundancy-profile-2026-10.md`. No test lost a check: only speed and robustness change.
`tests/test_eff_tests_report.py` regenerates every number below from the saved evidence in `docs/eff-tests/evidence/`.

## What changed

1. **The difffuzz CI run is bounded by its work, not its CPU seconds.** `tools/difffuzz.py` counts its work where it is
   done: inputs evaluated, Python calls, and the requests and cases sent to each Lean or Rust runner, with a batch
   that is split after a failure counted again. `tests/test_difffuzz.py::test_ci_run` checks that every sampled input
   is evaluated exactly once and that no count is over `WORK_LIMIT`, about 1.25 times the measured run. The CPU seconds
   are recorded as a test property only. The time guard in `tests/test_hang_guards.py` now also flags a CPU cost that
   is read by its key and bounded, such as `report["cpu_seconds"] <= 300`. That form had slipped past it.
2. **`tools/gate.py --rerun-failed [RECORD]`.** Every gate now records its tree (`tree_sha`) and its `mode`. A rerun
   takes a gate record that failed only on tests, on the same tree, clean, and on the same toolchains. It runs the
   collection and the suite over only the failed tests' files, and it reuses that gate's Lean audit and native Rust
   tests. The record names the previous gate, the tests, the files, the reused stages and each test's outcome. Its
   status is `rerun-passed`, never `passed`, so the final evidence is still a full gate. Any other record runs the
   full gate and records why (`rerun_failed.refused`).
3. **`test_every_field_keeps_its_domain` is split into 8 shards** (`[0]` to `[7]`). Each shard elaborates every 8th
   Lean source of 20 consecutive probes. `test_the_shards_prove_every_probe_once` checks that the shards' sources are
   exactly the old test's: every probe once, by index and by (file, pointer, name), the same groups of 20, and the
   same numbers of positive and negative examples.
4. **The wire gate corpus's nested recording run is cached** (`tools/run_cache.py`). The key covers the 32 recorded
   files and the Python files their imports reach, the plugins and modules that run them, the Lean and Rust binaries,
   the Lean sources, `uv.lock`, the interpreter, the settings and the run's environment. It also covers what the
   audit hook `tests/read_recorder.py` saw the run read: files opened or imported, directories listed and programs
   started. A stored record is used only while every one of those is unchanged. `tests/test_run_cache.py` changes
   each kind of input in a scratch repository and checks that the run happens again.

## Suite wall time, same machine, before and after

Each row is one full run: `nice -n 19 uv run --frozen python -m pytest -n 16 -p no:cacheprovider -q` on the shared
32-CPU VM, with the 1-minute load average sampled each minute. "Cold" starts from an empty run cache. "Warm" finds
the record stored for its commit.

| run | commit | wall | load median (min-max) | sum of test times | passed | failed |
|---|---|---|---|---|---|---|
| before | c24aeab2 | 3,122 s (52.0 min) | 57.9 (21.8-97.4) | 29,637 s | 13,642 | 1 |
| after, cold cache | 23ba0930 | 2,710 s (45.2 min) | 50.6 (24.9-71.4) | 29,430 s | 13,697 | 1 |
| after, warm cache | d0dbd667 | 2,660 s (44.3 min) | 46.3 (29.8-103.5) | 26,091 s | 13,698 | 0 |

- The loads overlap but are not equal: the before run's median was higher. The rows support "faster", and the size
  of the change comes from the per-test lines below, not from the wall times alone.
- Before, `tests/test_difffuzz.py::test_ci_run` failed on its CPU limit, at load up to 97.4. This is the failure that
  sent seven loaded gates back. After, the test recorded 305.1 s (cold) and 326.7 s (warm) of CPU. The old 300 s limit
  would have failed both runs, and the work bound passed both.
- The cold run's one failure was `tests/test_nested_pytest.py::test_every_pytest_command_is_built_by_the_builder`. It
  read the gate's new tuple of stage names (`"pytest"`, `"pytest command"`) as a pytest command. d0dbd667 makes it a
  set, and the warm run passed it.
- `tests/test_wire_gate_corpus.py::test_gate_corpus_holds_every_test_input_of_every_unit` (its time includes the
  recording fixture) took 2,122.6 s before, 1,219.2 s cold and 377.7 s warm. On the warm run the fixture read the
  stored record (`evidence/run-cache.json`).
- `test_every_field_keeps_its_domain` took 498.6 s as one test. Its longest shard took 205.3 s cold and 395.2 s warm.
  The warm figure includes the module's Lean fixtures, which that worker built first.

## The difffuzz work bound

The run of `tools/difffuzz.py --ci` at load about 38 did this work. `WORK_LIMIT` is about 1.25 times each count.

| count | measured | limit |
|---|---|---|
| inputs | 26,676 | 33,000 |
| python_calls | 26,680 | 33,500 |
| runner_requests | 62 | 78 |
| runner_cases | 18,829 | 23,500 |
| service_requests | 33 | 42 |
| service_cases | 15,255 | 19,000 |

The 26,676 inputs are the 26,422 sampled mutants plus the 254 baseline entries. The same run took 225.1 CPU seconds.

## Other CPU-bounded tests (item 1's "any other test")

Six files bound a Lean request or a child process by CPU seconds (`completed_within`, `run_cpu_bounded`). A measuring
plugin divided each of those limits. At load about 20, every bound held at a quarter of its limit. At a fifth, only
`test_no_pending_candidates_document_is_built[more-sets]` (1 s) failed. The relay renderer's 2 s cap could not be
measured that way. The agent logs from 2026-10-05 to 2026-10-10 show no load failure of these tests: the failures
found there were regressions or a broken merge-train run. So they stay as runaway guards, which docs/TESTING.md
allows (`evidence/cpu-margins.json`). Only the difffuzz limit was a performance bound inside the suite.

## Seeded bugs: each test can fail

Each bug was planted alone, the named tests were run, and the file was restored (`evidence/seeded-bugs.json`).

| bug | planted in | what it breaks | failed |
|---|---|---|---|
| M1 | tools/run_cache.py | the Rust binary left out of the cache key | 2 tests |
| M2 | tools/run_cache.py | the observed reads never checked | 4 tests |
| M3 | tests/test_enum_domains.py | one probe dropped from the split | 1 test |
| M4 | tools/difffuzz.py | every runner batch sent twice | 1 test |
| M5 | tools/gate.py | a passing rerun recorded as `passed` | 3 tests |
| M6 | tools/gate.py | a rerun on another tree | 1 test |
| M7 | tests/test_hang_guards.py | a CPU cost read by its key not flagged | 2 tests |
| M8 | tests/test_difffuzz.py | the old `cpu_seconds <= 300` assertion added back | 1 test |

## Not done here

- The profile's items 3, 4 and 5 (fixer and builder prompts, the coverage-map refresh loop) are orchestration
  changes in `manage-agents`. They are not in this repository. The same goes for forbidding a full rerun on an
  unchanged commit in build-checklist line 22, which item 2 proposes.
- Item 7 (`audit.py` reading `lake build`'s replayed `#print axioms`) touches the audit trust boundary and needs
  human sign-off.
- The run cache does not see files that Python child processes read. Those children are started by 6 of the 32 files,
  for example `python -c` probes. Their imports are covered by the static import closure, but their data reads are
  not. The outer suite runs those tests itself, so a failure there is not hidden. `VE_RUN_CACHE=off` turns the cache
  off, for a nightly run for example.
- The full gate runs after this report's commit. Its record is committed after it.

## Commits

Saved in `evidence/commits.json` (`main..HEAD --no-merges` when this report was written):

- fc91a289 tests: bound the difffuzz CI run by counted work, not CPU seconds
- cecbe0bc tests: split the enum-domain proofs into 8 shards xdist runs at once
- 828e9f77 gate: --rerun-failed reruns only a failed gate's test files on the same tree
- 7728bf26 tests: cache wire_gate_corpus's nested recording run under a key of its inputs
- 6d5cab1b docs: the wire gate corpus run cache
- a12942f2 gate: pin the new and split test IDs
- 28c3ae73 tests: the run cache's default directory
- 23ba0930 docs: the suite-timing summarizer for the eff-tests report
- d0dbd667 gate: hold the rerunnable failure stages as a set of names
