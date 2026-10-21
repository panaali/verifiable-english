No DRI signature is needed: trust growth K +0, S +93, V +0 is signed by standing ruling R16; no DELTA row reserves
one. By the size rule me-12a delivers the statement API of `arith@0` (spec 12.1, the boundedness half of 12.2, and
12.3). The budgeted evaluator and the evaluation fixtures are **me-12aa** (Next item). They are built, proved and
passing on the local branch `wip/me-12aa`.

# me-12a report: the `arith@0` statement API

Base `7855620f3` (`git merge-base HEAD main`); commits `git log --oneline --no-merges main..HEAD`. Lean is the only
product language changed; no Python, Rust or public output.

**Statement gate.** ME-S passed (manage-agents math-evidence-p3ver2.final.md: PASS). I checked each declaration
against spec 12.1–12.3 (main `7855620f3`) after collapsing whitespace, using a scratch script (not committed) that
reads the spec's Lean blocks. These are equal word for word: `Term`, `Formula`, `Env`, `Term.value`, `Term.values`,
`Holds`, `Def`, `Defs`, `Defs.env`, `Defs.Means`, `Term.bnd`, `Term.bndList`, `Formula.bnd`, `Defs.boundedNames`,
`Formula.Bounded`, `primeBody`, `primeDefs`, `IsPrime`, `bertrand` and `bertrand_means_iff`. `Defs.WellFormed` and
`Formula.Scoped` have the spec's signatures; the spec leaves their bodies open. The task also lists `Defs.expand`, but
that is plan 3.9's name. The reviewed spec replaced it with `Defs.env` (choice C5: same meaning, no inlining) and kept
`Defs.Means`, so no statement had to change. `Formula.evalB`, `decideBounded` and `decideBounded_sound` are in
me-12aa; on `wip/me-12aa` they match 12.2 the same way.

## Delivered (task order)

| Row | Delivered | Test or proof |
|---|---|---|
| `Syntax.lean`, `Holds.lean`: 12.1's syntax and meaning (a count through `Holds`, F4) | yes | `primeBody_iff`, `bertrand_means_iff`, the meaning examples `Examples.lean:50-79` |
| `Defs.lean`: `Formula.Bounded`, `Defs.WellFormed`, `Formula.Scoped` | yes | `#guard`s `Examples.lean:116-125` |
| `Bounded.lean`: the fuel accounting, `maxSteps`, `decideBounded`, the evaluator proved to agree | **me-12aa** (size); built on `wip/me-12aa` with `decideBounded_sound`, `decideBounded_work` and `arithOutcome`'s three theorems | — |
| `Examples.lean`: 12.3's vocabulary, `IsPrime`, `bertrand_means_iff` | yes | the proofs |
| `lean/ARITH.md` | yes | — |
| The refusals the core decides: `UnscopedVariable`, `UnknownDefinition`, `RecursiveDefinition`, `ArityMismatch`, `UnboundedCount` (and `DuplicateName`), in the decoder's order | yes: `Refusal`, `caseRefusal` | `Examples.lean:122-142`, each refused and admitted |
| `ShadowedVariable` | **me-12b**: shadowing is about the request's variable names, and the de Bruijn core has none | — |
| An unbounded statement "stated, not decided" | in part: `bertrand.Bounded primeDefs = false` (`Examples.lean:116`); the row (`arithOutcome`) is me-12aa | `#guard` |
| M-5 fails, deciding value n = 1 | in the meaning: `¬ primeDefs.Means m5`, proved with n = 1 (`Examples.lean:91`); the evaluator's 2 units and 12.5's `decidingValue` are me-12aa | the proof |
| M-1, M-1b, M-2, M-4 (measured at 200 and 1,000), M-4b, M-4x | **me-12aa**; statements here (`m1`, `m2`, `m4`, `countDefs`), admitted and bounded (`Examples.lean:116, 122`) | — |
| The plan's Lean seeded bug (a range from lo to hi reaches hi + 1: M-5 fails) | in the meaning: S1 and S1b below; in the evaluator, me-12aa | — |
| One mutant per new trusted definition | yes: all 163 | Trust |

Measured on `wip/me-12aa` (for me-12aa, at budget 1,000,000), with the spec's numbers reproduced exactly:
- M-1: (true, 17,011); at 17,010 none. M-5: (false, 2).
- M-4 at 200: (true, 576,518); at 248: (true, 998,395); at 249: none, and 1,008,568 at 2,000,000; at 1,000: none.
  The completing bound is 248, as spec 13.3 says.
- M-4b, completing bounds: k = 1, 3 and 4 through 248 (998,948, 997,399 and 993,580 units); k = 5 through 249
  (997,116). Each pair fails at T − 1 and holds at T.
- Spec 13.3's 111 and 127 units are the difference term alone; with its `le` node they are 112 and 128.
- M-2 costs 395 units as the right fold of its 17 facts closed by "0 equals 0", and 393 without that closing atom.
  The spec does not give the stub's formula.

## Deviations

- **The cut.** The first build of the whole task came to 849 hand-written Lean lines before docs and evidence (commit
  `d7be5b890`, saved as `wip/me-12aa`). I cut at the boundary that leaves two coherent parts. This item is the
  statement API that EX-1 needs ("after ME-12's statement API"). me-12aa is the evaluator with its proofs and
  measured fixtures, which needs no more design.
- **Refusal texts.** `caseRefusal` returns `Refusal` values whose `code` is spec 13.1's code. The texts name
  variables and definitions by the request's names, so they are the wire's (me-12b). For an unscoped variable the
  core reports its de Bruijn distance past the scope.
- **What kills the meaning's mutants.** `trust_mutants.py` counts only evaluated checks, and `Holds`, `Term.value`,
  `Defs.env`, `Defs.Means` and `IsPrime` are propositions or noncomputable, so no check can read them. This is the
  class me-9b allowed for `IsIdentity`. `proofkill.py` builds every planned mutant against the proofs and examples as
  written. Its first runs found 8 survivors, each now killed by a new example: a call with too few arguments, a
  direct call of an earlier function, a two-argument predicate, counts from 2 through 5 and through 6, and a bounded
  "for every" past hi. The allow file names, for each (definition, operator), the proofs that break.
- **Size.** 610 hand-written lines for the product, docs, scripts and side table: Lean 406, `ARITH.md` 49,
  `proofkill.py` 45, the allow file 48, trust classes 62. This report and DELTA add about 130 more. The tool outputs
  `mutants.json` (178) and `trust-mutants.json` (165) are extra.

## Trust

`trust_map.py --check` on the final code passes. Measured: K +0, S +93 (`Syntax.lean` 31, `Holds.lean` 60, `IsPrime`
2), untied V +0. Admission and boundedness (`Defs.lean`) are G[R]; the examples are T. The growth is recorded with
`--allow` and signed under R16 (DELTA row 1); the FOLLOW-UPS.md "## me-12a" row asks for the ties pass.

**`trust_mutants.py --max-mutants 1000 --allow`** on the Mac ([`trust-mutants.json`](trust-mutants.json)): 163
mutants: 159 allowed, 4 invalid, 0 survivors, 0 unknown, exit 0. Without `--allow` (first run) it gave 0 killed and
every mutant a survivor or unknown, as expected for propositions. [`mutants.json`](mutants.json) `proof_kills`: 147
break a named proof or example as written, and Lean refuses the other 16 in the mutated definition itself.

## Seeded bugs (Lean; [`mutants.json`](mutants.json) `seeded`, each with its exact edit)

Each bug was planted alone in a scratch copy, then `VE.Arith.Examples` was built under `timeout 600`; every one
fails:
- S1 and S1b (the plan's bug, in the meaning): a bounded ∃ and a bounded ∀ reach hi + 1. S1 breaks `primeBody_iff`
  and M-5's failure (`Examples.lean:29, 93`); S1b breaks the "1 through 3, each below 4" example (`:61`).
- Admission, each failing its `#guard`: a self or later call admitted (S2: `:124, 130, 131`); a variable one past
  its scope (S3); "for every whole number" counted as bounded (S4: `:116`); extra arguments (S5: `:132`); the
  decoder's order ignored (S6: `:138, 139`); a duplicate name (S7: `:137`); an unbounded count (S8: `:133, 135`);
  the kind of a call ignored (S9: `:129`).

## Tests

- **Selected tests:** `mac-pytest.sh --select -- --base 7855620f3 --run` on the Mac runner: 74 units, 0 failed (HEAD
  `ea8e7e75`). The item adds no pytest file: its tests are the Lean guards and proofs that `lake build` checks.
- **Checks:** `regen_generated.py --check --skip route-cases` (no route changed), `repo_map.py --check`,
  `check_lean_imports.py`, `lean/audit.py` and `trust_map.py --check` pass.
- **Collection:** `gate_collection.py --check --prebuilt`: 0 added, 0 removed, 0 refused, 0 stale, 0 malformed.
- **Full gate:** left to the chain. No test that main-known-red.txt lists failed.

Shared files: `lean/VE.lean` (union), `tools/trust-classes.json` and `docs/trust-baseline.json` (registries). No
branch in flight touches `lean/VE/Arith/` or `lean/ARITH.md`.

**Bytes:** 0 expected (use-case ceiling); nothing is claimed before a pilot audit.

## Next item

- **me-12aa:** restore `Bounded.lean` and the evaluation guards from `wip/me-12aa`, then add `decideBounded_mono`,
  `decideBounded_complete`, 12.5's `decidingValue` with its theorems, and M-6.
- **me-12b** (protocol queue after AP-4): the wire, with `ShadowedVariable` and the refusal texts, plus the runner,
  rows, encoder and mode. EX-1 can start from this item's statement API.

## Sibling lessons (me-2 review)

- F1 (identity parts not pinned): N.A.; nothing here is hashed.
- F2 (decoder checks tested on the refusing side only): each refusal has a refused and an admitted guard. Calls to
  earlier definitions of the right kind and arity are admitted (`:122`); a call of the wrong kind is refused (`:129`).
  The duplicate, scope, recursion, arity and count checks are each admitted by `countDefs` and refused by their own
  guard. S2 to S9 show that each check is read.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer is relayed; no mode or schema (me-12b).
2. PASS: the task's rows above, each with its proof or guard; Bounded and its fixtures moved to me-12aa and
   ShadowedVariable to me-12b by the size rule (named). `git diff main...HEAD` has no Python copy of a Lean decision,
   no report test and no file an in-flight branch edits.
3. PASS: 10 seeded bugs (`mutants.json` `seeded`), each failing a named guard or proof; `trust_mutants.py` exit 0
   with evidence and allow file; each allowed mutant was verified to break a named proof or example
   (`proof_kills`).
4. N.A.: no Python or Rust counterpart exists for `arith@0`.
5. N.A.: no relayed field to bind (me-12b binds rows to statements).
6. PASS: base from `git merge-base`; commits from `main..HEAD --no-merges`; full gate on the final HEAD by the chain.
7. PASS: DELTA row 1 cites R16; `trust_map.py --check` PASS; FOLLOW-UPS row present.
8. PASS: DELTA "Public output: none" (no mode, command, route or Python/Rust product file).
9. PASS: the selection ran 74 units; this item's fixtures are the Lean build's guards and proofs, which S1 to S9
   break.
10. PASS: the statements equal spec 12.1–12.3 after whitespace normalisation; `lean/audit.py` PASS; S1 breaks
    `primeBody_iff` as written.
11. N.A.: no budget in this item (the evaluator's budget is me-12aa's).
12. N.A.: no runtime path; `Examples.lean` builds in about 6 s.
13. PASS: no test removed; `gate_collection.py --check --prebuilt` reports 0 refused, 0 stale and 0 malformed.
