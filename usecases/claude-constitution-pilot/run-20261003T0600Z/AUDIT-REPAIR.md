# Audit repair

Input: the audit of run `20261002T1800Z` (`AUDIT-20261002T1800Z-received.md`): **19 of 20 sampled units faithful, 1 unfaithful** (`u0168.s01`). The audit sampled
1 CHECKED, 7 LABELLED, 6 OPEN and 6 READINGS units and named only the rejected one, so the 19 accepted units cannot be identified from it.

The rule behind the repair (from the audit's own account): a source that calls the lines absolute and says they should never be crossed regardless of seemingly compelling arguments cannot
keep a reading in which an open exception can make firmness not required. Same shape as the hard-constraint repairs of run `20261002T0620Z` (the defeasible candidate removed, one strict reading
chosen from cited spans, not silently).

| Unit | Finding | Repair | Status before → now |
|---|---|---|---|
| `u0168.s01` ("When faced with seemingly compelling arguments to cross these lines, Claude should remain firm.") | The defeasible reading kept in the reading set had an open exception that can make firmness *not required*; the source calls these lines absolute, to be held "regardless of … seemingly compelling arguments" (`u0166.s01`) and says "the strength of an argument is not sufficient justification for acting against these principles" (`u0168.s03`). That weakens the instruction. | The defeasible candidate is removed (also from the S1 companion). One strict rule carries the sentence as content in the main document and in the strict companion; completion `unspecified`, duty on instances of Claude only; the force choice is recorded with its two cited spans (`force_resolution` in `units.json`). VE: the case holds → SETTLED yes; the case does not hold → UNDECIDED. | READINGS → OPEN (one reading; claimed, not re-audited) |

The audit's three further points are language work and are addressed only where S1 makes them possible: (1) "let reading candidates carry checkable rules" — done on the soft route (`readings/s1.ve.md`, ten sets);
"make source-supported force choices binding" — `u0168.s01` is now one reading, but the language still cannot say "this choice is supported by that sentence" as a checked link; (2) "combine unspecified outcomes with defeasible norms without inventing a completion" — **not possible at this tag**
(`readings@1` content and `norm-defaults@0` do not compose, `FEATURE-REVIEW.md`); (3) "cross-sentence scope and force dependencies" — not possible (F14).

## Status of every unit an audit rejected (no covered status without a repair)

| Unit | Rejected by | Status now | Repair |
|---|---|---|---|
| `u0168.s01` | 20261002T1800Z | OPEN | above; not re-audited |
| `u0062.s01`, `u0123.s02.p1`, `u0166.s04.p4` | 20261002T0620Z | READINGS, READINGS, OPEN | scoped permissions / ability statement (run 20261002T1800Z); not re-audited. In this run their readings also carry content in the S1 companion (same scope). |
| `u0165.s02`, `u0165.s04`, `u0165.s06` | 20261001T1800Z | OPEN (one strict reading, content) | repaired in run 20261002T0620Z; not re-audited |
| `u0165.s01`, `u0165.s03`, `u0165.s05`, `u0165.s07` | same shape (s03, s05, s06 rejected by earlier audits) | OPEN | same; not re-audited |
| `u0156.s03`, `u0125.s04.p2` | 20260929T1800Z / same defect class | READINGS | strict reading is a prohibition (permission predicate, `unspecified`); not re-audited |

## What audit-verified means this run

Verified = accepted by an audit of this lineage AND byte-identical to the audited form. This run: **734 substantive bytes (0.40%) + 328 label bytes**. The previous run's 830 bytes included `u0168.s01`
(96 bytes), accepted by an earlier audit and rejected by the latest, so it leaves the list (asserted in `finish.py`: 830 − 96 = 734). The 19 units the last audit accepted cannot be added: the audit does not list them.
Repaired but not verified: 1,679 bytes (the seven hard constraints `u0165.s01`–`s07`, `u0125.s04.p2`, `u0062.s01`, `u0123.s01.p1`, `u0123.s02.p1`, `u0166.s04.p4`, `u0168.s01`). Claimed but not audit-verified: 2,385 bytes.
