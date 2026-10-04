# Audit repair

Input: the audit of run `20261004T0600Z` (`AUDIT-20261004T0600Z-received.md`): **18 of 20 sampled units faithful, 2 unfaithful** (sample: 1 CHECKED, 13 LABELLED, 3 OPEN, 3 READINGS; its VERDICTS block names all 20). Both rejections are repaired below. Both are the same defect: an *ability* candidate says something the text does not.

| Unit | Finding | Repair | Status before → now |
|---|---|---|---|
| `u0123.s01.p1` | "Operators are permitted to ask" states a permission outright; the ability candidate replaces it with a capability, and the transparency clause does not license that | the ability candidate is removed. The sentence has one reading, the scoped permission (the six limits of `u0123.s03` as exceptions; completion `unspecified`), carried as content in the main document and in `readings/all-strict.ve.md`; no reading set remains (9 → 8). The reason clause (`.p2`) stays UNFORMALISED (causation) | READINGS → OPEN |
| `u0062.s01` | the ability candidate describes what operators can "get Claude to do"; the source says operators can **give** instructions, a persona or information; supplying input does not entail inducing compliance | the ability candidate now reads "an operator is able to give Claude a specific set of instructions, a persona, or information (supplying input; it does not say Claude complies with it)", and the unit's note says so. The permission candidate and its three scoped rules are unchanged | READINGS → READINGS (candidate text changed) |
| `u0123.s02.p1` (not sampled) | same defect: "can legitimately instruct" had an ability candidate about what the party "can get Claude to do" | the candidate says what an operator is able to *instruct* Claude to do (supplying those instructions) and that doing so is legitimate (open term `instruction_is_legitimate`); the other two candidates are unchanged | READINGS → READINGS (candidate text changed) |

`u0123.s03` ("cannot instruct … X") keeps its ability candidates ("for each behaviour, an operator is unable to get Claude to do it by instructing it"): there the complement *is* what Claude is made to do, and the audit that checked them (20261003T0600Z) asked for exactly that wording; this audit did not sample the unit.

The audit's three further points, answered only where the language allows: (1) content-bearing `readings@1` beside `norm-defaults@0` and `unspecified` — **not possible at this tag** (`probes/s1-probe.json`, byte-identical); (2) typed modal expressions with explicit action complements — **not possible**: the language has no modal form, so the three ability readings (supply / instruct / get Claude to do) can only be told apart in the candidate texts, which carry no content; (3) linked reading choices across sentences — not possible (F14): the narrow/wide scope choice of `u0123.s03` does not reach the exceptions of the permissions that cite it.

## Status of every unit an audit rejected (no covered status without a repair)

| Unit | Rejected by | Status now | Repair |
|---|---|---|---|
| `u0123.s01.p1`, `u0062.s01` | 20261004T0600Z | OPEN, READINGS | above; not re-audited |
| `u0036.s05`, `u0156.s03`, `u0123.s03` | 20261003T0600Z | READINGS | repaired 20261004T0600Z; not re-audited |
| `u0263.s04.p2`, `u0073.s05` | 20261003T0600Z | READINGS, OPEN | repaired 20261004T0600Z; **accepted by the 20261004T0600Z audit** (now audit-verified) |
| `u0078.s01` | 20261003T0600Z | UNFORMALISED | repaired 20261004T0600Z (`other:graded-force`) |
| `u0168.s01` | 20261002T1800Z | OPEN | one strict reading from cited spans; not re-audited |
| `u0123.s02.p1`, `u0166.s04.p4` | 20261002T0620Z | READINGS, OPEN | `u0166.s04.p4` accepted by the 20261003T0600Z audit; `u0123.s02.p1` repaired again now |
| `u0165.s01`–`s07`, `u0125.s04.p2` | 20261001T1800Z and earlier | OPEN, READINGS | strict prohibition; `u0165.s01`, `s02`, `s05`, `s06`, `s07` accepted by the 20261003T0600Z audit |

## What audit-verified means this run

Verified = accepted by an audit of this lineage AND byte-identical to the form that audit saw. This run: **1,104 substantive bytes (0.60%) + 341 label bytes**. Previous run 755 + 328. The 20261004T0600Z audit accepted `u0263.s04.p2` and `u0073.s05` (byte-identical to the form it saw) and the label unit `u0001`, which join; its two rejections were never verified, so nothing leaves the list. `finish.py` asserts: previous verified bytes plus the bytes of the two units that joined, and previous label bytes plus `u0001`. Claimed but not audit-verified: 1,551 bytes, of which 1,543 are repaired units (including the three repaired now) that no audit has accepted.
