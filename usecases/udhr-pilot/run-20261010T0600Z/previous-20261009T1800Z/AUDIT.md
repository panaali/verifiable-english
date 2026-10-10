**Faithful: 20/20 sampled + 16/20 changed.**

Sample: Python `Random("20261009T1800Z").sample` over the ID-sorted CHECKED/LABELLED/OPEN/READINGS pool. Seven overlaps; 33 distinct units audited. Source hash and selected spans match. No model calls.

```text
VERDICTS:
u022a FAITHFUL
u022b FAITHFUL
u022c FAITHFUL
u024 FAITHFUL
u025 FAITHFUL
u026 FAITHFUL
u027 FAITHFUL
u029 FAITHFUL
u033b FAITHFUL
u034 FAITHFUL
u037 FAITHFUL
u044 FAITHFUL
u048 FAITHFUL
u049 UNFAITHFUL
u051 FAITHFUL
u056 FAITHFUL
u063 FAITHFUL
u066 FAITHFUL
u070 FAITHFUL
u073 UNFAITHFUL
u074 FAITHFUL
u077 FAITHFUL
u084a FAITHFUL
u084b FAITHFUL
u084d FAITHFUL
u087 FAITHFUL
u096 FAITHFUL
u105a FAITHFUL
u105b UNFAITHFUL
u105c UNFAITHFUL
u111 FAITHFUL
u112 FAITHFUL
u114 FAITHFUL
```

Unfaithful units:

- **u049:** CHECKED conceals unresolved “his country”: nationality versus residence. The same ambiguity receives explicit alternatives in u077; retaining the phrase inside one opaque predicate does not resolve it.
- **u073:** CHECKED leaves the scope of “peaceful” unresolved: assembly alone versus both assembly and association. No scope alternatives are represented.
- **u105b, u105c:** Both explicitly extend “freely” to enjoying the arts and sharing scientific advancement. The source also supports attachment solely to “participate.” Keeping only the broader attachment leaves readings incomplete and CHECKED unjustified.

Three highest-value language features:

1. **Compositional phrase grammar:** explicit coordination, modifier scope, anaphora and ellipsis; addresses these failures and 11 grammar-blocked units.
2. **Integrated rights and norms:** combine entitlement structure, reading alternatives and unspecified completion without inventing bearers or duties.
3. **Temporal and comparative expressions:** represent birth, offence-time law, penalty comparisons and periodic events; five units currently carry time blockers.

`AUDIT.md` was not written because the requested directory is outside the permitted writable roots.