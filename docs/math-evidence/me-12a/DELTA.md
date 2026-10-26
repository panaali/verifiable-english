# me-12a delta: the `arith@0` statement API

Base `7855620f3` (`git merge-base HEAD main`). **Public output: none.** me-12a adds Lean modules (`lean/VE/Arith/`
`Syntax.lean`, `Holds.lean`, `Defs.lean`, `Examples.lean`) and `lean/ARITH.md`: no service mode, command, route,
schema, Python product code or Rust file, so no verdict, diagnostic, fault order or line a user can see changes. The
refusals of `caseRefusal` reach users only through me-12b's decoder. The only row is the trust growth.

Re-measured on the final code with `uv run python tools/trust_map.py --check`: K +0, S +93, untied V +0, trusted +93
against `7855620f3e06`, recorded with `--allow` (allowance S 93 in `docs/trust-baseline.json`); `--check` passes.
The R16 ties row is in manage-agents FOLLOW-UPS.md, section "## me-12a".

| # | File | Trusted lines (class, declaration: lines) | Exercised by | Ruling |
|---|---|---|---|---|
| 1 | `lean/VE/Arith/Syntax.lean`, `lean/VE/Arith/Holds.lean`, `lean/VE/Arith/Examples.lean` | +93: S (`Term`, `Formula`, `Def`, `Defs`: 31; `Env`, `Term.value`, `Term.values`, `Holds`, `Defs.env`, `Defs.Means`: 60; `IsPrime`: 2) | `primeBody_iff`, `bertrand_means_iff`, the meaning examples of `Examples.lean` (one per clause, both directions) and M-5's failure at n = 1; every one of the 163 mutants `trust_mutants.py` plans breaks one of them as written, or Lean refuses it ([`mutants.json`](mutants.json) `proof_kills`, [`trust-mutants.json`](trust-mutants.json) exit 0 with [`trust-mutants-allow.json`](trust-mutants-allow.json)) | R16 (standing ruling, DRI-RULINGS.md) |
