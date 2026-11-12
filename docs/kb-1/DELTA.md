# KB-1 user-visible deltas

Base: main `35a9ba135f` (`git merge-base HEAD main`). No service answer changes: no runner, schema or theorem
statement of an existing module is touched (`git diff 35a9ba135f... --stat -- lean/` lists only `lean/VE.lean`,
the two new `lean/VE/Kernel/` modules and generated inventories).

| # | Delta | Evidence | Ruling |
|---|---|---|---|
| 1 | `ve document check --help` gains a description: the DRI's wording of what a unit's CHECKED status means (fable-team/architect/inbox/20261111T0452Z-dri.md item b, as corrected; confirmed in 20261111T0838Z-dri.md item 1). The base help had no description, so no quoted name, path or specificity is lost; README.md quotes the same text | `tests/test_kernel_closure.py::test_the_readme_quotes_what_checked_means` | R1 |
| 2 | Trust budget: K +34 (`VE/Kernel/Carry.lean`: Path, Row, Path.row, Path.Ran, shell, carry, classed K by the task); `tools/trust_map.py --check` reports "K +34 ... PASS" against the allowance signed in `docs/trust-baseline.json` (3350e57cdf) | `docs/kb-1/trust-mutants.json` (exit 0: 24 KILLED, 14 INVALID, 8 ALLOWED), `docs/kb-1/trust-mutants-allow.json` | SIGNED by the DRI 2026-11-12 (reviews/dri-decisions-20261112-kb-1.md item 1) |
