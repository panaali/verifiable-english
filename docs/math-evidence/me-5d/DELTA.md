# me-5d DELTA: what a decided derivation shows (math-evidence ME-5, last part)

Feature item me-5d (plan `docs/spec/math-evidence-PLAN.md` 3.2, 3.4, ME-2 and ME-5; spec `docs/spec/math-evidence.md`
3.4 and 5). Base: main at ab010c3f0. Every user-visible change is a row. No answer changes: the certificate and the
counterexample are computed and pinned in Lean but are not on the wire (REPORT, "Stop"). No verdict, reason, refusal,
member, `meaning_id` or `claim_id` changes. Evidence:

- The 7 recorded genuine `calc` answers of `tests/data/binding-answers.jsonl.gz` (recorded on main) are byte-identical
  when asked of the head's `ve_service`.
- The whole-answer goldens of R-1 to R-4 in `lean/VE/Calc/RunExamples.lean` are unchanged and pass.
- `tests/test_calc_service.py::test_route_cases_answer_their_rows` is unchanged and passes.

| # | Change | Evidence | Ruling |
|---|---|---|---|
| 1 | Trusted base: untied V +41, K +0, S +0 (`tools/trust_map.py --check` on the final HEAD, PASS with the allowance in `docs/trust-baseline.json`): `lean/VE/Calc/Run.lean` +41, all D[V]: `Shown`, `Run.factJson`, `Run.stepJson`, `Run.reads`, `Run.shownJson`. `Derive.shown` and `Check.runShown` are C: they replace `Derive.outcome` and `Check.run`'s body, which `Check.run_sound` covers. `Check.run` is now `(Check.runShown ds k).1`, and its statement is unchanged. The `RunExamples` helpers are T | Every new trusted definition is exercised by a check that can fail. `trust-mutants.json`: `tools/trust_mutants.py --max-mutants 1000` on the final Lean change (ve-mac-1), with 91 killed, 0 survivors, 0 unknown and exit 0; the 8 allowed are mutants that do not elaborate, each with its reason in `trust-mutants-allow.json`. `mutants.json` has 12 seeded bugs, each failing a named `#guard` or proof. FOLLOW-UPS "## me-5d" asks for the ties pass | R16 |
