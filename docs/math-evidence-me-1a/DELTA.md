# me-1a delta: the `VE.Numbers` core

Base `b5248038e` (`git merge-base HEAD main`). me-1a is the first of the three items that replace
foundation/me-1 (reviews/dri-decisions-20261017b.md #6). It carries over me-1's `lean/VE/Numbers/`
files (7b93539a4) unchanged and adds `lean/VE/Numbers/Examples.lean`, whose `#guard` fixtures exercise
every new trusted definition. No Calc file is in this item.

**Public output: none.** me-1a registers no service mode, command or route. The one Python change is
where `ve/english.py` gets its four order phrases: from `ve/numbers_phrases.json`, generated from Lean's
`VE.Numbers.orderPhrases`, instead of the deleted `_COMPARISONS` literal. The rows are byte-for-byte the
same phrases, relations, operand order and row order as on main (`tests/test_numbers_phrases.py::
test_comparison_rows_match_generated_table` pins them; `tests/test_english_lean_s3.py::
test_the_comparison_actions_swap_more_and_at_least` and the selected suite check the parser's behaviour
on them). No diagnostic, fault order, verdict or English line changes, so none of this is a row below.

## User-visible deltas

Trust growth, re-measured with `uv run python tools/trust_map.py --check` on the final code: K +0,
S +76, untied V +27, trusted +103 against `b5248038ee26`. Recorded as two allowances (S 76, V 27) in
`docs/trust-baseline.json` with `trust_map.py --allow`; `trust_map.py --check` passes. R16's part is
88 lines (its cap is 150 per item, none in K); R6's part is 15 lines. The ties-pass row R16 asks for is
in manage-agents FOLLOW-UPS.md, section "## me-1a" (infra item ties-me-1a). Line numbers below are
`lean/VE/Numbers/Examples.lean`; the seeded bugs that make these checks fail are in
[`mutants.json`](mutants.json).

| # | File | Trusted lines (class, declaration: lines) | Exercised by | Ruling |
|---|---|---|---|---|
| 1 | `lean/VE/Numbers/Round.lean` | +54: S 50 (`Printed` 5, `Printed.value` 1, `Rounding` 4, `RoundsTo` 14, `tieAt` 4, `Verdict` 4, `Limit` 4, `UnknownReason` 9, `Outcome` 5); V 4 (`Printed.ofDec` 1, `Printed.sci` 3) | `#guard`s 22-29 (`Printed`), 32-70 (all four rules, both sides of zero, negative places, spec fixtures V-1, V-8, V-9; `tieAt` at 35, 38, 45, 57), 73-84 and 100 (every `UnknownReason` text against the spec table, `Limit`, `Outcome`, `Verdict`; the guards at 83-84 on the types `Verdict` and `Outcome` can fail only by not compiling); seeded bugs 1-4 | SIGNED by standing ruling R16 (DRI-RULINGS.md) |
| 2 | `lean/VE/Numbers/Decimal.lean` | +9: S 9 (`decValue` 4, `tenPow` 5) | `#guard`s 11-19 (sign, written places, negative powers); the proof `decValue_lower` ties `decValue` to W6's `VE.Time.lower`; seeded bug 5 | SIGNED by standing ruling R16 (DRI-RULINGS.md) |
| 3 | `lean/VE/Numbers/PhrasesMain.lean` | +14: V 14 (`relName` 5, `phraseJson` 7, `main` 2): the generator of `ve/numbers_phrases.json` | `tests/test_numbers_phrases.py::test_the_committed_table_is_the_lean_generators_output` runs `tools/numbers_phrases.py --check` unmocked in the suite (review F1; the regen entry `numbers-phrases` names it as its `fresh` check, and `tests/test_regen_generated.py::test_every_table_the_product_reads_is_checked_by_the_suite_or_the_gate` requires one for every generated `ve/` file); `tests/test_numbers_phrases.py::test_comparison_rows_match_generated_table`; seeded bugs 7, 11 and 12 | SIGNED by standing ruling R16 (DRI-RULINGS.md) |
| 4 | `lean/VE/Numbers/Phrases.lean`, new meaning | +11: S 8 (`Rel.Holds` 5, `Comparison.Holds` 3); V 3 (`equalsPhrase` 1, `withinPhrase` 2) | `#guard`s 88-91 (each relation, swapped and not, at its boundary), 94-97 | SIGNED by standing ruling R16 (DRI-RULINGS.md) |
| 5 | `lean/VE/Numbers/Phrases.lean`, the moved table | +15: S 9 (`Rel` 4, `Comparison` 5); V 6 (`orderPhrases` 6). These replace `ve/english.py`'s `_COMPARISONS` (two lines of rows, relation and operand swap), deleted in this change; Python now reads the generated rows | `#guard`s 92-95; `tests/test_numbers_phrases.py::test_comparison_rows_match_generated_table`; `tests/test_english_lean_s3.py::test_the_comparison_actions_swap_more_and_at_least`; seeded bugs 6 and 8 | SIGNED by standing ruling R6 (DRI-RULINGS.md) |

The task put all 26 lines of `Phrases.lean` under R6. Rows 4 and 5 split them more strictly: only the
lines that stand for the deleted Python rows (the row type and the rows) are under R6, and the new
meaning and the two phrases Python never had are under R16. Both parts stay within their rulings
(R16's total is 88 of 150).
