# qt-b1b: user-visible delta

Feature item qt-b1b (the model-construction half of QT-B1 of `docs/spec/quantities-PLAN.md`, rank 33 of the feature
feed, acting DRI dri-featurefeed, 2026-10-18).

**What users see does not change.** The changed modules `lean/VE/Scales/*` are reachable from no service mode, route,
decoder or relay: no `runMode` case, wire field, diagnostic, verdict, limit or fault order changes, and no Python or
Rust product file changes. No Lean source outside `lean/VE/Scales/` changed except the generated audit files. No
approved statement changed: the five new statements equal spec 6.2's text (`evidence/statements.json`). The one delta
is the trust budget.

| # | Delta | Ruling | Evidence |
| --- | --- | --- | --- |
| 1 | Trust budget: **S +9** (K +0, V +0), measured with `uv run python tools/trust_map.py --check` on the final tree against its merge base with main, b1f7ca7ad: `VE/Scales/Degrees.lean` +6 (StrictLinear 6), `VE/Scales/Intended.lean` +3 (Fresh 3). The model constructions `reread`, `point` and the degree classes `asMuch`, `below`, `degreeSetoid` are proof helpers (P), used only inside proofs; the new fixtures are T. | SIGNED by standing ruling R16 (DRI-RULINGS.md): new Lean-owned behaviour, at most 150 lines, none in K; every trusted definition is stated about by a theorem (`tests/test_scales_exercised.py` runs `tools/trust_map.py`'s R16 rule `unexercised` over `lean/VE/Scales/`, and `test_fresh_is_stated_about_by_scales_conservative` shows it names `Fresh` once `scales_conservative` is dropped); each trusted definition carries seeded bugs that fail `lake build VE.Scales.Examples` (`docs/quantities/qt-b1b/mutants.json`: Fresh 2, StrictLinear 2; 12/12 killed, `evidence/mutants-run.json`); the ties pass is asked for in `manage-agents/FOLLOW-UPS.md` ("## qt-b1b", text saved in `evidence/follow-ups-row.md`). The allowance is recorded with `tools/trust_map.py --allow` (S 9 in `docs/trust-baseline.json`, signed "SIGNED by standing ruling R16 (DRI-RULINGS.md), qt-b1b, 2026-10-18") | `uv run python tools/trust_map.py --check` PASS; `tests/test_scales_exercised.py` 4 passed; mutants 12/12 killed |
