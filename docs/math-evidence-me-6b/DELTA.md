# me-6b delta: `ve-units@2`

**Public output: none.** me-6b registers no service mode, command or route and changes no Python or Rust file:
`VE.Calc.Units` is reached only by the Lean build and `tests/test_calc_units.py`.

Trust growth, re-measured with `uv run python tools/trust_map.py --check` on the final code: K +0, S +0, untied V +60,
recorded with `trust_map.py --allow` in `docs/trust-baseline.json`. The ties-pass row R16 asks for is in
manage-agents FOLLOW-UPS.md, section "## me-6b". [`mutants.json`](mutants.json) lists each definition's mutants and the
tests they fail: 32 of 32 are killed.

| # | File | Trusted lines (class, declaration lines) | Exercised by (`tests/test_calc_units.py`) | Ruling |
|---|---|---|---|---|
| 1 | `lean/VE/Calc/Units.lean` | +60: D[V] 55 (`UnitDef` 7, `UnitEnv` 5, `decodeFactor` 10, `decodeUnit` 13, `decodeV2` 14, `decode` 6), G[V] 5 (`UnitEnv.find?` 2, `UnitEnv.values` 3) | `test_fixture[refuse-*]`, `[i2-*]`, `[h7c*]`, `[h7l*]`, `[claim-*]`; mutants `factor-pos`, `factor-spelling`, `unit-dim`, `unit-day`, `unit-exponent-string`, `v2-nodup`, `v2-schema`, `decode`, `find`, `values` | SIGNED by standing ruling R16 (DRI-RULINGS.md) |
