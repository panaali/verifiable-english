I couldn't write AUDIT.md because the Write tool was denied, so the audit is below. I changed no files, so there is nothing to commit.

# Fidelity audit, run 20261019T1800Z (xhigh)

**Faithful: 20/20 sampled plus 9/9 changed.** The PS-0p class-B items, which I also checked, are 2/2.
- **Sample:** `sorted(random.Random("20261019T1800Z").sample(pool, 20))` over the 64 CHECKED, LABELLED, OPEN and READINGS units, in ledger order.
- **Changed:** the 6 `changed_units` plus u0165.s01, s02 and s06 (the AT-0p units not already sampled).
- No unit is `claimed: false`. Compared with the previous run, only u0013 (added) and u0032 (removed) change in content.

```text
VERDICTS:
u0013.heading FAITHFUL
u0027.heading FAITHFUL
u0040.heading FAITHFUL
u0042.presupposition FAITHFUL
u0062.s01 FAITHFUL
u0095.heading FAITHFUL
u0103 FAITHFUL
u0123.s02.p1 FAITHFUL
u0123.s03 FAITHFUL
u0165.s03 FAITHFUL
u0165.s04 FAITHFUL
u0165.s05 FAITHFUL
u0165.s07 FAITHFUL
u0174.heading FAITHFUL
u0235.heading FAITHFUL
u0245.heading FAITHFUL
u0263.s04.p2 FAITHFUL
u0282 FAITHFUL
u0286.heading FAITHFUL
u0286.presupposition FAITHFUL
u0002.presupposition FAITHFUL
u0013.presupposition FAITHFUL
u0032.presupposition FAITHFUL
u0083.presupposition FAITHFUL
u0095.presupposition FAITHFUL
u0235.presupposition FAITHFUL
u0165.s01 FAITHFUL
u0165.s02 FAITHFUL
u0165.s06 FAITHFUL
u0069.presupposition FAITHFUL
u0245.presupposition FAITHFUL
```

**Unfaithful:** none.

**Checks:**
- **PS-0p:**
  - **u0286 and u0245:** accepted again.
  - **u0013:** "Some thing is a core value of claude." passes every test. "Claude's" is in the title, the content is existence only, and the source affirms "its core values".
  - **u0013 against the merged text:** that text still says u0013 "should not be claimed". The line predates ps-6r, and its reason (no admitted wording) no longer holds. I accept u0013. You should retire that line, or overrule me and drop its 24 B.
  - **Correctly unclaimed:** u0095, u0002 and u0235. u0069, u0083 and u0032 are correctly not offered, and u0055's note is right.
- **u0042 (overlap):** exactly three pairwise different types, closed over Claude's sort only, none named.
- **AT3:** all seven guards are `(C(s) and knowingly_engages_N(c,s)) or thinks_quite_likely_N(c,s)`. c is the regulated instance (var 1), both u0173.s01 alternatives are kept, and s03 has one pair per candidate.
- **JT-0p:** no hits.
- **AT4:** the records match the words.

**Faults to fix before claiming (no verdict change):**
- **u0235:** "Claude's nature" is a singular possessive. PS-0p, and u0042's own reading of a possessive, call for existence and uniqueness, as u0002 has. The record and fence give existence only.
- **u0002, u0095:** the fences' owner is `anthropic`, which is declared as "Anthropic, as a type of principal". The mission and the guidelines belong to the company.
- **u0013:** "of claude" is written in lower case.

**Most valuable missing features:**
1. **A premise check that holds several existential presuppositions,** using witnesses rather than a 10,000-model search. Today, which heading fits depends on the predicates' alphabetical order. It blocks u0095, u0002 and u0235 (92 B).
2. **Terms in their own words:** hard constraints still render as `is classified as "…"`, constants are lower case, and "deployment context" and "value" have no wording (u0069, u0083).
3. **Cross-sentence scope as a construct** (352 units): it would replace the u0123.s03 exceptions copied by hand into u0062.s01 and u0123.s02.p1.
