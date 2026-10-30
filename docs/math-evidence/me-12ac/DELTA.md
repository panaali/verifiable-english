# me-12ac delta: the deciding value and M-6

Base `62d8329d4` (`git merge-base HEAD main`). **Public output: none**, so the table has no row:

- **No caller.** me-12ac adds two Lean modules, `lean/VE/Arith/Deciding.lean` and `lean/VE/Arith/DecidingExamples.lean`.
  It also edits `lean/ARITH.md`, `lean/VE.lean` (two imports) and the trust side table. It adds no service mode,
  command, route, schema, Python product code or Rust file, and edits no existing Lean file. It changes no verdict,
  diagnostic, fault order or line a user can see; me-12b puts the deciding value on the wire.
- **Trust budget: +0.** `uv run python tools/trust_map.py --check --since 62d8329d4` passes: K +0, S +0, D +0, G +0,
  unclassified +0, trusted +0. The new definitions are C (`decidingLoop`, `decidingAt`, `decidingValue`, `isPrimeB`,
  `decIsPrime`: executables tied to the meaning by `decidingValue_all`, `decidingValue_ex`, `decidingLoop_iff` and
  `isPrimeB_iff`) or T (fixtures). No R16 allowance is recorded, so no ties-pass row is needed.
  `tools/trust_mutants.py` selects 0 definitions ([`trust-mutants.json`](trust-mutants.json)). Each new definition still
  has a hand mutant, killed by a named proof or guard ([`mutants.json`](mutants.json)).
- **No approved statement changes.** `decidingValue_all`, `decidingValue_ex` and `decidingValue_of_fails`, and
  `decidingValue`'s signature, equal spec 12.5 after whitespace normalisation. `lean_statements.py --check` reports
  0 removed and 0 changed.
