# me-6 delta: physical dimensions and `ve-units@2`

Base `9ea276842` (`git merge-base HEAD main`). **Public output: none.** me-6 registers no service mode, command
or route and changes no Python or Rust file; `VE.Calc.Units.decode` and `Expr.dimOf` are reached only by the
Lean build and `tests/test_calc_dimensions.py`. No diagnostic, verdict or English line a user sees changes.
`ve-units@1` identities are unchanged (fixture `i2-legacy`: W6a's id of the news environment is the one
`tests/data/route-cases.jsonl` records).

Trust growth, re-measured with `python3 tools/trust_map.py --check` on the final code: K +0, S +55, untied V +60,
trusted +115 against `9ea276842060`; recorded with `trust_map.py --allow` in `docs/trust-baseline.json`. The
ties-pass row R16 asks for is in manage-agents FOLLOW-UPS.md, section "## me-6". Each definition's mutants and
the tests they fail are in [`mutants.json`](mutants.json) (all 31 killed, proofs they break stubbed).

| # | File | Trusted lines (class, declaration lines) | Exercised by (`tests/test_calc_dimensions.py`) | Ruling |
|---|---|---|---|---|
| 1 | `lean/VE/Calc/Dimension.lean` | +55: S 55 (`PhysDim` 5, `PhysDim.Normal` 2, `PhysDim.one` 2, `insertExp` 8, `PhysDim.mul` 1, `PhysDim.inv` 1, `PhysDim.npow` 3, `Expr.dimOf` 12, `Rescale` 5, `zpowR` 4, `Rescale.of` 3, `Rescale.apply` 6, `legacyDim` 3) | `test_fixture[h7-dimof]`, `[normal]`, `[h7-ratio-sum]`, `[h7-area]`, `[h7-frequency]`, `[h7u-values]`, `[h7l]`, `test_a_change_of_units_has_positive_factors`; mutants normal-le to legacy | SIGNED by standing ruling R16 (DRI-RULINGS.md) |
| 2 | `lean/VE/Calc/Units.lean` | +60: D[V] 55 (`UnitDef` 7, `UnitEnv` 5, `decodeFactor` 10, `decodeUnit` 13, `decodeV2` 14, `decode` 6), G[V] 5 (`UnitEnv.find?` 2, `UnitEnv.values` 3) | `test_fixture[refuse-*]`, `[i2-*]`, `[h7c-value]`, `[h7c]`, `[h7l]`, `[context-unit]`, `test_malformed_environments_get_a_lean_answer`; mutants factor-pos to values | SIGNED by standing ruling R16 (DRI-RULINGS.md) |
