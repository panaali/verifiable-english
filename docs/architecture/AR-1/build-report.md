# AR-1 build report

## Change

`lean/audit.py` now reads ranged theorem declarations and their declaring modules from the compiled `lean/declarations.txt` inventory. `--write` generates both audit manifests, with sorted theorem names and imports for precisely their declaring modules, then writes `axioms.txt`. `--check` regenerates both manifests in memory, compares their bytes, checks every source module hash in `declarations.txt`, compiles both manifests, and compares the axiom output. The source scan still rejects forbidden tokens and the `admit` tactic; its theorem-name regex was removed.

`tools/lean_statements.py --declarations-only` breaks the generation cycle. The generated-file registry regenerates declarations, manifests, the frozen hash of `VE/Audit.lean`, and statements in that order. The corresponding precommit and merge checks were updated.

## Measured outcome

| Inventory | Base `main` | AR-1 code commit |
| --- | ---: | ---: |
| Lean source modules in `declarations.txt` | 479 | 479 |
| Ranged theorems in both manifests and `axioms.txt` | 5,196 | 5,711 |
| Statements in `statements.txt` | 4,755 | 5,270 |
| Predicates in `predicates.txt` | 589 | 589 |

All 515 added audit names, with no removed names, are in [added-theorems.txt](evidence/added-theorems.txt). The three Prop-class instances compiled as theorems are `VE.Discourse.instLawfulBEqTerm`, `VE.Discourse.instLawfulBEqFormula`, and `VE.Order.instLawfulBEqValue`; all three occur in the generated manifest and axiom record. There are no new Lean declarations or VE verdict, wording, or wire changes. No user-visible delta needs a standing ruling signature.

The old hand-maintained manifests received 202 edits in the plan's 14-day measurement window. AR-1 replaces each future hand edit with regeneration. The merge rule is: **for a conflict in either `Audit.lean`, take either side and run `python3 lean/audit.py --write` after regenerating `declarations.txt`**. `question-answering/q2` and `readings-defaults/rd6b` also edit these generated manifests; regeneration resolves that shared-inventory overlap. `tools/regen_generated.py` is shared with AR-3 and AR-5a, so its AR-1 edit only changes the audit entries and their order.

## Verification

- `tests/test_lean_audit_record.py`: 14 focused tests, including a scratch theorem that fails `--check` before `--write` and passes afterward, a stale source hash, and forbidden proof tactics.
- `tests/test_lean_conformance.py -k source_audit`: 35 passed.
- `tests/test_regen_generated.py tests/test_precommit_hook.py`: 81 passed.
- `tools/mutants.py`: 3 of 3 seeded faults were caught; see [mutant-results.json](evidence/mutant-results.json). The tested faults were dropping a ranged theorem, accepting a stale module hash, and skipping the forbidden `admit` check, all in `lean/audit.py`.
- The selected-test command and final release gate results are recorded in the final gate evidence after their foreground runs complete.

## Acceptance ownership

| Item | Owner | Status |
| --- | --- | --- |
| Generated manifests, exact imports, hashes, axiom allowlist, focused tests | AGENT | Complete |
| Full release gate and saved gate JSON | AGENT | Pending final gate run |
| Independent review | HUMAN | Deferred to the review owner after handoff |
| External evaluation | EXTERNAL | Not applicable to this tooling batch |

The DRI's D4 ruling applies to the saved batch evidence: it is checked at the batch gate and merge, with no permanent report test. No Lean-owned answer binding or product code changed, so the AR-6 relay findings do not recur here.
