# Audit repair

Input: the audit of run `20260930T0600Z` (`AUDIT-20260930T0600Z-received.md`): 18 of 20 sampled units faithful, two
rejected, both for the same reason. Earlier repairs (from the `20260929T1800Z` audit, `u0156.s03`, `u0165.s03` and the
seven units with the same defect) are described in the `20260930T0600Z` run's `AUDIT-REPAIR.md` and are unchanged here.

## The two rejected units

### `u0165.s05` — "* Engage or assist in an attempt to kill or disempower the vast majority of humanity or the human species as whole" (bytes [101873, 101989))

**Finding (audit).** The required act was "avoid assisting an attempt on humanity". "Engage" survived only in the guard
atom, so where Claude itself engages, the stated duty did not cover it. The ledger note said the act phrase
"abbreviates nothing"; that was not true of the act phrase.

**Repair.** The act phrase is now the neutral pointer `{0} avoid the participation in {1}`. It names no act, so it
narrows nothing; the source's own words ("engaging or assisting in an attempt to kill or disempower the vast majority of
humanity or the human species as whole") stay in the case atom `attempt_to_kill_or_disempower_most_of_humanity`, which is
the open term (factors: what counts as the vast majority, disempowering, engaging or assisting). Status stays READINGS.

### `u0165.s06` — "* Engage or assist any individual or group with an attempt to seize unprecedented and illegitimate degrees of absolute societal, military, or economic control" (bytes [101989, 102149))

**Finding (audit).** Same defect ("avoid assisting an attempt to seize control"), and not disclosed in the ledger.

**Repair.** The act phrase is now the neutral pointer `{0} avoid the involvement in {1}`; the source's words stay in the
case atom `illegitimate_absolute_control`. Status stays READINGS. The ledger entry now carries an `audit_repair` note
for both units.

## What is counted as verified

* Not re-audited, so **not** counted as audit-verified: `u0165.s05`, `u0165.s06` and the five other units repaired
  earlier and not yet re-audited (`u0165.s02`, `u0165.s03`, `u0165.s07`, `u0156.s03`, `u0125.s04.p2`): 703 bytes
  (`metrics.json`, `audit_rejected_units_and_repair_status`).
* Newly audit-verified by the `20260930T0600Z` audit, because this run did not touch them (ledger entries identical):
  `u0036.s05`, `u0165.s01`, `u0165.s04` (READINGS); `u0265` and the heading markers of `u0027`, `u0130`, `u0207`, `u0260`
  (LABELLED).
* Only two ledger entries differ from the previous run (`u0165.s05`, `u0165.s06`), asserted in `finish.py`.

## Minor audit items, carried

* `u0165.s01` "giving weapons uplift" is broader than the source act; the audit called it harmless inside the guard. Left
  as audited (changing an audit-accepted unit would make it unaudited again).
* `u0073.s05`: the English export does not parse back (nested "all of the following" list); unchanged and disclosed.
* `u0126` keeps an `ethical_harm` tag on a heading recorded as having no content (ledger only); unchanged.
