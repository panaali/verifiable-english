# AR-1 deltas

AR-1 changes Lean tooling and generated inventories only. No Lean declaration is added or changed, and no
verdict, diagnostic, wire field, document-check CPU or trust count changes. `tools/trust_map.py --since cc534bfc`:
K +0, S +0, D +0, G +0, tied +0, trusted +0 (evidence/checks.json). None of the rows below is a user-visible delta
of the checker, so none needs a standing ruling or a DRI signature.

| Change | Kind | Ruling |
|---|---|---|
| `lean/audit.py` audits 5,780 theorems, not 5,252 (base 5479466f; Lean identical to 8b9927f2): the 528 added are 525 Prop fields of structures (VE and Iceberg) and 3 Prop-class instances (evidence/manifests.json). All use only `propext`, `Classical.choice` and `Quot.sound` | stricter tool check; nothing accepted that was refused | none needed |
| `lean/audit.py` fails when `lean/declarations.txt` records a module hash that differs from the source, or a module set that differs from the tree (the two manifests excepted: they are its outputs and are compared byte for byte) | stricter tool check (converged edit, Astra + Fable, 2026-10-10) | none needed |
| `lean/audit.py --check` is accepted (the default mode, as before) | additive CLI flag | none needed |
| `lean/statements.txt` gains the 528 entries; every kept entry is byte-identical (`lean_statements.py --diff` against main 8b9927f2 (Lean identical to the base 5479466f): added 528, removed 0, changed 0) | generated inventory, additions only | none needed |
| `tools/lean_statements.py` takes the statement names from the manifest generated from its own dump, not from the file, and records each manifest's generated hash. It reads the predicates and the statements in two Lean runs instead of one | tooling; same outputs on a current tree | none needed |
| The `example` pinning the approved statement of `VE.SoftNorms.coh_rank_valid` moves from `VE/Audit.lean` (now generated) to `VE/SoftNorms/Status.lean`, beside the theorem, unchanged | a check moved, not removed (mutant L1 shows it still binds) | none needed |
| `lean/VE/Route/frozen-sources.sha256`: `VE/Audit.lean` and `VE/SoftNorms/Status.lean` rehashed | generated inventory (R12) | R12 |
