# rd9-docroute user-visible delta

| Input | Before | After | Ruling | Evidence |
| --- | --- | --- | --- | --- |
| `ve document check` on a `norm-defaults@0` soft-chain document with a claim graph | `UnsupportedProfile: norm-defaults@0 documents are checked through fill (ve.norm_defaults)` | Lean's filled soft admission answer; the small fixture reports `admitted: true` | DRI signature needed. `msg.sh dri rd9-docroute` could not write the read-only DRI inbox; this is the item stop reason under L52. | `tests/test_rd9_docroute.py::test_soft_chain_document_checks_the_filled_route`; `probe.json` |

The direct soft check of an unfilled tree and a document lacking `norm-defaults@0` keep their distinct refusals (`test_direct_soft_check_of_unfilled_tree_still_refuses`, `test_unspecified_without_profile_keeps_its_own_refusal`). They are controls, not deltas.
