# Worker X closure certificate report

BRANCH

`codex/closure-cert`, based on `ve-integration` at tag `ve-green-0350` (`eb4b17b`). Implementation commit: `4facd5b`.

SUMMARY

- Extended Lean certificate soundness covers all admissible structures; the original v0 theorem and four tableau files are unchanged.
- Both signs of plus/star unfolding and Reach congruence include capture-safe nested Body handling.
- Lean-proved edge inclusion, mixed plus/star composition, first/last-edge existence and Named/Body conversion now have Python replay rules.
- Conformance accepts 63/63 closure certificates and rejects 442/442 closure forgeries; combined totals are 795/795 and 592/592.
- Documentation distinguishes implemented rules; argument results expose profiles and actual Lean replay; Body endpoint display spacing preserves identities.

VERIFY

Commands are run serially from the repository root; `LEAN_NUM_THREADS=1` limits Lean/Lake workers.

```sh
export UV_CACHE_DIR=/private/tmp/ve-uv-cache
export LEAN_NUM_THREADS=1
export CARGO_HOME="$PWD/.cargo-home"
export CARGO_TARGET_DIR="$PWD/rust/target"
export CARGO_BUILD_JOBS=1
(cd lean && lake build)
uv run python lean/audit.py
uv run python conformance/certificates.py --report conformance/certificates-report.json
VE_LEAN_PREBUILT=1 uv run pytest -q
cargo test -j 1 --locked --manifest-path rust/Cargo.toml -- --test-threads=1
git diff ve-integration -- lean/VE/Tableau.lean lean/VE/TableauClosure.lean lean/VE/TableauChecker.lean lean/VE/TableauChecks.lean
git diff --check
```

Build passed. Audit: **41 Lean source files, 200 named theorems**; no proof placeholders or new axioms, only the existing `propext`, `Classical.choice`, `Quot.sound` allowlist. The original tableau diff is empty. The 882-case frozen v0 replay test retains identical validity, status, steps and diagnostics. Full pytest: **736 passed, 3 skipped in 120.22 seconds**. Rust: **11 passed, 0 failed**. `git diff --check` passed. The three skips are missing optional `llguidance` and `xgrammar` packages and explicitly unsupported Rust closure evaluation.

The theorem is `VE.Closure.Tableau.checkCertificate_sound`: acceptance implies
`VE.Closure.Entails.{u} E premises conclusion`. Its corollary
`checkCertificate_sound_v0` derives `VE.Entails.{u}` on embedded old formulas
using `VE.Closure.conservativity`. JSON acceptance has the same universe-zero
target as the existing adapter. Replay terminates by fuel; 124 expansions are
permitted. No user-supplied derived AST, witness or semantic oracle is accepted.

Trusted-code change inventory (each justification concerns soundness, not completeness):

| Change | One-line soundness justification |
|---|---|
| `ve/entailment.py`: `_Branch`, `copy`, `_initial_branch` add declared predicate signatures | Signature metadata comes from the validated environment, is preserved across branches and authorizes no new fact. |
| `ve/entailment.py`: `_Replayer` and `check_entailment_certificate` gate and replay extra rules | Only closure environments can use the five new tags; exact parent inputs reconstruct one child, with unchanged depth/budget and strict-schema checks. |
| `ve/closure.py`: `derive_extra`, edge inclusion | A homogeneous declared base-relation edge is a one-edge positive path; heterogeneous signatures are rejected. |
| `ve/closure.py`: `derive_extra`, path composition | Both inputs must be positive with identical edge syntax, captured bindings and middle term; concatenation yields plus unless both inputs are star. |
| `ve/closure.py`: `derive_extra`, first/last-edge existence | Only positive plus paths qualify; finite nonempty paths have an endpoint edge, and ordinary delta generates the fresh existential witness. |
| `ve/closure.py`: `derive_extra`, Named/Body conversion | A homogeneous declared relation equals the domain-restricted Body containing that same binary atom in either polarity. |
| `lean/VE/TableauExtended.lean` | The v0 signed/branch/witness and ordinary logical rules are separately re-proved over the extended denotation; fresh valuations preserve existing scoped formulas. |
| `lean/VE/TableauExtendedClosure.lean` | The equality, atomic closure and complementary-formula proofs are separately re-proved for extended formulas, retaining exact bindings and typed tokens. |
| `lean/VE/TableauExtendedRules.lean`: `unfoldAt`, `closure_holds` | Endpoint sorts and edge signature checks permit the proved unfolding equivalence under either sign, including capture-safe Body substitution. |
| `lean/VE/TableauExtendedRules.lean`: `groundMatch`, `reachClosed` | Positive equality closure gives equal denotations; structural formula congruence preserves locals through every one- and two-variable binder. |
| `lean/VE/TableauExtendedExtra.lean`: five rule constructors and dispatcher | Each constructor has a Holds-preservation theorem from path inclusion/concatenation/end edges or Named/Body equivalence; dispatch only adds that proved consequence. |
| `lean/VE/TableauExtendedChecker.lean` | Every accepted transition preserves some satisfiable child and every accepted close contradicts satisfaction, so fuel induction proves extended entailment. |
| `lean/VE/Closure/Substitution.lean` | General term substitution preserves denotation under matching valuations; lifted substitutions preserve both Body binders and justify typed path unfolding. |
| `lean/VE/Closure/Congruence.lean` | Matching terms have equal denotations; lifting and structural induction preserve formula denotation, including nested reach relations. |
| `lean/VE/Closure/PathRules.lean` | Finite-path metatheorems prove composition, inclusion and endpoint-edge existence, while admissibility proves the Named/Body relation equality. |
| `lean/VE/CertificateWire.lean` | Closure dispatch uses only the proved extended checker, strict versioned traces and v0.1 identity domains; `ClosureQuery.accepts_sound` connects acceptance to extended entailment. |
| `lean/VE/Audit.lean` | Adds dependency checks for all 59 new theorem declarations without altering the standard-axiom policy. |
| `ve/argument.py`: `_lean_deductions` and result labels | `yes` requires actual successful replay of every supporting deduction certificate; absent executables, errors, timeouts and rejection report `no`. |

The original `Tableau.lean`, `TableauClosure.lean`, `TableauChecker.lean` and
`TableauChecks.lean` have **no changes**. Existing Python `_closed`, `_derive`,
`_apply`, substitution, unfolding and congruence functions have no semantic
changes. `_Searcher`, `extra_candidates`, NotFound wording, rendering and report
formatting are outside proof authorization. Signature metadata and the new
replay dispatcher are the only changes to existing Python replay machinery.

GAPS

- Of the reviewer's five requested entailment families, transitivity, Named/Body equivalence and last-edge existence now prove. First-edge existence also proves. Monotonicity under universally quantified inclusion and symmetric-relation reversal remain `ResourceLimit` at 400 steps; both outcomes remain in tests and the committed report.
- There is no monotonicity, general induction, cyclic proof or saturation-completeness rule. Composition currently requires exact edge syntax, middle terms and captured bindings; first/last-edge search and Named conversion are goal-directed.
- Formal Python refinement, JSON/hash correspondence and IO/compiler/runtime correctness remain outside the Lean theorem. The conformance results cover every emitted certificate in the stated corpus, not every possible Python input.
- The extended graph-checker theorem and full Body/document round trip remain unproved. Argument `lean_checked` labels supporting deduction certificates, not a Lean execution of graph composition or verification of factual assumptions.
- Rust closure support remains unsupported; the existing explicit closure skip remains. Other pre-existing optional skips are retained and listed in the full-suite output.

PLAN CHANGES

Mark closure certificate soundness, capture-safe substitution/congruence and the implemented small path rules complete; retain monotonicity, symmetric reversal, the extended graph theorem and full Body/document round trip as open. No edits to `PLAN.md` are required by this branch.
