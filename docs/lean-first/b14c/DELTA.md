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

- **SIGNED by standing ruling R1 (DRI-RULINGS.md):** a model that supplies its own n-ary defined table still raises `InvalidModel`, but Lean's `InvalidModel(definitions): supplied table for defined predicate` replaces the base's `InvalidModel: supplied table for a defined predicate`. No quoted name or JSON path is lost, and the new generator names the fault more specifically. `targeted_ab.py` checks the saved `evidence/targeted-ab.json` for the same code, path and quoted names and the retained error details.
- **SIGNED by standing ruling R6 (DRI-RULINGS.md):** the added Lean validation, table computation and response checks replace the deleted Python n-ary fallback decision path. `tools/trust_map.py --since f1b719c7` reports **139 trusted lines** of growth relative to the merge base: K +0, S +8, untied V +131. That raw comparison exits 1 because it knows no new signed allowance; R6 signs this class. The generated `docs/trust-baseline.json` records the growth and owner-switch reason in its history; `tools/trust_map.py --check` passes with zero unclassified declarations. The changed source and deleted fallback are covered by `tests/test_b14c.py` and the 5,260-declaration Lean audit.
- **SIGNED by standing ruling R8/R11 (DRI-RULINGS.md):** Python checks the Lean response's typed schema and its binding to the request. The generated Background remains a Lean decision. The schema generated from Lean also requires `background` and `premises` to be equal and their rows to align with `generators`; `test_nary_background_relay_refuses_missing_or_extra_generated_rows` checks this with missing, repeated and changed rows. The relay mutation gate retypes, rebinds, empties, drops and duplicates fields of genuine responses. Its route-specific run on the new n-ary fixture refused 5,477 of 5,503 mutations, with 26 pre-existing allowed classes and no failures (`evidence/route-mutations.json`).
- The two structural response relations, `x-same-length` and `x-equal-fields`, are classified in `test_lean_shapes_are_classified` and `test_adr_relation_keywords`. They compare response fields to each other and do not add a request-binding relation to the signed D1 list. Both architecture inventory tests pass.
- **SIGNED by standing ruling R12 (DRI-RULINGS.md):** Lean audits, statements, checker pins, response schemas and gate collection were regenerated through `tools/regen_generated.py`.
- **D4:** batch scope, corpus, latency and gate evidence are saved and checked at the batch gate and merge. No permanent test reads this batch's report numbers.

The statement inventory gained 43 declarations and changed or removed none. The Lean audit checked all 5,260 named theorem declarations with only the standard axiom allowlist. No approved theorem statement was altered.

## Seeded bugs

`evidence/mutants.json` records three planted and removed faults: a Python family scope exclusion, an erased Lean biconditional, and a Lean evaluator that omits every derived tuple. Each caused its named test to fail; all focused tests passed after restoration. `test_nary_metered_zero_budget_is_unknown` checks that the changed metered caller returns `ResourceLimit` at zero budget and a true value with adequate budget.

## Deletion ledger

The branch's diff relative to `main` removes **24 production Python lines** and **178 Lean source lines**, and adds **439 Lean source lines** (excluding generated Audit manifests). The Python deletions remove the n-ary predicate scope detector and its `model_in_scope`/`family_in_scope` exclusions, and the `_compile_lean` n-ary fallback call. Lean deletes the separate n-ary validation walk and formula encoder in `Service/Standalone.lean`; the callers now use `Core.Layers.decodeLayered`, `completeModel` and `Core.Wire.encodeFormula`. The new Lean Background generator also replaces the FOL-only core branch. `tests/test_b14c.py` checks each changed path.

## Behaviour and limits

This batch changes the authority for identity-bound n-ary core definitions to Lean. The corpus comparison and differential fuzzer results below determine whether that changes any public answer. Search-internal candidate evaluation and the standalone direct-entry elaborator remain in their already recorded scopes. This batch does not change the document wrapper or norm-defaults logic addressed in the sibling 16d review.

## Evidence

The five-run same-host route measurement (`latency.py`, `evidence/latency.json`) found a 78.239 ms base versus 74.336 ms head median CPU on the unchanged core Background case. The n-ary evaluate case took 73.386 ms CPU and 721.813 ms wall at the median, within the plan's absolute document budget. The final report records the corpus A/B, differential fuzzer, pilots and full release gate from saved evidence on the final HEAD.

`tools/difffuzz.py --ci` passed with no new findings. Its reviewed baseline remains 250 entries (222 seen in the CI sample); the report is saved as `evidence/difffuzz.json`.

Fourteen dated differential fuzz samples covered 369,908 inputs. They found 306 signatures outside the fixed 250-entry CI baseline, and all 306 reproduced on the base revision; none is new to this batch. The saved `evidence/date-seeds-summary.json` and `evidence/date-seeds-base-replay.json` record each seed and the replay check. `tools/relay_lint.py` passed on 13 relayed modules and six relayed functions.
