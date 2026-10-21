# me-5b delta: the lowering of a derivation's claims and its meaning

Base `ca15b6d1c` (`git merge-base HEAD main`). **Public output: none.** me-5b adds two Lean modules
(`lean/VE/Calc/Lower.lean`, `LowerExamples.lean`) and moves one theorem (`freeNames_mem`, from `Identity.lean` to
`Inline.lean`, unchanged): no service mode, command, route, schema, Python product code or Rust file, so no verdict,
diagnostic, fault order or line a user can see changes. A derivation reaches users only through ME-2's `calc` mode and
the `follows` check (me-5c). The only row is the trust growth.

Re-measured on the final code with `uv run python tools/trust_map.py --check`: K +0, S +12, untied V +0, trusted +12
against `ca15b6d1ca00`, recorded with `--allow` (allowance S 12 in `docs/trust-baseline.json`); `--check` passes.
The R16 ties row is in manage-agents FOLLOW-UPS.md, section "## me-5b".

| # | File | Trusted lines (class, declaration: lines) | Exercised by | Ruling |
|---|---|---|---|---|
| 1 | `lean/VE/Calc/Lower.lean` | +12: S (`Follows` 6, `HasCounterexample` 6) | the proofs of `not_follows_of_counterexample`, `follows_of_check` and `counterexample_of_check`, which every mutant of them breaks ([`mutants.json`](mutants.json) 25 to 43, [`trust-mutants.json`](trust-mutants.json)), and `r3_follows`, `r4_not_follows` in `LowerExamples.lean` | R16 (standing ruling, DRI-RULINGS.md) |
