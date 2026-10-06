**Faithful: 16/20**, including 8 metadata units.

Sampling: Python `Random("20261005T1800Z")`, ID-sorted pools, sequential draws: CHECKED=1, LABELLED=8, OPEN=0, READINGS=11. No OPEN units exist separately in `units.json`; READINGS maps to OPEN in the checker. Compared source, main document, and all 32 sampled reading companions.

VERDICTS:
```text
u011 FAITHFUL
u025 FAITHFUL
u026 FAITHFUL
u030 FAITHFUL
u033a FAITHFUL
u035 UNFAITHFUL
u045a FAITHFUL
u048 UNFAITHFUL
u050 FAITHFUL
u054 FAITHFUL
u055 FAITHFUL
u061 FAITHFUL
u063 UNFAITHFUL
u074 FAITHFUL
u075 FAITHFUL
u090 FAITHFUL
u095 FAITHFUL
u096 FAITHFUL
u098 UNFAITHFUL
u109 FAITHFUL
```

Unfaithful units:

- **u035:** The tribunal candidate obliges every competent national tribunal to remedy every qualifying violation. Competence is unary, with no tribunal–violation jurisdiction relation. A tribunal competent for one case consequently owes remedies for unrelated cases: strengthening.
- **u048:** Removing the combined candidate leaves the reading that requires both noninterference and protection unrepresented as a bundle of duties. Separate alternatives do not express their conjunction; the opaque entitlement predicate supplies no explicit replacement: incomplete readings.
- **u063:** `state_positive` requires securing actual ownership by everyone, individually and with others. A right to own property does not require everyone to become an owner: strengthening. The combined noninterference/protection reading was also removed.
- **u098:** `person_attends` unconditionally obliges every human to attend compulsory elementary education. Neither applicability nor prior completion restricts the rule. The open-term annotation does not restrict that universal quantifier; repairing the guardian relation leaves this strengthening intact.

Highest-value missing features:

1. **Compositional act phrases and bundled duties:** preserve qualifications and simultaneous obligations without the 80-byte workaround or deletion of readings.
2. **`norm-defaults@0` inside executable reading sets:** integrate actual candidate content, distinguishing situations, and verdicts across readings instead of unresolved main-document placeholders.
3. **Explicit event participants and temporal applicability:** represent jurisdiction, beneficiary, eligibility, and completion without hiding them in prose descriptions.

Read-only audit; no model calls. `AUDIT.md` was not written because the requested directory is outside the permitted write roots.