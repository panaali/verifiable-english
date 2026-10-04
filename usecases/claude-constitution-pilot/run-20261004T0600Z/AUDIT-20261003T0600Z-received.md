**Faithful: 14/20**, including seven LABELLED units. Audited source spans, main VE, and strict/default/S1 companions.

Sampling: Python `random.Random("20261003T0600Z")`; ID-sorted strata, sequential draws of CHECKED=1, LABELLED=7, OPEN=6, READINGS=6.

```text
VERDICTS:
u0248 FAITHFUL
u0013.heading FAITHFUL
u0162.heading FAITHFUL
u0108 FAITHFUL
u0032.heading FAITHFUL
u0282 FAITHFUL
u0294 FAITHFUL
u0219.heading FAITHFUL
u0165.s05 FAITHFUL
u0166.s04.p4 FAITHFUL
u0165.s02 FAITHFUL
u0165.s01 FAITHFUL
u0165.s06 FAITHFUL
u0165.s07 FAITHFUL
u0156.s03 UNFAITHFUL
u0036.s05 UNFAITHFUL
u0078.s01 UNFAITHFUL
u0123.s03 UNFAITHFUL
u0073.s05 UNFAITHFUL
u0263.s04.p2 UNFAITHFUL
```

Unfaithful units:

- **u0036.s05, u0073.s05, u0263.s04.p2:** Companion `deny` completions assert “not required” outside the stated conditions. The source leaves those cases unspecified. These are additional claims, even though the limitation is disclosed.
- **u0156.s03:** The defeasible companion converts an exception into “not required to avoid deception.” Defeating this rule does not establish that negative obligation claim; the source supplies no such completion.
- **u0078.s01:** “Should err on the side of following” expresses a preference. The strict candidate strengthens this to mandatory compliance; neither candidate preserves the leaning itself. Companion defaults also settle unstated cases negatively.
- **u0123.s03:** S1’s permission completion forbids otherwise unaddressed inputs. Its ability candidates deny operators’ ability to *supply instructions*, rather than their ability to get Claude to perform the prohibited behavior. Listing four readings does not make their contents faithful.

Accepted OPEN units preserve the absolute restrictions and explicitly retain unresolved meanings; sampled metadata labels are appropriate.

Three highest-value missing features:

1. Compose `readings@1`, defeasible norms, and `unspecified` completion, preserving silence throughout executable readings.
2. Represent preferences and graded normative force, especially “err on the side,” without replacing them with duties.
3. Link reading choices across sentences so scope, referents, and permission limits propagate consistently.

Read-only; no model calls. `AUDIT.md` was not written because the requested directory is outside the configured writable roots.