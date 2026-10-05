# Testing

## The fast path: only the tests a change can affect

While you work, run the tests your change can affect, not the whole suite:

```sh
PATH="$HOME/.elan/bin:$PATH" UV_CACHE_DIR=/tmp/ve-xdist-uv-cache \
    uv run --frozen python tools/select_tests.py --impacted --run
```

This takes the changed files from the working tree (tracked changes and new files). Use `--base origin/main` for a branch, `--commit REV` for one commit, or `--paths FILE...` to name the files yourself. Leave out `--run` to see the plan, or add `--json` for the full selection. `--run` runs the checks, the native builds the selection needs, and pytest on the selected files, one after another and in the foreground.

A test file is selected when one of these changed:

- a Python file it imports, directly or transitively. This covers tests, their helpers, `conformance/`, `tools/`, `ve/` and `ve_experiments/`, and includes imports inside functions. A name taken from the `ve` facade counts as its defining module. Every `conftest.py` pytest loads for the test (from the repository root down to its directory) counts as imported, so a change to `tests/conftest.py` or to anything it imports selects every test below it.
- a Lean module, when the test's code names an executable that contains that module. Product code counts only when it starts that executable itself. Test code that names the service, the Lean authority, `.lake` or the Lean sources also counts. So a Lean change selects that executable's conformance tests.
- the Rust sources, when the test's code starts the Rust checker or selects an authority. So a Rust change selects the Rust conformance and three-way tests.
- a data file whose path, name or use-case directory appears in a string in the test's code, such as `usecases/asimov-laws/...` for `tests/test_asimov_laws.py`.

The cross-cutting tests in `ALWAYS` (`tools/select_tests.py`) always run. A change no test reaches selects the full suite: an unknown file, a deleted file or `ve/__init__.py`. A script that no test reaches selects only `ALWAYS`, and the tool reports it.

The fast path is precise for changes to tests, helpers, tools, data and use cases. It is coarse for core product modules: they import one another widely, so a change to, for example, `ve/ast.py` still selects most of the suite. The gate (`tools/gate.py`) always runs everything.

`tests/test_select_tests.py` checks that a change to at least one source path selects every test file. If it names a file that nothing reaches, make the test's sources visible. Import the module under test, or name its data path in a string. Failing that, add the file to `EXTRA_SOURCES` in `tools/select_tests.py`. Then check the selection:

```sh
uv run --frozen python tools/select_tests.py --impacted --paths path/to/source --json
```

Without `--impacted`, `tools/select_tests.py` selects by function from a recorded coverage map, with the static graph for whatever the map cannot answer (next section). The two modes are separate rules today: `--impacted` needs no map and runs one plain pytest process; the default is finer for product modules and records coverage as it runs. Both read every `conftest.py` above a test as part of what it imports.

## The complete suite

From the repository root, with Lean's `lake` and Rust's `cargo` available:

```sh
PATH="$HOME/.elan/bin:$PATH" UV_CACHE_DIR=/tmp/ve-xdist-uv-cache uv run --frozen python -m pytest -n auto
```

The default pytest options exclude tests marked `live`, so this command makes no model calls. Leave out `-n auto` for a serial run.

`-n auto` adapts to the machine's load (`tests/conftest.py`: `worker_count`). It uses the CPUs this process may run on, minus the 1-minute load average, capped at `VE_TEST_WORKERS` (default: every usable CPU), and never fewer than one. A busy machine therefore gets fewer workers, not an oversubscribed run: with 32 CPUs at load 31 it gets one. More parallelism is opt-in: `VE_TEST_MIN_WORKERS=N` (default 1, at most `VE_TEST_WORKERS`) is a floor, for a shared VM whose load never drops below its CPU count and which would otherwise run a suite of about 20,000 CPU seconds on one worker. No test's outcome depends on load either way (see below). Use `-n N` to fix the count.

The session hook in `tests/conftest.py` prepares Lean and Rust once per pytest invocation, under a checkout-wide file lock in `rust/target/`. Every pytest process holds a shared lock while tests read the binaries and Lean object files, so another invocation waits before rebuilding them. Builders inherit the exclusive lock, and a build that times out stops its whole process group before the lock is released. Rust's release and debug targets share this lock, and individual tests start no further builds. Each test's `tmp_path` is unique across workers. Tests that change environment variables or module globals use pytest's `monkeypatch`, which is local to their worker and restored after the test.

How the native builds are reused is set by `VE_NATIVE_PREBUILT`:

- unset (local runs): the binaries are reused when the stamp of the last build in this checkout (`rust/target/.ve-native-stamp.json`) still matches. The stamp covers the inputs (the content of every tracked or unignored file under `lean/` and `rust/`, build directories apart, and `rust-toolchain.toml`) and the outputs (size, modification time and inode of each executable). Otherwise the hook builds and writes a new stamp.
- `VE_NATIVE_PREBUILT=1`: use the binaries as they are. The gate sets this after building them itself.
- `VE_NATIVE_PREBUILT=0`: always build.

`VE_LEAN_PREBUILT=1` also skips the service tests' redundant target builds.

## Speed is not a correctness criterion

Under load, any elapsed-time bound can fail a correct program. A merge-train suite at load 50 failed on a 5-second default and on a fake service's 0.5-second retry. The rules:

- **Waits are hang guards.** Every wait on a child process is `HANG_TIMEOUT` (`tests/subprocesses.py`, 1800 s). The checker clients' settings (`VE_RUST_TIMEOUT`, `VE_LEAN_SERVICE_TIMEOUT`, `VE_LEAN_SERVICE_STARTUP_TIMEOUT`, `VE_LEAN_TIMEOUT`, `VE_CONFORMANCE_HANG_TIMEOUT`, `VE_PRECOMMIT_TIMEOUT`) are raised to it for every test and every process a test starts.
- **Deadlines are tested by injection.** A deadline test starts a fake that never answers and injects the deadline as already expired: `expired_waits` in `tests/subprocesses.py` covers `subprocess.run` and `Popen.communicate`, and `expire_service_waits` in `tests/test_lean_service.py` covers the Lean service client. It then asserts that the configured value was the one asked for. No test waits out a real deadline, and a recovery after an injected timeout waits `HANG_TIMEOUT`.
- **Guards.** `tests/test_hang_guards.py` fails on four things outside its reviewed allowlist `INJECTED`, where each entry is an injected-clock, instrumented, event-poll or reaping function: a wait shorter than `HANG_TIMEOUT`, a sleep, a short deadline setting, or an assertion on a clock, a duration or a CPU cost. Stale entries fail too. At run time, `tests/conftest.py` refuses a child started without a checker setting, and a real Lean or Rust checker started with a setting below `HANG_TIMEOUT`.
- **Work bounds.** Tests bound work with the backends' own budgets, or with a kernel CPU limit (`run_cpu_bounded`) that stops a runaway child and fails the test through its exit status.

## Benchmarks: what the code costs

Speed checks live in `tools/bench/test_perf.py`, which runs nightly and on demand, never in the suite. It measures CPU seconds, which load stretches far less than elapsed time, and compares them with `tools/bench/baselines.json`. A measurement fails when it exceeds its baseline × (1 + `tolerance`) + `slack_seconds`. The benchmarks cover the pre-commit hook on a large staged change, the soft validators refusing exponential unfoldings, and the CPU of each kernel-bounded Lean and Rust batch in the W6a limit tests. Run them after the native builds:

```sh
PATH="$HOME/.elan/bin:$PATH" UV_CACHE_DIR=/tmp/ve-xdist-uv-cache \
    uv run --frozen python -m pytest tools/bench/test_perf.py --bench-report /tmp/ve-bench.json
```

`--update-baselines` rewrites the baselines of the benchmarks that ran. Commit the change only after reviewing it: a baseline is a claim about the code's cost. `tests/test_bench_baselines.py` checks, in the suite, that a baseline can fail a measurement.

## The default selection: function-level, from the coverage map

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

### How tests are chosen

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
  counts as an import-time change: every test that imported it, even when the
  module binds nothing (empty, only a docstring, `pass` or comments). The map
  cannot have seen an added module imported, so for one the static graph also
  selects, among all tests, those whose imports now reach it.
* **Deleted and changed files in the static graph.** The graph is built from
  the tree after the change, plus each changed file as it was before: a
  deleted module keeps its importers, a deleted fixture the tests that named
  it, and an import the change removed still counts.
* **Lean.** The executables whose root imports the module (from the Lean
  import graph), then the tests that ran those executables; plus `lake build`,
  `lean/audit.py` and the Lean import check.
* **Rust.** The tests that ran a Rust binary, `cargo test`, and the release
  and debug builds.
* **Any file.** Whatever its kind (Python, Lean, Rust, data), the tests that
  read it, and for an added or removed file the tests that listed any
  directory above it, up to and including the root `.` (as the first or last
  file there it also makes its directory appear or vanish, which changes the
  parent's listing). `kind_of` and `file_impact` in `tools/select_tests.py` are this
  one rule for the plan and the drift check; a path named without a visible
  edit may also have appeared or vanished.
* **Data and documents.** Nothing beyond that rule, except that a fixture a
  Rust test embeds with `include_bytes!` also runs `cargo test`.
  Documentation selects only its readers and listers.
* **Everything.** `tests/conftest.py`, `pyproject.toml`, `uv.lock`,
  `.gitignore` and files outside the known top-level directories select the
  complete suite.
* **Smoke.** Any change beyond documentation also runs three fast files
  (`SMOKE` in `tools/select_tests.py`).

The layer checks run only when their inputs change: the Python import check
when a `ve/` module's imports change, the Lean import check for `.lean`
files, the Rust dependency check for Rust sources, and
`tools/test_layer_policy.py` when the selector's own code changes.

### The coverage map

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
*uncertain* (the drift check applies the plan's per-file rule, so a file that
selects everything, such as `pyproject.toml`, makes every test uncertain) and
is selected by the static graph (`tools/source_graph.py`: import closure,
string-literal mentions of files, directories and programs) instead. Test files that failed or were opaque when recorded (a Python child
the recorder could not follow) are treated the same way, and without a map
the static graph is the whole answer (`--static` forces it).

Selection takes about 1 s with warm caches (parsed sources are cached per
file under `~/.cache/ve-testselect`); the first run after a new map or a
change to the selector parses more and took up to 11 s on the loaded VM.

### Evidence

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

These numbers were computed on 2026-10-04 with version-2 maps and the
selector before the review fixes in `docs/testselect-report.md`; they have
not been regenerated since (that needs a version-3 map recording).

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
