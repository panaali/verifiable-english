# Audit repair, run 20261005T1800Z

The audit received for the previous run (`AUDIT-20261005T0600Z-received.md`, 20/20 FAITHFUL) rejected no unit and marked none incomplete, so no unit needed repair and no unit lost a covered status.

Its sample: CHECKED 1, LABELLED 7, OPEN 6, READINGS 6. Verdicts by unit: `u0248`, the labels `u0286.heading`, `u0013.heading`, `u0055.heading`, `u0008.heading`, `u0023`, `u0126`, `u0282` (label bytes were verified already), the OPEN units `u0168.s01`, `u0165.s07`, `u0165.s01`, `u0166.s04.p4`, `u0165.s04`, `u0165.s03`, the READINGS units `u0125.s04.p2`, `u0123.s02.p1`, `u0036.s05`, `u0123.s01.p1`, `u0062.s01`, `u0263.s04.p2`.

Audit-verified covered bytes: 1,419 → 2,296 (+877): `u0165.s04` 175, `u0165.s03` 89, `u0123.s02.p1` 348, `u0123.s01.p1` 180, `u0062.s01` 85. Each is byte-identical to the form the audit saw: `finish.py` asserts that `units.json`, `translation.ve.md` and the three companion documents equal the previous run's, and that `ve document check` of the main, strict and default documents gives the previous run's output. `u0123.s03` was repaired in the same way as its neighbours but not sampled, so it stays claimed, not verified. Claimed but not verified: 359 bytes (2,996 − 2,296 − 341).
