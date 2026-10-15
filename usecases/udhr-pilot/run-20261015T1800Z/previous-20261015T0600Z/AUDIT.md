## UDHR fidelity audit, run 20261015T0600Z

**Faithful: 20/20 sampled + 0/0 changed.** Both `changed_units` and `plan_repairs` in metrics.json are empty, so there were no changed units to re-check and u097 gets no separate verdict.

**Sampling:** Python's `random.Random("20261015T0600Z").sample()` over the 88 eligible units sorted by id gave 2 CHECKED, 11 LABELLED, 6 OPEN and 1 READINGS. For each unit I compared the source text with the formula, the predicate and sort descriptions, every open-term record (description, factors, decider) and the rendered reading.

```text
VERDICTS:
u002 FAITHFUL
u011 FAITHFUL
u022a FAITHFUL
u024 FAITHFUL
u025 FAITHFUL
u027 FAITHFUL
u036 FAITHFUL
u044 FAITHFUL
u045a FAITHFUL
u047 FAITHFUL
u053 FAITHFUL
u054 FAITHFUL
u056 FAITHFUL
u075 FAITHFUL
u080 FAITHFUL
u081 FAITHFUL
u083 FAITHFUL
u099b FAITHFUL
u106 FAITHFUL
u107 FAITHFUL
```

**Unfaithful units:** none.

**Notes:**
- **u025 (READINGS):** both readings come from the words "shall be prohibited":
  - a requirement, on no named party, that each practice be prohibited;
  - a refusal of permission for the practice itself.

  No bearer is invented, and "in all their forms" is kept by covering every practice.
- **u027:** the scope is right: "torture" stands alone, and "cruel, inhuman or degrading" applies only to "treatment or punishment". One minor point: "torture" has no open-term record, although "slavery" and "servitude" do. This doesn't change the meaning, but the record understates what is open.
- **u081:** "as a member of society" holds of every person and does not narrow who holds the right.
- **u099b and u106:** neither names a bearer. In u106 the "author of" condition takes its two arguments in the right order.
- **u011:** labelled as a context-dependent transition, which is right for "Now, therefore,".
- **Bytes:** all 20 units were already audit-verified and none is marked `claimed: false`, so this audit adds no verified bytes. The two units still waiting for an audit, u098 and u110 (160 B), were not drawn.

**Three highest-value missing features:**
1. **Act phrases built from parts:** who takes part, conditions, purposes and relative clauses inside an act. Eight units are blocked on this.
2. **References to the set of rights, with limits on their scope:** link "these rights", "this Declaration" and the Article 29/30 limits to the units they govern. 98 units carry the `other:scope` blocker, and 4 are blocked because a right reaches across open sets.
3. **Norms about time and comparison:** no retroactive offences, "heavier penalty than", and periodic elections and holidays (5 time units and 2 comparison units).

No model calls were made and nothing was changed. **AUDIT.md was not written:** writing to the run directory was denied in this session, so the audit is only printed here.
