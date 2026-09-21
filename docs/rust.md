# Experimental Rust VE core

The cargo workspace in `rust/` provides the `ve-core` library and `ve` CLI for
`ve.core@0`, `relational-fol@0`, revision `ve-v0-draft-2026-09-20`, and opt-in
`ve.core@0.1`, profiles `["closure@0", "relational-fol@0"]`, revision
`ve-v0.1-closure-2026-09-21`.
**This implementation is not verified.** It is differentially tested against the
Python reference and the executable Lean evaluator covered by the P6 theorem.
Those tests do not transfer Lean's proofs to Rust or prove the input decoders.

## Build and use

Run from the repository root. Both cargo directories must stay in the worktree
in this sandbox; `.gitignore` excludes them. `Cargo.lock` pins the dependencies.

```sh
export CARGO_HOME="$PWD/.cargo-home"
export CARGO_TARGET_DIR="$PWD/rust/target"
cargo build -j 2 --locked --release --manifest-path rust/Cargo.toml
cargo test -j 2 --locked --all-features --manifest-path rust/Cargo.toml -- --test-threads=1
cargo fmt --manifest-path rust/Cargo.toml --all --check
cargo clippy -j 2 --manifest-path rust/Cargo.toml --workspace --all-targets --all-features -- -D warnings

rust/target/release/ve parse --env examples/environment.json --source examples/requirements.ve
rust/target/release/ve format --env examples/environment.json --source examples/requirements.ve
rust/target/release/ve evaluate --env examples/environment.json --source examples/requirements.ve --model examples/model.json
rust/target/release/ve countermodel --env examples/environment.json --premises examples/premise.ve --conclusion examples/conclusion.ve --max-domain-size 2
```

`check-countermodel` takes the same inference source arguments plus `--model`.
A conclusion must contain exactly one statement. An empty premises file is
rejected with `SyntaxError`, matching Python. Empty premise arrays remain valid
in the programmatic inference envelope. File argument `-` reads
stdin. `--help` lists the commands. These are small explicit commands, not a
replacement for every Python CLI option or acceptance-record field.

`conformance FILE.json` reads a case or array, producing one result per case.
`jsonl FILE.jsonl` streams the same envelope one case per line, with a 16 MiB
per-line cap (including a terminating LF). An oversized record emits one
`ResourceLimit` record, drains through its newline using bounded storage, and
continues with subsequent lines. Envelopes contain `environment`, `ast` and/or `source`, optional
`model` and `id`. Submitted source and AST must agree. An inference envelope
instead has an ordered `premises` AST array and single `conclusion` AST; `model`
selects witness checking, otherwise optional `max_domain_size`, `max_models` and
`max_evaluations` bound search. Test metadata is ignored, including expectations.
`canonical-json FILE.json` emits the exact restricted canonical bytes without an
extra newline. Batch per-formula evaluation uses a fresh evaluation budget for
each formula; the normal `evaluate` command budgets the entire document.

For ordinary commands, exit 0 means successful output, satisfaction, a found
witness or valid countermodel; 1 means violation, bounded absence or invalid
countermodel; 2 means malformed input or resource exhaustion. Batch/JSONL uses
0 for processed logical results, 1 for any rejected case, and 2 for a malformed
batch/invocation; consumers must read each record's `status`. False is not a
parse error. Diagnostic output uses ordinary JSON and can contain null; semantic
input packages use the restricted subset that rejects null.

## Representation and implemented boundary

`Environment::from_json` and `FiniteModel::from_json` validate the same required
wire fields as Python. They reject unknown/missing entries, unsupported versions,
reserved/duplicate symbols, malformed descriptions/signatures, incomplete models,
wrong-sort or dangling entities, duplicate entities/tuples and bad constant
assignments. Empty domains are allowed unless a constant needs an inhabitant;
constants can alias. Domain/relation sets are normalized before model identity.
Strict JSON decoding rejects duplicate keys before overwrite, lone surrogates,
null, fractions/exponents, and integers outside `[0, 2^53-1]`. Negative zero is
accepted and canonicalized to zero, matching Python. UTF-8 input, JSON depth and
package size are checked. Public constructors from `serde_json::Value` cannot
recover duplicate keys discarded by an earlier decoder; use `from_json` or
`loads_json` at untrusted byte boundaries.

`Term` and `Formula` expose raw indexed constructors. `Document::check` and
`Document::from_value` produce a private-field checked document only after scope,
arity, sort, closure, depth and aggregate node validation. This is extrinsic
typing, as in Python and the Lean raw syntax/checker, not a Rust dependent type.
The document carries its full environment ID; evaluation rejects a differently
bound model. Sort-qualified entity IDs are internally compiled to domain indices.
Rust validates and identity-binds optional sort/predicate `verbalisation` and
predicate `negative_verbalisation` metadata, including the 256-character limit.
Display templates are not executed by the Rust core.
Private immutable model/document fields preserve validation, so Rust need not
repeat model decoding and hashing on each evaluation. Raw `to_value` helpers are
not a validation boundary; in-process callers must check raw constructors before
using them as claims.

`parse` accepts the exact ASCII grammar, including final period plus LF, literal
spaces and punctuation, with no alternate grouping, comments or normalization.
It resolves source names to nearest-first indices, rejects shadowing/free names,
and type-checks the complete result. `parse_with_metadata` retains the original
source and formula-completion-order spans/binder names separately. Parse errors
carry locations; type errors after resolution carry a whole-source span.
`print_document` returns a `Result<String>`, enforces the 64 KiB canonical-output
limit, and emits globally fresh preorder `x0`, `x1`, etc., resetting at each
statement, byte-identical on the shared fixtures. It preserves all constructors
and statement order.

`evaluate` short-circuits a whole document; `evaluate_formula` selects one checked
statement. Both return `Satisfied`, `Violated`, or `ResourceLimit`, an optional
Boolean, and evaluation work count. Empty-domain universals and false-antecedent
implications are true; empty-domain existentials are false. The budget is at most
1,000,000 work units (formula visits plus closure edge/Warshall work).
Resource exhaustion never becomes a false judgment.
Rust currently returns no explanatory trace and therefore has no separate trace
budget. Python's default 10,000-node trace cap can exhaust earlier, while
`evaluate(..., trace=False)` disables that cap and explanatory traces. Comparisons
of Boolean semantics require both evaluators to have sufficient resources;
resource behavior is not claimed byte-identical to Python.

`CountermodelProblem::new` validates the ordered premises and one conclusion
under a single 10,000-node aggregate budget. `check_countermodel` independently
checks all needed premise values and conclusion falsity, returning the ordered
meaning IDs, environment and model IDs, values and work. A false premise ends
the check without evaluating the conclusion, as in Python. `find_countermodel`
enumerates sorted domain-size vectors, all constant denotations including aliases,
and every relation subset **only for predicates used anywhere in the formulas**.
Unused predicates have empty relations in witnesses. This is complete within the
finite size bound modulo unused predicate extensions: those extensions cannot
affect the input formulas. That argument is not a mechanized search proof.
The search preserves empty domains and imposes a 100,000-used-atom allocation cap,
model count and work bounds. It uses a bounded bit vector rather than allocating
an exponential list. A returned witness can be checked independently through the
public witness API. `NotFound` and `ResourceLimit` never establish entailment.
The merged Python search also fixes unused predicates to empty; the shared
search and benchmark cases now agree on model/work counts.

`canonical_json` uses UTF-16 key ordering, minimal string escaping and restricted
integer serialization. SHA-256 uses the specified domain-separated preimages.
`Environment::environment_id`, `Document::meaning_id`,
`Document::formula_meaning_id` and `FiniteModel::model_id` agree with Python;
formula and singleton-document meaning IDs intentionally differ. Description
changes affect environment/meaning identity. Hash equality is used under a
collision-resistance assumption, not as a proof of equality or equivalence.

The runtime envelope also bounds source bytes (64 KiB), JSON input/output
packages (16 MiB), JSON nesting (256), AST depth (64), AST nodes (10,000),
sorts (32), predicates (256), entities per sort (1,000), total tuples (100,000),
and identifiers (64 ASCII bytes). Host allocation failure/cancellation remain
process outcomes, not logical results.

Direct dependencies are only `serde` (result-record serialization), `serde_json`
(JSON values and standard string escape handling) and `sha2` (artifact hashes).
No parser, solver, random, CLI or benchmark crate is required. All project Rust
crate roots, tests and the benchmark example forbid unsafe code. Standard-library
and dependency internals, including any upstream unsafe implementation, remain
part of the build/runtime trust boundary.

## Closure representation and evaluation

`Formula::Reach(ReachKind, Edge, Term, Term)` encodes exactly
`["reach", k, e, t, u]`, where `k` is `"plus"` or `"star"` and `e` is
`["named", relation]` or `["body", sort, formula]`. Raw invalid kinds remain
rejected by the checker after structural decoding of the complete document.
Named edges must be homogeneous binary predicates. A body adds two locals:
index **0 is destination**, index **1 is source**, and outer variables shift
by two. Endpoints are checked in the original outer context. Both local binder
names must be fresh. The edge wrapper itself adds no AST node or depth level;
its body adds one formula level, matching Python.

Strict source forms are `tc[edge](t, u)` / `rtc[edge](t, u)` and
`tc[node a, b | (body)](t, u)` / `rtc[node a, b | (body)](t, u)`.
The printer allocates both body names in preorder even when unused. `tc` and
`rtc` remain contextual tokens usable as ordinary vocabulary identifiers.
The v0 profile rejects Reach; its identity preimages remain unchanged. Closure
environments, meanings and models use the `v0.1` identity domain separators,
including Reach-free documents under the closure profile.

Finite evaluation materializes positive transitive closure using Warshall.
It does not seed identity edges: positive self-reach needs a self-loop or cycle;
star additionally accepts equal endpoints. Body edges evaluate every ordered
pair while keeping outer parameters fixed. Cache keys contain the structural
edge and the full outer binding vector, and caches are local to one model and
evaluation context. Document evaluation can reuse a cache across statements;
witness checking clears it between premises and conclusion, matching Python.
Named edge visits, body evaluation and pivot work all consume the budget.
Incomplete closure computation yields `ResourceLimit` with no Boolean.
Search collects predicates from named edges and recursively from body formulas,
including nested closures; unused predicates remain empty in witnesses.

## Differential evidence

The commands below exercise the same committed files in Python, Rust and, where
its API supports the operation, Lean:

```sh
export UV_CACHE_DIR=/private/tmp/ve-uv-cache
UV_CACHE_DIR=/private/tmp/ve-uv-cache uv run --frozen python conformance/generate.py
(cd lean && lake build)
VE_LEAN_PREBUILT=1 uv run --frozen python -m pytest -q
uv run --frozen python conformance/fuzz.py --rust rust/target/release/ve --count 5000
```

The merged corpus has **701 cases / 4,912 formulas** and **708 countermodel
requests**, all checked by Python, Lean and Rust. Added fixtures check **742
parser cases**, **706 identity cases** (including Unicode/escaping, model
reordering and individual formula IDs), **40 restricted JSON cases**, **43
malformed environment/model/AST cases**, and **30 search/witness cases**.
Python and Rust agree on all pinned expectations. Lean consumes evaluation,
countermodel, parser, identity and validation files directly; it checks values,
text and acceptance, not hashes or exact error classes. These files overlap and
are not independent draws. Semantic golden values come from Python; wire classes
are explicitly pinned in the generator and fixture. Incomplete `nul`, `1.`, `1e`
are `SyntaxError`; `NaN`, `Infinity`, `-Infinity` and escaped lone surrogates are
`InvalidInput`. The [diagnostic contract](spec/v0-language.md#rejection-and-resource-behavior)
records identifier length/order and structural AST decoding precedence too.
Python already follows these choices; no Python implementation change is needed.

The seeded fuzz run agrees on **5,000/5,000** formula/model pairs: 2,900 true,
2,100 false, with 781 cases containing an empty domain. It also compares ASTs and
canonical text. The seed, output digest and counts are in
[`conformance/fuzz-summary.json`](../conformance/fuzz-summary.json); generated
JSONL stays under `rust/target`. A disagreement invokes greedy typed reduction
and writes a replay file. No disagreement was found in this run. This generator
has not established exhaustive coverage or statistical error bounds. It does
not fuzz malformed decoders, arbitrary search spaces or resource exhaustion;
those have explicit finite regressions.

Original v0 validation on September 21, 2026: **652 Python tests passed**, including
all available Lean comparisons and its 80-theorem axiom audit; **2 optional
grammar-backend tests skipped** (`llguidance`, `xgrammar` are not installed).
**11 Rust tests passed** with all features and one test thread; rustfmt and
Clippy with warnings denied passed. Regeneration left all corpus JSON bytes
unchanged. CLI regressions cover overlong JSONL recovery
(including newline-at-limit and EOF cases), empty premises rejection, source
binding, and canonical output exceeding 64 KiB despite a valid AST node count.

The closure extension additionally checks **46/46 cases / 866/866 formulas**,
with byte-identical canonical text, AST preimages and environment/document/
formula/model identities; **30/30 E0 witness models**, **204/204 countermodel
checks** (including work exhaustion), **30/30 bounded-search statuses**, and
**56/56 malformed-input diagnostic classes**. Search witnesses are checked by
Python; bounded exhaustive results compare model counts. Enumeration order can
differ, so first-witness and resource-work counts are not claimed identical.
The full suite has no Rust closure skip.

The new seeded stream agrees on **3,000/3,000 closure formula/model pairs** and
all their identities: 1,701 true, 1,299 false, 1,204 with an empty sort, 2,500
with body edges, 622 with nested closures, and 1,500 forced outer-parameter
cases. Models include 961 with self-loops and 353 explicitly generated cycles
of length at least two; categories overlap. The unchanged v0 stream still
agrees on **5,000/5,000** pairs. Generator, seed and replay digest are in
[`rust/fuzz_closure.py`](../rust/fuzz_closure.py) and
[`rust/closure-fuzz-summary.json`](../rust/closure-fuzz-summary.json).
Every generated pair contains Reach, though empty domains or short-circuiting
may avoid evaluating a subformula. These remain development tests rather than
independently sampled evidence. Failure reduction reuses the existing typed
reducer; the replay JSONL stays under `rust/target`.

Rust also compares all **512 directed three-vertex graphs**, all nine endpoint
pairs, and three named/body plus/star formulas with independent path search:
**13,824/13,824 Boolean agreements**. Regressions exercise captured-parameter
cache separation, changing models, strict syntax, version gates, body scope,
depth/node limits and every budget below completion on nested closures.

Closure validation on September 21, 2026: **738 Python tests passed**, including
all available Lean comparisons and the axiom audit; only the same two optional
grammar backends were skipped. **16 Rust tests passed**, all features enabled,
one test thread; rustfmt and Clippy with warnings denied passed. Commands and
benchmarks run sequentially, with Cargo limited to two jobs.

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache uv run --frozen python rust/fuzz_closure.py \
  --rust rust/target/release/ve --count 3000 --summary rust/closure-fuzz-summary.json
```

## Performance

The reproducible driver and committed raw samples are
[`rust/benchmark.py`](../rust/benchmark.py) and
[`rust/benchmark-results.json`](../rust/benchmark-results.json):

```sh
python rust/benchmark.py --repeats 5 --output rust/benchmark-results.json
```

The driver builds the release timed example with two Cargo jobs, checks matching
values and formula-node work, alternates Python/Rust order across five samples,
and runs everything sequentially. Setup, JSON decoding and process startup are
excluded. Evaluation uses three nested universal quantifiers over a full binary
relation, forcing all `n³` atomic visits; the size-64 case does 266,305 formula-node
evaluations. Both implementations use the same 1,000,000-node budget and return
results without traces.

**Kernel-vs-kernel:** Python `_evaluate_validated(..., trace=False)` and Rust's
benchmark-only `EvaluationKernel` evaluate already-validated inputs and wrap
results. Initial validation, model hashing and environment compatibility checks
are outside this timing. The Rust harness is enabled only by the `bench-internals`
feature and still requires checked inputs. Python's no-trace path retains its
ordinary interpreter overhead, including detail-string construction; it is the
merged production implementation, not a separately optimized benchmark kernel.

**API-vs-API:** Python `evaluate(..., trace=False)` is compared with Rust
`evaluate_formula`. Python rechecks its AST and model and recomputes hashes on
each call; Rust checks compatibility of previously validated immutable objects.
These API costs explain why small-case API ratios are much higher than kernel
ratios. Neither comparison isolates programming-language cost from data
structures and implementation choices.

The original v0 reviewer's characterization was **roughly 20–30x on the evaluation kernel**.
That loaded rerun was near that range's upper end: 31.46x at size 32 and
30.14x at size 64. Smaller fixtures have larger kernel ratios as shown below;
this is an approximate workload-specific characterization, not a uniform speedup
or a hard 30x upper bound. Public API ratios are reported separately.

Measured on macOS-26.3.1-arm64-arm-64bit-Mach-O, Python 3.14.6, rustc 1.98.1 and
cargo 1.98.1. CPU model and RAM were not queried in this run. The committed result
records the measured commit, exact source hashes, platform/tool versions, load
averages and all raw timing samples. The
machine is shared and loaded; timings are observations, not isolated performance
estimates. One-minute load was 10.24 at the start and 10.72 at the end.

| Evaluation | Python kernel ms | Rust kernel ms | Kernel ratio | Python API ms | Rust API ms | API ratio |
|---|---:|---:|---:|---:|---:|---:|
| eval_n2 | 0.0112 | 0.000164 | 68.30× | 0.1453 | 0.000184 | 790.07× |
| eval_n4 | 0.0673 | 0.001133 | 59.36× | 0.2561 | 0.001226 | 208.80× |
| eval_n8 | 0.4666 | 0.009898 | 47.14× | 0.9016 | 0.009630 | 93.63× |
| eval_n16 | 3.5513 | 0.092900 | 38.23× | 5.1507 | 0.092415 | 55.74× |
| eval_n24 | 11.2413 | 0.344097 | 32.67× | 14.5407 | 0.340000 | 42.77× |
| eval_n32 | 27.5279 | 0.874889 | 31.46× | 33.6687 | 0.884653 | 38.06× |
| eval_n64 | 244.7169 | 8.119430 | 30.14× | 280.0671 | 8.086500 | 34.63× |

Search includes candidate construction and validation in both implementations;
the merged Python search also uses no-trace evaluation. Matched binary search
checks 3, 19 and 531 models respectively:

| Search | Python API ms | Rust API ms | API ratio |
|---|---:|---:|---:|
| search_binary_n1 | 0.2735 | 0.017548 | 15.58× |
| search_binary_n2 | 1.9604 | 0.111930 | 17.51× |
| search_binary_n3 | 67.0155 | 3.712666 | 18.05× |

For the unused-binary-predicate example, Python takes 1.6762 ms
and Rust 0.081625 ms. **Both now check 15 models / 117 formula nodes.**
Only raw times and counts are reported for this pruning workload. The old
comparison against Python's 4,165-model enumeration is obsolete, and no
pruned-search ratio is presented as a speedup.

The benchmark does not establish production throughput, latency under load,
broad workload generality or performance on other hardware. All five samples
are retained; no timing outliers are removed.

Closure evaluation has a separate recorded run in
[`rust/closure-benchmark-results.json`](../rust/closure-benchmark-results.json):

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache uv run --frozen python rust/benchmark.py \
  --repeats 5 --closure-only --output rust/closure-benchmark-results.json
```

Both cases evaluate positive self-reach for every vertex of a directed
12-vertex cycle. The body case uses `Body(item, edge(Var(1), Var(0)))`; the
named case uses `Named(edge)`. Each implementation starts a fresh cache for
every timed evaluation, includes the full outer context in cache keys, and
performs the same Warshall work. Results are true with **4,405** work units for
named closure and **5,989** for body closure, identical in both kernels/APIs.
Initial validation and process startup stay outside timing. Five samples of
five calls each are retained, with alternating Python/Rust execution order.

| Closure evaluation | Python no-trace kernel ms | Rust kernel ms | Kernel ratio | Python no-trace API ms | Rust API ms | API ratio |
|---|---:|---:|---:|---:|---:|---:|
| closure_named_n12 | 0.5593 | 0.103950 | 5.38× | 0.7458 | 0.102375 | 7.29× |
| closure_body_n12 | 1.8535 | 0.123458 | 15.01× | 2.0606 | 0.123617 | 16.67× |

This run used the same tool/platform versions listed above; one-minute load was
3.72. The result records the core commit and exact worktree source hashes,
including the benchmark driver added alongside these results. These are small,
specific closure workloads, not evidence for the v0 ratios or a general speedup.

## Trust, Lean and P8

Trusted components include this entire Rust implementation, its raw-byte decoder,
validators, name resolver, type checker, evaluator, canonicalizer/hashing, search
and witness-checking code, CLI/IO, dependencies, compiler and runtime. Safe Rust
prevents project unsafe blocks; it does not prove logical correctness. Search
cannot issue a positive entailment judgment. No certificate replay, graph
validation/composition, FOL adapter, natural-language display, source-ID acceptance
record or empirical-evidence verification is implemented here.

The [Lean project](../lean/README.md) proves P6 for its actual finite evaluator,
P10 for semantic assumption composition and P11 for admissible countermodels.
The merged follow-ups prove successful model decoding implies admissibility,
and P4/P5 cover the full v0 language under the declaration-name conditions.
Rust has no refinement proof to those definitions. The Lean bridge's wire-spec
correspondence, compiler and native execution remain trusted. Conformance is
empirical evidence relating these concrete executions, not a Rust P6, P8 or
complete acceptance theorem.

P8 would require an explicit representation relation from Rust's checked
objects/domain indices to `VE.Term`, `VE.Formula`, environments, contexts and
`VE.FiniteModel`, then proofs that successful Rust operations refine the same
reference operations on identical inputs. A concrete work plan is:

1. Pin an extraction toolchain and isolate a tractable core. Try Charon plus
   Aeneas extraction into Lean; first establish which of this crate's maps,
   strings, collections, recursion, integer operations and dependencies are
   supported. Successful extraction has not been attempted. Aeneas supplies a
   Lean backend and requires models for missing external definitions; it does
   not automatically prove those models faithful. See the project's
   [README](https://github.com/AeneasVerif/aeneas/blob/main/README.md) and
   [getting-started guide](https://github.com/AeneasVerif/aeneas/blob/main/documentation/getting-started.md).
2. Prove decoder/validator success yields declared environments, well-formed
   scoped formulas and admissible models. Keep byte parsing, UTF-8/JSON escaping,
   duplicate detection, set normalization, domain-index encoding and exact
   environment binding in scope, or list them as remaining trusted boundaries.
3. Prove parser soundness against an independent grammar-and-binding relation;
   connect Rust printing and successful parse/print to the full-language AST and
   Lean's full-language round-trip theorem. Preserve source/AST substitution
   rejection and its declaration-name premises.
4. Prove budgeted Rust evaluation agrees with the Lean evaluator whenever it
   returns a Boolean, and conditional completeness with sufficient resources.
   Prove work limits/overflow and failure paths preserve the distinction between
   rejection, resource exhaustion and logical false. Then compose with P6.
5. Prove the countermodel checker refines the exact ordered inference and apply
   P11 under model admissibility. Prove the unused-predicate projection lemma
   and bounded enumeration properties if advertising search completeness.
   Preserve model/work exhaustion as inconclusive.
6. Prove byte-exact canonicalization and preimage binding separately; explicitly
   state SHA-256 assumptions. Add full graph/certificate refinement only when
   those Rust operations exist, with P9/P10's corresponding prerequisites.

A completed source proof would still leave the extraction/toolchain assumptions,
external models, compiler, IO and machine execution within their declared trust
boundary. No P8 gate is claimed by this implementation.
