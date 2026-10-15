# Seeded bugs, 2026-10-15T0600Z

No file under `ve/`, `lean/` or `rust/` was changed by this run, and no translation unit, vocabulary or reading was changed (the four
parts are the previous run's, byte for byte). There is therefore no new behaviour to plant a bug in. The previous run's two planted
bugs (the `integrate.py` two-argument guard for u106 and the `is_fundamental` guard of the u097 companion) are in
`previous-20261014T1800Z/seeded-bugs.md`; the code and documents they concern are unchanged.

Re-run instead of re-planted this run, all at ve-green-lf-14b: the four parts (`check_parts.py`), the 59 companions and their 118 Lean
status rows (`witnesses_all.py`), the unit comparison (130 of 130 equal), the wrong-separating-situation refusal (`refusal_test.py`),
the QT-0p isolated measurement (`qt0p_isolated.py`), and the whole-declaration load (`whole_check.py`).
