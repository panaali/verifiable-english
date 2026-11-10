# ap-5 delta: specialisation, definitions and generator only (`VE.Acts.Specialise`)

Base: `git merge-base HEAD main`. ap-5 is batch AP-5 of [act-phrases-PLAN.md](../../spec/act-phrases-PLAN.md)
("AP-5. Specialisation: definitions and generator only"); see [REPORT.md](REPORT.md).

**Public output: none.** ap-5 adds `lean/VE/Acts/Specialise.lean` and its fixtures
`lean/VE/Acts/SpecialiseExamples.lean`. Nothing imports them except the library root `lean/VE.lean` and the generated
audit (`grep -rn "VE.Acts.Specialise" lean --include=*.lean`). No service mode, route, request, answer, decoder, pack,
profile, command or diagnostic reaches them, and no Python or Rust product code changes. So there is no user-visible
delta and no row here (the task: "no DELTA row is expected"). The trusted growth, which is not user-visible, is
itemised per file under standing ruling R16 in REPORT.md section 5, as the task asks.

## User-visible deltas

None.
