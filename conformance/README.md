# Portable VE v0 conformance cases

`evaluation.json` contains **701** valid environment/model/document cases
(**4,912 formulas**). `countermodels.json` contains **708** valid
premises/conclusion/model requests. Every committed case is checked by both
Python and Lean; no failed case is dropped from the comparison.

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

The response is `{id, status: "ok", refutes: boolean}`. `refutes: false` is a
successful check, not rejection; it means a false premise or true conclusion.
Zero premises have vacuously true conjunction. Lean exposes the proved
`countermodelCheck` through this path and rejects ill-typed premises/conclusions
before evaluation. Python compares with `ve.search.check_countermodel`.
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
`certificates-report.json` records all 803 search attempts: 721 produce accepted
certificates, 75 produce `NotFound`, and 7 produce `ResourceLimit`. This includes
320/320 bounded-schema random valid queries; 317/320 broader random valid
queries (three search resource failures); 82/160 unconditioned random queries;
and the bridged/merged positive worked examples. The separated example is
`NotFound`, and its forged close is rejected. Every produced certificate is
replayed: **721/721 accepted**, with no format gaps, unsupported rules or bugs
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
