# ap-2 delta: the act grammar's vocabulary, terminals and listing (`VE.Acts.Syntax`, `VE.Acts.Read`)

Base: `git merge-base HEAD main`. ap-2 is the first part of batch AP-2 of
[act-phrases-PLAN.md](../../spec/act-phrases-PLAN.md) (section 4, "AP-2"); the rest is ap-2b ([REPORT.md](REPORT.md)).

**Public output: none.** ap-2 adds three Lean modules under `lean/VE/Acts/` and nothing imports them except the
library root `lean/VE.lean`. It registers no service mode, route, command or diagnostic that any request reaches:
the D-31 texts of `checkVocab` are raised only when AP-3's `VE.Acts.Wire.decodeVocab` calls it. No Python or Rust
product code changes. `tools/layer_policy.py` places `VE.Acts.*` in layer 3 beside `VE.Grammar.*`, which it imports.
No verdict, diagnostic, fault order, English line or CPU figure changes, so none of these is a row below.

## User-visible deltas

Trust growth, re-measured with `python3 tools/trust_map.py --check` on the final code: K +0, S +69, untied V +76,
trusted +145 (tied +15), against the merge base; recorded as two allowances (S 69, V 76) in
`docs/trust-baseline.json` with `trust_map.py --allow`, and `trust_map.py --check` passes. R16's cap is 150 lines per
item, none in K. The ties-pass row R16 asks for is in manage-agents FOLLOW-UPS.md, section "## ap-2". Line numbers
in the table are `lean/VE/Acts/GrammarExamples.lean`'s; the seeded bugs that make these checks fail are in
[`mutants.json`](mutants.json) (`seed_bugs.py`).

| # | File | Trusted lines (class, declaration: lines) | Exercised by | Ruling |
|---|---|---|---|---|
| 1 | `lean/VE/Acts/Syntax.lean` and `lean/VE/Acts/Read.lean` | Syntax.lean +109: S 45 (`Lexical.Tok` 4, `Lexical.joinWords` 2, `Lexical.clauseWords` 3, `Frame` 9, `Vocab` 6, `Term` 8, `Term.accepts` 10, `framesOk` 3); D[V] 53 (`checkVocab`); G[V] 11 (`instAcceptsTermTok` 2, `wordsOf` 2, `wordOk` 2, `firstDup` 5). Read.lean +36: S 24 (`rawCap` 2, `stepBudget` 2, `maxReadings` 3, `Listing` 4, `firsts` 5, `ReadOutcome` 4, `DerivedIn` 4); G[V] 12 untied (`readingsIn` 4, `readIn` 8). `listing` (9) and `valueOf` (6) are G[V] tied to `listing_ok`/`listing_limit` and `valueOf_eq_some`, so not trusted | `#guard`s 26-34 (LG1-LG8, `firsts`), 60-72 (D2's three values pinned, `Term.accepts` through the parse, `rawCap` at 255 and 256 derivations, `maxReadings` at 63, 64 and 65 readings, `stepBudget` and N at 0, `readIn`'s `ok`, `none`, `many` and `limit`), 76 (every `Term.accepts` case), 96-285 (every D-31 text of `checkVocab` and every pair of rows in D-31's order, both sides of 31a, each half of `wordOk`, 31l, 31q and 31r, every reserved word in each position, with `firstDup`, `wordsOf`, `clauseWords` and `joinWords`; FR1, FR2, FR6; 189-285, the faults in a later element, at the other end of a list and on the marker list 1.4 names that the generated mutants need: for every list the generator types from `Syntax.lean`'s declarations, each list-valued name, operand of `++`, binding value and list a `flatMap`'s function builds, cut in each of four ways (its first element alone, its last element alone, without its first, without its last), and each marker list swapped, `ms f`'s operands included), 313 (FR7: `framesOk` on every vocabulary of spec 11.2, 11.2b and the measurement); `DerivedIn` by the proofs of `readingsIn_exact`, `readIn_unique`, `readIn_none` and `readIn_many`; seeded bugs 1-9 and the 463 mutants of `tests/test_acts_vocab_mutants.py` (448 killed, 15 equivalent, each with its reason) | SIGNED by standing ruling R16 (DRI-RULINGS.md) |
