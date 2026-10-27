No DRI signature is reserved: DELTA has no row and trust is +0. By the size rule, me-12ab delivers task parts (1) and
(2), `decideBounded_mono` and `decideBounded_complete`, with a work bound per statement that does not depend on the
budget. Parts (3) and (4), spec 12.5's `decidingValue` with its three theorems and M-6, are **me-12ac** (Next item).

# me-12ab report: the evaluator's monotonicity and completeness

Base `a557ff887` (`git merge-base HEAD main`); commits `git log --oneline --no-merges main..HEAD`. Lean is the only
product language changed. There is no Python, Rust, mode, route or public output.

**Statement gate.** ME-S passed (manage-agents math-evidence-p3ver1.final.md, then math-evidence-p3ver2.final.md:
PASS). A scratch script cuts each theorem at its `:=` and collapses whitespace. `decideBounded_mono` and
`decideBounded_complete` then equal spec 12.2's text (main 0e7a813e8), and so do me-12aa's `decideBounded_sound`
and `decideBounded_work`. `lean_statements.py --check` reports 0 removed and 0 changed.

## Delivered (task order)

| Task row | Delivered | Proof or test |
|---|---|---|
| (1) `decideBounded_mono` | yes. `Extends O O'` is shaped like `Agrees`: each call `O` completes, `O'` completes with the same value and units. `opEnv_extends` shows `D.opEnv limit` extends `D.opEnv limit'` for `limit ≤ limit'`, by `foldl_rel`; `Formula.evalB_mono` is a mutual induction | `Bounded.lean` (`lake build`, `lean/audit.py` PASS); `CompleteExamples.lean:25` sweeps every budget from 0 through 40 or 200 for five statements, each answer kept by the next budget |
| (2) `decideBounded_complete`, with a work bound per formula that does not depend on the limit | yes, through `decideBounded_covered`: a bounded, admitted statement has an answer b and units W, fixed by the statement and its definitions, and every budget ≥ W returns (b, W). `Total` is the invariant of the definitions' environments, one per budget, built by `total_take` from `Defs.WellFormed`; `Formula.evalB_total` is a mutual induction over the sites admission checks (`Site.Ok`) | `CompleteExamples.lean:19-24`: W − 1 none, W and W + 1 (b, W), on calls, counts, nested binders and a short circuit |
| (2) each hypothesis on its refusing side | an unbounded statement, a variable no binder gives, a wrong arity, a missing name and a recursive definition stay none at budgets 0, 1 and 1,000,000, and each fails its hypothesis | `CompleteExamples.lean:32-37` |
| Seeded bug: a monotonicity counterexample from a budget-dependent environment | M1 (below); also `tickEnv`, an environment that reads the budget, whose answer changes from budget 5 to 6 | `CompleteExamples.lean:43` |
| Budget boundaries at, just under and just over the limit | yes | `CompleteExamples.lean:19-24` |
| (3) `decidingValue`, `decidingValue_all`, `decidingValue_ex`, `decidingValue_of_fails` | **me-12ac** (size) | — |
| (4) M-6 as a `#guard` | **me-12ac** (size) | — |
| `lean/ARITH.md` | the three theorems in plain words, the new file, the split | — |

## Findings

- **N1 is unchanged.** `decideBounded_covered` bounds units, and spec 12.2 charges formula nodes only, so W does not bound
  the CPU of term-bodied functions. me-12aa's N1 stands for the DRI before me-12b. Neither theorem needs N1's fix.
  Charging calls would change W, not the theorems.

## Deviations

- **Size.** 579 hand-written lines before this report and DELTA: `Bounded.lean` +502 (monotonicity 195, completeness 307),
  `CompleteExamples.lean` 52, the trust side table +14/−1, `ARITH.md` +7/−2, `VE.lean` 1. DELTA adds 20 lines and this
  report about 100, so the item is about 700. I did not measure before starting part (2), as the size rule asks; parts
  (1) and (2) are one unit (both read the same environments), and I cut there, before (3).
- **Generated `route-cases`.** `regen_generated.py --write` ran with `--skip route-cases`, which needs the Rust release
  binary, as in me-12aa. No route changed.

## Trust

`uv run python tools/trust_map.py --check --since a557ff887` on the final code: K +0, S +0, D +0, G +0, unclassified
+0, trusted +0, PASS. New definitions are P (`tools/trust-classes.json`); fixtures are T. No allowance, no R16 row.
`mac-pytest.sh --trustmut -- --jobs 6 --max-mutants 1000` ([`trust-mutants.json`](trust-mutants.json); it ran on the VM
because the Mac slots were busy) selects 0 definitions and 0 mutants, exit 0.

## Seeded bugs and mutants (Lean; [`mutants.json`](mutants.json))

All are in `lean/VE/Arith/Bounded.lean`. Each mutant was planted alone, in a copy of the file joined with both fixture
modules into one file. One `lake env lean` run on that file lists the broken proofs and the failing guards; the
control has no error. **9 of 9 are killed.**

- **M1** `Defs.opEnv`, a budget-dependent environment (a function's value adds the budget's parity): breaks
  `opEnv_extends` and `agrees_env`; fails `CompleteExamples.lean:25` and `BoundedExamples.lean:130`.
- **M2** `charge`: budget 4 refuses every visit. Breaks `charge_mono`; fails `CompleteExamples.lean:23, 25`.
- **M3** `Formula.evalB`: a one-place predicate call never completes. Breaks `Formula.evalB_total` and
  `Formula.evalB_sound`; fails `CompleteExamples.lean:19-24` and M-1, M-2, M-4.
- **M4** `Term.evalB`: an unbound variable reads 0, so an unscoped statement is decided. Breaks `Term.evalB_sound`;
  fails `CompleteExamples.lean:32` and `BoundedExamples.lean:106`.
- **M5** `Extends`: a call need only complete, not with the same value. Breaks `Term.evalB_mono`, `opEnv_extends`.
- **M6** `Total`: a strict work bound. Breaks `Term.evalB_total`, `Total.snoc`.
- **M7** `Site.Ok`: a free variable one past the outer values. Breaks `Site.ok_of_refusal`, `Term.evalB_total`.
- **M8** `Def.SitesOk`: a predicate body read under one binder too many. Breaks `wellFormed_at`, `Total.snoc`.
- **M9** `subSites`: a formula's parts are not read as its sites. Breaks `Formula.evalB_total`.

M5–M9 are proof helpers (P), so a proof, not a guard, kills them. A `#guard` cannot evaluate a `Prop`.

## Tests

- **Selected tests:** TESTS_LINE
- **Checks on the final code:** `lake build` of the whole library passes (1,118 jobs). `lean/audit.py`,
  `lean_statements.py --check`, `repo_map.py --check` and `trust_map.py --check` pass. `regen_generated.py --write
  --skip route-cases` wrote 32 entries. `gate_collection.py --check --prebuilt` reports 0 added, 0 removed, 0 refused,
  0 stale and 0 malformed.
- **Full gate:** left to the chain, on the final HEAD.

Shared files: `lean/VE.lean` (one import, union) and `tools/trust-classes.json` (one new file key, five P names).
In-flight branches that touch them: `feature/ap-2b`, `feature/qt-a3b` and `foundation/me-1` (both files);
`feature/jt-2` and `feature/q1-4` (`trust-classes.json`). No in-flight branch touches `lean/VE/Arith/` or `lean/ARITH.md`.

**Bytes:** 0 expected (use-case ceiling); nothing is claimed before a pilot audit.

## Next item

- **me-12ac:** spec 12.5's `decidingValue` (the first decisive value of the outermost bounded quantifier, in 12.2's
  order) with `decidingValue_all`, `decidingValue_ex` and `decidingValue_of_fails`, and M-6 (VE's `prime` against
  `IsPrime` on 0 … 400, 78 primes) as a `#guard`. Mutants: one per new definition. New files only.
  - Plan: a loop shaped like `quantLoop` that returns the index where it stops early. The first two theorems follow
    from `Formula.evalB_sound` through `agrees_env`. `decidingValue_of_fails` follows from `quantLoop` returning false
    exactly when that loop stops.
  - `IsPrime` needs a `Decidable` instance, proved equal to it, for the guard.
- **me-12b** (protocol queue after AP-4, after the DRI's decision on N1): the wire, runner, rows, encoder and mode.

## Sibling lessons (me-2c review)

- F1 (expressions evaluated again per row): N.A. This item adds no runtime evaluation; the evaluator is unchanged.
- F2 (a field `null` where the spec wants a value, the rest unnamed): applies to the size cut. (3) and (4) are named
  as me-12ac above, with what each needs.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer is relayed; no mode or schema (me-12b).
2. PASS: each task row above, with its proof or guard; (3) and (4) move to me-12ac by the size rule. `git diff
   main...HEAD` has no Python copy of a Lean decision, no report test, and no file an in-flight branch edits except
   the two registries listed.
3. PASS: 9 hand mutants, each killed by a named proof or guard (`mutants.json`); the control is clean. `trust_mutants.py`
   exits 0 with 0 definitions (`trust-mutants.json`).
4. N.A.: `arith@0` has no Python or Rust counterpart.
5. N.A.: no relayed field to bind.
6. PASS: base from `git merge-base`; commits from `main..HEAD --no-merges`; full gate on the final HEAD by the chain.
7. PASS: DELTA has no row; trust +0 (`trust_map.py --check --since a557ff887`); no allowance, so no signature.
8. PASS: DELTA "Public output: none": no mode, command, route or Python or Rust product file.
9. PASS: TESTS_SHORT
10. PASS: the two statements equal spec 12.2 after whitespace normalisation; `lean/audit.py` PASS; M1, M2, M5–M9
    break the proofs as written, and `decideBounded_mono` is about `decideBounded` itself, not a copy.
11. PASS: budget 0 is none on every refusing fixture (`CompleteExamples.lean:32-37`) and below the work on every
    accepting one (`:19-24`); M2 and M3 show these guards can fail.
12. PASS: no runtime path changes. N1, the CPU class, is unchanged and still pinned by `BoundedExamples.lean:130`.
13. PASS: no test removed; `gate_collection.py --check --prebuilt` reports 0 refused, 0 stale and 0 malformed.
