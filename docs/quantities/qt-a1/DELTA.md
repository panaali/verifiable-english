# qt-a1: user-visible delta

Feature item qt-a1 (QT-A1 of `docs/spec/quantities-PLAN.md`, rank 16 of the feature feed, acting DRI dri-featurefeed,
2026-10-18).

**What users see does not change.** The new modules `lean/VE/Cardinality/*` are reachable from no service mode,
route, decoder or relay: no `runMode` case, wire field, diagnostic, verdict, limit or fault order changes, and no
Python or Rust file changes. Every existing environment and its `environment_id` is unchanged (no existing Lean source
changed except the import list `lean/VE.lean` and the generated audit files). The diagnostic texts of `problemLimits`
(spec 4.2, P1 and P2) are new Lean strings that no route emits yet; QT-A3 puts them on the wire. The one delta is the
trust budget.

| # | Delta | Ruling | Evidence |
| --- | --- | --- | --- |
| 1 | Trust budget: **S +137** (K +0, V +0), measured with `uv run python tools/trust_map.py --check` on the final tree against its merge base with main, c7fc6acac: `VE/Cardinality/Syntax.lean` +81 (Body 9, Rel 4, CountAtom 8, Cmp 5, Proportion 10, CFormula 11, CEnv 5, regionPrefix 2, CEnv.WellFormed 6, BodyTyped 8, Admitted 13), `VE/Cardinality/Semantics.lean` +56 (Body.holds 7, HasCount 5, Rel.holds 5, Cmp.holds 8, Counts 6, CountAtom.holds 4, Proportion.holds 5, CFormula.holds 9, Admissible 4, CEntails 3). The check passes with the recorded allowance. | SIGNED by standing ruling R16 (DRI-RULINGS.md): new Lean-owned behaviour, at most 150 lines, none in K; each definition is exercised by a named theorem of `lean/VE/Cardinality/Examples.lean` that states its cases, true cases beside false ones (fix round 1, review F1: `body_cases`, `counts_unique`, `counts_two`, `everyone_two`, `rel_cases_two`, `weighted_two`, `share_two`, `cmp_cases_two`, `population_cases`, `quantity_cases`, `connective_cases`, `admissible_cases`, `entails_cases`, `wellFormed_cases`, `admitted_cases`); `tests/test_cardinality_exercised.py` checks with `tools/trust_map.py`'s R16 rule (`unexercised`) that no trusted definition of `lean/VE/Cardinality/` is left out of every theorem statement, and 51 seeded bugs, one per case of each trusted definition (the review's 15 among them), each fail `lake build VE.Cardinality.Examples` (`docs/quantities/qt-a1/mutants.json`, run with `tools/mutants.py`, results `evidence/mutants-run.json`); the ties pass is asked for in `manage-agents/FOLLOW-UPS.md` ("## qt-a1", re-appended in fix round 2; its text is saved in `evidence/follow-ups-row.md`). The allowance is recorded with `tools/trust_map.py --allow` (S 137 in `docs/trust-baseline.json`, signed "SIGNED by standing ruling R16 (DRI-RULINGS.md), qt-a1, 2026-10-18") | `uv run python tools/trust_map.py --check` exit 0; `tests/test_trust_budget.py`, `tests/test_trust_ratchet.py` pass (110 passed, HEAD a5b780b4e); after fix round 1 the check still measures S +137 (the new fixtures are T); `tests/test_cardinality_exercised.py` passes; mutants 51/51 killed |
