# me-2nb DELTA: `calc@0`'s claims computed once and charged (spec 3.2 (a), (b) and limit 10)

Feature item me-2nb (plan `docs/spec/math-evidence-PLAN.md` ME-2; spec `docs/spec/math-evidence.md` 3.2; build plan
`docs/math-evidence/me-2n/REPORT.md` "me-2nb"). Base: main at ddbed3bd4. Lean lines are in
`lean/VE/Calc/RunExamples.lean` at the final HEAD. No other answer changes: a claim case that finishes today keeps its
rows (`runC_sound`, `lean/VE/Calc/Run.lean:292`; `outcome_sound` re-proved, `:461`), and no claim case ends
`ResourceLimit` (H-1, 497 rows `unknown (limit .digits)` in 107,837,424 units, under 3.2's bound 163,290,000, `:1069`).
Limit 10's refusal (`ResourceLimit: the work of the calculation exceeds 8589934592`, `:1084`) is reachable only by
derivations, whose charge is me-2nc's. No `meaning_id`, `claim_id`, schema field or row field changes.

| Row | Change | Evidence (condition tests, kept selected) | Ruling |
|---|---|---|---|
| B1 | Requests today's runner does not finish (`CheckerUnavailable` at the 60 s deadline) get 2.4's outcomes: F1-28 `holds`; G-1x512 512 rows `unknown (limit .digits)`. F1-24 and G-1 keep their answers, faster | `runC_sound`, `runC_mono`, `runC_work` (`Run.lean:292`, `:301`, `:308`) and `valueTable_read` (`Decls.lean:952`), proved without `sorry` (`python3 lean/audit.py` PASS); guards F1-28 `holds` (`:1044`), F1-511 `holds` in 396,545 units (`:1045`), G-1x512's rows all `unknown (limit .digits)` (`:1054`); route cases F1-28 and G-1 (`tests/test_calc_service.py::test_route_cases_answer_their_rows`) | SIGNED by the DRI 2026-10-27 (reviews/dri-decisions-20261027-me-2n.md item 1) |
| B2 | Trusted Lean, re-measured on the final HEAD (`uv run python tools/trust_map.py --check`: PASS, K +0, S +0, trusted −2): `lean/VE/Calc/Run.lean` −2 (D[V] `display`, `tie`, `claimFields` read a claim's sides; `Run.sides` deleted); `lean/VE/Calc/Decls.lean` +0 (the charged evaluator is C, checked by `Expr.evalC_agrees`, `valueTableC_eq`, `Claim.ofSides_eq`; `maxWork`, `smallBits`, `digitBound` G[R]); `lean/VE/Calc/Wire.lean` +0 (`Check.sidesC`, `Case.sidesC` C; `Wire.workLimit` D[R]); `Run.rowOf`, `Run.rowsC` G[V] tied to `Run.rowOf_outcome`, `Run.rowsC_some` | every new definition has a seeded bug that a guard or proof catches (`docs/math-evidence/me-2nb/mutants.json`, 28 of 28 killed); FOLLOW-UPS.md row "## me-2nb" asks for the ties pass | SIGNED by standing ruling R16 (DRI-RULINGS.md), me-2nb, 2026-10-30 |
