# gi-1 build report

Status: implemented; the chain runs the final full gate on the committed HEAD.
HEAD: `feature/gi-1` tip at handoff.
Changed: both generated audit manifests leave every default Lake target; Lean audit remains a full gate stage and now runs in x86 essentials through its selected test.
Open items: gi-2a follows; no DRI signature is reserved. Pilot bytes expected: 0.

## Delivery and checks

| Acceptance item | Owner | Evidence |
|---|---|---|
| DESIGN §7 step 1: remove `VE.Audit` from the default root, preserving build of its other modules | AGENT | `lean/VE.lean`; `test_every_lean_source_is_built_by_the_default_build` |
| Move the ResponseShape manifest outside `ResponseShape.*`; update its sole owner, registry, merge rule, layer and path tests | AGENT | `lean/ResponseShapeAudit.lean`, `lean/audit.py`, `tools/regen_generated.py`, `.gitattributes`, `tools/layer_policy.py`; `test_gi1_names_every_default_build_route_of_every_manifest`, `test_every_pattern_names_a_tracked_file_and_owns_it` |
| Update the hand-reviewed JSON classification and route recipe path | AGENT | `ve/assurance-manifest.json`, `docs/ROUTE-RECIPE.md`; `test_every_json_handling_lean_file_is_classified`, `test_every_path_named_in_agents_md_exists[ROUTE-RECIPE.md]` |
| Exclude both manifests from the statement dump build and imports; retain their generated hashes in declarations | AGENT | `tools/lean_statements.py`; `test_gi1_dump_build_omits_both_audit_modules`, `test_committed_manifests_are_the_generated_ones`; no `lean/statements.txt` diff |
| Derive the two `RUN_ONLY` entries from `audit.MANIFESTS`, and reject either manifest returning to the default closure | AGENT | `tools/check_lean_imports.py`; `test_every_lean_source_is_built_by_the_default_build`; Lean import mutant below |
| Full gate and candidate checkout run `Lean audit`; x86 essentials audits when the Mac leg is absent | AGENT | `test_lean_audit_stage_runs_in_full_and_candidate_mode`; `tests/test_lean_service_audit.py` matches x86 essentials' `test_lean_service*.py` selector and runs `lean/audit.py` on its x86 scratch path; `test_x86_audit_refuses_failure_and_accepts_success`; `x86_essentials.essential_files()` probe includes the file |
| Signed statement gate: no theorem statement changes | AGENT | `git diff main...HEAD -- lean/statements.txt` is empty; DRI decisions `dri-decisions-20261028-gen-inv-design.md` item 1 and `-b.md` items 1, 3 |
| Final candidate gate | EXTERNAL, merge chain | Runs on committed HEAD after handoff, per BUILDER_TEST_BUDGET; not run by builder. |

The full gate's `Lean audit` stage checks the two generated manifests, every named theorem's axiom dependencies, the committed `axioms.txt`, and source freshness. The committed-manifest test checks generated content. The x86 essentials selected test runs that same audit for every x86 candidate. These now cover the manifest checks that default `lake build` previously got by compiling `VE.Audit` and `ResponseShape.Audit`; default Lake still compiles all ordinary modules and their `#guard`s.

## Timing and trust

`timing.json` saves all six wall times on the same VM. Each run changed whitespace in the declaration of `ResponseShape.CaseDeciders.all_complete`, ran `lake build`, and restored the source. Before: 530.822, 401.603, 439.321 s (median **439.321 s**). After: 291.379, 419.673, 610.216 s (median **419.673 s**). The measured median difference is 19.648 s (4.47%); the wide spread limits confidence in the size of the gain. This resolves the design's assumed build-time gain only for this VM and theorem.

`tools/trust_map.py --check`: K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0. No new trusted definition, R16 allowance, FOLLOW-UPS row, or trust-mutants run applies. `DELTA.md` has no rows because answers are unchanged. Generated inventories were rewritten by `tools/regen_generated.py --write`; the statements and axiom record are unchanged.

## Test runs

The focused new tests passed (9 tests), the default-build guard passed, the full default `lake build` passed (1159 jobs), and `lean/audit.py` passed (668 sources, 7428 named theorem declarations). The selected Mac run reached 425 of 437 units before stopping at three failing units: the missing assurance path, the missing route recipe path, and five errors in `test_trust_mutants.py` caused by removing the direct imports from `lean_statements.SCRIPT`. After the three fixes, the two path test IDs passed, the five trust-mutants IDs passed, and the 12 units not started by the early stop passed (10,410 tests). The chain runs the final full gate on this commit.

The branch overlap check found old refs `foundation/me-1` (root, registry, merge rule) and `infra/arch-AR-1` (audit and dump files); gi-1 is the first signed implementation item of the merged design, and no in-flight work was merged into this branch. Generated files are covered by R12. `tools/gate.py` was not changed.

## Seeded bugs removed

| Behavior | Mutated file | One failing test |
|---|---|---|
| Audit import cannot re-enter default build (Lean mutant) | `lean/VE.lean`: restored `import VE.Audit` | `test_every_lean_source_is_built_by_the_default_build` |
| Dump cannot compile manifests (Python mutant) | `tools/lean_statements.py`: included all modules in its build | `test_gi1_dump_build_omits_both_audit_modules` |
| Committed manifest path stays generated (Python mutant) | `lean/audit.py`: restored old ResponseShape path | `test_committed_manifests_are_the_generated_ones` |
| Full and candidate gate stage stays present | `tools/gate.py`: changed stage label | `test_lean_audit_stage_runs_in_full_and_candidate_mode[True]` |
| x86 must reject an audit failure | `tests/test_lean_service_audit.py`: accepted nonzero exit | `test_x86_audit_refuses_failure_and_accepts_success` |

All five test runs exited 1 and each mutated file was restored. The accepting side is covered by the focused passing runs; `test_gi1_route_guard_accepts_exactly_nondefault_modules` also probes an exact nondefault module, direct import, and globbed module.

## Next item

gi-2a: train-only registry field, inventory overlay and `inventory_path` accessor.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. (no relay or response change).
2. Every deliverable and rule: PASS (`test_gen_inv_design.py`, `test_lean_default_build.py`, and the delivery table above).
3. Tests and gates can fail: PASS (five seeded bugs and their named failures above).
4. Python, Lean and Rust agree: N.A. (no answer or Rust behavior change).
5. R8 binding: N.A. (no relayed field change).
6. Gate evidence matches final HEAD: N.A. (the chain owns the final-HEAD full gate; `git status --short` is clean).
7. No unsigned item: PASS (`tools/trust_map.py --check`, `DELTA.md`).
8. Every user-visible change in DELTA: PASS (`lean/statements.txt` and `lean/axioms.txt` byte-identical; no answer path changed).
9. Test selection finds the checks: PASS (selected run recorded below).
10. Lean statements and proofs: PASS (empty `lean/statements.txt` diff; `test_committed_manifests_are_the_generated_ones`).
11. Budgets, limits and deadlines: N.A. (no runtime limit changed).
12. CPU or memory regression: N.A. (no evaluator changed; build wall times are in `timing.json`).
13. Removed test trailers: N.A. (no test removed or renamed).
