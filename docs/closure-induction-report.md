# Closure induction implementation report

The `closure@0` certificate checker now implements supplied-invariant induction
for both positive and reflexive-transitive closure, including Body edges,
captured parameters, arbitrary unary formulas, and nested binders. New
certificates use `ve-tableau-closure-checker@1`; `@0` replay is preserved.
The original FOL checker and its theorem are unchanged.

The new Lean semantic, substitution and branch-preservation proofs feed the
existing `VE.Closure.Tableau.checkCertificate_sound` theorem. Its conclusion is
still `Entails` over every admissible structure, with no certificate-soundness
assumption. The five new named theorems are included in `Audit.lean` and
`axioms.txt`; the audit covers 236 named theorems in 52 source files and permits
only `propext`, `Classical.choice`, and `Quot.sound`. The underlying path
induction theorem uses no axioms. No proof placeholders or native evaluation
proofs were introduced.

The new differential corpus checks 36 accepted certificates and 17 forgeries
in Python and Lean. It covers Named/Body, tc/rtc, nested closure in the invariant,
captured parameters through several binders, wrong versions, missing proof
branches, wrong targets/sorts, ill-scoped or altered invariants, and missing
base/preservation hypotheses. Additional tests cover universal conclusions over
empty sorts, exhaustive two-node graph/invariant interpretations, and a cyclic
policy model plus a checked countermodel after breaking preservation.

Regression checks replay all 63 old closure cases with checker version `@0`,
all 15 nonempty committed mini-paper certificates, and the unchanged frozen
882-case v0 corpus (732 accepted, 150 rejected). Existing tests and certificate
files were not rewritten. New example certificates live in a separate
[supplement](../usecases/closure-induction/README.md).

T9 and T9e now certify using their original premises and conclusions. The
cyclic-policy example certifies that no G member reaches R by tc or rtc.
T9 and the policy use automatic search with supplied invariants; T9e has an
explicit untrusted proof schedule. Automatic invariant discovery, general proof
completeness, and cyclic proof acceptance remain outside this change. Rust has
closure evaluation but no certificate checker to extend; that boundary is
documented in [the Rust scope](rust.md).

Changing checker source also changes its honest build fingerprint. Six existing
P1 tests reconstruct historical paid-request bytes and consequently exposed a
separate compatibility issue: they were regenerating historical findings with
the current fingerprint. `experiments/p1_history.py` now loads the exact retained
finding from the original ledger and reuses it only after the current checker
replays the evidence and matches every field except the build fingerprint.
Changed semantics, artifact commitments, checker versions, or witness results
fail closed. The current checker still reports its actual new build ID. Paid
cache equality, the historical ledger, and frozen source gates are unchanged.
No model calls were made.

Reproduction commands are in [the rule specification](spec/closure-induction.md).

Final serial validation (2026-09-22):

| Check | Result |
|---|---|
| Full Python suite, `VE_LEAN_PREBUILT=1 uv run pytest -q` | 1,422 passed; 3 skipped; 1 live test deselected |
| `lake -d lean build`, `LEAN_NUM_THREADS=1` | Passed (90 build jobs) |
| `lean/audit.py` | 236 theorems / 52 source files; only the standard allowlist |
| Rust, `cargo test -j 1 --all-features --locked ... -- --test-threads=1` | 16 passed |
| [New Python/Lean differential corpus](../conformance/induction-report.json) | 36/36 accepted; 17/17 forgeries rejected in both |
| [Four example deductions](../usecases/closure-induction/results.json) | 4/4 accepted in Python and Lean |

The three skips are the optional `llguidance` and `xgrammar` backends and an
uncached pinned tokenizer; its test deliberately never downloads. All commands
used `UV_CACHE_DIR=/private/tmp/ve-uv-cache-induct`. No required work remains.
