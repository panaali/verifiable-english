# me-2 delta: the `ve-calc@0` wire and the `calc` runner

**Public output: none.** me-2 registers no service mode, command or route (the `calc` mode, its shape and its encoder
are me-2b), and no Python or Rust product path reads the new modules: `VE.Calc.Wire` and `VE.Calc.Run` are reached
only by the Lean build, whose `#guard`s in `lean/VE/Calc/RunExamples.lean` hold the route cases. `VE.Calc.Units` now
takes `checkFields` and `invalid` from `VE.Calc.Wire` (moved, unchanged but for an optional-field list) and spells a
factor with `Wire.plain`, which writes every positive decimal as before: every `UnitsExamples` guard is unchanged.

Trust growth, re-measured with `uv run python tools/trust_map.py --check` on the final code: K +0, S +14, untied V
+134, trusted +148, recorded with `trust_map.py --allow` in `docs/trust-baseline.json`. The ties-pass row R16 asks
for is in manage-agents FOLLOW-UPS.md, section "## me-2". [`trust-mutants.json`](trust-mutants.json) is
`tools/trust_mutants.py --max-mutants 1000` on the final Lean change: 125 killed, 21 allowed
([`trust-mutants-allow.json`](trust-mutants-allow.json), each with its reason), 10 not programs, 0 survivors, 0
unknown, 0 not run; exit 0. [`mutants.json`](mutants.json) is the hand mutants' record: 23 of 23 killed.

| # | File | Trusted lines (class, declaration lines) | Exercised by (`lean/VE/Calc/RunExamples.lean`) | Ruling |
|---|---|---|---|---|
| 1 | `lean/VE/Calc/Wire.lean`, `lean/VE/Calc/Run.lean` | +148. Wire.lean: S 4 (`Check` 4); D[V] 129 (`Case` 5, `literal` 14, `operations` 3, `comparisons` 3, `rules` 2, `expr` 20, `claim` 26, `value` 17, `entry` 9, `decl` 5, `decode` 25). Run.lean: S 10 (`Check.UnknownCause` 5, `Check.OutcomeMeans` 5); D[V] 5 (`Run.rowJson` 5). Not counted: the limits, refusals and name checks are D[R], the canonical forms and digests D[I]; `decodeCase`, `Run.rows`, `Row`, `Run.row`, `Run.words`, `Run.outcomes`, `Run.outcomeAt` and `Run.runCaseReported` are tied to `decodeCase_wellFormed`, `rows_outcome`, `row_outcome`, `outcomes_words`, `outcome_sound` and `row_sound` | the R-1 and R-2 answers pinned whole (lines 54-55), `outcomeAt` and `words` (57-60), the route family (91: V-1, V-2, V-5, V-9, V-8's rules, I-1, every claim form, order), the identity guards (132-145), limits (153), the hostile set (188) and paths (242); the decided-row meaning (123); `trust-mutants.json` (every mutant of each listed definition killed or allowed); hand mutants in `mutants.json` | SIGNED by standing ruling R16 (DRI-RULINGS.md) |
