**Faithful: 17/20.** This was a read-only audit with no model calls. The source hash and all 20 sampled spans match. The score describes the sample, not the whole translation.

I included the sole CHECKED unit (u074) and OPEN unit (u111), then used Python `Random("20261002T0600Z")` to draw 14 sorted READINGS IDs (u110, u032, u022c, u017, u066, u029, u052, u049, u022b, u054, u051, u046, u112, u033a) and four sorted LABELLED IDs (u021, u040, u109, u056).

**Unfaithful units:**

- **u054, Article 15:** Both readings turn a *right to a nationality* into an accomplished fact: everyone already has one, or some state already grants one to everyone. The source does not say the right is fulfilled.
- **u051, Article 14:** The two noninterference readings apply only if a person `is_persecuted`. A person seeking asylum to escape threatened persecution can fall outside that guard, weakening the right to seek asylum *from* persecution.
- **u111, Article 29:** Its limitation has the source’s necessary conditions, but the assembled document reports zero limitation terms. Because the rights are reading-set candidates, the limitation currently constrains none of them.

**Highest-value missing language features:**

1. Rights that keep entitlement distinct from fulfilment and allow an unspecified duty bearer.
2. Per-choice rights elaboration, so Article 29 limitations attach to each candidate right.
3. Richer guarded relations for prospective harm and case-specific scope, so asylum protection need not depend on persecution already occurring.

I could not write `AUDIT.md` because the requested directory is outside the writable roots.