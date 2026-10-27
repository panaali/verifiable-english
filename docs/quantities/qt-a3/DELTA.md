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
| 1 | Trust growth, re-measured on the final tree with `uv run python tools/trust_map.py --check` against `110b3bf3a` (the same against `25ac41311`): K +0, S +0, untied V +51, recorded as one allowance in `docs/trust-baseline.json`. Per file: `lean/VE/Cardinality/Wire.lean` +51 (D[V] `decodeEnvironment` 17, `decodeStatement` 13, `finiteSorts` 10, `projectW6` 8, `profileLists` 3); `CardEnv` and `CAdmission` are tied by `CAdmission.sound`. The FOLLOW-UPS row "## qt-a3" asks for the ties pass | every new trusted definition has a seeded bug that a `#guard` of `lean/VE/Cardinality/WireExamples.lean` fails ([mutants.json](mutants.json), 18 of 18 killed, [evidence/mutants-run.json](evidence/mutants-run.json)); each is stated about by a theorem of `lean/VE/Cardinality/WireTheorems.lean` (`tests/test_cardinality_exercised.py`); the mechanical mutants of `tools/trust_mutants.py` in [trust-mutants.json](trust-mutants.json): 58 KILLED, 0 SURVIVOR, 0 UNKNOWN, 29 ALLOWED, each with its reason in [trust-mutants-allow.json](trust-mutants-allow.json) | SIGNED by standing ruling R16 (DRI-RULINGS.md) |
