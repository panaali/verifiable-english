**Faithful: 17/20 sampled + 0/0 changed.** Supplementary checks: 11/12. Sampling used Python `Random("20261020T1800Z").sample` over 64 eligible units sorted by ID; all four statuses were represented. Both change lists are empty.

VERDICTS:
```text
u0001 FAITHFUL
u0002.heading FAITHFUL
u0002.presupposition FAITHFUL
u0013.presupposition UNFAITHFUL
u0032.presupposition FAITHFUL
u0036.s05 UNFAITHFUL
u0040.heading FAITHFUL
u0042.presupposition FAITHFUL
u0043.s02.p1 FAITHFUL
u0043.s02.p2 FAITHFUL
u0055.presupposition FAITHFUL
u0069.heading FAITHFUL
u0069.presupposition FAITHFUL
u0075.heading FAITHFUL
u0083.presupposition FAITHFUL
u0095.presupposition FAITHFUL
u0125.s04.p2 FAITHFUL
u0143.heading FAITHFUL
u0156.s03 UNFAITHFUL
u0165.s06 FAITHFUL
u0168.s01 UNFAITHFUL
u0235.presupposition FAITHFUL
u0238.heading FAITHFUL
u0245.heading FAITHFUL
u0245.presupposition FAITHFUL
u0260.heading FAITHFUL
u0265 FAITHFUL
u0268.heading FAITHFUL
u0277 FAITHFUL
u0282 FAITHFUL
u0286.presupposition FAITHFUL
u0298 FAITHFUL
```

Unfaithful units:

- **u0036.s05:** The rendering converts silence under the defeasible reading into “c is not required to.” Its formal completion is unspecified: absence of an obligation verdict does not establish exemption.
- **u0156.s03:** The two contextual readings bind confidentiality only to the Claude instance, losing the situation and associated user. A request in one context consequently governs every user for that instance; these candidates misrepresent the contextual reading.
- **u0168.s01:** The guard depends only on the situation. One instance facing an argument therefore imposes firmness on every instance, strengthening the source’s condition.
- **u0013.presupposition:** The existence claim is intelligible, but claiming it violates this prompt’s explicit PS-0p exclusion. Earlier audit acceptance does not supersede that instruction.

Open-term records and vocabulary descriptions were inspected. No sampled CHECKED unit has a JT integrity hit. u0165.s06 binds the acting instance and preserves both epistemic alternatives. QT closure covers only Claude’s types; the heading names none; “At the moment” has no date. u0286 expresses unsolved-problem existence; u0245 preserves novelty. u0055’s corrected note is appropriate. Accepted UNFORMALISED entries remain unclaimed and contribute no verified bytes.

Three highest-value missing features:

1. Discourse frames binding situations, agents, users and inherited conditions.
2. Compositional defeasible norms and graded force, preserving UNDECIDED in English.
3. Quantities and comparisons, including likelihood thresholds.

Read-only; no model calls. Printed only: the requested `AUDIT.md` is outside the writable roots.