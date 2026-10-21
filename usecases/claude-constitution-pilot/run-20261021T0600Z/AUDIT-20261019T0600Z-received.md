I couldn't write AUDIT.md because the Write tool was denied, so the audit is below. Nothing changed in the repository, so there is nothing to commit.

# Fidelity audit, run 20261019T0600Z (xhigh)

**Faithful: 20/20 sampled plus 10/11 changed.**
- **Sample:** `sorted(random.Random("20261019T0600Z").sample(pool, 20))` over the 64 CHECKED, LABELLED, OPEN and READINGS units in ledger order.
- **Changed:** the 7 `changed_units` plus u0165.s01–s07, less the 3 already sampled (u0042.presupposition, u0043.s02.p2, u0165.s03).
- No unit is `claimed: false`.

```text
VERDICTS:
u0001 FAITHFUL
u0027.heading FAITHFUL
u0040.heading FAITHFUL
u0042.presupposition FAITHFUL
u0043.s02.p1 FAITHFUL
u0043.s02.p2 FAITHFUL
u0052.s01 FAITHFUL
u0062.s01 FAITHFUL
u0069.heading FAITHFUL
u0123.s02.p1 FAITHFUL
u0130.heading FAITHFUL
u0143.heading FAITHFUL
u0151.heading FAITHFUL
u0156.s03 FAITHFUL
u0165.s03 FAITHFUL
u0207.heading FAITHFUL
u0219.heading FAITHFUL
u0245.presupposition FAITHFUL
u0263.s04.p2 FAITHFUL
u0286.heading FAITHFUL
u0032.presupposition UNFAITHFUL
u0235.presupposition FAITHFUL
u0277 FAITHFUL
u0286.presupposition FAITHFUL
u0294 FAITHFUL
u0165.s01 FAITHFUL
u0165.s02 FAITHFUL
u0165.s04 FAITHFUL
u0165.s05 FAITHFUL
u0165.s06 FAITHFUL
u0165.s07 FAITHFUL
```

**Unfaithful:**
- **u0032.presupposition:** the formula and its open-term record are right. Its English, "Some thing is helpful.", drops "genuine" and "constitutes", so it is weaker than the heading and says something different. The ledger refuses the same kind of lossy wording for u0069 ("says something else"). Not accepted: it reverts to UNFORMALISED, and its 38 B are not claimed.

**Checks:**
- **PS-0p:**
  - u0286 is accepted: "unsolved" means exactly "open" for problems, and the source affirms them.
  - u0245 is accepted again.
  - u0069 and u0083 were correctly not offered. u0013, u0095, u0002 and u0235 make no claim.
  - u0055's note is right. The source withholds none of these presuppositions.
- **QT-0p:**
  - u0042 states exactly three pairwise different types. It is closed over a sort that holds only Claude's types and that no other unit uses, and it names no type.
  - u0043.s02.p2 matches.
  - "At the moment," is LABELLED and carries no date.
- **AT3:** all seven guards are `(C(s) and knowingly_engages_N(c,s)) or thinks_quite_likely_N(c,s)`. c (var 1) is the acting instance, both u0173.s01 alternatives are kept, and s03 has one pair per candidate.
- **JT-0p:** no hits.
- **AT4:** the records match the words.

**Small faults:**
- "principal type of Claude" can also be read as "main type of Claude".
- Two carried faults remain: u0156.s03's frame term and u0168.s01's guard.

**Most valuable missing features:**
1. **Admitted English for multiword and relational predicates** ("constitutes genuine helpfulness", "deployment context", "core value"). Open terms should also render in their own words, not as `is classified as "…"`, which fills 43 rendered lines and appears in every hard constraint. This would have saved u0032 and would unblock six headings.
2. **Native "should" through `ve document check`:** its absence blocks 669 norms units.
3. **Cross-sentence scope with situation frames:** it covers 352 units and 55,294 B. It would replace the exceptions copied by hand into u0062.s01 and u0156.s03's hand-made frame.
