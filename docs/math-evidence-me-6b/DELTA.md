# me-6b delta: `ve-units@2`

**Public output: none.** me-6b registers no service mode, command or route and changes no Python or Rust file:
`VE.Calc.Units` is reached only by the Lean build and `tests/test_calc_units.py`.

Trust growth, re-measured with `uv run python tools/trust_map.py --check` on the final code: K +0, S +0, untied V +60,
recorded with `trust_map.py --allow` in `docs/trust-baseline.json`. The ties-pass row R16 asks for is in
manage-agents FOLLOW-UPS.md, section "## me-6b". [`trust-mutants.json`](trust-mutants.json) is
`tools/trust_mutants.py --max-mutants 1000` on the final Lean change (0c83cac0b): 88 of 89 mutants killed by the
`#guard`s of the generated `lean/VE/Calc/UnitsExamples.lean`, 1 allowed as equivalent
([`trust-mutants-allow.json`](trust-mutants-allow.json)), 0 survivors, unknown or not run; exit 0.
[`mutants.json`](mutants.json) is the hand mutants' record on 4609cc74e: 32 of 32 killed.

| # | File | Trusted lines (class, declaration lines) | Exercised by (`tests/test_calc_units.py`) | Ruling |
|---|---|---|---|---|
| 1 | `lean/VE/Calc/Units.lean` | +60: D[V] 55 (`UnitDef` 7, `UnitEnv` 5, `decodeFactor` 9, `decodeUnit` 13, `decodeV2` 15, `decode` 6), G[V] 5 (`UnitEnv.unit?` 2, `UnitEnv.values` 3) | `test_fixture[refuse-*]`, `[factor-*]`, `[i2-*]`, `[h7c*]`, `[h7l*]`, `[claim-*]`, `test_malformed_environment[*]`; `trust-mutants.json` (every mutant of `decodeFactor`, `decodeUnit`, `decodeV2` and `UnitEnv.unit?` killed or allowed); hand mutants `factor-pos`, `factor-spelling`, `unit-dim`, `unit-day`, `unit-exponent-string`, `v2-nodup`, `v2-schema`, `decode`, `find`, `values` | SIGNED by standing ruling R16 (DRI-RULINGS.md) |
