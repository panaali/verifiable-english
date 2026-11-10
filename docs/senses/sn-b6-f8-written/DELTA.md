# sn-b6-f8-written DELTA (two senses definitions counted in the trust budget)

Base: the merge base with main, `223babd3d` (after the sync with main; first measured over `1ddb87dc1`, also +13). Reclassification (reviews/dri-decisions-20261109-sn-b6-f8-written.md
item 1, from the sn-b6-f8-trust builder's finding): no Lean definition, statement, verdict or wire output changes;
`tools/trust-classes.json` moves two names from G[I] to G[V], and `lean/VE/Senses/RunExamples.lean` gains two
`#guard` examples, one per definition, and three helpers (test code, class T).

| # | Delta | Evidence | Ruling |
|---|---|---|---|
| 1 | Trusted Lean growth V +13, K +0, S +0 over `223babd3d`, re-measured on the final HEAD: `lean/VE/Senses/Run.lean` +13 (G[I] to G[V]: `Projection.written` +8, `SensesOutcome.written` +5); `lean/VE/Senses/RunExamples.lean` +0 (its new helpers are T) | `uv run python tools/trust_map.py --check` (PASS, "VE/Senses/Run.lean: trusted +13"); `lean/VE/Senses/RunExamples.lean` (`Projection.written` line 214, `SensesOutcome.written` line 219; seeded bugs 1-3 in REPORT.md); `evidence/follow-ups-row.md` | R16 |
