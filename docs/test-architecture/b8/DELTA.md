# Batch 8 user-visible delta

None. The edits change historical test inputs, evidence reads, and when a test-only legacy oracle is imported. They do not change Lean answers, diagnostics, verdicts, or public output. No standing ruling or DRI signature is needed.

The existing `tests/test_norm_defaults_contract.py` fixtures and the batch 8 focused run check the contract's accepted and rejected outcomes. The chain owns the full gate on the committed final HEAD.
