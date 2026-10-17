# Seeded bugs, 2026-10-17T1800Z

No file under `ve/`, `lean/` or `rust/` was changed by this run (`git diff ve-green-rights-licence-relay HEAD -- ve lean rust` is empty; the two
merges since the last tag are tests and a trust-tool rule), so there is no changed Lean, Python or Rust behaviour to plant a bug in. The earlier
planted bugs are in the 2026-10-14 run's `previous-20261014T1800Z/seeded-bugs.md`; the code and documents they concern are unchanged.

What this run changed is pilot data: two reading sets (u037, u027) and their ledger. The checks that would catch a wrong repair were re-run at
ve-green-fu-ar2-decoders (foreground): each new candidate is written as its own document and checked (`repair15.py`: premises `model`, and every Lean
status row as expected, including a detention that is not arbitrary and a punishment that is not cruel, inhuman or degrading, which separate the two
readings); the four parts (`check_parts.py`), the 61 companions and their 135 status rows (`witnesses_all.py`), the unit comparison against the previous
run's parts (`compare_units.py`: 128 of 130 equal, the two others are u027 and u037), the wrong-separating-situation refusal (`refusal_test.py`), the
QT-0p isolated measurement (`qt0p_isolated.py`: part03 OPEN +76 B, premises `model`) and the whole-declaration load and check (`whole.py`, `whole_check.py`).
