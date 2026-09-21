## BRANCH

`codex/integration-fix`, based on `ve-integration` at `a406e8a`.
Implementation commit: `cf3a380`.

## SUMMARY

The oracle merge renamed the deliberately invalid `separated` fixture to `g1` without updating conformance's exception, and Python's version-2 certificates met a Lean checker supporting only version 1.
The completeness regression came from whole-formula-only connection hints: unused constants delayed the useful existential witness pair until the depth frontier exhausted 10,000 search steps.
Check the unchanged `g1` countermodel; port and prove Python's existing version-2 closure in Lean, preserving version-1 rules; rank ground connections within each universal's parameter choices without changing Python replay.
Align Python/Lean at 124 expansions plus a close, preserve the 256-level JSON cap, and report oversized cases individually within batches.
Regenerated conformance: 732/732 certificates accepted and 150/150 forgeries rejected, with every search outcome retained.

## VERIFY

All commands run serially from the repository root, with Rust compilation limited
to two jobs and Rust tests to one thread:

```sh
export UV_CACHE_DIR=/private/tmp/ve-uv-cache
export CARGO_HOME="$PWD/.cargo-home"
export CARGO_TARGET_DIR="$PWD/rust/target"
export CARGO_BUILD_JOBS=2
uv run pytest -q
(cd lean && lake build)
uv run python lean/audit.py
cargo test -j 2 --locked --manifest-path rust/Cargo.toml -- --test-threads=1
uv run python conformance/certificates.py --report conformance/certificates-report.json
git diff --check
```

- Final full pytest: 686 passed, 2 optional-backend skips in 115.38 seconds,
  including Lean and Rust conformance.
- `lake build`: all 41 build jobs complete.
- Audit: 25 Lean source files, 111 named theorems; only the standard allowlist.
- Cargo: all 11 integration tests pass; no unit/doc-test failures.
- Certificate report: both 320-query constructive cohorts fully prove; the 160
  unconditioned queries give 82 `Found`, 76 `NotFound`, 2 `ResourceLimit`;
  worked examples give 2 `Found`, 1 checked counterexample/`NotFound`; eight
  weakening regressions all prove and replay in Lean.
- The nine trusted Python definitions (`_initial_branch`, `_kind`, `_term_token`,
  `_closed`, `_derive`, `_apply`, `_binding`, `_Replayer`,
  `check_entailment_certificate`) are AST-identical to `a406e8a`.
- New regressions cover all compound closure constructors, version-1 rejection
  of version-2-only closes, opposite compounds with different witness bindings,
  strict malformed JSON, the 124/125 expansion boundary, and 126/300-deep traces
  between valid batch neighbors. Search refuses proofs beyond its depth budget.

The fixture formulas did not change meaning: the one-service countermodel still
refutes `g1`; `g2` and `g3` still prove. The forged version now uses an actually
unknown version, and the forged delta case still expands a delta instead of
mutating a version-2 immediate close.

The regression generator is `completeness_regression` in
`conformance/certificates.py`: premise
`exists x exists y (not (not r(y,y) or r(x,x)) and r(x,y))`, with the conclusion
obtained by weakening that outer `and` to `or` and applying the specified
recursive De Morgan transformation twice. It tests zero, one, two and four
unused constants, both with and without quantifier dualization.
The constant-free variants already prove on integration; the failing variants
below reproduce the old-`Found`/new-`ResourceLimit` behavior.

| Case | Oracle before fairness (`7a85024`) | Integration (`a406e8a`) | Fixed |
|---|---:|---:|---:|
| One constant, including quantifier duals | Found, 84 steps | ResourceLimit, 10,000 steps | Found, 24 steps |
| Two constants, connective-only transformation | Found, 83 steps | ResourceLimit, 10,000 steps | Found, 16 steps |

All eight fixed variants take 16 or 24 steps. The per-universal instantiation
bound, priority classes and least-used/oldest formula order are unchanged;
the extra hint only ranks parameters within the same formula. It cannot close
a branch or suppress an expansion. Reproduce the comparison without touching
another worktree:

```sh
uv run python - <<'PY'
import subprocess, sys, types
from conformance.certificates import completeness_regression
from ve.entailment import prove_entailment
for revision in ('7a85024', 'a406e8a', 'fixed'):
    if revision == 'fixed':
        prove = prove_entailment
    else:
        name = 've.integration_baseline'
        module = types.ModuleType(name)
        sys.modules[name] = module
        source = subprocess.check_output(
            ['git', 'show', revision + ':ve/entailment.py'], text=True)
        exec(compile(source, revision, 'exec'), module.__dict__)
        prove = module.prove_entailment
    for constants, duals in ((1, True), (2, False)):
        result = prove(*completeness_regression(constants, duals), max_steps=10000)
        print(revision, constants, duals, result.status, result.steps)
PY
```

## GAPS

- `llguidance` and `xgrammar` are not installed; their two optional tests skip.
- These are bounded development regressions, not a completeness theorem or a
  rerun of the historical 602-pair fairness benchmark. Two unconditioned corpus
  queries still reach the proof budget; none are removed from the denominator.
- JSON correspondence and cryptographic correctness remain tested boundaries,
  not new refinement theorems. A case whose JSON is too deep to decode has a
  zero-based `case_index` in its error because its ID is unavailable.

## PLAN CHANGES

No scope change. Update the P9 evidence count in `PLAN.md` from 721/721 to
732/732 certificates; the forged denominator remains 150/150.
