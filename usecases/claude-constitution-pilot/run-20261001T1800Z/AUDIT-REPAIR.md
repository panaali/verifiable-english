# Audit repair

Input: the audit of run `20260930T1800Z` (`AUDIT-20260930T1800Z-received.md`): **20 of 20 sampled units faithful, none
unfaithful, none incomplete.** So no unit has to be repaired, and no unit that an audit rejected keeps a covered
status without a repair: the four units rejected by the two earlier audits (`u0156.s03`, `u0165.s03` by 20260929T1800Z;
`u0165.s05`, `u0165.s06` by 20260930T0600Z) were repaired earlier and stay as repaired (`READINGS`, neutral act
pointers, no permission predicate).

## What changed in the counts

This run's translation document is byte-identical to the audited one (`metrics.json`,
`unchanged_from_previous_run.translation_document_byte_identical_to_20260930T1800Z`), and all 1,127 ledger entries are
identical. So everything that audit accepted still counts as audit-verified:

* newly audit-verified substantive units: `u0156.s03`, `u0078.s01`, `u0165.s02`, `u0165.s03` (READINGS), two of them
  (`u0156.s03`, `u0165.s03`) repairs of the 20260929T1800Z audit's rejections, now re-audited and accepted, and
  `u0165.s02`, which had the same defect;
* newly audit-verified labels: the heading markers `u0055.heading` and `u0238.heading`.

Still repaired and **not** re-audited (counted as claimed, not verified; 375 bytes): `u0165.s05`, `u0165.s06`,
`u0165.s07`, `u0125.s04.p2`.

## Minor items the audit listed (none counted as a defect; deliberately not changed)

Changing an audit-accepted unit would make it unaudited again and would blur what the language, not the translator,
changed. They stay open and are disclosed:

* `u0078.s01`: "err on the side of" is a leaning, so the strict candidate is stronger than the source licenses and no
  narrowing is recorded. The English export of this rule and of `u0073.s05` does not parse back (`comply-operator-prompt`,
  `follow-operator-in-conflict`).
* `u0165.s02`: the act pointer "giving attack uplift" carries content; harmless inside the guard, but the ledger's
  "abbreviates nothing" is too strong for this unit.
* `u0165.s02`, `u0165.s03`: the defeasible candidate contradicts `u0166.s04` ("cannot be unlocked"); the narrowing to
  strict is recorded only (the language cannot bind a narrowing to a candidate that carries no content).
* `u0126`: a stray `ethical_harm` tag on a heading with no content (ledger only).
