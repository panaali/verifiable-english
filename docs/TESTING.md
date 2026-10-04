# Running the complete test suite

From the repository root, with Lean's `lake` and Rust's `cargo` available:

```sh
PATH="$HOME/.elan/bin:$PATH" UV_CACHE_DIR=/tmp/ve-xdist-uv-cache uv run --frozen python -m pytest -n auto
```

The default pytest options exclude tests marked `live`, so this command makes no model calls. For a serial comparison, run:

```sh
PATH="$HOME/.elan/bin:$PATH" UV_CACHE_DIR=/tmp/ve-xdist-uv-cache uv run --frozen python -m pytest
```

`-n auto` uses the available CPUs (16 on the current VM).

The session hook in `tests/conftest.py` builds Lean and Rust once per pytest invocation under a checkout-wide file lock in `rust/target/`. Every pytest process holds a shared lock while tests read the prepared binaries and Lean object files, so another invocation waits before rebuilding them. Builders inherit the exclusive lock, and timed-out builds stop their whole process group before the lock is released. Rust's release and debug targets share this lock; individual tests do not start further builds. Each test's `tmp_path` is unique across workers, including the Rust fuzz test inputs and summaries. Tests that change environment variables or module globals use pytest's `monkeypatch`, which is local to their worker process and restored after the test.

After a successful explicit `lake build` and both Rust release and debug builds, set `VE_NATIVE_PREBUILT=1` to take the shared read lock and run pytest against those binaries without rebuilding. Set `VE_LEAN_PREBUILT=1` as well to skip the service tests' redundant target builds. The ordinary command above still performs the native builds itself.

# Running only the tests a change affects

For a fix loop, run the tests the working-tree change can affect, with the
builds and checks they need:

```sh
python3 tools/select_tests.py --run
```

`--base origin/main` selects for a branch, `--commit REV` for one commit and
`--paths P...` for named files; without `--run` it prints the plan, and
`--explain` gives the reason for each selected test. `--run` runs each
selected test file in its own pytest process (`--jobs`, default 8) with the
coverage recorder on, prints the log tail of each failure, and saves the
recorded coverage for this exact working tree, so the next selection after
you commit starts from a fresh map. `--no-record` runs one plain pytest
process instead. Before a green tag and nightly, run the complete suite as
above; a selection is not a gate.

## How tests are chosen

The selector works at the level of functions, not layers:

* **Python.** `tools/change_units.py` parses the old and new file with `ast`
  into functions (named by their CPython `__qualname__`) and import-time
  statements. Comments and docstrings belong to neither, so a comment-only
  edit selects nothing but the tests that read the file as text. A function's
  digest is its whole `ast` node less docstring and decorators, so its kind
  (`def` or `async def`), signature and type parameters count; defs under any
  compound statement (`match`, `try`/`except*`, loops) are functions too. A
  changed function selects the tests that executed it. A changed import-time
  statement selects the functions, in this module and in modules that import
  the name, that read a name it binds (following derived values such as
  `DERIVED = LIMIT * 2`). A top-level call or a registering decorator selects
  every test that imported the module. A new function that nothing in the
  change calls by name might be dispatched dynamically, so it selects every
  test that ran a function of its file. A module that is added or deleted
  counts as an import-time change: every test that imported it.
* **Deleted and changed files in the static graph.** The graph is built from
  the tree after the change, plus each changed file as it was before: a
  deleted module keeps its importers, a deleted fixture the tests that named
  it, and an import the change removed still counts.
* **Lean.** The executables whose root imports the module (from the Lean
  import graph), then the tests that ran those executables; plus `lake build`,
  `lean/audit.py` and the Lean import check.
* **Rust.** The tests that ran a Rust binary, `cargo test`, and the release
  and debug builds.
* **Data and documents.** The tests that read the file, and for an added or
  removed file the tests that listed its directory. A fixture that a Rust test
  embeds with `include_bytes!` also runs `cargo test`. Documentation selects
  only its readers.
* **Everything.** `tests/conftest.py`, `pyproject.toml`, `uv.lock`,
  `.gitignore` and files outside the known top-level directories select the
  complete suite.
* **Smoke.** Any change beyond documentation also runs three fast files
  (`SMOKE` in `tools/select_tests.py`).

The layer checks run only when their inputs change: the Python import check
when a `ve/` module's imports change, the Lean import check for `.lean`
files, the Rust dependency check for Rust sources, and
`tools/test_layer_policy.py` when the selector's own code changes.

## The coverage map

`python3 tools/test_map.py record` runs every test file in its own process
with `tools/test_map_recorder.py` loaded into each Python process of the
project environment (through a `.pth` hook that exists only while recording;
children started with an explicit `env=` inherit it). It records, per test
file, the functions under the repository that ran (`sys.monitoring`), the
files read and directories listed by test code (an audit hook; the import
system's, pytest's, tracebacks' and warnings' source reads are excluded), and
the programs started. Who a read or listing is for is decided by the
innermost frame that is either code under the repository (the test and the
project: recorded) or infrastructure (import system, site, pytest: not
recorded); the standard library and third-party packages in between act for
their caller, and pytest frames further out do not matter. Maps of an
earlier recorder version are not used. The map for commit C goes to
`~/.cache/ve-testmap/C.json.gz` (`$VE_TESTMAP_CACHE`); the selector uses the
recorded map nearest below the base, or one saved by `--run` for exactly the
base's tree. The full recording takes about an hour with 7 parallel files on
the loaded VM.

* Nightly: `python3 tools/test_map.py record` on main.
* After each merge to main: `python3 tools/test_map.py update` re-records only
  the test files whose coverage may have changed since the nearest map and
  carries the others over (`--dry-run` lists them).

**Drift.** Between the map's commit and the base, other changes may have
altered which code a test reaches. A test that ran none of the code changed
since the map (no changed function, no module whose import-time statements
changed, no changed file it read or listed, no rebuilt program it started)
runs exactly as recorded, so its map entry holds. Every other test is
*uncertain* and is selected by the static graph (`tools/source_graph.py`:
import closure, string-literal mentions of files, directories and programs)
instead. Test files that failed or were opaque when recorded (a Python child
the recorder could not follow) are treated the same way, and without a map
the static graph is the whole answer (`--static` forces it).

Selection takes about 1 s with warm caches (parsed sources are cached per
file under `~/.cache/ve-testselect`); the first run after a new map or a
change to the selector parses more and took up to 11 s on the loaded VM.

## Evidence

`python3 tools/select_tests_evidence.py replay --head f4142cb9` replays the 50
newest non-merge commits before main's `f4142cb9` (2026-10-04): the layer
selector as it was there ("before"), this selector with the nearest
nightly-style map recorded at an ancestor of the commit's parent (`d9f8c4aa`
or `7903d5fa`, recorded at the main heads of about 19:44 and 02:34 UTC on
2026-10-02), and the same map taken as if recorded at the parent ("fresh",
which `update` after each merge plus `--run` keep close to; an estimate,
since it skips the drift check). Counts are test units (pytest files plus
`tools/test_layer_policy.py`) in the tree of the time.

`python3 tools/select_tests_evidence.py mutants --at f4142cb9` seeds one bug
(a swapped comparison or boolean operator, a negated `if`, an off-by-one
constant or `return None`, chosen by a seeded random generator) in a function
that each of the first 10 replayed commits with a Python function change
touched, at `f4142cb9` with the map recorded there, selects, and runs the
selected files until the first failure. A failure counts only if the same
test passes without the bug; a test failing either way is deselected and the
run repeated. A seed the selection does not catch is run against every other
test file: a failure there would be an escape (none occurred); seeds that no
test in the suite detects are listed, and the next seed is used.

The tables below are generated from `docs/testselect-evidence.json` by
`python3 tools/select_tests_evidence.py table`; `tests/test_select_tests.py`
checks that they match.

<!-- testselect-evidence:start -->
| Commit | Changed files | Before | After (nightly map) | After (fresh map) | Map | Uncertain | Seconds |
|---|---|---:|---:|---:|---|---:|---:|
| `4188ee60` | `ve/environment.py` | 208/208 | 196/210 | 175/210 | `d9f8c4aa` | 210 | 10.77 |
| `9c6d1658` | `tests/test_environment_field_types.py`, `tools/gate-collection.json` | 208/208 | 7/210 | 4/210 | `d9f8c4aa` | 210 | 2.33 |
| `f43864c0` | `ve/environment.py`, `ve/profiles.py`, `ve/speech_acts.py` | 208/208 | 197/210 | 175/210 | `d9f8c4aa` | 210 | 1.43 |
| `19061bfa` | `ve/environment.py` | 208/208 | 196/210 | 175/210 | `d9f8c4aa` | 210 | 1.15 |
| `e98b23a1` | `tests/test_environment_field_types.py`, `tools/gate-collection.json` | 208/208 | 7/210 | 4/210 | `d9f8c4aa` | 210 | 0.66 |
| `448b0e80` | `ve/definitions.py` | 208/208 | 194/210 | 34/210 | `d9f8c4aa` | 210 | 1.21 |
| `a4235ab3` | `ve/environment.py` | 208/208 | 196/210 | 175/210 | `d9f8c4aa` | 210 | 1.1 |
| `cd085076` | `ve/rights.py` | 208/208 | 194/210 | 18/210 | `d9f8c4aa` | 210 | 1.37 |
| `608a087d` | `docs/ARCHITECTURE-LAYERS-PLAN2.md` | 94/208 | 0/210 | 0/210 | `d9f8c4aa` | 210 | 1.17 |
| `73e3c453` | `tests/test_environment_field_types.py`, `tools/gate-collection.json`, `ve/environment.py` | 208/208 | 196/210 | 175/210 | `d9f8c4aa` | 210 | 1.15 |
| `f8176839` | `tests/test_environment_field_types.py`, `tools/gate-collection.json` | 208/208 | 7/210 | 4/210 | `d9f8c4aa` | 210 | 1.13 |
| `e9669e13` | `ve/admission.py`, `ve/discourse.py`, `ve/document.py` ... | 208/208 | 195/210 | 43/210 | `d9f8c4aa` | 210 | 1.02 |
| `6d9f7012` | `ve/backends/validation.py`, `ve/bundle.py`, `ve/environment.py` | 208/208 | 196/210 | 175/210 | `d9f8c4aa` | 210 | 0.78 |
| `1f31f7b5` | `tools/check_rust_deps.py`, `tools/test_layer_policy.py` | 208/208 | 12/210 | 6/210 | `d9f8c4aa` | 210 | 0.55 |
| `95c5e308` | `docs/ARCHITECTURE-LAYERS-PLAN2.md` | 94/208 | 0/210 | 0/210 | `d9f8c4aa` | 210 | 0.84 |
| `5114d0c6` | `docs/ARCHITECTURE-LAYERS.md`, `tools/check_rust_deps.py`, `tools/test_layer_policy.py` | 208/208 | 12/210 | 6/210 | `d9f8c4aa` | 210 | 0.43 |
| `d7978bd3` | `tools/check_rust_deps.py`, `tools/test_layer_policy.py` | 208/208 | 12/210 | 6/210 | `d9f8c4aa` | 210 | 0.45 |
| `28fc0fdd` | `docs/ARCHITECTURE-LAYERS.md`, `tools/check_rust_deps.py`, `tools/test_layer_policy.py` | 208/208 | 12/210 | 6/210 | `d9f8c4aa` | 210 | 0.47 |
| `15fab794` | `tests/test_surface_registry.py`, `tools/gate-collection.json`, `ve/ast.py` | 208/208 | 196/210 | 156/210 | `d9f8c4aa` | 210 | 1.29 |
| `c44ea4a9` | `tools/rust_output_diff.py`, `tools/test_layer_policy.py` | 208/208 | 12/210 | 6/210 | `d9f8c4aa` | 210 | 1.01 |
| `eb18c74e` | `docs/ARCHITECTURE-LAYERS.md`, `tools/check_rust_deps.py`, `tools/test_layer_policy.py` | 208/208 | 12/210 | 6/210 | `d9f8c4aa` | 210 | 0.76 |
| `cd6753a9` | `docs/spec/wire-contract-s4.md` | 94/208 | 3/210 | 2/210 | `7903d5fa` | 210 | 0.74 |
| `b04888fd` | `.importlinter`, `docs/ARCHITECTURE-LAYERS.md`, `tests/test_precommit_hook.py` ... | 208/208 | 210/210 | 210/210 | `d9f8c4aa` | 210 | 1.41 |
| `c81c0708` | `conformance/wire-contract/s4-integration.md` | 208/208 | 65/210 | 10/210 | `7903d5fa` | 210 | 0.89 |
| `c9563d2c` | `.importlinter`, `docs/ARCHITECTURE-LAYERS.md`, `tests/test_surface_registry.py` ... | 208/208 | 210/210 | 210/210 | `d9f8c4aa` | 11 | 1.43 |
| `962a4458` | `tools/gate-collection.json` | 208/208 | 6/210 | 3/210 | `7903d5fa` | 210 | 0.85 |
| `9d42b8ef` | `conformance/wire-contract/soft-norms@0-switch.json`, `docs/spec/soft-norms.md`, `docs/spec/wire-contract-s4.md` ... | 208/208 | 67/210 | 13/210 | `7903d5fa` | 210 | 0.71 |
| `64aee577` | `tests/test_wire_contract_faults.py` | 182/208 | 6/210 | 6/210 | `7903d5fa` | 210 | 3.1 |
| `12481cac` | `conformance/soft_norms.py`, `conformance/wire-contract/soft-norms@0-delta.json`, `conformance/wire-contract/soft-norms@0-gate.json` ... | 208/208 | 71/210 | 19/210 | `7903d5fa` | 210 | 1.7 |
| `c9015aba` | `docs/ARCHITECTURE-LAYERS.md`, `tools/check_rust_deps.py`, `tools/hooks/README.md` ... | 208/208 | 9/210 | 9/210 | `d9f8c4aa` | 4 | 0.9 |
| `2c0306c2` | `docs/ARCHITECTURE-LAYERS-PLAN2.md` | 94/208 | 0/210 | 0/210 | `d9f8c4aa` | 4 | 1.01 |
| `d335a82a` | `conformance/wire-contract/s4-pre.md`, `tests/test_softnorms_contract.py`, `tests/test_wire_contract_soft_lean.py` ... | 208/208 | 196/210 | 35/210 | `7903d5fa` | 210 | 1.59 |
| `d14c4f8f` | `conformance/wire-contract/s4-integration.md` | 208/208 | 65/210 | 10/210 | `7903d5fa` | 210 | 0.87 |
| `daa62a99` | `tools/gate-collection.json` | 208/208 | 6/210 | 3/210 | `7903d5fa` | 210 | 0.72 |
| `61d3eae6` | `tests/test_softnorms_public_contract.py`, `tests/test_wire_contract_three_way.py` | 182/208 | 7/210 | 7/210 | `7903d5fa` | 210 | 1.29 |
| `2f1ca809` | `docs/spec/composition-s1.md` | 94/208 | 1/210 | 0/210 | `7903d5fa` | 210 | 0.96 |
| `b00889ad` | `tests/test_readings_s1_differential.py` | 182/208 | 4/210 | 4/210 | `7903d5fa` | 210 | 0.95 |
| `452f3d72` | `tests/test_readings_s1_lean.py`, `ve/readings_route.py`, `ve/readings_s1.py` | 208/208 | 194/210 | 23/210 | `7903d5fa` | 210 | 1.14 |
| `1ded19ab` | `tests/test_rights.py`, `tests/test_rights_lean.py`, `ve/rights.py` | 208/208 | 194/210 | 31/210 | `7903d5fa` | 210 | 0.97 |
| `f3566dc6` | `conformance/wire-contract/soft-norms@0-delta.json`, `conformance/wire-contract/soft-norms@0-gate.json`, `conformance/wire-contract/soft-norms@0-golden.json` ... | 208/208 | 208/210 | 208/210 | `7903d5fa` | 210 | 1.21 |
| `2818fcd5` | `docs/spec/composition-s1.md` | 94/208 | 1/210 | 0/210 | `7903d5fa` | 210 | 0.79 |
| `0a8e67f2` | `tests/test_readings_s1_differential.py` | 182/208 | 4/210 | 4/210 | `7903d5fa` | 210 | 0.73 |
| `cda2975a` | `tests/test_readings_s1_lean.py`, `ve/readings_s1.py` | 208/208 | 194/210 | 23/210 | `7903d5fa` | 210 | 0.72 |
| `bf52c8db` | `docs/spec/composition-s1.md` | 94/208 | 1/210 | 0/210 | `7903d5fa` | 210 | 1.3 |
| `dd2a1ee3` | `tests/test_readings_s1_differential.py` | 182/208 | 4/210 | 4/210 | `7903d5fa` | 210 | 1.79 |
| `6aae2cd1` | `tests/test_readings_s1_lean.py`, `tests/test_readings_s1_python.py`, `ve/readings_s1.py` | 208/208 | 194/210 | 24/210 | `7903d5fa` | 210 | 2.12 |
| `1509d4ee` | `conformance/wire-contract/s4-pre.md`, `ve/softnorms.py` | 208/208 | 196/210 | 35/210 | `7903d5fa` | 210 | 1.23 |
| `c45a5ccd` | `ve/readings_s1.py` | 208/208 | 194/210 | 23/210 | `7903d5fa` | 210 | 1.05 |
| `207a0653` | `docs/spec/composition-s1.md` | 94/208 | 1/210 | 0/210 | `7903d5fa` | 210 | 0.75 |
| `492f1710` | `docs/spec/composition-s1-measured.md`, `docs/spec/composition-s1.md`, `tools/readings_s1_pilot.py` ... | 208/208 | 194/210 | 39/210 | `7903d5fa` | 210 | 1.56 |

Totals over 50 commits ending at `f4142cb9d4`: before 9358, after (nightly map) 4554, after (fresh map) 2304 test-file runs; `lean/audit.py` before 50 times, after 1 times; selection time before 51.6 s at most, after 10.77 s at most.

| Commit | Function | Mutation | Selected | First failing test | Caught | Earlier seeds no test detects |
|---|---|---|---:|---|---|---|
| `4188ee60` | `ve/environment.py:Environment._decode` | swap Is | 174/209 | `tests/test_readings_s1_differential.py` | yes | Environment._decode: constant 2 -> 3 |
| `f43864c0` | `ve/environment.py:Environment._decode` | swap And | 174/209 | `tests/test_assist_recovery_replay.py` | yes | - |
| `19061bfa` | `ve/environment.py:Environment._decode` | negate if | 174/209 | `tests/test_assist_recovery_replay.py` | yes | - |
| `448b0e80` | `ve/definitions.py:_mentions` | return None | 31/209 | `tests/test_bluedot_grant.py::test_would_keeps_its_conditional_force` | yes | - |
| `a4235ab3` | `ve/environment.py:Environment._decode` | negate if | 174/209 | `tests/test_order.py` | yes | - |
| `cd085076` | `ve/rights.py:_duplicate` | negate if | 16/209 | `tests/test_compose_integration.py::test_gamma_document_admission_and_end_to_end` | yes | - |
| `73e3c453` | `ve/environment.py:Environment._decode` | swap In | 174/209 | `tests/test_assist_recovery_replay.py` | yes | - |
| `6d9f7012` | `ve/backends/validation.py:environment_in_scope` | negate if | 12/209 | `tests/test_stage2_validation.py::test_statement_layers_and_rust_keep_the_python_decoder` | yes | - |
| `e9669e13` | `ve/admission.py:_admit_document_python` | negate if | 27/209 | `tests/test_p0_three_way.py::test_data_background_deduction_admission_matches_lean` | yes | admit_document: return None |
| `1f31f7b5` | `tools/check_rust_deps.py:parse_module` | negate if | 4/209 | `tools/test_layer_policy.py` | yes | - |
<!-- testselect-evidence:end -->

What the numbers say, and what was not run:

* Documentation-only commits go from 94 test files to at most 3, test-only
  and tool commits from 182-208 to 4-12, and `lean/audit.py` (about 420 s)
  runs only when Lean sources change (1 of 50 commits, against all 50 before).
* With the nightly map, most Python changes still select about 195 files.
  `ve/assurance-manifest.json` (read at import by 205 test files) and
  `Environment._decode` (run by 170) changed between the map and those
  commits, so nearly every test was uncertain. With a map fresh at the parent
  the same commits select 18-45 files, except changes to `Environment._decode`
  (174) and to import-time code such as `registry.register` (every file),
  which really do reach almost every test. Keeping the map fresh with
  `update` after merges and `--run` on branches is what turns the first column
  into the second.
* The fresh-map figure is an estimate. In an earlier run of the seeded-bug
  check against commits whose own changes postdated the map, a bug in
  `ve/rights.py:_duplicate` was caught by tests outside the fresh estimate.
  Commit `cd085076` itself had added those callers after the map was
  recorded. The drift rule exists for exactly this case, and the real
  selection included them. The mutants above therefore run at `f4142cb9`,
  with a map recorded at that very commit.
* The seeded-bug runs check the selected files plus, for undetected seeds,
  all other test files; the full suite was not run for every caught mutant,
  so a further failure outside the selection after the first caught one
  was not looked for.
