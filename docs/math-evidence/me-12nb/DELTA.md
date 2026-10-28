# me-12nb delta: the `arith@0` draft 5 charge

Base `d9cff5345` (`git merge-base HEAD main`). **Public output: none**, so the table has no row:

- **No caller.** me-12nb changes the budgeted evaluator in `lean/VE/Arith/Bounded.lean` and its fixtures
  (`BoundedExamples.lean`, `CompleteExamples.lean`), and nothing public reads the core yet: no service mode, command,
  route, schema, Python product code or Rust file changes (the wire is me-12b). The units the core computes change
  (spec 13.3, draft 5); no user sees them before me-12b.
- **Trust budget: +0.** `uv run python tools/trust_map.py --check` passes: K +0, S +0, D +0, G +0, unclassified +0,
  trusted +0. The new definitions `bits`, `chargeBits` and `stepB` are C, as the evaluator is, so there is no R16
  allowance and no ties-pass row. `tools/trust_mutants.py` selects 0 definitions ([`trust-mutants.json`](trust-mutants.json));
  each new definition has hand mutants, killed by named proofs and guards ([`mutants.json`](mutants.json)).
- **No approved statement changes.** The evaluator, `decideBounded_sound`, `_mono`, `_work`, `_complete`,
  `Term.evalB_bits` and the three bit-length bounds equal spec 12.2 (draft 5, main `d9cff5345`) after whitespace
  normalisation; `decideBounded_covered` keeps me-12ab's text. `lean_statements.py --check` reports 0 added, 0 removed
  and 0 changed; the regenerated `lean/statements.txt` only adds theorems.
