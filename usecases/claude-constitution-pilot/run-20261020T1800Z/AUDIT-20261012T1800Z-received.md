**Faithful: 17/20 sampled + 5/12 changed.** Four overlap; 28 unique units audited.

Sample: Python `Random("20261012T1800Z").sample(pool, 20)`, with the 58 CHECKED/LABELLED/OPEN/READINGS units sorted by ID. It contains 13 labels, six OPEN units, and one READINGS unit. No model calls.

```text
VERDICTS:
u0001 FAITHFUL
u0027.heading FAITHFUL
u0036.s05 FAITHFUL
u0042.heading FAITHFUL
u0052.s01 FAITHFUL
u0069.heading FAITHFUL
u0075.heading FAITHFUL
u0123.s01.p1 FAITHFUL
u0125.s04.p2 FAITHFUL
u0126 FAITHFUL
u0130.heading FAITHFUL
u0156.s03 FAITHFUL
u0165.s01 UNFAITHFUL
u0165.s02 UNFAITHFUL
u0165.s03 UNFAITHFUL
u0165.s04 UNFAITHFUL
u0165.s05 UNFAITHFUL
u0165.s06 UNFAITHFUL
u0165.s07 UNFAITHFUL
u0168.s01 FAITHFUL
u0173.s01 FAITHFUL
u0174.heading FAITHFUL
u0195.heading FAITHFUL
u0212.heading FAITHFUL
u0254.heading FAITHFUL
u0260.heading FAITHFUL
u0263.s04.p2 FAITHFUL
u0286.heading FAITHFUL
```

**Unfaithful:** u0165.s01–u0165.s07 all weaken applicability. Each repaired guard requires **actual restricted-category membership AND knowledge-or-likelihood**. But u0173.s01 also covers actions Claude *thinks quite likely* to fall into a restricted category; that belief need not be correct. The saved probes confirm all seven return UNDECIDED when the epistemic condition holds but actual category membership does not. Thus the repair loses prohibitions in mistaken-but-confident belief cases.

The denial repair faithfully removes the unsupported exception to “never.” The remaining “should” alternatives have textual support for strict versus defeasible force; their open factors introduce no unsupported substantive scenarios. Labels correctly distinguish heading markers from adjacent content. u0173.s01 is accepted **only as correctly UNFORMALISED**, not as translated coverage.

Three highest-value language features:

1. Typed knowledge, intention, and likelihood, binding each attitude to its actor, action, and restricted category.
2. Graded normative force and defeasibility, preserving source-supported exceptions without inventing permissions or exemptions.
3. Cross-sentence scope: attach later qualifications and list introductions to exactly the rules they govern.

AUDIT.md was not written: the requested directory is outside the permitted writable roots.