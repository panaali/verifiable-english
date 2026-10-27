# qt-a3b delta: the cardinality certificate check and case runner

Base: `git merge-base HEAD main` (`a274d9488`). qt-a3b is the second part of batch QT-A3 of
[quantities-PLAN.md](../../spec/quantities-PLAN.md); what it does not deliver is named in [REPORT.md](REPORT.md).

**No answer, text, availability or verdict changes.** No service mode, route or document hook reaches
`lean/VE/Cardinality/Run.lean` yet (the `cardinality` mode is qt-a3c). `lean/VE/Time/Wire.lean` changes, so the
`ve_service` build and `lean/checkers.lock` change, but only by moving code into named helpers W6a owns
(`statementIds`, `quantityLimits.aggregate`, `staleW6`, `staleCore`): W6a's 37 recorded `quantity` cases of
`tests/data/route-cases.jsonl`, run through `VE.Service.runMode .quantity` on a build of the base and on this branch,
give byte-identical answers (SHA-256 of the 37 compressed rows, one per line:
`e2d720ea903ef1fbeaf0dad1e7433617fcdae8208efe70e8ece3e2a0522d89e6` on both; 29 `ok`, 8 `error`, 2 `valid: true`,
2 `valid: false`). The one delta is the trusted base.

## User-visible deltas

| # | Delta | Evidence and tests | Ruling |
|---|---|---|---|
| 1 | Trust growth, measured on the final tree with `uv run python tools/trust_map.py --check` against `a274d9488`: K +0, S +0, untied V +44, recorded as one allowance in `docs/trust-baseline.json`. Per file: `lean/VE/Cardinality/Run.lean` +46 (D[V] `CardCertificate` 6, `decodeCertificate` 11; G[V] `runCase` 23, `runCaseReported` 6); `lean/VE/Time/Wire.lean` −2 (`decodeQuantity`'s identities moved to W6a's `statementIds`, D[I]). `checkCertificate` is tied to `checkCertificate_sound`. The FOLLOW-UPS row "## qt-a3b" asks for the ties pass | every new trusted definition is stated about by a theorem (`checkCertificate_sound` in `Run.lean`; `decodeCertificate_sound`, `runCaseReported_ok`, `runCaseReported_error` in `RunTheorems.lean`; `tests/test_cardinality_exercised.py`) and has a seeded bug that a `#guard` of `lean/VE/Cardinality/RunExamples.lean` fails ([mutants.json](mutants.json), 25 of 25 killed, [evidence/mutants-run.json](evidence/mutants-run.json)); the mechanical mutants of `tools/trust_mutants.py` in [trust-mutants.json](trust-mutants.json): 60 KILLED, 0 SURVIVOR, 2 ALLOWED (they do not elaborate; [trust-mutants-allow.json](trust-mutants-allow.json)) | SIGNED by standing ruling R16 (DRI-RULINGS.md) |
