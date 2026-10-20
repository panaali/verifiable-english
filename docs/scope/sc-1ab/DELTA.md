# User-visible deltas (sc-1ab)

| Item | Change | Ruling |
|---|---|---|
| Trust budget | Classified trusted Lean lines rise by 72 against the merge base `585794c92` (S +64, V +8, K +0), all in the new `lean/VE/Scope/Effects.lean`: S 64 for `Effect`, `Commutes`, `narrowing`, `depthLimit`, `hasOwn`, `depthOk`, `ownSafe`, `substOwn` and `mergeParts` (spec 4.2's text, `mergeParts` reading through `lookups`); G[V] 8 untied for `members` and `lookups`. `lean/VE/Scope/Theorems.lean` holds theorems only (P); the new fixtures in `lean/VE/Scope/Examples.lean` are T. Recorded with `tools/trust_map.py --allow` (S +64, V +8). | SIGNED by standing ruling R16 (DRI-RULINGS.md): 72 <= 150 lines, K +0, new Lean-owned behaviour (scope's effects on a rule's JSON object); itemised per file and re-measured on this HEAD with `uv run python tools/trust_map.py --check` (PASS). Every new trusted definition is exercised by a check that can fail: `tests/test_scope_lean.py::test_every_trusted_scope_definition_is_used_by_a_theorem` (with `::test_an_effects_definition_no_theorem_uses_is_reported` showing it can fail), and 16 seeded Lean mutants, at least one per new trusted definition, each failing a named theorem or `#guard` (`docs/scope/sc-1ab/mutants.json`). Ties pass: manage-agents FOLLOW-UPS.md, "## sc-1ab (2026-10-19)". |

No other delta. Nothing a caller sees changes:

- **The new definitions reach no caller.** No route, service mode or other Lean module calls `VE.Scope.Effects`
  until scope's `govern` (sc-1ac) and the document mode (SC-1b); its texts (`ScopeConflict: <u>: <key>`,
  `InvalidInput: scope@0 parts of <u> must be objects`) appear in no answer yet.
- **No approved statement changes.** The five theorems (`substOwn_no_own`, `substOwn_id`, `commutes_symm`,
  `mergeParts_keys`, `mergeParts_conflict`) and nine of the ten definitions equal spec 4.2 and 5.1 after whitespace
  normalisation (`docs/scope/sc-1ab/statement-diff.txt`). The tenth, `mergeParts`, reads members through `lookups`
  instead of `VE.Bridge.fields` (sc-1a's deviation 3). It accepts and answers exactly as the spec's text on every
  well-formed object and every non-object (`mergeParts_text`, proved), and the JSON parser builds only well-formed
  objects, so no input a document can carry is answered differently. The REPORT records the change.
- **No existing file changes behaviour.** The other edits are an import list, the trust ledgers, a test file and
  docs.
