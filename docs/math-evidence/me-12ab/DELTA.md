# me-12ab delta: the evaluator's monotonicity and completeness

Base `a557ff887` (`git merge-base HEAD main`). **Public output: none**, so the table has no row:

- **No caller.** me-12ab adds proofs to `lean/VE/Arith/Bounded.lean` and one fixture module,
  `lean/VE/Arith/CompleteExamples.lean`. It also edits `lean/ARITH.md`, `lean/VE.lean` (one import) and the trust side
  table. It adds no service mode, command, route, schema, Python product code or Rust file. It changes no evaluator
  definition, verdict, diagnostic, fault order or line a user can see.
- **Trust budget: +0.** `uv run python tools/trust_map.py --check --since a557ff887` passes: K +0, S +0, D +0, G +0,
  unclassified +0, trusted +0. The four new definitions (`Extends`, `Total`, `Site.Ok`, `Def.SitesOk`) and the
  `sub_sites` macro (`subSites`) are P, proof helpers. No R16 allowance is recorded, so no ties-pass row is needed.
  `tools/trust_mutants.py` selects 0 definitions ([`trust-mutants.json`](trust-mutants.json)). Each new definition still
  has a hand mutant, killed by a named proof or guard ([`mutants.json`](mutants.json)).
- **No approved statement changes.** `decideBounded_mono` and `decideBounded_complete` equal spec 12.2 (main
  0e7a813e8) after whitespace normalisation. `decideBounded_sound`, `decideBounded_work`, the evaluator and
  `arithOutcome`'s theorems are unchanged. `lean_statements.py --check` passes. The generated `lean/statements.txt`
  only adds theorems; in `declarations.txt` only the source hashes of `VE.Arith.Bounded`, `VE` and `VE.Audit` change.
