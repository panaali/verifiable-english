# df-2: user-visible delta

Feature item df-2 (batch DF-2 of `docs/spec/defeasible-PLAN.md`, the meaning; spec `docs/spec/defeasible.md` 3.7, 7.3
and 8.2; acting DRI dri-featurefeed, 2026-10-18).

**What users see does not change. Bytes 0.** `lean/VE/Defaults/Meaning.lean` defines default bases and proves the
meaning theorem; `lean/VE/Defaults/MeaningExamples.lean` holds `#guard`s. No service mode, executable, response shape,
schema, relay, Python or Rust product file reads either: `tools/regen_generated.py --check` passes with only the Lean
inventories rewritten (`Audit.lean`, `axioms.txt`, `statements.txt`, `predicates.txt`, `declarations.txt`), and no
schema or checker pin changed. `lean/DEFAULTS.md` now states the minimal-exception reading under the gate and
`replacementSafe`, as the plan allows once DF-2 is proved (that text is documentation, not an answer). The one delta is
the trust budget.

| # | Delta | Ruling | Evidence |
| --- | --- | --- | --- |
| T1 | Trust budget: **S +35, V +5** (K +0), measured with `uv run python tools/trust_map.py --check` on the final tree against its merge base with main, f39c78dde: all in `VE/Defaults/Meaning.lean`. S: `withOpen`, `SwitchesOff`, `DefaultBase`, `leastDecisions`, `ReplacementHolds` (the meaning spec 7.3 states). Untied G[V]: `softX`. C (not counted): `replacementSafe`. The theorems are P and `MeaningExamples.lean`'s declarations are T. | SIGNED by standing ruling R16 (DRI-RULINGS.md): new Lean-owned behaviour, 40 lines, at most 150, none in K. Every new trusted definition is exercised by a test that can fail: `python3 docs/defeasible/df-1a/evidence/run_mutants.py docs/defeasible/df-2/mutants.json` runs 17 mutants, at least one per new definition (`withOpen` W1, W2; `SwitchesOff` S1; `DefaultBase` P2, D1, T1-T4; `softX` X1; `leastDecisions` L1, L2; `replacementSafe` R1; `ReplacementHolds` H1, T5, T6) and the plan's two seeded bugs (P1, P2); each fails inside the theorems it names (saved run `evidence/mutants.out`, control 0 failures). `tools/trust_mutants.py` (Mac): 20 killed by `MeaningExamples.lean`'s `#guard`s, 4 invalid, 45 allowed with one line each (`trust-mutants.json`, `trust-mutants-allow.json`, exit 0). The ties pass is asked for in `manage-agents/FOLLOW-UPS.md` ("## df-2"). The allowance is recorded with `tools/trust_map.py --allow` (S 35, V 5 in `docs/trust-baseline.json`, signed "SIGNED by standing ruling R16 (DRI-RULINGS.md), df-2, 2026-10-18") | `uv run python tools/trust_map.py --check` exit 0; `tools/regen_generated.py --check` |
