# Test selection: fix report (infra/testselect, 2026-10-04)

Task (throughput P0): run the fewest tests a change needs, safely. Before
this branch, `tools/select_tests.py` selected "the changed layer and every
outer layer" plus four always-run conformance files, the layer checks and
`lean/audit.py`. Each call took 7-50 s.

## What changed

- `tools/select_tests.py` selects by function, file and program instead of by
  layer. `tools/change_units.py` splits old and new Python with `ast` into
  functions (CPython qualified names) and import-time statements.
  `tools/source_graph.py` is the cached static fallback graph.
  `docs/TESTING.md` has the rules.
- `tools/test_map.py` and `tools/test_map_recorder.py` produce the coverage
  map: per test file, the functions it ran (`sys.monitoring`), the files it
  read and directories it listed (audit hook, with import-system, pytest,
  traceback and warning reads excluded), and the programs it started. Python
  child processes are covered through a temporary `.pth` hook. `record`
  builds a full map, `update` re-records only the units drift made
  uncertain, and `select_tests.py --run` records what it runs and saves a map
  for that exact tree.
- Drift rule: a test that ran none of the code changed since the map keeps
  its map entry. Any other test, and any unit that failed or was opaque when
  recorded, gets the static graph.
- `ALWAYS` (four heavy conformance files) became `SMOKE` (three files of
  about 2 s each). `lean/audit.py` (about 420 s) and the layer checks run only
  when their inputs change.
- `tools/select_tests_evidence.py` produces `docs/testselect-evidence.json`
  and the tables in `docs/TESTING.md`.

## Results

All numbers come from `docs/testselect-evidence.json`. The test
`tests/test_select_tests.py::test_testing_doc_tables_are_generated_from_the_evidence`
checks that the tables match it.

- Over the 50 non-merge commits before main's `f4142cb9`, test-file runs went
  from 9358 before to 4554 with the nightly-style map and 2304 with a map
  fresh at the parent (estimate). Medians per commit: 208, 38.5 and 9.5.
  `lean/audit.py` ran 50 times before and once after.
- Documentation-only commits went from 94 files to 0-3, test and tool
  commits from 182-208 to 4-12. Python changes stay near 195 with the nightly
  map because `ve/assurance-manifest.json` and `Environment._decode` changed
  after it, and drop to 18-45 with a fresh map.
- Speed: median 1.0 s warm; the first selection after a new map or a
  selector change took up to 10.8 s on the loaded VM (load 40-95). Before:
  median 16.3 s, up to 51.6 s.
- Seeded bugs: 10 of 10 were caught by the selected tests at `f4142cb9` with
  its own map. Each failing test passed without the bug. There were no
  escapes. Two seeds that no test in the whole suite detects are listed in
  the table.

## Checks run on HEAD `36e1d27e` (clean worktree)

- `lake build`: OK.
- `lean/audit.py`: PASS (2959 declarations).
- pytest, full suite with 14 workers: 8678 passed, 6 skipped, 0 failed (25:43).
- `check_python_layers`, `check_lean_imports`, `check_rust_deps`,
  `tools/test_layer_policy.py`, `wire_contract.py --check`: all exit 0.
- `tests/test_select_tests.py`: 37 passed. It includes four seeded mutants of
  the selector, each of which must fail a check.

Not run: `tools/gate.py` itself, whose pytest stage is serial (about 6.5
CPU-hours). The orchestrator's merge-verify equivalent above was run instead.
`cargo test` was not run either, because no Rust changed.

## Acceptance items

- AGENT, done: function-level selection for Python, executables for Lean, a
  binary for Rust, readers for data (1); the coverage map with static fallback
  and the drift rule (2); docs-only and test-only rules (3); smoke set, with
  audit and checks only on their inputs (4); selection under 2 s warm (5);
  evidence and `docs/TESTING.md` (6).
- EXTERNAL, deferred (owner: orchestrator): schedule
  `python3 tools/test_map.py record` in the nightly job and
  `python3 tools/test_map.py update` after each merge to main (for example in
  `manage-agents/nightly-verify.sh` and `after-main-green.sh`). Without
  these, only the maps recorded on 2026-10-04 exist, at `f4142cb9`, `d9f8c4aa`
  and `7903d5fa` in `~/.cache/ve-testmap`. Precision for Python changes
  depends on map freshness (see the results above).

## Known limits

- Dynamic dispatch of a new function from unchanged code is covered only by
  the "new function not called by name" rule (every test of its file).
- Coverage of randomized tests can vary between runs: `record` unions the
  previous map's edges.
- A Python child started outside the project environment, or with `-S`,
  makes its test opaque, so the static graph answers for that test.
- Directory listings by a test's own code are recorded, but which files
  match its glob is not, so an added file selects every lister of its
  directory.
