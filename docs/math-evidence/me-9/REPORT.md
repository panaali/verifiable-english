No DRI signature is needed: trust growth K +0, S +3, V +0 is signed by standing ruling R16; no DELTA row reserves
one. me-9 delivers the normaliser half of ME-9; the rest is **me-9b** (below). Size: 939 changed lines before this
report (`git diff --numstat`, the generated files of `regen_generated.py --list` excluded), 1,169 with it; recheck 2's
class fix (the limit table, its theorems and 77 more mutants) added 320 of them, `mutants.json` 105 in all.

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
  before like terms merge. Two bounds keep coefficients and exponents in budget, since a chain of powers otherwise
  grows without limit: a numerator and a denominator below `10 ^ maxDigits` (ME-1's digit limit), and exponents at most
  4,096, in a result (`fits`) and in a power node (`pow?`). Every polynomial built passes `Poly.guard`, a literal too
  (recheck F9), and `Poly.ofExpr?` looks for division only after the limits passed (hunt 1).

  **One condition gives an answer.** `Frac.ofExpr_within`, `Poly.ofExpr_within` and `Identity.compare_within` prove it:
  an answer other than `none` comes only when the side has at most 10,000 nodes and every polynomial on the way,
  the cross products included, is `Within` (`fits`, and at most 10,000 terms). Every other case is `none`, and each
  refused case has a fixture one past its limit (the table below). `fits` does not count terms: `add?` and `mul?` count
  them first, and `Poly.length_norm` proves that `norm` never adds one (review F1 deleted the unreachable check).

  Past any limit `Identity.compare` is `none` and `identityCheck` is false (`[over-the-limit-is-not-an-identity]`).
  Which reason me-9b's runner shows for the coefficient and exponent bounds is open (FOLLOW-UPS).
- **Cost.** `Small` builds every coefficient's digit list; checking each intermediate coefficient that way took 10 s for
  one fixture. A comparison with the cached `10 ^ maxDigits` takes 4 s for the whole file. `Poly.combine` is
  tail-recursive: the first version overflowed the Mac runner's stack on the 10,000-term product.
  `test_a_shared_side_costs_only_the_limit[nodes-shared-41]` is a side that shares itself (2⁴¹ − 1 nodes as a tree).
  It ends at the node limit; without the limit (mutant 22) it does not return, so it runs in its own process and fails
  alone. `[poly-shared-41]` is the same side through `Poly.ofExpr?`, and `[power-10^12]` a power refused before its
  steps.

## Trust

`trust_map.py --check` on the final code: K +0, S +3 (`Poly.eval`), untied V +0, trusted +3; G[R] +9 (`maxPolyTerms`,
`maxPolyExponent`, `Poly.coeffBound`); everything else C or P (`vprod`, `Frac.Means`, `Poly.Within`; the limit theorems
are P). Recorded with `--allow`, signed
under R16; DELTA row 1. The FOLLOW-UPS.md "## me-9" row asks for the ties pass.

## Limit truth table (recheck 2: the class of F1, F6 and F8)

Every definition of `Poly.lean` whose value reads a limit constant is a row here: Lean's environment lists them, and
`test_every_limit_check_is_pinned_at_and_past_it` fails if one is missing from the test's `LIMIT_CHECKS` or has no
fixture at and past its limit. Fixtures are `tests/test_calc_algebra.py::test_fixture[...]`, generated from one table
(`LIMITS`, `digit_rows`). A one-sided row gives `form` (`Frac.ofExpr?` answers or not) and `-compare` (the side
compared with itself); a two-sided row gives the comparison and `-form`; every row past its limit gives `-swapped` (the
side compared second). At the limit the answer is `true`/`some true`; one past it, `false`/`none`.

| Check (declaration) | At the limit | One past it | Mutants, each failing only this row's fixtures |
|---|---|---|---|
| Nodes in a side: `nodesWithin maxPolyTerms` (`Frac.ofExpr?`) | `nodes-10000`, and with a `sub`, `mul`, `div` node or a literal last: `nodes-10000-{sub,mul,div,lit}` | `nodes-10001`, `-pow`, `-right`, `-{sub,mul,div,lit}`, `nodes-shared` (2¹⁵ − 1 as a tree); own processes: `nodes-shared-41`, `poly-shared-41` | 27 (+1), 28 (+99), 29 (`<`), 22 (not checked), 30 (a leaf free), 31 (a binary node free), 32, 33 (one operand not walked), 34 (the right operand given the node's fuel), 18 (a power node free), 64 to 73 (each node kind and leaf free or counted twice), 99, 100 (one side of `compare` not checked), 89 (division looked for first) |
| Terms in a sum: `p.length + q.length ≤ maxPolyTerms` (`Poly.add?`) | `sum-10000` | `sum-10001`, `sum-merged-10001` (10,000 after like terms merge), `add-cross-sum-10001` (`Frac.add?`'s cross products) | 16 (`<`), 35 (+1), 36 (+99), 37, 38 (one summand not counted), 90 (counted after merging), 76 (`Frac.add?`'s sum unguarded) |
| Terms in a product: `p.length * q.length ≤ maxPolyTerms` (`Poly.mul?`) | `product-10000`, `pow-10000`, `sum-10000-compare` (10,000 × 1) | `product-10001` (73 × 137, F8), `product-10100`, each with `-form`; every other product a fraction form takes: `add-cross-10001`, `add-cross-right-10001`, `add-den-10001`, `mul-den-10001`, `div-num-10001`, `div-den-10001`, `pow-10201` (10,001 cannot be reached by a power's step), `compare-cross-10001`, `compare-cross-right-10001`; within it, `product-by-zero` | 17 (`<`), 39 (+1), 40 (+99), 41, 42 (one factor not counted), 43 (`+` for `*`), 91 (counted after merging), 103 (the limit divided by a factor's terms), 77 to 82, 85 to 87 (one call site unguarded) |
| A power node's exponent: `k ≤ maxPolyExponent` (`Poly.pow?`) | `exponent-constant-4096` | `exponent-constant-4097`; own process: `power-10^12` | 44 (`<`), 24 (+1), 45 (+99), 101 (the numerator stepped without it); 102 (the denominator stepped without it) is equivalent: the numerator's guard refuses the same `k` first |
| Each variable's exponent: `·.2 ≤ maxPolyExponent` (`Poly.fits`) | `exponent-4096` (by products), `exponent-4096-two-vars` | `exponent-4097`, `-product`, `-middle-var` (x·y⁴⁰⁹⁷·z), `-middle-term` (the middle monomial of four), `pow-num-4097`, `pow-den-4097` (x^(17·241)) | 46 (`<`), 21 (+1), 47 (+99), 48 (the first variable only), 49 (the first monomial only), 74 (the total degree), 83 to 85 (a power unguarded) |
| Numerator: `num.natAbs < 10 ^ maxDigits` (`Poly.fits`) | for each sign, 10⁴⁰⁹⁶ − 1 as a literal, a product and a middle monomial: `digits-[neg-]4096`, `-product`, `-middle-term`; `digits-[neg-]both-4096` (4,096 digits above and below the line) | for each sign, 10⁴⁰⁹⁶ as a literal, a product, a sum and a middle monomial: `digits-[neg-]4097-literal`, `digits-[neg-]4097`, `-sum`, `-middle-term` | 50 (`≤`), 51 (+99), 52 (one short), 26 (`natAbs` dropped, F6), 53 (not checked), 54 (`\|\|` for `&&`), 92, 93 (the first or last monomial only), 94 (constant monomials only), 98 (`natAbs` for constants only), 75 (numerator × denominator), 61 (a literal unguarded, F9), 62, 63 (a sum or product unguarded) |
| Denominator: `den < 10 ^ maxDigits` (`Poly.fits`) | the same with `den-`: `digits-[neg-]den-4096`, `-product`, `-middle-term` | `digits-[neg-]den-4097-literal`, `digits-[neg-]den-4097` (F1), `-sum` ((2⁴⁰⁹⁶ + 5⁴⁰⁹⁶)/10⁴⁰⁹⁶), `-middle-term` | 55 (`≤`), 56 (+99), 57 (one short), 23 (not checked), 95, 96, 97 (first, last or constant monomials only), 75, 61 to 63 |
| The constants `maxPolyTerms`, `maxPolyExponent`, `Poly.coeffBound` | the rows above | the rows above | 14, 15 (9,999, 10,001), 20, 60 (4,095, 4,097), 19, 58, 59 (10⁴⁰⁹⁷, 10⁴⁰⁹⁶ ± 1) |

The size of each side placed at or past a limit is a fixture too (`size-*`: 9,999 nodes, 100, 73 and 137 terms,
`top` has 4,096 digits). `[same-denominator]` (two fractions over a 101-term denominator) is the one case inside the
limits that a path through cross products would refuse (mutant 88).

## Seeded bugs (Lean; [`mutants.json`](mutants.json), 103 mutants, each with its exact edit)

Each mutant was applied to `lean/VE/Calc/Poly.lean` as committed (`ea6cc898d`) and run against every fixture, with the
soundness and limit sections cut, so only `tests/test_calc_algebra.py` can catch it; the `SHARED` fixtures ran each
in its own process. `test` lists the fixtures it failed, and every one is its own row's (the table above; mutants 1 to
13 and 25 are not limit mutants). `proofs_failing_as_is` records whether the full file, theorems included, also
fails to compile (55 of 103): every mutant that skips a guard at one call site (76 to 89, 99 to 101) breaks
`Frac.go_within`, `Identity.compare_within` or a soundness proof. Mutant 102 is equivalent. Each run used
`timeout 600`; no `lean` process was left running. Mutants 80 and 82 timed out under the load of twelve parallel runs
and were rerun alone: each failed its one fixture. Mutant 103 and its fixture `[product-by-zero]` came last, and only
it ran against that fixture.
- Trusted definition `Poly.eval`: the coefficient dropped (3), killed by `[binom-value]`.
- Normal forms: the plan's seeded bug (1), different variable lists merged (2), zeros kept (4), exponents multiplied
  (5), variables out of order (6), monomials in descending order (7), a zero literal kept (25).
- Fractions: division keeps the divisor's denominator (8), no common denominator (9), subtraction adds (10), no
  cross-multiplication (11), division accepted by `Poly.ofExpr?` (12). `differsAt` reports equal sides (13).
- Limits: 14 to 24, 26 to 103, by row in the table above.

## Tests

- **Selected tests:** `select_tests.py --base 2f633d7b5 --run` on the Mac runner: 78 units, 0 failed (HEAD
  `cf5e2bae2`). Earlier, at `480daf7b1`, it failed `tests/test_calc_algebra.py` (the stack overflow above); it was
  fixed in `8c6402d24`, and that file passes on Linux and on the Mac. After the review fixes: 78 units, 0 failed on the
  Mac runner (HEAD `5d14eaa2`), and `tests/test_calc_algebra.py` 44 passed on Linux. After the recheck fixes: 78
  units, 0 failed on the Mac runner (HEAD `1b192f53`), and `tests/test_calc_algebra.py` 52 passed on Linux. After
  recheck 2: 78 units, 0 failed on the Mac runner (HEAD `97450f27`), and `tests/test_calc_algebra.py` 223 passed on
  Linux (about 2 minutes; the limit table is 219 fixtures in one Lean run, and 3 sides run in their own processes).
- **Generated files and audits:** `regen_generated.py --check --skip route-cases`: 30 entries pass. Route cases need
  the Rust binary, and this item does not change them. `repo_map.py --check` passes, as does `lean/audit.py`.
- **Collection:** `gate_collection.py --check --prebuilt`: 223 added, 0 removed, 0 refused, 0 stale, 0 malformed.
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
- a fixture that the names a side reads are listed only after the normaliser has accepted it;
- me-9 review F3: report `undefined` before `holds` when a side's denominator is identically zero (`Frac.ofExpr_sound`),
  with the review's four cases (`0/0 = 5`, `(x − x)/(x − x) = 5`, `1/0 = 2/0`, `(a + b)² + 1/0 = a² + b² + 1/0`) as
  fixtures;
- me-9 review F4: the node limit refuses `sumx 5000` (one term) and counting a product before like terms merge
  refuses `(geo 100)²` (201 terms), so neither may be shown as "more than 10,000 terms";
- me-9 review F5: a work budget before the runner is wired (a side at the node limit over 10,000 terms costs minutes).
  Recheck 2's hunts found two more forms of it, outside the limit class: a power within the limits costs minutes
  (`Frac.ofExpr? ((x + 1)^2048)` took 73 s in the interpreter, a 4-node side), and `differsAt` evaluates with
  `Expr.eval`, with no limit at all (a 4,097-digit value, an exponent of 5,000, a shared side).

R-10c after ME-4. Then ME-7.

## Review fixes (me-9 review)

- **F1 (B)**, the denominator half of the digit bound unpinned: `[digits-den-4096]`/`[digits-den-4097]`, mutant 23.
  As a class, every comparison in a limit check now has a killing mutant: the sweep found the power node's exponent
  guard unpinned too (no fixture had a constant base, where only that guard refuses): `[exponent-constant-4096]`/
  `[exponent-constant-4097]`, mutant 24. `fits`'s term count, which no input reached, is deleted. The fixture file
  prints each answer on one line, so a wrong answer that prints over several lines fails its own fixture instead of
  the whole file's parse (mutant 23's first run).
- **F2 (C)**, a zero literal's normal form unpinned: `[zero-literal]`, mutant 25.
- **F3 to F5 (C)** are me-9b's (Next item).

## Review fixes (me-9 recheck 1)

- **F6 (B)**, the digit bound pinned on positive numerators only: with `natAbs` dropped from `fits`,
  `compare (−10^4096, −10^4096)` was an identity past the limit. As a class, the digit fixtures are now generated
  over both sides of the line and both signs (`DIGIT_FIXTURES`, now `digit_rows`), each at the limit, one past it, and past it compared
  with itself: `[digits-neg-4096]`, `[digits-neg-4097]` (the probe), `[digits-neg-4097-compare]` and the same for
  `den-` and `neg-den-`. Mutant 26 fails `[digits-neg-4097]` and `[digits-neg-4097-compare]` only. The sweep found
  no other signed bound: denominators, exponents, term and node counts are natural numbers.
- **F7 (C)**, the G count: `trust_map` measures G[R] +9, all in `Poly.lean` (Trust).

## Review fixes (me-9 recheck 2, and the acting DRI's note of 2026-10-20)

- **F8 (B)**, the product term limit tested at 10,000 and 10,100, not 10,001: `[product-10001]` (the probe, 73 × 137
  terms compared with its commuted self, `none`) and `[product-10001-form]`; mutants 39 (+1) and 40 (+99) fail them
  only. As the DRI's note asks, the class is fixed rather than this form: every limit check is a row of the truth
  table above, generated from one table and enumerated from Lean's environment, at its value and exactly one past it,
  with a mutant for each way of getting it wrong, each failing only its own row's fixtures. Three forms the table
  turned up before the hunts: `form` fixtures for products, since `compare`'s cross-multiplication re-checks the first
  factor (mutant 42 survived `[product-10001]` without them); the digit fixtures at 10⁴⁰⁹⁶ − 1 exactly (at 10⁴⁰⁹⁵, a
  bound one short, mutant 52, survived); and a variable or monomial past the limit in the middle (mutants 48, 49).
- **F9 (C, under the note's item 2)**, a bare literal skipped `fits`: a literal goes through `Poly.guard`, so
  `Poly.ofExpr? (lit 10^4096)` is `none` (`[digits-4097-literal]` and its `neg-`, `den-` forms; mutant 61). ME-1 is
  not relied on. The rule is inverted: `Frac.ofExpr_within`, `Poly.ofExpr_within` and `Identity.compare_within` name
  the one condition under which an answer is given (Deviations, Limits).
- **Claims:** "Limits" (Deviations) and checklist item 11 now say what the table shows.
- **Adversarial hunt** (two rounds, each one subagent given only the class, PROBEs F1, F6 and F8, and the code):
  - Hunt 1 tried 22 forms (each node kind and call site counted once) and returned 15 PROBEs: 14 surviving
    mutants, as it grouped them, and one real bug; a power of a zero base past its exponent is equivalent. Fixed: each node kind and leaf counted at and past the limit (A1, mutants 64
    to 73); each variable at the exponent limit (A2, total degree, 74); 4,096 digits above and below the line at once
    (A3, numerator × denominator, 75); every product, sum and power a fraction form takes, one past its limit (B,
    mutants 76 to 87; the build already caught them through the limit theorems); two fractions over one denominator
    (mutant 88); and a real bug: `Poly.ofExpr?` walked a shared side whole (`hasDiv`) before the node limit, now after
    it (`[poly-shared-41]`, mutant 89). Not of the class, left to F5 (Next item): `differsAt` has no limit.
  - Hunt 2 tried 9 forms; 8 survived the fixtures (3 of them broke the build), no real bug. Fixed: a sum counted after like terms merge
    (`[sum-merged-10001]`, mutant 90); the digit bounds checked on some monomials only, or `natAbs` on constant ones
    only (`digits-[neg-][den-]{4096,4097}-middle-term`, mutants 92 to 98); one side of `compare` without the node
    limit (`-swapped` for every row past its limit, mutants 99, 100); a power's numerator stepped without its exponent
    guard (`[power-10^12]`, mutant 101); a count that divides the limit by a factor's terms (`[product-by-zero]`,
    mutant 103). Not of the class, left to F5: a power within the limits costs minutes.
  - Open forms of the class: none. Mutant 102 (a power's denominator without its exponent guard) is equivalent.
- The DRI's note: DELTA row 1 stays under R16; no signature is reserved. Every mutant ran under `timeout 600`, and
  no `lean` process of this item is running.

## Sibling lessons (me-5 review)

- F1, limits unpinned: every limit check here is pinned at its value and one past it (Limit truth table). Fixing
  one form per round did not converge (review F1, rechecks F6 and F8); the table, enumerated from Lean's environment,
  and two adversarial hunts did.
- F2, a run-out shown as an inconclusive answer: past a limit the answer is `none` from `Identity.compare`, never
  "not an identity" from it; `identityCheck` is false, which no theorem reads as a refutation.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer is relayed; no mode or schema.
2. PASS: the plan rows above, each delivered or moved to me-9b by the size rule (R-10c by the task). `git diff
   main...HEAD` has no Python copy of a Lean decision (the test states expected strings; Lean prints answers) and no
   report test.
3. PASS: 103 seeded bugs; 102 fail named `tests/test_calc_algebra.py` fixtures with the proofs cut, each limit
   mutant only its own row's (`mutants.json`); one is equivalent.
4. N.A.: no Python or Rust counterpart exists for the normaliser.
5. N.A.: no relayed field to bind; me-9b's runner rows bind later (ME-3).
6. PASS: base from `git merge-base`; commits from `main..HEAD --no-merges`; full gate on the final HEAD by the chain.
7. PASS: DELTA row 1 cites R16; `trust_map.py --check` PASS; FOLLOW-UPS row present.
8. PASS: DELTA "Public output: none" (no mode, command, route or Python/Rust product file).
9. PASS: the selection contained `tests/test_calc_algebra.py` and caught the Mac stack overflow at `480daf7b1`.
10. PASS: `lean/audit.py` PASS; the statements match the spec verbatim (the limit theorems are new; plan 3.8's four
    are unchanged); 55 mutants also break a proof as written.
11. PASS: each limit check of the truth table (every definition that reads a limit, from Lean's environment) has
    fixtures at its value and exactly one past it, for each sign and side of the line where it has them, except a
    power's step, where 10,001 terms cannot be reached (10,000 and 10,201). Each listed mutant fails only its row's
    fixtures. Past a limit the answer is `none` (`-compare`, `-swapped`) and never an identity
    (`[over-the-limit-is-not-an-identity]`); the limit theorems prove no other answer is given.
12. PASS for the limits: the node walk stops at the limit, so a shared side cannot cost its tree
    (`[nodes-shared-41]`, `[poly-shared-41]`, mutants 22, 89), and a power past its exponent is refused before its steps
    (`[power-10^12]`). The coefficient bound is one comparison, and `combine` runs in constant stack. The work inside
    the limits is not budgeted yet (F5, me-9b).
13. PASS: no test removed; `gate_collection.py --check --prebuilt` reports 0 stale and 0 malformed trailers.
