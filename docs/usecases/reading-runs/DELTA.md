# statute-feature-ambig delta: ambiguous text answered under each named reading (`usecases/reading_runs.py`)

Base: `git merge-base HEAD after-release` (4ea4a857b7; the branch merged after-release at d1074a8622). Merge target:
after-release only, never release B. The branch adds, outside VE core and the kernel:
- `usecases/reading_runs.py` and `tests/test_reading_runs.py`: the helper that runs a law's staged route once per named
  reading (ruling: orchestrator 2026-11-23T18:21Z, manage-agents inbox/dri/done/20261123T182152Z-orchestrator-2693027.md).
- `usecases/reading_compare.py`, `tests/test_reading_compare.py`, `tests/fixtures/reading_compare/` and
  `usecases/reading_tables/` (the reading tables, their runs, both match graders' outputs, the sealed per-reading answers
  with every value hashed, the frozen reading names, the checks and findings): the sealed-answer gate of the resume ruling
  (orchestrator 2026-11-24T00:00Z, manage-agents inbox/dri/done/20261124T000034Z-orchestrator-3444163.md, gates 1-6).
  The gate test `test_the_reading_tables_pass_the_sealed_gate` reads that folder, so `tools/select_tests.py` selects it for
  any change there; it fails on a per-reading answer that differs from the sealed answer of its matched reading, on a
  run or check made on another version of a table, and on a reading whose frozen name changed.

**Public output: none changes.** No service mode, runner, decoder, encoder, Lean file, profile, schema or refuses pair
changes; no file under `ve/`, `lean/` or `rust/` changes. The helper calls a law's own use-case runner (its `run.py`
`main()`, which Lean-checks every answer exactly as today) once per reading and reads VE's existing checked-English
renderer (`ve.surface.time.render_w6_sentence` / `parse_w6_sentence`) for the read-back; the gate only reads files. Neither
adds a verdict path. The laws' use cases (pawhp, tenant_fees, faa-medical, uc_award, hicbc) are not on this branch; their
tables are data the gate checks, and each run file records the table it ran.

## Trust and kernel, measured on the branch
- Trust map: `python tools/trust_map.py --check` -> "against 4ea4a857b705: K +0, S +0, D +0, G +0, tied +0, unclassified
  +0, trusted +0" and "PASS: K, S and untied [V] within 4ea4a857b705 and the allowances introduced since".
- Kernel: `python tools/kernel_closure.py` -> "kernel (distinct lines of every path of tier kernel): 9738" before (branch
  at 843bed8223, and after-release 4ea4a857b7) and after (this branch, after-release merged in).

## User-visible deltas
None: the helper and the gate are use-case tools; no trusted line is added or removed, so the table has no row.

| # | File | Trusted lines (class, declarations) | Exercised by | Ruling |
|---|---|---|---|---|
