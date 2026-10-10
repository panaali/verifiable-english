**Faithful: 14/20 sampled + 1/5 changed.** I used Python `Random("20261010T0600Z")` on ID-sorted status groups, drawing 1 CHECKED, 7 LABELLED, 8 OPEN, and all 4 READINGS. Three changed units overlap the sample; each ID appears once below.

VERDICTS:
```text
u0013.heading FAITHFUL
u0036.s05 FAITHFUL
u0062.s01 UNFAITHFUL
u0073.s05 FAITHFUL
u0103 FAITHFUL
u0123.s01.p1 UNFAITHFUL
u0123.s02.p1 UNFAITHFUL
u0123.s03 UNFAITHFUL
u0125.s04.p2 FAITHFUL
u0126 FAITHFUL
u0156.s03 FAITHFUL
u0165.s04 UNFAITHFUL
u0165.s05 UNFAITHFUL
u0165.s07 UNFAITHFUL
u0166.s04.p4 FAITHFUL
u0168.s01 FAITHFUL
u0212.heading FAITHFUL
u0235.heading FAITHFUL
u0238.heading FAITHFUL
u0248 FAITHFUL
u0263.s04.p2 FAITHFUL
u0298 FAITHFUL
```

**Unfaithful units:**

- **u0062.s01, u0123.s01.p1, u0123.s02.p1, u0123.s03:** The repaired rules remove the unsupported wide role-play reading, but their shared open term still asks whether the role-play phrase qualifies *every* item. That leaves the rejected scope available through the term’s unresolved factors. u0123.s02.p1 also lists an unsupported ambiguity about whether “decline” governs revealing information.
- **u0165.s04, u0165.s05, u0165.s07:** Their notes still refer to “two readings” of u0166.s04. The current ledger has no such reading set, and the repaired u0166.s04.p4 note treats the clause’s meaning as settled. The stale notes present an unsettled question the text does not raise.

**Three highest-value language features:**

1. Typed permission, capability, and authority, including who can authorize a norm change.
2. Defeasible obligations with context-bound exceptions and priorities.
3. Graded quantities and causal possibility, without invented thresholds.

No model calls were made. I could not write `AUDIT.md`: the requested directory is outside the writable roots.