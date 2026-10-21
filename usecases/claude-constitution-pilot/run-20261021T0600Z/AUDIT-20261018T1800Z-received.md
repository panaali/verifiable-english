I couldn't write AUDIT.md because the Write tool was denied, so the audit is below. Nothing changed in the repository, so there is nothing to commit.

# Fidelity audit, run 20261018T1800Z (xhigh)

**Faithful: 20/20 sampled plus 27/28 changed.**
- **Sample:** `sorted(random.Random("20261018T1800Z").sample(pool, 20))` over the 62 CHECKED, LABELLED, OPEN and READINGS units in ledger order. It drew 14 LABELLED, 5 OPEN and 1 CHECKED unit.
- **Changed:** the 25 `changed_units` plus AT-0p's u0165.s01–s07, less the 4 already sampled.
- No unit is `claimed: false`.

```text
VERDICTS:
u0001 FAITHFUL
u0023 FAITHFUL
u0042.heading FAITHFUL
u0062.s01 FAITHFUL
u0095.heading FAITHFUL
u0108 FAITHFUL
u0125.s04.p2 FAITHFUL
u0130.heading FAITHFUL
u0165.s01 FAITHFUL
u0165.s02 FAITHFUL
u0165.s06 FAITHFUL
u0165.s07 FAITHFUL
u0195.heading FAITHFUL
u0212.heading FAITHFUL
u0238.heading FAITHFUL
u0245.heading FAITHFUL
u0260.heading FAITHFUL
u0277 FAITHFUL
u0286.heading FAITHFUL
u0294 FAITHFUL
u0002.presupposition FAITHFUL
u0013.presupposition FAITHFUL
u0032.presupposition FAITHFUL
u0040.presupposition FAITHFUL
u0042.presupposition UNFAITHFUL
u0043.s02.p1 FAITHFUL
u0043.s02.p2 FAITHFUL
u0055.presupposition FAITHFUL
u0069.presupposition FAITHFUL
u0075.presupposition FAITHFUL
u0083.presupposition FAITHFUL
u0095.presupposition FAITHFUL
u0151.presupposition FAITHFUL
u0162.presupposition FAITHFUL
u0165.s03 FAITHFUL
u0165.s04 FAITHFUL
u0165.s05 FAITHFUL
u0174.presupposition FAITHFUL
u0195.presupposition FAITHFUL
u0207.presupposition FAITHFUL
u0212.presupposition FAITHFUL
u0235.presupposition FAITHFUL
u0245.presupposition FAITHFUL
u0254.presupposition FAITHFUL
u0257.presupposition FAITHFUL
u0260.presupposition FAITHFUL
u0268.presupposition FAITHFUL
u0286.presupposition FAITHFUL
```

**Unfaithful:**
- **u0042.presupposition:** the content is exact: three pairwise different types, each one of Claude's, with the closure over `claude_principal_type` only and none of the types named. Its English, though, is the quoted fallback (`Y1 is classified as "claude_principal_type"`), which PS-0p rejects. It reverts to UNFORMALISED, and its 38 B are not claimed.

**Checks:**
- **QT-0p:**
  - u0043.s02.p2 closes over Claude's types only.
  - "At the moment," is LABELLED and carries no date.
  - p2's English has the same fallback. PS-0p's rule covers headings only, so the DRI decides whether it applies here.
- **PS-0p:**
  - **Accepted:** u0245. "as" is in the title, and "Claude is novel." says exactly that Claude is a novel entity. The source never withholds this; u0246.s03 affirms it.
  - **No claim, correctly:** u0286 and u0032 were reverted, u0069 and u0083 were not offered, and u0013, u0095, u0002 and u0235 make no claim.
  - **Notes:** the class-E claims are gone, u0254 and u0268 cite u0269.s02, and u0055's note is right.
- **AT3:** all seven guards are `(case(s) and knowingly_engages_N(c,s)) or thinks_quite_likely_N(c,s)`. c is the acting instance, both u0173.s01 alternatives are kept, and s03 has one pair per candidate. Nothing changed.
- **JT-0p:** no hits.
- **AT4:** the records match the words.

**Small faults, no verdict change:**
- u0277 and u0294 have no tag for their definite triggers ("The", "the word").
- Two unclaimed `presupposed_claim` fields exceed their `pre`: u0235's "…a nature to discuss" and u0032's "…has criteria".

**Most valuable missing features:**
1. **Admitted VE English for classifying and relational nouns** ("is one of Claude's types of principals", "core value of", "deployment context"). It removes the fallback from u0042, u0043 and the hard constraints, and it unblocks 6 heading items.
2. **Native "should" through `ve document check`:** it blocks 669 norms units.
3. **Cross-sentence scope with situation frames:** it covers 352 units and 55,294 B.
