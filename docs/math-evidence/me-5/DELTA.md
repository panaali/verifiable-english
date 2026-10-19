# me-5 delta: derivations over rational unknowns, at the level of facts

Base `b7613541c` (`git merge-base HEAD main`). **Public output: none.** me-5 adds Lean modules only
(`lean/VE/Calc/{Linear,FourierMotzkin,Derive,DeriveExamples}.lean`): no service mode, command, route, schema, Python
or Rust file, so no verdict, diagnostic, fault order or line a user can see changes. The only row is the trust growth.

Re-measured on the final code with `uv run python tools/trust_map.py --check`: K +0, S +6, untied V +0, trusted +6
against `b7613541cbd3`, recorded with `--allow` (allowance S 6 in `docs/trust-baseline.json`); `--check` passes.
The R16 ties row is in manage-agents FOLLOW-UPS.md, section "## me-5".

| # | File | Trusted lines (class, declaration: lines) | Exercised by | Ruling |
|---|---|---|---|---|
| 1 | `lean/VE/Calc/Linear.lean` | +4: S (`QLin.eval` 1, `QFact.Holds` 3) | `DeriveExamples.lean` #guards 33, 41, 42, 47, 83, 84; mutants 5 and 6 in [`mutants.json`](mutants.json) | R16 (standing ruling, DRI-RULINGS.md) |
| 2 | `lean/VE/Calc/Derive.lean` | +2: S (`Answer.point` 2) | `DeriveExamples.lean` #guard 84; mutant 8 | R16 (standing ruling, DRI-RULINGS.md) |
