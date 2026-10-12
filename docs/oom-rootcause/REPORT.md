# OOM root cause: the Rust `ve` search, and memory budgets for every checker process

Branch `infra/oom-rootcause`, base `main` 5479466f. Times are UTC.

## Summary

Both out-of-memory kills (2026-10-10 18:54:28, `ve` PID 1353080, anon-rss 91 GB; 2026-10-11 06:28:26, PID
2800679, anon-rss 99 GB) were a `ve jsonl -` process that the UDHR translation pilot's whole-document check
started. Its countermodel search built the list of every domain-size vector before it looked at a single
model. There are (max_domain_size + 1)^sorts such vectors. The whole UDHR has 22 sorts (23 with the reading
sort), so at domain bound 2 the list is 3^23 ≈ 9.4 × 10^10 vectors. No search budget applied before the list
was complete. The default 5 s Rust timeout used to kill the process at about 2 GB. Both times the pilot's
translator raised the timeout (`VE_RUST_TIMEOUT=900`, then `1200`) to make the slow check finish, which let
the list grow until the kernel's OOM killer acted. systemd then stopped the whole tmux scope.

The fix enumerates the vectors lazily, in the same order. The same recorded case now takes 0.05 s and
7 MB, where it used to take more than 2 GB in 11 s. In addition, the binary enforces a global memory
budget (default 8 GiB, `VE_RUST_MEMORY_LIMIT`), answered with ResourceLimit. The Python client passes that
budget on and sets an address-space limit (RLIMIT_AS) on each child. The Lean one-shot runners now run under
RLIMIT_AS too. The Lean service already did.

## 1. What ran (facts, with confidence)

| | 2026-10-10 | 2026-10-11 |
|---|---|---|
| Kernel kill | 18:54:28, `ve` 1353080, anon-rss 95,887,716 kB | 06:28:26, `ve` 2800679, anon-rss 103,485,072 kB |
| Pilot worktree | `~/code/ve-udhr-20261010T1800Z` | `~/code/ve-udhr-20261011T0600Z` |
| Command (pilot translator session) | 18:36:32: `VE_RUST_TIMEOUT=900 timeout 3300 uv run --frozen python $N/verify_step.py $N/scratch/translation-whole.ve.md check` | 06:18:54: `VE_RUST_TIMEOUT=1200 timeout 3300 uv run --frozen python whole_check.py` (`check_document` on `scratch-whole.ve.md`) |
| Input | `run-20261010T1800Z/scratch/translation-whole.ve.md` (136,062 bytes, 19 declared sorts) | `run-20261011T0600Z/scratch-whole.ve.md` (155,183 bytes, 22 declared sorts) |
| Its log | `logs/whole-check-rust900.log`, created 18:36:32, still 0 bytes | `logs/whole_check.log`, created 06:18:54, still 0 bytes |
| The attempt before it, at the default timeout | `logs/whole-load.log` 18:35: `find_countermodel` … `CheckerUnavailable` … `timed out after 4.999215909978375 seconds` | `logs/whole_try.log` 06:18:43: `timed out after 4.994150220998563 seconds 234.3 s` |
| Transcript | `~/.agent-accounts/claude-panaali2/projects/-home-seyran-code-ve-udhr-20261010T1800Z/2d85a7da-….jsonl`: the last record, 18:54:28.601, is the command's end (exit 144) | `…-ve-udhr-20261011T0600Z/9458b846-….jsonl`: no result was ever recorded |

- **Subcommand:** `ve jsonl -`, started by `ve/backends/rust_jsonl.py` (`_Checker`). The call that grows
  is `check_document` → `readings_verdicts` → `ve.search.find_countermodel` → the Rust `countermodel-search`
  case (no `kind`, `premises` + `conclusion`, `max_domain_size` 2, `min_domain_size` 0).
- **Confidence: high** that the pilot's whole-document check was the process. The evidence: the matching
  commands, the empty logs created at the start, and the earlier 5 s timeouts on the same document, in
  `find_countermodel`. On 10-10 the session's command also ended in the same second as the kill. Two points
  rest on inference, not proof: (a) the parent PID of each `ve` (the OOM dump lists processes, not
  parents; the 06:00 dump shows the bash/tail/tee/timeout/uv/python chain of that command just before
  PID 2800679); (b) the constitution pilot is ruled out by timing (on 10-10 it had finished at 18:47:37;
  on 10-11 its last command started after PID 2800679 existed, 82 s before the kill). No other `VE_RUST_TIMEOUT=`
  appears in any pilot transcript, and `merge-train.log`, the gate and the pytest logs show nothing in
  either window. The process search was done by a read-only sub-agent and re-checked here on the quoted lines.

## 2. Reproduction (under a cap)

All runs were under `zsh ~/code/manage-agents/iso.sh oomrepro <cap> -- …`:

1. A synthetic case, 22 sorts with no constants and bound 2, on the old binary (main, sha256 3ec83dee…)
   under 8G: killed by the memory cgroup after 20.6 s at 8.37 GB RSS, with no model checked.
2. **The real command on the real input:** `check_document` on a copy of the 10-11 `scratch-whole.ve.md`,
   with `VE_RUST_TIMEOUT=1200`, from this worktree at main's code, under 8G. After 3 min 50 s the kernel
   logged `Memory cgroup out of memory: Killed process 2956810 (ve) … anon-rss:8304492kB` and systemd logged
   `Failed with result 'oom-kill'` for the scope. This is the incident, contained.
3. The same run with the fixed binary, through a wrapper that recorded every case line sent to Rust: it
   completed in 2,343.5 s with no kill (`premises: model`). It sent 66 cases: 44 countermodel searches,
   all with 22 or 23 sorts at bound 2, and 22 `readings-superposed-evaluate` cases.
4. The first recorded search, now `tests/data/oom/udhr-whole-search.jsonl` (23 sorts): the old binary
   under 2G was killed at 2.09 GB after 11.0 s. The new binary answers `Found` in 0.05 s at 7 MB peak.
   All 66 recorded cases on the new binary take 18.7 s CPU at 5.5 MB peak.

## 3. Mechanism

`rust/ve-profile/src/search.rs` `domain_sizes` (shared by `Models::new` and `order.rs` `order_models`) returned
`Vec<Vec<usize>>`: for every total from the minima's sum to `sorts × max`, it walked every vector with that
total. With k sorts, all minima 0 and bound 2, that is 3^k vectors of k `usize`s (24 + 8k bytes plus allocator
overhead each). For k = 23 that is about 9.4 × 10^10 vectors, tens of terabytes, so the walk only ever ended in a kill.
`max_models` (10,000) and `max_evaluations` are checked per model, after the list exists. The 100,000-atom
check is per size vector, so neither could stop it. The limit Python applies (`MAX_SORTS = 32`) admits the
shape. Lean owns meaning, and this was not a wrong answer: the process never answered.

## 4. What changed

**Root cause (Rust).** `DomainSizes` (`search.rs`) is an iterator that yields the same vectors in the same
order, holding one at a time. It yields the minima, then the lexicographic successor with the same total
(raise the last entry that can grow while its suffix can shrink, then refill the suffix with its least
completion), then the least vector of the next total. `Models` and `order_models` iterate it. A unit test
keeps the old eager walk as the order oracle over every minima vector of 0–4 sorts with entries 0–3, at
bounds 0–3 (including minima above the bound).

**(a) Global memory budget in the binary.** `rust/ve/src/memory.rs` is a counting `GlobalAlloc` over
`System`. It charges every live heap chunk at glibc's chunk size (size + 8, rounded up to 16, at least 32;
with requested bytes alone, a 32 MiB budget let peak RSS reach 41 MB on many small allocations). An allocation
past the budget, or one the system refuses (the RLIMIT_AS backstop), is not made. The registered handler
then ends the process:
- `ve jsonl`: it writes `{"id": <the case's id>, "status": "error", "error": {"code": "ResourceLimit",
  "message": "memory budget exhausted: <N> bytes (VE_RUST_MEMORY_LIMIT)"}}`, the record shape and exit
  status 1 that `rust_jsonl` already reads as ResourceLimit (`require_ok`). The process then exits.
  Memory is not reclaimed from a case midway, and the client starts a new process for the next case.
- any other command: `{"status":"error","error":{…ResourceLimit…}}` on stderr, exit 2, the binary's
  existing failed-command convention.

The budget is `VE_RUST_MEMORY_LIMIT` (a positive decimal byte count), by default `DEFAULT_LIMIT` = 8 GiB =
`ve/limits.py` `MAX_RUST_MEMORY_BYTES`. A test reads the binary's `--help` line to check that the two agree.
An invalid setting is InvalidInput (exit 2). This module is the binary's only unsafe code. The `ve` crate
goes from `forbid(unsafe_code)` to `deny` with one module-level `allow`. The three library crates keep
`forbid`. The unsafe code only forwards each call to `System`.

**(b) Backstops in the Python code that starts checkers.** In `ve/backends/process_limits.py`:
`configured_bytes`, `limit_address_space` (prlimit right after the start; `preexec_fn` is unsafe in a threaded
client) and `run_limited` (`subprocess.run` with the limit applied).
- `rust_jsonl`: each `ve jsonl` child gets `VE_RUST_MEMORY_LIMIT=<memory_limit()>` and RLIMIT_AS
  1 GiB above it. A process started under a different budget is never reused. An invalid setting is
  CheckerUnavailable before any process starts.
- `ve/backends/lean.py` one-shot runners (`run`, `run_route_cases`): `run_limited` with RLIMIT_AS
  `ADDRESS_SPACE` = 8 GiB. A runner that exceeds it gives no answer (CheckerUnavailable).
- The Lean service already ran under RLIMIT_AS 4 GiB (`lean_service.ADDRESS_SPACE`) and recycles at 2 GiB
  RSS. A new test checks the started service's `/proc/<pid>/limits`.
- Test plumbing that followed the one-shot transport: `tests/route_case_recorder.py` now wraps
  `lean.run_limited` (the relay mutation gate's one-shot cases), `tests/test_speech_source_relay.py` tampers
  through `ve.backends.lean.run_limited`, and the three `expired_waits` tests in
  `tests/test_assurance_manifest.py` inject the deadline into `process_limits`, the module that now waits.

## 5. Tests (`tests/test_rust_memory_budget.py`, 27 test IDs; Rust `search::domain_size_tests`, 2)

| Behaviour | Test |
|---|---|
| A seeded runaway input (a 90,000-tuple model under a 32 MiB budget) gets ResourceLimit with its id, exit 1, peak RSS within budget + 16 MiB; the same input under 256 MiB, and under the default, is answered | `test_runaway_input_returns_resource_limit_within_the_budget`, `test_the_same_input_is_answered_under_the_default_budget` |
| Other commands report it as a failed command (exit 2, stderr) | `test_every_other_command_reports_the_budget_as_a_failed_command` |
| The limit is configurable; invalid settings (`""`, `0`, `8G`, `-1`, `1.5`, `" 1"`, Arabic-Indic digits, overflow) are refused in Rust and in Python | `test_an_invalid_budget_setting_is_refused[*]`, `test_the_client_refuses_an_invalid_budget_setting[*]`, `test_configured_bytes` |
| Rust's default is Python's | `test_the_rust_default_is_the_python_default`, `test_the_client_default_budget` |
| The incident's input (the recorded UDHR search) and its shape (22 sorts) are answered within 64 MiB | `test_the_incidents_search_is_answered_within_a_small_budget`, `test_many_sorts_search_needs_no_memory` |
| The client passes the budget, caps the address space at budget + 1 GiB, never reuses across budgets, and reads an exhausted budget as ResourceLimit, then serves the next case | `test_the_client_passes_the_budget_and_caps_the_address_space`, `test_the_client_reads_an_exhausted_budget_as_resource_limit` |
| One-shot runners run under RLIMIT_AS; a child past it fails its allocation; a timed-out child is killed (injected deadline) | `test_one_shot_runners_run_under_an_address_space_limit`, `test_lean_one_shot_routes_run_under_their_address_space_limit`, `test_one_shot_runner_timeout_kills_the_child` |
| The Lean service runs under its RLIMIT_AS | `test_the_lean_service_runs_under_its_address_space_limit` |
| Lazy order equals the eager order; 22 sorts hold one vector | `domain_size_tests::lazy_sizes_are_the_eager_order`, `many_sorts_hold_one_vector` |

**Normal workloads are unchanged (corpus A/B):** `tools/rust_output_diff.py --baseline <main's binary> --new
<this binary>` compared 133 invocations (`ve conformance`, `ve jsonl` and `ve canonical-json` over every
`conformance/*.json` corpus and the route cases, plus the `wire.json` raw inputs) byte for byte, covering
stdout, stderr and exit code. Result: **0 differences, 0 timeouts**
(`evidence/rust-output-diff.txt`). The full suite's three-way and differential tests (difffuzz, conformance,
search) run on this binary in the gate.

**Selected tests** (`tools/select_tests.py --base main` selects all 360 units for this change). The
non-pytest steps passed: the layer checks, the crate graph, `cargo test` and the layer policy. The pytest
files ran in 16 chunks at `-n 3` at load 50–100: 14,323 passed, 83 xfailed, 8 skipped, 7 failed. Six of
the seven were reviewed inventories and test plumbing that predate the new transport. Each was fixed and
its file rerun green:
- `test_assurance_manifest.py`: the process-starter list (process_limits added) and the broad-handler review
  (`run_limited` now catches only TimeoutExpired/OSError).
- `test_senses_route.py`: two tests patched global `subprocess.run` to tamper with or guard the one-shot
  runner, and now patch `run_limited`.
- `test_numeral_conversion.py`: `int(text)` in `configured_bytes` is now bounded to 19 digits and listed.
- `test_relay.py`: the runner-transport inventory reads `run_limited` as starting a runner.

The seventh, `test_english_mixed_merge_smoke[claude-constitution-excerpt-reviewed-1]`, ran over a Lean
service CPU deadline at load 98 and passed alone (144 s). It is load-only. The 19-digit bound landed after
chunks 0–11 had run. It changes nothing when the setting is unset, and the final gate covers it.

## 6. Seeded bugs (each planted, its test shown to fail, then removed)

`docs/oom-rootcause/seed_faults.py` plants each one, runs its test (a Rust fault is built into the release
binary first), restores the source, rebuilds, and checks that the restored binary has the pinned hash. Saved
as `evidence/mutants.json` (file and test keys).

| # | Language | File | Bug | Failing test |
|---|---|---|---|---|
| 1 | Rust | `rust/ve-profile/src/search.rs` | the successor raises an entry whose suffix is already at its minima (`>=` for `>`) | `search::domain_size_tests::lazy_sizes_are_the_eager_order` |
| 2 | Rust | `rust/ve-profile/src/search.rs` | the search builds every domain-size vector up front again | `test_the_incidents_search_is_answered_within_a_small_budget` |
| 3 | Rust | `rust/ve/src/memory.rs` | the allocator charges nothing against the budget | `test_runaway_input_returns_resource_limit_within_the_budget` |
| 4 | Rust | `rust/ve/src/main.rs` | an exhausted jsonl case is answered without its id | `test_the_client_reads_an_exhausted_budget_as_resource_limit` |
| 5 | Python | `ve/backends/rust_jsonl.py` | the child starts without the address-space cap | `test_the_client_passes_the_budget_and_caps_the_address_space` |
| 6 | Python | `ve/backends/rust_jsonl.py` | the child gets the default budget, not the configured one | same |
| 7 | Python | `ve/backends/rust_jsonl.py` | a process started under another budget is reused | same |
| 8 | Python | `ve/backends/process_limits.py` | a one-shot runner starts without the cap | `test_one_shot_runners_run_under_an_address_space_limit` |
| 9 | Python | `ve/backends/process_limits.py` | a byte setting in non-ASCII digits is read as a number | `test_configured_bytes` |

No Lean product code changed, so there is no Lean seeded bug.

## 7. User-visible deltas

Recorded in `docs/oom-rootcause/DELTA.md`. One is covered by a standing ruling (R3). Four need a DRI signature.

## 8. Not done, hypotheses, follow-ups

- **Hypothesis, not proven:** the parent links of PIDs 1353080 and 2800679 (section 1). The difference in
  the time to the kill (18 min on 10-10, 9.5 min on 10-11) is consistent with about 4 min of Python work
  before the first search plus machine-load-dependent growth, but it was not measured at the incidents' load.
- **FOLLOW-UP (CPU, not memory):** a search can still spend CPU on size vectors it skips without counting
  them against `max_models` (no candidate subset, or a constant whose sort is empty). That CPU is bounded by the
  caller's timeout, not by a work budget. Charging skipped vectors would change `models_checked` on existing
  workloads, so it is left for a separate decision.
- **FOLLOW-UP (pilot speed):** the whole-UDHR `check_document` takes 39 min, and only 18.7 s of that is Rust.
  The rest is Python and Lean. Whole-document checks inside the pilot should stay off until that is
  profiled. The pilot prompt should also forbid raising `VE_RUST_TIMEOUT`. Every searched case is now
  memory-bounded, but a raised timeout still buys CPU.
- **FOLLOW-UP (pins):** `lean/checkers.lock` keeps earlier Rust digests (the regeneration tool's merge of
  both sides). main's runaway build 3ec83dee… stays allowed until someone prunes the pins.
- Processes that start the binary directly (tools/difffuzz, conformance/fuzz, tests) get the binary's own
  8 GiB budget but no RLIMIT_AS backstop. Only `rust_jsonl`, the production path, sets one.
- Not done (checklist 2): no limit−1/limit/limit+1 fuzz at byte granularity on the memory budget.
  Allocation sizes are not deterministic across builds. The tests bound the outcome instead: ResourceLimit
  at 32 MiB, an answer at 256 MiB and at the default.
- The machine-level containment (`manage-agents/iso.sh`, one systemd scope per job) predates this branch
  and is not part of it.

## 9. Gate

The commits are listed in `evidence/commits.txt` (`git log main..HEAD --no-merges`, taken before the last
two commits).

1. The first full gate on `ab00e274` was started in the background. The tool's two-hour limit stopped it
   during the Python suite at load ~110, and it left no result. It was restarted as a detached process
   under `iso.sh` (64G) with `--workers 8`.
2. The full gate on `ab00e274` (`evidence/gate-result-ab00e274-full.json`): 14,336 passed, 92 skipped,
   38 Rust tests passed, **3 failed**, all of them `tests/test_gate_integrity.py::test_interrupted_gate_cannot_record_pass[*]`.
   `--rerun-failed` on the same commit failed them again (`evidence/gate-result-ab00e274-rerun.json`),
   so R13 does not apply. The cause predates this branch. The test replaces `check_toolchains`, which
   puts the pinned Lean on the gate's PATH. `lake_outputs.drop_stale` (from rd-6b, `1fc602bd`) runs `lean`
   itself, so it found `lean` only through the real HOME's `~/.elan/bin`. That works in plain pytest, but
   under the gate's isolated HOME every parameter fails. It reproduces with code identical to main's when
   HOME and PATH are set the same way. Fix: the test also fakes `drop_stale` (commit "test_gate_integrity:
   fake Lake's trace check"). The file then passed 37/37 both ways, and the 79 files its change selects
   passed: 2,825 passed, 1 skipped, 83 xfailed.
3. The full gate on the final code, `ef36aece` (`evidence/gate-result.json`): **passed**. 14,339
   passed, 92 skipped, 0 failed, 38 Rust tests passed, every stage run (toolchains, Lean build, Lean
   audit, Rust build, cargo test, pytest). The commit that adds it changes only docs.
