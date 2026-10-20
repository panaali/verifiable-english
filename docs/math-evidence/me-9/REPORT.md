No DRI signature is needed: trust growth K +0, S +3, V +0 is signed by standing ruling R16; no DELTA row reserves
one. me-9 delivers the normaliser half of ME-9; the rest is **me-9b** (below). Size: 609 changed lines before this
report (`git diff --numstat`, generated files excluded), about 690 with it.

# me-9 report: algebraic identities, the normaliser

Base `2f633d7b5`; commits `git log --oneline --no-merges main..HEAD`. No Python product code, Rust or public output
changes. Statement gate: ME-S passed (manage-agents math-evidence-p3ver2.final.md: PASS). Plan 3.8's three theorems
(`Poly.ofExpr_sound`, `Frac.ofExpr_sound`, `identity_sound`) and spec 8.2's `differsAt_sound` have the reviewed
statements unchanged, and `Mono`, `Poly`, `Poly.eval` and `differsAt` have the spec's text (compared after collapsing
whitespace). No statement had to change.

## Plan rows (ME-9)

| Plan row | Delivered |
|---|---|
| New files `lean/VE/Calc/Poly.lean`, `tests/test_calc_algebra.py` | yes; the test states fixtures, and Lean prints each answer (as me-6's `test_calc_dimensions.py`) |
| Proves 3.8 | yes: the three theorems above, `lean/audit.py` PASS |
| ... over sides inlined with the free values kept, against `IsIdentity` (J3) | **me-9b**: `Expr.inline` is not on main (me-5's report moved it to me-5b, which has not started), so me-9 built it. It and `IsIdentity`, `NotIdentity`, `isIdentity_of_check`, `notIdentity_of_differsAt` and the runner were then cut for size (Deviations) |
| H-1, H-2, H-3 | yes, over free D, V, v: `test_fixture[h1]`, `[h2]`, `[h3]` (identity); `[h1-at-v]`: at V = v the left side denotes nothing; `[h1-point]`: both sides 33/4 at (11, 3, 1) |
| H-4 with D free | **me-9b**: its `sq` is a stated value, so the fixture is about inlining |
| R-6 | the false half, over expressions: `[binom]` not shown, `[binom-point]` a = b = 1 with sides 4 and 2. R-6's named sides (`round_trip`, `closed_form`) need inlining: **me-9b**, with the request and answer JSON after ME-2 |
| R-10c | not built: it waits for ME-4 (task) |
| A division by an expression that can be zero denotes nothing at that point | yes: `[cancel]` (x/(x − 1)·(x − 1) = x is an identity), `[cancel-at-1]` and `[recip-at-1]` (no value at x = 1, so no point there), `[recip-at-3]` (1/(x − 1) = 1 fails at 3) |
| Seeded bug: monomials merged wrongly, "(a + b)² = a² + b²" reported an identity, its regression fails | mutant 1: `[binom]` and `[binom-compare]` fail. The plan's literal edit, merging different variable lists (mutant 2), gives 4ab-type and 2a²-type single terms, which still differ, so it fails the normal-form fixtures instead (`[binom-form]`, `[distinct-terms]`, …) |
| Bytes: 0 | 0 expected; nothing is claimed before a pilot audit |

## Deviations

- **Cut for size.** Inlining (spec 2.7) with its theorems, the meaning layer and the runner took 340 more lines. Built
  on top of the normaliser, the item reached about 1,050 lines with fixtures and docs. They are proved and kept on the
  local branch `wip/me-9b` (commits `ca4dc16ae`, `10819663b`), so me-9b starts from them. The manage-agents
  FOLLOW-UPS.md "## me-9" row lists what is there and what is still to write.
- **Limits.** Spec 3.2 gives one limit, 10,000 terms. The normaliser checks it before it does the work: at most
  10,000 nodes in a side, counted without walking past the 10,000th; at most 10,000 terms in a sum, or in a product
  before like terms merge. Each limit is pinned at its value and one past it: `[nodes-10000]`/`[nodes-10001]`,
  `[nodes-10001-pow]`, `[sum-10000]`/`[sum-10001]` and `[product-10000]`/`[product-10100]`. Two bounds keep
  coefficients and exponents in budget, since a chain of powers otherwise grows without limit:
  - a coefficient below `10 ^ maxDigits`: ME-1's digit limit, pinned by `[digits-4096]`/`[digits-4097]`;
  - exponents at most 4,096: `[exponent-4096]`, `[exponent-4097]` and `[exponent-4097-product]`.

  Past any of these, `Identity.compare` is `none` and `identityCheck` is false (`[over-the-limit-is-not-an-identity]`).
  Which reason me-9b's runner shows for the coefficient and exponent bounds is open (FOLLOW-UPS).
- **Cost.** `Small` builds every coefficient's digit list; checking each intermediate coefficient that way took 10 s for
  one fixture. A comparison with the cached `10 ^ maxDigits` takes 4 s for the whole file. `Poly.combine` is
  tail-recursive: the first version overflowed the Mac runner's stack on the 10,000-term product.
  `[nodes-shared]` is a side that shares itself (2⁴¹ − 1 nodes as a tree). It ends at the node limit; without the
  limit (mutant 22) the fixture file does not return.

## Trust

`trust_map.py --check` on the final code: K +0, S +3 (`Poly.eval`), untied V +0, trusted +3; G[R] +8 (`maxPolyTerms`,
`maxPolyExponent`, `Poly.coeffBound`); everything else C or P (`vprod`, `Frac.Means`). Recorded with `--allow`, signed
under R16; DELTA row 1. The FOLLOW-UPS.md "## me-9" row asks for the ties pass.

## Seeded bugs (Lean; [`mutants.json`](mutants.json), 22 mutants, each with its exact edit)

Each mutant is run twice, from `lean/VE/Calc/Poly.lean`: as written, and with every theorem proved by `sorry`. With
the proofs sorried, only `tests/test_calc_algebra.py` can catch it. Every one fails named fixtures and was restored;
`proofs_failing_as_is` records whether the proofs also break as written (12 of 22).
- Trusted definition `Poly.eval`: the coefficient dropped (3), killed by `[binom-value]`.
- Normal forms: the plan's seeded bug (1), different variable lists merged (2), zeros kept (4), exponents multiplied
  (5), variables out of order (6), monomials in descending order (7).
- Fractions: division keeps the divisor's denominator (8), no common denominator (9), subtraction adds (10), no
  cross-multiplication (11), division accepted by `Poly.ofExpr?` (12). `differsAt` reports equal sides (13).
- Limits: 9,999 and 10,001 terms (14, 15), `<` for `≤` in sums and products (16, 17), a power node not counted (18),
  4,097 digits (19), exponent limit 4,095 (20), an exponent past the limit kept by `fits` (21), the node limit not
  checked (22).

## Tests

- **Selected tests:** `select_tests.py --base 2f633d7b5 --run` on the Mac runner: 78 units, 0 failed (HEAD
  `cf5e2bae2`). Earlier, at `480daf7b1`, it failed `tests/test_calc_algebra.py` (the stack overflow above); it was
  fixed in `8c6402d24`, and that file passes on Linux and on the Mac.
- **Generated files and audits:** `regen_generated.py --check --skip route-cases`: 30 entries pass. Route cases need
  the Rust binary, and this item does not change them. `repo_map.py --check` passes, as does `lean/audit.py`.
- **Collection:** `gate_collection.py --check --prebuilt`: 39 added, 0 removed, 0 refused, 0 stale, 0 malformed.
- **Full gate:** left to the chain. No test that main-known-red.txt lists failed.

Shared files: `lean/VE.lean`, `tools/trust-classes.json` and `docs/trust-baseline.json` are the union and registry
files that ap-1a, ar-10a and sc-1ab also append to. `lean/CALC.md` is edited elsewhere only by the stale
`foundation/me-1`, which me-1a/b/c superseded.

## Next item

**me-9b**:
- take `Inline.lean` and the meaning layer and runner from `wip/me-9b`;
- add `assign_wellFormed`, `Expr.inline_tooLarge`, `Claim.inline` and `Claim.inline_sound`; me-5b needs the same
  lowering, so whichever lands first owns it;
- R-6 and H-4 through named and stated values, and the undefined and unknown rows;
- the reason text for the coefficient and exponent bounds;
- a fixture that the names a side reads are listed only after the normaliser has accepted it.

R-10c after ME-4. Then ME-7.

## Sibling lessons (me-5 review)

- F1, limits unpinned: every limit here is pinned at its value and one past it (Deviations); mutants 14 to 22 move
  each one.
- F2, a run-out shown as an inconclusive answer: past a limit the answer is `none` from `Identity.compare`, never
  "not an identity" from it; `identityCheck` is false, which no theorem reads as a refutation.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer is relayed; no mode or schema.
2. PASS: the plan rows above, each delivered or moved to me-9b by the size rule (R-10c by the task). `git diff
   main...HEAD` has no Python copy of a Lean decision (the test states expected strings; Lean prints answers) and no
   report test.
3. PASS: 22 seeded bugs, each failing named `tests/test_calc_algebra.py::test_fixture[...]` tests with the proofs
   sorried (`mutants.json`).
4. N.A.: no Python or Rust counterpart exists for the normaliser.
5. N.A.: no relayed field to bind; me-9b's runner rows bind later (ME-3).
6. PASS: base from `git merge-base`; commits from `main..HEAD --no-merges`; full gate on the final HEAD by the chain.
7. PASS: DELTA row 1 cites R16; `trust_map.py --check` PASS; FOLLOW-UPS row present.
8. PASS: DELTA "Public output: none" (no mode, command, route or Python/Rust product file).
9. PASS: the selection contained `tests/test_calc_algebra.py` and caught the Mac stack overflow at `480daf7b1`.
10. PASS: `lean/audit.py` PASS; the statements match the spec verbatim; 12 mutants also break a proof as written.
11. PASS: every limit is pinned at and past its value, and past it the answer is never an identity
    (`[over-the-limit-is-not-an-identity]`, `[nodes-10001]`, `[sum-10001]`, `[product-10100]`).
12. PASS: the node walk stops at the limit, so a shared side cannot cost its tree (`[nodes-shared]`, mutant 22). The
    coefficient bound is one comparison, and `combine` runs in constant stack (`[product-10000]` on the Mac).
13. PASS: no test removed; `gate_collection.py --check --prebuilt` reports 0 stale and 0 malformed trailers.
