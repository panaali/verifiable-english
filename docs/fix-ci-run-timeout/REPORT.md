# fix-ci-run-timeout: build report

**DRI signature needed: DELTA rows 1–3** (`DELTA.md`). The acting DRI's task (2026-10-16) directs all three, but
no standing ruling covers a changed hang guard, a deleted assertion or a new tool option. No product output
changes.

Branch `fix/ci-run-timeout`, from main 2a4fbf70 (merged with main 8cbb3049 at the end). The fast lane: no full
gate was run here; the chain runs the selected tests on the final HEAD.

## Cause

`tests/test_difffuzz.py::test_ci_run` ran `python -m tools.difffuzz --ci` under a fixed wall wait of
`HANG_TIMEOUT` (1800 s). The x86 nightly of 2026-10-15 (`gate.py --no-quarantine`, 8 workers, 229 min) stopped it
there. The run's standard error showed that it had started its third surface of four (`requests`,
`environment`, `wire` logged; no `document`) (`manage-agents/nightly-vm-gate.json`). So it was working, and
slowly, not hung.

**No stage grows out of proportion; the whole run is CPU-bound and stretches with the CPU share it gets.**
The stages, timed with an instrumented copy of the run (`evidence/time_stages.py.txt`) on the VM while other
agents' jobs held the load average at 70–97 on 32 vCPUs (`evidence/stage-timings-loaded.json`):

| Surface | Wall s | Own CPU s | Lean service CPU s | Runner CPU s |
|---|---:|---:|---:|---:|
| requests | 93.6 | 50.7 | 10.1 | 14.3 |
| environment | 73.5 | 36.8 | 22.8 | 0.4 |
| wire | 117.4 | 70.9 | 20.5 | 0 |
| document | 122.8 | 38.8 | 40.0 | 0 |
| baseline replay | 3.7 | 0.9 | 0.2 | 0.5 |
| **run** | **419** | **204.6** | children in all: 92.2 | |

The run is one Python process that alternates with its Lean services and runners. Nothing in it waits on a
clock: the Python calls (26,677 of them, 156 s of CPU) and the service requests are all CPU work. Its wall time is
therefore its CPU time (about 300 s) divided by the share of one CPU it gets. At load 70–97 that share was 0.7
(419 s). Alone it is 85 s on the Mac runner (aarch64, `mac-pytest.sh -n 0`, 2026-10-16 03:27Z) and was 184 s on
the VM (2026-10-10, `docs/test-speed-b5/evidence/quarantine-test_ci_run.json`). The nightly needed more than
1,800 s, so it got less than a sixth of a CPU. One likely reason, for the orchestrator (not changed here): the
nightly's gate runs in an `iso.sh nightly-vm-run` scope, whose name does not match `svc-nightly-vm*`, so it
gets CPUWeight 100, while the merge trains' scopes get 1000 (`systemctl --user show -p CPUWeight`,
2026-10-16 03:30Z). The Lean service's CPU deadlines already count user CPU only (fix-x86-cpu-deadline). The
run's inner guards (each runner batch's RLIMIT_CPU, the Python calls' CPU alarm, the services' CPU deadlines)
count CPU too. Only the test's outer wait was wall time.

## Fix

The hang guard stays; it now tells a hang from a slow machine by the run's progress.

- `tools/difffuzz.py --progress`: the run writes its work counters (`WORK`: inputs, Python calls, runner and
  service requests and cases) to standard error as `difffuzz-progress {...}` lines. The lines come from where
  the work is counted (`spend`), the first at once, then at most one every 5 s (`PROGRESS_EVERY`), and one at
  the end. Only work advances them, so a run that hangs falls silent; no timer thread reports for it.
- `tests/subprocesses.py`: `run_while_progressing(command, progress)` runs the child as
  `subprocess.run(capture_output=True, text=True)` would, and reads its standard error as it comes. It stops the
  child, and raises `Stalled` (a `TimeoutExpired`), when the child reports no progress for `HANG_TIMEOUT`
  (1800 s), or when it is still running after `PROGRESS_WALL_CAP` (4 × `HANG_TIMEOUT` = 7200 s) in all. Progress is
  a value above every earlier one (`Progress`): a repeated or falling report is none. The cap is checked
  before every read, so a child that floods its standard error is still stopped at it. On a stop, or when the
  progress reader raises, the child's whole session is killed (its Lean services and runners with it). Its
  waits are computed from an injectable clock; no literal timeout or sleep (`tests/test_hang_guards.py` passes).
- `test_ci_run` runs `--ci --progress` through it. Every assertion on the report is unchanged
  (no new finding, the baseline reproduces and is reviewed, `CI_BUDGET`'s mutant counts, every engine
  answers both ways on every surface, `WORK_LIMIT` and each input evaluated once). One is added: the last
  progress line equals the report's `work`, so the progress reports cannot silently stop.
- The quarantine entry is removed (`tools/test-quarantine.json` has no entry).

A first version also stopped the run as soon as a progress line showed a count past `WORK_LIMIT`. A planted
wrong answer (S7 below) showed why that is wrong: a run with a new finding minimises it, which costs more work,
and the early stop then failed the test on the work limit, with no report, instead of on the finding. The
third commit removes it; the limit is checked on the ended run's report as before.

## What the tests show

| Claim | Evidence |
|---|---|
| Under a slow machine the old guard fails and the new one passes | A/B, 2026-10-16 04:24Z, each run in its own systemd scope capped at 15% of one CPU (`CPUQuota=15%`), at load 82–103: main's `test_ci_run` failed with `TimeoutExpired: Command [... -m tools.difffuzz --ci --report ...] timed out after 1800 seconds` after 1,849 s and 277 s of CPU (the nightly's error). This branch's `test_ci_run` passed in 2,749 s (412 s of CPU) (`evidence/ab-cpu-quota.json`) |
| The test passes in a loaded full run on the VM | The full suite of 5269b750 (`-n 8`, in an `iso.sh` scope with MemoryMax 32G and CPUWeight 100, like the nightly's) ran beside other agents' jobs, 02:45–05:12Z: 15,647 passed, 0 failed (8 skipped, 83 xfailed) in 2 h 27 min. The load average had a median of 82 and a range of 55–155 on 32 vCPUs, with at least 19 GB available. `test_ci_run` passed in 581 s at load 64–89 (`evidence/loaded-full-run.json`, `evidence/loaded-full-run-load.log`). 5269b750 differs from the final code only by the early work stop that 65bad680 removed, which a passing run never reaches |
| A real hang still fails it | S6: the run blocks forever (no CPU) once 12,000 inputs are counted; `test_ci_run` failed with `Stalled: ... made no progress for 1800 s` at 1,924 s (124 s of work, then the stall window), and no process of the run was left |
| A wrong answer still fails it | S7: Python's `UnknownSymbol` code set to `SyntaxError` in `ve/errors.py`: `test_ci_run` failed on the report's new `code` disagreement (`requests`, `elaborated-document:evaluate`) after 684 s |
| The rules of the watch | `tests/test_progress_watch.py`: a child that keeps progressing outlasts the stall window several times over and is due only at the cap; only a value above every earlier one is progress; a working child's output and exit status are returned; a child that stops (blocks, repeats its last report, or closes its standard error and keeps running) is stopped with its session (its grandchild's FIFO reaches end of file); a child past the cap is stopped while it still reports; a progress reader that raises stops the child. The deadlines are passed by an injected clock; nothing waits them out |
| The run reports its work as it counts it | `tests/test_difffuzz.py::test_the_run_reports_its_work_as_it_is_counted` (an injected progress clock) |

## Seeded bugs

Each was planted in a mutant worktree of the branch (S1–S6 on 5269b750, S7 on 65bad680, S8 on 5269b750), its test run, and restored (`git checkout`). Only Python code changed
(`tools/`, `tests/`); no Lean or Rust file is changed, so there is no Lean or Rust seed.

| # | File | Seeded bug | Failing test |
|---|---|---|---|
| S1 | `tools/difffuzz.py` | `spend` never reports progress | `tests/test_difffuzz.py::test_the_run_reports_its_work_as_it_is_counted` |
| S2 | `tests/subprocesses.py` | `Progress.seen` counts any report, a repeated or falling one too | `tests/test_progress_watch.py::test_only_a_value_above_every_earlier_one_is_progress[same]` |
| S3 | `tests/subprocesses.py` | `PROGRESS_WALL_CAP = HANG_TIMEOUT` (no room for a slow run) | `tests/test_progress_watch.py::test_a_child_that_keeps_progressing_is_never_due_before_its_cap` |
| S4 | `tests/test_difffuzz.py` | (the early work stop of the first version, removed since; seed retired) | — |
| S5 | `tests/subprocesses.py` | the cap is not checked while lines keep coming | `tests/test_progress_watch.py::test_a_child_past_its_cap_is_stopped_while_it_still_progresses` |
| S6 | `tools/difffuzz.py` | the run hangs without CPU after 12,000 inputs | `tests/test_difffuzz.py::test_ci_run` (`Stalled ... made no progress for 1800 s`) |
| S7 | `ve/errors.py` | Python's `UnknownSymbol` code is `SyntaxError` (a wrong answer) | `tests/test_difffuzz.py::test_ci_run` (the new disagreement) |
| S8 | `tools/difffuzz.py` | no progress line at the end of the run | `tests/test_difffuzz.py::test_ci_run` (`progress[-1] == report["work"]`) |

## Tests run

- While iterating: `tests/test_progress_watch.py`, `tests/test_difffuzz.py` (the new and work-bound tests),
  `tests/test_hang_guards.py`, `tests/test_cpu_bounds.py`, `tests/test_gate_quarantine.py`: all pass.
- `tools/gate_collection.py --check --prebuilt`: 15,739 collected, 11 added, 0 refused, 0 stale, 0 malformed.
- `tools/select_tests.py --base $(git merge-base HEAD main)`: 310 of 395 units, because `tests/subprocesses.py`
  is the helper most tests import; the selection holds `tests/test_progress_watch.py`, `tests/test_difffuzz.py`
  and `tests/test_hang_guards.py`.
- __SELECTED__
- Not run: the full release gate (fast lane).

Pre-existing failures (`main-known-red.txt`), not touched: none of the three tests listed there failed in the loaded full run.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed Lean answer, schema or relay changed.
2. PASS: each directive above has its commit and test: the stage timing (`evidence/stage-timings-loaded.json`),
   the progress guard (`tests/test_progress_watch.py`), the loaded full run, the planted hang (S6), the
   planted wrong answer (S7), and the quarantine removed (`tests/test_gate_quarantine.py`).
3. PASS: seeded bugs S1–S3 and S5–S8 each fail a named test.
4. PASS: `tests/test_difffuzz.py::test_ci_run` (no new disagreement between Python, Lean and Rust) on HEAD;
   no product code changed.
5. N.A.: no field read from a Lean answer changed.
6. PASS: fast lane, so no gate evidence here; the branch is synced with main 8cbb3049 and the chain tests the
   final HEAD.
7. PASS: DELTA rows 1–3 are listed as DRI signature needed in the first line.
8. PASS: `DELTA.md`; no product output changes.
9. PASS: `tools/select_tests.py --base $(git merge-base HEAD main)` selects `tests/test_progress_watch.py` and
   `tests/test_difffuzz.py`, which S1–S8 fail.
10. N.A.: no Lean change.
11. PASS: the guard's deadlines are injected (`tests/test_progress_watch.py`); no sleep or literal timeout
    (`tests/test_hang_guards.py`).
12. PASS: one `time.monotonic()` per counted unit of work and at most one line every 5 s; `test_ci_run` alone
    on the Mac ran in 85 s.
13. PASS: no test removed or renamed; `tools/gate_collection.py --check --prebuilt` reports 0 refused, 0 stale and 0 malformed.
