# ap-1d: user-visible delta

Feature item ap-1d (batch AP-1 of `docs/spec/act-phrases-PLAN.md`, spec `docs/spec/act-phrases.md` 4.3; acting DRI
dri-featurefeed, 2026-10-18).

**What users see does not change.** The item adds theorems, their lemmas, the specification `Accepts` (spec 4.3,
verbatim), a `Decidable` instance for it and `#guard` fixtures, all in `lean/VE/Acts/LexicalProofs.lean`, which no
service mode, executable, schema, relay, Python or Rust product file reads. No definition that is evaluated changes:
`check`, `lex`, `decodeFixed` and every decoder answer as at the merge base `768a935fc`. `ve/assurance-manifest.json`
gains the file's `other_json` reason (`Accepts` names `getStr?`). The one delta is the trust budget.

| # | Delta | Ruling | Evidence |
| --- | --- | --- | --- |
| T1 | Trust budget: **S +9** (K +0, D +0, G +0; trusted **-23** net), measured with `uv run python tools/trust_map.py --check` on the final tree against its merge base with main, `768a935fc`. `VE/Acts/LexicalProofs.lean` +9: S `Accepts`, the independent statement of spec 1.3. `VE/Acts/Lexical.lean` -32: D[V] `check` now tied by `check_spec`, D[V] `decodeFixed` tied by `fixedOk_unique` (the ties of FOLLOW-UPS "## ap-1a"). P (not counted): `decOkAnd`, `decWord`, `decAccepts`; T: `acc`. | SIGNED by standing ruling R16 (DRI-RULINGS.md): new Lean-owned meaning, 9 lines, at most 150, none in K; the new trusted definition is exercised by tests that can fail: the `#guard` fixtures at `LexicalProofs.lean:770-778` (each condition of 1.3 failing alone, and the 400-byte limit both ways) and the proof of `check_spec` (seeded bug `Accepts-words` in `mutants.json`); `tools/trust_mutants.py` exits 0 with its 64 mutants allowed, each with a reason (`trust-mutants-allow.json`; the run without it, `trust-mutants-raw.json`, shows 54 refuted at those fixture lines, 7 that do not elaborate and 3 equivalent). The ties pass is asked for in `manage-agents/FOLLOW-UPS.md` ("## ap-1d"). The allowance is recorded with `tools/trust_map.py --allow` (S 9 in `docs/trust-baseline.json`, signed "SIGNED by standing ruling R16 (DRI-RULINGS.md), ap-1d, 2026-10-18"). | `uv run python tools/trust_map.py --check` exit 0 |
