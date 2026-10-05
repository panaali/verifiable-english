# Lean-first batch 1: DELTA

Base `776a64d7` (the head of batch 0), head `lean-first/b1`. Batch 1 of `docs/LEAN-FIRST-PLAN.md` (section
5.2 row 1, F1 and F4 of section 4): every one-shot route executable becomes a mode of the one Lean service, its
callers switch to the service, and the duplicate transports and runners are deleted ([`LEDGER.md`](LEDGER.md)).

## What changed

- **Lean.** Twelve service modes, each the per-case function its one-shot executable mapped over a case
  array, pinned by an `rfl` theorem (`lean/VE/Service/Protocol.lean`, `runMode_*`): `soft-norms`, `rights`,
  `speech-acts`, `reports`, `alternatives`, `risk`, `risk-eval`, `quantity`, `norm-defaults`, `discourse`,
  `readings-route`, `diagnose` (`norms` was already a mode). `diagnose` reads the contract from the case's
  `unit` member (`VE/Service/Diagnose.lean`, `diagnoseCase_registered`); `risk-eval` reads its batch with
  `Lean.Json.parse`, as `ve_risk_eval` did. The 13 one-shot executables, their roots and the 13 `main` loops
  are deleted; `lean/.lake/build/bin` goes from 2,889 MiB to 693 MiB. `lake build` passes; `lean/audit.py`:
  276 source files, 3,058 theorems, standard axioms only (13 new theorems, `axioms.txt` regenerated).
- **Python.** The six bespoke transports of `ve/backends/lean.py` are deleted; soft norms, rights,
  readings, norm defaults, reports, alternatives, risk, discourse and W6 quantity admission reach Lean through
  `relay.decide` / `relay.rows` (and `lean.run` for the manifest bindings, which are now `ve_service` modes).
  Each request has a per-operation CPU deadline (F4, `lean_service.DEADLINES`). The client caches the service
  binary's SHA-256 beside it across processes (section 4: it cost every CLI process 0.19 s of CPU).
- **Policy.** `VE.Service.Diagnose` is the one service module allowed to import the diagnostic-only
  `VE.WireContract` (wire-contract spec 7.3; `tools/check_lean_imports.py`), in place of the deleted
  `DiagnoseMain` root. Statement review needed for the 13 new theorems (build checklist 17).

## Gate (section 5.1)

### Item 1: suite

The full suite (`tests/`, `tools/test_layer_policy.py`) ran at `c687b1b4`–`7e4f3a4c` in four interleaved
chunks (`VE_NATIVE_PREBUILT=1`, `-n 10`); its failures were fixed in `7e4f3a4c` and the re-run of those files
passed (one load-only failure, `test_w6a_limit_generator.py`'s three seeds, is Rust's flat 5 s JSONL limit at
load 40; they pass alone, as recorded before this batch). The changes after `7e4f3a4c` (the per-case deadline,
the digest cache, two tests) were run with their files; the final run is below.

**Final run at `74b5d2a9`** (four chunks, `-n 12`, load 25–41): 8,795 passed, 6 skipped, 2 failed; both failures
are load-only and pass alone (`test_precommit_hook.py::test_large_staged_change_stays_under_ten_seconds`, its
10 s bound; `test_w6a_limit_generator.py::…[0]`, Rust's 5 s JSONL limit), as recorded before this batch.
`test_gate_collection.py` passes after `tools/gate_collection.py --write` (8,768 IDs: 7 renamed with the
rebound manifest bindings, 31 new). Outside pytest: `lake build`, `lean/audit.py`, `lean/VE/Route/frozen.py`,
`tools/wire_contract.py --check`, `tools/check_lean_imports.py`, `tools/check_python_layers.py` and
`tools/relay_lint.py` pass.

Test changes are transport only (a route's executable became its service mode) except: `test_runner_errors`
(the `diagnose` mode answers an unknown unit with an error row where the one-shot exited 2; no usage error
exists), the manifest tests' one-shot-only fake runners (skipped for service bindings, whose forged rows are
checked directly), and the discourse and missing-executable tests (they fake the service, not an executable).

### Item 2: corpus A/B

**Gate-1 byte parity against the one-shot runners.** `tests/route_case_recorder.py` recorded every case the
suite sent to a route mode (155,479 distinct cases); [`route_parity.py`](route_parity.py) sent each through the
base's one-shot executable and the head's service mode in the same batches
([`route-parity.json`](route-parity.json)):

| Mode | Cases | Identical | Different | By design | One-shot CPU s | Service CPU s | One-shot wall s | Service wall s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| alternatives | 7,250 | 7,250 | 0 | 0 | 24.1 | 15.8 | 38.6 | 25.2 |
| diagnose | 3,766 | 3,764 | 0 | 2 | 27.7 | 29.1 | 50.3 | 94.8 |
| discourse | 6,399 | 6,399 | 0 | 0 | 25.4 | 18.9 | 130.1 | 89.0 |
| norm-defaults | 28,008 | 28,008 | 0 | 0 | 85.6 | 56.6 | 122.8 | 92.3 |
| norms | 5,474 | 5,474 | 0 | 0 | 9.5 | 3.2 | 18.3 | 10.4 |
| quantity | 31,870 | 31,870 | 0 | 0 | 105.1 | 70.1 | 146.3 | 144.4 |
| readings-route | 6,649 | 6,649 | 0 | 0 | 17.9 | 9.0 | 121.6 | 50.3 |
| reports | 8,265 | 8,265 | 0 | 0 | 45.7 | 36.0 | 73.6 | 56.9 |
| rights | 7,355 | 7,355 | 0 | 0 | 128.0 | 117.8 | 175.6 | 154.9 |
| risk | 23,120 | 23,120 | 0 | 0 | 6,912.0 | 6,874.1 | 8,933.3 | 12,973.8 |
| risk-eval | 203 | 203 | 0 | 0 | 0.8 | 0.8 | 1.0 | 1.6 |
| soft-norms | 16,328 | 16,328 | 0 | 0 | 122.3 | 115.7 | 319.4 | 363.0 |
| speech-acts | 10,792 | 10,792 | 0 | 0 | 23.9 | 12.9 | 32.8 | 31.5 |
| **all** | 155,479 | 155,477 | 0 | 2 | 7,528.2 | 7,360.0 | 10,163.7 | 14,088.1 |

Rows are compared as JSON values (keys sorted), every row of every batch. The tool exits 0 only on evidence
(lf-1 review B): a missing or empty recording, an unknown mode, a requested mode without a recorded case
or a missing one-shot executable exits 2 before anything runs, and a run that does not account for every
case sent exits 1 (`tests/test_route_parity.py`). `tools/lean_first_diff.py compare` likewise refuses the
same file twice and empty runs, and fails a missing corpus or one unavailable on both sides
(`tests/test_lean_first_diff.py`); the A/B above passes it (one pilot record, D2, is unavailable on both
sides). The other evidence tools of this class were fixed alike (`tests/test_evidence_tools.py`). The two by-design rows are `diagnose`
cases whose unit is missing or not a contract: `ve_diagnose` exited 2 for them (it could not be asked without
a unit); the mode answers each with an error row (D1 below). Wall times are summed over 12 parallel workers on
a host at load 20–40.

**`tools/lean_first_diff.py`** (probe matrix under both authorities, the conformance fixtures under both, and
every pilot document): 58,719 records per side, 58,718 identical, one listed difference
([`delta.json`](delta.json), [`ab-compare.json`](ab-compare.json)); `compare --delta` exits 0.

| Id | Record | Base | Head | Class |
|---|---|---|---|---|
| D2 | `pilots/default` `document_check` of the UDHR translation (`pilot/udhr-20261003T0600Z`) | `CheckerUnavailable: ve_readings_route is unavailable` (the one-shot's 120 s wall limit) | `CheckerUnavailable: the Lean service mode readings-route used more than its deadline of 228.599 s of CPU` (`operation`: `readings-route`) | the tool says `verdict` (pilot records compare stdout); both sides are unavailable, the head names the operation as F4 requires |

**Differential fuzzer** (`infra/difffuzz`, merged in scratch onto the base as `7d1872bf` and onto the head as
`7ac6be05`, whose only change to the fuzzer sends each one-shot route's batch, as the same text, to its
service mode): the CI sample and the 13 date seeds 20260921–20261003 (`--deep 1`) give identical reports on
both sides, run by run: the same new signatures (23 for the CI sample, 66–77 per seed), the same findings,
329 (CI) and 255–269 baseline entries seen, 80 not reproduced ([`difffuzz.json`](difffuzz.json)). No head-only
signature: **the baseline does not grow.** The fuzzer's child processes used 1,544 s of CPU against 2,089 s.

### Item 3: deletion ledger

[`LEDGER.md`](LEDGER.md). `tools/relay_lint.py` passes.

### Item 4: latency

- **Route calls.** In the parity run the service used less Lean CPU than the one-shots in 12 of 13 modes
  (diagnose +5%), 2.2% less in all: the per-process start-up the plan measured (F1, about 0.1 s of CPU per
  one-shot call) is gone. Wall time summed over the 12 workers is 39% higher, almost all of it the risk mode
  (+45%) and diagnose. A single-threaded sample of 192 risk cases gives one-shot 67.7 s CPU and 76.4 s wall,
  service 65.2 s CPU and 83.8 s wall, with 0.05 s of client CPU: the extra wall is not the client's response
  checks and is not explained yet (open item O1).
- **Documents** ([`latency.py`](latency.py), [`latency.json`](latency.json); `ve document check`, medians of
  5 alternating runs, process-tree CPU, load about 15–30): the constitution pilot's `readings/s1.ve.md` 5.44 s
  base, 5.09 s head; `readings/all-default.ve.md` 0.97 s base, 0.78 s head; outputs identical. Before the
  digest cache the head was slower (4.21 → 4.57 s and 0.80 → 1.00 s at a lower load): the service start
  (0.06 s) is cheap, the client's SHA-256 of the binary (0.19 s) was not.
- **Use-case harness.** `test_asimov_extended.py::test_rerun_equals_the_committed_results` (risk-route heavy,
  12 workers): 939 s wall and 8,612 s CPU at the base, 904 s and 7,583 s at the head. The agent-policy and
  eligibility harnesses passed in the suite; their timings were not taken separately.

## Changes for signature

| Id | Class | Change | Signature |
|---|---|---|---|
| D1 | `availability` (by design) | `diagnose`: a case without a unit, or with a unit that names no contract, gets an error row (`InvalidInput: a diagnose case names its unit`, `UnsupportedProfile: no wire contract <unit>`) where `ve_diagnose` exited 2 for the whole batch. Diagnostic only; no verdict depends on it. | DRI: signed 2026-10-04 |
| D2 | `verdict` by the tool, unavailable on both sides | the UDHR load's `CheckerUnavailable` names the readings route and its CPU deadline (F4) and arrives after 228.6 s of CPU instead of 120 s of wall | DRI: signed 2026-10-04 |
| D3 | `wording` (code) | a route rejection raised through the relay is the class of the service's public code (`UnsupportedProfile`, `UnknownSymbol`, …) with Lean's text; it was a plain `VEError` with code `InvalidInput` for the rights, reports and norm-defaults routes. A soft-norms rejection keeps its soft-norms@0 code as before. No corpus record changed (the A/B corpora reach these routes only through `ve document check`, whose outputs are identical). | DRI: signed 2026-10-04 |
| D4 | `availability` (operational) | `reports_route.run_case` without a build was `UnsupportedProfile: reports@0 needs the built ve_reports_route executable`; without the service it is `CheckerUnavailable` like every other route | DRI: signed 2026-10-04 |

## Open items

- **O1.** The service's wall time on heavy risk batches exceeds the one-shots' at equal or lower CPU (above).
  Candidates to measure: the 4 GiB address-space limit the supervisor sets, the heap of a long-lived process.
- **O2 (closed by the lf-1 review fixes).** Route modes' `ok` rows were checked for their binding only
  (`common.json` `route_ok`): an answer without `environment_prime`, or with every payload field removed,
  passed the relay and the caller raised `KeyError`. Every route mode's answers are now closed schemas
  (`ve/backends/lean_service_schema/<mode>.json`, each field the encoder writes, typed to the leaves, the
  route's own dispatch test as the selector) with `ve_response_decode` deciding the same responses with
  the runners' dispatch tests (`ResponseDecode.Routes`). `tests/test_route_row_schemas.py` runs a recorded
  corpus of every answer kind (`tests/data/route-cases.jsonl`, 248 cases) through the service: every
  genuine answer is accepted, every drop, empty and retype of every field (to depth 4) gets the same
  verdict from both sides, no alteration of a field leaves a valid answer, the review's three soft-norms
  mutants raise `CheckerUnavailable` through `relay.decide` and the public elaboration, twelve schema
  weakenings are each caught, and a lint fails any answer object left open (one allowance: E''s echoed
  predicate declarations). `norms.json`'s path now includes all four statement-layer profiles
  (`Plain.layered`); it named two. **One source (lf-1 recheck B):** the schemas and
  `ve_response_decode`'s checks were two hand-written descriptions. Every response shape is now Lean data
  beside the service (`lean/ResponseShape/Schemas/`, dialect `ResponseShape`): every file of
  `ve/backends/lean_service_schema/` is its rendering (`tools/response_schemas.py`; a hand-written,
  hand-edited, stale or missing file fails `tests/test_response_schemas.py`), `ve_response_decode` checks
  responses with the same shapes, each Lean decoder and route dispatch test decides beside the shape it
  names and must agree with it, and the enumerations with a Lean list (codes, modes, limits, acts,
  modalities, relations, generators, statement layers) are that list. The rendering equals the former
  files; ResponseDecode lost its 1,090 lines of per-mode checks.
- **O3.** Docs outside this batch (`lean/*.md`, `docs/spec/*.md`, `conformance/DIFFFUZZ.md` on its branch)
  still name the one-shot executables. `infra/difffuzz` needs the head's adapter (one function) when it merges.
- **O4.** HUMAN: statement review of the 13 new theorems (`runMode_*` for the twelve modes,
  `diagnoseCase_registered`).
