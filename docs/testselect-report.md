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

## Review fixes (testselect-review.final, round on `589229ed`)

Each finding was treated as a class; each reviewed failure is a regression
test in `tests/test_select_tests.py`, and each fix has a seeded mutant in
`SAFETY_CASES` that must fail a check.

- B, recorder dropped test reads and listings (any pytest frame on the stack
  made an open or listing "infrastructure", and every test runs under
  pytest). `test_map_recorder.origin` now decides by the innermost frame
  that is code under the root (recorded) or infrastructure (import system,
  site, pytest: not recorded); the standard library and third-party code act
  for their caller. Map `VERSION` is 3, so the version-2 maps (which lack
  these edges) are no longer used. Tests:
  `test_a_test_run_by_pytest_keeps_its_own_reads_and_listings` (a real
  pytest run under the recorder; it fails with the reviewed recorder) and
  `test_reads_and_listings_belong_to_the_innermost_owner`.
- B, `async def` digested as `def`. A unit's digest is now its own `ast`
  node less docstring and decorators, so the def's kind and any field
  (including future ones) count; the import-time residue keeps the kind;
  nested blocks are found from the `ast` schema, so defs under `match` and
  `try`/`except*` are units; `except ... as e` and match captures bind.
  Tests: `test_making_a_repository_method_async_changes_it`,
  `test_every_field_of_a_def_or_class_is_part_of_its_digest`,
  `test_defs_in_every_compound_statement_are_units` and
  `test_every_identifier_field_of_the_ast_is_classified` (the last three
  enumerate from the `ast` schema and fail on a field or statement kind
  that is not classified).
- B, deleted modules lost their dependents. `Graph.overlay` keeps each
  changed file's earlier version in the static graph (removed files with
  their old imports and mentions; old edges of changed files), used by
  `select` and by the drift check. A module that appears or vanishes is an
  import-time change for mapped tests. Drift results are cached under a key
  that includes the selector's own code. Tests:
  `test_a_deleted_file_keeps_the_tests_that_used_it`,
  `test_without_a_map_deleting_a_module_selects_its_importers` (deleting
  `ve/authoring.py`) and
  `test_with_a_map_deleting_a_module_selects_every_test_that_imported_it`.

Checks on HEAD after these fixes: `lake build` OK; `lean/audit.py` PASS
(2959 declarations); full pytest suite with 14 workers on the loaded VM
(load about 27): 8695 passed, 6 skipped, 1 failed:
`test_precommit_hook.py::test_large_staged_change_stays_under_ten_seconds`
took 18 s against its 10 s wall-clock bound under that load, and passed
when rerun alone. The pre-commit hook shares no code with the selector.
`tests/test_select_tests.py`: 55 passed, including nine seeded mutants.

Not redone: the evidence numbers above (replay and seeded bugs) were
computed with the version-2 maps and the selector before these fixes. Those
maps are now rejected, so selection uses the static graph until
`python3 tools/test_map.py record` writes a version-3 map (nightly, deferred
to the orchestrator as above). Cold selection speed (finding C) is
unchanged; the overlay adds about 0.2 s when a change touches Python files.

## Review fixes (testselect-looprecheck1.final, round on `1f1e154f`)

Both B findings were cases of one class: the plan (`select`) and the drift
check (`uncertain_units`) each had their own per-kind rules, and an added or
removed file was handled differently by kind. Both now call one rule,
`kind_of` and `file_impact` in `tools/select_tests.py`.

- B, deleting a module that binds nothing (empty, only a docstring, `pass`)
  selected none of its importers, statically or with a map, and the drift
  check kept their map entries. An empty semantic delta no longer hides an
  added or deleted module, in the plan's static and mapped parts and in the
  drift check. In the same class: an added module, which the map cannot have
  seen imported, also selects every test whose static closure now imports
  it, and a path named without a visible edit may have appeared or vanished.
  Tests: `test_deleting_a_module_that_binds_nothing_selects_its_importers`
  (four contents, fresh map, static graph and drift check) and
  `test_a_new_module_selects_the_tests_that_now_import_it`.
- B, an added Python fixture ignored the tests that listed its directory
  (only data files used listers). Every kind (Python, Lean, Rust, data) now
  selects the listers of an added or removed file's directory. Test:
  `test_adding_a_python_fixture_selects_the_tests_that_listed_its_directory`
  (`.py`, `.json`, `.lean`, `.rs` added to `tests/fixtures`).
- Class check: `test_the_plan_and_the_drift_check_treat_presence_alike`
  runs every kind in `select_tests.KINDS` (the test fails if a kind has no
  example) × added/deleted × contents. It requires the readers, listers and,
  by kind, importers or program runners, and it requires the plan and the
  drift check to agree. As in the plan, a file that selects everything
  (`pyproject.toml`, unknown areas) changed since the map now makes every
  map entry uncertain.
- Two seeded mutants were added to `SAFETY_CASES`: "an empty delta hides an
  added or deleted module" and "directory listings count for data files only".

Checks on HEAD `dd669c45`: `lake build` OK; `lean/audit.py` PASS (2959
declarations); full pytest suite with 14 workers: 8738 passed, 6 skipped, 0
failed. `tests/test_select_tests.py`: 97 passed, including 11 seeded
mutants. In the run of only the tests this change affects (load about 40),
`test_precommit_hook.py::test_large_staged_change_stays_under_ten_seconds`
went over its wall-clock bound, as in the previous round. It passed alone
and in the full suite.

Not redone (follow-up): the evidence tables still come from the version-2
maps and the selector before both review rounds. `docs/TESTING.md` now says
so. Regenerating them needs a version-3 map recording (about an hour) and the
replay. That recording is the nightly job deferred to the orchestrator above.

## Known limits

- An assignment whose value calls something (`X = registry.add(f)`) counts
  as computing `X`, not as an import-time effect, so it selects the readers
  of `X` rather than every importer.

- Dynamic dispatch of a new function from unchanged code is covered only by
  the "new function not called by name" rule (every test of its file).
- Coverage of randomized tests can vary between runs: `record` unions the
  previous map's edges.
- A Python child started outside the project environment, or with `-S`,
  makes its test opaque, so the static graph answers for that test.
- Directory listings by a test's own code are recorded, but which files
  match its glob is not, so an added file selects every lister of its
  directory.
