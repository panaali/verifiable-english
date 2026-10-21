I couldn't write AUDIT.md because the Write tool was denied, so the audit is below. Nothing was changed and there is nothing to commit.

# Fidelity audit, run 20261016T1800Z (xhigh)

**Faithful: 20/20 sampled plus 11/11 changed.** The 11 are the 7 `changed_units` (u0123.s02.p1 was also sampled) and u0165.s04 to s07.
- **Sample:** `sorted(random.Random("20261016T1800Z").sample(pool, 20))` over the 58 eligible units in ledger order, the method that reproduces the 0600Z sample. It drew 15 LABELLED, 4 OPEN and 1 READINGS unit.
- `translation.ve.md` is byte-identical to `prev/`; only ledger texts changed. No audited unit is `claimed: false`.

```text
VERDICTS:
u0001 FAITHFUL
u0023 FAITHFUL
u0027.heading FAITHFUL
u0036.s05 FAITHFUL
u0055.heading FAITHFUL
u0062.s01 FAITHFUL
u0073.s05 FAITHFUL
u0075.heading FAITHFUL
u0083.heading FAITHFUL
u0095.heading FAITHFUL
u0123.s01.p1 FAITHFUL
u0123.s02.p1 FAITHFUL
u0123.s03 FAITHFUL
u0126 FAITHFUL
u0143.heading FAITHFUL
u0151.heading FAITHFUL
u0156.s03 FAITHFUL
u0165.s01 FAITHFUL
u0165.s02 FAITHFUL
u0165.s03 FAITHFUL
u0165.s04 FAITHFUL
u0165.s05 FAITHFUL
u0165.s06 FAITHFUL
u0165.s07 FAITHFUL
u0238.heading FAITHFUL
u0257.heading FAITHFUL
u0263.s04.p2 FAITHFUL
u0268.heading FAITHFUL
u0282 FAITHFUL
u0298 FAITHFUL
```

**Unfaithful:** none.

**AT-0p:** every guard is `(C(s) and knowingly_engages_N(c,s)) or thinks_quite_likely_N(c,s)`, where c (var 1) is the regulated instance.
- The guard binds the acting Claude instance and keeps both alternatives of u0173.s01. The belief alone suffices and need not be correct.
- The probes give SETTLED no, SETTLED no, UNDECIDED and UNDECIDED.
- u0165.s03 has its own attitude pair per candidate.

**Changed units:** the repairs are correct. 26 case atoms now say "the operator input is …", and none are stale. The three "should" sets list their `exception_to_*` terms, and u0073.s05's history is true.

**Small faults, no verdict change:**
- The document's `units[].meaning` still leaves out each default candidate's exception term: u0036.s05 lists only genuine_ambiguity, and u0156.s03 and u0263.s04.p2 say "specified". `ve document check` accepts this.
- The `audit_repair` texts of u0165.s01, s02 and s04 to s07 omit the 20261014T1800Z acceptance that `plan_repairs` cites.

**Most valuable missing features:**
1. **Native "should" through `ve document check`:** the soft-chain probe answers (ALL in 16 of 16 choices), but `check` fails with `UnsupportedProfile`. Fixing it would drop the three invented `exception_to_*` terms. "norms" blocks 669 units.
2. **Typed attitudes** (know, intend and think "quite likely", on an agent and a formula): these would formalise u0173.s01 to s04 and replace the 16 hand-named attitude terms.
3. **Cross-sentence scope with an English round trip:** list lead-ins (u0164.s02), "For example" frames (u0072.s02 over u0073.s05), and u0123.s03's limits, copied by hand into three permissions. This covers 150 governors, 352 units and 55,294 bytes. All seven hard-constraint rules fail the round trip.
