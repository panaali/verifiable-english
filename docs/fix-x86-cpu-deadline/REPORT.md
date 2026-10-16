# fix-x86-cpu-deadline: build report

**DRI signature needed: DELTA row 1** (the CPU deadline now counts user CPU only). The task directs
this change, but no standing ruling covers it.

Branch `fix/x86-cpu-deadline`, synced with main a650eeb63. The product change is in
`ve/backends/lean_service.py`. Tests are in `tests/test_lean_service.py`, plus one stale entry
removed from the reviewed list in `tests/test_numeral_conversion.py`.

## Cause

The CPU attribution was wrong, but not in any of the ways the task suspected. The extra CPU is
**system time the kernel spends compacting memory inside the service's own page faults** while the
host is short of memory. It is real CPU in the service's main thread, but the host's memory state
causes it, not the request.

1. **Per-request probe** (pytest plugin wrapping `LeanService._roundtrip`, reading
   `/proc/<pid>/stat`, `/proc/<pid>/task/*/stat` and `schedstat` before and after each request). It
   ran `test_english_mixed_merge_smoke`, `test_asimov_extended.py` and
   `test_definitions_differential.py` with `-n 8` next to 24 `yes` hogs, 13:36–14:00 UTC, load rising
   to about 80 on 32 CPUs. Eleven `english.check` requests and two `english.read` requests were each
   charged 0.26–1.38 s of **system** CPU but at most 0.12 s of user CPU. Examples: user 0.01 s,
   system 1.12 s; user 0.09 s, system 1.38 s; user 0.0 s, system 0.92 s. Each had only 26–177 minor
   faults, about 10 ms of kernel time per fault, and all of the time was in the main thread. On a
   long-lived service (5,500–6,000 requests served) none of this was startup.
2. **Kernel stacks** of every `ve_service` on the host (bpftrace `profile:hz:997`, kernel-mode
   samples only), 16:16–17:01 UTC, while the integration gates ran. From 16:23 to 16:36 the host's free
   memory fell from 69 GB to 1 GB (`evidence/vmstat-16h20-16h37.log`: `compact_stall` up to 3,444 and
   `thp_fault_fallback` up to 742 per 10 s). During that window, `ve_service` processes spent up to
   9.9 s of kernel CPU in each 10 s window. One process spent 241.8 s from 16:23 to 16:36, another
   146.1 s (`evidence/kernel-cpu-windows.json`). Of the leading kernel stacks' samples, 97.4% are in
   direct compaction: `__alloc_pages_slowpath` → `__alloc_pages_direct_compact` → `compact_zone`,
   spinning in `balloon_page_isolate`/`balloon_page_putback` on the VM's balloon pages
   (`evidence/kernel-stacks.txt`).
3. **Why the service compacts.** Lean's allocator (mimalloc) reserves a 1 GiB arena with
   `madvise(MADV_HUGEPAGE)` and returns freed memory with `MADV_DONTNEED` (strace of `ve_service`
   at startup). THP here is `enabled=madvise`, `defrag=madvise`, so a fault in that arena tries a
   huge page and, when the host is low on free memory, runs direct compaction synchronously. The
   kernel charges that work to the faulting process as system time.

**Hypotheses the task listed, ruled out:**
- *Other threads.* The service has 3 threads: main, `iou-sqp-<pid>` (libuv's io_uring SQPOLL kernel
  thread) and a libuv `ep_poll` thread. Across all 221 logged requests in run 1 the other two used
  0.0 s. All the CPU is the main thread's.
- *An earlier request still running, or a delta taken across a request boundary.* The start reading
  is taken after the previous response has been read in full. The overcharged requests' extra time is
  system time inside the request window, in the main thread.
- *GC or startup.* Lean frees memory by reference counting; the time is kernel time. The services
  involved had served thousands of requests.
- *Another process's pid.* `Popen` runs the executable directly, so `pid` is `ve_service`, and
  per-thread data under that pid shows the time.

Earlier workers timed these requests at no more than 0.1 s, and they were right: that is their user
CPU. The overruns come and go with the host's memory state. In this item's four later probe runs
(14:00–15:35, one of them an A/B with THP off for the service) no request got more than 0.1 s of
system CPU.

## Fix

`_cpu_seconds(pid)` now returns the process's **user** CPU: field 14 (utime) of
`/proc/<pid>/stat`, parsed by the new `_user_seconds`. The CPU deadline (`_deadline`, `_wait`) and
`LeanService.cpu_seconds()` read it. The deadline values (`DEADLINES`), `WALL_FACTOR`, the wall-clock
cap and the `CheckerUnavailable` text are unchanged. A user-CPU spin is still stopped at its deadline
(`test_a_request_past_its_cpu_deadline_names_its_mode_and_is_not_retried`). A process stuck in the
kernel is still bounded by the wall-clock cap. A stat line whose utime is not a number reads as "not
reported" (None) instead of raising a ValueError out of the client. The module docstring and the
`_user_seconds` docstring give the reason.

The user/system split is the kernel's tick-sampled split, scaled to the precise runtime. Across one
request it is accurate to a few ticks, which matters nothing against deadlines of 5 s and more.

## Tests

- `tests/test_lean_service.py::test_a_request_is_charged_its_user_cpu_not_the_kernels_time_in_the_service`:
  a fake service (`kernel` behaviour) reads `/dev/zero` until its own system time has grown by 0.6 s.
  That is kernel work with almost no user CPU, the shape of the compaction stalls. Under a 0.3 s
  deadline it is answered without a retry, and the test checks that the request really used
  user < 0.3 < 0.6 <= system. The fake measures its own CPU, so no timing threshold depends on the
  machine's speed. It is skipped where there is no `/proc`, like the other CPU-deadline tests.
- `tests/test_lean_service.py::test_the_cpu_deadline_reads_the_user_time_of_a_proc_stat_line`: field
  14, not 15 and not their sum, after a command name containing `) (`. A short line and a non-numeric
  utime both give None.

Runs:
- VM (x86, load about 40): `tests/test_lean_service.py tests/test_numeral_conversion.py
  tests/test_hang_guards.py test_english_mixed_merge_smoke test_rerun_mutant_equals_the_committed_results
  test_populated_defined_table_limit_boundary` with `-n 8`: 381 passed.
- Mac, selected tests (`mac-pytest.sh --select -- --base <merge base> --run`, 298 of 384 units): one
  failure, `tests/test_numeral_conversion.py::test_every_int_conversion_in_ve_is_bounded_or_reviewed`.
  It still listed the removed `int(fields[12])` as stale; fixed in b227a89fd, and that file now
  passes (86 passed, VM).
- Mac, final code: `mac-pytest.sh -- tests/test_lean_service.py tests/test_numeral_conversion.py`:
  287 passed. The kernel-time test is skipped there (no `/proc`); the parser test runs.
- `lake build` passes after the sync with main. No Lean or Rust code changed.

## Pre-existing failures (not this branch's)

- `tools/relay_mutation_gate.py` exits 1 with "42 routes, 116583 mutants, 39 failures": allow-list
  paths that match nothing, plus accepted mutants in the `route`, `parse`, `graph` and `norm-defaults`
  schemas. Run with main's `ve/backends/lean_service.py` swapped in, the output is identical,
  failure for failure. It belongs to main (probably the lf-14a merge, which changed
  `parse.json`/`readings-route.json`), not to this item. Not touched.
- `main-known-red.txt` lists the two
  `test_the_sub_tick_deadline_tests_hold_on_a_fast_machine_and_need_the_response_check` cases. They
  passed in this branch's VM run. Not edited.

## Follow-ups

- The compaction stalls also cost wall time: a service at 100% kernel CPU for minutes still meets
  the wall-clock cap (10 times the deadline, or the suite's `HANG_TIMEOUT`). Turning THP off for
  `ve_service` would remove the stalls themselves: `prctl(PR_SET_THP_DISABLE)` in the spawn, or
  mimalloc's large-page option. That changes how the service runs, so it is a separate DRI
  decision; this item only fixes the measurement.
- The `CheckerUnavailable` text could quote the measured user seconds, to make the next report
  easier. Not done, since it would be a wording delta.

## Seeded bugs

Committed in `docs/fix-x86-cpu-deadline/seeded-bugs.json`. All are in Python (the only language
whose product code changed) in `ve/backends/lean_service.py`, and all were restored afterwards:
- **S1** `ve/backends/lean_service.py`: utime + stime (the old measure). Failed:
  `test_a_request_is_charged_its_user_cpu_not_the_kernels_time_in_the_service` (CheckerUnavailable
  ... deadline of 0.3 s of CPU) and `test_the_cpu_deadline_reads_the_user_time_of_a_proc_stat_line`
  (503.0 == 3.0).
- **S2** `ve/backends/lean_service.py`: stime in place of utime. Failed: both new tests. The old
  user-CPU spin test still passed (after 674 s), so these two tests are what catch it.
- **S3** `ve/backends/lean_service.py`: `except IndexError` only. Failed:
  `test_the_cpu_deadline_reads_the_user_time_of_a_proc_stat_line` (ValueError: invalid literal for
  int()).

## Directive lines

- "find what ... `_cpu_seconds` ... actually charges to one request under load": Cause, above;
  evidence in `docs/fix-x86-cpu-deadline/evidence/`.
- "Reproduce it on the VM under the gate's real load ... log per-request CPU deltas": probe run 1
  (per-request user, system and per-thread deltas) and the host-wide bpftrace run.
- "Fix the measurement so one request is charged only its own CPU, with the deadline values
  unchanged; do NOT raise or remove the CPU deadline and do not quarantine the tests": commit
  dfe7bf24f; `DEADLINES` and `WALL_FACTOR` untouched; no quarantine.
- "Add a test that pins the corrected attribution (no timing threshold that depends on machine
  speed)": `test_a_request_is_charged_its_user_cpu_not_the_kernels_time_in_the_service`.
- "Test on the VM and via mac-pytest.sh on the Mac": Runs, above.
- FAST LANE: the full gate was not run, as the task directs.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer, schema or relay changed; this is the client's CPU clock.
2. PASS: every directive line is mapped above (Directive lines); the diff adds no Python copy of a
   Lean decision and no report test (D4).
3. PASS: seeded bugs S1–S3 (`seeded-bugs.json`), each failing
   `test_a_request_is_charged_its_user_cpu_not_the_kernels_time_in_the_service` and/or
   `test_the_cpu_deadline_reads_the_user_time_of_a_proc_stat_line`.
4. N.A.: no Python, Lean or Rust checker output changed; the corpus answers are the same.
5. N.A.: no field read from a Lean answer changed.
6. PASS for the parts that apply: synced with main a650eeb63 and rebuilt (`lake build`); the full
   gate is left to the merge train (FAST LANE).
7. PASS: DELTA row 1 is marked "needs a DRI signature", and the first line of this report says so.
8. PASS: DELTA row 1 covers the one user-visible change, availability (answered instead of
   `CheckerUnavailable` when the extra CPU is the kernel's); `test_a_request_is_charged_its_user_cpu_not_the_kernels_time_in_the_service`.
9. PASS: `tools/select_tests.py --base <merge base>` selects 298 of 384 units, including
   `tests/test_lean_service.py`, which catches S1–S3.
10. N.A.: no Lean statements or proofs.
11. PASS: the CPU deadline still fails closed on user CPU
    (`test_a_request_past_its_cpu_deadline_names_its_mode_and_is_not_retried`, the
    `test_each_phase_of_a_request_is_bounded_by_its_cpu_deadline` cases); the new test uses no sleep
    and no wall-clock deadline (`tests/test_hang_guards.py` passes).
12. N.A.: the measure costs the same (one `/proc` read); no Lean or Python work changed.
13. N.A.: no test removed or renamed.
