# sc-10a delta

No answer changes: no route, wire, Python or English reads the new definitions before SC-11 (bytes 0). The one row is
the trust budget, which R16 asks to itemise per file.

| Input | Before | After | Ruling | Evidence |
| --- | --- | --- | --- | --- |
| Trusted Lean lines (`uv run python tools/trust_map.py --check` against 8c28fe28635a) | K 994, S 12210, untied V 44053 | K +0, S +0, untied V +12: `lean/VE/Readings/SoftSup.lean` +12 (`supX`, `sharedEnvSD`, `supCertificateCheckSD`, G[V] untied; `pullF` G[V] tied to `fill_sim` and `fill_sim_author`; `FillLite` P) | SIGNED by standing ruling R16 (DRI-RULINGS.md), sc-10a, 2026-10-31 | Allowance in `docs/trust-baseline.json`; each definition exercised by `#guard`s of `lean/VE/Readings/SoftSupExamples.lean` that fail under its mutants (`docs/rd-9/sc-10a/mutants.json` M1, M3, M5, M6; `docs/rd-9/sc-10a/trust-mutants.json`: 30 KILLED, 1 ALLOWED); ties pass filed in FOLLOW-UPS.md under `## sc-10a` |
