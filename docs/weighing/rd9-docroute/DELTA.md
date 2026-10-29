# rd9-docroute user-visible delta

| Input | Before | After | Ruling | Evidence |
| --- | --- | --- | --- | --- |
| `ve document check` on a `norm-defaults@0` soft-chain document with a claim graph, including generated graph leaves, contradictory filled premises, and source `instruction_of` declarations | `UnsupportedProfile: norm-defaults@0 documents are checked through fill (ve.norm_defaults)` | Lean's filled soft admission and premise answer; generated leaves and valid source instruction declarations are admitted, and a strict contradiction reports `INCONSISTENT` and `vacuous: true` | SIGNED by the DRI 2026-10-29 (reviews/dri-decisions-20261029-rd9-docroute.md item 1) | `tests/test_rd9_docroute.py::test_soft_chain_document_checks_the_filled_route`, `test_filled_soft_premises_make_a_contradiction_vacuous`, `test_filled_graph_leaves_decode_in_the_filled_vocabulary`, `test_soft_coherence_graph_leaf_uses_filled_vocabulary`, `test_soft_chain_without_readings_uses_the_filled_route`, `test_filled_soft_source_instruction_declarations_match_lean_base`; `probe.json` |

The direct soft check of an unfilled tree and a document lacking `norm-defaults@0` keep their distinct refusals (`test_direct_soft_check_of_unfilled_tree_still_refuses`, `test_unspecified_without_profile_keeps_its_own_refusal`). They are controls, not deltas.
