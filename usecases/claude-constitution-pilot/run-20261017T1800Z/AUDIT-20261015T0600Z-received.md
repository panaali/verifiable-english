I couldn't write `AUDIT.md` because the Write tool was denied, so the audit is below. No files were changed and there was nothing to commit.

# Fidelity audit, run 20261015T0600Z (xhigh, read-only, no model calls)

**Faithful: 20/20 sampled plus 9/9 changed.**
- **Sample:** `random.Random("20261015T0600Z").sample(pool, 20)` over the 58 CHECKED/LABELLED/OPEN/READINGS units, sorted by id. It drew 14 LABELLED, 3 OPEN, 2 READINGS and 1 CHECKED.
- **Changed:** the four `changed_units`, plus AT-0p u0165.s01, s02 and s04–s06 (s07 was in the sample).
- 29 units in all; none is `claimed: false`.

```text
VERDICTS:
u0001 FAITHFUL
u0002.heading FAITHFUL
u0023 FAITHFUL
u0032.heading FAITHFUL
u0052.s01 FAITHFUL
u0073.s05 FAITHFUL
u0083.heading FAITHFUL
u0108 FAITHFUL
u0123.s01.p1 FAITHFUL
u0126 FAITHFUL
u0151.heading FAITHFUL
u0156.s03 FAITHFUL
u0162.heading FAITHFUL
u0165.s01 FAITHFUL
u0165.s02 FAITHFUL
u0165.s03 FAITHFUL
u0165.s04 FAITHFUL
u0165.s05 FAITHFUL
u0165.s06 FAITHFUL
u0165.s07 FAITHFUL
u0173.s01 FAITHFUL
u0207.heading FAITHFUL
u0235.heading FAITHFUL
u0238.heading FAITHFUL
u0248 FAITHFUL
u0263.s04.p2 FAITHFUL
u0268.heading FAITHFUL
u0286.heading FAITHFUL
u0298 FAITHFUL
```

**Unfaithful:** none.

**u0165.s03 (repaired):** each reading now has its own "knowingly" and "thinks quite likely" terms, and each term's record names that reading's category. The probes confirm it:
- The narrow reading's own belief term alone gives SETTLED no; the other reading's terms give UNDECIDED.
- A cyberweapon that could not cause significant damage, created knowingly, gives UNDECIDED under the wide reading and SETTLED no under the narrow one.

Both readings come from the English words.

**AT-0p (s01–s07):** every guard is `(C(s) and knowingly_N(c,s)) or thinks_quite_likely_N(c,s)`, where c is the instance the rule regulates. So the guard binds the acting Claude instance and keeps both alternatives of u0173.s01. Outside them the result is UNDECIDED, which fits "centrally". u0173.s01 is correctly UNFORMALISED.

**Small faults, no verdict change:**
- **u0156.s03 and u0263.s04.p2:** the admission text says the readings have no content and the stored model is empty. Neither is true.
- **u0156.s03 ledger:** `defeasible_reading_predicate` names a predicate that is not in the document. `where_the_text_is_silent` says nothing is left unsaid, but the defeasible reading leaves excepted cases UNDECIDED.
- **u0263.s04.p2 ledger:** the case atom says "the situation has explicitly been instructed"; it should say Claude.
- **u0165.s01–s07 ledger:** these entries say `audit_verified: false` and "Not audited", but `metrics.json` counts s01, s02 and s04–s07 as audit-verified.

**Most valuable missing features:**
1. **Typed attitudes** (know, intend, think likely) whose content is a formula. A scope reading would then carry into the belief, so s03 would not need four terms, and "knowingly" would imply the category without an added case atom.
2. **Cross-sentence scope as a construct:** list lead-ins, u0173's qualification of the hard-constraint list, u0123.s03's limits on s01, and "For example" frames (u0072.s02 over u0073.s05). This covers 150 governors and 29.9% of the bytes.
3. **Graded quantities and nested-guard English:** quantities like "quite likely", "serious uplift" and "significant damage", plus an English round trip for nested guards. All seven hard-constraint rules are currently refused with `IdentityMetadataMismatch`.
