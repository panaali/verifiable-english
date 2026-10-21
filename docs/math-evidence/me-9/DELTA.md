# me-9 delta: algebraic identities, the normaliser

Base `2f633d7b5` (`git merge-base HEAD main`). **Public output: none.** me-9 adds one Lean module
(`lean/VE/Calc/Poly.lean`) and its fixture test (`tests/test_calc_algebra.py`): no service mode, command, route, schema,
Python product code or Rust file, so no verdict, diagnostic, fault order or line a user can see changes. The only row is
the trust growth.

Re-measured on the final code with `uv run python tools/trust_map.py --check`: K +0, S +3, untied V +0, trusted +3
against `2f633d7b595a`, recorded with `--allow` (allowance S 3 in `docs/trust-baseline.json`); `--check` passes.
The R16 ties row is in manage-agents FOLLOW-UPS.md, section "## me-9".

| # | File | Trusted lines (class, declaration: lines) | Exercised by | Ruling |
|---|---|---|---|---|
| 1 | `lean/VE/Calc/Poly.lean` | +3: S (`Poly.eval` 3) | `tests/test_calc_algebra.py::test_fixture[binom-value]`; the statements of `Poly.ofExpr_sound` and `Frac.ofExpr_sound`; mutant 3 in [`mutants.json`](mutants.json) | R16 (standing ruling, DRI-RULINGS.md) |
