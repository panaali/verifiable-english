I couldn't write `AUDIT.md` because the Write tool was denied, so the audit is below (395 words). Nothing was changed and there is nothing to commit.

# Fidelity audit, run 20261015T1800Z (xhigh, read-only, no model calls)

**Faithful: 20/20 sampled plus 5/5 changed.**
- **Sample:** `sorted(random.Random("20261015T1800Z").sample(pool, 20))` over the 58 CHECKED/LABELLED/OPEN/READINGS units in ledger order. The same method reproduces the previous audit's sample. It drew 15 LABELLED, 2 OPEN, 2 READINGS and 1 CHECKED.
- **Changed:** `changed_units` is empty. The five are the AT-0p units not in the sample: u0165.s01 and s04–s07.
- No audited unit is `claimed: false`. The translation is byte-identical to the one audited last.

```text
VERDICTS:
u0008.heading FAITHFUL
u0023 FAITHFUL
u0027.heading FAITHFUL
u0040.heading FAITHFUL
u0042.heading FAITHFUL
u0055.heading FAITHFUL
u0075.heading FAITHFUL
u0095.heading FAITHFUL
u0123.s03 FAITHFUL
u0126 FAITHFUL
u0151.heading FAITHFUL
u0156.s03 FAITHFUL
u0165.s01 FAITHFUL
u0165.s02 FAITHFUL
u0165.s03 FAITHFUL
u0165.s04 FAITHFUL
u0165.s05 FAITHFUL
u0165.s06 FAITHFUL
u0165.s07 FAITHFUL
u0195.heading FAITHFUL
u0212.heading FAITHFUL
u0238.heading FAITHFUL
u0248 FAITHFUL
u0265 FAITHFUL
u0277 FAITHFUL
```

**Unfaithful:** none.

**AT-0p (s01–s07):** every guard is `(C(s) and knowingly_engages_N(c,s)) or thinks_quite_likely_N(c,s)`, where c (var 1) is the instance the rule regulates. So the guard binds the acting Claude instance and keeps both alternatives of u0173.s01.
- Outside the two alternatives the result is UNDECIDED, which fits "centrally".
- u0165.s03's wide and narrow candidates each have their own attitude terms, and both attachments come from the English words.
- The term records list only the source's own vague words as factors.
- For every rule the probes give SETTLED no, SETTLED no, UNDECIDED, UNDECIDED.

**Small faults, no verdict change:**
- **u0123.s03:** the ledger `case_atoms` say "the situation is an instruction…", but the terms take an `operator_input`.
- **u0165.s01–s07:** `audit_repair` still ends "Not audited." next to `audit_verified: true`. The notes call u0173.s01–s04 modality/belief, but the ledger tags them `norms`.
- **u0156.s03:** the previous audit's three ledger faults are unrepaired.
- **Headings:** "Being helpful" and "The existential frontier" are labelled whole, while "Being broadly safe" and "Safe behaviors" get presupposition units. This is inconsistent, but the labels are true.

**Most valuable missing features:**
1. **Typed attitudes with graded likelihood:** know, intend and think "quite likely", taking a formula and bound to an agent. This would formalise u0173.s01–s04 and replace the 16 attitude terms and the explicit case atoms.
2. **Cross-sentence scope:** u0164.s02 "Claude should never:" gives all seven rules their subject and force, yet it is UNFORMALISED. This covers 150 governors and 29.9% of the bytes.
3. **Defeasible "should" beside norm-defaults** (soft-norms@0 is refused): exceptions the text leaves unnamed would no longer need translator-named `exception_to_*` terms. `norms` blocks 669 units. Also needed: an English round trip for nested guards, which all seven rules currently fail.
