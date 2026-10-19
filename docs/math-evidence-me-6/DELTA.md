# me-6 delta: physical dimensions

**Public output: none.** me-6 registers no service mode, command or route and changes no Python or Rust file:
`Expr.dimOf` and the change of units are reached only by the Lean build and `tests/test_calc_dimensions.py`.

Trust growth, re-measured with `python3 tools/trust_map.py --check` on the final code: K +0, S +55, untied V +0,
recorded with `trust_map.py --allow` in `docs/trust-baseline.json`. The ties-pass row R16 asks for is in
manage-agents FOLLOW-UPS.md, section "## me-6". [`mutants.json`](mutants.json) lists each definition's mutants
and the tests they fail: 15 of 15 are killed, with the proofs they break stubbed.

| # | File | Trusted lines (class, declaration lines) | Exercised by (`tests/test_calc_dimensions.py`) | Ruling |
|---|---|---|---|---|
| 1 | `lean/VE/Calc/Dimension.lean` | +55: S 55 (`PhysDim` 5, `PhysDim.Normal` 2, `PhysDim.one` 2, `insertExp` 8, `PhysDim.mul` 1, `PhysDim.inv` 1, `PhysDim.npow` 3, `Expr.dimOf` 12, `Rescale` 5, `zpowR` 4, `Rescale.of` 3, `Rescale.apply` 6, `legacyDim` 3) | `test_fixture[normal]`, `[h7-*]`, `[h7u-values]`, `[h7l]`, `[h7l-same]`, `test_a_change_of_units_has_positive_factors`; one or more mutants per definition | SIGNED by standing ruling R16 (DRI-RULINGS.md) |
