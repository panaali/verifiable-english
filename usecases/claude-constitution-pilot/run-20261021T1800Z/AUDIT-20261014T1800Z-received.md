I couldn't write `AUDIT.md`: the Write tool was denied for that directory, so the audit is below. No files were changed and there was nothing to commit.

**Faithful: 19/20 sampled plus 8/9 changed.** Four units are in both groups, so 25 units were audited.

Sampling: Python `random.Random("20261014T1800Z").sample(pool, 20)` over the 58 CHECKED/LABELLED/OPEN/READINGS units sorted by ID. That drew 1 CHECKED, 11 LABELLED, 6 OPEN and 2 READINGS units. Changed: all 9 units in `changed_units`, which include AT-0p u0165.s01–s07. No model calls.

```text
VERDICTS:
u0001 FAITHFUL
u0008.heading FAITHFUL
u0032.heading FAITHFUL
u0040.heading FAITHFUL
u0052.s01 FAITHFUL
u0055.heading FAITHFUL
u0062.s01 FAITHFUL
u0123.s01.p1 FAITHFUL
u0123.s02.p1 FAITHFUL
u0126 FAITHFUL
u0130.heading FAITHFUL
u0165.s01 FAITHFUL
u0165.s02 FAITHFUL
u0165.s03 UNFAITHFUL
u0165.s04 FAITHFUL
u0165.s05 FAITHFUL
u0165.s06 FAITHFUL
u0165.s07 FAITHFUL
u0173.s01 FAITHFUL
u0174.heading FAITHFUL
u0212.heading FAITHFUL
u0235.heading FAITHFUL
u0248 FAITHFUL
u0260.heading FAITHFUL
u0263.s04.p2 FAITHFUL
```

**AT-0p:** In all seven guards, both attitude terms take variable 1, which is the instance the rule regulates. So one instance's knowledge or belief no longer counts against another. Both alternatives of u0173.s01 are kept: the case plus knowing engagement, or the belief alone, which need not be correct. Outside these two cases the rule says nothing (UNDECIDED), which fits "centrally" and u0173.s02. u0173.s01 is accepted only as correctly UNFORMALISED.

**Unfaithful: u0165.s03.** The reading set splits the case atoms into wide and narrow, but not the attitude terms.
- `thinks_quite_likely_3` is the same belief alternative in both candidates.
- Its record, and the record of `knowingly_engages_3`, still describe the category with the unsplit phrase "cyberweapons or malicious code that could cause significant damage if deployed".
- So the narrow candidate never states that thinking it quite likely one is creating *any* cyberweapon triggers the ban. The two candidates differ only when the probe sets the knowing term true.

The readings are incomplete. Fix: give each candidate its own attitude terms.

**u0123.s02.p1 is accepted.** The binary term now ties "the operator's own products" to the operator who has the permission. The probe gives SETTLED yes for that operator and UNDECIDED for another.

Small faults, no verdict change:
- u0126's ledger entry still lists `ethical_harm`, which `repair.py` removed from the document.
- The record of `good_judgment` (u0052.s01) gives undeclared argument sorts.

Most valuable missing features:
1. **Typed attitudes** (know, intend, think likely) whose content is a formula. A scope reading would then carry into the belief automatically, and the case atom would no longer need to be added by hand (this is the s03 fault).
2. **Cross-sentence scope as a construct.** Examples: list lead-ins, u0173's qualification of the hard-constraint list, and u0123.s03's limits. This covers 150 governors and 29.9% of the bytes.
3. **Graded thresholds** ("quite likely", "serious uplift", "significant damage"), and an English round trip for nested guards.
