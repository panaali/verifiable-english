**Faithful: 16/20.** Audited current part documents against the pinned source; all sampled source spans match.

Reproducible sample: Python `Random("20261008T1800Z")`, sampling without replacement from ID-sorted strata in CHECKED/LABELLED/OPEN/READINGS order, with quotas 1/8/3/8.

```text
VERDICTS:
u011 FAITHFUL
u018 FAITHFUL
u020 UNFAITHFUL
u021 FAITHFUL
u022a FAITHFUL
u022b FAITHFUL
u024 FAITHFUL
u029 FAITHFUL
u035 FAITHFUL
u047 FAITHFUL
u048 FAITHFUL
u052 UNFAITHFUL
u055 UNFAITHFUL
u063 FAITHFUL
u073 FAITHFUL
u088 FAITHFUL
u098 UNFAITHFUL
u104 FAITHFUL
u107 FAITHFUL
u109 FAITHFUL
```

Reasons for rejection:

- **u020:** The `distinction` domain covers distinctions made “against” a person. This introduces an adverse-treatment restriction; the source prohibits status-based distinctions without that restriction.
- **u052:** Open-term factors introduce who classifies crimes, which UN purposes/principles “count,” and election authenticity. These add unsettled questions this sentence does not raise, triggering the invented-readings rule.
- **u055:** “Arbitrarily” acquires unsupported legality and procedural-safeguard factors. Additionally, the two modifier-scope readings regulate separate act predicates—“be applied” and “take place”—instead of preserving one act while varying scope.
- **u098:** “Elementary education shall be compulsory” becomes “Every person must receive elementary education.” The encoding supplies universal human recipient scope and a personal obligation absent from the impersonal source; CHECKED overstates fidelity.

Three highest-value language features:

1. **Compositional act grammar and impersonal norms:** address the 11 act-grammar blockers while preserving unstated bearers and recipient scope.
2. **Source-linked reading composition:** retain shared act identity across alternatives and constrain open-term factors to the relevant source wording.
3. **Temporal and event relations:** express “until,” historical applicability, and periodicity; five units explicitly remain blocked on time.

`AUDIT.md` was not written because its directory is outside the permitted write roots. No files changed; no external model calls made.