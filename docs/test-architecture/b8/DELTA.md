# Batch 8 user-visible delta

The batch 8 edits change historical test inputs, evidence reads, and when a test-only legacy oracle is imported. They do not change Lean answers, diagnostics, verdicts, or public output.

The existing `tests/test_norm_defaults_contract.py` fixtures and the batch 8 focused run check the contract's accepted and rejected outcomes. The chain owns the full gate on the committed final HEAD.

The pre-review relay mutation gate found 26 findings that main also has, on the `graph`, `parse` and `route` routes. Commits `0ba241d9a` and `3663dd1b4` copy the relay-only fix from premise-scale (`8808fb359`, and the relay files of `b961596b5`). Genuine Lean answers are unchanged; only malformed answers are now refused:

| # | Change | Before | After | Test | Signature |
|---|---|---|---|---|---|
| 1 | A malformed Lean graph response whose Background leaf has an empty or unknown label, or an AST outside the generated formula shape, is refused before the caller reads it | the label was any string and the AST any non-empty array | `CheckerUnavailable` | relay mutation gate `service:graph` (786 mutants, 0 failures) | SIGNED by standing ruling R8 (DRI-RULINGS.md): the Background field is fully typed by the Lean-authored schema and the relay refuses the malformed answer |
| 2 | A malformed Lean parse response with an empty diagnostic string is refused before the caller reads it | an empty error string could pass the parse-specific response shape | `CheckerUnavailable` | `test_parse_diagnostic_text_cannot_be_empty`; relay mutation gate `service:parse` | SIGNED by standing ruling R8 (DRI-RULINGS.md): the diagnostic field is fully typed by the Lean-authored schema and the relay refuses the malformed answer |
