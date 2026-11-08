# sc-6 delta

No answer changes. No route reads the rights reach yet: the document route moved to sc-6b
(reviews/dri-decisions-20261102-sc-6.md item 1, R9). A document without a rights reach answers byte for byte as main
(`tests/test_scope_rights_reach.py::test_a_document_without_a_rights_reach_answers_byte_for_byte_as_main`). It is a
rights@0 part document of the UDHR under scope@0, compared against main's answer recorded at f1c306460 in
`tests/data/scope/rights-reach-absent-main.json`. Bytes on the pinned runs: 0. The only delta is the trusted base.

| Input | Before | After | Ruling | Evidence |
| --- | --- | --- | --- | --- |
| Trusted Lean lines (`uv run python tools/trust_map.py --check` against f1c306460476) | K 994, S 12877, untied V 44437 | K +0. S +10: `lean/VE/Scope/Reach.lean` +10 (`Pinned.rightNames`, `Pinned.withReach`). Untied V +8: `lean/VE/Scope/Reach.lean` +8 (`Pinned.rightOf`). `Pinned.wholeRights` and `Pinned.withBarReach` are G[R] (reject-only), which the budget does not count as trusted. Trusted +18 in all. | SIGNED by standing ruling R16 (DRI-RULINGS.md), sc-6, 2026-10-18 | The allowance is in `docs/trust-baseline.json`. `docs/scope/sc-6/trust-mutants.json`: 17 KILLED, 8 INVALID, 1 ALLOWED (it does not elaborate; see `trust-mutants-allow.json`). Every new definition is killed by a guard or a proof (`mutants.json`). The ties pass is filed in FOLLOW-UPS.md under `## sc-6`. |
