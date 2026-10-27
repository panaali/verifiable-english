# qt-a3 delta: the `ve-cardinality@1` decoders

Base: `git merge-base HEAD main` (`110b3bf3a`, after the sync; the build began at `25ac41311`). qt-a3 is the first
part of batch QT-A3 of [quantities-PLAN.md](../../spec/quantities-PLAN.md); what it does not deliver is named in
[REPORT.md](REPORT.md).

**No answer, text, availability or verdict changes.** No service mode, route or document hook reaches
`lean/VE/Cardinality/Wire.lean` yet (the mode is qt-a3c): `lean/checkers.lock` is the base's, so the `ve_service`
build is unchanged, and `tools/regen_generated.py --check` regenerates `lean/VE/Route/examples/route-cases.json`
byte-identically. The one delta is the trusted base.

## User-visible deltas

| # | Delta | Evidence and tests | Ruling |
|---|---|---|---|
| 1 | Trust growth, re-measured on the final tree with `uv run python tools/trust_map.py --check` against `110b3bf3a`: K +0, S +0, untied V +124, recorded as two allowances in `docs/trust-baseline.json` (+51, then +73 for fix1). Per file: `lean/VE/Cardinality/Wire.lean` +124, all D[V]: `decodeEnvironment` 17, `elabBody` 12, `elabOperand` 12, `elabRatio` 12, `decodeStatement` 12, `finiteSorts` 10, `projectW6` 8, `arrayDepth` 6, `sourceFits` 6, `items` 5, `elabRule` 5, `printed` 5, `elabName` 5, `profileLists` 3, `ruleNames` 3, `cmpNames` 2, `relNames` 1. Fix1 (review F1) moved the elaborators' parts from C to D[V], as W6a classes `elabTerm` (`elabFormula` stays C, as W6a's does), and added S2's depth (review F2). `CardEnv` and `CAdmission` are tied by `CAdmission.sound`. The FOLLOW-UPS rows "## qt-a3" and "## qt-a3 fix1" ask for the ties pass ([evidence/follow-ups-row.md](evidence/follow-ups-row.md)) | every new trusted definition is stated about by a theorem of `lean/VE/Cardinality/WireTheorems.lean` (`tests/test_cardinality_exercised.py`, including `test_each_qt_a3_f1_helper_is_trusted_and_stated_about_by_its_theorem`) and has a seeded bug that a `#guard` of `lean/VE/Cardinality/WireExamples.lean` fails ([mutants.json](mutants.json), 32 of 32 killed, [evidence/mutants-run.json](evidence/mutants-run.json)); the mechanical mutants of `tools/trust_mutants.py` on `290c6a591` in [trust-mutants.json](trust-mutants.json): 114 KILLED, 0 SURVIVOR, 0 UNKNOWN, 8 INVALID, 69 ALLOWED, exit 0, each allowed one with its reason in [trust-mutants-allow.json](trust-mutants-allow.json) | SIGNED by standing ruling R16 (DRI-RULINGS.md) |
