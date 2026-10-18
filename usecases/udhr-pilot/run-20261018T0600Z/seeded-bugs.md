# Seeded bugs, 2026-10-18T0600Z

This run changed no file under `ve/`, `lean/` or `rust/` (it only added files under `usecases/udhr-pilot/`), so there is no changed Lean, Python or Rust
behaviour to plant a bug in. The merges since the last tag (lf-16f/g, rd-7, me-1a and tests/tools) were each seeded and reviewed in their own batches.
Earlier planted bugs for the pilot are in the 2026-10-14 run's `previous-20261014T1800Z/seeded-bugs.md`; the code and documents they concern are unchanged.

What this run measured is the pilot data at the new tag (all foreground): `check_parts.py` (four parts), `witnesses_all.py` (61 companions, 135 Lean status rows),
`compare_units.py` (130 of 130 units equal to the previous run's), `integrate.py all` (all four parts rebuilt byte for byte), `refusal_test.py` (a wrong separating
situation is refused), `qt0p_isolated.py` (part03 OPEN +76 B, premises `model`) and `whole.py` + `whole_check.py` (the whole declaration as one document).
