**Faithful: 14/20.**

Sampling: Python `random.Random("20261007T1800Z")`, sampling ID-sorted strata sequentially: CHECKED 1, LABELLED 8, OPEN 0, READINGS 11. No OPEN units exist. Reviewed source, main VE, and 32 companions. This is a stratified sample result, not a corpus estimate.

```text
VERDICTS:
u002 FAITHFUL
u021 FAITHFUL
u023 FAITHFUL
u027 FAITHFUL
u033b FAITHFUL
u038 FAITHFUL
u044 FAITHFUL
u046 UNFAITHFUL
u059 FAITHFUL
u063 UNFAITHFUL
u074 FAITHFUL
u077 UNFAITHFUL
u095 FAITHFUL
u099a FAITHFUL
u099b FAITHFUL
u100b UNFAITHFUL
u104 FAITHFUL
u105c UNFAITHFUL
u107 FAITHFUL
u110 UNFAITHFUL
```

Unfaithful units:

- **u046:** “Entitlement” candidates encode that the law protects the person, rather than that the person has a right to protection. Entitlement can persist when protection fails.
- **u063, u105c:** Four duty candidates quantify over right objects without encoding a right for every person. An empty rights domain makes those duties vacuous; the universal entitlement survives only in the separate entitlement candidate. The sort description supplies an unchecked existence assumption.
- **u077:** Both candidates assign duties to countries. Missing: the entitlement reading that leaves responsibility unspecified. Nationality/residence alternatives do not resolve this omission.
- **u100b:** The `education` candidate replaces “shall be directed” with a plain statement that education is directed. The `unassigned` act also drops “fundamental” from “fundamental freedoms,” broadening its wording.
- **u110:** `identified_community` does not preserve the relative clause. Direct formula evaluation confirms it remains true when duties and an identified community exist but development is possible nowhere. The other candidates do not repair this alternative.

Three highest-value missing features:

1. Native rule content inside reading sets with unspecified defaults, enabling combined checking and substantive rendering.
2. Explicit right-holder relations and existence constraints, including support for relative clauses and presuppositions.
3. Compositional act phrases preserving modality, modifiers, and participants without moving essential content into unchecked descriptions; act-phrase grammar currently blocks 11 units.

No model calls or file changes. `AUDIT.md` was not written because its destination is outside this session’s writable roots.