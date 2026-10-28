# User-visible deltas (sc-1ae)

| Item | Change | Ruling |
|---|---|---|
| Approved statements of spec 5.1 | `decodeNorm_name`, `govern_strings`, `govern_no_new_symbols` and `govern_preserves` are built with spec 5.1's text plus one hypothesis each, `(hw : JsonWF o)` for the decoded rule and `(hw : JsonWF D.doc)` for the document (`docs/scope/sc-1ae/statement-diff.txt`: every other token is exact). `JsonWF` is spec 11.3's `Pinned.JsonWF` (identical text) and is defined once, in `lean/VE/Scope/Govern.lean`. `govern_provenance`, the fifth, is not built (sc-1aeb). | SIGNED by the DRI 2026-10-27 (reviews/dri-decisions-20261027-featureplan-gates.md item 2). Condition tests: F-raw's four `#guard`s stay in `lean/VE/Scope/Examples.lean` (lines 738 (items 1 and 2), 743 (item 3) and 748 (item 4)) as the reason for the hypothesis; the parser lemma is not proved here (`Lean.Json.parse` is `partial`), so it is sc-1af and, as the decision says, SC-1b's statements may not take `JsonWF` as a hypothesis until it is proved. |
| Trust budget | Classified trusted Lean lines rise by 27 against the merge base `c2a0ee977` (S +27, V +0, K +0), all in `lean/VE/Scope/Govern.lean`: `JsonWF` 9, `HasStr` 5, `payload` 6 and `BlockBound` 3 (their source ranges in `lean/declarations.txt`), and the 4 lines between them. `lean/VE/Scope/Theorems.lean` holds theorems only (P); the new fixtures in `lean/VE/Scope/Examples.lean` (`inventedC`, `gI`, `count`) are T. Recorded with `tools/trust_map.py --allow` (S +27). | SIGNED by standing ruling R16 (DRI-RULINGS.md): 27 <= 150 lines, K +0, new Lean-owned meaning (what spec 5.1's statements claim); itemised per file and re-measured on this HEAD with `uv run python tools/trust_map.py --check` (PASS). Every new trusted definition is exercised by a check that can fail: `tests/test_scope_lean.py::test_a_govern_definition_no_theorem_uses_is_reported[VE.Scope.JsonWF]`, `[VE.Scope.HasStr]`, `[VE.Scope.payload]` and `[VE.Scope.BlockBound]`; `tools/trust_mutants.py` (`docs/scope/sc-1ae/trust-mutants.json`: 3 killed, 4 allowed with their proof kills, exit 0); and the 18 hand mutants of `docs/scope/sc-1ae/mutants.json`. Ties pass: manage-agents FOLLOW-UPS.md, "## sc-1ae (2026-10-28)". |

No other delta. Nothing a caller sees changes:

- **No answer or refusal changes.** The item adds four definitions that are propositions or read nothing at run
  time (`payload` is read by no executable code) and theorems. No definition that computes an answer is edited.
- **No other statement changes.** `HasStr`, `payload` and `BlockBound` equal spec 4.2; the four theorems equal
  spec 5.1 but for the signed hypothesis (`statement-diff.txt`).
- **No existing file changes behaviour.** The other edits are the trust ledgers, a test case list, `lean/SCOPE.md`,
  generated inventories and docs.
