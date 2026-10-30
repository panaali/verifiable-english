# me-4 delta: tables and pinned data, the Lean core

Base `379130067` (`git merge-base HEAD main`). **Public output: none.** No service mode, command, route, schema,
Python product code or Rust file changes: the `Handles` data kind and the relay are me-4b, and nothing public reads
the new modules yet. No approved statement changes: the twelve theorems equal spec 4.1 to 4.3 after whitespace
normalisation, and `lean/statements.txt` only adds theorems. The one row is the trusted-base growth.

| # | Change | Evidence | Ruling |
|---|---|---|---|
| 1 | Trusted base: K +0, S +54, untied V +96, total +150 (`tools/trust_map.py --check`, PASS with the R16 allowances in `docs/trust-baseline.json`): `lean/VE/Calc/Table.lean` +68 (the original S definitions; D[V] `ColType`, `readCell`, shared `tableDimensions`), `lean/VE/Calc/Csv.lean` +34 (D[V] CSV decoder), `lean/VE/Calc/Jsonl.lean` +35 (D[V] JSON-lines decoder), `lean/VE/Calc/Data.lean` +13 (D[V] data dispatch). `runCounted` remains tied to `counted_bound` and `counted_exhausted`. No public route reads these modules yet. | Every new trusted definition is exercised by a check that fails on a seeded bug: `TableExamples.lean` guards for 64/65 columns in both formats and 1,000,000/1,000,001 rows in the shared check; the CSV `!` and tab guards kill the formerly allowed equality mutants. The saved mutation run is `trust-mutants.json`; the existing FOLLOW-UPS "## me-4" asks for the ties pass. | R16 |
