**Faithful: 15/20.**

Seed `20261009T0600Z`; Python `random.Random(seed)`, sampling sequentially from ID-sorted pools: CHECKED=1, LABELLED=7, OPEN=6, READINGS=6. Audited pinned source, VE content, labels, candidate readings, and open terms. No model calls.

```text
VERDICTS:
u0248 FAITHFUL
u0219.heading FAITHFUL
u0238.heading FAITHFUL
u0069.heading FAITHFUL
u0286.heading FAITHFUL
u0032.heading FAITHFUL
u0277 FAITHFUL
u0001 FAITHFUL
u0165.s05 FAITHFUL
u0166.s04.p4 UNFAITHFUL
u0165.s03 UNFAITHFUL
u0052.s01 FAITHFUL
u0168.s01 FAITHFUL
u0165.s02 FAITHFUL
u0123.s01.p1 UNFAITHFUL
u0125.s04.p2 FAITHFUL
u0156.s03 FAITHFUL
u0263.s04.p2 FAITHFUL
u0123.s03 UNFAITHFUL
u0062.s01 UNFAITHFUL
```

The unfaithful units fail for these reasons:

- **u0165.s03:** Adds the unsettled question “how likely deployment must be.” The source’s “could cause significant damage if deployed” concerns damage conditional on deployment; it introduces no deployment-probability threshold.
- **u0166.s04.p4:** Encodes non-overridability as factual inability to “make Claude treat [a constraint] as not binding.” This adds a capability guarantee to a normative restriction; the asserted-ability interpretation is unsupported.
- **u0123.s03, u0123.s01.p1, u0062.s01:** Their wide candidates use `instruction_given_while_role_playing_persona`, moving the role-play condition from the instructed behavior to instruction-issuance time. An instruction issued beforehand to abandon principles during later role-play can escape the prohibition. The corresponding permissions inherit this widening. A faithful narrow candidate does not rescue these sets.

The three highest-value missing language features are:

1. **Typed, event-scoped modalities:** Distinguish permission, practical ability, and authority to override; bind conditions to the intended action or instruction event.
2. **Native graded and defeasible norms:** Preserve “should,” “generally,” and exception scope without substituting arbitrary exception predicates; require source support for alternatives.
3. **Compositional conditional risk and quantities:** Express potential damage *if deployed*, likelihood, severity, and thresholds separately, reducing opaque case predicates and invented questions.

`AUDIT.md` was not written: the requested directory is outside the permitted writable roots.