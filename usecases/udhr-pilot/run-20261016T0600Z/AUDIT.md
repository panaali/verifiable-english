## UDHR fidelity audit, run 20261015T1800Z

**Faithful: 20/20 sampled + 0/0 changed.** `changed_units` and `plan_repairs` in metrics.json are both empty, so u097 gets no separate verdict.

**Sample:** `random.Random("20261015T1800Z").sample(…, 20)` over the 88 eligible units, sorted by id. It drew 3 CHECKED, 9 LABELLED, 6 OPEN and 2 READINGS units. For each one I compared the source span with the front-matter content, the predicate and sort descriptions, every open-term record (factors and decider) and the rendered reading.

```text
VERDICTS:
u018 FAITHFUL
u022a FAITHFUL
u023 FAITHFUL
u028 FAITHFUL
u030 FAITHFUL
u035 FAITHFUL
u045b FAITHFUL
u048 FAITHFUL
u049 FAITHFUL
u053 FAITHFUL
u062 FAITHFUL
u069 FAITHFUL
u077 FAITHFUL
u081 FAITHFUL
u085 FAITHFUL
u088 FAITHFUL
u099b FAITHFUL
u105b FAITHFUL
u110 FAITHFUL
u113 FAITHFUL
```

**Unfaithful units:** none.

**Notes:**
- **u110** (first audit since its 2026-10-09 repair):
  - "Has duties" stays a statement of fact; it is not turned into an obligation.
  - "In which alone … is possible" is read as: the development is possible in that community and in no other.
  - The community's existence is asserted, not left as an unsettled question.
  - The words support both readings: one community per person, or one community for everyone.
  - I checked both formulas and the situation that tells them apart by hand.

  All three earlier rejections are fixed. Only a wording gap remains: the rendering prints raw relation names.
- **u035:** faithful. Its "not claimed" mark (DRI X5) could be lifted: the predicate's description already says "granted to the person", just as u049's says "their own". Its 168 bytes stay uncounted while the mark stands.
- **u045b:** "arbitrary" applies only to "interference", so leaving "attacks" unqualified is right.
- **LABELLED (9):** all are article headings, recorded as comments, with exact spans.

**Bytes:** u110 (118 B, claimed) is newly audit-verified, which raises audit-verified bytes from 4,660 to 4,778 (43.77%). u098 (42 B) is still waiting for an audit.

**Three highest-value missing features:**
1. **Act phrases with internal structure.** "His country" (u049, u077), "granted him" (u035) and "as a member of society" (u081) exist only inside one predicate's wording, so nothing checks them. Eight more units are blocked on act-phrase grammar.
2. **References to the set of rights, with limits on their scope.** 98 units carry the `other:scope` blocker. u019, u108, u111, u112 and u114 govern every sampled right, but no checked link connects them. This is also why u111 is marked not claimed.
3. **Plain-English wording for predicates and relations.** Readings render as `classified as "has_the_right_to_life"` and `recorded relation "owes_duties_to"`, which is not zero-training English.

No model calls were made and nothing was changed. **AUDIT.md was not written:** this session isn't allowed to write files, so the audit is only printed here.
