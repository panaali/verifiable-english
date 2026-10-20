# df-1ab: user-visible delta

Feature item df-1ab (batch DF-1a of `docs/spec/defeasible-PLAN.md`, second part; spec `docs/spec/defeasible.md` 7.1;
acting DRI dri-featurefeed, 2026-10-18).

**What users see does not change.** The new definitions are in `lean/VE/Defaults/Premises.lean`, which no service
mode, executable, response shape, schema, relay, Python or Rust product file reaches (`Wire.lean` and the kinds are
df-1ac's): `tools/regen_generated.py --check` passes with no schema or checker pin rewritten. The one other Lean edit,
`lean/VE/SoftNorms/RankProof.lean`, changes proofs only: its helper lemmas (`raw_dom_denote`, `raw_eff_denote`,
`raw_dom_congr`, `raw_eff_stable`, `raw_resolve_higher`, `raw_selects_eff`, none in a spec) take the substitution
table as a parameter, and the new `coh_rank_valid_with` states soft's argument for any table. The approved statement
`VE.SoftNorms.coh_rank_valid` (soft-norms.md 7) and its pinning `example` in `SoftNorms/Status.lean` are unchanged, as
is `coh_rank_valid_unconditional`'s. The one delta is the trust budget.

| # | Delta | Ruling | Evidence |
| --- | --- | --- | --- |
| T1 | Trust budget: **S +6, V +23** (K +0; 29 lines), measured with `uv run python tools/trust_map.py --check` on the final tree against its merge base with main, bfec7f9ef: all in `VE/Defaults/Premises.lean`. S: `DefaultCoherent` (the gate's meaning, spec 3.3). Untied G[V]: `collisionTuple`, `decidersOf`, `giveWayDeciders`. Tied (not counted): `selU` to `cohPremiseU_selU` (an equation with the S-side `cohPremiseU`). G[R] (not counted): `decisionFree`, `whatOf`, `questionDiag`, `limitDiag`. C (not counted): `pairChecks`, `defaultCoherenceCheck`, `collisionCheck`. The check passes with the recorded allowance. | SIGNED by standing ruling R16 (DRI-RULINGS.md): new Lean-owned behaviour, 29 lines, at most 150, none in K; every new definition of `Premises.lean` is exercised by a test that can fail: `docs/defeasible/df-1a/evidence/run_mutants.py docs/defeasible/df-1ab/mutants.json` runs D1 to D17 (at least one per new definition), each failing the `#guard`s it names with every theorem removed, and D4 (`DefaultCoherent` read as `True`, a `Prop`) failing `collision_sound`; the saved run is `evidence/mutants.out`, control 0 failures. The ties pass is asked for in `manage-agents/FOLLOW-UPS.md` ("## df-1ab"). The allowance is recorded with `tools/trust_map.py --allow` (S 6 and V 23 in `docs/trust-baseline.json`, signed "SIGNED by standing ruling R16 (DRI-RULINGS.md), df-1ab, 2026-10-18") | `uv run python tools/trust_map.py --check` exit 0; `tools/regen_generated.py --check` |
