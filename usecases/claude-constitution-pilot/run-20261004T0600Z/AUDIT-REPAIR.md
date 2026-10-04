# Audit repair

Input: the audit of run `20261003T0600Z` (`AUDIT-20261003T0600Z-received.md`): **14 of 20 sampled units faithful, 6 unfaithful**. Sample: 1 CHECKED, 7 LABELLED, 6 OPEN, 6 READINGS; its VERDICTS block names all 20, and all six rejections are repaired below. The audit's defect class is the same in five of six: a companion completes a duty or a permission with `deny`, which says "not required" (or "forbidden") outside the stated conditions, and the source says nothing there.

| Unit | Finding | Repair | Status before → now |
|---|---|---|---|
| `u0036.s05`, `u0263.s04.p2` | companion `deny` completions assert "not required" outside the stated conditions | the defeasible reading is no longer elaborated in any companion that counts; both readings stay in the main document's reading set (no content, so nothing is invented); the strict reading is elaborated in `readings/all-strict.ve.md` with `unspecified`. `readings/all-default.ve.md` and `readings/s1.ve.md` stay as demonstrations only (not claimed) | READINGS → READINGS (no companion content claimed) |
| `u0156.s03` | the defeasible companion turns an exception into "not required to avoid deception" | same; the strict reading stays a prohibition (permission predicate, `unspecified`) | READINGS → READINGS |
| `u0078.s01` | "err on the side of following" is a preference; the strict candidate makes it mandatory compliance, neither candidate keeps the leaning, companion defaults settle unstated cases negatively | no duty is stated: the unit is UNFORMALISED, missing feature `other:graded-force`; the reading set, rules, regulated predicate and seven open terms are removed from every document | READINGS → UNFORMALISED |
| `u0123.s03` | S1 completion forbids unaddressed inputs; ability candidates deny the *supply of instructions*, not the ability to get Claude to do the behaviour; four readings do not make their content faithful | the S1 companion no longer counts; the two ability candidates of the main document now read "for each of the six behaviours, an operator is unable to get Claude to do it by instructing it" (narrow, and wide with "while Claude role-plays a custom AI persona"); the narrow permission stays in the strict companion with `unspecified` | READINGS → READINGS (candidate texts changed) |
| `u0073.s05` | `deny` completion on the soft route | one reading with content in the main document under `norm-defaults@0` (`unspecified`): guard = an operator prompt addresses the case; exceptions = complying is unsafe, unethical, against Anthropic's guidelines, plus the named open exception `general_exception_to_complying` for "generally". VE: addresses and no exception → SETTLED yes; addresses and unsafe → UNDECIDED; exception applies → UNDECIDED; not addressed → UNDECIDED. The English form parses back (the guard form with a nested all-of list did not) | READINGS → OPEN |

The audit's three further points, answered only where the language allows: (1) compose `readings@1`, defeasible norms and `unspecified` — **not possible at this tag** (probe `probes/s1-probe.json` unchanged: `readings@1` is refused beside `norm-defaults@0`); (2) represent preferences and graded force — **not possible**: `u0078.s01` is now UNFORMALISED with `other:graded-force`; (3) link reading choices across sentences — not possible (F14).

## Status of every unit an audit rejected (no covered status without a repair)

| Unit | Rejected by | Status now | Repair |
|---|---|---|---|
| `u0036.s05`, `u0156.s03`, `u0263.s04.p2`, `u0123.s03` | 20261003T0600Z | READINGS | above; not re-audited |
| `u0073.s05` | 20261003T0600Z | OPEN | above; not re-audited |
| `u0078.s01` | 20261003T0600Z | UNFORMALISED | above |
| `u0168.s01` | 20261002T1800Z | OPEN | one strict reading from cited spans; not re-audited |
| `u0062.s01`, `u0123.s02.p1`, `u0166.s04.p4` | 20261002T0620Z | READINGS, READINGS, OPEN | scoped permissions / ability statement; not re-audited |
| `u0165.s01`–`s07`, `u0125.s04.p2` | 20261001T1800Z and earlier | OPEN, READINGS | strict prohibition; not re-audited |

## What audit-verified means this run

Verified = accepted by an audit of this lineage AND byte-identical to the audited form. This run: **755 substantive bytes (0.41%) + 328 label bytes**. The previous run's 734 bytes included `u0036.s05` (68), `u0263.s04.p2` (115) and `u0078.s01` (451), which this audit rejected: 734 − 634 = 100 (`u0248`, `u0052.s01`). Unlike earlier audits, this one lists a verdict for every sampled unit, so its 14 acceptances are identified; the six substantive ones not yet in the list, each byte-identical to the form it saw (`u0165.s01`, `s02`, `s05`, `s06`, `s07`, `u0166.s04.p4`: 655 bytes), join, superseding their earlier rejections; its label units were already in the list. 100 + 655 = 755, asserted in `finish.py`. Repaired but not verified: 1,892 bytes (the repaired units that no audit has accepted and that still have a covered status: `u0165.s03`, `s04`, `u0125.s04.p2`, `u0062.s01`, `u0123.s01.p1`, `u0123.s02.p1`, `u0168.s01`, and the five covered units repaired now). Claimed but not audit-verified: 1,913 bytes.
