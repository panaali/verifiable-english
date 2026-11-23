# statute-feature-ambig delta: ambiguous text answered under each named reading (`usecases/reading_runs.py`)

Base: `git merge-base HEAD main` (df25d3c3b3). The branch adds one use-case helper outside VE core and the kernel,
`usecases/reading_runs.py`, and its tests, `tests/test_reading_runs.py`. Ruling: orchestrator 2026-11-23T18:21Z (feature
C, build for main), manage-agents inbox/dri/done/20261123T182152Z-orchestrator-2693027.md.

**Public output: none changes.** No service mode, runner, decoder, encoder, Lean file, profile, schema or refuses pair
changes; no file under `ve/`, `lean/` or `rust/` changes. The helper calls a law's own use-case runner (its `run.py`
`main()`, which Lean-checks every answer exactly as today) once per reading and reads VE's existing checked-English
renderer (`ve.surface.time.render_w6_sentence` / `parse_w6_sentence`) for the read-back; it adds no verdict path.

## Trust and kernel, measured on the branch
- Trust map: `python tools/trust_map.py --check` -> "against df25d3c3b3d8: K +0, S +0, D +0, G +0, tied +0, unclassified
  +0, trusted +0" and "PASS: K, S and untied [V] within df25d3c3b3d8 and the allowances introduced since".
- Kernel: `python tools/kernel_closure.py` -> "kernel (distinct lines of every path of tier kernel): 9738" before
  (main df25d3c3b3) and after (this branch).

## User-visible deltas
None: the helper is a use-case tool; no trusted line is added or removed, so the table has no row.

| # | File | Trusted lines (class, declarations) | Exercised by | Ruling |
|---|---|---|---|---|
