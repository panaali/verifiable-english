# Semantics migration plan: compiled Lean as the single semantic authority

**Status:** plan for the lead's decision, 2026-09-27. No code or proofs change with this document.
Inputs: `~/code/ve-bench/bench/ANALYSIS.md` and `results-full/REPORT.md` (commit `5c20b6b`),
[implementation.md](../implementation.md), [verification-contract.md](verification-contract.md),
[conformance/README.md](../../conformance/README.md), [INTEGRATION-GAPS.md](../INTEGRATION-GAPS.md).

## 0. Decision and scope

The benchmark gives no performance reason to keep three implementations of the same semantics. Every ordinary
compiled-Lean check meets the 200 ms target even one-shot (47–152 ms medians, startup included), batches run
2–30x faster than Python, and Rust is the only runtime that matters for countermodel search (22,145 searches/s,
18.2x Python) and hot evaluation (2.0x Lean). Python's checkers are 1–12 ms warm, so a naive switch would slow
interactive checks; the persistent service in stage 1 removes that objection first.

Target architecture: **Lean decides** (parsing acceptance and canonical text, typing, environment and model
validity, evaluation verdicts, countermodel validity, certificate replay, Background and definition
elaboration, norm elaboration and conflict verdicts, admission, labels, bundles). **Rust searches and evaluates
fast** (countermodel and distinguishing-model search, budgeted evaluation, traces); every Rust witness is
validated by Lean before it is reported. **Python keeps the surface** (English, five views, documents, IDE and
`ve assist`, web app, CLI, harnesses, adapters) and **proof generation** (tableau, order, closure-induction and
norm searches), all untrusted producers whose output Lean checks. Nothing in this plan changes a proved checker
module, a frozen wire identity or an artefact identity; only `checker_build` and the record ids derived from it
change, by design.

## 1. Inventory of `ve/` (19,051 lines, 70 modules)

### 1.1 Semantic duplicates: authority moves to Lean (search and hot paths to Rust), code deleted in stage 5

| Python | Lines (semantic part) | Lean authority today | Rust role | Kept after stage 5 |
|---|---:|---|---|---|
| `ast.py` `_Checker`, `check_formula/document` | ~200 of 468 | `Formula.check` via `Bridge.decodeFormula` | typed `Document::check` | constructors, wire encode/decode |
| `environment.py` semantic validation | ~250 of 366 | `Bridge.decodeEnvironment`, `Route/Gate`, `Route/Wire.decodeVocabulary` | decodes | structural decode for display, `environment_id` |
| `model.py` validation | 189 | `Bridge.decodeModel` (proved admissible), Background validity | decodes, validates | container, `model_id` |
| `evaluate.py` | 232 | `Document.eval` (P6) | budgeted evaluation, traces (new) | nothing |
| `search.py` `check_countermodel` | ~110 | `countermodelCheck` (P11) | | nothing |
| `search.py` `find_countermodel`, `find_distinguishing_model`, non-vacuity filters | ~460 | none (search is not a checker) | search, extended in stage 2 | nothing |
| `entailment.py` `check_entailment_certificate` and replay internals | ~350 of 711 | `Tableau.checkCertificate` (v0, closure, core) | | `prove_entailment` searcher |
| `closure.py` replay side | ~120 of 244 | `Closure/*`, `TableauClosure` | | induction derivation for search |
| `order.py` `replay_trace` | ~350 of 741 | `Order/Tableau.checkCertificate` | evaluates order models | `search` |
| `background.py` generators, `validate_background`, `dependency_order` | 201 | route `background`, `dependency-order`, model validity | regenerates Background | `Premise` type |
| `definitions.py` | 165 | `Definitions/*` via route `background` | defined tables | nothing |
| `norms.py` generated premises, conflict targets, `check_conflict`, `check_witness`, certificate replay | ~300 of 409 | `ve_norms_route` `norms-elaborate`, `norms-conflict`, `norms-certificate` | evaluates generated formulas | `NormDocument` surface object, `prove_norm_entailment` |
| `norm_admission.py`, `admission.py` | 599 | norms `admission`; route `admission`, `label` | label grammar, DAG order | nothing |
| `bundle.py` Python replay | ~100 of 191 | route `bundle` (`bundle_sound`) | | Lean call only |
| `profiles.py` `checker_family` | 66 | `Route/Gate` (`route_gate`) | envelope gate | static routing table |
| `parser.py` (strict surface) | 396 | `Surface.parse` (P4/P5) | `parse` with spans and diagnostic classes | nothing |
| `printer.py` canonical `print_document/formula` | ~150 of 861 | `Surface.print` (`canonical` field) | byte-identical printer | view renderers only |
| `argument.py` per-edge replay and countermodel checks | ~250 of 725 | per edge via `check-certificate`/route (today optional `lean_executable`) | | graph and composition orchestration |

About 5,000 lines, a quarter of the package, are duplicate semantics.

### 1.2 Orchestration: stays in Python, calls the authorities, has no semantics of its own

`check.py`, `vacuity.py`, `equivalence.py`, `readings.py`, `document.py` (format plus admission and premise
report), `argument.py` graph validation, composition and displays, `identity.py` and `wire.py` (spec-pinned
RFC 8785 subset and SHA-256; Lean recomputes every binding it accepts and rejects mismatches), `errors.py`,
`limits.py`, the `ve` package API.

### 1.3 Surface, authoring, IDE, CLI, harness: unchanged by this plan

`english.py`, `fluent.py`, `natural.py`, `english_vocabulary.py`, `english_phrases.py`, `surface/*` (registry,
Earley all-derivations check, definitions and norms English, data and n-ary sugar), `norm_english.py`,
`norm_strict.py`, `grammar.py`, `lexicon/`, `propose.py`, `authoring.py`, `fol.py`, `openterms.py`,
`adapters/*` (Cedar, Gatekeeper, records, attributes), `printer.py` views, legend and lint, `assist/*`
(`ground.py` is a search whose witnesses are already re-checked; an optional Rust port), `attacks.py`,
`stream_audit.py`, `argument_fixtures.py`, `__main__.py`, `ve_experiments/`, `experiments/`, `conformance/*.py`
generators, `tools/`, and `ve_webapp` in `~/code/ve-webapp`. Surface desugaring (English, data sugar, norm
blocks to norm objects) stays outside Lean's authority exactly as today; the W7 round-trip proof is the
separate remedy.

## 2. What Lean and Rust lack today

| Python behaviour | Lean | Rust | Plan |
|---|---|---|---|
| Long-running process | one-shot, reads all of stdin, 16 MiB cap | `jsonl --flush` | stage 1 service mode |
| Deterministic work budget, `evaluations` count, 10,000-node trace budget | none; reference evaluator is unbudgeted | 1,000,000-unit budget, not byte-identical | Rust owns budgets and counts; Lean owns verdicts under wall-clock and memory bounds |
| Explanation trees | none | none | Rust `--trace` with the Python schema; fallback: Python tree demoted to display, root value must equal Lean's |
| Search options `min_domain_size`, `nonempty_domains`, `nonvacuous_for`, `semantic_nonvacuity`, distinguishing models | none | absent | extend Rust; Lean validates every witness |
| Parse diagnostics with codes and spans | failure is `none` | pinned by `parser.json` (742 cases) | Rust diagnoses rejections, Lean decides acceptance and canonical text |
| Norms with definitions or data flags | `UnsupportedProfile` | declarations only | close in Lean before stage 4 or accept with measured pilot impact |
| Admission on closure and order families, admission with definitions, closure bundles, citations without a bundle binding | deferred | n/a | same treatment, one decision per item |
| `ve-argument-tableau@1` graph package | `ClaimGraph` for Lean's own representation | none | Python orchestrates, Lean checks every edge; Lean decoder stays a PLAN-EXPAND2 §7 item |
| English surface | v0 unary/binary core skeleton, pretokenised | none | stays Python by decision |

## 3. Stages and gates

### Stage 1: persistent Lean service (1–1.5 weeks)

Build one new executable `ve_service` from a new `lean/Serve.lean` that imports the existing runners
(`VE.Order.runEvaluationCaseReported`, `VE.CertificateWire.runCaseReported`, `VE.Order.Surface.runCaseReported`,
`VE.Route.Run.runCaseReported`, `VE.Norms.Run.runCaseReported`, `VE.English.Run.run`). No file under `lean/VE/`
changes; the P0 hash test is extended to all of them. Protocol: one JSON object per line,
`{"id", "mode", "case"}`, modes `evaluate`, `check-certificate`, `order`, `route`, `norms`, `english`; one
response line `{"id", "result"}` whose `result` is byte-for-byte the existing runner output; first line is a
handshake `{"service": "ve-lean@1", "lean": "4.24.0", "build": <sha256>, "modes": [...]}`; 16 MiB per line as
in Rust; a malformed line yields one error record and processing continues; no state between requests. The glue
is pinned by six `rfl` theorems `dispatch m j = <runner> j`, so the statement review reduces to reading those
six lines, and `audit.py` covers them. Bounded resources come from the Python supervisor
(`ve/backends/lean_service.py`): address-space limit (default 4 GiB), per-request timeout (5 s interactive,
60 s batch), restart on timeout, crash, EOF or protocol error, recycle after N requests or an RSS threshold,
small pool, nonce ids that must match. A service failure is reported as `CheckerUnavailable`, a new operational
code; it never becomes a verdict and never falls back to Python.

**Gate 1.** Byte-identical results against the one-shot executables on every conformance fixture and report
generator; a 20,000-request mixed-mode soak with RSS growth under 10% and no restarts; fault injection (kill,
hang, garbage output, truncated line) fails closed; `audit.py` and the hash test clean; on a quiet machine,
median ≤ 5 ms and p95 ≤ 20 ms per ordinary bench case through the service, p95 ≤ 200 ms for the 2,047-node
certificate.

### Stage 2: Python adapters (3–4 weeks, overlaps stage 1)

New package `ve/backends/` with `lean_service.py`, `rust_jsonl.py`, `dispatch.py` (flag
`VE_AUTHORITY=python|shadow|lean`, default `python`), `diagnostics.py`. Every public semantic function in
section 1.1 gains an adapter with the same signature and result type. Preservation obligations:

- **Schemas.** Every `to_dict` keeps its keys: `EvaluationResult` (`evaluations` from Rust's work count,
  `explanation` from Rust's trace), `CountermodelCheck`, `EntailmentCertificateCheck` (`steps` becomes the
  trace node count, documented), the `check()` record, admission reports, bundle rows, `ArgumentResult`.
  Snapshot tests pin them.
- **Identities.** `environment_id`, `source_id`, `meaning_id`, `model_id`, `claim_id`, `edge_id`, `report_id`,
  `document_hash` are computed in Python as today and recomputed by Lean, which rejects mismatches. Only
  `checker_build` changes: it becomes the Lean binary hash plus toolchain, the Rust binary hash and the Python
  surface digests, pinned in a committed `checkers.lock`; the adapter refuses unpinned binaries unless
  overridden. Composition `record_id` therefore changes; nothing else does.
- **Diagnostics.** Lift the convention already in `tests/test_p0_three_way.py` into `diagnostics.py`:
  `InvalidModel(<generator>)`, `UnsupportedProfile:`, `AdmissionError:`, `ResourceLimit:`, `DependencyCycle`,
  `DuplicateDeclaration`, `Definition …` map to the existing `VEError` codes; parse rejections carry Rust's code
  and span; anything else is `InvalidInput` with Lean's message.
- **Traces and limits.** Rust gains `evaluate --trace` (Python's kind, value, bindings, detail, children; the
  10,000-node budget) and the missing search options. Work budgets stay deterministic in Rust; Lean's wall-clock
  and memory bounds add a second, non-deterministic `ResourceLimit` source that is labelled as such. Exit codes
  0/1/2/3/4 are unchanged.
- **Failure modes.** Missing or mismatched binaries, crashes and timeouts surface as `CheckerUnavailable` with
  detail; there is no silent degradation and no inference of a Lean result from a Python one.
- **Batching.** `premise_status`, `check_readings`, `check_argument` and `check_step` send one batched request
  per operation instead of one per call, since a sentence check performs four to six authority calls.

**Gate 2.** The full suite (1,059 tests, in the usual four chunks) passes under `VE_AUTHORITY=lean` for every
covered operation, with fixture changes limited to `checker_build`, `record_id` and documented message
wording; adapter fault-injection tests; a written coverage-gap list from section 2 with an owner and a decision
(close in Lean or accept as `UnsupportedProfile` with pilot impact from the coverage dashboard) for each row.

### Stage 3: shadow mode (1 week to build, then 14 consecutive clean days)

`VE_AUTHORITY=shadow` runs Python and Lean/Rust on every semantic call, returns Python's result, and appends a
divergence record `{op, input_digest, python, lean, rust, class}` to a JSONL log. Classes: verdict, identity,
diagnostic-code, schema (zero tolerance); resource and performance (recorded, allowed to differ). Corpora: the
full suite; every conformance fixture and generator (evaluation 701, countermodels 708, parser 742, identity
706, certificates 732 plus 150 forged, the closure, order, induction, admission, elaborated-document and norms
families, the 1,000-set definitions and 1,000-case data differentials, 85,000 English pairs); fuzz (5,000 core,
3,000 closure, plus a fresh 5,000-case seed nightly); the `usecases/` pilots through `ve document check`;
assist ledgers (tests, `experiments/authoring-gates/`, T1c); E1, P1 and iceberg validators; the web app API
tests. CI runs shadow on every merge. Triage rule: a Python deviant is a Python bug, fixed with a new
conformance case; a Lean glue or decoder deviant is fixed with statement review; a spec ambiguity gets a spec
note and a fixture. Any adapter or glue fix restarts the 14-day clock. Shadow also produces the performance
data for gate 4.

**Gate 3.** Zero divergences in the four zero-tolerance classes on all corpora for 14 consecutive days.

### Stage 4: switch authority (3–5 days, packaging 1 week in parallel with stage 3)

Default becomes `VE_AUTHORITY=lean`; Python semantic functions become thin wrappers. Records for covered
operations may carry `assurance: reference-theorems-checked` with a `covered_operations` list and the
`checker_build`, as the contract's evidence table requires; the JSON boundary, IO, compiler and display remain
listed as trusted. Packaging: one stripped `ve_service` (today's two binaries are 175 MiB each) built for
linux-x86_64 and macOS arm64 as release artefacts with a committed SHA-256 manifest, `lake-manifest.json`,
toolchain and `axioms.txt`; the adapter verifies the hash before use; environments without the binary
(Colab, harness sandboxes) run Rust-only for evaluation and search and label results `experimental`.
Documentation: `implementation.md` trust section, `lean/README.md`, `docs/rust.md`, `conformance/README.md`,
ROADMAP status.

**Gate 4.** Gate 3 passed; performance gates in section 4 met from shadow data; packaging installed on a clean
machine and the suite passes there; rollback rehearsed (flip the variable, or revert one merge).

### Stage 5: delete Python semantics, two-way conformance (1–2 weeks)

Delete the "nothing" and partial rows of table 1.1; keep the searchers and the surface objects. Regenerate
fixture goldens with Lean (`conformance/generate.py` and the report generators call the service); Rust is
checked against Lean-produced goldens, so the three-way families (`test_p0_three_way`, `test_norms_three_way`,
`test_data_three_way`, `test_nary_differential`, `test_definitions_differential`, Rust and Lean conformance)
lose their Python column. The README sentence "golden truth values are produced by Python" flips; malformed
package tests and Rust-versus-Lean decoder fuzz stay, because both decoders remain unproved. Tag
`pre-semantics-deletion` before the merge; one merge, one revert.

**Gate 5.** Suite green; a repository-wide import inventory (this repo, `ve-webapp`, `ve-bench`,
`experiments/`, sibling worktrees) shows no consumer of a deleted symbol; regenerated fixtures byte-identical
to the shadow-validated ones; `audit.py` clean; line-count and binary-size report in the merge message.

## 4. Performance gates (measured on a quiet machine, five repetitions, as in the benchmark)

| Gate | Target | Baseline |
|---|---|---|
| IDE: `check_step` end-to-end p95 on the assist replay corpus, checker portion | ≤ 200 ms; no regression over Python for the same step | Python 1–12 ms per check; Lean one-shot 47–152 ms |
| Per authority call through the service | median ≤ 5 ms, p95 ≤ 20 ms; large certificate p95 ≤ 200 ms | one-shot 85–116 ms medians, startup 87–96 ms |
| Pilot throughput: `ve document check` per `usecases/` pilot | ≤ Python wall time | to be recorded in shadow |
| Batches | 2,048 definitions ≤ 1.0 s; 256 bundles ≤ 0.25 s; 256 conflicts ≤ 0.5 s; 8 large certificates ≤ 0.3 s | 0.995 s, 0.203 s, 0.468 s, 0.239 s one-shot |
| Search (Rust) | ≥ 10,000 searches/s on `search.json` batches | 22,145/s |
| Service footprint | startup ≤ 150 ms once per session; ≤ 4 GiB per process; ≤ 2 processes for the IDE | startup 87–96 ms |

## 5. Risks and rollback

| Risk | Mitigation |
|---|---|
| Behaviour loss where Lean is narrower (section 2 rows 6–8) | enumerated at gate 2 with a decision each; shadow counts them as a class; the coverage dashboard measures pilot impact before stage 4 |
| Traces disappear | Rust trace mode with the identical schema; fallback keeps the Python tree as untrusted display whose root must equal Lean's verdict |
| `ResourceLimit` becomes partly wall-clock and non-deterministic | Rust keeps the deterministic budgets; Lean bounds are labelled; a limit is never a verdict; tests stay well inside budgets |
| Diagnostics lose spans or change wording | Rust spans for rejections; the mapping table; wording changes land in one reviewed commit |
| Interactive latency regresses | stage 1 before anything else; batching; gate 4 blocks the switch |
| Service crashes, hangs, desynchronises, grows | nonce framing, timeouts, restart and recycling, address-space limit, fail-closed `CheckerUnavailable` |
| Unproved JSON boundary is mistaken for a verified one | `assurance` lists covered operations only; decoder fuzz and malformed-package tests retained |
| 175 MiB binaries, two platforms, Lean-less environments | release artefacts with hash pinning; Rust-only mode labelled `experimental` |
| Hidden consumers of Python internals (`_Searcher`, `_apply`, `_derive`, `_binding` in conformance, bench, tests) | the searchers stay; import inventory at gate 5; one release of deprecation shims |
| `checker_build` and `record_id` churn | expected and excluded from the shadow diff; artefact identities are asserted byte-equal |
| Expansion streams keep adding Python checkers | rule change at stage 2 (section 6) |

Rollback: through stage 4 the Python code is present and `VE_AUTHORITY=python` restores it instantly; stage 5
is one tagged merge, reverted as a unit. Rust extensions and the Lean service are additive and need no rollback.

## 6. Effort and parallelism

| Stage | Effort | Calendar | Runs in parallel with |
|---|---|---|---|
| 1 service | Lean glue 3–4 d, supervisor 2–3 d, soak 1–2 d | weeks 1–2 | everything: new files only |
| 2 adapters | adapters 2 wk, Rust extensions 1–2 wk (parallel), tests 3–4 d | weeks 1–5 | everything: new package, flag off |
| 3 shadow | 1 wk build, ~1 d/wk triage | weeks 5–8 | everything: additive, and each expansion merge runs under it |
| 4 switch | 3–5 d plus 1 wk packaging | week 8–9 | needs a 2-day freeze on semantic modules |
| 5 delete | 1–2 wk | weeks 9–11 | after numbers round 2 and the W1 mixed-parity branches merge |

Total roughly 8–9 engineer-weeks over 10–11 calendar weeks. Team fit follows PLAN-EXPAND2: Lean glue by the
Lean agents with a statement review, Python and Rust by the Codex agents, shadow triage by the orchestrator.

Rule change from the start of stage 2, to be recorded in PLAN-EXPAND2 §2 and ROADMAP: no new Python semantic
code. New constructs (soft norms first, then rights, then causation) land as Lean checkers and elaborators
behind an adapter; Python contributes surface, IDE offering and proof search only. This removes one of three
implementations from every expansion immediately, before any deletion, and makes the three-way parity rule a
two-way rule for new work.

## 7. Summary

Compiled Lean meets the 200 ms target for every ordinary check and beats Python by 2–30x in batches;
only its process startup and missing service mode keep Python's duplicate checkers alive. The plan adds a
JSON-lines `ve_service` (no proved module touched, glue pinned by `rfl` theorems), then Python adapters that
preserve schemas, identities, diagnostics, traces, budgets and failure modes, then a 14-day shadow
soak with zero divergence across the suite, all conformance and fuzz corpora, pilots and assist replays, then
the switch with hash-pinned binaries and IDE and throughput gates, and finally deletion of about
5,000 lines of Python semantics with conformance becoming Lean-golden, Rust-differential. Rust takes search and
budgeted evaluation; Python keeps the English surface, IDE, web app, CLI, harnesses and proof search. Stages 1–3
run alongside expansion work; from stage 2 no new Python semantics is written. Rollback is a flag until stage 5,
then one revert.
