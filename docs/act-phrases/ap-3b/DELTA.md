# ap-3b delta: rendering and paraphrases (`VE.Acts.Linearize`, `VE.Acts.Table`'s paraphrase section)

Base: `git merge-base HEAD main` (`0e7a813e8`). ap-3b is the second part of batch AP-3 of
[act-phrases-PLAN.md](../../spec/act-phrases-PLAN.md) (section 4, "AP-3"); see [REPORT.md](REPORT.md).

**Public output: none.** ap-3b adds `lean/VE/Acts/Linearize.lean` and the paraphrase section of
`lean/VE/Acts/Table.lean`, with fixtures in `TableExamples.lean`. Nothing imports them except `Table.lean`, its
fixtures and the library root `lean/VE.lean`. No service mode, route, decoder, command or diagnostic reaches them, and
`_lean_route` is unchanged. No Python or Rust product code changes. No verdict, diagnostic, fault order, English line
or CPU figure changes, so the only row is the trust growth. The paraphrase definitions (`paraphrase`, `paraphrases`,
`distinctTexts` and their helpers) are G[R], which is not trusted.

## User-visible deltas

Trust growth, re-measured with `uv run python tools/trust_map.py --check` on the final code: K +0, S +46, V +0,
trusted +46, against the merge base. It is recorded as one allowance (S 46) in `docs/trust-baseline.json` with
`trust_map.py --allow`, and `trust_map.py --check` passes. The ties-pass row R16 asks for is in manage-agents
FOLLOW-UPS.md, section "## ap-3b".

| # | File | Trusted lines (class: declarations) | Exercised by | Ruling |
|---|---|---|---|---|
| 1 | `lean/VE/Acts/Linearize.lean` | +46, S: `joinWord`, `Part.toks`, `listToks`, `Filler.toks`, `Atom.normal`, `tokStr`, `tokText`, `Atom.withTo`, `Atom.text`, `partAct` (spec 5.5) | the `#guard`s of `TableExamples.lean`'s "Renderings" and "Paraphrases" sections (G6's and G7's parts, *to* exactly when plain, A19's canonical fixed phrase, lists of 0 to 4 parts by each join word, the order adverbs, object, marked arguments, modifiers; E9's D-23 text and P12n's four texts exactly); [`mutants.json`](mutants.json): 36 seeded bugs, at least one in each new definition, all killed, and the constructor sweep (105 rows: 21 killed, 84 refused by Lean); [`trust-mutants.json`](trust-mutants.json): 173 killed, 0 survivor, 0 unknown, 16 invalid, 25 allowed ([`trust-mutants-allow.json`](trust-mutants-allow.json): 5 equivalent `take 1` survivors, 20 that do not elaborate) | SIGNED by standing ruling R16 (DRI-RULINGS.md) |
