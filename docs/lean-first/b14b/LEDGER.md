# Batch 14b deletion ledger

| Former Python decision | Lean owner after 14b | Evidence |
|---|---|---|
| `ve/norms.py` `_NON_FOL_TAGS` and `_first_order`: a Python walk classified every guard and carve-out as first order or not | `VE.Norms.Family.firstOrder` decodes each formula with the selected family decoder and selects the FOL or full-family regeneration | `test_non_first_order_norms_are_dispatched_and_match_python`; batch A/B corpus |
| `_family_norms`: rejected closure, core and order documents containing reachability, n-ary atoms or arithmetic, and rejected `$int` declarations | `VE.Service.FamilyNorms.runCase` chooses `genericRun`; `VE.Norms.Family.decodeDoc` checks the family's formulas and `genericCase` supplies premises, certificate and conflict answers | The same route test across all three families; certificate and witness regressions |
| Python's fallback elaboration and conflict verdict for this newly covered family scope | `VE.Norms.Family.elaborate` and `targets`, checked by `VE.Service.FamilyNorms.genericCase` and the family route's certificate/evaluation cases | 1,350-record generated A/B corpus, service schema fuzz, selected tests |

`NormDocument._elaborate_python` remains for statement-layer environments outside batch 14b. Python's search and prover remain untrusted candidate generators under the lead's question-10 decision; their reports are checked by Lean. `family_in_scope` still excludes n-ary definitions, assigned to 14c. No Rust product code changed.
