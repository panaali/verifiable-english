# me-12aa delta: the budgeted evaluator of `arith@0`

Base `22dad00fd` (`git merge-base HEAD main`). **Public output: none**, so the table has no row:

- **No caller.** me-12aa adds two Lean modules (`lean/VE/Arith/Bounded.lean`, `lean/VE/Arith/BoundedExamples.lean`)
  and edits `lean/ARITH.md`. It adds no service mode, command, route, schema, Python product code or Rust file. No
  verdict, diagnostic, fault order or line a user can see changes. `arithOutcome`'s rows reach users only through
  me-12b's runner.
- **Trust budget: +0.** `uv run python tools/trust_map.py --check --since 22dad00fd` passes with K +0, S +0 and
  untied V +0. The G +11 lines are `arithOutcome`, a G[V] tied to its three theorems, and `maxSteps`, a G[R]. The
  evaluator is C and `Agrees` is P. No R16 allowance is recorded, so no ties-pass row is needed.
  `tools/trust_mutants.py` selects 0 definitions ([`trust-mutants.json`](trust-mutants.json)). Every new definition
  still has a hand mutant that a named guard kills ([`mutants.json`](mutants.json)).
- **No approved statement changes.** `charge`, `quantLoop`, `countLoop`, `OpEnv`, `Term.evalB`, `Term.evalBs`,
  `Formula.evalB`, `Defs.opEnv`, `maxSteps`, `decideBounded`, `arithOutcome`, `decideBounded_sound`,
  `decideBounded_work` and `arithOutcome`'s three theorems equal spec 12.2 after whitespace normalisation. me-12a's
  statements are unchanged: the generated `lean/statements.txt` adds 128 lines and removes none, and
  `lean_statements.py --check` passes. In `declarations.txt` only the hashes of `VE` and `VE.Audit` change, because
  each imports the new modules.
