# Batch 14c: n-ary core definitions

## Scope and owner

Lean now elaborates three to six argument `defined` predicates on the core family in dependency order. It regenerates their Background biconditionals, computes defined model tables under the route budget, checks the biconditionals, and uses the result for evaluate, countermodel, certificate, model validation and core family calls. Python's retained n-ary exclusion in `definitions._compile_lean`, `validation.model_in_scope` and `validation.family_in_scope` is gone. The old Python implementation remains for direct entries that cannot be embedded in an environment and for environments outside Lean's model scope; it is not selected for an identity-bound n-ary declaration within that scope.

The Lean route reuses the FOL definition decoder and budget for unary and binary declarations and extends the core environment for n-ary ones. The schema of the regenerated Background is derived from the Lean `ResponseShape` declarations. The core formula encoder is shared by the service and route.

## Acceptance items

| Item | Type | Evidence or owner |
|---|---|---|
| Core n-ary Background, derived table and Python route | AGENT | `tests/test_b14c.py`, `tests/test_definitions.py` |
| Fully typed and request-bound relayed responses | AGENT | Generated response schemas; relay mutation gate |
| Theorem audit, statement diff and trust ratchet | AGENT | `lean/audit.py`, `tools/lean_statements.py`, `tools/trust_map.py` |
| Seeded test faults in each changed product language | AGENT | `evidence/mutants.json` |
| Full suite, Rust tests and Lean build on committed HEAD | AGENT | `evidence/gate.json` or `gate-result.json` |
| Independent review and final DRI acceptance | HUMAN | DRI |
| Three-day operational soak after batch 13b | EXTERNAL | DRI, per plan section 8 answer 1 |

## DRI rulings

- **SIGNED by standing ruling R6 (DRI-RULINGS.md):** the added Lean validation, table computation and response checks replace the deleted Python n-ary fallback decision path. `tools/trust_map.py --since f1b719c7` measures the branch relative to the merge base; the recorded trust budget is a ratchet. The changed source and deleted fallback are covered by `tests/test_b14c.py` and the Lean audit.
- **SIGNED by standing ruling R8/R11 (DRI-RULINGS.md):** Python checks the Lean response's typed schema and its binding to the request. The generated Background remains a Lean decision. The relay mutation gate retypes, empties, drops and duplicates fields of genuine responses.
- **SIGNED by standing ruling R12 (DRI-RULINGS.md):** Lean audits, statements, checker pins, response schemas and gate collection were regenerated through `tools/regen_generated.py`.
- **D4:** batch scope, corpus, latency and gate evidence are saved and checked at the batch gate and merge. No permanent test reads this batch's report numbers.

## Seeded bugs

`evidence/mutants.json` records three planted and removed faults: a Python family scope exclusion, an erased Lean biconditional, and a Lean evaluator that omits every derived tuple. Each caused its named test to fail; all focused tests passed after restoration.

## Deletion ledger

The branch's non-merge commits relative to its merge base remove **23 production Python lines** and **176 Lean lines**, and add **419 Lean lines** (excluding generated Audit manifests). The Python deletions remove the n-ary predicate scope detector and its `model_in_scope`/`family_in_scope` exclusions, and the `_compile_lean` n-ary fallback call. Lean deletes the separate n-ary validation walk and formula encoder in `Service/Standalone.lean`; the callers now use `Core.Layers.decodeLayered`, `completeModel` and `Core.Wire.encodeFormula`. The new Lean Background generator also replaces the FOL-only core branch. `tests/test_b14c.py` checks each changed path.

## Behaviour and limits

This batch changes the authority for identity-bound n-ary core definitions to Lean. The corpus comparison and differential fuzzer results below determine whether that changes any public answer. Search-internal candidate evaluation and the standalone direct-entry elaborator remain in their already recorded scopes. This batch does not change the document wrapper or norm-defaults logic addressed in the sibling 16d review.

## Evidence

The final report records the exact branch line counts, corpus A/B, differential fuzzer, pilots, latency, and full release gate from saved evidence on the final HEAD.
