I couldn't write AUDIT.md because the Write tool was denied, so the audit is below. Nothing was changed and there is nothing to commit.

# Fidelity audit, run 20261017T0600Z (xhigh)

**Faithful: 20/20 sampled plus 4/5 changed.** The changed units are the 3 `changed_units` plus u0165.s01 and s05 (AT-0p `plan_repairs`; s02, s03, s04, s06 and s07 were sampled).
- **Sample:** `sorted(random.Random("20261017T0600Z").sample(pool, 20))` over the 58 CHECKED, LABELLED, OPEN and READINGS units in ledger order. It drew 14 LABELLED, 5 OPEN and 1 READINGS unit.
- No audited unit is `claimed: false`.

```text
VERDICTS:
u0002.heading FAITHFUL
u0013.heading FAITHFUL
u0027.heading FAITHFUL
u0036.s05 FAITHFUL
u0040.heading FAITHFUL
u0062.s01 FAITHFUL
u0069.heading FAITHFUL
u0083.heading FAITHFUL
u0095.heading FAITHFUL
u0130.heading FAITHFUL
u0151.heading FAITHFUL
u0156.s03 UNFAITHFUL
u0165.s01 FAITHFUL
u0165.s02 FAITHFUL
u0165.s03 FAITHFUL
u0165.s04 FAITHFUL
u0165.s05 FAITHFUL
u0165.s06 FAITHFUL
u0165.s07 FAITHFUL
u0195.heading FAITHFUL
u0235.heading FAITHFUL
u0245.heading FAITHFUL
u0257.heading FAITHFUL
u0263.s04.p2 FAITHFUL
u0294 FAITHFUL
```

**Unfaithful: u0156.s03 (readings incomplete).**
- The run's own scope tally (governor u0156.s01, reach "frontier") says the frame "Consider a situation where Claude is asked to keep its system prompt confidential" may reach s02 to s04. The ledger also lists u0156.s01 as `governed_by_candidate`.
- The words support that reading: s05 ("If Claude is not given any instructions about the confidentiality …") closes the case.
- Both candidates are unconditional (`guard: top`, for every user). Under the frame reading they therefore say more than the sentence does.
- No candidate is scoped to the frame, and no cited choice drops one. The `meaning` repair itself is correct. Earlier audits missed this.

**Checks:**
- **Labels:** all 14 spans and `heading_label` values match the source bytes.
- **AT-0p:** all seven guards are `(C(s) and knowingly_engages_N(c,s)) or thinks_quite_likely_N(c,s)`, where c (var 1) is the regulated `claude_instance` argument.
  - The guard binds the acting instance and keeps both alternatives of u0173.s01. The belief alone suffices.
  - u0165.s03 has a wide and a narrow candidate, each with its own attitude pair.
- **AT4:** every open-term record and description I read matches the words.
- **Repaired meanings:** all three now list the default candidate's exception term.

**Small faults, no verdict change:**
- u0165.s06 lists u0186.s01 ("especially severe and flagrant attempts") as a governor, but neither its note nor the `illegitimate_absolute_control` record mentions it.
- The notes of all three "should" units still say "8 compatible choices" for files that now record 16.

**Most valuable missing features:**
1. **Cross-sentence scope as a construct, including situation frames:** u0156.s03 could then carry its frame candidate, and the hand-copied lead-ins and limits could go. This covers 150 governors, 352 units and 55,294 bytes.
2. **Native "should" through `ve document check`** (still `UnsupportedProfile`): this would drop the invented `exception_to_*` terms. "norms" blocks 669 units.
3. **Typed attitudes** (know, intend and think "quite likely", on an agent and a formula): these would formalise u0173.s01 to s04 and replace the 16 hand-named attitude terms.
