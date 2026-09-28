# Lean service `ve_service` (semantics migration, stage 1)

**Status:** stage 1 of [SEMANTICS-MIGRATION-PLAN.md](SEMANTICS-MIGRATION-PLAN.md) as amended by the converged
review (`~/code/manage-agents/debates/semantics-migration/`): a persistent JSON-lines service over the
**existing** runners, with gate 1 restricted to one-shot/service equivalence on existing modes, protocol
faults, soak and service-call latency. The section-2.1 glue modes (`parse`, `check`, `graph`, …) are stage
2b. Nothing in `ve` calls the service yet; no Python semantics is switched.

## Threat model (design directive 3)

**The Lean service is the semantic authority.** It is trusted: its dispatch is pinned to
the existing runners by the `runMode_*` theorems, the runners carry the Lean proofs, and
the service's outputs are covered by parity with the one-shot executables and with
Python's independent regenerations. The Python client does **not** re-derive semantic
content.

**The client guarantees binding and integrity.**

- Every response echoes the request's nonce (`id`) and `mode`.
- Result `i` is `{"digest", "index": i, "result"}`, where `digest` is the SHA-256 of the
  text of case `i` as the client sent it (split from the `cases` array and trimmed of
  JSON whitespace; `VE.Service.caseDigest`, `ve.backends.lean_service.case_digest`). The
  client computes the digest of every case it sends and compares.
- Each result also carries the identity fields the runners echo from its case, and the
  client compares them with the case: the case `id`, the requested label and witness
  target, the admission root and unit kinds, the requested lemmas' meaning ids, one value
  per requested formula and one English result per requested case.
- An omitted, reordered, duplicated or substituted result is therefore rejected by
  binding, not by semantic re-checking.
- Every field must be well formed: the Lean decoders' domains (formula, term and kind
  grammars with their fuel, labels, tokens, enumerations; `ve/backends/lean_service_schema/`).
- A malformed envelope, a binding mismatch or a malformed field is a protocol fault. The
  client kills the process and retries once on a fresh one; a second fault raises
  `CheckerUnavailable`.

**Content that preserves binding is the service's responsibility.** The client does not
check such content. Examples:

- the conflict targets inside one norms result (their distinctness, completeness and
  argument sorts);
- the Background premises, layers and counts regenerated from the environment;
- the admission assumptions (the root's unfolding);
- the validity of a dependency order;
- the conjunction of evaluation values;
- whether a verdict carries a detail;
- the consistency of an English check with its rendering.

These are tested on the service's outputs instead:

- `ve_response_decode`'s `invariants` check (`lean/ResponseDecode.lean`) must accept every
  genuine response of the test corpus, and must reject each content corruption found by
  the rechecks.
- The service's norms layers, premises and conflict targets must equal Python's
  regeneration (`ve/norms.py`) over the three-way corpus
  (`tests/test_lean_service_schema.py`).
- The full parity run compares every result with the one-shot runner byte for byte.

The rule for the boundary: a value the client can read directly off its own request is
binding and is checked. A value the client would have to compute with VE's semantics is
content and is not checked.

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
`{"lean":"4.24.0","limits":{"json_depth":256,"max_cases":4096,"max_line_bytes":16777216},"modes":[…],"protocol":2,"service":"ve-lean@1"}`.
Protocol 2 binds results to cases (below); the client refuses protocol 1.
The build identity is the SHA-256 of the executable, computed by the supervisor.
By default the hash must be in `lean/checkers.lock`; `expected_sha256=` pins an explicit
build and `allow_unlisted_build=True` is an explicit development override. Hashing
175 MiB in Lean at every start would break the cold-start budget.

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
sorted order). `results[i]` is `{"digest","index":i,"result"}`: `result` is exactly the one-shot runner's output
for case `i` of this request, including the per-case depth record `{"case_index", "error", "status"[, "valid"]}`,
whose `case_index` is the position in this request, as in a one-shot batch. `digest` is the SHA-256 (lowercase
hex) of the text of case `i` as split from the request by `VE.JsonInput.caseTexts` and trimmed of JSON
whitespace (`VE.Service.caseDigest`). `counts.errors` counts the results whose `result.status` is `error`. A whole request that cannot be answered gets one line error
`{"error","id","status":"error"}`: malformed envelope (`id: null` when the id cannot be read), unknown mode,
a batch the restricted decoder rejects (the one-shot exit-2 message, verbatim), or a budget. Processing
continues with the next line; no state is kept between lines. Blank lines are ignored.

**JSON.** The envelope is split into top-level members by a small scanner (`objectMembers`, the same quote,
escape and depth tracking as `VE.JsonInput`'s batch splitter); `id`, `mode` and `budget` are decoded by
`VE.JsonInput.parse`. The non-English modes decode `cases` with `VE.JsonInput.parseCases`, the one-shot batch
decoder. English decodes its cases array with `Lean.Json.parse`, the decoder of its one-shot runner. This
English exception resolves the Gate 1 acceptance conflict: the service accepts `null`, fractions, exponents
and duplicate keys in English payloads that the runner accepts. The envelope remains restricted.

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

1. The English one-shot runner decodes its input with `Lean.Json.parse`; the service decodes the English cases
   array with that parser, then passes each case's canonical re-encoding to the runner. The envelope stays
   restricted. This is the narrow exception to the plan's restricted-decoder rule required by Gate 1's
   equivalence for runner-accepted English payloads.
2. An English failure is the record `{"error": <message>, "status": "error"}` instead of the message on
   stderr with exit 2.
3. `VE/English/Run.lean` declares a root `main`, so an executable with its own `main` cannot import it, and
   the file may not be edited. The service uses `VE/Service/EnglishRun.lean`, the original text with the
   namespace renamed `VE.English.ServiceRun` (still inside `VE.English`, so every identifier resolves as in
   the original) and the `main` omitted; `english_copy.py --check` pins it byte for byte. The English
   runner is a harness entry point on which no theorem depends; the copy is listed for statement review.

## Supervisor (`ve/backends/lean_service.py`)

- Each request carries a fresh nonce id; a response with another id or mode, a result not bound to its
  case (position or digest), a malformed or short response, a
  timeout (5 s interactive default, 60 s for batch callers), a crash, end of output or a bad handshake is an
  operational failure: the process is killed and the batch retried once on a fresh process; a second
  failure raises `CheckerUnavailable` (code `CheckerUnavailable`, never `ResourceLimit`, never a verdict). No
  fallback to Python. Cancellation is out of band only (the kill).
- Response shapes have one source: `ve/backends/lean_service_schema/` (one JSON schema file per mode plus the
  envelope and shared Lean value domains; dialect in its `README.md`). `ve/backends/service_schema.py`
  compiles it; the supervisor has no other shape checks. Following the threat model, the schemas hold binding
  and well-formedness only. The binding is the nonce, the mode, each result's position and case digest, and the
  identity fields echoed from the case: `id`, the requested label and witness target, the admission root and
  unit kinds, the requested lemmas' meaning ids and `checked`, one value per requested formula, one result per
  English case. The well-formedness is the Lean enumerations (kinds, acts, modalities, relations, generators,
  verdicts) and the Lean decoders' grammars and fuel (formula and term depth 64, kind depth 16; generated
  formulas at any depth). A response outside them is an operational failure.
- `lean/ResponseDecode.lean` (`ve_response_decode`, test tooling outside `VE/`, no theorems) has two checks.
  `decode` reads responses with the Lean decoders and runner dispatch, and is the schemas' differential oracle.
  `invariants` checks the content the client leaves to the service, as listed in the threat model.
  `tests/test_lean_service_schema.py` has these requirements:
  - the schemas and `decode` accept every genuine response over a corpus with every mode and result kind;
  - they agree on every mutation of those responses: dropped, altered, retyped, enum-swapped, truncated and
    extra fields, bindings included; joint request/result mutations; altered requests; kind, label, depth and
    numeral probes;
  - each of 16 weakenings of the schemas is caught, including dropping the digest or the index check;
  - `invariants` accepts every genuine response and rejects each content corruption of the rechecks, which the
    client accepts.
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
  within budget whose cases decode, one per case text, is answered with `response`), `results_eq` (result `i`
  is `caseResult` of case `i`), `boundResults_eq` (bound result `i` is `caseResult` of case `i` with position
  `i` and the digest of case text `i`). Trusted and not proved: `objectMembers`, `decodeRequest`, the
  restricted decoder, and `Sha256.digest`. `Sha256.digest` is pinned by `#guard`s to the FIPS 180-4 vectors
  and to `VE.CertificateWire.sha256` on 130 inputs, and by the client comparing it with Python's `hashlib`.
- `lean/VE/Service/EnglishRun.lean`: generated copy (deviation 3).
- `lean/Serve.lean`: IO loop.
- `lean/VE/Audit.lean`: one import and ten `#print axioms` lines. `lean/lakefile.toml`: two executables, and
  the untrusted test oracle `ve_response_decode`.
- No pre-existing trusted checker module under `lean/VE/` changed during stage 1;
  `VE/Route/frozen.py` now pins all 124 VE Lean modules.

## Gate 1 review follow-up (2026-09-27)

| Criterion | Result | Evidence |
|---|---|---|
| One-shot/service equivalence | 16,556 / 16,556 cases identical across all six modes, including English `null`, fractional, exponent and duplicate-key payloads; zero restarts | [Full parity](../../experiments/lean-service/parity/PARITY.md) |
| Protocol and supervision faults | 42 focused tests pass: malformed responses, startup EOF and invalid handshakes retry and clean up; unlisted executables are refused by default; malformed and binary request lines receive an error and processing continues | `tests/test_lean_service.py` |
| Three-session soak | 60,000 mixed-mode requests, zero mismatches and restarts; worst RSS growth 5.24% against the 10% gate | [Session summary](../../experiments/lean-service/soak/SESSIONS.md) |
| Service-call latency | On the measured 95% confidence upper bounds: ordinary p50 at most 2.039 ms (gate 5 ms), ordinary p95 at most 4.198 ms (gate 20 ms), large certificate p95 50.645 ms (gate 200 ms). First 100 warmup calls and 20 separate cold starts reported; 30 repetitions per batch. | [Latency run](../../experiments/lean-service/latency/LATENCY.md) |
| Source and theorem guards | `lake build`, 889-theorem `audit.py`, generated English-copy check and hashes over all 124 VE Lean modules pass | `lean/audit.py`, `lean/VE/Route/frozen.py` |

**Quiet-machine condition remains open.** The 1-minute load average was 3.15–4.85 at the start of these timing runs on 8 logical CPUs, and rose as high as 5.70. The measured upper bounds meet the numerical targets under this contention; the plan also calls for a quiet host. A quiet-machine rerun or explicit gate acceptance is still required.

The section-4 batch targets are separate from Gate 1. In the latest 30-repetition run, 2,048 definitions took a 1.197 s median against a 1.0 s target and 8 large certificates took 0.310 s against 0.3 s. The other two batch medians were within their targets. These rows remain work for later gates.

## Left for later stages

- The section-2.1 glue modes and identities (stage 2b), adapters (2a), end-to-end and pilot latency (gates 2–4).
- The plan's later assist-ledger latency method under `VE_AUTHORITY=lean` and a quiet-machine Gate 1 timing rerun.
