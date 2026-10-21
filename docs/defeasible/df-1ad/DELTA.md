# df-1ad: user-visible delta

Feature item df-1ad (batch DF-1a of `docs/spec/defeasible-PLAN.md`, the question kinds; spec `docs/spec/defeasible.md`
7.2 and 8.1; acting DRI dri-featurefeed, 2026-10-18).

**What users see does not change.** `lean/VE/Defaults/Wire.lean` now also defines the `defaults-certificate` and
`defaults-model` kinds (`defaultsCase`). No service mode, executable, response shape, schema, relay, Python or Rust
product file calls them: the kind-table row that would is df-1ae's. `tools/regen_generated.py --check` passes with no
schema or checker pin rewritten. `ve/assurance-manifest.json` updates the file's decoder pin (bookkeeping the manifest
tests require, no behaviour). The one delta is the trust budget.

| # | Delta | Ruling | Evidence |
| --- | --- | --- | --- |
| T1 | Trust budget: **V +37** (K +0, S +0), measured with `uv run python tools/trust_map.py --check` on the final tree against its merge base with main, 7855620f3: all in `VE/Defaults/Wire.lean`. Untied D[V]: `basisLabel`, `formLabel`, `certFields`, `modelFields`. Untied G[V]: `CertReplay.form`, `forcedAt`, `ModelReplay.verdict`, and `defaultsCase`'s two new branches. Tied (not counted): `CertReplay.verdict`, `CertReplay.assumptions` and `CertReplay.basis` to `defaults_certificate_sound`; `ModelReplay.forced` to `forcedAt_sound` and `defaults_model_sound`. C (not counted): the replays and checks (`CertReplay`, `certOk`, `coherent`, `collides`, `modelOk`, `strictCounter`, `ModelReplay`, `ModelReplay.ok`, `filledOf`, `replayCert(On)`, `replayModel(On)`). G[R] (not counted): `CertReplay.reason`. | SIGNED by standing ruling R16 (DRI-RULINGS.md): new Lean-owned behaviour, 37 lines, at most 150, none in K. Every new trusted definition is exercised by a test that can fail: `python3 docs/defeasible/df-1a/evidence/run_mutants.py docs/defeasible/df-1ad/mutants.json` runs Q1 to Q8 and M1 to M5, at least one per trusted definition. Each fails the `#guard`s it names with every theorem removed (saved run `evidence/mutants.out`, control 0 failures). `tools/trust_mutants.py` kills 55 of 80 mechanical mutants and allows the other 25 as mutants that do not elaborate (`trust-mutants.json`, `trust-mutants-allow.json`, exit 0). The ties pass is asked for in `manage-agents/FOLLOW-UPS.md` ("## df-1ad"). The allowance is recorded with `tools/trust_map.py --allow` (V 37 in `docs/trust-baseline.json`, signed "SIGNED by standing ruling R16 (DRI-RULINGS.md), df-1ad, 2026-10-18") | `uv run python tools/trust_map.py --check` exit 0; `tools/regen_generated.py --check` |
