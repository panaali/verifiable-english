# User-visible deltas (sc-1a)

| Item | Change | Ruling |
|---|---|---|
| Trust budget | Classified trusted Lean lines rise by 93 against the merge base `c7fc6acac`, all new Lean-owned behaviour of `scope@0` (the layout's list runs, joining parts): `lean/VE/Layout/List.lean` +79 (S 17: `Unit`, `GovernedItem`; D[V] 62: `ofSource`, `paraCounts`, `lineStart`, `spacesOnly`, `skipSpaces`, `markerLen`, `lastNonBlank`, `boldLabel`, `isBlank`, `isDigit`, `sp`, `nl`; `continues`, `indexOf`, `runFrom` and `listRun` are D[V] tied by `continues_iff`, `indexOf_iff`, `mem_runFrom`, `listRun_iff`/`listRun_ok_iff`, so not counted), `lean/VE/Scope/Effects.lean` +14 (S 8: `mergeParts`; G[V] 6: `lookups`). K +0. `lean/VE/Scope/Examples.lean` is T; `lean/VE/Scope/Theorems.lean` holds only theorems (P). Recorded with `tools/trust_map.py --allow` (S +25, V +68). | SIGNED by standing ruling R16 (DRI-RULINGS.md): 93 <= 150 lines, K +0, new Lean-owned behaviour; itemised per file and re-measured on this HEAD with `uv run python tools/trust_map.py --check` (PASS). Every new trusted definition is exercised by a check that can fail: the theorems `listRun_iff`, `listRun_ok_iff`, `mergeParts_keys`, `mergeParts_conflict`, `lookups_spec` and the kernel fixtures of `lean/VE/Scope/Examples.lean` (`of_source`, `short_layout`, `short_run`, `markers`, `bold_labels`, `byte_tests`, `para_counts`, `unordered_join`); `tests/test_scope_lean.py::test_every_trusted_scope_definition_is_used_by_a_theorem` checks the condition on the compiled `-- uses` lines for every trusted definition of `lean/VE/Layout/` and `lean/VE/Scope/`, and `::test_a_definition_no_theorem_uses_is_reported` shows it can fail; seeded bugs in `docs/scope/sc-1a/mutants.json` (8, each failing a proof or fixture). Ties pass: manage-agents FOLLOW-UPS.md, "## sc-1a (2026-10-18)". |

No other delta. The item adds no route, service mode, response field, diagnostic or verdict that any caller sees:

- Every file is new (`lean/VE/Layout/List.lean`, `lean/VE/Scope/{Effects,Theorems,Examples}.lean`) and no route,
  service mode or document check imports them; `lean/VE.lean` only adds their imports. The texts they can produce
  (`NotALeadIn`, `ScopeUnknownUnit`, `ScopeConflict`, `InvalidInput: scope@0 parts of <u> must be objects`) reach
  no caller until SC-1b wires `govern` into the document mode.
- No existing Lean, Python or Rust file changes behaviour. The edits outside the new files are generated inventories
  (`lean/VE/Audit.lean`, `lean/axioms.txt`, `lean/declarations.txt`, `lean/predicates.txt`, `lean/statements.txt`),
  the side tables `tools/trust-classes.json` and `docs/trust-baseline.json`, and three `other_json` reasons in
  `ve/assurance-manifest.json` (checked by `tests/test_assurance_manifest.py`, 137 passed).
