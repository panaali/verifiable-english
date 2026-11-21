# srccov-math-mini-paper-1119 DELTA

This item changes no product code: nothing under `ve/`, `lean/` or `rust/`, and no decision path. VE's diagnostics,
fault order, fields, verdicts, availability and CPU are those of main at 12cb72fa55. One legend of one use case changes
(the reader is shown it), so it gets one row. The identity hashes that legend feeds were re-pinned by the generators,
which REPORT.md lists. No row is reserved for the DRI.

| # | Delta | Evidence and tests | Ruling |
|---|---|---|---|
| 1 | `usecases/math-mini-paper/environment.json`, predicate `lists`, `description`: the first sentence of the paper's Definition D1 (unit S0001) is appended word for word after the old text, which stays unchanged: "A point y is self-listing for a relation R when R(y, y)." (paper.template.md:123, markdown emphasis left out). Information is added; nothing is removed or renamed. The `environment_id` of this environment changes as a result, and `verify.py` re-pins it in the 11 certificates of C2, T1-T8, T7a and T7b (with their meaning ids). The proof traces stay byte-identical, and so do the verdicts (verdict.json), the rendered paper and the vocabulary lint. | `tests/test_srccov_math_mini_paper_1119.py::test_source_unit_is_carried_in_the_rules_legend[srccov-math-mini-paper-s6-1-1119]` (the legend holds the sentence read from the source, after `omit_norm`) and `::test_carrier_legend_belongs_to_a_symbol_the_rules_use`; `tests/test_defs_repair_math_mini_paper_1119.py::test_certificates_pin_the_carrier_environments`; `tests/test_closure_induction.py::test_all_committed_mini_paper_certificates_still_replay_unchanged` (Python and Lean replay). Goldens: certificates (`verify.py`), `conformance/english-lean/lexicon-report.json` and `corpus-seal.json` regenerated. No id or position is named, so there is nothing to bind. | R3 (DRI-RULINGS.md) |
