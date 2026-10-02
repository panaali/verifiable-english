# Audit repair

Input: the audit of run `20261001T1800Z` (`AUDIT-20261001T1800Z-received.md`): **17 of 20 sampled units faithful, 3 unfaithful**
(`u0165.s02`, `u0165.s04`, `u0165.s06`), none incomplete. The sample is reproducible
(`random.Random("20261001T1800Z").sample(<the 55 covered units in ledger order>, 20)` gives exactly 15 LABELLED, `u0073.s05`
OPEN, and READINGS `u0165.s02`, `u0165.s04`, `u0165.s06`, `u0263.s04.p2`); the accepted ones are the 15 labels, `u0073.s05` and
`u0263.s04.p2`. One accepted label, `u0235.heading`, was not on any earlier accepted list and is added to the audit-verified set.

## What the audit found, and what was done

The three units are hard constraints. The source calls the hard constraints "absolute restrictions … lines that should never be
crossed regardless of context, instructions, or seemingly compelling arguments" (`u0166.s01`) that are "non-negotiable and cannot be
unlocked by any operator or user" (`u0166.s04`). The previous translation kept a defeasible candidate (a rule with an open exception) in
each reading set and recorded the narrowing to strict as "recorded only", so both readings stayed available: a weakening of the source.

**Repair (all seven hard constraints, `u0165.s01` to `u0165.s07`, because the four unsampled ones have the same shape).** The reading set
is gone. Each unit now carries one strict reading as content, chosen from the cited spans `u0166.s01` and `u0166.s04`
(not silently: the ledger entry's `force_resolution` names the cites and the dropped candidate). The defeasible candidate is not
admissible for these units: it would give the restriction an exception that those two sentences exclude. Under either reading of
`u0166.s04`'s own modal ("cannot be unlocked": not permitted, or no effect, see `u0166.s04.p4`) the hard constraints have no exception
an instruction can trigger, so the resolution does not depend on how that sentence is read. No narrowing remains that is recorded but
not binding (`metrics.json`, `reading_sets.narrowings`).

The same units also drop the earlier workaround. They are written as prohibitions again (a permission predicate with a negative rule,
scoped to instances of Claude) with the completion `unspecified` (`norm-defaults@0`), not as duties to avoid the act with completion
deny. Where the source's case holds VE reports "SETTLED no" (Claude may not); elsewhere "UNDECIDED" (the text does not say), see
`probes/unspecified-probe.json`. No party other than Claude is made permitted or forbidden by default.

## Status of every unit an audit rejected (no covered status without a repair)

| Unit | Rejected by | Status now | Repair |
|---|---|---|---|
| `u0165.s02`, `u0165.s04`, `u0165.s06` | 20261001T1800Z | OPEN (one strict reading, content) | above; not re-audited |
| `u0165.s01`, `u0165.s03`, `u0165.s05`, `u0165.s07` | none directly (same shape; `u0165.s03`, `u0165.s05`, `u0165.s06` rejected by earlier audits and repaired then) | OPEN | above; not re-audited |
| `u0156.s03` | 20260929T1800Z (repaired, accepted 20260930T1800Z) | READINGS | its strict reading is a prohibition again (permission predicate, completion `unspecified`); changed, so no longer counted as verified |
| `u0125.s04.p2` | same defect class | READINGS | the same change; not re-audited |

## What audit-verified means this run

Counted as audit-verified only if an audit accepted the unit **and** it is byte-identical in this run (same ledger entry apart from
volatile notes, same document unit, same reading-set admission text). Result: **830 substantive bytes** (`u0248`, `u0052.s01`,
`u0168.s01`, `u0263.s04.p2`, `u0036.s05`, `u0078.s01`) and **328 label bytes**; last run it was 1,714 and 325. The drop is not a loss of
translation: `u0165.s02` and `u0165.s04` were accepted by earlier audits and rejected by the latest, `u0165.s01` and `u0165.s03` were
rewritten, `u0156.s03` changed its strict elaboration, and `u0073.s05` moved from a content-bearing OPEN unit to a one-candidate
reading set (the main document no longer runs `soft-norms@0`; its rule is unchanged in `readings/all-default.ve.md`).
The five force units that stay verified (`u0052.s01`, `u0168.s01`, `u0263.s04.p2`, `u0036.s05`, `u0078.s01`) keep the same main-document
unit, reading set and English; only the completion of their strict elaboration changed (deny → unspecified), which the audits did not assess.

Minor items from earlier audits that stay open (not changed so that audited units stay audited): `u0078.s01` ("err on the side of" is a
leaning; the strict candidate is stronger than the source licenses); `u0126` stray tag on a heading (ledger only).
