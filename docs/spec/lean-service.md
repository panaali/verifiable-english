# Lean service `ve_service` (semantics migration, stage 1)

**Status:** stage 1 of [SEMANTICS-MIGRATION-PLAN.md](SEMANTICS-MIGRATION-PLAN.md) as amended by the converged
review (`~/code/manage-agents/debates/semantics-migration/`): a persistent JSON-lines service over the
**existing** runners, with gate 1 restricted to one-shot/service equivalence on existing modes, protocol
faults, soak and service-call latency. The section-2.1 glue modes (`parse`, `check`, `graph`, …) are stage
2b. Nothing in `ve` calls the service yet; no Python semantics is switched.

## Components

| File | Role |
|---|---|
| `lean/Serve.lean` | executable root: handshake, then one flushed response line per request line until end of input |
| `lean/VE/Service/Protocol.lean` | request decoding, mode dispatch, budgets and counts, pin theorems; pure (`respond : String → Json`) |
| `lean/VE/Service/EnglishRun.lean` | generated copy of `VE/English/Run.lean` without its root `main` (see below) |
| `lean/VE/Service/english_copy.py` | generates the copy; `--check` fails on any drift (run by `tests/test_lean_service.py`) |
| `ve/backends/lean_service.py` | Python supervisor and client: `LeanService`, `LeanServicePool`, `CheckerUnavailable` |
| `tests/test_lean_service.py` | protocol, byte identity, protocol and supervisor faults |
| `tools/lean_service_{parity,soak,latency}.py` | gate-1 harnesses; results in `experiments/lean-service/` |

`lake build` now also builds `ve_service` and `ve_english_run` (root `VE.English.Run`, the one-shot English
reference the ve-bench harness already used).

## Protocol

Handshake (first line):
`{"lean":"4.24.0","limits":{"json_depth":256,"max_cases":4096,"max_line_bytes":16777216},"modes":[…],"protocol":1,"service":"ve-lean@1"}`.
The build identity is the SHA-256 of the executable, computed by the supervisor
(`LeanService.build`; `expected_sha256=` refuses any other build). Hashing 175 MiB in Lean at every start
would break the cold-start budget; a committed `checkers.lock` is stage-4 packaging.

Request (one line): `{"id": string, "mode": string, "cases": [...], "budget"?: {"cases"?: n, "bytes"?: n}}`.
Unknown or duplicate fields are rejected.

| Mode | Runner (pinned by `VE.Service.runMode_*`) | One-shot equivalent |
|---|---|---|
| `evaluate` | `VE.Order.runEvaluationCaseReported` | `ve_conformance` |
| `check-certificate` | `VE.CertificateWire.runCaseReported` | `ve_conformance check-certificate` |
| `order` | `VE.Order.Surface.runCaseReported` | `ve_conformance order` |
| `route` | `VE.Route.Run.runCaseReported` (definitions, bundles, background, admission, labels …) | `ve_conformance route` |
| `norms` | `VE.Norms.Run.runCaseReported` | `ve_norms_route` |
| `english` | `VE.English.ServiceRun.run` on each case object | `ve_english_run` / `lake env lean --run VE/English/Run.lean` |

Response: `{"counts":{"bytes","cases","errors"},"id","mode","results":[…],"status":"ok"}` (keys in Lean's
sorted order). `results[i]` is exactly the one-shot runner's output for case `i` of this request, including
the per-case depth record `{"case_index", "error", "status"[, "valid"]}`, whose `case_index` is the position
in this request, as in a one-shot batch. A whole request that cannot be answered gets one line error
`{"error","id","status":"error"}`: malformed envelope (`id: null` when the id cannot be read), unknown mode,
a batch the restricted decoder rejects (the one-shot exit-2 message, verbatim), or a budget. Processing
continues with the next line; no state is kept between lines. Blank lines are ignored.

**JSON.** The envelope is split into top-level members by a small scanner (`objectMembers`, the same quote,
escape and depth tracking as `VE.JsonInput`'s batch splitter); `id`, `mode` and `budget` are decoded by
`VE.JsonInput.parse` and the `cases` text by `VE.JsonInput.parseCases`, the one-shot batch decoder. No second
JSON parser is introduced.

**Budgets and counts (deterministic).** A request's cases text may not exceed `budget.bytes` and its case
count may not exceed `budget.cases`; both default to and are capped by the service limits (16 MiB, 4,096
cases). Exceeding either is a `ResourceLimit:` line error, decided from the request alone. `counts` reports
the cases, the bytes of the cases text and the error results. The reference runners have no work budget
and none is added (that would change checker code); work budgets for evaluation and search are Rust's
(plan section 2.1).

**Memory.** Lines are read with `getLine`, whose cost is linear in the line; a line over 16 MiB is rejected
with one error record after it is read, and processing continues. The byte-wise alternative that never
holds an over-long line costs 1.07 s per 4 MiB against 0.07 s, and `Handle.read n` blocks until `n` bytes
arrive, so a chunked reader cannot serve interactive requests. The hard bound is the supervisor's
address-space limit (4 GiB): a line too large to hold kills the process, which the supervisor reports as
`CheckerUnavailable`. The client never sends a line over 16 MiB.

### Deviations from the one-shot executables (all in the English mode)

1. The English one-shot runner decodes its input with `Lean.Json.parse`; the service decodes every case with
   the restricted decoder first (the plan's rule), then passes the canonical re-encoding to the runner.
   Inputs with `null`, fractions, exponents or duplicate keys are therefore rejected as a batch, where the
   one-shot runner would accept some of them. Accepted inputs give identical results.
2. An English failure is the record `{"error": <message>, "status": "error"}` instead of the message on
   stderr with exit 2.
3. `VE/English/Run.lean` declares a root `main`, so an executable with its own `main` cannot import it, and
   the file may not be edited. The service uses `VE/Service/EnglishRun.lean`, the original text with the
   namespace renamed `VE.English.ServiceRun` (still inside `VE.English`, so every identifier resolves as in
   the original) and the `main` omitted; `english_copy.py --check` pins it byte for byte. The English
   runner is a harness entry point on which no theorem depends; the copy is listed for statement review.

## Supervisor (`ve/backends/lean_service.py`)

- Each request carries a fresh nonce id; a response with another id, a malformed or short response, a
  timeout (5 s interactive default, 60 s for batch callers), a crash, end of output or a bad handshake is an
  operational failure: the process is killed and the batch retried once on a fresh process; a second
  failure raises `CheckerUnavailable` (code `CheckerUnavailable`, never `ResourceLimit`, never a verdict). No
  fallback to Python. Cancellation is out of band only (the kill).
- A line error from a healthy service is deterministic: `ResourceLimit` for budgets, otherwise `VEError`; the
  process stays up.
- `RLIMIT_AS` 4 GiB on the child (`prlimit`, or `setrlimit` before exec where `prlimit` is missing);
  recycling after 10,000 requests or above 2 GiB RSS; `LeanServicePool` (default 2 processes).
- `run(mode, cases)` splits at 256 cases or 4 MiB per request (the plan's adapter caps); each request is one
  timeout unit. `exchange(mode, cases_text, n)` sends one request and returns the raw line.

## Statement review list (new Lean glue)

- `lean/VE/Service/Protocol.lean`: every definition, and the theorems `runMode_evaluate`,
  `runMode_checkCertificate`, `runMode_order`, `runMode_route`, `runMode_norms`, `runMode_english` (each
  mode is its runner, by `rfl`), `caseResult_ok` (a decoded case gets `runMode`), `runRequest_ok` (a request
  within budget whose cases decode is answered with `response`), `results_eq` (result `i` is `caseResult`
  of case `i`). Trusted and not proved: `objectMembers`, `decodeRequest`, and the restricted decoder.
- `lean/VE/Service/EnglishRun.lean`: generated copy (deviation 3).
- `lean/Serve.lean`: IO loop.
- `lean/VE/Audit.lean`: one import and nine `#print axioms` lines. `lean/lakefile.toml`: two executables.
- No file under `lean/VE/` other than `Audit.lean` changed; `VE/Route/frozen.py` passes.

## Gate 1 evidence (2026-09-27, AMD EPYC 7B12, 8 logical CPUs)

The machine was **not quiet**: other sessions' test suites held the load average at 5–7 throughout. The
latency figures are therefore upper estimates; the plan's gate figures need a rerun on a quiet machine
(`tools/lean_service_latency.py`, `tools/lean_service_soak.py`).

| Criterion (gate 1 as amended) | Result | Evidence |
|---|---|---|
| Byte-identical to the one-shot executables on existing modes | **16,552 / 16,552** cases identical, 0 restarts: every committed runner fixture (evaluation, countermodels, parser, identity, validation, closure, route-cases, v0 replay baseline), the P1, closure-induction and iceberg replay queries, the definitions (2,000), n-ary core (747), DAG (200), norms (1,100) and English (17 vocabularies, about 3,400 pairs) differential generators, the prover-backed certificate, closure, induction and order generators with their forged sets, adversarial and batch-rejecting inputs for every mode | `experiments/lean-service/parity/` |
| Fault injection fails closed | kill between and during a batch (one retry succeeds), hang, crash, garbage, truncated output, wrong id, short response, bad or missing handshake → `CheckerUnavailable` after one retry; over-long (16 MiB + 8) line, truncated line, malformed envelopes → one error record each, processing continues | `tests/test_lean_service.py` (23 tests) |
| Soak | 20,000 mixed-mode requests (1–8 cases each) on one process in 70.5 s: 0 mismatches, 0 restarts, RSS 96.1 MB at request 1,000 → 101.0 MB at 20,000 (+5.1%, one step near request 5,000, then flat) | `experiments/lean-service/soak/` |
| Service-call latency (median ≤ 5 ms, p95 ≤ 20 ms; 2,047-node certificate p95 ≤ 200 ms) | met on every workload: ordinary medians 0.60–1.70 ms, p95 1.18–4.86 ms; large certificate p50 30.9 ms, p95 45.7 ms; mixed soak p50 2.57 ms, p95 7.85 ms, p99 12.0 ms | `experiments/lean-service/latency/` |
| `audit.py`, frozen hash test | PASS (129 files, 889 theorems, standard axioms only); `frozen.py` PASS | |

Persistent against one-shot, per call (p50 / p95 ms, persistent timed at the Python boundary):

| Workload | Persistent | One-shot |
|---|---:|---:|
| tableau certificate | 0.97 / 1.45 | 84.5 / 116.0 |
| 2,047-node tableau certificate | 30.9 / 45.7 | 78.4 / 115.6 |
| closure certificate | 1.28 / 2.43 | 86.0 / 98.2 |
| order/Farkas certificate | 1.25 / 2.00 | 69.3 / 109.1 |
| finite-model evaluation | 0.78 / 1.50 | 65.4 / 90.0 |
| W1 norm elaboration | 0.62 / 1.51 | 79.6 / 92.4 |
| W1 conflict check | 1.70 / 2.75 | 75.6 / 84.3 |
| W3 definitions | 1.39 / 4.86 | 81.1 / 131.5 |
| W3 bundle | 1.66 / 2.82 | 84.1 / 104.6 |
| English parse | 0.60 / 1.18 | 55.5 / 82.6 |
| English admission | 0.65 / 1.45 | 56.1 / 82.5 |

Cold start (spawn to handshake): p50 53.8 ms, p95 91.3 ms.

**Not met, and not gate 1:** the section-4 batch gates. Under the same load, 2,048 definitions took 2.23 s
through the client against 1.94 s one-shot (gate 1.0 s); 256 bundles 0.32 s against 0.24 s (gate 0.25 s);
256 conflicts 0.32 s (gate 0.5 s, met); 8 large certificates 0.34 s against 0.33 s (gate 0.3 s). The time is
the runners' own work (about 0.55 ms per definitions case); a single pre-encoded 2,048-case request measured
1.19 s against 1.16 s one-shot at lower load, so the service adds little, and the client adds Python
encoding and decoding. The batch rows belong to gates 2–4 and need a quiet-machine measurement; if they still
miss, the cost is in the runners, which stage 1 does not change.

## Left for later stages

- `checkers.lock` and refusal of unlisted builds by default (stage 4 packaging; `expected_sha256` exists).
- The section-2.1 glue modes and identities (stage 2b), adapters (2a), end-to-end and pilot latency (gates 2–4).
- The plan's full latency method (≥ 20,000 requests from the assist ledgers, three sessions, quiet machine).
