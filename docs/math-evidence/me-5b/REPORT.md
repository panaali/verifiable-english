No DRI signature is needed: trust growth K +0, S +12, V +0 is signed by standing ruling R16; no DELTA row reserves
one. me-5b delivers the lowering half of what me-5 left: `Claim.facts`, `facts_sound`, `Follows`, `HasCounterexample`
and the three bridge theorems, with R-3 and R-4 proved over declarations. The `follows` check, its runner and the J3
clauses wait for ME-2's `Check`, which is not on main: they are **me-5c** (Next item). Size: 446 hand-written changed
lines before this report (`git diff --numstat`, generated files and the tool's `trust-mutants.json` excluded).

# me-5b report: the lowering of a derivation's claims and its meaning

Base `ca15b6d1c` (`git merge-base HEAD main`); commits `git log --oneline --no-merges main..HEAD`. No Python, Rust or
public output changes. Read first: me-5's REPORT ("Next item", "Deviations") and me-9b's REPORT, both on main.

**Statement gate.** ME-S passed (manage-agents math-evidence-p3ver2.final.md: PASS). After collapsing whitespace, these
equal spec 5 (main `c5197da78`) word for word: `Follows` and `HasCounterexample` (docstring, signature and body),
`not_follows_of_counterexample`, `Claim.facts`'s signature and docstring (without the spec's "*Opaque*:" marker, as
me-5 did for `Derivation.check`), `Claim.facts_sound`, `follows_of_check` and `counterexample_of_check`. Plan 3.4's
statements are me-5's and unchanged. No statement had to change.

## Delivered (task order)

| Row | Delivered | Test or proof |
|---|---|---|
| The lowering me-9b did not deliver | nothing left: me-9b delivered `freeNames`, `assign`, `assign_wellFormed`, `Expr.inline`, `Claim.inline` and their theorems; imported from `Inline.lean`, not copied. `freeNames_mem` (in `Identity.lean`, which `Lower.lean` must not import) moved unchanged to `Inline.lean`, beside `freeNames`, so both modules read one copy | `lake build` |
| `Claim.facts` and `facts_sound` | yes, `lean/VE/Calc/Lower.lean`: `Claim.inline` keeping `freeNames`, then `Expr.linear` (a product needs a constant factor, a divisor a nonzero constant, a power a constant base unless it is the 0th or 1st; a form is constant when its coefficients cancel, `QLin.isConst`) and `Claim.lower` (`eq`, `within` two facts; `lt`, `le`, `gt`, `ge` one; `rounds` none). Proved through `Expr.linear_sound`, `Claim.lower_sound` and `Claim.inline_sound` | `LowerExamples.lean` 58-59 (13.4's row: p1 at d = 2/125, s = 1/25 and at d = 1, s = 0), 65-69 (each comparison and `within` on both sides of its boundary, swapped, rounding refused), 78-79 (nine linear and six nonlinear shapes, at eight points against four constants), 86-88 (inlining: a stated value and a definition inlined; a missing name, an undefined and an exhausted counted value give none) |
| `Follows`, `HasCounterexample`, `not_follows_of_counterexample`, `follows_of_check`, `counterexample_of_check` | yes, `Lower.lean`; `mapM_facts` and `premises_iff` carry `facts_sound` across the premise list | `r3_follows`, `r4_not_follows` |
| R-3 and R-4 as cases | over declarations and claims (13.6's values, premises, link and conclusions): the lowered facts are me-5's fact fixtures `h6 (2/100)` and `below (1/4)` in 3.4's order (29-30); `Derive.search` gives R-3's certificate (32) and R-4's counterexample r = 1/5, s = 1/25, d = 2/125 (42); `r3_follows` proves `Follows` through `follows_of_check`, `r4_not_follows` proves `¬ Follows` through `counterexample_of_check`, each side condition decided by the kernel (`decide +kernel`, no axiom beyond the allowlist) | `LowerExamples.lean` 29-43; `lean/audit.py` PASS |
| The `follows` clauses (J3) and the runner | **me-5c**: me-2's `Check.OutcomeMeans` is not on main (`feature/me-2` is in flight), so no `Check` is introduced here | — |
| `tests/test_calc_derive.py` | **me-5c**: no relay exists | — |
| R-10a | waits for ME-4 (task) | — |

## Deviations

- **The runner and its JSON cases are me-5c.** R-3 and R-4 are built as Lean cases (declarations, premises, link,
  conclusion) and proved end to end; their request and answer JSON, the `follows` row, `NonlinearPremise` naming the
  term and the J10 rendering of each link as two numbered premises need ME-2's wire and `Check`.
- **`Claim.facts` gives none for an exhausted counted value too**, as for an undefined one: the spec's "reads a value
  that has none" names only the undefined case, but no fact can stand for a value whose budget ran out. Which of the
  two a premise hit is the runner's to report (`Expr.inline_error`, `inline_exhausted`), in me-5c.
- **A rounding claim lowers to none**: spec 5 lists `eq`, `within`, `lt`, `le`, `gt` and `ge` only.

## Trust

`trust_map.py --check` on the final code: K +0, S +12 (`Follows` 6, `HasCounterexample` 6), untied V +0;
`Expr.linear`, `QLin.isConst`, `QFact.sub`, `Claim.lower` and `Claim.facts` are C (each tied by a soundness theorem),
the fixtures T. Recorded with `--allow` and signed under R16 (DELTA row 1). The FOLLOW-UPS.md "## me-5b" row asks for
the ties pass and names me-5c.

**`tools/trust_mutants.py --max-mutants 1000`** ([`trust-mutants.json`](trust-mutants.json), allow file
[`trust-mutants-allow.json`](trust-mutants-allow.json); run on the VM, the Mac runner unreachable): 19 mutants, 0
killed, 0 survivors, 0 unknown, 19 allowed, exit 0. All 19 are of `Follows` and `HasCounterexample`, propositions over
every κ : String → Rat that no evaluated check can read (as me-9b allowed `IsIdentity`); each breaks the proofs named
in `mutants.json` 25 to 43.

## Seeded bugs (Lean; [`mutants.json`](mutants.json), 43, each with its exact edit)

Lean is the only product language changed. `/tmp` runner: each mutant applied to `lean/VE/Calc/Lower.lean`,
`lake build VE.Calc.LowerExamples`, the file restored; two controls (as written, and with the proofs cut) pass.
- Behaviours (1 to 24), each run with every proof of `Lower.lean` cut to `sorry`, so only the checks of
  `LowerExamples.lean` (`#guard`s and the kernel-decided side conditions of `r3_follows`, `r4_not_follows`) can
  catch them; each also breaks a proof as written. `Expr.linear`: a product of two forms (1), the right constant factor
  dropped (2), a zero divisor (3), a divisor not inverted (4), a non-constant divisor (5), the 0th power 0 (6), x²
  linear (7), a constant power multiplied (8), subtraction's sign (9), addition's right side (10), a name's
  coefficient (11), a literal's value (12). `QLin.isConst`: only an empty form (13), every form (14). `QFact.sub`
  swapped (15). `Claim.lower`: `eq` one fact (16), `lt` not strict (17), `le` strict (18), the swap ignored (19),
  `within`'s upper bound (20) or one fact (21), a rounding claim lowered (22). `Claim.facts`: no name kept (23), a
  fault giving facts (24).
- Survivors found, then fixed by fixtures: 5 (`x / (y + 1)`, a divisor with a nonzero constant term, 79), 6 and 8
  (the linear shapes are now checked at eight points against four constants, 78: x⁰ = 1 and 8x against 6x at x = 1/4).
- Trusted definitions (25 to 43): `trust_mutants.py`'s 19 operators on `Follows` (8) and `HasCounterexample` (11),
  run as written: each breaks `not_follows_of_counterexample` and `follows_of_check` or `counterexample_of_check`.

## Tests

- **Selected tests:** `select_tests.py --base ca15b6d1c --run` through mac-pytest (the Mac unreachable, run on the
  VM): 81 units; 80 exit 0 before the call's hour ran out, and the last, `tests/test_acts_vocab_mutants.py`, was rerun
  alone with `-n 6`: 643 passed. The selection's `lake build` and `lean/audit.py` steps passed.
- **Generated files and audits:** `regen_generated.py --write --skip route-cases` (route cases need the Rust binary;
  this item does not change them), then `--check`; `repo_map.py --check`, `check_lean_imports.py`, `lean/audit.py` and
  `trust_map.py --check` pass.
- **Collection:** `gate_collection.py --check --prebuilt`: 0 added, 0 removed, 0 refused, 0 stale, 0 malformed.
- **Full gate:** left to the chain. No test that main-known-red.txt lists failed.

Shared files: `lean/VE.lean` (union), `tools/trust-classes.json` and `docs/trust-baseline.json` (registries).
`feature/me-2` edits `Wire.lean`, `Run.lean`, `RunExamples.lean` and `Units.lean`, none of which this item touches; no
branch in flight edits `Inline.lean`, `Identity.lean`, `Lower.lean`, `LowerExamples.lean` or `lean/CALC.md`
(`foundation/me-1` lists `CALC.md` only against an old base).

**Bytes:** 0 expected (use-case ceilings); nothing is claimed before a pilot audit.

## Next item

- **me-5c** (after ME-2's `Check` lands): the `follows` check and the case's `premises`, the runner over
  `Claim.facts` and `Derive.search` with `follows_of_check` / `counterexample_of_check` for its outcomes,
  `NonlinearPremise`, the `follows` clauses of `Check.OutcomeMeans` (J3) naming `Follows` and `HasCounterexample`, the
  J10 rendering, R-3 and R-4 as JSON cases and `tests/test_calc_derive.py`. R-10a after ME-4.
- Then me-9's follow-ups (R-10c after ME-4), then ME-7.

## Sibling lessons (me-2 review)

- F1, hashed fields no fixture tells apart: no identity or hash here. The class in this item is a lowering whose
  parts no fixture separates; mutants 1 to 24 cover each branch, and the three survivors got fixtures.
- F2, checks tested on the refusing side only: each lowering rule has accepting and refusing fixtures (78 against 79;
  86-87 against 88; 65-67 against 69), and each comparison is checked on both sides of its boundary and at it.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer is relayed; no mode or schema.
2. PASS: the task's rows above, each with its fixture or proof, the runner and J3 clauses moved to me-5c because
   `Check` is not on main (the task's own rule); `git diff main...HEAD` has no Python copy of a Lean decision, no report
   test, no file an in-flight branch edits; the lowering is imported, not copied (`freeNames_mem` now has one copy).
3. PASS: 43 seeded bugs (`mutants.json`), behaviours failing `LowerExamples.lean` checks with the proofs cut;
   `trust_mutants.py` exit 0 with evidence and allow file.
4. N.A.: no Python or Rust counterpart exists for the lowering.
5. N.A.: no relayed field to bind (the `follows` row binds at me-5c and ME-3).
6. PASS: base from `git merge-base`; commits from `main..HEAD --no-merges`; full gate on the final HEAD by the chain.
7. PASS: DELTA row 1 cites R16; `trust_map.py --check` PASS; FOLLOW-UPS "## me-5b" row present.
8. PASS: DELTA "Public output: none" (no mode, command, route or Python/Rust file).
9. PASS: the selection contains `lake build`, which builds `LowerExamples.lean`, the file every mutant breaks.
10. PASS: statements equal spec 5 after whitespace normalisation; `lean/audit.py` PASS; `r3_follows` and
    `r4_not_follows` are about the lowered claims themselves; every seeded bug also breaks a proof as written.
11. N.A.: no budget or limit is added; the search's limits are me-5's, and `Claim.facts` stops at inlining's faults
    (88), never a verdict.
12. N.A. here, with a condition for me-5c: no public path reaches `Claim.facts`. Inlining is me-9b's shared table,
    but `Expr.linear` walks the inlined tree, which a chain of definitions makes exponential (me-9b's `[chain-41]`).
    `Claim.facts` keeps spec 5's `Option` type and owns no limit; me-5c's runner must check `Expr.nodesWithin
    maxPolyTerms` on each inlined claim before lowering, as `identityDecide` does, and pin it with a chain fixture
    (FOLLOW-UPS "## me-5b").
13. PASS: no test removed; `gate_collection.py --check --prebuilt` reports 0 refused, 0 stale and 0 malformed.
