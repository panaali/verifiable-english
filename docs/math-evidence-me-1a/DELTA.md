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
| 6 | `lean/VE/Numbers/{Decimal,Round,Phrases,PhrasesMain}.lean`: ties pass (infra item ties-me-1a, R16's FOLLOW-UPS row "## me-1a") | −8: S −8, untied V ±0, K ±0. `decValue` (4, Decimal.lean) and `tieAt` (4, Round.lean) move from S to G[V], each tied in `tools/trust-classes.json` to an existing theorem (`Printed.value_ofDec`; `tieAt_iff`). Per file, trusted before → after: Decimal.lean 9 → 5, Round.lean 54 → 50, Phrases.lean 26 → 26, PhrasesMain.lean 14 → 14; all files 52,111 → 52,103 (S 10,228 → 10,220, tied 263 → 271). me-1a's growth over its base `c4d7ea565` falls from +103 to +95 (S +76 → +68). The 95 lines left are listed, each with why no existing theorem ties it, in "Trust ties pass" below; no allowance is raised or added and no trusted line is written | `python3 tools/trust_map.py --check --since c4d7ea565` PASS before (05b85b631, "S +76 … trusted +103") and after (db74414d9, "S +68, … tied +8, … trusted +95"); `python3 tools/trust_map.py --check` against main 05b85b631 PASS ("S -8, D +0, G +8, tied +8, … trusted -8"); seeded ties M1–M6 each fail `trust_map.py --check` and `tests/test_trust_ratchet.py::test_committed_budget_passes_its_check`; [`evidence/ties/`](evidence/ties/) | R16 ties pass |

The task put all 26 lines of `Phrases.lean` under R6. Rows 4 and 5 split them more strictly: only the
lines that stand for the deleted Python rows (the row type and the rows) are under R6, and the new
meaning and the two phrases Python never had are under R16. Both parts stay within their rulings
(R16's total is 88 of 150).

## Trust ties pass (infra item ties-me-1a, 2026-10-18)

Row 6. Method: `python3 tools/trust_map.py --check --since c4d7ea565` was run on main with me-1a merged (`05b85b631`)
against main before the merge (`c4d7ea565`). The growth is all in `lean/VE/Numbers/`: trusted +103 (S +76, untied V +27)
in Round.lean (+54), Phrases.lean (+26), PhrasesMain.lean (+14) and Decimal.lean (+9), the declarations of rows 1-5. Each
was looked up in `lean/statements.txt` for a theorem whose `-- uses` line names it and another anchor (K, S or untied [V]).
No theorem outside `VE.Numbers` names any of them; me-1a registers no service mode, so there is no render, wire, encoder
or decoder theorem, and the ties use me-1a's own theorems. The tool ties only C, D and G declarations, so a tied
declaration moves from S to G[V] (as in ties-qs-1). A tie was added only where the statement, on its own, fixes what the
declaration means in terms of declarations that stay trusted.

### Ties added (commits 736f9a049, db74414d9)

| File | Declaration (lines) | Tying theorem (anchors) | What the statement fixes |
| --- | --- | --- | --- |
| `VE/Numbers/Round.lean` | `VE.Numbers.tieAt` (4), S to G[V] | `VE.Numbers.tieAt_iff` (`VE.Numbers.tenPow`, S) | `tieAt k x = true ↔ ∃ d : Int, 2 * (x * tenPow k) = 2 * d - 1`, for every `k` and `x`: `tieAt` is Bool, so this fixes it completely as "x at k places lies exactly halfway between two integers", in terms of `tenPow` |
| `VE/Numbers/Decimal.lean` | `VE.Numbers.decValue` (4), S to G[V] | `VE.Numbers.Printed.value_ofDec` (`Printed.value`, S; `Printed.ofDec`, untied V; `VE.Time.Dec`, untied D[V]) | `(Printed.ofDec d).value = decValue d` for every written decimal `d`: this fixes `decValue` completely as the value of the decimal's printed form, `Printed.value` (S) applied to `Printed.ofDec` (trusted, untied). Both stay trusted, so nothing here rests on a second tied declaration |

Rejected candidates (FOLLOW-UPS lists them; each was checked and not added):

- `tieAt_iff_floor_tie` and `rules_differ_iff` for `tieAt`: both follow from `tieAt_iff` and add nothing to it.
- `decValue_lower` for `decValue` (`lower d k = some q → decValue d = q / 10 ^ k`): the tool would accept it, but its only
  anchor is the binder's type `VE.Time.Dec`, which says nothing about a value; the constraint comes through
  `VE.Time.lower`, which is C (not an anchor), and holds only with `VE.Time.decimal_exact` beside it. A tie must hold on
  its own statement, so it is not listed; `value_ofDec` fixes `decValue` on its own.
- `Printed.value_sci` for `Printed.value`: `value` is defined from `tenPow`, so `value_sci` only restates that definition;
  and tying `value` beside the `decValue` tie would let both be wrong together (doubling `value` and `decValue` keeps
  `value_ofDec` and `value_sci` true). `value` stays S as the anchor of the `decValue` tie.

### Per-file counts (`trust_map.py`; base `c4d7ea565`, before `05b85b631` (main with me-1a merged), after `db74414d9`)

| File | S before | S after | G[V] before | G[V] after | Tied before | Tied after | Trusted before | Trusted after |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `VE/Numbers/Decimal.lean` | 9 | 5 | 0 | 4 | 0 | 4 | 9 | 5 |
| `VE/Numbers/Round.lean` | 50 | 46 | 4 | 8 | 0 | 4 | 54 | 50 |
| `VE/Numbers/Phrases.lean` | 17 | 17 | 9 | 9 | 0 | 0 | 26 | 26 |
| `VE/Numbers/PhrasesMain.lean` | 0 | 0 | 14 | 14 | 0 | 0 | 14 | 14 |
| **All files** | **10,228** | **10,220** | **27,940** | **27,948** | **263** | **271** | **52,111** | **52,103** |

No other file changes; K (997) and untied V are unchanged, and the class falls by exactly the 8 tied lines. Saved in
[`evidence/ties/check-before.txt`](evidence/ties/check-before.txt), [`check-after.txt`](evidence/ties/check-after.txt),
[`check-after-vs-main.txt`](evidence/ties/check-after-vs-main.txt) and [`trust-counts.json`](evidence/ties/trust-counts.json).
The S 76 and V 27 allowances of rows 1-5 are untouched; no allowance is raised or added.

### Declarations no existing theorem ties

None of these was tied, and no trusted code was written to make up for one (95 lines).

| File | Declaration (lines, class) | Why no existing theorem ties it | A theorem that would |
| --- | --- | --- | --- |
| `VE/Numbers/Round.lean` | `Printed` (5, S), `Rounding` (4, S) | Data types: the theorems that name them use them as the binder's type, and they are the anchors of every Round.lean statement | None: a type is meaning; it stays S |
| `VE/Numbers/Round.lean` | `Printed.value` (1, S) | The anchor of the `decValue` tie; see the rejected `value_sci` above | None from the tree: it is the printed form's meaning |
| `VE/Numbers/Round.lean` | `RoundsTo` (14, S) | The rounding rules themselves. `roundsTo_iff_round` and the four `*_iff` name it beside `Rounding.round`, which is C and is checked against `RoundsTo` by those theorems; tying the rule to its checked implementation would make the meaning rest on the code. No earlier profile defines rounding to bind it to | None in the tree today; it stays S (row 1's new meaning) |
| `VE/Numbers/Round.lean` | `Printed.ofDec` (1, V), `Printed.sci` (3, V) | `value_ofDec` and `value_sci` fix the value of the printed form but not its places, which `RoundsTo` reads: `ofDec d := ⟨10 * d.significand, d.places + 1⟩` keeps `value_ofDec` true, yet would check "3.1" at two places (3.14 rounds to ⟨31, 1⟩ but not to ⟨310, 2⟩) | `ofDec_eq : Printed.ofDec d = ⟨d.significand, d.places⟩` and `sci_eq : Printed.sci d e = ⟨d.significand, d.places - e⟩` (anchors `Dec.significand`, `Dec.places`, S). Not `value_ofDec` alone: with `decValue` tied through it, `ofDec` and `decValue` could then be wrong together |
| `VE/Numbers/Round.lean` | `Verdict` (4), `Limit` (4), `UnknownReason` (9), `Outcome` (5), all S | No theorem names them; no service mode reports them in me-1a, so there is no wire or encoder theorem | The types stay S. When a route first reports an `Outcome`, its encoder theorem and decoder round-trip tie the encoder and decoder (D) to these types and to `UnknownReason.text` (already G[R]) |
| `VE/Numbers/Decimal.lean` | `tenPow` (5, S) | `tenPow_eq_zpow` (`tenPow k = 10 ^ k`) fixes it completely, but against Lean core's `Rat` power, which is no declaration of the tree; the tool accepts only tree anchors. `tenPow_add` and `tenPow_pos` name only `tenPow`; `value_sci`, `halfEven_interval`, `roundsTo_close` and `tieAt_iff` use it to fix other declarations | None in the tree: tying it needs `trust_map.py` to accept core-library anchors, a tool change outside this item |
| `VE/Numbers/Phrases.lean` | `Rel` (4, S), `Comparison` (5, S), `orderPhrases` (6, V): row 5, R6 | No theorem names them; they replace the deleted Python rows, which Python reads from the generated file | The statement a later item proves when Lean decides a comparison claim: its verdict holds iff `Comparison.Holds` of the claim's row in `orderPhrases` |
| `VE/Numbers/Phrases.lean` | `Rel.Holds` (5, S), `Comparison.Holds` (3, S) | The meaning of the comparisons; no theorem names them, and no Lean semantics of comparison sentences exists to bind them to (Python parses them) | The same theorem; the predicates stay S |
| `VE/Numbers/Phrases.lean` | `equalsPhrase` (1, V), `withinPhrase` (2, V) | No theorem names them; only the `#guard`s of `Examples.lean` read them, and the generator does not write them | The same theorem, for the "equals" and "from … through" claims |
| `VE/Numbers/PhrasesMain.lean` | `relName` (5, V), `phraseJson` (7, V), `main` (2, V) | The generator of `ve/numbers_phrases.json`; no theorem names them (its output is checked byte for byte by `tools/numbers_phrases.py --check` in the suite) | A decoder round-trip, `phrasesOfJson (toJson (orderPhrases.map phraseJson)) = some orderPhrases`, with the decoder in Lean (anchor `orderPhrases`) |

### Seeded ties (each planted alone on db74414d9, then restored; `trust_map.py --check` exit 1)

Listed in [`evidence/ties/seeded-ties.json`](evidence/ties/seeded-ties.json), outputs in `evidence/ties/seed-<id>.txt`. Each also
fails `tests/test_trust_ratchet.py::test_committed_budget_passes_its_check`.

| Id | Seed | File | Failure |
| --- | --- | --- | --- |
| M1 | `tieAt_iff`'s `-- uses` line loses `VE.Numbers.tenPow`, its one anchor | `lean/statements.txt` (generated; edited only for the seed) | "the statement of VE.Numbers.tieAt_iff mentions no K, S or untied [V] declaration of the tree, validly classified, to tie it to" |
| M2 | `tieAt_iff`'s `-- uses` line loses `VE.Numbers.tieAt` | `lean/statements.txt` | "the statement of VE.Numbers.tieAt_iff does not mention VE.Numbers.tieAt of VE.Numbers.Round" |
| M3 | `tieAt` tied to the unrelated `VE.Numbers.tenPow_pos` | `tools/trust-classes.json` | "the statement of VE.Numbers.tenPow_pos does not mention VE.Numbers.tieAt of VE.Numbers.Round" |
| M4 | `tieAt` tied to `Printed.value_sci` (same file, about `sci` and `value` only) | `tools/trust-classes.json` | "the statement of VE.Numbers.Printed.value_sci does not mention VE.Numbers.tieAt of VE.Numbers.Round" |
| M5 | `Printed.value_ofDec`'s `-- uses` line loses `VE.Numbers.decValue` | `lean/statements.txt` | "the statement of VE.Numbers.Printed.value_ofDec does not mention VE.Numbers.decValue of VE.Numbers.Decimal" |
| M6 | `decValue` tied to the unrelated `VE.Numbers.tenPow_add` | `tools/trust-classes.json` | "the statement of VE.Numbers.tenPow_add does not mention VE.Numbers.decValue of VE.Numbers.Decimal" |
