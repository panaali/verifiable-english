**Fidelity: 19/20 faithful.** I used `random.Random("20261002T1800Z")` to sample 1 CHECKED, 7 LABELLED, 6 OPEN, and 6 READINGS units. I compared the [ledger](/home/seyran/code/manage-agents/pilots/claude-constitution/run-20261002T1800Z/units.json), VE document and companion readings with the [pinned source](/home/seyran/code/manage-agents/pilots/claude-constitution/source/claude-constitution.md). No external model calls were made.

**Unfaithful unit**

- `u0168.s01` — VE retains a defeasible reading of “Claude should remain firm” when faced with arguments to cross the hard-constraint lines. Its open exception can make firmness *not required*. The source calls those lines absolute and says they should never be crossed **regardless of seemingly compelling arguments**, so this reading weakens the instruction.

The other sampled units preserve their source wording or explicitly mark unresolved terms and readings. Their fidelity does not mean every reading is executable in the main VE document.

**Highest-value language work**

1. Let reading candidates carry checkable rules, and make source-supported force choices binding.
2. Combine unspecified outcomes with defeasible norms without inventing a completion.
3. Express cross-sentence scope and force dependencies, including absolute constraints on later instructions and limits on operator permissions.

I could not write `AUDIT.md` because the requested run directory is outside the writable workspace.