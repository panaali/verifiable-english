# ap-4bb delta: `sourceCheck_complete`, `View`'s soft fields, the `atomSituation` tie (`VE.Acts.Sources`, `VE.Acts.SourcesProofs`, `VE.Acts.Situation`)

Base: `git merge-base HEAD main` (`97b3c7999a`). ap-4bb carries the FOLLOW-UPS rows "## ap-4b (2026-10-31)" (ties
pass) and "## ap-4b round 1" (ap-4b-f2); [REPORT.md](REPORT.md) has the deliverables and evidence.

**Public output: none.** No service mode, route, relay, decoder, command or diagnostic reaches `sourceCheck`,
`View` or `atomSituation` on this base: `grep -rln "sourceCheck\|atomSituation" lean/VE ve rust` lists only
`lean/VE/Acts/{Sources,SourcesProofs,Situation,ReadingsExamples,Run}.lean` and `lean/VE/Audit.lean`, and `Run.lean`
names `sourceCheck` only in a comment (line 95). No file under `lean/VE/Readings/`, `lean/VE/Service/`, `ve/` or
`rust/` changes. Every existing fixture keeps its answer: S1-S8, the 64-choice boundary, the choice limit and F11
are the same `#guard`s as on the base (`cd lean && lake build VE.Acts.ReadingsExamples` passes; `git diff
$(git merge-base HEAD main) -- lean/VE/Acts/ReadingsExamples.lean` adds lines and changes one import line, it removes
no guard).

## Deltas

| # | File | Change | Evidence | Ruling |
|---|---|---|---|---|
| 1 | `lean/VE/Acts/SourcesProofs.lean`, `docs/spec/act-phrases.md` 7 | Spec 7's `sourceCheck_complete` is stated with the added hypothesis `hn : (VE.Readings.choices D).length ≤ VE.Readings.maxChoices` (an approved statement changed); spec 7 gets `hn` and one sentence citing item 8c and the counterexample | (A) `sourceCheck_complete_needs_bound` (`SourcesProofs.lean:40-52`): `SourceExact` holds and `sourceCheck` is `ResourceLimit` whenever the cut part passes D-29 and the choices exceed 64; its decidable premises hold on S4 beside six sets (128 choices, cut at 65) by the `#guard` at `ReadingsExamples.lean:287`. Statement gate: `python3 docs/act-phrases/ap-4bb/check_statements.py`, 14 EQUAL. Plant `hn-dropped` KILLED ([mutants.json](mutants.json)) | SIGNED by the DRI 2026-11-02 (reviews/dri-decisions-20261102-followup-triage.md item 8c) |
| 2 | `lean/VE/Acts/Sources.lean`, `docs/spec/act-phrases.md` 7 | `View`, `ruleView` and `expected` also compare `SoftNode`'s `mode`, `rank`, `alterable`, `exception` and `hard`; `expected` reads them from `VE.Readings.strictNodeOf s.template` (reviews/dri-decisions-20261111-ap-4bb.md item 1). A choice that changes only one of them is refused with D-29's third text, where the base passed it | Failing-first fixture `ReadingsExamples.lean:319` (S4's document, strict to default, refused with D-29's third text; plant `ruleView-no-mode` KILLED); `:320` the four other fields (plants `ruleView-no-hard`, `view-drops-alterable` KILLED); `:324` `expected`'s fields equal `strictNodeOf`'s on S4's source (plant `strictNodeOf-default` KILLED) | SIGNED by the DRI 2026-11-10 (reviews/dri-decisions-20261110-ap-4b-f2.md item 1) |
| 3 | `lean/VE/Acts/Sources.lean`, `lean/VE/Acts/Situation.lean` | Trust, `uv run python tools/trust_map.py --check` against `97b3c7999add`: K +0, S +5, D +0, G +0, tied +15, trusted -10 (Sources.lean +5: `View`, `ruleView`, `expected`; Situation.lean -15: `atomSituation`, `rulePred` now tied). Recorded in `docs/trust-baseline.json` with `trust_map.py --allow` | Every changed trusted definition has a plant a guard kills ([mutants.json](mutants.json): `View`, `ruleView`, `expected`); `tools/trust_mutants.py` selects 0 mechanical mutants on the changed lines ([trust-mutants.json](trust-mutants.json)) | R16 |
