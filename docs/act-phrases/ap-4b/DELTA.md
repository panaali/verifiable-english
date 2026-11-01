# ap-4b delta: `Source`, `sourceCheck`, `sourceCheck_exact` and `atomSituation` (`VE.Acts.Sources`, `VE.Acts.Situation`)

Base: `git merge-base HEAD main` (`09fca5013`). ap-4b is part 2 of 3 of batch AP-4 of the act-phrases plan
(`docs/spec/act-phrases-PLAN.md` at `80f056f9e`, section 4, "AP-4"; [REPORT.md](REPORT.md)).

**Public output: none.** ap-4b adds two new Lean modules, `lean/VE/Acts/Sources.lean` (`Source`, `sourceCheck`,
`SourceExact`, `sourceCheck_exact`) and `lean/VE/Acts/Situation.lean` (`atomSituation`), and their fixtures in
`lean/VE/Acts/ReadingsExamples.lean`. Only `VE.lean`, `VE/Audit.lean` (generated) and the fixtures import them: no
service mode, route, relay, decoder, command or diagnostic reaches them (ap-4 adds the `act-readings` mode and the
admission hook in `lean/VE/Readings/Run.lean`). No file under `lean/VE/Readings/`, `lean/VE/Service/`, `ve/` or `rust/`
changes. No verdict, diagnostic, fault order, English line or CPU figure changes, so the only row is the trust growth.
`sourceCheck`'s own refusals (none shown yet) are in REPORT.md, "Deviations" 2, in their order; review F1 added the
choice limit (`ResourceLimit` above 64 choices) between D-32 and D-29.

## User-visible deltas

Trust growth, re-measured on the final code with `uv run python tools/trust_map.py --check`: K +0, S +68, D +0,
G +65 (tied +48), unclassified +0, trusted +83 against the merge base. It is recorded as two allowances (S 68, V 15)
in `docs/trust-baseline.json` with `trust_map.py --allow`, and `trust_map.py --check` passes. `sourceCheck`,
`compareViews`, `pick` and `viewsOn` are G[V], tied to `sourceCheck_exact`, `compareViews_ok`, `pick_forall₂` and
`viewsOn_choices`, so they are not trusted. The ties-pass row R16 asks for is in manage-agents FOLLOW-UPS.md, section "## ap-4b".

| # | File | Trusted lines (class: declarations) | Exercised by | Ruling |
|---|---|---|---|---|
| 1 | `lean/VE/Acts/Sources.lean`, `lean/VE/Acts/Situation.lean` | Sources.lean +68, all S: `Source`, `View`, `ruleView`, `expected`, `choicesOn`, `choiceRules`, `choiceViews`, `readingViews`, `opOfSource`, `SourceExact`, `List.Forall₂`; Situation.lean +15, untied G[V]: `atomSituation`, `rulePred`. K +0; total 83 ≤ 150 | `sourceCheck_exact` (statement EQUAL to spec 7, [check_statements.py](check_statements.py)); ReadingsExamples guards S1 to S8, F11, the template and rule guards, the projection, the largest sizes and the choice limit (F1), D-29's texts and `atomSituation` through `separates` both ways. Every new trusted definition has a plant a guard or theorem kills ([mutants.json](mutants.json): 36 plants, all killed); `tools/trust_mutants.py` ([trust-mutants.json](trust-mutants.json), allow reasons in [trust-mutants-allow.json](trust-mutants-allow.json); numbers in the REPORT) | R16 |
