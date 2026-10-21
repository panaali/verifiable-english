# ap-1e: user-visible delta

Feature item ap-1e (batch AP-1 of `docs/spec/act-phrases-PLAN.md`, spec `docs/spec/act-phrases.md` 1.1 and 4.3;
acting DRI dri-featurefeed, 2026-10-18).

**What users see does not change.** The item adds the specification `expand` and `Grouped`, theorems, `Decidable`
instances and `#guard` fixtures, all in `lean/VE/Acts/LexicalProofs.lean`, which no service mode, executable,
schema, relay, Python or Rust product file reads. No evaluated definition changes: `group`, `lex`, `rawLex`,
`decodeFixed` and `check` answer as at the merge base `343261104`. The one delta is the trust budget.

| # | Delta | Ruling | Evidence |
| --- | --- | --- | --- |
| T1 | Trust budget: **S +13** (K +0, D +0, G +0; tied +15; trusted **-2** net), measured with `uv run python tools/trust_map.py --check` on the final tree against its merge base with main, `343261104`. `VE/Acts/LexicalProofs.lean` +13: S `expand` and `Grouped`, the grouping of spec 1.1 (condition 6). `VE/Acts/Lexical.lean` -15: D[V] `group` now tied by `group_spec`, D[V] `lex` tied by `lex_spec` (the ties of FOLLOW-UPS "## ap-1a" and "## ap-1d"). P (not counted): `decFixed`, `decPlain`, `decSuffixes`, `decGrouped`; T: `seek`, `free`, `grouped`. | SIGNED by standing ruling R16 (DRI-RULINGS.md): new Lean-owned meaning, 13 lines, at most 150, none in K; each new trusted definition is exercised by tests that can fail: `expand` by the `#guard`s at `LexicalProofs.lean:1123-1125` (trust_mutants: 12 KILLED there; seeded bugs `expand-fixed`, `expand-plain`), `Grouped` by the `#guard`s at `:1126-1131` (one per condition failing alone) and the proofs of `group_spec` and `grouped_unique` (seeded bugs `Grouped-written`, `Grouped-range`, `Grouped-empty`, `Grouped-plain` in `mutants.json`). trust_mutants' 21 UNKNOWN of `Grouped` are listed with their cause in `mutants.json` (14 refuted by those `#guard`s through `decGrouped`, the ap-1d tool gap; 7 do not elaborate); its 9 allowed are equivalent or do not elaborate (`trust-mutants-allow.json`). The ties pass is asked for in `manage-agents/FOLLOW-UPS.md` ("## ap-1e"). Allowance recorded with `tools/trust_map.py --allow` (S 13 in `docs/trust-baseline.json`, "SIGNED by standing ruling R16 (DRI-RULINGS.md), ap-1e, 2026-10-18"). | `uv run python tools/trust_map.py --check` exit 0 |
