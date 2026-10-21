No DRI signature is needed: trust K +0, S +0, V +0 (no allowance); DELTA row 1 cites R5. One deviation from the task's
wording: a run past the budget is reported as `limit .polyTerms` with the stop `.budget`, not `limit .evaluations`,
because `identityRun_unknown` (approved) and spec 3.4's `Check.UnknownCause` tie `limit .evaluations` to a read of an
exhausted counted value (Deviations). No approved statement changed.

# me-9c report: the identity runner's work budget (me-9 review F5)

Base `3432611041` (`git merge-base HEAD main`); commits `git log --oneline --no-merges main..HEAD`. Lean is the only
product language changed. Read first: me-9b's REPORT ("Next item", "Deviations").

**Statement gate.** ME-S passed (manage-agents math-evidence-p3ver2.final.md: PASS). `lean/statements.txt` only gains
lines: `IsIdentity`, `NotIdentity`, `isIdentity_of_check`, `notIdentity_of_differsAt`, `identityRun_holds`, `_fails`,
`_undefined`, `_unknown`, `differsAt`, `identityCheck` and the normaliser's theorems are unchanged; the runner's proofs
now go through `identityDecideB_outcome`.

## Delivered (task order)

| Row | Delivered | Test or proof |
|---|---|---|
| (1) a work budget for powers and `differsAt` (`Poly.lean`) | `charge`, `Budgeted.bin`; `Poly.pow?B` (each step charged before its product), `Frac.add?B`, `mul?B`, `div?B`, `pow?B`; `Expr.evalB` and `sidesAtB` (a node: a unit and the 64-bit words it reads, a power the words it writes, a value read a unit per 8 names of the point) | `Poly.pow?B_eq`, `Frac.pow?B_eq`, `Expr.evalB_eq`, `sidesAtB_eq`; `[budget-power-2048]`, `[budget-points]`, `[budget-cost-*]` |
| (2) the same for `Expr.zeroDivisor` (`Identity.lean`) | `Frac.goB`: the normaliser's pass finds the zero divisors itself, so nested divisors cost their nodes, not their square | `Frac.goB_eq`; `[budget-nested-divisors]`, `[budget-nested-zero-divisor]`, `[budget-cost-divisors]` |
| (3) answered rows unchanged, exhaustion only the unknown row | `identityDecideB` (the row within `n` units), `identityRun` with `VE.Limits.maxEvaluations` | `identityDecideB_eq` (the row is `identityDecide`'s or `budgetRow`), `identityDecideB_within`, `identityDecideB_exhausted`, `identityRun_exhausted`; `[budget-binom-*]`, `[budget-literal-*]` |
| (4) fixtures | F5's 400 `+ 0` over a 10,000-term side, a side at 9,999 nodes, nested divisors at the limit, H-1 to H-4 and R-6 unchanged, exact charges, R5's boundaries | `BUDGET_FIXTURES` in `tests/test_calc_algebra.py` (29) |

Time in `lake env lean` (interpreted, VM), before (unbudgeted `identityDecide`) and after: F5's 400 `+ 0` over
`four`, 60 s (review) / 3.0 s; the same at 9,999 nodes, about 24 min (review) / 2.9 s; `(x + 1)^2048`, 49 s / 3.1 s;
1/(1/(… x)) with 4,998 divisions, 133 s / 0.14 s (now `holds` at once); 13 points over 2,401 names, 17 s / 2.2 s; a
product of 4,900 names to the 4,096th times `roots`, 246 s / 2.5 s. One unit costs about 3 to 5 µs there, so a row
stops within about 5 s; the compiled service is faster. All but the nested divisors end in `budgetRow`.

## Deviations

- **The budget's unknown reason.** `identityRun_unknown` states `u = .limit .evaluations → ∃ e ∈ [a, b],
  e.ReadsExhausted ds`, as `Check.UnknownCause` does for every kind but claims; a normaliser that runs out reads no
  exhausted counted value, so reporting `limit .evaluations` would make that approved statement false. As for me-9b's
  F4 stops, the outcome stays `limit .polyTerms` (the normaliser's reason, which spec 3.4 allows an identity) and the
  row carries `stop := some .budget`, whose text is spec 1.5's budget text, `(UnknownReason.limit .evaluations).text
  maxEvaluations`. The point search ends the same way. Nothing shows a row yet; the wording is ME-2's DRI decision
  (FOLLOW-UPS "## me-9b", F2).
- **`Expr.zeroDivisor` reads `Frac.go`,** not `Frac.ofExpr?`: it is read only on a side the normaliser accepted, so its
  divisors are within the node limit and the two agree; `Frac.goB_eq` states it against the pass.
- **`Poly.powWithin`** now holds the exponent check that `Poly.pow?` and `Poly.pow?B` share (the limit table names it).
- **Not charged:** inlining (me-5b's `Expr.inline`) and the filter of the names a side reads (at most 512 × 20,000
  comparisons by the decoder's limits; the list is now built once, not once per kept name: 9 s to 2 s above).

## Trust

`trust_map.py --check` on the final code: K +0, S +0, untied V +0, trusted +0; G +1 (`IdentityStop.text`'s budget line,
G[R]). The 20 new definitions are C in `tools/trust-classes.json`. No new trusted definition, so no R16 allowance,
FOLLOW-UPS row or `trust_mutants.py` run.

## Seeded bugs (Lean; [`mutants.json`](mutants.json), 22)

One per budget charge and one per new definition, each with its exact edit, built as written; the 6 that break a
proof as written were run with the budget theorems cut to a stub. Each ran under `timeout 600` against every fixture
of `tests/test_calc_algebra.py` but the four heavy ones, then restored. Each fails named fixtures:
- budgets not decremented: a power's steps (1), sums (2), products (3), quotients, the zero-divisor pass (4), the
  cross products (18), evaluated operations (11), values read (12), the point search (19). Run against the F5 fixtures
  themselves, 1 fails `[budget-power-2048]`, 2 `[budget-f5-zeros]`, 12 `[budget-points]` (each answers unbudgeted);
- the charges: a power's denominator (5), `Poly.size` (6), `Poly.mulCost` (7), `charge`'s bound (8), `ratWords` (10),
  a power's words (13), a point's names (14), a leaf (17);
- the answers: an undefined operand as exhaustion (9), `Poly.powWithin` (15), the pass's zero divisors (16: the F3
  fixtures), `budgetRow` as `holds` (20), the point search past the budget as `identityNotShown` (21), its text (22).

## Tests

- **Selected:** `mac-pytest.sh --select -- --base 3432611041 --run` on ve-mac-1 at `b95312fc`: 79 units, 0 failed
  (`tests/test_calc_algebra.py` among them). `tests/test_calc_algebra.py` on the final code: 392 passed.
- `lake build`, `lean/audit.py --check`, `regen_generated.py --write --skip route-cases` (route cases need the Rust
  binary and are unchanged), `trust_map.py --check`; `gate_collection.py --check --prebuilt`: 28 added, 0 refused,
  0 stale, 0 malformed. Full gate: left to the chain.

Shared files: `tools/trust-classes.json` (registry). No branch in flight edits `Poly.lean`, `Identity.lean`,
`tests/test_calc_algebra.py` or `lean/CALC.md`'s identity sections.

**Bytes:** 0 expected; nothing is claimed before a pilot audit.

## Next item

R-10c after ME-4, then ME-7. me-2b may now wire `identityRun` to the `calc` mode; its row must show
`IdentityRow.reason` (the stops, the budget's among them).

## Sibling lessons (me-5b review)

F1, constant arithmetic past the node guard: every polynomial the budgeted pass builds passes `Poly.guard`, and an
evaluated power is charged its result's words before it is computed; `[budget-power-tower]`: `((2⁶⁴)⁶⁴)⁶⁴` stops at
the digit limit (`form`).

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer is relayed; no mode or schema.
2. PASS: the task's rows above with their tests; no Python copy of a Lean decision (the fixtures state expected
   strings), no report test, no file an in-flight branch edits.
3. PASS: 22 seeded bugs (`mutants.json`), each failing named `test_fixture[...]`s; no new trusted definition for
   `trust_mutants.py`.
4. N.A.: no Python or Rust counterpart of the runner.
5. N.A.: nothing relayed to bind.
6. PASS: base from `git merge-base`, commits from `main..HEAD --no-merges`; the full gate on the final HEAD by the chain.
7. PASS: DELTA row 1 cites R5 with its tests; trust +0.
8. PASS: DELTA "Public output: none"; the unserved row's one change is row 1.
9. PASS: the selection contained `tests/test_calc_algebra.py`, which every seeded bug fails.
10. PASS: the `_eq` theorems are about the returned row (`identityDecideB_eq` on `identityDecideB`'s value); 6 seeded
    bugs break a proof as written (`proofs_failing_as_is`); `lean/audit.py --check` PASS.
11. PASS: budget 0 is the unknown row (`[budget-binom-0]`, `[budget-literal-0]`), never a verdict
    (`identityRun_exhausted`); no timing in the tests.
12. PASS: step counts, not time, pin the cost (`[budget-cost-*]`, exact units); the quadratic zero-divisor walk is gone
    (`[budget-cost-divisors]`, `[budget-nested-divisors]`).
13. PASS: no test removed; `gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed.
