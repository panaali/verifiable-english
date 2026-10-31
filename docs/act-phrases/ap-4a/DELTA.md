# ap-4a delta: the edge rule's kinds, `modifier_edges` and `phraseReadings` (`VE.Acts.Grammar`, `VE.Acts.Readings`)

Base: `git merge-base HEAD main` (`0c4ea31d2`, main with ap-2bb merged). ap-4a is part 1 of 3 of batch AP-4 of the act-phrases plan
(`docs/spec/act-phrases-PLAN.md` at `80f056f9e`, section 4, "AP-4"; [REPORT.md](REPORT.md)).

**Public output: none.** ap-4a gives each rule of the act grammar's table a kind (`RuleS.kind`: `shape`, or an edge's
attachment `first`, `last` or `all`), proves where the table writes them (`modifier_edges`), and has the meaning read
an edge's `all` from its kind instead of from the rule's position. The rules' sides and order are unchanged, so every
derivation and meaning AP-2 gave is unchanged: every `RuleExamples` and `MeaningExamples` guard passes (`lake build`,
1181 jobs on the merged tree, exit 0). It adds `phraseReadings`, `phraseReadings_exact`, `_nodup`, `_length` and `table_length` to
`lean/VE/Acts/Readings.lean`, and the fixtures in `lean/VE/Acts/ReadingsExamples.lean`. No service mode, route, relay,
decoder, command or diagnostic reaches `phraseReadings` or the kinds (plan G17: AP-7 runs on `phraseReadings` first).
No Python or Rust product code changes. No verdict, diagnostic, fault order, English line or CPU figure changes, so
the only row is the trust growth.

## User-visible deltas

Trust growth, re-measured on the final code with `uv run python tools/trust_map.py --check`: K +0, S +31, D +0,
G +9 (tied +9), unclassified +0, trusted +31 against the merge base. It is recorded as one allowance (S 31) in
`docs/trust-baseline.json` with `trust_map.py --allow`, and `trust_map.py --check` passes. `phraseReadings` is G[V],
tied to `phraseReadings_exact`, so it is not trusted. The ties-pass row R16 asks for is in manage-agents
FOLLOW-UPS.md, section "## ap-4a".

| # | File | Trusted lines (class: declarations) | Exercised by | Ruling |
|---|---|---|---|---|
| 1 | `lean/VE/Acts/Grammar.lean` | +31, all S: `Attach`, `Kind`, `RuleS`'s `kind` field, the kinds `globalRules` writes on `E1X`'s two rules and `frameRules` on each trailing edge's two (`two`), `attachOf`, `edgeLhs`; the other rules gain `.shape` | `modifier_edges` (Grammar.lean); ReadingsExamples guards 32-48 (A5, A8 to A12, P9m, P12n), 83 (edge sides), 88-92 (`edgeLhs`, `attachOf` both ways), 98 (`closed`'s never rules); MeaningExamples 184-186 (`edgeOnly`, 17 `all` rules on V5) and every meaning guard (the meaning reads the kinds). Each new trusted definition has a plant a guard or theorem kills ([mutants.json](mutants.json): 15 plants, all killed); `tools/trust_mutants.py` exits 0 ([trust-mutants.json](trust-mutants.json): 382 killed, 16 invalid, 34 ill-typed cuts allowed with reasons in [trust-mutants-allow.json](trust-mutants-allow.json), 0 survivors, 0 unknown) | R16 |
