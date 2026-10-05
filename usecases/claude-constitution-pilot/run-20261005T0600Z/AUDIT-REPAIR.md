# Audit repair

Input: the audit of run `20261004T1800Z` (`AUDIT-20261004T1800Z-received.md`): **18 of 20 sampled units faithful, 2 unfaithful** (sample: 1 CHECKED, 7 LABELLED, 6 OPEN, 6 READINGS; its VERDICTS block names all 20). Both rejections are repaired below, and the same defect is repaired in two units the audit did not sample.

| Unit | Finding | Repair | Status before → now |
|---|---|---|---|
| `u0123.s01.p1` | its one permission rule hardcodes the six limits of `u0123.s03` as exceptions, i.e. the *narrow prohibition* reading of that sentence; the sentence also reads wide (outside role-play five of the six would not apply) and as an inability (which forbids nothing), so the rule weakens the permission and loses admitted combinations | the unit is a reading set again, with no ability candidate ("permitted" is explicit, audit 20261004T0600Z) and three permission candidates, one per way the limits reach: `permission-narrow-limits` (the six kinds are exceptions; elaborated as a strict rule in `readings/all-strict.ve.md`), `permission-wide-limits` (the six kinds are exceptions only while Claude role-plays a custom persona), `permission-no-limits` (the inability reading forbids nothing). No candidate has content beside `norm-defaults@0`; no rule with hardcoded exceptions is claimed. The reason clause (`.p2`) stays UNFORMALISED (causation) | OPEN → READINGS |
| `u0123.s03` | the ability candidates replace "cannot instruct" with inability to *get Claude to perform* the behaviours; issuing an instruction and securing compliance are different acts and the passage does not say that inducing them is impossible | the two ability candidates (narrow, wide scope) now say an operator is unable to **give Claude an instruction** to do each of the six behaviours (issuing; nothing about compliance). No candidate is about inducing the behaviours. The prohibition candidates keep their meaning (their text now says "prohibition reading" rather than "permission reading", which is what they elaborate: a negative rule) | READINGS → READINGS (candidate texts changed) |
| `u0062.s01` (not sampled) | its permission candidate carried the same defect: "limited by the six kinds as exceptions" fixes the narrow reading of `u0123.s03` | the candidate says the permission is limited by whatever `u0123.s03` forbids under that sentence's own reading (narrow: the six kinds; wide: the six kinds only while role-playing; inability: no exception). Not multiplied into three candidates here: the three-way split is recorded once, in `u0123.s01.p1` (F14: choices do not propagate) | READINGS → READINGS (candidate text changed) |
| `u0123.s02.p1` (not sampled) | same as `u0062.s01` (permission and conditional-permission candidates) | same | READINGS → READINGS (candidate texts changed) |

The audit's three highest-value missing features, answered only where the language allows: (1) **strict/defeasible readings with content under the `unspecified` completion** — not possible at this tag (`probes/s1-probe.json`: still rejected, now by Lean's `InvalidInput` alone); (2) **typed modal action complements** (permission / ability to issue an instruction / ability to induce behaviour) — not possible: no modal form, so the three are told apart in candidate text only, which carries no content; (3) **linked reading choices across sentences** — not possible (F14), which is why `u0123.s01.p1` lists the three ways the limits reach instead of following `u0123.s03`'s choice.

## Status of every unit an audit rejected (no covered status without a repair)

| Unit | Rejected by | Status now | Repair |
|---|---|---|---|
| `u0123.s01.p1`, `u0123.s03` | 20261004T1800Z | READINGS, READINGS | above; not re-audited |
| `u0123.s01.p1`, `u0062.s01` | 20261004T0600Z | READINGS, READINGS | repaired 20261004T1800Z; `u0062.s01` repaired again now (candidate text); not re-audited |
| `u0036.s05`, `u0156.s03` | 20261003T0600Z | READINGS | **accepted by the 20261004T1800Z audit** (now audit-verified) |
| `u0123.s03` | 20261003T0600Z | READINGS | rejected again by 20261004T1800Z; repaired now |
| `u0078.s01` | 20261003T0600Z | UNFORMALISED | `other:graded-force`; not re-audited |
| `u0263.s04.p2`, `u0073.s05` | 20261003T0600Z | READINGS, OPEN | accepted by 20261004T0600Z and 20261004T1800Z |
| `u0168.s01` | 20261002T1800Z | OPEN | **accepted by the 20261004T1800Z audit** |
| `u0123.s02.p1`, `u0166.s04.p4` | 20261002T0620Z | READINGS, OPEN | `u0166.s04.p4` accepted; `u0123.s02.p1` repaired again now (same defect as the rejected units) |
| `u0165.s01`–`s07`, `u0125.s04.p2` | 20261001T1800Z and earlier | OPEN, READINGS | `u0165.s01`, `s02`, `s05`, `s06`, `s07` accepted; `u0165.s03`, `s04` not re-audited; `u0125.s04.p2` **accepted by the 20261004T1800Z audit** |

## What audit-verified means this run

Verified = accepted by an audit of this lineage AND byte-identical to the form that audit saw. This run: **1,419 substantive bytes (0.77%) + 341 label bytes**. Previous run 1,104 + 341. The 20261004T1800Z audit accepted `u0168.s01`, `u0125.s04.p2`, `u0036.s05`, `u0156.s03` (each byte-identical to the previous run's form, which it audited), and seven labels already verified. `finish.py` asserts: previous verified bytes plus the bytes of those four, label bytes unchanged. Claimed but not audit-verified: 1,236 bytes, of which 1,228 are units no audit has accepted: the four repaired now (`u0123.s01.p1`, `u0123.s03`, `u0062.s01`, `u0123.s02.p1`: 964 bytes) and `u0165.s03`, `u0165.s04` (264 bytes, repaired earlier, not re-audited); the other 8 are label bytes.
