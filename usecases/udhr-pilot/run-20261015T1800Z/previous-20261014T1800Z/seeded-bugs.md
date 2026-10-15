# Seeded bugs, 2026-10-14T1800Z

No file under `ve/`, `lean/` or `rust/` changed, so there is no product bug to plant. Two pilot-harness changes were planted and restored:

1. `integrate.py`, the guard in `as_assertion` that keeps a plain predicate with two arguments (u106) as a norm unit: removed; `integrate.py u104 u114` fails with
   `ValueError: too many values to unpack (expected 1, got 2)` at `(sort,) = decl["arguments"]`; restored (file identical to the checked one).
2. The u097 companion's guard with `is_fundamental` dropped (checked on a temporary copy): Lean's status row for the `fund` control is UNDECIDED and the witness
   `witnesses_nd.run` reports `as_expected: False` for `['fund']`; the real companion passes all four rows.
