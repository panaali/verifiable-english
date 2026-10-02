# Audit repair

Input: the audit of run `20261002T0620Z` (`AUDIT-20261002T0620Z-received.md`): **17 of 20 sampled units faithful, 3 unfaithful**
(`u0062.s01`, `u0123.s02.p1`, `u0166.s04.p4`). The audit sampled 1 CHECKED, 6 LABELLED, 6 OPEN and 7 READINGS units and named only
the rejected ones, so the 17 accepted units cannot be identified from it (see "What audit-verified means").

The rule behind all three repairs (from the 2026-10-02 audit): translate every permission together with the limits the text attaches to
it, including limits in adjacent sentences; the permission's scope excludes what the limit forbids, so the two sentences never conflict;
never turn "cannot be unlocked" into a duty on someone; report a VE conflict as a finding only when the auditor accepted both readings.

| Unit | Finding | Repair | Status before → now |
|---|---|---|---|
| `u0062.s01` ("Operators can give Claude a specific set of instructions, a persona, or information.") | The permission allowed every input classified as instructions, a persona or information, including inputs `u0123.s03` says operators cannot give; VE reported a conflict the source does not contain. | Each of the three permission rules has the six kinds of `u0123.s03` as exceptions (`unless`), so an input of one of those kinds is not covered by the permission. No default is added for any other input (completion `unspecified`). The ability candidate is unchanged (it is existential: operators can give some such input; it states no limit). | READINGS → READINGS (claimed, not re-audited) |
| `u0123.s02.p1` ("Operators can legitimately instruct Claude to role-play … , and so on") | (1) "Legitimately" makes a pure ability reading incomplete. (2) The five permission rules were too broad: a role-play instruction stayed permitted even when it included conduct `u0123.s03` prohibits. | (1) The reading set has three candidates: `permission` (the word of permission carries "legitimately"), `conditional-permission` (legitimacy is a separate condition, open term `instruction_is_legitimate`), `ability` (the ability and the evaluative "legitimately", same open term). Candidates carry no content (a candidate norm cannot), the permission is elaborated in `readings/all-strict.ve.md`. (2) Each of the five rules has the six limits of `u0123.s03` as exceptions. | READINGS → READINGS (claimed, not re-audited) |
| `u0166.s04.p4` ("cannot be unlocked by any operator or user.") | The permission candidate adds a duty on operators and users not to unlock; the source states no such duty. | The permission reading and its two rules are removed, together with the regulated predicates `operator_unlock_permitted` and `user_unlock_permitted`. The clause is one checked English statement (a fence) with no norm: for every operator and every hard constraint, the operator is not able to unlock it, and the same for users (relations `operator_unlocks`, `user_unlocks`, each an open term: what counts as unlocking, what counts as being able to). "Cannot" is carried by the predicate (an ability), so VE sees no modality. The two phrasings "nobody has the ability" and "no instruction changes what Claude does" are one formula here and are not told apart. | READINGS → OPEN (one reading; claimed, not re-audited) |
| `u0123.s01.p1` (not sampled) | Same permission shape as the two above, and `u0123.s03` is its adjacent limit. | Same six exceptions. | READINGS → READINGS |

**Two dependencies recorded, not hidden.** (a) The exceptions follow the narrow reading of `u0123.s03` (its scope reading set: "while role-playing as a custom AI persona"
qualifies the first item only or every item); under the wide reading each exception would also need that condition. (b) The six exception atoms are the same
open terms as the prohibitions' guards, so a decision about what counts as, say, "claim to be human when directly and sincerely asked" applies to permission and prohibition together.

**What VE says now** (`probes/unspecified-probe.json`, 28 points): 19 SETTLED, 9 UNDECIDED, 0 CONFLICT. A persona input that is also an instruction to claim to be human is SETTLED no;
a role-play instruction that also claims to be human is SETTLED no (last run: a checked CONFLICT); a specific set of instructions that also endangers health or safety is SETTLED no;
an input that is none of the permitted kinds is UNDECIDED (the text does not say). The whole-document conflict proof returns CONFLICT-FREE (last run UNKNOWN, search budget).
The conflict reported last run is **withdrawn as a finding**: it came from the reading the audit rejected, so no auditor accepted both readings.

## Status of every unit an audit rejected (no covered status without a repair)

| Unit | Rejected by | Status now | Repair |
|---|---|---|---|
| `u0062.s01`, `u0123.s02.p1`, `u0166.s04.p4` | 20261002T0620Z | READINGS, READINGS, OPEN | above; not re-audited |
| `u0165.s02`, `u0165.s04`, `u0165.s06` | 20261001T1800Z | OPEN (one strict reading, content) | repaired in run 20261002T0620Z; not re-audited |
| `u0165.s01`, `u0165.s03`, `u0165.s05`, `u0165.s07` | same shape (s03, s05, s06 rejected by earlier audits) | OPEN | same; not re-audited |
| `u0156.s03`, `u0125.s04.p2` | 20260929T1800Z / same defect class | READINGS | strict reading is a prohibition (permission predicate, `unspecified`); not re-audited |

## What audit-verified means this run

Verified = accepted by an audit of this lineage AND byte-identical to the audited form. This run: **830 substantive bytes (0.45%) + 328 label bytes**, identical to last run's
(asserted in `finish.py`). None of the three rejected units had been verified, so nothing is lost; the three repaired units and `u0123.s01.p1` (658 bytes) are claimed, not verified.
Total repaired but not verified: 1,583 bytes. The 17 units the last audit accepted cannot be added: the audit does not list them and the sampling by status stratum cannot be reproduced from its text.
