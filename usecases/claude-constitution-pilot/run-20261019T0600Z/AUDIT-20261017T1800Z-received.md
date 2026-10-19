I couldn't write AUDIT.md because the Write tool was denied, so the audit is below. Nothing was changed and there is nothing to commit.

# Fidelity audit, run 20261017T1800Z (xhigh)

**Faithful: 20/20 sampled plus 8/8 changed.** The changed units are the 4 `changed_units` (u0036.s05, u0156.s03, u0165.s06, u0263.s04.p2) and the AT-0p `plan_repairs` that were not sampled (u0165.s02, s03, s05, s07; s01 and s04 were sampled).
- **Sample:** `sorted(random.Random("20261017T1800Z").sample(pool, 20))` over the 58 CHECKED, LABELLED, OPEN and READINGS units in ledger order. It drew 14 LABELLED, 5 OPEN and 1 CHECKED unit.
- No audited unit is `claimed: false` (the ledger has none).

```text
VERDICTS:
u0001 FAITHFUL
u0013.heading FAITHFUL
u0036.s05 FAITHFUL
u0042.heading FAITHFUL
u0052.s01 FAITHFUL
u0062.s01 FAITHFUL
u0108 FAITHFUL
u0151.heading FAITHFUL
u0156.s03 FAITHFUL
u0165.s01 FAITHFUL
u0165.s02 FAITHFUL
u0165.s03 FAITHFUL
u0165.s04 FAITHFUL
u0165.s05 FAITHFUL
u0165.s06 FAITHFUL
u0165.s07 FAITHFUL
u0174.heading FAITHFUL
u0207.heading FAITHFUL
u0212.heading FAITHFUL
u0238.heading FAITHFUL
u0245.heading FAITHFUL
u0248 FAITHFUL
u0254.heading FAITHFUL
u0257.heading FAITHFUL
u0260.heading FAITHFUL
u0263.s04.p2 FAITHFUL
u0282 FAITHFUL
u0294 FAITHFUL
```

**Unfaithful: none.**

**Checks:**
- **Labels:** all 11 `heading_label` values equal their source lines. The 4 whole headings make no claim.
- **u0156.s03 (last audit's UNFAITHFUL):** it now has four candidates: strict or default, each for every case or in the frame. The in-frame pair is guarded by `asked_to_keep_system_prompt_confidential`, and that term's record ties it to u0156.s01. The frame probe gives SETTLED no in the frame and UNDECIDED outside it. The reading set is now complete, with nothing invented.
- **u0165.s06:** the new factor from u0186.s01 is raised by the text itself; the next sentence reads "In most other cases, though, Claude will need to use judgment". The guard is unchanged.
- **"should" notes:** the 32 choices (2×4×2×2) are counted correctly. The other three sets changed only in their meaning hashes.
- **AT3:** all seven guards have the form `(C(s) and knowingly_engages_N(c,s)) or thinks_quite_likely_N(c,s)`, where c (var 1) is the regulated `claude_instance`.
  - The guard binds the acting instance and keeps both alternatives of u0173.s01; the belief alone is enough.
  - u0165.s03 has its own attitude pair for each candidate (wide and narrow).
- **AT4:** every open-term record and predicate description I read matches the words.

**Small fault, no verdict change:** u0156.s03's frame term takes only the instance. The words describe "a situation", and the rule ranges over (instance, user). So an instance classified as asked is in the frame toward every user.

**Most valuable missing features:**
1. **Cross-sentence scope as a construct, with situation frames:** u0156.s03's frame would no longer be hand-made, and could take a situation. This covers 150 governors, 352 units and 55,294 bytes.
2. **Native "should" through `ve document check`** (still `UnsupportedProfile`): this would drop the invented `exception_to_*` terms. "norms" blocks 669 units.
3. **Typed attitudes** (know, intend and think "quite likely", on an agent and a formula): these would formalise u0173.s01 to s04 and replace the 16 hand-named attitude terms.
