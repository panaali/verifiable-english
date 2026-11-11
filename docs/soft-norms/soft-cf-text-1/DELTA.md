# soft-cf-text-1: user-visible deltas

Base: main b81b82ef9 (with rights-cfr-2-budget-1 merged). Only the `status_text` of a `soft-conflict` CONFLICT-FREE
answer with no `coherent_model` in the request changes. Every JSON field (`verdict`, `coherent_exhibit`, `budget`,
`targets`, `conditional_on`) is byte for byte as on the base, no field is added or removed, and so are the UNKNOWN
line, the witness lines, the line with a model (`yes`) and every count. The saved records are in `delta.json`; their
base lines were measured on the unedited tree (`evidence/step1-output.txt`).

Not a row, because no printed output changes: the line's `<j>` already counts the open WP(T) on the base
(`openAfterClassification`, rebuilt on `Wire.openCoherence` by rights-cfr-2-budget-1), so deliverable (2) changes no
product line. Step 1 shows `<j>` equal to the size of the open WP(T) list on every recorded fixture and every logged
test answer (all with `<k>` = `<j>`), and on one constructed case where `<k>` 0 and `<j>` 1 differ. This item pins
that count with a test (`test_soft_weighing_point_count_is_the_open_wp_list`) and a `#guard`. No printed count moves,
so the task's only reason to stop does not apply. The rights route's line is unchanged byte for byte: `exhibitedText`
now reads the same words from `Wire.notSearchedText` (RightsChecks.lean :55-:64 and tests/test_rights_report_parts.py
pass unchanged).

| # | Delta | Ruling |
|---|---|---|
| 1 | `soft-conflict`, CONFLICT-FREE, with no `coherent_model` in the request: `status_text` ends `coherent situation exhibited: none supplied (not searched; budget N unused)` instead of `coherent situation exhibited: UNKNOWN (budget N)`, N the request's `budget` (default 10000). No coherent-situation search runs on this route, so the old words read as a search that hit its budget. With a model supplied the line still ends `coherent situation exhibited: yes`. The words are rights-cfr-2-budget-1's, from one Lean definition (`VE.SoftNorms.Wire.notSearchedText`) that both routes call. | R1: the quoted value `budget N` and the path `status_text` are kept, and the text is more specific (it says no model was supplied or searched). Tests: `test_soft_no_search_delta_keeps_every_quoted_value` (over `delta.json`: each head is Lean's line now, keeps every number the base quoted, removes only `UNKNOWN (budget N)`, and every JSON field equals the saved one), `test_soft_conflict_free_without_a_coherent_model_names_no_search` (budgets 10000 and 7, raw route and relay; with a model, `yes`), `#guard`s SoftNorms/Run.lean :129-:130. |
| 2 | docs/spec/soft-norms.md 7.3 writes the shipped no-search alternative (`none supplied (not searched; <budget> unused)`) and says what `<k>` and `<j>` count; docs/spec/rights.md 7.3 adds that the soft route uses the same words from one definition. | R3: explanation added to the spec; nothing removed or renamed (the template keeps `yes` and `UNKNOWN (<budget>)`). Test: `soft_spec_line` in tests/test_soft_norms_lean.py reads the soft template from the spec, and the two tests of row 1 and the weighing-point test compare Lean's line with it; tests/test_rights_report_parts.py still reads the rights template and passes. |
| 3 | Trusted Lean growth V +8 (K +0, S +0), re-measured with `tools/trust_map.py --check` against b81b82ef91ad: lean/VE/SoftNorms/Wire.lean +6 (`notSearchedText`), lean/VE/SoftNorms/Run.lean +2 (`conflictFreeText`'s docstring and call). Recorded in docs/trust-baseline.json. | R16: at most 150 lines, no K growth; each new trusted definition is exercised by a `#guard` that can fail (SoftNorms/Run.lean :129, :130; mutants S1-S4 in `mutants.json`); the ties-pass row is in `evidence/follow-ups-row.md` and appended to FOLLOW-UPS.md. |
