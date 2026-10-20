# User-visible deltas (jt-1b)

| Item | Change | Ruling |
|---|---|---|
| Trust budget | Classified trusted Lean lines rise by 96 against the merge base `e010fb6aa`, all new Lean-owned behaviour of `judgments@0` (dependence, the unit status and the usage map). Everything is in `lean/VE/Judgments/Status.lean`: S +88 (`Content` 6, `Content.formulas` 4, `defEdges` 4, `reachedBodies` 7, `dependsOn` 4, `dependsOnC` 4, `ActiveSet` 8, `UnitView` 11, `UnitView.reads` 6, `UnitView.complete` 8, `UnitView.legacy` 6, `status` 13, `usageMap` 7) and G[V] +8 (`viewOf`). K +0. `lean/VE/Judgments/Examples.lean` is T. Recorded with `tools/trust_map.py --allow` (S +88, V +8). | SIGNED by standing ruling R16 (DRI-RULINGS.md): 96 <= 150 lines, K +0, new Lean-owned behaviour; itemised per definition and re-measured on this HEAD with `uv run python tools/trust_map.py --check` (PASS). Every new trusted definition is exercised by a check that can fail, with at least one seeded bug each in `mutants.json` (16 mutants, every one fails a named `#guard` or theorem). The checks are the 11.3 and 11.9 `#guard`s in `lean/VE/Judgments/Examples.lean`, three internal rows (`formulas_carve` for `Content.formulas`, `reachedBodies_chain` for `reachedBodies` and `defEdges`, `viewOf_xi` for `viewOf`, `ActiveSet` and `Content`), and the theorems `dependsOn_iff`, `dependsOn_no_defs`, `viewOf_legacy`, `status_eq`, `status_never_checked`, `status_checked`, `status_ok_iff`, `status_legacy`, the four `usageMap` theorems, `dependsOnC_remove` and `status_remove_unused`. `tests/test_judgments_exercised.py::test_every_trusted_judgment_definition_is_used_by_a_theorem` checks the condition on the compiled `-- uses` lines. Ties pass: manage-agents FOLLOW-UPS.md, "## jt-1b (2026-10-19)". |

No other delta. The item adds no route, service mode, response field or diagnostic that any caller sees:

- `Status.lean` and its fixtures are imported only by `lean/VE.lean` and `Examples.lean`. No service mode, route or
  document check calls `status` or `usageMap` before JT-2, and `ve_service` is not rebuilt (`lean/checkers.lock` is
  unchanged).
- The diagnostics `JudgmentNotChecked`, `JudgmentNotListed` and `JudgmentListedUnused` are reached by no route until
  JT-2 switches the profile on in the document mode.
- `status_legacy` proves that with no bound judgments every unit keeps today's status, and J-λ's `#guard` checks it
  on eight units.
