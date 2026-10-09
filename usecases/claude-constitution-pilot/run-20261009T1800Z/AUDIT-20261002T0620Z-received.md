## Fidelity audit: **17/20 faithful**

I sampled `units.json` in ledger order with `random.Random("20261002T0620Z")`, drawing 1 CHECKED, 6 LABELLED, 6 OPEN, and 7 READINGS units. I compared their VE records and companion readings with the pinned [constitution source](/home/seyran/code/manage-agents/pilots/claude-constitution/source/claude-constitution.md). No model calls were made.

**Unfaithful units**

- `u0062.s01` — Its permission candidate allows *every* operator input classified as specific instructions or a persona. That includes instructions the source later expressly says operators cannot give. The VE records the resulting conflict without a restriction or precedence rule.
- `u0123.s02.p1` — “Legitimately” makes a pure ability reading incomplete. Its permission rules are also too broad: an instruction to role-play remains permitted even when it includes conduct the next sentence prohibits.
- `u0166.s04.p4` — “Cannot be unlocked” describes hard constraints that an operator or user cannot change. The permission candidate adds a duty on operators and users not to unlock them; the source does not state that duty.

**Highest-value language work**

1. Let norm reading candidates carry checkable rules, with source-supported choices binding in the main document.
2. Combine `unspecified` outcomes with defeasible norms, so soft readings need no invented completion.
3. Add scoped norm composition and precedence for overlapping permissions and prohibitions, alongside causal and quantified guards. Norms are the ledger’s largest recorded blocker (669 units).

I could not write `AUDIT.md`: the requested run directory is outside this session’s writable roots.