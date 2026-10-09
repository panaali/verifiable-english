**Fidelity: 17/20 faithful.** I sampled 20 of the 55 eligible units in `units.json` order using `random.Random("20261001T1800Z")`: 15 LABELLED, one OPEN, and four READINGS. All 15 labels match their source headings. The OPEN unit and one READINGS unit preserve the source’s force and conditions.

**Unfaithful units**

- `u0165.s02` — The critical infrastructure restriction is absolute in the source, but its reading set still offers a defeasible rule with an open exception.
- `u0165.s04` — The oversight restriction has the same weakening.
- `u0165.s06` — The illegitimate control restriction has the same weakening.

Each ledger entry records a narrowing to the strict reading, but says that narrowing is **“recorded only”**; both readings remain available. I therefore counted the retained defeasible readings as fidelity failures.

**Highest-value language features**

1. Put actual rules in reading candidates and make source-supported narrowings binding.
2. Allow an **unspecified** outcome for regulated acts, so a translation need not invent a default.
3. Compose norms with attribution, causation, quantities, and discourse; norms are the largest recorded missing-feature category at 668 units.

The audit used the pinned local source and made no model calls. I could not write `AUDIT.md`: the requested pilot directory is outside this session’s writable roots.