# Implemented closure@0 boundary

This implements the closure part of the [v0.1 design](v0.1-profiles.md). Integer
order support is separate. Rust supports closure syntax and finite evaluation,
but has no tableau certificate checker. The v0 wire envelope,
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

The Lean-checked tableau rules and their implementation status are listed in
[v0.1-profiles.md](v0.1-profiles.md). Both polarities of plus/star
unfolding and exact Reach congruence are checked, including outer captures
through nested Body binders. New versioned rules add homogeneous Named edge
inclusion, composition of all plus/star combinations, plus first/last-edge
existence, and Named-to-binary-Body equivalence. Every new rule has a Lean
soundness proof. Version `@1` adds supplied-invariant induction with three
checked branches (base, preservation, continuation); cyclic certificates remain
rejected. See [the rule and wire format](closure-induction.md).

`CertificateWire` routes the exact closure envelope to
`VE.Closure.Tableau.checkCertificate`. It validates the v0.1 environment/meaning
identity domains and accepts `ve-tableau-closure-checker@0` and `@1`.
Old certificates are accepted unchanged; only `@1` enables induction. V0 versions in a
closure envelope are rejected, even for Reach-free formulas. V0 envelopes still
use the unchanged original checker. The four original `Tableau*.lean` sources
and `VE.Tableau.checkCertificate_sound` statement are unchanged.

`VE.Closure.Tableau.checkCertificate_sound` ranges over all admissible structures
at every universe. `checkCertificate_sound_v0` derives v0 entailment from accepted
embedded formulas using conservativity. The recursion is bounded by the same
124-expansion limit; extra consequences introduce no recursive proof search in
replay. Failure to find a closure certificate explicitly says it is inconclusive.
Without supplied invariants, monotonicity and symmetric reversal retain their
ResourceLimit reviewer regressions. The new T9/T9e induction certificates replay
in both Python and Lean.

Argument results expose `profiles`, `lean_checked`, and `lean_status`. The default
Python API says `Lean-checked: no`; it does not infer an execution result from
the existence of a soundness theorem. `check_argument(..., lean_executable=path)`
independently replays every supporting deduction certificate and reports `yes`
only when all are accepted. This label applies to those deduction certificates;
the argument composition record and empirical assumptions remain separate.
Missing executables, rejection and timeouts cannot produce `yes`.

The exact proved Lean statements and proof gaps are in
[lean/CLOSURE.md](../../lean/CLOSURE.md). The extended evaluator and independent
typing checker are proved correct for both edge variants. Reach-free
conservativity and both least-fixed-point characterizations are proved. The
new syntax theorem covers Named atoms with arbitrary typed endpoints and
canonical outer scope, public singleton-document round trip, and Named-atom
printer injectivity; full extended-document/Body round trip and general printer
injectivity are not proved. Closure substitution, congruence, branch preservation and certificate soundness
are now proved. An extended claim-graph checker theorem remains open. The list-based Lean evaluator has no proved complexity or
runtime budget bound; JSON/IO/compiler correspondence and Python refinement
remain outside the metatheory.

Reproduce sequentially from the root:

```sh
export UV_CACHE_DIR=/private/tmp/ve-uv-cache-induct
export LEAN_NUM_THREADS=1
export CARGO_HOME="$PWD/.cargo-home"
export CARGO_TARGET_DIR="$PWD/rust/target"
export CARGO_BUILD_JOBS=1
(cd lean && lake build)
uv run python lean/audit.py
uv run pytest -q
cargo test -j 1 --locked --manifest-path rust/Cargo.toml -- --test-threads=1
```

Pytest builds the Lean and Rust backends once per invocation under a shared artifact lock.
The committed closure corpus has 46 models and 866
formulas: exhaustive two-vertex directed graphs, empty sorts, isolated vertices,
self-loops, cycles, reversed paths, captured filters and nested closures. Lean
also checks every corpus model as a countermodel request. These are development
fixtures, not an independent estimate of real-world coverage or translation accuracy.

Rust supports the closure profile, including Body scopes, finite evaluation,
identity domains, and the shared closure corpus. It has no tableau certificate
type, proof search, or certificate-replay command, so there is no Rust induction
checker to update. [Rust scope](../rust.md) documents this boundary. The complete
882-case frozen v0 certificate replay regression is documented in
[conformance/README.md](../../conformance/README.md). The full trusted-code change
inventory and verification results are in
[the merge report](../closure-merge-report.md).
