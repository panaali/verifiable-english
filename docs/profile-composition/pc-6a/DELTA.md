# User-visible deltas (pc-6a)

No answer changes: no decoder sets `SoftNode.splitFrom`, no lookup reads `decisionRule` yet, and no output prints a
`SoftNode` through `Repr` (`git grep -nE 'reprStr|repr ' -- 'lean/VE/*.lean'` finds only `VE/Time/Decimal.lean`). The
one row is the trust growth that R16 asks to itemise.

| # | Delta | Evidence and tests | Ruling |
|---|---|---|---|
| 1 | Trust growth, re-measured on the final tree with `uv run python tools/trust_map.py --check` against `8c28fe286`: K +0, S +5, untied V +0, unclassified +0, recorded as one allowance in `docs/trust-baseline.json` (S +5). Per file: `lean/VE/SoftNorms/Tree.lean` +5 (S: the `SoftNode.splitFrom` field and its doc comment +2, `decisionRule` and its doc comment +3; `decisionRule_unsplit` is P). `lean/VE/SoftNorms/TreeExamples.lean` is T only (`unsplitKeys`, `layeredDocs`, classified in `tools/trust-classes.json`). | `decisionRule` is exercised by F6.1b (`lean/VE/SoftNorms/TreeExamples.lean:26-28, :33`), by the split-direction `#guard` (`:36`) and by `decisionRule_unsplit`; the field's default by `lean/VE/Defaults/MeaningExamples.lean:116`. Seeded bugs: `docs/profile-composition/pc-6a/mutants.json` (3, all killed). Ties pass: FOLLOW-UPS.md "## pc-6a". | SIGNED by standing ruling R16 (DRI-RULINGS.md), pc-6a, 2026-10-18 |
