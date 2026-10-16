I couldn't write `AUDIT.md` because the Write tool was denied, so the audit is below (about 400 words). Nothing was changed and there is nothing to commit.

# Fidelity audit, run 20261016T0600Z (xhigh, read-only, no model calls)

**Faithful: 20/20 sampled plus 8/8 changed.** The 8 are the 4 `changed_units` and the 4 AT-0p units the sample missed (u0165.s03, s04, s06, s07).
- **Sample:** `sorted(random.Random("20261016T0600Z").sample(pool, 20))` over the 58 CHECKED/LABELLED/OPEN/READINGS units in ledger order. With its own seed, the method reproduces the 1800Z sample. It drew 1 CHECKED, 13 LABELLED and 6 OPEN.
- **Against `prev/`:** only the six admission texts differ. Body, vocabulary, open terms and contents are identical.
- No audited unit is `claimed: false`.

```text
VERDICTS:
u0002.heading FAITHFUL
u0036.s05 FAITHFUL
u0055.heading FAITHFUL
u0062.s01 FAITHFUL
u0073.s05 FAITHFUL
u0075.heading FAITHFUL
u0103 FAITHFUL
u0108 FAITHFUL
u0123.s01.p1 FAITHFUL
u0123.s03 FAITHFUL
u0143.heading FAITHFUL
u0156.s03 FAITHFUL
u0162.heading FAITHFUL
u0165.s01 FAITHFUL
u0165.s02 FAITHFUL
u0165.s03 FAITHFUL
u0165.s04 FAITHFUL
u0165.s05 FAITHFUL
u0165.s06 FAITHFUL
u0165.s07 FAITHFUL
u0235.heading FAITHFUL
u0245.heading FAITHFUL
u0248 FAITHFUL
u0254.heading FAITHFUL
u0260.heading FAITHFUL
u0263.s04.p2 FAITHFUL
u0265 FAITHFUL
u0294 FAITHFUL
```

**Unfaithful:** none.

**AT-0p:** every guard is `(C(s) and knowingly_engages_N(c,s)) or thinks_quite_likely_N(c,s)`, with c (var 1) the regulated instance.
- The guard binds the acting Claude instance and keeps both alternatives of u0173.s01. The belief alone suffices and need not be correct.
- Outside the two alternatives the result is UNDECIDED, which fits "centrally" and u0173.s02.
- u0165.s03 has its own attitude pair per candidate.
- The term records list only the source's own vague words.

**Changed units:** the corrected admissions are true: both candidates carry content, and the separating situations are stored and checked by Lean. u0123.s03's case atoms now say "operator input".

**Small faults, no verdict change:**
- **Case atoms:** u0062.s01 (9), u0123.s01.p1 (7) and u0123.s02.p1 (10) still say "the situation is …" for terms on an operator input. The u0123.s03 repair didn't reach the units sharing these terms.
- **Audit-verified flags:** u0123.s03 keeps `audit_verified: true` though dropped as changed. u0073.s05's `audit_repair` still says "not audit-verified", though it was accepted four times and metrics counts it verified.
- **Open-term lists:** u0156.s03 and u0263.s04.p2 have `meaning` "specified" and an empty `open_terms`; u0036.s05 lists only genuine_ambiguity. All three omit their default candidate's `exception_to_*` term.

**Most valuable missing features:**
1. **Typed attitudes:** know, intend, think "quite likely" and want/hope, bound to an agent and taking a formula. This would formalise u0173.s01–s04, replace the 16 hand-named attitude terms and their case atoms, and reach about 122 "we want/hope" `norms` units (rough surface count).
2. **Native defeasible "should":** an exception nobody names, completion unspecified. About 143 `norms` units say "should", and the `exception_to_*` terms would go.
3. **Cross-sentence scope:** list lead-ins (u0164.s02), "For example" frames, u0123.s03's limits: 150 governors, 352 units, 29.9% of bytes. It also needs an English round trip for nested guards, which all seven rules fail.
