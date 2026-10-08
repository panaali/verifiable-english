**Faithful: 18/20.**

Sampling: Python `Random('20261004T0600Z').sample(..., 20)` over the 59 eligible units sorted by ID. Sample: 1 CHECKED, 13 LABELLED, 3 OPEN, 3 READINGS. READINGS verdicts assess recorded interpretations, including explicitly pending content. Excluded demonstration companions were not audited as translation.

```text
VERDICTS:
u0219.heading FAITHFUL
u0165.s07 FAITHFUL
u0123.s01.p1 UNFAITHFUL
u0257.heading FAITHFUL
u0001 FAITHFUL
u0002.heading FAITHFUL
u0126 FAITHFUL
u0260.heading FAITHFUL
u0108 FAITHFUL
u0042.heading FAITHFUL
u0263.s04.p2 FAITHFUL
u0062.s01 UNFAITHFUL
u0268.heading FAITHFUL
u0075.heading FAITHFUL
u0238.heading FAITHFUL
u0174.heading FAITHFUL
u0248 FAITHFUL
u0013.heading FAITHFUL
u0166.s04.p4 FAITHFUL
u0073.s05 FAITHFUL
```

Unfaithful units:

- **u0123.s01.p1:** “Operators are permitted to ask” explicitly grants permission. The additional ability candidate replaces permission with causal capability. The subsequent explanation about transparency does not license that alternative; retaining it creates spurious ambiguity.
- **u0062.s01:** The ability candidate describes what operators can “get Claude to do.” The source says operators can **give** instructions, a persona, or information. Supplying input does not entail inducing compliance. The ordinary input-supply ability reading is missing.

The sampled labels correctly cover headings or heading markers; adjacent substantive heading text remains separately UNFORMALISED. The repaired `u0073.s05` preserves conditional, defeasible compliance and leaves exceptional cases undecided.

Three highest-value missing features:

1. **Content-bearing readings with `norm-defaults@0` and `unspecified` completion:** represent strict/defeasible alternatives without inventing negative defaults.
2. **Typed modal expressions with explicit action complements:** distinguish permission, ability to supply instructions, and ability to induce behavior.
3. **Linked reading choices across sentences:** propagate alternative prohibition scopes into dependent permissions and check complete, coherent interpretations.

Read-only audit; no model calls. `AUDIT.md` was not written because its requested directory is outside the permitted write roots.