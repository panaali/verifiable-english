# User-visible deltas (sc-1ad)

| Item | Change | Ruling |
|---|---|---|
| Trust budget | Classified trusted Lean lines rise by 31 against the merge base `9b7e6e5c7` (S +23, V +8, K +0), all in `lean/VE/Scope/Govern.lean`: S 23 for the graph step's `edgesOf`, `edgesInto` and `addOver`, and `govern`'s graph lines (spec 4.2's text); G[V] 8 untied for `normOf`, `memo` and the derived `DecidableEq Reach`. Not trusted: the graph step's `ruleTable` and `edgesFor` (tied by `ruleTable_decoder`, `edgesFor_ok`), the run path `governFast` and `fastReads` (tied by `governFast_eq`, `fastReads_eq`) and its steps `frameOnF`, `baseObjF`, `coveredBy`, `governorsOfF`, `composedF`, `edgesOfF` and `governBody` (each tied by its `rfl` equation to `govern`'s step), and the reject-only `orderCheckF` (G[R]). `lean/VE/Scope/Theorems.lean` holds theorems only (P); the new fixtures in `lean/VE/Scope/Examples.lean` are T. Recorded with `tools/trust_map.py --allow` (S +23, V +8). | SIGNED by standing ruling R16 (DRI-RULINGS.md): 31 <= 150 lines, K +0, new Lean-owned behaviour (scope's precedence step and run path); itemised per file and re-measured on this HEAD with `uv run python tools/trust_map.py --check` (PASS). Every new trusted definition is exercised by a check that can fail: `tests/test_scope_lean.py::test_every_trusted_scope_definition_is_used_by_a_theorem` (with `::test_a_govern_definition_no_theorem_uses_is_reported[VE.Scope.addOver]`, `[VE.Scope.edgesInto]` and `[VE.Scope.memo]` showing it can fail), `tools/trust_mutants.py` (`docs/scope/sc-1ad/trust-mutants.json`, exit 0) and the hand mutants of `docs/scope/sc-1ad/mutants.json`. Ties pass: manage-agents FOLLOW-UPS.md, "## sc-1ad (2026-10-20)". |

No other delta. Nothing a caller sees changes:

- **The changed definitions reach no caller.** No route, service mode or other Lean module calls `VE.Scope.govern`
  or `VE.Scope.governFast` until the document mode (SC-1b). `govern` now answers a `precedes` or `yields` governor
  as spec 4.2 states, where sc-1ac refused it (`UnsupportedProfile: scope@0 precedence requires SC-4`); its new text
  `ScopeNoEffect: <governor>` appears in no answer yet.
- **No approved statement changes.** The four theorems built here equal spec 5.1 after whitespace normalisation
  (`docs/scope/sc-1ad/statement-diff.txt`), `governFast_eq` with the placeholder `Pinned.governFast` pinned to this
  item's own `governFast`, as spec 8.1 says. `govern`, `normOf` and the six graph-step definitions equal spec 4.2.
  The five theorems whose statements fail on raw trees (the REPORT's statement gate) are not built, and no statement
  is changed: they wait for the DRI's decision.
- **No existing file changes behaviour.** The other edits are the trust ledgers, a test file and docs.
