# Implemented closure@0 boundary

This implements the closure part of the [v0.1 design](v0.1-profiles.md). Integer
order and Rust closure support are outside this change. The v0 wire envelope,
canonical source and all existing identity preimages remain unchanged.

A closure environment has exactly these version fields plus `vocabulary`:

```json
{"language":"ve.core@0.1","profiles":["closure@0","relational-fol@0"],"spec_revision":"ve-v0.1-closure-2026-09-21"}
```

The sorted unique profiles list is required. Unknown combinations, revisions,
and the singular `profile` field are rejected in the new envelope. Reach in a
v0 environment is rejected. Vocabulary and finite model schemas remain v0.
The wire constructor is `["reach", "plus"|"star", edge, left, right]`, with
`edge = ["named", relation] | ["body", sort, formula]`. No edge coercion occurs.

Python exposes `Reach(kind, Named(relation), left, right)` and
`Reach(kind, Body(sort, formula), left, right)`. Body index 0 is destination,
index 1 source; outer variables start at 2. Endpoints use the outer scope.
Named closure requires a homogeneous binary relation. The strict syntax is
`tc[r](t, u)`, `rtc[r](t, u)` and their two-local Body variants. `tc` and `rtc`
remain available as ordinary v0 identifiers outside that contextual prefix.

Environment, meaning and model identities use `ve-*-v0.1\n` domains, with the
full envelope bound through the environment ID. `source_id(source, env)` selects
that environment's source domain; the legacy one-argument function retains the
v0 raw-source hash. `check` and claim creation pass the environment. The
regression suite checks every hash and canonical preimage in the unchanged
706-case v0 identity corpus.

Python computes a Body relation over all domain pairs for the current outer
valuation, then performs finite Warshall pivots. Plus never seeds identity;
star additionally accepts equal endpoints. Cache lifetime is one evaluator and
its exact finite model; keys include the edge AST and full outer bindings.
Pair/body/pivot work consumes the evaluation budget; exhaustion returns
`ResourceLimit` with no Boolean answer. Countermodel enumeration is unchanged,
with the predicate-use traversal extended to find Named and Body base relations.
It never guesses an unconstrained closure table.

All five views preserve the direction and edge variant, retaining both Body
locals even when vacuous. English closure phrases use raw relation IDs and
cannot enter fluent relative guards. Closure-specific lexical collision
filtering and identical legends are enabled only in the new profile, preserving
v0 rendering. Independent inverse parsers cover the 866 committed closure
formulas and 100 seeded additional extended formulas, including nested bodies.
The full grammar exporter adds two-local context transitions and checks endpoint
scope and homogeneous Named signatures. Syntax mode remains an overapproximation.

Python's only new tableau expansions are:

- `closure-plus@0`: `R+(a,c)` becomes `R(a,c) or exists b (R(a,b) and R+(b,c))`.
- `closure-star@0`: `R*(a,c)` becomes `a=c or R+(a,c)`.

These equivalences can be expanded under either sign; ordinary signed rules
then handle their connectives and quantifiers. Body substitution avoids capture,
including through nested Body binders. Reflexivity of star follows from the
second rule. Congruence preserves exact edge syntax and local indices while
identifying equal endpoints and captured parameters. Different edge variants
are never identified. There is no induction, inclusion-oracle, cyclic-proof,
or saturated-branch-is-satisfiable rule. The new checker version is
`ve-tableau-closure-checker@0`; parent indices and the exact identity-bound
inputs determine the reconstructed expansion. Supplied witnesses are rejected.

The **Lean certificate adapter rejects every v0.1 environment explicitly**.
The proved v0 checker never sees a closure formula or closure trace. Integration
retains integration's v0 version-2 complementary-formula close rule and its
single `VE.Tableau.complementary_sound` proof over exact formulas AND parameter
bindings. All four `Tableau*.lean` files match integration, preserving the
version-1 gate, 124-expansion limit and exact `checkCertificate_sound` statement. Existing v0
certificates remain supported. The oracle returns UNKNOWN when neither checked
Python replay nor an independently re-evaluated finite countermodel succeeds;
it does not infer validity from bounded search exhaustion. Python closure
replay is not advertised as Lean-certified.

The exact proved Lean statements and proof gaps are in
[lean/CLOSURE.md](../../lean/CLOSURE.md). The extended evaluator and independent
typing checker are proved correct for both edge variants. Reach-free
conservativity and both least-fixed-point characterizations are proved. The
new syntax theorem covers Named atoms with arbitrary typed endpoints and
canonical outer scope, public singleton-document round trip, and Named-atom
printer injectivity; full extended-document/Body round trip and general printer
injectivity are not proved. Closure substitution and tableau branch-preservation
proofs remain open. The list-based Lean evaluator has no proved complexity or
runtime budget bound; JSON/IO/compiler correspondence and Python refinement
remain outside the metatheory.

Reproduce sequentially from the root:

```sh
export UV_CACHE_DIR=/private/tmp/ve-uv-cache
export CARGO_HOME="$PWD/.cargo-home"
export CARGO_TARGET_DIR="$PWD/rust/target"
export CARGO_BUILD_JOBS=1
(cd lean && lake build)
uv run python lean/audit.py
VE_LEAN_PREBUILT=1 uv run pytest -q
cargo test -j 1 --locked --manifest-path rust/Cargo.toml -- --test-threads=1
```

`VE_LEAN_PREBUILT=1` keeps pytest from starting a nested build. It requires the
preceding successful build. The committed closure corpus has 46 models and 866
formulas: exhaustive two-vertex directed graphs, empty sorts, isolated vertices,
self-loops, cycles, reversed paths, captured filters and nested closures. Lean
also checks every corpus model as a countermodel request. These are development
fixtures, not an independent estimate of real-world coverage or translation accuracy.

Rust still rejects the new envelope. It would need matching profile/wire types,
Body scoping and substitution, checker and parser/printer support, budgeted finite
closure evaluation, updated base-predicate discovery, v0.1 identity domains,
and replay of `conformance/closure.json` plus the E0 witnesses. Its v0 behavior
and existing fixture files are unchanged. Rust v0 conformance and cargo tests
are included in the integration verification; only its named closure corpus
test is explicitly skipped because that profile is unsupported. The complete
882-case frozen v0 certificate replay regression is documented in
[conformance/README.md](../../conformance/README.md). The full trusted-code change
inventory and verification results are in
[the merge report](../closure-merge-report.md).
