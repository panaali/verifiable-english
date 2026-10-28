# me-4 delta: tables and pinned data, the Lean core

Base `379130067` (`git merge-base HEAD main`). **Public output: none.** No service mode, command, route, schema,
Python product code or Rust file changes: the `Handles` data kind and the relay are me-4b, and nothing public reads
the new modules yet. No approved statement changes: the twelve theorems equal spec 4.1 to 4.3 after whitespace
normalisation, and `lean/statements.txt` only adds theorems. The one row is the trusted-base growth.

| # | Change | Evidence | Ruling |
|---|---|---|---|
| 1 | Trusted base: K +0, S +54, untied V +94, total +148 (`tools/trust_map.py --check` on the final HEAD, PASS with the allowance in `docs/trust-baseline.json`): `lean/VE/Calc/Table.lean` +67 (S `Cell`, `Table`, `Table.cell`, `Filter`, `Filter.Selects`, `Table.numbers`, `mean?`, `Agg`, `Agg.run`; D[V] `ColType`, `readCell`), `lean/VE/Calc/Csv.lean` +34 (D[V] `CsvMode`, `csvRecords`, `columnTypes`, `decodeCsv`), `lean/VE/Calc/Jsonl.lean` +34 (D[V] `jsonScalar`, `jsonFlatObject`, `jsonCell`, `decodeJsonl`), `lean/VE/Calc/Data.lean` +13 (D[V] `Format`, `DataDecl`, `decodeTable`). `runCounted` is G[V] tied to `counted_bound` and `counted_exhausted`; `Filter.sel`, `Table.select`, `Filter.selB`, `Table.selectB` and `Agg.runB` are C (`Filter.sel_iff`, `Table.select_iff`, `Agg.runB_sound`) | every new trusted definition is exercised by a check that can fail: `trust-mutants.json` (`tools/trust_mutants.py` on the final Lean change: 253 KILLED, 0 SURVIVOR, 0 UNKNOWN; equivalents, mutants Lean refuses and the proposition `Filter.Selects` allowed in `trust-mutants-allow.json`, each with its reason) and `mutants.json` (hand mutants of `Table.cell`, `decodeTable`, `Filter.Selects` and `Agg.run`, which the tool cannot reach or counts as allowed); FOLLOW-UPS "## me-4" asks for the ties pass | R16 |
