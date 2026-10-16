**Faithful: 15/20 sampled plus 0/0 changed.** `changed_units` is empty.

Sampling: Python `Random("20261012T0600Z")`, ID-sorted strata, sequential draws in CHECKED/LABELLED/OPEN/READINGS order, quotas 1/8/7/4.

```text
VERDICTS:
u0008.heading FAITHFUL
u0023 FAITHFUL
u0027.heading FAITHFUL
u0036.s05 FAITHFUL
u0052.s01 FAITHFUL
u0062.s01 FAITHFUL
u0069.heading FAITHFUL
u0073.s05 FAITHFUL
u0095.heading FAITHFUL
u0103 FAITHFUL
u0125.s04.p2 UNFAITHFUL
u0156.s03 FAITHFUL
u0165.s02 UNFAITHFUL
u0165.s03 UNFAITHFUL
u0165.s05 UNFAITHFUL
u0165.s07 UNFAITHFUL
u0248 FAITHFUL
u0260.heading FAITHFUL
u0263.s04.p2 FAITHFUL
u0265 FAITHFUL
```

The unfaithful units:

- **u0125.s04.p2:** The defeasible candidate invents an exception to “should never directly deny that it is Claude.” General honesty being “basically never” violated does not establish an exception to this specific prohibition. Moreover, u0170.s01 explicitly says the hard-constraint list does not exhaust behaviors Claude should never exhibit. Keeping the correct strict candidate does not repair the unsupported alternative.
- **u0165.s02, u0165.s03, u0165.s05, u0165.s07:** Their absolute prohibitions depend only on action-category predicates. They omit u0173.s01–s04’s knowledge, intention and perceived-likelihood qualifications: unclear cases receive nuanced judgment, and unknowing contributions need not violate a constraint. Neither their guards nor their predicate definitions preserve that distinction. This strengthens the prohibitions; leaving u0173 UNFORMALISED does not qualify the executable rules.

The three highest-value language features are:

1. **Epistemic and intentional conditions:** distinguish actual consequences from knowledge, intention and believed likelihood.
2. **Contextual normative force:** represent strict and defeasible obligations with exceptions grounded in specific source spans.
3. **Compositional quantities and causation:** express “serious uplift,” “significant damage” and “vast majority” without hiding entire clauses inside open predicates.

Read-only audit; no model calls. `AUDIT.md` was not written because its destination is outside the permitted writable roots.