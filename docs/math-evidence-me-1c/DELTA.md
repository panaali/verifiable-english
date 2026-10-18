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

`lean/VE/Calc/Examples.lean` adds no trusted line (its helpers are T). Two of its new checks close me-1b review
F1 and F2 (C): `Small` at minus the limit and a decided claim on a negative value (138, 141), and a finished
count that is not exhausted (`example` 304-314); seeded bugs 14-15 (in `Decls.lean`, which this item does not
change) show each one fails.
