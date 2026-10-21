No DRI signature is needed: trust growth K +0, S +18, V +0 is signed by standing ruling R16; no DELTA row reserves
one. me-9b delivers the rest of ME-9 except F5 (a work budget), which is **me-9c** (Next item). Size: 695 hand-written
changed lines before this report (`git diff --numstat`, the generated files of `regen_generated.py --list` excluded),
743 with `trust-mutants.json` (the tool's output); see Deviations.

# me-9b report: inlining and identities over named values

Base `6454946a5` (`git merge-base HEAD main`); commits `git log --oneline --no-merges main..HEAD`. No Python product
code, Rust or public output changes. Read first: me-9's REPORT ("Deviations", "Next item") and the FOLLOW-UPS "## me-9"
row.

**Statement gate.** ME-S passed (manage-agents math-evidence-p3ver2.final.md: PASS). After collapsing whitespace, these
equal spec 2.7 and 8.2 (main `c5197da78`) word for word: `freeNames`, `assign`, `assign_wellFormed`,
`Expr.inline_names`, `Expr.inline_sound`, `Expr.inline_undefined`, `Expr.inline_exhausted`, `Expr.inline_tooLarge`,
`Claim.inline_sound`, `IsIdentity`, `NotIdentity`, `not_isIdentity`, `isIdentity_of_check`, `notIdentity_of_differsAt`
and `differsAt_sound`; `Expr.inline` and `Claim.inline` have the spec's signatures. No statement had to change.

## Delivered (task order)

| Row | Delivered | Test or proof |
|---|---|---|
| Restore `Inline.lean`, the meaning layer and the runner from `wip/me-9b` (`ca4dc16ae`, `10819663b`) | yes: `Inline.lean` as on `10819663b`; the meaning layer and runner in a new `Identity.lean`, since `Poly.lean` on main is me-9's later version and its limit-reader test lists every definition there that reads a limit | `lake build`; `lean/audit.py` PASS |
| `assign_wellFormed`, `Expr.inline_tooLarge`, `Claim.inline`, `Claim.inline_sound` | yes. `inline_tooLarge` holds vacuously: with no statistics (ME-7) inlining never gives `.tooLarge` | `[claim-inline]`, `[claim-fault-undefined-first]`, `[claim-fault-exhausted-first]`, `[assign]`, the `#guard`s of `IdentityExamples.lean` |
| me-9 review F3: `undefined` before `holds` when a side's denominator is identically zero | yes, as a class: `Expr.zeroDivisor` finds a divisor whose fraction form's numerator is the zero polynomial anywhere in a side, inside a divisor or under a power 0 too (`1/(1/0)` and `(1/0)^0` have a nonzero top denominator); `Expr.zeroDivisor_sound` (from `Frac.ofExpr_sound`) gives `identityRun_undefined` | the review's four cases `[f3-0/0]`, `[f3-x-x]`, `[f3-1/0]`, `[f3-binom]`; `[f3-zero-rate]` (through a definition), `[f3-right]`, `[f3-inner]`, `[f3-pow-0]`; `[f3-0/0-compare]` shows `compare` alone says `some true`; `[f3-cancel-holds]` (a divisor zero at one point only) |
| F4: neither `sumx 5000` nor `(geo 100)^2` shown as "more than 10,000 terms" | yes: `IdentityRow.stop` names the node limit or the form's limits, and `IdentityRow.reason` gives its text (Deviations) | `[f4-nodes]`, `[f4-nodes-right]`, `[f4-product]` |
| The names a side reads are listed only after the normaliser accepted it | yes (zero divisors too) | `test_a_shared_side_costs_only_the_limit[chain-41]`, a chain of 40 definitions (2⁴¹ − 1 nodes as a tree), in its own process; mutant 10 |
| R-6 and H-4 through named and stated values | yes: R-6's `h1` holds over `round_trip` and `closed_form`; `sq` fails at x = y = 1 with sides 4 and 2 (spec 13.6's row); H-4 holds with D free and with D stated (2 × 10⁷, against 0.4) | `[r6-h1]`, `[r6-sq]`, `[h4]`, `[h4-stated]`, `[h4-stated-fails]` |
| The undefined and unknown rows | yes: a missing name, an undefined counted value, a zero divisor (undefined); a counted value whose budget ran out (`limit .evaluations`), the first faulty side naming the fault; the normaliser's limits; `identityNotShown` (normal forms differ, no point found: a product with a root at each of the 13 values) | `[undefined-missing]`, `[undefined-counted]`, `[exhausted]`, `[fault-*]`, `[f4-*]`, `[not-shown]`, `[point-later]`, `[point-skips-undefined]` |
| The reason text for the coefficient and exponent bounds | yes: `IdentityStop.text .form` | `[f4-exponent]`, `[f4-digits]` |
| F5, a work budget for powers and `differsAt` | **me-9c** (it does not fit) | — |
| `Check.OutcomeMeans` (me-2's) | not used: the runner's theorems state each outcome's clause directly (`identityRun_holds`, `_fails`, `_undefined`, `_unknown`, the last in `Check.UnknownCause`'s form for identities); no `Check` here | — |
| R-10c | waits for ME-4 | — |

## Deviations

- **The unknown reason at the normaliser's limits.** Spec 3.4 allows an identity four reasons, and only
  `limit .polyTerms` fits a normal form stopped by a limit. Its 1.5 text, "a normal form would have more than 10,000
  terms", is wrong for a side past the node limit (`sumx 5000` has one term) and for a product counted before like
  terms merge (`(geo 100)^2` has 201), and silent on exponents and digits (review F4). A new reason would change spec
  1.5's approved type, which no standing ruling covers. So the outcome stays `limit .polyTerms`, and the row carries
  `stop` (`.nodes` when a side is past the node limit, else `.form`), whose text `IdentityRow.reason` gives:
  "unknown: a side would have more than 10,000 nodes once its named values are written out", or "unknown: a normal
  form on the way would have more than 10,000 terms before like terms merge, an exponent above 4,096 or a
  coefficient of more than 4,096 digits". Nothing shows a row yet. When ME-2 makes the row public, its reason field
  must show `IdentityRow.reason`, and the wording is a DRI decision there (FOLLOW-UPS "## me-9b").
- **Undefined comes after the limits.** The zero-divisor check normalises divisors, so it runs only once both sides
  passed the normaliser. A side past a limit is unknown even if it also divides by zero.
- **Size.** 695 hand-written lines against ~600: 340 are the wip code the task restores. Of the rest, 119 are the
  evidence the checklists ask for: the trust classes (45), the `#guard`s for the trusted definitions (30), the
  seeded-bug list (32) and the allow file (12). F5, the next row in the task's order, is cut to me-9c.

## Trust

`trust_map.py --check` on the final code: K +0, S +18 (`freeNames` 4, `assign` 4, `IsIdentity` 5, `NotIdentity` 5),
untied V +0. G[R] +17 (`IdentityStop`, its text, `IdentityRow.reason`) and C, P, T for the rest. Recorded with
`--allow` and signed under R16 (DELTA row 1). The FOLLOW-UPS.md "## me-9b" row asks for the ties pass.

**`tools/trust_mutants.py --max-mutants 1000`** ([`trust-mutants.json`](trust-mutants.json), allow file
[`trust-mutants-allow.json`](trust-mutants-allow.json)): 46 mutants: 27 killed, 8 invalid, 11 allowed, 0 survivors,
0 unknown, exit 0. Its first run found two weak checks, both fixed: `freeNames` with the last declaration dropped
survived, because the guard list ended with a counted value (it now ends with a free one), and the example's helpers
were unclassified (now T). Allowed: 9 mutants of `IsIdentity` and `NotIdentity`, propositions over every
κ : String → Rat that no evaluated check can read. Each breaks `isIdentity_of_check` or `notIdentity_of_differsAt`,
and `not_isIdentity` (`mutants.json` 22 to 30), as me-2 allowed `Check.UnknownCause`. The other 2 (`list-empty` on
`assign` and `freeNames`) are not well-typed.

## Review fixes (manage-agents me-9b-review.final.md)

- **F1 (B), a place of a check that no fixture fills.** Fixed as a class in `tests/test_calc_algebra.py`, with no
  product change: `place_fixtures()` fills every place of every constructor from two tables, `OPERANDS` (`Expr`) and
  `CLAIMS` (`Claim`), which `test_the_place_tables_are_lean_s_constructors` holds to the constructors and expression
  fields Lean's environment lists, so a constructor added in Lean fails until its places are filled. They give 1/0 in
  each operand of each node (`[zero-divisor-<node>-<place>]`), every mix of a free value, a missing name and an
  exhausted counted value in each node's operands (`[subst-*]`) and in each claim's expressions (`[claim-*]`).
  `point_fixtures()` gives, for each of the 13 values, a side zero at every earlier point and not at it
  (`[point-1st]` to `[point-13th]`, values and products computed in Python), and `[identity-values]`; the point's
  names come from both sides in declaration order (`[point-right-only]`, `[point-left-only]`,
  `[point-declaration-order]`). The review's examples are `[f3-numerator]`, `[f3-left]`, `[fault-inside-side]`,
  `[claim-fault-compare]` and `[claim-fault-within-e]`. The review's 7 mutants were replayed (`mutants.json` 31 to
  37): each fails the fixtures listed there; 31 and 32 also break `Expr.zeroDivisor_sound` as written.
- **Tests for the fix** (`632a6eb6b`, the VM, the Mac runner unreachable): the review's probe fails before (no such
  fixtures) and passes after; `select_tests.py --base 6454946a5 --run` ran 81 units, 79 to exit 0 before the call's
  hour ran out, and the other two, `tests/test_acts_vocab_mutants.py` (643) and `tests/test_trust_mutants.py` (301),
  were rerun alone with `-n 6` and passed; `lake build` and `lean/audit.py` pass. No Lean changed, so the trust
  numbers and `trust-mutants.json` stand.
- **F2 (C)** and **F3 (C)** are not changed here: F2 is ME-2's wording decision (Deviations), F3 asks the DRI to
  confirm the allow class.

## Seeded bugs (Lean; [`mutants.json`](mutants.json), 37, each with its exact edit)

Lean is the only product language changed. Each mutant was applied in place and built as written
(`proofs_failing_as_is`). It was then run with every proof of `Inline.lean` and `Identity.lean` cut to `sorry`, so
only the fixtures could catch it, against `IDENTITY_FIXTURES` and `[chain-41]`. The other fixtures read only
`Poly.lean`, which no mutant touches. Every Lean run used `timeout 600`, and every file was restored after.
- Behaviours (1 to 21), each failing the named fixtures: F3's zero divisor never found (1), checked after `holds` (2),
  not looked for inside a divisor (3), under a power (4), or on the right side (5); F4's stop always `.form` (6), the
  node limit checked on the left side only (7), the reason ignoring the stop (8), the node text saying "terms" (9);
  names listed before the normaliser (10: `[chain-41]` fails); the point order (11), unread names in the point (12),
  no point reported `holds` (13), the fault order (14); a stated value inlined as undefined (15: H-4), the kept names
  inlined (16), a definition not inlined (17: R-6), `Claim.inline`'s fault order (18) and its sides swapped (19);
  the trusted `freeNames` (20) and `assign` (21).
- `IsIdentity` and `NotIdentity` (22 to 30): no fixture reads a proposition; each breaks the proofs named in
  `mutants.json`.
- Survivors found, then fixed by fixtures: mutant 5 (no fixture had the zero divisor on the right: `[f3-right]`) and
  mutant 19 (the `claim-inline` fixture compared two sides of equal value with `eq`; it is now `x < round_trip`).

## Tests

- **Selected tests:** `select_tests.py --base 6454946a5 --run` on the Mac runner: 81 units, 0 failed (HEAD
  `0239496e`, which contained `tests/test_calc_algebra.py`). On Linux, `tests/test_calc_algebra.py` passes in full: 258
  tests (363 after the review fixes).
- **Generated files and audits:** `regen_generated.py --write --skip route-cases` (route cases need the Rust binary
  and this item does not change them); `repo_map.py --check`, `lean/audit.py` and `trust_map.py --check` pass.
- **Collection:** `gate_collection.py --check --prebuilt`: 35 added, 0 removed, 0 refused, 0 stale, 0 malformed.
- **Full gate:** left to the chain. No test that main-known-red.txt lists failed.

Shared files: `lean/VE.lean` (union), `tools/trust-classes.json` and `docs/trust-baseline.json` (registries), as for
me-9. No branch in flight edits `lean/VE/Calc/Inline.lean`, `Identity.lean`, `IdentityExamples.lean`,
`tests/test_calc_algebra.py` or `lean/CALC.md`. feature/me-2 adds `Check` in `Wire.lean` and `Run.lean`, which this
item does not touch.

**Bytes:** 0 expected (use-case ceilings); nothing is claimed before a pilot audit.

## Next item

- **me-9c** (F5): a work budget for powers within the limits, for `differsAt` (`Expr.eval`, unlimited) and for
  `Expr.zeroDivisor` (quadratic in nested divisors), before the runner is wired to a mode.
- me-5b (rank 44) imports `Inline.lean`; it must not write a second lowering. R-10c waits for ME-4, then ME-7.

## Sibling lessons (me-6b review)

- F1, a trusted check tested on one side only: every new trusted definition has a check that fails both ways
  (`assign`: a kept value, a value given, and a definition reading both; `freeNames`: a free value first, in the
  middle and last); the zero-divisor and stop checks have fixtures on each side (`[f3-right]`, `[f4-nodes-right]`).
- F2, `trust_mutants.py` not run: it was run on the final Lean, evidence and allow file committed, exit 0 (Trust).
- F3, two readings of a text: the stop texts name one limit each, or list the form's limits in one clause.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer is relayed; no mode or schema.
2. PASS: the task's rows above, each with its commit's test, F5 moved to me-9c by the size rule; `git diff main...HEAD`
   has no Python copy of a Lean decision (the test states expected strings, Lean prints answers), no report test, no
   file an in-flight branch edits.
3. PASS: 30 seeded bugs (`mutants.json`), each failing named `tests/test_calc_algebra.py` fixtures with the proofs cut,
   or the named proofs; `trust_mutants.py` exit 0 with evidence and allow file.
4. N.A.: no Python or Rust counterpart exists for inlining or the runner.
5. N.A.: no relayed field to bind; the identity row's fields bind at ME-3 (spec 3.4).
6. PASS: base from `git merge-base`; commits from `main..HEAD --no-merges`; full gate on the final HEAD by the chain.
7. PASS: DELTA row 1 cites R16; `trust_map.py --check` PASS; FOLLOW-UPS row present.
8. PASS: DELTA "Public output: none" (no mode, command, route or Python/Rust product file).
9. PASS: the selection contained `tests/test_calc_algebra.py` (81 units), whose fixtures fail for each seeded bug.
10. PASS: the statements match the spec after whitespace normalisation; `lean/audit.py` PASS; 23 of 30 mutants also
    break a proof as written.
11. PASS: the budget's unknown is never a verdict (`[exhausted]`, `[fault-exhausted-first]`, `[fault-right]`); past
    the normaliser's limits the row is unknown, never `holds` (`[f4-*]`, `[chain-41]`), and `identityRun_unknown`
    proves an unknown names only the identity's reasons.
12. PASS: the shared chain stops at the node limit (`[chain-41]`, 3 s, mutant 10); the cost inside the limits is
    me-9c's (F5).
13. PASS: no test removed; `gate_collection.py --check --prebuilt` reports 0 refused, 0 stale and 0 malformed.
