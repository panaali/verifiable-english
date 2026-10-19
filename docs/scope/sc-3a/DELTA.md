# User-visible deltas (sc-3a)

| Item | Change | Ruling |
|---|---|---|
| Trust budget | Classified trusted Lean lines rise by a net 11 against the merge base `702ff7429` (S +6, V +5, K +0). `lean/VE/Layout/Anchors.lean` +68: S 63 for discourse's containment bodies (`within`, `narrower`, `innermostAnchor`), its anchor checks (`reachesRoot`, `anchorsOk`) and the generic checks they call (`req`, `runAll`, `allOk`, `dupOf`, `spanIn`, `spansDisjoint`), moved from `lean/VE/Discourse/Access.lean` (−16) and `lean/VE/Discourse/WellFormed.lean` (−48); D[V] 5 untied (`headingOf`, `spansOf`). `lean/VE/Layout/List.lean` +7 (S: `ItemUnit`). Tied, so not counted: `anchorUnits` (`mem_anchorUnits`), `anchorReach` (`anchorReach_iff`), `itemFrom` (`mem_itemFrom`), `itemRun` (`itemRun_iff`), and discourse's call-only `within`, `innermostAnchor` and `anchorsOk` (G[V], tied by `discourse_within_unchanged`, `discourse_innermost_unchanged`, `discourse_anchorsOk_unchanged`). `lean/VE/Layout/Discourse.lean` holds theorems only; the fixtures are T. Recorded with `tools/trust_map.py --allow` (S +6, V +5). | SIGNED by standing ruling R16 (DRI-RULINGS.md): net 11 <= 150 lines (68 + 7 before the moved lines leave discourse), K +0, new Lean-owned behaviour (the anchor and label reaches); itemised per file and re-measured on this HEAD with `uv run python tools/trust_map.py --check` (PASS). Every new or moved trusted definition is exercised by a check that can fail: `tests/test_scope_lean.py::test_every_trusted_scope_definition_is_used_by_a_theorem` (with `::test_a_definition_no_theorem_uses_is_reported` showing it can fail), and 32 seeded Lean mutants, at least one per such definition, each failing a named theorem or `#guard` (`docs/scope/sc-3a/mutants.json`). Ties pass: manage-agents FOLLOW-UPS.md, "## sc-3a (2026-10-19)". |

No other delta. Nothing a caller sees changes:

- **Discourse answers are unchanged on every document.** Discourse's `within`, `narrower`, `innermostAnchor` and
  `anchorsOk` now call the moved bodies, and `docs/scope/sc-3a/evidence/before-bodies.lean.txt` proves each equal to
  the body it had at `702ff7429` for every `DDoc` (`before_within`, `before_innermost`, `before_reachesRoot`,
  `before_anchorsOk`; run on this HEAD, exit 0; a planted difference makes it fail). The diagnostics, their texts
  and their order are the same code. The discourse tests pass unchanged (468 tests on `8b91d997`, and the selected
  run of 356 units on `b152db4a`).
- **No theorem statement changes.** Every one of the 5,978 theorem statements at `702ff7429` is unchanged at HEAD
  (`docs/scope/sc-3a/statements-unchanged.txt`), including `acc_no_heuristic`, `name_scope`, `innermost_within` and
  `narrower_mem`, which are re-proved by unfolding.
- **No extra cost.** Discourse's containment is no slower: on a synthetic 300-unit discourse document with 40
  sections, the `earlierUnits` access pattern took 5.6 to 7.7 s against 9.0 to 10.5 s for the pre-move bodies
  (interpreted, three runs each; `docs/scope/sc-3a/evidence/containment-bench.lean.txt`), because the innermost
  anchor now builds the span list once rather than once per anchor.
- **The new scope parts reach no caller.** `anchorReach`, `headingOf`, `itemRun` and their texts
  (`ScopeUnknownAnchor: <a>`, `NotALabel: <unit>`, `ScopeUnknownUnit: <unit>`) are called by no route or service
  mode until scope's `govern` (sc-1ac, then sc-3ab) and the document mode (SC-1b).
