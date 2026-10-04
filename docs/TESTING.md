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

Without `--impacted`, `tools/select_tests.py` selects by architecture layer: the changed layer and every layer outside it (`docs/ARCHITECTURE-LAYERS.md`). That is the broader check to run before asking for review.

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
