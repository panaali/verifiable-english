# df-1ac: user-visible delta

Feature item df-1ac (batch DF-1a of `docs/spec/defeasible-PLAN.md`, the wire; spec `docs/spec/defeasible.md` 7.2;
acting DRI dri-featurefeed, 2026-10-18).

**What users see does not change.** `lean/VE/Defaults/Wire.lean` defines the `defaults-elaborate` and
`defaults-coherence` kinds (`defaultsCase`), but no service mode, executable, response shape, schema, relay, Python or
Rust product file calls them: the kind-table row that would is df-1ad's. `tools/regen_generated.py --check` passes
with no schema or checker pin rewritten; `ve/assurance-manifest.json` gains the new file's decoder pin and its
fixture file's reason (bookkeeping the manifest tests require, no behaviour). The one delta is the trust budget.

| # | Delta | Ruling | Evidence |
| --- | --- | --- | --- |
| T1 | Trust budget: **V +36** (K +0, S +0), measured with `uv run python tools/trust_map.py --check` on the final tree against its merge base with main, c5197da78: all in `VE/Defaults/Wire.lean`. Untied D[V]: `entityIds`, `elaborateFields`, `PairStatus.label`, `coherenceFields`. Untied G[V]: `PairStatus`, `defaultsCase`. Tied (not counted): `CoherenceReplay.verdict` to `defaults_coherence_sound`, `CoherenceReplay.pairs` to `defaults_coherence_sound` (a pair shown `resolved`) and `coherence_collision_shown` (a pair shown `collision`), `elaborateRows` to `elaborateRows_eq`. C (not counted): the view, the replays and the checks. D[R] (not counted): `viewRest` and the diagnostic texts. | SIGNED by standing ruling R16 (DRI-RULINGS.md): new Lean-owned behaviour, 36 lines, at most 150, none in K; every new trusted definition is exercised by a test that can fail: `docs/defeasible/df-1a/evidence/run_mutants.py docs/defeasible/df-1ac/mutants.json` runs W1 to W10 (at least one per trusted definition but the type `PairStatus`; W9 and W10 are the review's dropped conditions and also break `coherence_collision_shown`), each failing the `#guard`s it names with every theorem removed (saved run `evidence/mutants.out`, control 0 failures), and `tools/trust_mutants.py` kills 84 of 90 mechanical mutants with the other 6 allowed as mutants that do not elaborate (`trust-mutants.json`, `trust-mutants-allow.json`, exit 0). The ties pass is asked for in `manage-agents/FOLLOW-UPS.md` ("## df-1ac"). The allowance is recorded with `tools/trust_map.py --allow` (V 36 in `docs/trust-baseline.json`, signed "SIGNED by standing ruling R16 (DRI-RULINGS.md), df-1ac, 2026-10-18") | `uv run python tools/trust_map.py --check` exit 0; `tools/regen_generated.py --check` |
