# Seeded bugs, 2026-10-17T0600Z

No file under `ve/`, `lean/` or `rust/` was changed by this run, and no translation unit, vocabulary or reading was changed (the four
parts are the 18:00Z run's, byte for byte). There is therefore no new behaviour to
plant a bug in. The earlier planted bugs are in the 2026-10-14 run's `previous-20261014T1800Z/seeded-bugs.md`; the code and documents
they concern are unchanged.

Re-run instead of re-planted this run, all at ve-green-rights-licence-relay (foreground): the four parts (`check_parts.py`), the 59 companions and
their 118 Lean status rows (`witnesses_all.py`, identical to the previous run's), the unit comparison against the previous run's parts
(`compare_units.py`: 130 of 130 equal), the wrong-separating-situation refusal (`refusal_test.py`), the QT-0p isolated measurement
(`qt0p_isolated.py`: part03 OPEN +76 B, premises `model`), and the whole-declaration load and check (`whole.py`, `whole_check.py`).

The only edit this run is to `units.json` (the ledger lines of u052 and u114, `repair14.py`); that file is a pilot record, not product code, so there is nothing to plant a bug in.
