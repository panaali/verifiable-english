# sn-b6-f8-trust DELTA (three senses definitions counted in the trust budget)

Base: the merge base with main, `9ba8aeaed`. Reclassification only (reviews/dri-decisions-20261105-cfr2.md, C-finding
regrade 11-04 #9, sn-b6-review-ov F8; queued by reviews/dri-decisions-20261109-lp0412.md item 2): no Lean definition,
statement, verdict or wire output changes; `tools/trust-classes.json` moves three names from G[I] to G[V].

| # | Delta | Evidence | Ruling |
|---|---|---|---|
| 1 | Trusted Lean growth V +38, K +0, S +0 over `9ba8aeaed`, re-measured on the final HEAD: `lean/VE/Senses/Run.lean` +38 (G[I] to G[V]: `projectionIds` +10, `admittedIds` +24, `usedOf` +4) | `uv run python tools/trust_map.py --check` (PASS, "VE/Senses/Run.lean: trusted +38"); `lean/VE/Senses/RunExamples.lean` (`usedOf` line 43, `projectionIds` line 55, `admittedIds` through the pinned `runCaseReported` answers, lines 120-136); `evidence/follow-ups-row.md` | R16 |
