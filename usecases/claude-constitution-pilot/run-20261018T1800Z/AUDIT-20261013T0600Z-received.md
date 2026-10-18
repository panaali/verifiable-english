Faithful: **14/20 sampled + 1/8 changed**.

Sampling: Python `Random("20261013T0600Z")`, ID-sorted strata, drawing CHECKED/LABELLED/OPEN/READINGS in order: 2/8/7/3. Changed-only units: u0165.s02, u0165.s06, u0173.s01; overlaps count in both totals.

```text
VERDICTS:
u0023 FAITHFUL
u0036.s05 FAITHFUL
u0042.heading FAITHFUL
u0055.heading FAITHFUL
u0108 FAITHFUL
u0123.s01.p1 FAITHFUL
u0123.s02.p1 UNFAITHFUL
u0125.s04.p2 FAITHFUL
u0156.s03 FAITHFUL
u0165.s01 UNFAITHFUL
u0165.s02 UNFAITHFUL
u0165.s03 UNFAITHFUL
u0165.s04 UNFAITHFUL
u0165.s05 UNFAITHFUL
u0165.s06 UNFAITHFUL
u0165.s07 UNFAITHFUL
u0173.s01 FAITHFUL
u0248 FAITHFUL
u0263.s04.p2 FAITHFUL
u0265 FAITHFUL
u0268.heading FAITHFUL
u0277 FAITHFUL
u0282 FAITHFUL
```

Unfaithful units and reasons:

- **u0165.s01–s07:** The repaired disjunction correctly preserves possibly mistaken belief. However, both guards take only `situation`; neither binds the regulated Claude instance. Thus `K(s) ∨ L(s)` prohibits **every** instance at that situation, transferring one instance’s knowledge/intention/belief to others. The source’s qualification concerns the acting Claude; it explicitly acknowledges multiple simultaneous instances. The encoding strengthens the restriction.
- **u0165.s03 additionally:** Whether “that could cause significant damage if deployed” modifies both alternatives or only “malicious code” appears merely as an open-term factor. The single recorded reading does not separately represent these supported scope alternatives.
- **u0123.s02.p1:** `instruction_promote_own_products(input)` omits the operator argument. Once an input qualifies, the permission applies to every operator, losing the source’s binding of “the operator’s own products.” This grants permission beyond the stated ownership condition.

u0173.s01 is accepted as correctly **UNFORMALISED**, not as translated coverage. The sampled headings and three “should” reading sets are faithful; those alternatives have source support.

Three highest-value language features:

1. Typed knowledge, intention and belief tied to the actor and contemplated action.
2. Compositional possessive/coreference binding and explicit modifier-scope readings.
3. Graded quantities and thresholds for “serious uplift,” “significant damage” and “quite likely.”

No model calls or file changes. AUDIT.md was not written because its destination is outside the permitted writable paths.