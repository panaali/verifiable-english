## BRANCH

`codex/closure`, merging `ve-integration` at
`6798e034c4aa7082dafacbb7b130879cd4eec4f6` into closure head `151b78e`.

## SUMMARY

Merge integration's certificate-v2 proof, 124-expansion bound, corrected fixtures and fair prover into closure@0.
Keep integration's single `complementary_sound` proof; its generality equals the removed `compoundClosed_sound` proof, and its version-1 gate is preserved.
All four `Tableau*.lean` files are byte-identical to integration, including the exact `checkCertificate_sound` statement.
Extend only Reach paths in Python replay and search; retain the Lean closure certificate profile gate, including Reach-free v0.1 queries and spoofed v0 versions.
Freeze the entire pre-closure v0 certificate corpus and require all 882 complete replay results to remain identical.

## VERIFY

Run serially from the repository root:

```sh
export UV_CACHE_DIR=/private/tmp/ve-uv-cache
export CARGO_HOME="$PWD/.cargo-home"
export CARGO_TARGET_DIR="$PWD/rust/target"
export CARGO_BUILD_JOBS=1
uv run python conformance/replay_baseline.py
(cd lean && lake build)
uv run python lean/audit.py
VE_LEAN_PREBUILT=1 uv run pytest -q
cargo test -j 1 --locked --manifest-path rust/Cargo.toml -- --test-threads=1
uv run python conformance/certificates.py --report conformance/certificates-report.json
git diff --check
git diff --exit-code 6798e034 -- 'lean/VE/Tableau*.lean'
```

- `lake build`: successful, 60 build jobs; pinned Lean 4.24.0.
- `lean/audit.py`: **33 source files, 141 named theorems**, only `propext`,
  `Classical.choice`, `Quot.sound`; `axioms.txt` regenerated from that output.
- Full pytest: **731 passed, 3 skipped in 154.80 seconds**, including Lean and
  Rust conformance, the 5,000-case Rust v0 fuzz stream, closure evaluation and E0
  witnesses, all six profile/version gate combinations, and the entire frozen
  v0 replay corpus. The skips are unavailable `llguidance`, unavailable
  `xgrammar`, and the explicitly unsupported Rust closure corpus.
- Cargo: **11 integration tests passed** (six conformance, five search), no
  unit/doc-test failures; one compilation job and one test thread.
- Regenerated certificate report: **732/732 accepted by Lean, 150/150 forgeries
  rejected**, byte-identical to integration's report. All **811 search attempts**
  remain recorded: 732 `Found`, 77 `NotFound`, two `ResourceLimit`.
- Frozen before/after replay: **882/882 full results identical**, 732 valid and
  150 invalid; expected verdicts come from the pinned pre-closure code, not this
  branch. The focused Python closure/replay run also passed (36 tests).
- `git diff --check` and the no-diff comparison of all four `Tableau*.lean`
  files pass. There are no unresolved merge conflicts.

The complete trusted Python replay inventory below is relative to the merged
integration commit, not a three-dot diff (the histories had multiple merge bases):

| Definition | Every branch change and its justification |
|---|---|
| `_Replayer.replay` | Recognizes `closure-plus@0` and `closure-star@0` in addition to `expand`; after reconstructing the expansion, requires the tag to match the targeted formula's kind. Child count, exact fields, recursion/step budgets, and recursive checking remain unchanged. Wrong tags, induction tags and supplied closure parameters are rejected. |
| `_closed` | Adds signed Reach keys using `closure.congruence_key` after the existing equality union-find. Equal endpoints and captured parameters denote the same relation and reachability proposition, so opposite signs contradict. Edge kind, Body sort, all local indices and structural distinctions remain represented; no finite-model approximation or inclusion rule is used. Existing v0 literal/equality/compound tests are unchanged. |
| `_derive` | Adds a Reach branch that rejects supplied parameters, obtains the homogeneous sort from the scoped left endpoint, unfolds the formula once and preserves sign/bindings. It uses the existing target validation and one-shot expansion guard. The two logical rules are justified separately below. |
| `_apply` | No change; AST-identical to integration. Its existing one-shot bookkeeping covers closure, with fresh witnesses introduced only by ordinary delta expansion. |
| `_binding` | Selects `ve-tableau-closure-checker@0` for closure environments; v0 still selects `ve-tableau-checker@2`. Environment identity, ordered premise identities and conclusion identity retain the same binding structure. This separates certificate profiles; it adds no logical inference. |
| `_kind` | Recognizes Reach as `closure`; classification of every v0 constructor is unchanged. |
| `_rule` | New deterministic formula-to-tag helper: Reach selects its versioned plus/star rule, everything else selects `expand`. |
| Module imports/version | Adds `Reach`, `Named` imports and `CLOSURE_CHECKER_VERSION`; the v0 checker version stays `ve-tableau-checker@2`. |

New unfolding rules, valid under either sign:

- `closure-plus@0`: `R+(a,c) ↔ R(a,c) ∨ ∃b (R(a,b) ∧ R+(b,c))`, because every finite nonempty path is one edge or its first edge followed by a finite nonempty suffix, and concatenation gives the converse.
- `closure-star@0`: `R*(a,c) ↔ a=c ∨ R+(a,c)`, because a finite path has either zero length (equal endpoints) or positive length.

The new replay dependency `ve/closure.py` implements `map_free`, `shift` and
`edge_at` for capture-avoiding substitution (quantifiers introduce one local,
Body edges two); `unfold` reconstructs precisely those equivalences;
`congruence_key` substitutes equality representatives only for free parameters
and constants, retaining local indices, nested edges and endpoint direction.
Substitution/equality soundness here is a mathematical justification and tested
implementation, not a Lean proof of this Python code. No induction/cyclic rule
was added. Tests cover both signs, both kinds, both edge variants, wrong tags,
supplied parameters, nested Body capture and equality congruence.

`_initial_branch`, `_term_token`, `_validate_inputs`, `_apply` and
`check_entailment_certificate` are AST-identical to integration. The search-only
changes are `_instance_key` and `_connection_key` traversals for Reach, including
Body's two locals, and `_Searcher.search` using `_rule` to emit a closure tag.
The fair scheduling, ground-connection ordering, iterative instantiation bounds
and all v0 key paths are retained; these hints cannot accept a certificate.

For v0 documents, type checking excludes Reach at every depth, so the new
closure derivation and congruence paths are unreachable. Existing expansion
rules, version binding, replay depth and step budgets remain unchanged, and new
closure tags cannot expand a v0 formula. The frozen regression confirms **all
882 original results match exactly**, including validity, status, steps and
diagnostics: **732 accepted and 150 rejected**. Its generator runs the pinned
integration source in an isolated temporary checkout, so the expected results
do not come from the new checker. All search outcomes, including unsuccessful
attempts, remain in the fixture's generation report; only actual certificates
are replayed. This is exhaustive over that corpus, not all possible v0 inputs.

Every `lean/VE/Tableau*.lean` file is accounted for:

| File | Net change from integration; merge resolution |
|---|---|
| `Tableau.lean` | None; retain integration's shared certificate-version documentation and all definitions/proofs. |
| `TableauClosure.lean` | None; remove this branch's duplicate `compoundClosed`/`compoundClosed_sound` and its unconditional insertion into `closed`; retain only integration's `complementary`/`complementary_sound`. Both prove contradiction from exact equal formulas/bindings and opposite signs; the removed proof is not more general. |
| `TableauChecker.lean` | None; retain version-2-only compound closes and fuel 125 (124 expansions plus a close), including integration's `replay_sound` proof and the exact `checkCertificate_sound` statement. |
| `TableauChecks.lean` | None; retain all integration guards. |

Related Lean boundary changes: `CertificateWire.runCase` still explicitly
rejects every `ve.core@0.1` environment before certificate replay. `Main.lean`
dispatches non-certificate v0.1 cases to the closure evaluator while preserving
integration's per-case JSON/depth errors; certificate requests always use the
gated adapter. `Audit.lean` removes the duplicate theorem entry, retains all
closure metatheory entries and integration's complementary theorem; `axioms.txt`
is regenerated from the successful audit. The separate `VE/Closure/*.lean`
metatheory remains as documented in `lean/CLOSURE.md`.

## GAPS

Python closure certificate replay is not Lean-certified: capture-avoiding
substitution and tableau branch-preservation proofs for Reach remain open.
Lean proves the closure evaluator/path semantics but rejects all closure
certificate environments. Full Body/document round-trip and general extended
printer injectivity, JSON/compiler/runtime correspondence and Python refinement
also remain outside the proof claims.

Rust still implements v0 only. `test_rust_closure_evaluation` explicitly skips
`conformance/closure.json` with a documented unsupported-profile reason; closure
E0 witnesses are checked by Python/Lean. All seven v0 fixture files and the
5,000-case v0 fuzz stream remain in the Rust conformance tests. Optional
`llguidance` and `xgrammar` are unavailable, so their two existing tests skip.

## PLAN CHANGES

No new scope. Record closure/integration reconciliation, the single version-2
proof, preserved profile gate, 141 audited theorems and the 882-case v0 replay
regression. Keep the existing gaps for Lean-certified closure replay and Rust
closure support open.
