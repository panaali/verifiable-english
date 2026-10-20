# User-visible deltas (sc-1ac)

| Item | Change | Ruling |
|---|---|---|
| Trust budget | Classified trusted Lean lines rise by 132 against the merge base `75a9bcef9` (S +90, V +42, K +0), all in the new `lean/VE/Scope/Govern.lean`: S 90 for `Reach`, `Governor`, `SDoc`, `applyEffect`, `isFrame`, `unary`, `graph`, `baseObj`, `covered`, `classOf`, `position`, `ordered`, `composed`, `affected` and `govern` (spec 4.2's text, with the three deviations of the REPORT); G[V] 42 untied for `keysOf`, `unitsOf`, `idOf`, `unitIds`, `contentOf`, `isPart`, `isNorm`, `objectOf`, `partUnits`, `ruleUnits`, `coveredLayout`, `frameOn`, `baseName`, `newContent` and `patch`. Not trusted: `coversU`, `governorsOf` and `itemRule` (tied by `coversU_iff`, `governorsOf_iff`, `itemRule_decoder`) and the reject-only `admitBlock`, `orderCheck`, `conditions`, `vocabularyNames`, `firstDup` and `setUnits` (G[R]). `lean/VE/Scope/Theorems.lean` holds theorems only (P); the new fixtures in `lean/VE/Scope/Examples.lean` are T. Recorded with `tools/trust_map.py --allow` (S +90, V +42). | SIGNED by standing ruling R16 (DRI-RULINGS.md): 132 <= 150 lines, K +0, new Lean-owned behaviour (scope's `govern` and the block's admission); itemised per file and re-measured on this HEAD with `uv run python tools/trust_map.py --check` (PASS). Every new trusted definition is exercised by a check that can fail: `tests/test_scope_lean.py::test_every_trusted_scope_definition_is_used_by_a_theorem` (with `::test_a_govern_definition_no_theorem_uses_is_reported` showing it can fail), and 57 seeded Lean mutants, at least one in each of the 30 new trusted definitions, each failing a named theorem or `#guard`, and each failing a fixture with the proofs bypassed (`docs/scope/sc-1ac/mutants.json`). Ties pass: manage-agents FOLLOW-UPS.md, "## sc-1ac (2026-10-20)". |

No other delta. Nothing a caller sees changes:

- **The new definitions reach no caller.** No route, service mode or other Lean module calls `VE.Scope.Govern` until
  the document mode (SC-1b); its texts (`ScopeOrphanPart`, `ScopeNotARule`, `ScopeReadings`, `ScopeReach`,
  `ManifestMismatch: scope.…`, and the `UnsupportedProfile` refusals that stand until sc-1ad and sc-3ab) appear in
  no answer yet.
- **No approved statement changes.** The five theorems built here (`itemRule_decoder`, `govern_identity`,
  `govern_orphan`, `govern_admits`, `governorsOf_iff`) equal spec 5.1 after whitespace normalisation, and 36 of the
  39 definitions equal spec 4.2 (`docs/scope/sc-1ac/statement-diff.txt`). The other three, `coveredLayout`,
  `admitBlock` and `govern`, refuse what later items add (the REPORT's deviations 1 to 3). Every answer the built
  `govern` gives is the answer of the spec's text: it refuses more (anchors, anchor and label reaches, precedence),
  never less, and `isNull` agrees with the compiled `== .null` on every value.
- **No existing file changes behaviour.** The other edits are an import list, the trust ledgers, one assurance
  manifest reason, a test file and docs.
