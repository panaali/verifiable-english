# Batch 14b behaviour delta

The saved [1,350-record A/B comparison](evidence/corpus-ab.json) covers 150 generated documents, 50 per closure, core and order family, across premises, certificate replay, proof search, absent packages, no evidence and three finite models per document. The two recordings contain the same inputs. 1,334 answers are identical. The full section 5.1 corpus gate remains to be recorded.

## Four n-ary core documents: 16 changes

Corpus document indices 13, 28, 64 and 94 have a well-typed n-ary atom inside a lower regulated predicate's outcome. The old Python fallback did not substitute the atom's variables when it expanded that outcome for conflict search. It raised `TypeMismatch` from the resulting ill-typed candidate. The new candidate expansion substitutes those variables, and the Lean family route checks every reported witness or certificate. The affected operations are `conflict-prove` and `conflict-model-0/1/2` for each document; exact base/head records are in `evidence/corpus-ab.json`.

These are rejection-to-answer changes, outside standing rulings R1–R14. **DRI signature requested, not yet recorded (HUMAN, owner: DRI).** The corpus itself checks each changed answer; `test_non_first_order_norms_are_dispatched_and_match_python` and `test_non_first_order_conflict_witness_is_checked_by_lean` cover the new route. No answer is presented as checked without Lean's replay.

## Standing rulings and ownership

* **SIGNED by standing ruling R8 (DRI-RULINGS.md).** Every family-norms response is typed by the Lean-owned generated schema, and the Python adapter binds order, premise labels, target names and sorts, target lists, layer counts and witness target to the request. `test_every_field_dropped_emptied_nulled_and_retyped_agrees_with_lean`, `test_genuine_responses_are_accepted_by_schema_and_lean`, and the unbound-row tests in `test_stage2_norms.py` check the contract.
* **SIGNED by standing ruling R6 (DRI-RULINGS.md).** The trusted Lean V budget rises by 607 lines, from 37,154 to 37,761, to replace the deleted Python `_first_order`/`_family_norms` decision path and to type and bind the new route. `docs/trust-baseline.json` records the allowance and reason; `tools/trust_map.py --check` passes with zero unclassified declarations.
* **SIGNED by standing ruling R12 (DRI-RULINGS.md).** The frozen inventory, checker pin and response schema are regenerated through `tools/regen_generated.py`; no generated file is hand edited. `tools/regen_generated.py --check` is the check.
* The authority move for the 14b family norms scope is the explicit 14b row of the DRI-approved draft-3 plan. The Python duplicate removed in the same batch is mapped in [LEDGER.md](LEDGER.md).
