Faithful: **19/20 sampled plus 3/3 changed**; supplemental PS checks: **5/6**.

Seed `20261020T0600Z`; Python `Random.sample` over ID-sorted eligible units, redrawing until all four statuses appeared (draw 2). Verdicts below list sample, changed, then supplemental units.

```text
VERDICTS:
u0013.heading FAITHFUL
u0023 FAITHFUL
u0027.heading FAITHFUL
u0036.s05 FAITHFUL
u0042.heading FAITHFUL
u0069.heading FAITHFUL
u0073.s05 FAITHFUL
u0083.heading FAITHFUL
u0095.heading FAITHFUL
u0123.s03 FAITHFUL
u0156.s03 UNFAITHFUL
u0162.heading FAITHFUL
u0174.heading FAITHFUL
u0235.heading FAITHFUL
u0248 FAITHFUL
u0257.heading FAITHFUL
u0263.s04.p2 FAITHFUL
u0286.heading FAITHFUL
u0286.presupposition FAITHFUL
u0298 FAITHFUL
u0002.presupposition FAITHFUL
u0095.presupposition FAITHFUL
u0235.presupposition FAITHFUL
u0013.presupposition UNFAITHFUL
u0032.presupposition FAITHFUL
u0042.presupposition FAITHFUL
u0069.presupposition FAITHFUL
u0083.presupposition FAITHFUL
u0245.presupposition FAITHFUL
```

Unfaithful units:

- **u0156.s03:** `asked_to_keep_system_prompt_confidential` lists “who asks Claude” as an unresolved factor. The source’s passive supplies no asker-dependent qualification. This introduces an unsettled question the text does not raise, violating the invented-questions rule—even though the four force/scope alternatives are supported.
- **u0013.presupposition:** remains CHECKED and claimed despite your explicit Class-A exclusion. Under this audit’s instructions, its 24 bytes cannot remain claimed or audit-verified.

Open-term records, vocabulary descriptions, and source context were inspected. No sampled CHECKED unit violates the judgment-term integrity rule. u0286 passes with the vocabulary’s explicit definition of “unsolved” as an unsolved problem. u0042 asserts exactly three distinct Claude principal types, closes over those types only, and names none. u0055’s note correctly identifies existence of a way to treat operators/users.

The three changed units remain UNFORMALISED; their corrected ownership/uniqueness notes pass, adding **zero verified bytes**. No sampled unit has `claimed:false`. `plan_repairs` is empty.

Highest-value missing features:

1. Compositional norms with attribution, graded force, and priorities.
2. Quantities, comparisons, and counting.
3. Discourse frames and presupposition projection.

Read-only; no model calls. Printed only: the requested `AUDIT.md` lies outside the sandbox’s writable roots.