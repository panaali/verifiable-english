No DRI signature is needed: trust growth K +0, S +6, V +0 is signed by standing ruling R16; no DELTA row reserves
one. me-5 delivers the fact-level half of ME-5; the rest is **me-5b** (below). Size: 689 changed lines before this
report and 791 with it (`git diff --numstat`, generated files excluded), over the ~600 cap (Deviations, below).

# me-5 report: derivations over rational unknowns, at the level of facts

Base `b7613541c`; commits `git log --oneline --no-merges main..HEAD`. No Python, Rust or public output changes.
Statement gate: ME-S passed (manage-agents math-evidence-p3ver2.final.md: PASS). The four 3.4 theorems built here
(`Farkas.check_sound`, `lt_of_sq_lt`, `Derivation.check_sound`, `Counterexample.check_sound`) and `QFact.negate_holds`
have spec 5's statements unchanged. `QLin`, `QFact`, `Farkas.check`, `Step`, `Derivation` and `counterexampleCheck`
match spec 5's text; the only additions are `deriving DecidableEq` (the square step tests membership) and a
`Decidable` instance for `QFact.Holds`. No J3 clause is built here, so none was changed.

## Plan rows (ME-5)

| Plan row | Delivered |
|---|---|
| `lean/VE/Calc/{Linear,FourierMotzkin,Derive}.lean` | yes; fixtures in `lean/VE/Calc/DeriveExamples.lean` (T, as ME-1's `Examples.lean`) |
| Proves 3.4 | yes: the four theorems above, `lean/audit.py` PASS |
| Fourier-Motzkin with multiplier tracking within 64 facts, 16 unknowns, 10,000 steps; replayed by `Farkas.check`; counterexamples checked by evaluation | yes (`FM.search`, `Derive.search`); the budget applies to each search and is counted before combinations are built. Answers are replayed (`Derivation.check`) or checked (`counterexampleCheck`): the fixtures do this today, and me-5b's runner will through `follows_of_check` / `counterexample_of_check` |
| Square rule across a link, the claimed bound tried first | yes (`squareSteps`, `boundCandidate`, `FM.upperBound`) |
| Fixtures H-6, H-6p, H-6n; no-solution system and its certificate; forged negative-weight certificate; s = 0, r = 1 (A2) | yes, over facts: `DeriveExamples.lean` 28-33 (H-6), 36-38 (H-6p), 41-42 (H-6n), 46-50 (A2), 54-60 (no solution), 64-69 (forged) |
| R-3, R-4 | the Lean answers only: R-3's certificate (weights 1, 0, 1, 2/5, then the square step with a = 1/20, b = 1/4) and R-4's counterexample (r = 1/5, s = 1/25, d = 2/125) are reproduced exactly (lines 28, 41). The request and answer JSON need ME-2's wire: me-5b |
| R-10a | not built: it waits for ME-4 (task) |
| Seeded bug: `Farkas.check` accepts a negative weight | mutant 1: guards 67-68 fail |
| `follows` check, `premises`, lowering (`Expr.inline`, `Claim.facts`), `Follows` and its bridge theorems, the `follows` clauses of `Check.OutcomeMeans`, the J10 two-premise rendering, `tests/test_calc_derive.py` | **not built: me-5b** |

## Deviations

- **Cut for size.** The fact-level checkers, the search and their fixtures took 623 lines (code, fixtures, side table)
  before any lowering. The lowering with `Expr.inline`'s five fault theorems, `Follows` and the runner would add an
  estimated 300 or more, so they go to me-5b. The task says this item builds `Expr.inline` for me-9. It does not:
  me-9 must wait for me-5b, or build it itself (spec 2.7: "built by whichever of ME-5, ME-8 and ME-9 lands first").
- **No `Check` yet.** `Check` and `Check.OutcomeMeans` are ME-2's, which is not on main. me-5b should write the
  `follows` clauses (spec 3.4, lines 843-844, 849-850) as one definition that ME-2's `Check.OutcomeMeans` reuses
  unchanged, rather than a second copy.
- **No fact-level runner.** A `Derive.run` with its own soundness theorems was written, then removed: me-5b's runner
  must replay through the lowering anyway, so it would have been a second copy of that check.
- `QLin` and `QFact` are class C, as `VE.Order.Lin` is; their meaning, `QLin.eval` and `QFact.Holds`, is S.

## Trust

`trust_map.py --check` on the final code: K +0, S +6, untied V +0, trusted +6 (Linear.lean: `QLin.eval` 1,
`QFact.Holds` 3; Derive.lean: `Answer.point` 2); G[R] +4 (`FM.maxFacts`, `maxUnknowns`, `maxSteps`); everything else C,
P or T. Recorded with `--allow` and signed under R16. The FOLLOW-UPS.md "## me-5" row asks for the ties pass and
names me-5b.

## Seeded bugs (Lean; [`mutants.json`](mutants.json), 25 mutants, each with its exact edit)

Each mutant is run twice: as written, and with every theorem's proof replaced by `sorry`, so that only the `#guard`s
in `lean/VE/Calc/DeriveExamples.lean` can catch it. All 25 fail some guard in the second run, and were restored.
- Trusted definitions: `QLin.eval` drops its constant (5); `QFact.Holds` swaps < and ≤ (6); `Answer.point`
  defaults to 2 (8).
- `Farkas.check`: negative weight (1, the plan's seeded bug), no cancellation (2), zero constant without a strict
  fact (3), weight count (4). `QFact.negate` keeps strictness (7).
- `Step.derive`: no link (9), no a ≤ b² (10), no established bound (11). `Derivation.check` reads the first fact
  (12). `replay` drops derived facts (13). `counterexampleCheck`: no link equation (14, debate A2), no nonnegativity
  (15), no premises (16).
- Search: bound not tried (17), loose bound (18), no linear refutation (19), strictness lost (20), weights not
  tracked (21), 17 unknowns (22), back-substitution off by one (23), `upperBound` keeps the loosest (24), 1,000
  steps (25).

## Tests

`select_tests.py --base b7613541c --run` (mac-pytest, VM fallback): 65 units, 2 failed, both because the R16 allowance
was not yet recorded (`test_trust_budget.py::test_trust_map_check_passes_on_the_live_tree`,
`test_trust_ratchet.py::test_committed_budget_passes_its_check`). After recording it, those files and the inventory
tests pass (171 passed: trust, frozen sources, audit record, repo map). `regen_generated.py --check --skip route-cases`
passes 30 entries; route-cases needs the Rust binary, which this worktree lacks, and this item does not change it.
`gate_collection.py --check --prebuilt`: 0 added, 0 removed, 0 refused. Full gate: left to the chain. No test failed
that main-known-red.txt lists.

## Pilot bytes

0 expected (plan: "Bytes: 0"); nothing is claimed before a pilot audit.

## Next item

**me-5b**: `freeNames`, `assign`, `assign_wellFormed`; `Expr.inline` and `Claim.inline` with their five theorems
(2.7; first, for me-9); `Claim.facts` and `facts_sound`; `Follows`, `HasCounterexample`,
`not_follows_of_counterexample`, `follows_of_check`, `counterexample_of_check`; the `follows` clauses (J3) and runner;
R-3 and R-4 as cases; `tests/test_calc_derive.py` once a relay exists. R-10a after ME-4. Then me-9.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer is relayed; no mode or schema.
2. PASS: plan rows above, each delivered or moved to me-5b by the size rule; `git diff main...HEAD` has no Python
   copy of a Lean decision, no report test, and no file that an in-flight branch edits except the union and
   generated files (`lean/VE.lean`, `Audit.lean`, `trust-classes.json`).
3. PASS: 25 seeded bugs, each failing a named `#guard` with the proofs sorried (`mutants.json`).
4. N.A.: no Python or Rust counterpart exists for these checkers.
5. N.A.: no relayed field to bind (R8 arrives with me-5b and ME-3).
6. PASS: base from `git merge-base`; commits listed from `main..HEAD --no-merges`; full gate on the final HEAD by the chain.
7. PASS: DELTA rows 1-2 cite R16; `trust_map.py --check` PASS.
8. PASS: DELTA "Public output: none" (no mode, command, route or Python/Rust file).
9. PASS: the selection includes `lake build`, which runs `DeriveExamples.lean`, the file every mutant breaks.
10. PASS: `lean/audit.py` PASS; the statements are spec 5's verbatim; mutants 1-7 and 9-16 also break a proof as written
    (`proofs_failing_as_is` in `mutants.json`).
11. PASS: 17 unknowns and 261,888 steps give `unknown (limit derivationSteps)`, never a verdict (guards 92-93).
12. PASS: the step budget is counted before any combination is built (`FM.eliminate`); the first elimination's
    count is pinned at 1,024 (guard 91), and the whole fixture file checks in about 3 s.
13. PASS: no test removed; `gate_collection.py --check --prebuilt` reports 0 stale and 0 malformed trailers.
