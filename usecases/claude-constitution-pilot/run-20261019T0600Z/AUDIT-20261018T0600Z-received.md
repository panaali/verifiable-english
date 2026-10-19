I couldn't write AUDIT.md: the Write tool was denied, so the audit is below. Nothing changed in the repository, so there is nothing to commit.

# Fidelity audit, run 20261018T0600Z (xhigh)

**Faithful: 20/20 sampled plus 5/5 changed.** `changed_units` is empty. The 5 changed units are the AT-0p `plan_repairs` the sample didn't draw (u0165.s01, s02, s03, s05, s07); s04 and s06 were drawn.
- **Sample:** `sorted(random.Random("20261018T0600Z").sample(pool, 20))` over the 58 CHECKED, LABELLED, OPEN and READINGS units in ledger order. It drew 13 LABELLED, 5 OPEN, 1 READINGS and 1 CHECKED unit.
- No unit is `claimed: false`.

```text
VERDICTS:
u0013.heading FAITHFUL
u0023 FAITHFUL
u0042.heading FAITHFUL
u0062.s01 FAITHFUL
u0069.heading FAITHFUL
u0083.heading FAITHFUL
u0108 FAITHFUL
u0123.s03 FAITHFUL
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
u0168.s01 FAITHFUL
u0207.heading FAITHFUL
u0248 FAITHFUL
u0265 FAITHFUL
u0277 FAITHFUL
u0286.heading FAITHFUL
```

**Unfaithful: none.**

**Checks:**
- **Labels:** all 8 `heading_label` values equal their source lines, and the 5 whole headings equal the source bytes. No heading makes a claim.
- **u0248:** `not human(claude)` matches the source exactly.
- **u0062.s01 and u0123.s03:** the six items split at the commas, and "while role-playing" attaches only to the first. Every factor is a phrase from the source.
- **u0156.s03:** it has four candidates: strict or default, each for every case or within u0156.s01's frame. The default candidate cites u0109.s05–s06, and no reading is invented.
- **AT3:**
  - All seven rules have the guard `(C(s) and knowingly_engages_N(c,s)) or thinks_quite_likely_N(c,s)`; u0165.s03 has a pair of terms per candidate.
  - c is var 1, the regulated `claude_instance`, so the guard binds the acting instance.
  - It keeps both alternatives of u0173.s01: the belief alone is enough, without C.
  - The strict force is cited from u0166.s01 and u0166.s04.p4. s06's factor from u0186.s01 is raised by the text.
- **AT4:** every open-term record and predicate description I read matches the words.

**Small faults, no verdict change:**
- **u0156.s03 (carried):** the frame term takes only the instance, while the words say "a situation".
- **u0168.s01 (new; last audited before AT-0p):** the guard `seemingly_compelling_argument_to_cross_line(s)` takes only the situation. So when one instance faces the argument, every instance in s is obliged to remain firm. In English that extra duty is empty, but it is the binding pattern AT-0p removed from the hard constraints.

**Most valuable missing features:**
1. **Cross-sentence scope with situation frames:** this covers 352 units and 55,294 bytes. It would replace the exceptions copied by hand from u0123.s03 into u0062.s01, and let u0156.s03's frame take a situation.
2. **Native "should" through `ve document check`** (still `UnsupportedProfile`): its absence blocks 669 `norms` units. It would drop the `exception_to_*` terms.
3. **Typed attitudes bound to an agent** (know, intend, think "quite likely", be faced with): these would formalise u0173.s01–s04, replace the 16 hand-named attitude terms, and bind u0168.s01's agent.
