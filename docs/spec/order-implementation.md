# Implemented order boundary: Lean Stage 1 only

This is a quota-conscious, green checkpoint on `codex/order`, branched from
`ve-integration`. The Lean foundation took substantially more work than expected;
the implementation stops after Stage 1. It does not expose an order environment
through Python or JSON. No E0 coverage gain or differential-conformance count is
claimed. See [ORDER.md](../../lean/ORDER.md) for the exact proved statements.

The fragment adds a disjoint built-in integer sort, literal integers, addition,
signed numeral scaling, `<`, `≤`, and ordinary equality. Minus and subtraction
are term constructors' definitional abbreviations. Standard integers are used
without overflow. User-domain quantifiers remain available; integer quantifiers
are rejected. This permitted implementation choice avoids inventing a bounded
meaning for an unbounded quantifier and avoids relying on unproved Presburger
elimination. It narrows design B: parity examples and translations needing
quantified integer field values are not covered by this checkpoint.

`closure@0` and `order@0` are declared incompatible until a combined syntax,
denotation and evaluator are implemented and proved. V0 formulas embed
conservatively into the new core, and every admissible old structure has an
admissible expansion with standard integers. Closure behavior is preserved by
leaving its implementation untouched, not by claiming a mixed-language theorem.

There are no arithmetic tableau rules. The existing Lean certificate entry
point rejects both the order-only and combined envelopes at its profile gate.
The existing Python environment parser also rejects those profiles. The proposed
revision in `VE.Order.Gate.envelope` is only a negative-test fixture, not a newly
accepted wire version. A future Python order oracle must return UNKNOWN for
arithmetic entailment until a separately proved and bound proof path exists.

Stage 2 requires AST/wire/parser/canonical-printer support, independent typing,
finite-presentation validation/evaluation/search, versioned identities, all five
views and their inverses, compact legends, explicit grammar budgets, oracle
routing and at least 500 generated cases replayed in Python and Lean. Preserve
every existing v0 and closure identity preimage and corpus fixture. Integer wire
values must be canonical decimal strings. The current Lean result does not prove
any correspondence for a future parser, serializer or Python evaluator.

The required search boundary is: **numerals are never enumerated or reassigned**;
each integer constant is assigned an actual integer (aliases allowed). Candidate
enumeration may bound those assignments to `[-B,B]` and numeric relation-table
cells to an explicit finite set, but those are search bounds, not semantic
integer bounds. No integer domain list is accepted. Predicate tables are complete
finite extensions, with absent tuples false on all integers. Every candidate
must pass complete typing/model validation and re-evaluation of all premises and
the conclusion before a countermodel is returned. `countermodel_sound` applies
only after that admissibility obligation is discharged. Bounded exhaustion or a
resource limit is UNKNOWN/NotFound, never entailment. This describes obligations
for the unimplemented Python search; it is not a search-completeness claim.

Stage 3 requires source-pinned true/false witness pairs in
`experiments/E0/order_witnesses/`. The existing ledger contains **no FRET order
movers**: its signal formulas are real-valued. Do not fabricate FRET witnesses
by integerizing them. Its 14-mover projection assumes the full design including
integer quantification; it cannot be credited to this narrower implementation.
Witness selection must re-audit each original translation obligation. Neither
parity through an unbounded quotient nor relational numeric field lookup may be
silently replaced by a finite active-domain quantifier.

Rust is out of scope. It will need a separately versioned opt-in envelope,
arbitrary-precision integer AST/model values and decimal-string codecs, typed
numeric arguments, matching parser/printer/evaluator/search behavior, numeric
view/grammar budgets where applicable, identity preservation, profile-gated
certificates, and replay of the eventual shared order corpus. Its existing v0
suite remains part of checkpoint regression testing.

## Trusted-code change inventory

Every changed or added implementation file affecting the Lean trust boundary is
listed here. No existing semantic definition or checker implementation changes.

| File | One-line soundness justification |
|---|---|
| `lean/VE/Order/Syntax.lean` | Defines a separate typed extension with literal coefficients and an explicit rejection of integer binders; it cannot change old syntax. |
| `lean/VE/Order/Typing.lean` | Proves the executable checker equivalent to the independently defined typing predicate. |
| `lean/VE/Order/Semantics.lean` | Fixes numeric meaning to standard `Int` in a disjoint carrier and proves typed terms defined and distinct numerals unequal. |
| `lean/VE/Order/Finite.lean` | Defines complete finite predicate extensions over actual integer values and proves executable evaluation equivalent to independent denotation. |
| `lean/VE/Order/Consequence.lean` | Proves refutation soundness from a semantically valid presentation; no bounded search failure is interpreted as proof. |
| `lean/VE/Order/Conservativity.lean` | Constructs admissible expansions of arbitrary old structures and proves exact truth preservation and no new old-language entailments. |
| `lean/VE/Order/Gate.lean` | Proves the unchanged environment gate rejects proposed order and combined profiles; it introduces no acceptance rule. |
| `lean/VE/Order/Checks.lean` | Adds executable boundary regressions without altering definitions or supplying proof evidence to replay. |
| `lean/VE/Audit.lean` | Imports the extension and adds every new named theorem to dependency auditing, retaining the existing allowlist. |
| `lean/VE.lean` | Imports order checks so the ordinary build checks them; no executable certificate dispatch changes. |
| `lean/axioms.txt` | Regenerated evidence of all audited dependencies, not an input supplying assumptions. |

`tests/test_order_gate.py` is an additional runtime regression only. Documentation
records limits and continuation obligations. No files under `ve/`, `rust/`, or
the old v0/closure proof modules are modified; the certificate checker and its
wire entry point are unchanged.

## Verification at the checkpoint

Base: `768dd518e85f196b379700b913d7288c50b9db74` (`ve-integration` when
`codex/order` was created). Run from the repository root, sequentially:

```sh
export UV_CACHE_DIR=/private/tmp/ve-uv-cache
export LEAN_NUM_THREADS=1
export CARGO_HOME="$PWD/.cargo-home"
export CARGO_TARGET_DIR="$PWD/rust/target"
export CARGO_BUILD_JOBS=1
lake -d lean build
uv run python lean/audit.py
cargo build -j 1 --locked --release --manifest-path rust/Cargo.toml
VE_LEAN_PREBUILT=1 uv run pytest -q
cargo test -j 1 --locked --manifest-path rust/Cargo.toml -- --test-threads=1
git diff --check
```

Results: Lean build passed, including 29 order boundary checks. The audit passed
for 49 source files and all 218 named theorems, including 18 new order results;
no new assumptions were added. Pytest: **775 passed, 2 skipped**, 137.93 seconds.
The two skips are uninstalled optional `llguidance` and `xgrammar` backends.
Existing v0 identities, closure views/identities, certificate replay and Lean
conformance regressions passed in that run. Rust: **16 passed**, no failures or
ignored tests. Whitespace validation passed. The serial release build primes the
cache before pytest's existing Rust fixture invokes its unchanged build command.

There are no changes to `ve/`, `rust/`, `conformance/`,
`lean/VE/Closure/`, the v0 theorem modules, any `Tableau*.lean` module, or
`lean/VE/CertificateWire.lean` relative to that base. The only modified existing
Lean source files are the aggregate import and audit registry.
