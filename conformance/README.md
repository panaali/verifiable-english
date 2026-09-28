# Portable VE v0 conformance cases

`evaluation.json` contains **701** valid environment/model/document cases
(**4,912 formulas**). `countermodels.json` contains **708** valid
premises/conclusion/model requests. Every committed case is checked by both
Python, Lean and Rust; no failed case is dropped from the comparison.

## Stable evaluation format

The existing evaluation envelope is unchanged for consumers, including Rust.
The top level is a JSON array in deterministic generation order. Every case has
exactly these keys (object key order is insignificant):

| Key | Value |
|---|---|
| `id` | Unique string identifying the case. |
| `environment` | VE v0 environment object, including version tags and vocabulary. |
| `model` | Complete finite model object with `domains`, `constants`, `relations`. |
| `ast` | Nonempty ordered array of closed, typed indexed formula ASTs. |
| `source` | Canonical source for the whole document, ending in period+LF. |
| `expected` | Boolean array, one truth value per formula in `ast` order. |

Whole-document truth is the conjunction of `expected`. The AST, environment and
model retain the formats in `docs/spec/v0-language.md`. Formula tags remain
`top`, `bottom`, `unary`, `binary`, `eq`, `not`, `and`, `or`, `implies`, `forall`,
`exists`; terms remain `["var", nearest_first_index]` or `["const", name]`.
Quantifier ASTs are `[tag, sort, body]`. Local IDs denote `(sort, local_id)`
entities; equal strings in different sorts are different entities. Constants of
the same sort may denote the same entity. Empty domains are valid when no
constant is declared for that sort. This change adds cases, without renaming
fields, tags or existing IDs. Consumers must not depend on a fixed case count,
array position or JSON whitespace.

The Lean response is an array of `{id, status, values, value, canonical}`
records. `values` follows AST order, `value` is their conjunction, and `canonical`
is the Lean printer output. `source`, when present, must parse to the submitted
AST. Every evaluation also checks the Lean canonical print/parse round trip.

## Opt-in countermodel format

The separate `countermodels.json` file adds a request kind; it does not change
`evaluation.json` or require evaluation-only consumers to support it.

| Key | Value |
|---|---|
| `id` | Unique case string. |
| `kind` | Exactly `"countermodel"`. |
| `environment`, `model` | The same objects/formats as evaluation cases. |
| `premises` | Ordered array of closed typed formula ASTs; may be empty or contain duplicates. |
| `conclusion` | One closed typed formula AST, not a document array. |
| `expected_refutes` | Boolean: all premises are true and the conclusion is false. |

The Lean response is `{id, status: "ok", refutes: boolean}`. `refutes: false` is a
successful check, not rejection; it means a false premise or true conclusion.
Zero premises have vacuously true conjunction. Lean exposes the proved
`countermodelCheck` through this path and rejects ill-typed premises/conclusions
before evaluation. Python compares with `ve.search.check_countermodel`. Rust
returns `status: "Valid"` or `"NotCountermodel"` and a `valid` Boolean; the tests
compare that Boolean and every Python witness-check field on all 708 requests.
A true result refutes the Lean common-carrier `Entails.{0}` target, which ranges
over all admissible Type 0 structures, including infinite ones. See
`lean/README.md` for the precise proof and remaining interpretation assumptions.

## Coverage and reproduction

The evaluation corpus includes 6 worked-example variants, 31 single-sort cases
exhausting unary extensions on sizes 0–4, 4 explicit constant-alias/ordered-edge
cases, 160 seeded depth-4 documents, and 500 extended mixed-sort documents.
The latter cover all 25 pairs of sort sizes 0–4, 20 cases each, including both
mixed-empty directions and both-empty domains. Each includes three seeded
random formulas of depth up to 6, an explicit six-binder alternating prefix
with outer/inner references, and mixed-sort vacuity tests. Nonempty item sorts
also test constant equality and its negation, with aliases and distinct values.
Random formulas use only constants/indices available at their sort. The seeds
are `20260921` and `20260922`. Countermodel cases use every evaluation model and
include explicit empty-premise, true-conclusion, false-premise, duplicate-premise
and positive-refutation cases.

These are development fixtures, not an independently frozen evaluation corpus.
Golden truth values are produced by Python, so Lean agreement is a differential
check, not an independent oracle for decoding. Regression tests also cover
malformed models, raw JSON, and ill-typed/free/cross-sort formula rejection.

From the repository root:

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache uv run --frozen python conformance/generate.py
UV_CACHE_DIR=/private/tmp/ve-uv-cache uv run --frozen python -m pytest -q tests/test_lean_conformance.py
```

From `lean/`:

```sh
lake build
python3 audit.py
lake exe ve_conformance ../conformance/evaluation.json
lake exe ve_conformance ../conformance/countermodels.json
```

A single case or an array (including mixed request kinds) can be supplied by
path or stdin. Exit 0 means every case was evaluated, 1 means a case was
rejected, and 2 means malformed restricted JSON or incorrect invocation.
Logical false is a successful result. Rejections have `{id, status: "error",
error: string}`. `expected` and `expected_refutes` are never read by Lean.
With no `lake`, Python golden checks run but Lean checks are explicitly skipped.

The bridge validates vocabulary declarations, typed ASTs and model inventories.
Successful model decoding is now proved to imply semantic admissibility.
This does not establish JSON/wire-spec correspondence, Python refinement, IO,
compiler or native-runtime correctness. The reference evaluator has no
work-budget outcome; the bridge is for bounded conformance inputs, not hostile
workloads. A separate certificate replay mode is described below. Both committed files are below the bridge's
16 MiB batch cap.

## Rust and extended shared fixtures

The merged generator retains the Lean evaluation/countermodel extensions and
regenerates every Rust fixture from the enlarged corpus:

| File | Cases | Checks |
|---|---:|---|
| `evaluation.json` | 701 / 4,912 formulas | Python, Lean, Rust Boolean evaluation and canonical text |
| `countermodels.json` | 708 | Python, Lean and Rust witness checks |
| `parser.json` | 742 | Source to canonical AST/text or Python/Rust diagnostic class; Lean acceptance/rejection |
| `identity.json` | 706 | Python/Rust environment, document, formula and normalized-model hashes and canonical preimages; Lean evaluation/surface checks |
| `wire.json` | 40 | Python/Rust restricted JSON, duplicate keys, UTF-16 key ordering, escaping and exact rejection classes |
| `validation.json` | 43 | Python/Rust diagnostic classes; Lean environment/model/AST rejection |
| `search.json` | 30 | Python/Rust bounded search or independent witness checks |

Semantic expectations are generated by Python. Wire diagnostic classes are
explicitly pinned and checked against Python during generation. Identity and parser files
include the enlarged evaluation fixtures, so their counts are overlapping tests,
not independent semantic samples. Lean has no identity, restricted-JSON
canonicalizer or search API: no agreement is claimed for those operations.
The merged Lean bridge consumes the evaluation, countermodel, parser, identity
and validation files directly. It supplies only acceptance/rejection
for invalid parser cases, not Python's diagnostic classes. Search expectations
omit unavailable fields to keep the fixture envelope inside the restricted JSON
subset; result records can contain null.

From the root:

```sh
export CARGO_HOME="$PWD/.cargo-home"
export CARGO_TARGET_DIR="$PWD/rust/target"
cargo test -j 1 --locked --manifest-path rust/Cargo.toml -- --test-threads=1
python conformance/generate.py
UV_CACHE_DIR=/private/tmp/ve-uv-cache uv run --frozen python -m pytest tests/test_rust_conformance.py -q
```

The Python test builds Rust when `cargo` is available, otherwise skips its Rust
checks. It similarly skips Lean checks when `lake` is absent. Available tools
that fail to build cause test failures, not skips. It checks every fixture file
above, including the new countermodels; the original Python/Lean test remains
unchanged. CLI regressions check that an oversized JSONL record produces one
error and later records still run, and that empty premises files are rejected.
Wire/validation regressions retain identifier length and validation-order cases
and malformed AST decoding precedence. Exact wire classes are documented in
[`../docs/spec/v0-language.md`](../docs/spec/v0-language.md#rejection-and-resource-behavior).

`fuzz.py` generates 5,000 well-typed random formula/model pairs (seed 20260922),
including mixed sorts, constant aliases, nearest-first indices, empty domains,
and all logical constructors. It evaluates with the Python package, writes
`rust/target/fuzz.jsonl`, invokes the Rust JSONL CLI, and compares truth values,
ASTs and canonical strings. Rust never reads the golden `expected` field.
`fuzz-summary.json` is a result summary, not an additional case corpus; it records
the JSONL digest and outcome distribution. Replay/regenerate with:

```sh
cargo build -j 2 --locked --release --manifest-path rust/Cargo.toml
python conformance/fuzz.py --rust rust/target/release/ve --count 5000
```

A disagreement triggers greedy reduction of formula subtrees, relation tuples
and nonconstant domain entities, retaining type correctness and the mismatch.
It writes `rust/target/fuzz-minimal.json`. This is a locally minimized failure,
not a claim of a globally smallest counterexample. Decoder/parser-only failures
need their own targeted reduction. The seed, generator and summary are committed;
the approximately 5.5 MiB replay stream stays in the ignored build directory.

See [`../docs/rust.md`](../docs/rust.md) for API scope, operational differences,
trust and the benchmark command/results.

## Data-only certificate replay

`ve_conformance check-certificate [file|-]` reads one query or a batch of queries:

| Key | Value |
|---|---|
| `id` | Case label. |
| `environment` | Exact VE environment including descriptions/display metadata. |
| `premises` | Ordered formula AST array; duplicates and zero premises are allowed. |
| `conclusion` | One formula AST, not a document. |
| `certificate` | Unchanged `ve.entailment` certificate, including all five fields and its trace. |

The adapter validates typed inputs, exact certificate fields and node schemas,
recomputes environment/premise/conclusion SHA-256 bindings, and calls the proved
Lean checker. An ordinary result is `{id, status: "ok", valid: boolean}`.
Malformed or stale data gives `{id, status: "error", valid: false, error}` and
exit 1; malformed restricted JSON gives exit 2. **Only `valid: true` is an
acceptance**, since a well-formed rejected trace returns exit 0 with false.
There is no model field and no expected-result field influences replay.

`certificates.py` regenerates all queries and Python certificates before invoking
the Lean executable in bounded batches. The seed is 20260923. The committed
`certificates-report.json` records all 811 search attempts: 732 produce accepted
certificates, 77 produce `NotFound`, and 2 produce `ResourceLimit`. This includes
320/320 bounded-schema random valid queries; 320/320 broader random valid
queries; 82/160 unconditioned random queries; eight existential weakening
regressions; and the bridged/merged positive worked examples. The separated example is
`NotFound`, and its forged close is rejected. Every produced certificate is
replayed: **732/732 accepted**, with no format gaps, unsupported rules or bugs
observed in that comparison. All **150/150 forgeries** are rejected.
The detailed report counts both signs of every propositional/quantifier rule.

These are seeded development cohorts, not an independently frozen corpus or an
unbiased estimate of real-workload acceptance. Forgeries include fresh/future
and wrong-sort gamma tokens, supplied delta witnesses, an empty-sort existence
fallacy, wrong indices/branch counts, stale ordered identities and malformed
schemas. Separate tests cover duplicate JSON keys, null, fractional/negative
indices and premise order/multiplicity. Identity tests include Unicode and
control-character descriptions and SHA-256 inputs spanning several blocks.

Reproduce from the repository root:

```sh
(cd lean && lake build)
.venv/bin/python conformance/certificates.py --report conformance/certificates-report.json
.venv/bin/python -m pytest -q tests/test_lean_certificates.py
```

The checker theorem ranges over all admissible structures, including infinite
ones and empty sorts; the JSON target is `Entails.{0}`. The proof covers replay
on decoded ASTs, not JSON/wire/hash correspondence, IO, compiler/runtime, or
Python refinement. Python search and its replay filter are untrusted for the
Lean result. The default Python API continues to use Python replay.

## Opt-in closure@0 fixtures

`closure.json` contains 46 v0.1 environments/models and 866 formulas. It is kept
separate so v0 consumers retain the original fixture envelopes.
`closure.py` deterministically regenerates it. Cases cover empty sorts, all
two-vertex graphs, positive cycles, isolated star reflexivity, direction,
Body parameters and nested closure. Python/Lean evaluation and canonical source
agree on every case; tests additionally exercise all five view inverses and
100 seeded extended formulas. See `docs/spec/closure-implementation.md` and
`lean/CLOSURE.md` for proof and runtime boundaries.

Rust runs every closure fixture through `test_rust_closure_evaluation`, including
all 866 formulas and their canonical AST/text and versioned identities. Its
tests also check the 30 closure E0 witnesses and closure countermodel requests.
All seven v0 files in the table above still run against Rust, including its
5,000-case v0 fuzz stream. `rust/fuzz_closure.py` adds 3,000 seeded closure pairs;
see `docs/rust.md` for reproduction and counts. There is no closure skip.

## Frozen v0 replay regression

`v0-replay-baseline.json` records the entire certificate corpus generated and
replayed by integration commit `6798e034c4aa7082dafacbb7b130879cd4eec4f6`, before
any closure changes: 732 accepted certificates and all 150 rejected forgeries.
It includes each original query/trace and full replay result (validity, status,
step count and diagnostic), as well as every corpus search outcome. No failed
search is converted into a certificate or removed from the generation report.

Regenerate with `UV_CACHE_DIR=/private/tmp/ve-uv-cache uv run python
conformance/replay_baseline.py`. The generator extracts the pinned commit into a
temporary directory and runs both its corpus generator and its replay checker
there; it never imports the current checker to produce expected verdicts.
`tests/test_replay_conservativity.py` replays all 882 frozen cases using the
current checker and requires identical complete results. This test needs no git
checkout or regenerated proofs at test time.

## Closure certificate replay

`certificates.py` also runs `closure_certificates.py`: **63/63** closure Python
certificates are accepted by Lean and **442/442** closure forgeries are rejected.
Combined with the unchanged v0 cohorts, the report has **795/795** accepted and
**592/592** rejected certificates, with no dropped mismatches. The two retained
reviewer failures are monotonicity under a universal inclusion and symmetric
reversal, both `ResourceLimit` at 400 steps. Transitivity, both Named/Body
directions and first/last-edge existence prove in two search steps each.

The closure cohort covers both signs and edge variants, nested captures, equality
on constants and outer bindings, empty sorts, every plus/star composition,
multiple path/edge composition, and version/schema/sort/sign/direction attacks.
These are constructive development regressions, not a completeness claim or an
unbiased workload sample. Run serially with the same command as the v0 corpus:

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache uv run python conformance/certificates.py --report conformance/certificates-report.json
```

The exact original four v0 tableau source files and theorem are preserved.
The default argument checker labels Python replay separately; callers can use
`check_argument(graph, lean_executable=path)` to obtain an actual Lean acceptance
label for every supporting deduction certificate.

### Adopted unary English vocabulary

The proposal generator has no unambiguity claim. The finite lexicon produced by
explicit adoption is included in `english_surface.configurations()`. Reproduce
its separate audit report (5,000 round trips; 500 directed-prefix plus 250 deep
random all-derivations checks; 50 multi-statement documents) with:

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-propose uv run python -m conformance.english_surface --adopted-only --output conformance/proposed-vocabulary-report.json
```

The audit uses `ve.propose.adopt`, reloads the written files, and checks the
ordinary finite English grammar. Its overlay and report remain unreviewed.

## order@0 (Python vs Lean)

`python -m conformance.order` generates order@0 entailment queries, proves them
with the untrusted Python search, and replays every certificate with the Python
checker (`ve/order.py`) and the Lean checker (`ve_conformance order`, proved by
`VE.Order.Tableau.checkCertificate_sound`). It also sends mutated and hand-built
certificates (all verdicts must agree; hazards must be rejected), Python
countermodels (checked by Lean's proved `checkCountermodel` gate) and random
evaluations. The report is `order-report.json`; `tests/test_order.py` reruns the
corpus. Rust evaluates checked order ASTs and supplied models via its separate
order route.

## P0 route fixtures

`alternatives.py` generates the a, b, c, d, e, j and o scenario shapes from
`docs/spec/alternatives.md` §8. `tests/test_alternatives_three_way.py` asks the
Lean alternatives route to validate each scenario and generate its closed
followability formula plus existential probes for all four profile words.
Python and Rust then evaluate those Lean-generated formulas against the same
base model and compare with Lean's scenario report. The Rust route receives a
plain base environment and never elaborates alternatives or supplies a
profile-word table. The s2 case separately checks Lean's CONFLICT witness
against independent evaluation of its regenerated conflict target.

`elaborated-document.json` contains the `ve.core@0.2` envelope, two declared
`$string` literals, a valid model, and three rejected profile combinations.
`invalid-background-model.json` contains an aliasing literal model that must
fail with `InvalidModel`; its flag and definition cases are marked `pending: W5`
and `pending: W3` until those declaration schemas are implemented. The fixtures
are generated by `conformance/p0.py`; `tests/test_rust_conformance.py` compares
the active cases with Python and Rust. Lean's new `route` subcommand is the
third consumer when the P0-Lean worktree is integrated.
