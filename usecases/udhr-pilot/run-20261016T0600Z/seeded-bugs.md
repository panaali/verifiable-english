# Seeded bugs, 2026-10-16T0600Z

No file under `ve/`, `lean/` or `rust/` was changed by this run, and no translation unit, vocabulary or reading was changed (the four
parts are the 18:00Z run's, byte for byte; `previous-20261015T1800Z/` holds that run's copies). There is therefore no new behaviour to
plant a bug in. The earlier planted bugs are in `previous-20261014T1800Z/seeded-bugs.md` (in the 2026-10-14 run); the code and documents
they concern are unchanged.

Re-run instead of re-planted this run, all at ve-green-premise-scale: the four parts (`check_parts.py`), the 59 companions and their 118
Lean status rows (`witnesses_all.py`, identical to the previous run's), the unit comparison against the previous run's parts (130 of 130
equal), the wrong-separating-situation refusal (`refusal_test.py`), the QT-0p isolated measurement (`qt0p_isolated.py`: part03 OPEN +76 B,
premises `model`), and the whole-declaration load and check (`whole_check.py`: both succeed this time).
