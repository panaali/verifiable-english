# me-7 delta: exact statistics, the Lean meanings

Base `d8f58bf3b` (`git merge-base HEAD main`). **Public output: none.** No service mode, command, route, wire row,
schema, Python product code or Rust file changes: the `Expr` and `Claim` constructors are me-7b and the wire rows
ME-10's, so nothing public reads the new module yet. No approved statement changes: `lean/statements.txt` only adds
24 theorems (none removed or changed), and spec 7's 25 declarations appear verbatim in `lean/VE/Calc/Stats.lean`
(`evidence/check_statements.txt`). The one row is the trusted-base growth.

| # | Change | Evidence | Ruling |
|---|---|---|---|
| 1 | Trusted base: K +0, S +84, untied V +0, total +84 (`uv run python tools/trust_map.py --check`: PASS with the R16 allowance in `docs/trust-baseline.json`): `lean/VE/Calc/Stats.lean` S +83 (`mean?` (moved from Table.lean), `sampleVariance?`, `populationVariance?`, `rootGe`, `rootGt`, `rootLe`, `rootLt`, `rootEq`, `SqrtRoundsTo`, `signs`, `absR`, `signFlipP`, `choose`, `binomialTail`, `kappa?`, `Stat`, `Stat.minLength`, `Stat.run`), `lean/VE/Calc/Table.lean` S +1 (`Agg.variance`, `Agg.populationVariance` and their `Agg.run` arms, net of `mean?` moving out). | Every new trusted definition is exercised by a check that can fail: `docs/math-evidence/me-7/trust-mutants.json` at `123e24e12` (212 KILLED, 145 ALLOWED, 32 INVALID, 0 SURVIVOR, 0 UNKNOWN; reasons in `trust-mutants-allow.json`), seeded bugs S1 to S7 in `mutants.json`; FOLLOW-UPS.md "## me-7" asks for the ties pass. | R16 |
