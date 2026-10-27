No DRI signature is reserved: there is no DELTA row and trust is +0. By the size rule, me-12aa delivers task parts (1)
and (2): the budgeted evaluator of `arith@0` and its evaluation fixtures. Parts (3) and (4) are **me-12ab** (Next
item). One finding is for the DRI before me-12b exposes the evaluator. **N1:** under spec 12.2's approved
accounting, terms are free, so the budget does not bound the work in function bodies that are terms. A 24-definition
request costs 1 unit and about 54 s of CPU (Findings).

# me-12aa report: the budgeted evaluator of `arith@0`

Base `22dad00fd` (`git merge-base HEAD main`); commits `git log --oneline --no-merges main..HEAD`. Lean is the only
product language changed. There is no Python, Rust, mode, route or public output.

**Statement gate.** ME-S passed (manage-agents math-evidence-p3ver1.final.md, then math-evidence-p3ver2.final.md:
PASS). `wip/me-12aa` (d7be5b890, also at origin as 23aa37074 with the same `Bounded.lean`) is an ancestor of main.
me-12a deleted its `Bounded.lean` later, so I restored the file unchanged. A scratch script, not committed, takes each
declaration from the Lean blocks of spec 12.2 (main, docs/spec/math-evidence.md) and from the file, cuts theorems at
their `:=`, and collapses whitespace. These are equal: `charge`, `quantLoop`, `countLoop`, `OpEnv`, `Term.evalB`,
`Term.evalBs`, `Formula.evalB`, `Defs.opEnv`, `maxSteps`, `decideBounded`, `arithOutcome`, `decideBounded_sound`,
`decideBounded_work`, `arithOutcome_unbounded_iff`, `arithOutcome_exhausted_iff` and `arithOutcome_decided` (16 of 16).
`decideBounded_mono`, `decideBounded_complete` and `decidingValue` are not built (me-12ab), so no statement changed.
me-12a's statements are unchanged: `lean_statements.py --check` passes, and the generated `statements.txt` only adds
lines.

## Delivered (task order)

| Task row | Delivered | Test or proof |
|---|---|---|
| (1) `Bounded.lean`: the fuel accounting (one unit per formula-node visit), `maxSteps` (default and maximum 1,000,000), `decideBounded`, `decideBounded_sound`, `decideBounded_work`, `arithOutcome`'s three theorems; `regen_generated.py --write` | yes, restored from d7be5b890 unchanged (commit f5b6dc4dd) | the proofs (`lake build`, `lean/audit.py` PASS); `BoundedExamples.lean:13` (`maxSteps = VE.Time.maxEvaluations = 1,000,000`) |
| (2) M-1 | yes: (true, 17,011) | `BoundedExamples.lean:19, 21` |
| (2) M-1b at, under and over the boundary | yes: 17,010 none, 17,011 and 17,012 (true, 17,011); the row at 17,010 is unknown | `:20, 22` |
| (2) M-2 | yes: (true, 395); at 394 none; one broken link fails | `:26-28` |
| (2) M-4 at the measured bounds 200 and 1,000 | yes: 200 (true, 576,518); 247 holds; 248 (true, 998,395); 249 none; 1,000 none; at 249 the budgets 1,008,567 / 1,008,568 / 1,008,569 give none / (true, 1,008,568) / (true, 1,008,568) | `:47-55` |
| (2) M-4b | yes: each pair fails at T − 1 and holds at T and T + 1; through its bound N, unknown at N + 1 (k = 1, 3, 4: N = 248; k = 5: N = 249) | `:59-69` |
| (2) M-4x | yes: budget 1,000 is unknown (`limit .evaluations`), never fails | `:23` |
| (2) M-5's evaluator half (2 units, deciding value n = 1) | yes: budgets 1 / 2 / 3 give none / (false, 2) / (false, 2); the row fails; the inner ∃ at n = 1 is (false, 1); from n = 2 the statement holds, so n = 1 is the first decisive value | `:35-43` |
| (2) Budget 0 is the unknown row, never a verdict | yes: on the one-visit statement (0 / 1 / 2 give none / (true, 1) / (true, 1)), on M-1 (row unknown) and on M-3 (stated, not decided, classified before evaluation) | `:14-16, 31` |
| (2) The plan's Lean seeded bug (a range from lo to hi reaches hi + 1: M-5 fails) | yes: S1 (∃) and S1b (∀) in `Formula.evalB` | Seeded bugs |
| (2) Each check on both sides | one guard per clause of the evaluator, each with its value both ways and its units: comparisons, `not`, short-circuit `and`/`or`/`imp`, unbounded quantifiers (none), ranges (empty, first decisive value), counts (empty, one, several), binders under outer values, missing values (variable, name, arity), calls through the definitions in order, budget inside a body, the definitions' fold order | `:75-120` |
| (3) `decideBounded_mono`, `decideBounded_complete` | **me-12ab** (size) | — |
| (4) spec 12.5's `decidingValue` with its theorems, M-6 | **me-12ab** (size) | — |
| `lean/ARITH.md` | the budget and the evaluator's theorems in plain words | — |

Plan ME-12 lines this item covers: "A count's meaning is defined through `Holds`; the evaluator is proved to agree"
(`decideBounded_sound`). "The budget is the spec's fuel accounting (one unit per formula-node visit, default and
maximum 1,000,000)" (`maxSteps`, `:13`). "Fixtures: M-1, M-2, M-4, M-4b, M-4x, M-5 (with its deciding value n = 1)":
the evaluator half is here; the reported value is `decidingValue` (me-12ab), and the row's field is me-12b. "an
unbounded statement reported 'stated, not decided'" (`:31`). "ME-12 measures M-4 at the candidate bounds 200 and
1,000 and pins the completing bound from that measurement, and does the same for each pair of M-4b" (`:47-69`). The
Lean seeded bug is S1. The rest of the ME-12 section (wire, refusal texts, runner, rows, encoder, mode, relay, Python
seeded bug) is me-12b.

## Findings

- **N1 (for the DRI, before me-12b exposes the evaluator; the me-2b review's F1 class).** Spec 12.2 charges formula
  nodes only, and term nodes are free. A function whose body is a term therefore costs no unit, however often it is
  called. Take `f0 = 1` and `f(i+1) = f(i) + f(i)`. That request is well formed, scoped and bounded, and is far within
  the wire's limits (512 definitions, 40-digit numerals). `0 < f(k)` or `2^k = f(k)` costs 1 unit at every k.
  - Work: 2^k evaluations of `f0`.
  - Measured with `lake env lean` (interpreted, whole run): k = 18 took 2.0 s, k = 22 took 14.1 s, k = 24 took
    55.8 s.
  - With `f(i+1) = f(i) × f(i)` the value's digits double at each level, so memory grows the same way.
  - `BoundedExamples.lean:125-130` pins the accounting as approved: 1,024 evaluations for 1 unit.
  - The fix changes approved text (the evaluator and spec 13.3's unit counts), so it is not made here. Two options: charge
    calls (or term nodes), or evaluate each zero-parameter definition once.
  - A 512-deep linear chain evaluates without exhausting the stack.

## Deviations

- **Size.** 655 hand-written lines before this report: `Bounded.lean` 468 (restored), `BoundedExamples.lean` 138,
  `ARITH.md` +16/−3, the trust side table 37, `VE.lean` 1. DELTA adds 26 lines and this report about 140. The restored
  file alone is 468 lines, so parts (1) and (2) cannot fit under 600 with their docs. I cut before (3), as the size
  rule asks; `mutants.json` and `trust-mutants.json` are tool outputs. The hand-mutant runner was a scratch script
  and is not committed: `mutants.json` records each edit exactly, with its occurrence, the cut and the control.
- **Fixture file.** The fixtures are in a new module, `BoundedExamples.lean` (namespace `VE.Arith.Examples`). me-12a's
  `Examples.lean` stays as merged (the task: new files only).
- **Generated `route-cases`.** `regen_generated.py --write` and `--check` ran with `--skip route-cases`, which needs
  the Rust release binary. No route changed. The other 32 entries were written and pass `--check`.

## Trust

`uv run python tools/trust_map.py --check --since 22dad00fd` on the final code: K +0, S +0, untied V +0, G +11 (tied
+9: `arithOutcome`, tied to its three theorems; `maxSteps` G[R]), trusted +0, PASS. The evaluator is C, `Agrees` P,
and the fixtures T (`tools/trust-classes.json`, the classes d7be5b890 gave). No allowance is recorded and no R16
signature is needed, so there is no FOLLOW-UPS row.

`mac-pytest.sh --trustmut -- --jobs 6 --max-mutants 1000` on f5b6dc4dd ([`trust-mutants.json`](trust-mutants.json))
reports 0 definitions and 0 mutants, exit 0. No new declaration is trusted, so the tool selects none. Every new
definition is therefore covered by hand mutants (below).

## Seeded bugs and mutants (Lean; [`mutants.json`](mutants.json))

All are in `lean/VE/Arith/Bounded.lean`. Each was planted alone, with the proofs cut, as `trust_mutants.py` cuts a
broken proof, so that a guard fails and not a proof. Then `lake build VE.Arith.BoundedExamples` ran. The control
(cuts, no mutant) builds. **39 of 39 are killed** by a named `#guard` of `BoundedExamples.lean`; none is invalid. The
build was redone from the restored sources afterwards.

- **The plan's bug.**
  - S1: the bounded ∃ reaches hi + 1, so M-5 holds at n = 1. It fails `:35, 36, 38` and M-1, M-2, M-4.
  - S1b: the same for the bounded ∀. It fails `:19, 20, 88, 100` and others.
- **`charge`.**
  - H01: refused one visit late. Fails `:14, 20, 22, 37`.
  - H02: a visit charges nothing. Fails `:14` and others.
- **`quantLoop`.**
  - H03: an empty range gives the other value. Fails `:88` and others.
  - H04: a decisive value is ignored. Fails `:36, 88` and others.
  - H05: every other value is skipped. Fails `:88` and others.
- **`countLoop`.**
  - H06: every value is counted. Fails `:95` and M-4.
  - H07: the count starts at 1. Fails `:95, 100`.
- **`Term.evalB`.**
  - H08: a variable reads the next binder.
  - H09–H11: sum, difference and product. Each fails `:75` and others.
  - H12: a function call ignores its arity. Fails `:106`.
  - H13: a count reaches hi + 1.
  - H14: a count's condition does not see its value.
- **`Term.evalBs`.**
  - H15: the arguments are reversed. Fails `:111`, `minus 5 3`.
- **`Formula.evalB`.**
  - H16–H19: the four comparisons. Each fails `:75` and others.
  - H20: a predicate call ignores its arity. Fails `:106`.
  - H21: `not` keeps the value.
  - H22–H24: no short circuit in `and`, `or` visiting its right side after true, and a false antecedent making `if`
    false. Each fails `:81`.
  - H25: "for every whole number" evaluated. Fails `:32, 86`.
  - H26: a ∀ binds its value second. Fails `:100`.
  - H27: ∃ read as ∀.
  - H28: the ∀ node is free.
- **`Defs.opEnv`.**
  - H29: a function reads its arguments reversed. Fails `:111`.
  - H30: a later predicate hides the earlier ones. Fails `:111, 120`.
  - H31: the same for functions.
  - H32: the first definition of a name wins. Fails `:120`.
- **`maxSteps`.**
  - H33: one more. Fails `:13`.
- **`decideBounded`.**
  - H34: evaluation starts with one unit spent.
- **`arithOutcome`.**
  - H35: exhausted reads as fails. Fails `:16, 22, 23, 37`.
  - H36: an unbounded statement is evaluated. Fails `:31`.
  - H37: false reads as holds. Fails `:36`.

With the proofs not cut, these three also break proofs as written (`lake build VE.Arith.Bounded`, exit 1):
- S1 breaks `Formula.evalB_sound` (`Bounded.lean:403`).
- H03 breaks `quantLoop_true` and `quantLoop_false` (`:136, 166`).
- H35 breaks `arithOutcome_exhausted_iff` and `arithOutcome_decided` (`:453, 463`).

## Tests

- **Selected tests:** `mac-pytest.sh --select -- --base 22dad00fd --run` on ve-mac-1, HEAD 668e1b8f5: 185 units,
  0 failed (2,628 s). The commit after it adds one guard (`:125-130`) and its trust-class entry.
  `tests/test_trust_budget.py`, `tests/test_trust_ratchet.py` and `tests/test_gate_trust.py` pass on it (143 tests).
  The item adds no pytest file. Its tests are the Lean guards and proofs that `lake build` checks
  (`VE.Arith.BoundedExamples` builds in about 55 s).
- **Checks on the final code:**
  - `lake build` of the whole library passes (1,094 jobs).
  - `lean/audit.py`, `lean_statements.py --check`, `repo_map.py --check` and `trust_map.py --check` pass.
  - `regen_generated.py --check --skip route-cases` passes (32 entries).
  - `gate_collection.py --check --prebuilt` reports 0 added, 0 removed, 0 refused, 0 stale and 0 malformed.
- **Full gate:** left to the chain, on the final HEAD. No test that main-known-red.txt lists failed.

Shared files: `lean/VE.lean` (one import, union), `tools/trust-classes.json` (registry, one new file key). In-flight
branches that touch them: `feature/df-1ae`, `feature/qt-a3` and `foundation/me-1` (`VE.lean`); `feature/ap-1bc`,
`feature/jt-2`, `feature/me-5c`, `feature/q1-4` and `infra/arch-20261026-2` (`trust-classes.json`). No in-flight
branch touches `lean/VE/Arith/` or `lean/ARITH.md`.

**Bytes:** 0 expected (use-case ceiling); nothing is claimed before a pilot audit.

## Next item

- **me-12ab:** `decideBounded_mono` and `decideBounded_complete` (spec 12.2), then spec 12.5's `decidingValue` with
  `decidingValue_all`, `decidingValue_ex`, `decidingValue_of_fails`, and M-6 (VE's `prime` against `IsPrime` on
  0 … 400, 78 primes). New files or `Bounded.lean` only. The mono proof needs a relation between `D.opEnv limit` and
  `D.opEnv limit'` (`limit ≤ limit'`), shaped like `Agrees`. Completeness needs a work bound per formula that does not
  depend on the limit.
- **me-12b** (protocol queue after AP-4): the wire with `ShadowedVariable` and the refusal texts, plus the runner,
  rows, encoder and mode. The DRI's decision on N1 comes first.

## Sibling lessons (me-2b review)

- F1 (a value recomputed at every read, exponential in a chain within every limit): **applies.** It is N1 above,
  measured. I did not fix it, because the fix changes approved text. The fixture pins it so the fix shows.
- F2 onwards (the size check, the identity parts): N.A.; this item has no wire, limits or identity.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer is relayed; no mode or schema (me-12b).
2. PASS: each task row and the ME-12 plan lines above, with its guard or proof; (3) and (4) move to me-12ab under the
   size rule (named). `git diff main...HEAD` has no Python copy of a Lean decision, no report test and no file an
   in-flight branch edits except the two registries listed.
3. PASS: 39 hand mutants (`mutants.json`), one or more per new definition, each killed by a named `#guard`. The control
   builds. `trust_mutants.py` exits 0 with 0 definitions selected (`trust-mutants.json`).
4. N.A.: `arith@0` has no Python or Rust counterpart.
5. N.A.: no relayed field to bind (me-12b binds rows to statements).
6. PASS: base from `git merge-base`; commits from `main..HEAD --no-merges`; full gate on the final HEAD by the chain.
7. PASS: DELTA has no row; trust +0 (`trust_map.py --check --since 22dad00fd`); no allowance, so no signature.
8. PASS: DELTA "Public output: none" (no mode, command, route or Python/Rust product file).
9. PASS: the selection ran 185 units, 0 failed. This item's fixtures are Lean guards that `lake build` checks, and
   S1–H37 break them.
10. PASS: 16 of 16 statements equal spec 12.2 after whitespace normalisation; `lean/audit.py` PASS; S1, H03 and H35
    break the proofs as written.
11. PASS: budget 0 is unknown on every fixture kind (`BoundedExamples.lean:14-16, 31`); each budget boundary is
    tested at, under and over (`:14, 20, 27, 35, 53, 117`). H01, H02 and H34 show these guards can fail.
12. PASS (finding): there is no runtime path yet. N1 is the CPU and memory class, measured, and pinned by the
    step-count guard `:125-130` for the DRI's decision.
13. PASS: no test removed; `gate_collection.py --check --prebuilt` reports 0 refused, 0 stale and 0 malformed.
