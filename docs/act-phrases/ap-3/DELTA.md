# ap-3 delta: act trees, ops and the modal × connective table (`VE.Acts.Tree`, `VE.Acts.Table`)

Base: `git merge-base HEAD main`. ap-3 is the first part of batch AP-3 of
[act-phrases-PLAN.md](../../spec/act-phrases-PLAN.md) (section 4, "AP-3"); the rest is ap-3b and ap-3c
([REPORT.md](REPORT.md)).

**Public output: none.** ap-3 adds two modules, `lean/VE/Acts/Tree.lean` (the act trees) and
`lean/VE/Acts/Table.lean`, with the fixtures `TableExamples.lean`. Nothing imports them except the library root
`lean/VE.lean`. No service mode, route, decoder, command or diagnostic reaches them; `_lean_route` is unchanged. No
Python or Rust product code changes. No verdict, diagnostic, fault order, English line or CPU figure changes, so the
only row is the trust growth.

## User-visible deltas

Trust growth, re-measured with `uv run python tools/trust_map.py --check` on the final code: K +0, S +64, V +0,
trusted +64, against the merge base; recorded as one allowance (S 64) in `docs/trust-baseline.json` with
`trust_map.py --allow`, and `trust_map.py --check` passes. The ties-pass row R16 asks for is in manage-agents
FOLLOW-UPS.md, section "## ap-3". Line numbers are `lean/VE/Acts/TableExamples.lean`'s.

| # | File | Trusted lines (class: declarations) | Exercised by | Ruling |
|---|---|---|---|---|
| 1 | `lean/VE/Acts/Table.lean` and `lean/VE/Acts/Tree.lean` | Table.lean +38, S: `Simple`, `Op`, `opOf`, `freeTable`, `table`. Tree.lean +26, S: `Join`, `Part`, `Filler`, `Modifier`, `Atom`, `Act` (the act trees of spec 1.5, 5.4) | `#guard`s 60-65 (`opOf`, every role and sign), 70-115 (`table` and `freeTable`: T1-T10 on G6, G7, G9, G10, G11, G12, G14v and every cell of plan 2.3), the 14 `table_*` theorems (each cell's equation, proved); the act trees by every fixture; [`mutants.json`](mutants.json): 16 seeded bugs, all killed, and the op sweep (20 killed, 28 refused by Lean); [`trust-mutants.json`](trust-mutants.json): 159 killed, 0 survivor, 0 unknown, 26 allowed (each does not elaborate, [`trust-mutants-allow.json`](trust-mutants-allow.json)) | SIGNED by standing ruling R16 (DRI-RULINGS.md) |
