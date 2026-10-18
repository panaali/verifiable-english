# me-1c delta: the `VE.Calc` English lines (`VE.Calc.Render`)

Base `c2b1a7d44` (`git merge-base HEAD main`; me-1b merged). me-1c is the last of the three items that replace
foundation/me-1 (reviews/dri-decisions-20261017b.md #6). It carries over me-1's `lean/VE/Calc/Render.lean`
(7b93539a4, with me-1's review fix F1: `renderClaim` writes a line only when spec 11.2 gives it one reading, and
`none` otherwise) unchanged, and adds its fixtures to `lean/VE/Calc/Examples.lean`. **With this item ME-1 is
complete**: me-1a (`VE.Numbers`), me-1b (`VE.Calc` meaning and checker) and me-1c (the English lines) together
deliver foundation/me-1, and wave-2 work that waited for me-1 (ME-2 first) waits for this item's merge.

**Public output: none.** me-1c registers no service mode, command or route, and no Python or Rust file changes:
`VE.Calc.English.renderClaim` is reached only by the Lean build and its fixtures (ME-2 puts its text in a row's
`line` field). No diagnostic, fault order, verdict or English line a user can see changes, so none of this is a
row below.

## User-visible deltas

Trust growth, re-measured with `uv run python tools/trust_map.py --check` on the final code: K +0, S +0,
untied V +113, trusted +113 against `c2b1a7d442b4`, all in `VE/Calc/Render.lean` (thirteen G[V] declarations).
Recorded as one allowance (V 113) in `docs/trust-baseline.json` with `trust_map.py --allow`; `trust_map.py
--check` passes. R16's cap is 150 lines per item, none in K. The ties-pass row R16 asks for is in manage-agents
FOLLOW-UPS.md, section "## me-1c" (infra item ties-me-1c). Line numbers below are `lean/VE/Calc/Examples.lean`;
the seeded bugs that make these checks fail are in [`mutants.json`](mutants.json) (13 in `Render.lean`).

| # | File | Trusted lines (class, declaration: lines) | Exercised by | Ruling |
|---|---|---|---|---|
| 1 | `lean/VE/Calc/Render.lean` | +113: G[V] 113 (`reservedWords` 5, `phraseWords` 4, `valueWordsOk` 8, `natWords` 7, `placesPhrase` 7, `printedWords` 8, `exactWords` 6, `exprDepth` 5, `renderAtom` 8, `renderTerm` 10, `renderExpr` 13, `fill` 10, `renderClaim` 22) | `#guard`s 321-324 (both tie rules, spec 13.6's line); 340-357 (every operand shape 11.2 refuses, me-1 review F1's sweep, and the accepted shapes); 359-367 (a negative number, value words that read as a phrase or are double-spaced, a template slot in value words); 446-447 (every expression to depth 3 over four atoms: a line exactly when 11.2 accepts the expression, read back by an every-parse reader of 11.2 as that expression alone); 452-460 (each comparison phrase, and a comparison with none); 461-468 (each rounding rule, zero and negative places); 470-478 (the places one to twenty in words, then 21); 480-484 (numerals, a value with no finite decimal, 40 places and 41); 486-495 (11.2's form of value words: each reserved word, the four phrase words that begin with "the", the leading "the", spacing, and whole-word matching; "twice" and "half of" cannot begin words that begin with "the", so they change no answer); seeded bugs 1-13 | R16 (standing ruling, DRI-RULINGS.md) |
| 2 | `lean/VE/Calc/Render.lean` | Ties pass for row 1 (infra item ties-me-1c, 2026-10-18): G[V] 113 -> 113, tied +0, trusted +0. Re-measured on main `22c4b9154` (me-1c merged) with `trust_map.walk`: the +113 is the thirteen G[V] declarations of row 1, all untied, and nothing else (the file did not exist at me-1c's base `c2b1a7d44`). None of the 5,774 theorems of `lean/statements.txt` names any of them on its `-- uses` line, and no Lean file states a theorem about one, so the tool can accept no tie and none is added (`tools/trust-classes.json` unchanged). The list of declarations with the theorem that would tie each is in "Trust ties pass" below. | R16 ties pass |

`lean/VE/Calc/Examples.lean` adds no trusted line (its helpers are T). Two of its new checks close me-1b review
F1 and F2 (C): `Small` at minus the limit and a decided claim on a negative value (138, 141), and a finished
count that is not exhausted (`example` 304-314); seeded bugs 14-15 (in `Decls.lean`, which this item does not
change) show each one fails.

## Trust ties pass (row 2; infra item ties-me-1c, 2026-10-18)

Method. `tools/trust_map.py`'s classifying pass (`walk`) was run on main with me-1c merged (`22c4b9154`), and every
declaration of `lean/VE/Calc/Render.lean` was listed with its class, tie and lines
([`evidence/ties/render-declarations.json`](evidence/ties/render-declarations.json), written by
[`evidence/ties/measure_render.py`](evidence/ties/measure_render.py)). The same script searched every `-- uses` line of
`lean/statements.txt` (5,774 theorems) for a constant `…@VE.Calc.Render`, the tool's own test of a tie (`classify`):
there is none. Every Lean file was also searched for a theorem that names one of the thirteen: outside `Render.lean`
itself (which states no theorem) the only file that names them is `lean/VE/Calc/Examples.lean`, whose checks are
`#guard`s and `example`s (T, not theorems, and not in the dump). So nothing is tied, and `tools/trust-classes.json` is
unchanged. `lean/VE/Calc/Examples.lean` holds no trusted line before or after.

### Per-file counts (`trust_map.py`; base = me-1c's base `c2b1a7d44`, before = `22c4b9154`, after = the same tree, since nothing is tied)

| File | Trusted at the base | Before (class: lines) | me-1c's growth | Ties | After | me-1c's growth after the ties |
| --- | --- | --- | --- | --- | --- | --- |
| `VE/Calc/Render.lean` | 0 (no file) | 113 (G[V] 113, untied) | +113 | 0 | 113 (G[V] 113, untied) | +113 |
| `VE/Calc/Examples.lean` | 0 | 0 | +0 | 0 | 0 | +0 |
| **All files** | | **52,410** (K 997, S 10,463, untied V 40,950; tied 362) | **+113** | **0** | **52,410** (tied 362) | **+113** |

`python3 tools/trust_map.py --check` passes before and after (saved: [`evidence/ties/check-before.txt`](evidence/ties/check-before.txt),
against `fcec329b9`, main's first parent, since the branch started at main's tip; and
[`evidence/ties/check-after.txt`](evidence/ties/check-after.txt), against the merge base `22c4b9154`): K +0, S +0, tied
+0, trusted +0. Of the +113 that R16 signed on the condition of this pass, the ties remove 0. No allowance is raised and
none is added.

### Declarations no existing theorem ties

Lines are untied G[V] lines. The last column is a proposal. None of these theorems is written or checked in Lean here:
the task allows ties to existing theorems only, and no trusted code was added to make up for one. Spec 9's
`read_render` and its reader `readClaim` exist only in `docs/spec/math-evidence.md` (section 9, ME-11): no Lean file
states either, so a tie to `read_render` fails today (seeded tie S3). Each proposed theorem would need, on its `-- uses`
line, a tree anchor other than the declaration it ties (a K, S or untied [V] declaration): `VE.Calc.Claim` and
`VE.Calc.Expr` (S, `VE/Calc/Syntax.lean`), `VE.Numbers.Printed.value` (S, `VE/Numbers/Round.lean`), or the phrase
table (`orderPhrases`, `equalsPhrase`, `withinPhrase`, untied G[V], `VE/Numbers/Phrases.lean`).

| File | Declaration | Lines | Why no existing theorem ties it | A theorem that would |
| --- | --- | --- | --- | --- |
| `VE/Calc/Render.lean` | `renderClaim` | 22 | No theorem names it. Its checks are `#guard`s in `Examples.lean` (321-324, 340-367, 446-495), including the depth-3 sweep read back by an every-parse reader of 11.2 that is written in the test file (T) | Spec 9's `read_render`: `renderClaim words c = some s → readClaim words s = .ok c`, with ME-11's reader of 11.1's claim forms (anchor `VE.Calc.Claim`), together with ME-11's instance of `english_reading_unique` so that the line has that one reading |
| `VE/Calc/Render.lean` | `renderExpr` | 13 | No theorem names it | The expression level of the same: `renderExpr words e = some s → readExpr words s = .ok e` for 11.2's `expression` (anchor `VE.Calc.Expr`), and the converse that the depth-3 sweep checks: `renderExpr words e = none` exactly when 11.2 refuses `e` or an atom has no words (ME-11's `NestedPhrase` rule as a predicate) |
| `VE/Calc/Render.lean` | `renderTerm` | 10 | No theorem names it | `renderTerm words e = some s → readTerm words s = .ok e` for 11.2's `term` (anchor `VE.Calc.Expr`); then no infix phrase stands inside a term |
| `VE/Calc/Render.lean` | `fill` | 10 | No theorem names it | A substitution theorem over the phrase table: for every template `t` of `orderPhrases ++ [equalsPhrase]` (two slots) and `withinPhrase` (three), written `p₀ ++ "{0}" ++ p₁ ++ "{1}" ++ …` with no `{` in any `pᵢ`, `fill args t.toList = p₀ ++ args[0] ++ p₁ ++ args[1] ++ …` for all `args` of that length, whatever text they hold (no filled-in text is read as a slot) |
| `VE/Calc/Render.lean` | `valueWordsOk` | 8 | No theorem names it | `valueWordsOk w = true ↔` 11.2's form of value words, with ME-2's `ValueWordsForm` and `ReservedWord` stated as predicates (spec 13's table gives both to ME-2; neither is in Lean yet). Through the atom level of the read-back theorems above, it also follows that an accepted value's words read as that one value |
| `VE/Calc/Render.lean` | `renderAtom` | 8 | No theorem names it | `renderAtom words e = some s → readAtom words s = .ok e` for 11.2's `atom` (a value's words or a numeral; anchor `VE.Calc.Expr`). An iff that only unfolds its two cases would be vacuous |
| `VE/Calc/Render.lean` | `printedWords` | 8 | No theorem names it; no theorem of the dump names `VE.Time.renderAmount`, which writes the numeral | `printedWords p = some s → readNumber s = some p.value` for 11.1's number reader (numerals and "times ten to the power"; anchor `VE.Numbers.Printed.value`), and `printedWords p = none ↔ p.digits < 0` |
| `VE/Calc/Render.lean` | `natWords` | 7 | No theorem names it | Part of `read_render` for a `.rounds` claim; on its own, `readPlacesWord (natWords n) = some n` for every `n ≥ 2` that `placesPhrase` passes it. Injectivity alone would not tie it: two swapped words keep it injective |
| `VE/Calc/Render.lean` | `placesPhrase` | 7 | No theorem names it | Part of `read_render` for a `.rounds` claim; on its own, `readPlaces (placesPhrase k) = some k` for every `k : Int` with 11.1's places reader |
| `VE/Calc/Render.lean` | `exactWords` | 6 | No theorem names it | `exactWords q = some s → readNumber s = some q` with the reader above, and `exactWords q = none ↔ q < 0 ∨ ∀ k < 41, (q * 10 ^ k).den ≠ 1` |
| `VE/Calc/Render.lean` | `reservedWords` | 5 | A table: its value is spec 11.2's list, and no theorem names it | None of its own: a theorem could name it only by restating the list, and an equation with another copy (ME-2's) would move the trust, not lower it. The `valueWordsOk` theorem above fixes its effect |
| `VE/Calc/Render.lean` | `exprDepth` | 5 | No theorem names it. Its only reader is `renderExpr`'s guard (depth over 2 gives `none`), so it can only withhold a line | `exprDepth e ≤ 2 ↔` 11.2's nesting rule for `e` (at most one phrase inside another), with that rule as ME-11's predicate. An equation with its own definition would be vacuous |
| `VE/Calc/Render.lean` | `phraseWords` | 4 | A table, as `reservedWords` | None of its own, as `reservedWords`; the `valueWordsOk` theorem fixes its effect |

Every one of these needs ME-11's reader (or ME-2's predicates) first, so this pass leaves the +113 for ME-11, which
spec 9 already gives `read_render`. One more note for the DRI, which is not a tie: the line is display only (it
decides no verdict), and `exprDepth` can only withhold a line, so a reclassification of some of these to [R] or [I]
would lower the count too. That is a classification question, not part of this pass, and nothing is reclassified here.

### Seeded ties (each restored after its run; the tree was clean afterwards)

Planted and restored by [`evidence/ties/seed_tie.py`](evidence/ties/seed_tie.py) (run from the checkout's root); outputs
in `evidence/ties/seed-*.txt`, summary in [`evidence/ties/seeded-ties.json`](evidence/ties/seeded-ties.json).

| Seed | Temporary change | `python3 tools/trust_map.py --check` |
| --- | --- | --- |
| S1 | `renderClaim` tied to an unrelated theorem, `VE.Calc.Claim.decide_holds` (`tools/trust-classes.json`) | exit 1: "VE.Calc.English.renderClaim: the statement of VE.Calc.Claim.decide_holds does not mention VE.Calc.English.renderClaim of VE.Calc.Render". `tests/test_trust_ratchet.py::test_committed_budget_passes_its_check` fails too |
| S2 | An existing tie's `-- uses` line broken: `VE.Calc.values@VE.Calc.Decls` removed from `VE.Calc.values_stated` (`lean/statements.txt`; me-1b's tie, the one tie in `VE.Calc`) | exit 1: "VE.Calc.values: the statement of VE.Calc.values_stated does not mention VE.Calc.values of VE.Calc.Decls" |
| S3 | `renderClaim` tied to spec 9's `VE.Calc.English.read_render`, which no Lean file states | exit 1: "VE.Calc.English.renderClaim: tying theorem VE.Calc.English.read_render is not in statements.txt" |

The control is the unseeded tree: its five existing `VE.Calc.values` ties validate and `--check` passes, so each
failure above comes from the seed.
