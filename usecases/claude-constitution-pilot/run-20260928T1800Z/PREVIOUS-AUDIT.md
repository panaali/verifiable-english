**Faithful: 20/20 sampled units. Unfaithful units: none identified.** This measures fidelity of the sampled spans and their labels, not completeness of the constitution’s translation.

Sampling: Python `random.Random("20260927T1800Z").sample(pool, 20)`, without replacement, retaining `units.json` order. The eligible pool contained 1 CHECKED and 39 LABELLED units; OPEN and READINGS were empty.

Per-unit findings, grouped by result:

- **CHECKED — u0248:** “Claude is not human” faithfully represents “Claude is not a human” in context. Negation and referent are preserved; support is correctly recorded as an assumption.
- **LABELLED, complete headings — u0023, u0103, u0277, u0282, u0294:** These function as topic or section headings. Their metadata classification introduces no stronger proposition; I found no substantive reading requiring separate formalisation within these spans.
- **LABELLED, heading markers — u0013.heading, u0027.heading, u0040.heading, u0042.heading, u0075.heading, u0095.heading, u0162.heading, u0174.heading, u0195.heading, u0212.heading, u0219.heading, u0245.heading, u0257.heading, u0286.heading:** Each sampled span contains only Markdown heading syntax. Labels are appropriate. Adjacent substantive titles remain explicitly UNFORMALISED.

Source bytes and ledger spans matched. No strengthening, weakening, or missing reading was identified within the sample. However, **19/20 sampled units are metadata**, and 1,084 units remain UNFORMALISED. The run’s 100% byte accounting is not semantic coverage; its checked assertion covers only 22 bytes.

The three highest-value additions for language work are:

1. **Soft normative force, priorities, and exceptions:** Preserve “should,” “generally,” holistic priority, hard constraints, and who may alter defaults.
2. **Scoped attitudes and epistemic modality:** Represent “we want,” “we believe,” “may,” and uncertainty without promoting embedded content into asserted fact; preserve alternative readings.
3. **Graded comparisons and vague quantification:** Express “most important,” stronger/weaker duties, and context-dependent degrees without inventing numerical thresholds.

No model calls or file changes were made. `AUDIT.md` was not written because the requested directory is outside the writable sandbox.