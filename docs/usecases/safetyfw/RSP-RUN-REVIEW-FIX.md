# RSP run review fix

Status: F1–F3 fixed; no open A/B finding or DRI signature requested.
HEAD: `infra/usecase-rsp-run` branch tip; implementation commit `a5ce6a414`.
Scope: RSP answer harness, saved results, regression tests and explanation; frozen PLAN section 6 and product sources unchanged.
Checks: RSP regressions 39 passed; selected plan 47 units passed; `lake build` and `lean/audit.py` passed.
Known red on main: the three IDs in `main-known-red.txt` were not edited or repaired here.

## Findings

- F1 -> W1 now proves conflict freedom for no-conflict rows and preserves `UNKNOWN` when proof is absent; failed D3 certificates stay undecided -> `test_rsp_unknown_w1_is_neither_false_nor_a_scored_answer` (C1–C7, C-doc) and `test_rsp_missing_quantity_certificate_is_undecided` (D1, D2, D3b, D4, D5) -> `a5ce6a414`.
- F2 -> M6 receives the actual extra rule and listed threshold from mutated VE inputs, and the mutants assert observed violations -> `test_rsp_invention_audit_checks_the_actual_mutation` (m2, m4) and `test_rsp_audit_uses_the_mutated_query_input` -> `a5ce6a414`.
- F3 -> section 9 has unscored VE reruns without N1, N2 and N3, saved separately from key scoring -> `test_rsp_each_narrowing_has_an_unscored_counterfactual`, `test_rsp_each_narrowing_reruns_a_ve_answer`, and `test_rsp_run_recomputes_every_key_item_and_records_causes` -> `a5ce6a414`.

The regenerated scored baseline remains 111/126 agreements and 15 faithful undecided rows. All six planned mutants still change exactly their named results. The unscored comparisons change 46 cells without N1 (including all 20 PROT cells), G1 and N5 without N2, and K13 without N3. Conflict statements about the source remain candidates pending the independent check required by standing ruling R14 (`DRI-RULINGS.md`). There is no VE product verdict or frozen-key delta and no DELTA ruling row.

## Seeded failures and verification

In `run.py`, three temporary bugs were planted together, tested, and restored byte for byte:

| Seed | Failing regression |
|---|---|
| Treat every W1 row without a conflict as false, including `UNKNOWN` | `test_rsp_unknown_w1_is_neither_false_nor_a_scored_answer` (all eight parameters failed) |
| Route M6 to the baseline-only audit | `test_rsp_invention_audit_checks_the_actual_mutation` (m2 and m4 failed) |
| Keep the N3 rule in the without-N3 variant | `test_rsp_each_narrowing_reruns_a_ve_answer[N3-K13]` failed |

The seeded run had 11 expected failures and 2 passes; the restored RSP regression selection had 39 passes. Both executable review probes failed before the fix and passed after it. The requested selected plan had 47 units, zero failed; no full suite or release gate was run. The Lean audit covered 668 source files and 7,428 named theorem declarations.
