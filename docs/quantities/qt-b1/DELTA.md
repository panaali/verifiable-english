# qt-b1: user-visible delta

Feature item qt-b1 (QT-B1 of `docs/spec/quantities-PLAN.md`, rank 18 of the feature feed, acting DRI dri-featurefeed,
2026-10-18).

**What users see does not change.** The new modules `lean/VE/Scales/*` are reachable from no service mode, route,
decoder or relay: no `runMode` case, wire field, diagnostic, verdict, limit or fault order changes, and no Python or
Rust product file changes. No existing Lean source changed except the import list `lean/VE.lean` and the generated
audit files. The one delta is the trust budget.

| # | Delta | Ruling | Evidence |
| --- | --- | --- | --- |
| 1 | Trust budget: **S +78** (K +0, V +0), measured with `uv run python tools/trust_map.py --check` on the final tree against its merge base with main, cb033316a: `VE/Scales/Syntax.lean` +29 (Direction 5, Grade 6, Dimension 11, ScaleDoc 4, Dimension.symbols 1, ScaleDoc.symbols 2), `VE/Scales/Premises.lean` +27 (gradeOrder 2, gradeCaps 2, aboveNodes 3, WellFormed 20), `VE/Scales/Intended.lean` +22 (Intended 22). `premises` and `scalePremises` are C, tied to `dim_iff` and `premises_iff_intended`; `rel1`, `rel2` are C; the fixtures are T. | SIGNED by standing ruling R16 (DRI-RULINGS.md): new Lean-owned behaviour, at most 150 lines, none in K; every trusted definition is stated about by a theorem (`tests/test_scales_exercised.py` runs `tools/trust_map.py`'s R16 rule `unexercised` over `lean/VE/Scales/` and shows it can fail); each trusted definition carries at least one seeded bug that fails `lake build VE.Scales.Examples` (`docs/quantities/qt-b1/mutants.json`, 50/50 killed, `evidence/mutants-run.json`); the ties pass is asked for in `manage-agents/FOLLOW-UPS.md` ("## qt-b1", text saved in `evidence/follow-ups-row.md`). The allowance is recorded with `tools/trust_map.py --allow` (S 78 in `docs/trust-baseline.json`, signed "SIGNED by standing ruling R16 (DRI-RULINGS.md), qt-b1, 2026-10-18") | `uv run python tools/trust_map.py --check` PASS after the sync with main (merge e3bf6c78d); `tests/test_scales_exercised.py` 3 passed; mutants 50/50 killed |
