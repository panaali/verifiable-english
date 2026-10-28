# ap-2b delta: the act grammar's rule table and `grammar_wf` (`VE.Acts.Grammar`)

Base: `git merge-base HEAD main`. ap-2b is the second part of batch AP-2 of
[act-phrases-PLAN.md](../../spec/act-phrases-PLAN.md) (section 4, "AP-2"); the meaning is ap-2c and rendering ap-2d
([REPORT.md](REPORT.md)).

**Public output: none.** ap-2b adds `lean/VE/Acts/Grammar.lean` (the rule table of spec 5.2, `grammar`,
`grammar_wf`) and its fixtures `lean/VE/Acts/RuleExamples.lean`. Nothing imports them except the library root
`lean/VE.lean` and the generated audit. No service mode, route, decoder, command or diagnostic reaches them. No Python
or Rust product code changes. No verdict, diagnostic, fault order, English line or CPU figure changes, so the only row
is the trust growth.

## User-visible deltas

Trust growth, re-measured with `python3 tools/trust_map.py --check` on the final code: K +0, S +126, untied V +14,
trusted +140, against the merge base; recorded as two allowances (S 126, V 14) in `docs/trust-baseline.json` with
`trust_map.py --allow`, and `trust_map.py --check` passes. The ties-pass row R16 asks for is in manage-agents
FOLLOW-UPS.md, section "## ap-2b". Line numbers are `lean/VE/Acts/RuleExamples.lean`'s.

| # | File | Trusted lines (class: declarations) | Exercised by | Ruling |
|---|---|---|---|---|
| 1 | `lean/VE/Acts/Grammar.lean` | +140. S +126: `frameRules` 44, `globalRules` 18, `NT` 9, `FNT` 8, `Core` 6, `RuleS` 6, `items` 6, `fillExcl` 6, `RSym` 4, `tail` 4, `schema` 4, `closed` 4, `grammar` 3, `kwSyms` 2, `many1` 2. G[V] +14 untied: `build` 9, `RSym.nt?` 5. `NT.rank` (12) is G[V] tied to `schema_ranked` | `#guard`s 36-63 (the raw counts of G5 to L0, spec 11.2), 68 (G5's derivation order), 77 (the 13 `ap0` rows, 11.2b), 97-109 (`grammar_wf` on both sides: FR1, an empty head, one-word markers and heads, FR2's doubled count), 164-174 (a corpus over a frame of each shape whose derivations use every rule but the six nothing reaches, each count pinned), 182-191 (two-element lists, each element at either end, on both sides), 202-208 (every word a filler excludes, refused frame by frame, the table tied to `fillExcl`: review F1), 212 (the `X → never` rules); `grammar_wf` and `schema_ranked`, proved; [`mutants.json`](mutants.json): 21 seeded bugs, one per definition and per claimed behaviour, 16 killed by a `#guard` with the proofs cut and 5 data-type mutants refused by Lean in the trusted file ([`seed_bugs.py`](seed_bugs.py)); [`trust-mutants.json`](trust-mutants.json): 1039 killed (with `list-drop-middle`), 0 survivor, 0 unknown, 52 invalid, 96 allowed, each with its reason in [`trust-mutants-allow.json`](trust-mutants-allow.json) (80 ill-typed cuts, 16 equivalent) | R16 (standing ruling, DRI-RULINGS.md) |
