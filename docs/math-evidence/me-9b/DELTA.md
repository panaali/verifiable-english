# me-9b delta: inlining and identities over named values

Base `6454946a5` (`git merge-base HEAD main`). **Public output: none.** me-9b adds Lean modules
(`lean/VE/Calc/Inline.lean`, `Identity.lean`, `IdentityExamples.lean`) and fixtures in `tests/test_calc_algebra.py`:
no service mode, command, route, schema, Python product code or Rust file, so no verdict, diagnostic, fault order or
line a user can see changes. The runner's rows reach users only through ME-2's `calc` mode. The only row is the trust
growth.

Re-measured on the final code with `uv run python tools/trust_map.py --check`: K +0, S +18, untied V +0, trusted +18
against `6454946a5f54`, recorded with `--allow` (allowance S 18 in `docs/trust-baseline.json`); `--check` passes.
The R16 ties row is in manage-agents FOLLOW-UPS.md, section "## me-9b".

| # | File | Trusted lines (class, declaration: lines) | Exercised by | Ruling |
|---|---|---|---|---|
| 1 | `lean/VE/Calc/Inline.lean`, `lean/VE/Calc/Identity.lean` | +18: S (`freeNames` 4, `assign` 4; `IsIdentity` 5, `NotIdentity` 5) | `freeNames`, `assign`: the `#guard`s of `IdentityExamples.lean` and `test_fixture[free-names]`, `[assign]`; `IsIdentity`, `NotIdentity`: the proofs of `isIdentity_of_check`, `notIdentity_of_differsAt` and `not_isIdentity`, which every mutant of them breaks; [`mutants.json`](mutants.json) 20 to 30 and [`trust-mutants.json`](trust-mutants.json) | R16 (standing ruling, DRI-RULINGS.md) |
