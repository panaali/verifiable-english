# Lean-first batch 2: DELTA

Base `24ea9e45` (the head of batch 1), head `lean-first/b2`. Batch 2 of `docs/LEAN-FIRST-PLAN.md` (section 5.2
row 2; F2, F3 and F6 of section 4) and the rule-3 measurement (DRI answer 2/10). Deletions:
[`LEDGER.md`](LEDGER.md).

## What changed

- **Lean (F2).** The service keeps one piece of state, a content-addressed table of environment handles
  (`lean/VE/Service/Protocol.lean`, `Handles`). A request may register environments
  (`"environments": {digest: environment}`); each key must be the SHA-256 of its value's text (`registerOne`,
  theorem `registerOne_digest`), and the value is parsed by the restricted decoder one level shallower than a
  case, as it would be inside one. A case that names `environment_handle` and no `environment` is answered as
  the case with the registered environment in its place (`Handles.expand`, theorems `expand_hit`,
  `runRequest_ok`); every other case as before (`expand_plain`); English and `risk-eval` cases are never
  expanded (`expandCases_unexpanded`). A handle the table does not hold makes the request a bound
  `CheckerUnavailable` request error (`expand_miss`). The table holds at most 64 environments of 64 MiB in all
  and empties before it would exceed either. The handshake states the member and both bounds (`handles`), and
  the rendered schema pins them exactly. 7 new theorems, 2 restated (`runRequest_ok`, `respond_decoded` take the
  table); `lake build` passes; `lean/audit.py`: 389 files, 4,164 theorems, standard axioms only.
- **Python (F2).** `LeanService` sends each case whose `environment` is a JSON object by handle, registering the
  environments its process does not hold yet, and keeps the same table as the service (`_note`, with the
  handshake's bounds). A request with handles that the service answers with a request error, a missed handle
  among them, is sent again with its environments in its cases, exactly as before this batch, and that answer is
  the answer. Responses are checked against the cases with their environments, as before.
- **Python (F3).** `relay.decide_once` asks the same request of a service pool once (`background` uses it: the
  agent-policy harness asked 12,199 Background requests of a few environments). Batching the remaining
  single-case streams is open item O1.
- **Rust and Python (F6).** `ve jsonl` flushes each record; `rust_jsonl` keeps one persistent process per caller
  instead of one per call, and hashes the binary through `executable_sha256` instead of on every call.
- **Measurement (rule 3).** [`rule3.py`](rule3.py), record [`rule3.json`](rule3.json); below.

## Gate (section 5.1)

### Item 1: suite

Four chunks of `tests/` plus `tools/test_layer_policy.py` (`VE_NATIVE_PREBUILT=1`, `-n 12`, load 13-51), run
on the heads as they were reached: chunk 1 at `4be1f762` 2,242 passed, 2 failed (the broad-handler review and the
trust table: fixed in `73af3459`); chunk 2 at `73af3459` 4,558 passed, 1 failed (`test_hang_guards`: the
transport's reaping waits, reviewed in `6382098b`); chunk 3 at `6382098b` 1,760 passed; chunk 4 at `6382098b`
2,012 passed, 4 failed (`test_stage2_faults` Background cases: the memo answered for a swapped faulty pool; fixed
by scoping it to the pool, `e66df944`). The files of every failure pass on the fix. The final run on HEAD in a
clean worktree is in section "Final run".

Test changes are transport only: the shell fakes of the Rust checker read one line instead of reading to end of
input (a persistent process never sees it), the Rust deadline test injects its expired deadline through
`rust_jsonl._deadline` instead of `communicate`, the chunking test counts the requests of the texts sent with
handles, the handshake fake and assertions carry `handles`, and the route-case recorder records each case with
its environment. New: `tests/test_lean_handles.py` (27 tests). `tools/gate_collection.py --write`: 27 new IDs,
none removed. Outside pytest: `lake build`, `lean/audit.py --write`, `lean/VE/Route/frozen.py`,
`tools/lean_statements.py --check`, `tools/response_schemas.py --check`, `tools/trust_map.py` (0
unclassified), `tools/check_lean_imports.py`, `tools/check_python_layers.py`, `tools/check_rust_deps.py`,
`tools/relay_lint.py`, `tools/wire_contract.py --check` pass.

### Item 2: corpus A/B

**`tools/lean_first_diff.py`** (probe matrix under both authorities, the conformance fixtures under both, every
pilot document, the readings and discourse corpora), base and final head recorded at the same load:
**66,247 records per side, 66,247 identical**; `compare --delta delta.json` exits 0 with an empty delta
([`ab-compare.json`](ab-compare.json), [`delta.json`](delta.json)). An earlier pair of recordings (head
`e66df944`) had one record unavailable on both sides: the constitution pilot's
`run-20261004T1800Z/readings/s1.ve.md` hit the recorder's 600 s cap per document at load 30-60. Run alone with a
1,500 s cap, base and head printed byte-identical reports (632.7 s and 616.6 s wall); at the lower load of the
final pair both sides finished it with the same record.

**The F2 obligation** (section 4: for every request of the corpus, the answer with a handle equals the answer
with the environment re-sent; a miss is a bound request error, never a different answer): the A/B above runs
every corpus through the handle path at the head; `tests/test_lean_handles.py` compares, request by request, a
client with handles and one without over the conformance evaluation corpus (701 cases) and the recorded route
corpus (282 cases, every route mode), and checks the miss (a bound `CheckerUnavailable` request error, then the
same answer resent), forged registrations, eviction and the pool.

**Differential fuzzer** ([`difffuzz_ab.py`](difffuzz_ab.py), [`difffuzz.json`](difffuzz.json)): `--ci` and
`--deep 1` for the 14 date seeds 20260923-20261006, each in the base and the head checkout: all 15 pairs equal
(findings by signature, new signatures, baseline entries seen 280-351, none unreviewed, none not reproduced).
Seed 20261004 is the CI sample's seed and repeats it. **The baseline does not grow.**

### Item 3: deletion ledger

[`LEDGER.md`](LEDGER.md). `tools/relay_lint.py` passes.

### Item 4: latency

Quiet host (load 8), one warm service, the agent-policy environment ([`latency.py`](latency.py),
[`latency.json`](latency.json)):

| Per call | Base | Head |
|---|---:|---:|
| typing (`check` of `top`): Lean CPU p50 | 1.785 ms | 0.937 ms |
| typing: wall p50 | 2.420 ms | 1.395 ms |
| typing, 300 cases in one request: Lean CPU per case | 1.692 ms | 0.811 ms |
| `environment` mode: Lean CPU p50 | 1.642 ms | 0.821 ms |
| Rust typing call: wall p50 | 5.622 ms | 0.853 ms |

The interactive budget (p50 at most 2 ms of Lean CPU) holds at both. Harnesses, base and head run at the same
time:

| Workload | Base wall / CPU | Head wall / CPU | Results |
|---|---:|---:|---|
| agent-policy `check.py base`, `VE_AUTHORITY=lean`, head `d894e67d` (load 17-20) | 389.1 s / 815 s | 263.4 s / 587 s | identical (42/42, same policy summary) |
| the same, head `0ac28c7e` before `decide_once` moved to the relay (load 11-15) | 270.4 s / 582 s | 188.9 s / 446 s | identical |
| eligibility `run.py --no-write`, default authority (load 17-20) | 344.7 s / 197 s | 323.7 s / 156 s | identical (32/32 mutants) |

CPU is user plus system time of the process tree. Agent-policy policy phases at the final head: pairs 153.3 → 98.3 s,
rules 16.3 → 9.7 s, tool gaps 32.0 → 25.5 s. Call profile of the earlier pair ([`agent-policy-calls.json`](agent-policy-calls.json),
recorded with the plan's call recorder): Lean CPU 293.2 → 178.8 s, request bytes 542 → 191 MB, Rust wall 113.4 →
30.1 s over the same 22,533 Rust and 61,695 Lean requests. Under `VE_AUTHORITY=lean` the harness is still slower
than the plan's default-authority run (162 s at load 57-88); the remaining Lean CPU per call is environment
decoding (O2). No measured workload uses more Lean CPU than the base.

## Rule-3 measurement (for 15a and question 10)

[`rule3.py`](rule3.py), record [`rule3.json`](rule3.json) (load 19.5, one warm service, handles, 256 candidates
per request). Rust's own search of each query ran in the same process at the same time (the persistent checker).

**Rust enumerates, Lean evaluates.** Candidates in the generator's order (`ve.search._models`, the order
`search.rs` follows) go to Lean's evaluation route in batches; the first candidate Lean values as a countermodel
is the witness.

| Corpus | Queries | Candidates | Order, first witness, counts, exhaustion as Rust | Lean CPU (decoding / semantic) | Transport and client | Rust wall |
|---|---:|---:|---|---:|---:|---:|
| `conformance/search.json` searches | 28 | 69 | 26 of 28; the 2 others are the evaluation-budget fixtures (`search_budget_1`, `_3`): Rust stops at its budget, Lean has no budget to stop at | 0.022 s (0.014 / 0.007) | 0.034 s | 0.026 s |
| bluedot `document.ve.md` query (19 premises) | 1 | 10,000 (Rust: the same 10,000, `ResourceLimit` at `max_models`) | equal | 53.5 s (43.0 / 10.5), 5.3 ms per candidate | 7.3 s, 68 MB sent | 6.05 s |

- **Preservation.** Order, first witness, model counts and exhaustion are preserved wherever Lean can say:
  every search fixture and the bluedot query. **Charging is not**: Lean's evaluator has no work budget, so
  `ResourceLimit` at an evaluation budget and Rust's evaluation counts (23,781 on bluedot) have no Lean
  counterpart before 15a's metered evaluator; neither has non-vacuity.
- **Deadline.** The bluedot query costs 53.5 s of Lean CPU and 60.7 s of wall without enumeration (82 s with
  Python standing in for the enumerator) against Rust's 6.05 s and its 5 s default deadline: about 10 times
  Rust, at this transport. 80% of the Lean CPU is decoding: every candidate carries its whole model and is decoded
  with the environment again (the handle saves sending the environment, not decoding it). The semantic work alone
  (10.5 s) is 1.7 times Rust's whole search.
- **What this says for 15a.** A compliant evaluator that meets the deadline needs candidate batches that share
  one decoded environment and send models as deltas or as an enumeration Lean expands itself; the JSON route as
  it is does not. The plan's next step, an in-process compiled Lean interface, was **not investigated** in this
  batch (no `@[export]` exists; a new build artifact linked into the Rust crate). The DRI has the numbers for
  question 10.

**The provers replay through Lean per step** (certificate cohorts of `conformance/certificates.py`, 40 queries
from each of the three cohorts): 99 certificates, 303 prover steps in all (at most 7 per certificate). Python's
prover took 0.106 s (search and self-replay), its replay alone 0.044 s; Lean replayed the 99 whole certificates
in 0.064 s of CPU (0.126 s wall), median 0.56 ms each, against a per-request floor of 0.29 ms (median, the same
environment, a trivial request). From these parts a per-step design costs 0.33 s (one request per step, each node
replayed once: an incremental replay that does not exist) or 0.37 s (each step's request replays its prefix):
about 3 times the prover's own time. The cohorts are small formulas; the agent-policy harness's certificate
replays cost 16.6 ms of Lean CPU each in the plan's run (section 3.4), so a cohort of real prover workloads is
the measurement 15a still needs.

## Seeded bugs (build checklist 13)

Each was planted alone, made the named test fail, and was reverted ([`seeds.py`](seeds.py),
[`lean_seeds.py`](lean_seeds.py); the Lean seeds were built into `ve_service`, listed in the lock for the run and
rebuilt away; the build hash is back to the committed one).

| Seed | Behaviour | Caught by |
|---|---|---|
| S1 | every case is sent with the first environment's handle (client) | `test_handles_answer_the_evaluation_corpus_as_resending_does` |
| S2 | the client raises on a request error instead of resending | `test_a_missed_handle_is_resent_with_its_environment` |
| S3 | the client never empties its table (mirror of the eviction) | `test_the_client_mirrors_the_services_eviction` |
| S4 | a Rust process that timed out goes back to the idle list | `test_a_rust_process_that_times_out_is_killed_and_not_reused` |
| S5 | a Rust process is reused after its executable changed | `test_a_replaced_rust_executable_gets_a_new_process` |
| S6 | one `decide_once` memo shared by every pool | `test_lean_background_is_asked_once_per_request` |
| S7 | Lean registers a handle without checking its digest | the theorem `registerOne_digest` (build fails); with its proof stubbed, `test_a_registration_whose_key_is_not_its_digest_is_refused` |
| S8 | Lean expands a handle to the table's first environment | the theorem `expand_hit` (build fails); with its proof stubbed, `test_handles_answer_the_evaluation_corpus_as_resending_does` |
| S9 | Lean's table empties at 3 environments instead of 64 | `test_the_client_mirrors_the_services_eviction` (after it was strengthened to re-ask every handle the client believes held; the first version missed this seed) |

One further Lean seed, keeping `environment_handle` beside the expanded environment, fails `expand_hit` at build
time but no corpus test: no runner reads that member, so on every corpus it is an equivalent mutant.

## Changes for signature

| Id | Class | Change | Signature |
|---|---|---|---|
| D1 | `availability` (protocol) | A raw service request may carry `environments`, and a case may name `environment_handle` without `environment`: such a case is answered as the case with that environment, or the request is a bound `CheckerUnavailable` (a missed handle) or `InvalidInput` (a key that is not its environment's SHA-256) request error. Before, `environments` was an unknown request field (an unbound line error) and such a case was refused for its missing environment. No public `ve` input reaches either form: only the client writes them. The handshake gains `handles`; the client refuses a service without it. | DRI |
| D2 | none (operational) | The Rust checker is a persistent process: a call no longer checks a process exit status per record, a reused process that has ended is replaced once for the same call, and a process with output pending is never reused. Every corpus record is unchanged. | DRI |

## Open items

- **O1 (F3, partial).** The prover already types a document in one request (`check_document`); Background is
  now asked once per request. `evaluate()`'s typing and Lean evaluation calls remain one request per
  (formula, model), because its callers ask one at a time; batching them needs a batched public evaluation,
  which is the candidate-batch design 15a decides from the rule-3 record. Measured headroom: 0.81 ms against
  0.94 ms of Lean CPU and 0.85 ms against 1.40 ms of wall per typing case.
- **O2.** With a handle, 0.8 of the 0.94 ms of Lean CPU of a typing call on the agent-policy environment is
  still decoding the environment into the mode's own structures, once per case. A cache of decoded environments
  needs each mode's decoder to take it; it is also what the rule-3 search design needs.
- **O3.** The in-process compiled Lean interface the plan names after a failed batched transport was not
  investigated (rule-3 measurement above).
- **O4.** The certificate cohorts are small; a cohort of real prover workloads (agent-policy) for the per-step
  replay design is still to be measured.
- Not run: the plan's 1,000-document rights and soft-norm differentials (no statement-layer route changed beyond
  its transport; their cases ran through the handle path in the suite and the route corpus), and the UDHR
  pilot load (unchanged at batch 1's `CheckerUnavailable`; the A/B records it identical at base and head).

## Final run

Pending: written by the clean-worktree run of the full gate on HEAD.
