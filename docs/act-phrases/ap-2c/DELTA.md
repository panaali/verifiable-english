# ap-2c delta: the meaning, `readings`, `read` and `analyse` (`VE.Acts.Meaning`, `VE.Acts.Readings`)

Base: `git merge-base HEAD main`. ap-2c is the third part of batch AP-2 of
[act-phrases-PLAN.md](../../spec/act-phrases-PLAN.md) (section 4, "AP-2"); rendering is ap-2d ([REPORT.md](REPORT.md)).

**Public output: none.** ap-2c adds `lean/VE/Acts/Meaning.lean`, `lean/VE/Acts/Readings.lean` and their fixtures
`lean/VE/Acts/MeaningExamples.lean`. Nothing imports them except the library root `lean/VE.lean` and the generated
audit. No service mode, route, decoder, command or diagnostic reaches them. No Python or Rust product code changes. No
verdict, diagnostic, fault order, English line or CPU figure changes, so the only row is the trust growth.

## User-visible deltas

Trust growth, re-measured with `python3 tools/trust_map.py --check` on the final code: K +0, S +110, untied V +25,
trusted +135, against the merge base; recorded as two allowances (S 110, V 25) in `docs/trust-baseline.json` with
`trust_map.py --allow`, and `trust_map.py --check` passes. The ties-pass row R16 asks for is in manage-agents
FOLLOW-UPS.md, section "## ap-2c". Line numbers are `lean/VE/Acts/MeaningExamples.lean`'s.

| # | File | Trusted lines (class: declarations) | Exercised by | Ruling |
|---|---|---|---|---|
| 1 | `lean/VE/Acts/Meaning.lean`, `lean/VE/Acts/Readings.lean` | +135. Meaning.lean +128: S +110 (`applyRule` 38, `piecesOf` 13, `atomOk` 9, `Piece` 7, `singleAct` 7, `coordAct` 7, `meaning` 7, `addPiece` 6, `joinAct` 5, `Att` 4, `actOk` 4, `Elt` 3), G[V] +18 untied (`itemOf` 6, `listOf` 5, `Atom.add` 4, `baseAtom` 3). Readings.lean +7, G[V] untied (`readings` 2, `read` 2, `analyse` 3); `Derived` (3) is G[V] tied to `derived_iff` | `#guard`s 33-68 (G5 to L0 by value, spec 11.2, and `analyse`), 78-85 (joins and shared elements), 90 (11.2b's meaning counts under D9 (i)), 112-124 (D9 (i) on both sides), 131-142 (`atomOk`, `actOk`), 148-171 (each list a check reads, at both ends), 183-185 (the edges' second rules). Every new trusted definition has a mutant a guard kills ([mutants.json](mutants.json): 36, 32 killed and 4 refused); `tools/trust_mutants.py` exits 0 ([trust-mutants.json](trust-mutants.json): 352 killed, 66 invalid, 86 allowed with reasons in [trust-mutants-allow.json](trust-mutants-allow.json), 0 survivors) | R16 |
