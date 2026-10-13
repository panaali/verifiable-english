# runner-portability: sub-tick CPU deadline tests on fast runners

Task (DRI 2026-10-13): the full suite must pass on a fast aarch64 runner (Apple M5 Pro, Ubuntu 24.04)
without weakening a check. One test failed there:
`tests/test_question_reading.py::test_the_whole_question_is_bounded_by_the_modes_deadline`,
"DID NOT RAISE CheckerUnavailable".

## Cause (the DRI's reading, confirmed)

`LeanService._wait` (`ve/backends/lean_service.py`) compares the service's CPU time, read from
`/proc/<pid>/stat` in clock ticks (`SC_CLK_TCK` = 100, so 10 ms), with the CPU it had at the request.
The test injects a 1e-6 s deadline and expects it to trip. On a fast machine the question's whole Lean
work fits in one tick, so every reading equals the start and `used - start > 1e-6` is never true.

Reproduced on this x86 VM by freezing the reading (`_cpu_seconds` returning 0.0, as a machine that
finishes within one tick sees it): main's question test and main's document test both fail with
`DID NOT RAISE CheckerUnavailable`; with this branch's tests both pass. The edit was reverted.

The product is right: every mode's real deadline is a second or more, a hundred ticks or more, so the
tick resolution does not change what it decides. No product code changed.

## Change

- `tests/subprocesses.py`: `busy_cpu(monkeypatch, module)`, a CPU clock for the service's deadlines.
  Each reading of a process is one tick past its last reading and never below its real CPU time, so
  the service is seen working and a sub-tick deadline is passed at the client's next check, on any machine.
- The two tests that inject a deadline below one tick and expect it to trip now read the service's CPU
  on that clock. Each keeps its claim and its injected deadline:
  - `tests/test_question_reading.py::test_the_whole_question_is_bounded_by_the_modes_deadline`
    (the failing test). It also now asserts `operation == "english.question"` and that the
    request's CPU was read at least twice (once at the start, once when the check fired).
  - `tests/test_lean_document_wrapper.py::test_a_document_past_its_cpu_deadline_is_unavailable_never_ok`
    (deadline 1e-4 s per case; it passed on the M5, but whether it passes depends on machine speed
    in the same way).
- `tests/test_hang_guards.py`: `test_every_sub_tick_cpu_deadline_is_read_on_the_busy_clock`, an `ast`
  lint that fails when a test sets a constant mode deadline below one tick (`setitem(... DEADLINES ...)`
  or `DEADLINES[mode] = ...`) without `busy_cpu`; `test_the_sub_tick_lint_sees_each_form` (five forms);
  `test_the_busy_cpu_clock_advances_a_tick_per_reading_above_the_real_one`.
- `tools/gate-collection.json` regenerated (seven new test IDs, none removed).

## The search for other tests of this kind

Searched `tests/` for `DEADLINES`, `_cpu_seconds`, `cpu_seconds`, near-zero `timeout=` and timeout
settings, and `deadline`/`budget` values below 0.1 s. Only the two tests above inject a deadline below
one tick and expect it to trip. The others do not depend on machine speed or tick resolution:

- `tests/test_lean_service.py::test_a_request_past_its_cpu_deadline_names_its_mode_and_is_not_retried`
  (0.3 s, against a fake that spins forever: certain to pass it).
- `tests/test_lean_service.py::test_a_request_that_gets_no_cpu_meets_the_wall_cap` (injected expired
  wall clock).
- `tests/lean_routes.py::completed_within` and its users, `tests/test_soft_request_economy.py`
  (deadlines expected *not* to trip; a faster machine only helps).
- `tests/test_senses_route.py`, `tests/test_senses_document.py`, `tests/test_assist_deadline.py`,
  `tests/test_assist_recovery_replay.py` (injected `time.monotonic`).
- `tests/test_stage2_dispatch.py`, `tests/test_hang_guards.py` short timeouts (recorded waits, not timed).

## DRI rulings

No user-visible delta: no verdict, wording, field, fault order, CPU or trust budget changes. Nothing
needs a standing ruling or a DRI signature.

## Seeded bugs

Committed in `docs/runner-portability/seeded-bugs.json` (file, change, test, result). Each was planted,
shown to fail its test, and removed:

1. S1 `tests/subprocesses.py`: busy_cpu adds no tick -> clock unit test fails.
2. S2 `tests/subprocesses.py`: busy_cpu drops the real floor -> clock unit test fails.
3. S3 `tests/test_question_reading.py`: question test reads the real clock -> the sub-tick lint fails.
4. S4 `tests/test_hang_guards.py`: the lint inverted -> 3 of its 5 form cases fail.
5. S5 `ve/backends/lean_service.py`: the CPU deadline check never fires -> both deadline tests fail.
6. S6 `ve/backends/lean_service.py`: the error names operation `lean`, not the mode -> question test fails.

Only Python test code changed (no Lean, no Rust, no product code); S5 and S6 seed the product code
whose behaviour the two fixed tests claim.

## Tests run

- The three changed test files in full (`-n 8`): 441 passed, 1 failed (the elapsed-time guard flagged the
  clock unit test's `module._cpu_seconds(...)` asserts as reading a CPU measure; fixed by reading the
  injected fake through a local name), then `tests/test_hang_guards.py` 68 passed.
- `select_tests.py --base $(git merge-base HEAD main)` selects all 370 of 370 units (the coverage map
  is stale for this base), the same set as the full gate, so it was not run separately; the full gate
  on the final HEAD covers it.
- Not run: the aarch64 runner itself (no access from this VM); the frozen-reading reproduction above
  stands in for it.
- Full gate, once, on the final code commit 336e8c93 with `--workers 8`: **passed**, 14,896 passed,
  92 skipped (all allowed), 0 failures, 36 Rust tests passed (`gate-result.json` in this folder). Only
  this report and that file were committed after it. An earlier start of the gate on the same commit
  was stopped unfinished: under a machine load of about 86 on 32 CPUs, `-n auto` gave the suite one
  worker, and after 2.4 hours it was about 16% through. It produced no result, so this is not a rerun.
