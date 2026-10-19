# qt-a2: user-visible delta

Feature item qt-a2 (QT-A2 of `docs/spec/quantities-PLAN.md`, rank 20 of the feature feed, acting DRI dri-featurefeed,
2026-10-18).

**What users see does not change.** `lean/VE/Cardinality/*` is reachable from no service mode, route, decoder or
relay (QT-A3 adds the mode): no `runMode` case, wire field, diagnostic, verdict, limit or fault order changes, and no
Python or Rust file changes. The one delta is the trust budget.

| # | Delta | Ruling | Evidence |
| --- | --- | --- | --- |
| 1 | Trust budget: **S +35** (K +0, V +0), measured with `uv run python tools/trust_map.py --check` on the final tree against its merge base with main, 702ff7429: `VE/Cardinality/Syntax.lean` +25 (CTerm 6, CTermTyped 6, admittedRules 3, CFormula +4, Admitted +6), `VE/Cardinality/Semantics.lean` +10 (CTerm.Denotes 5, CFormula.holds +5). The new C declarations are tied (`CTerm.tagOf` by `tagOf_iff`, `ratioTyped` by `ratioTyped_iff`, `erasedRounding` by `roundsTo_ratio_agree`) or untrusted (`roundingQ`, `CTerm.erase`, `CTerm.countBodies`). | SIGNED by standing ruling R16 (DRI-RULINGS.md): new Lean-owned behaviour, 35 lines, none in K; each new trusted definition is stated about by a named theorem of `lean/VE/Cardinality/Examples.lean`, true cases beside false ones (`denotes_cases`, `ratio_cases`, `admittedRules_cases`, `cterm_typed_cases`, `admitted_ratio_cases`), which `tests/test_cardinality_exercised.py` checks with `tools/trust_map.py`'s R16 rule; 36 seeded bugs, at least one in each new trusted definition and in each ratio case of `CFormula`, `Admitted` and `CFormula.holds`, each fail `lake build VE.Cardinality.Examples` (`docs/quantities/qt-a2/mutants.json`, results `evidence/mutants-run.json`); the ties pass is asked for in `manage-agents/FOLLOW-UPS.md` ("## qt-a2 (2026-10-19)", text saved in `evidence/follow-ups-row.md`). The allowance is recorded with `tools/trust_map.py --allow` (S 35 in `docs/trust-baseline.json`, signed "SIGNED by standing ruling R16 (DRI-RULINGS.md), qt-a2, 2026-10-18") | `uv run python tools/trust_map.py --check` exit 0 (PASS); `tests/test_trust_budget.py` and `tests/test_cardinality_exercised.py` pass in the selected run (HEAD 64571cab, 67 units, 0 failed); mutants 36/36 killed |
