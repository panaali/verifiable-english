# ar-10a delta: the profile-gate table

No verdict moves. On every list of legacy profiles `gateOf profileTable` is `dispatch` (verdict, refusal text, fault
order and route: `VE.Compose.gate_legacy`), and on every list of registered profiles `gateOf baseRows` is `today`
(`VE.Compose.baseGate_today`). Only lists that name a profile the table does not register change, in their text.

| # | Change | Where | Test | Ruling |
|---|---|---|---|---|
| 1 | Fault order. A list with a profile the gate does not register is refused for that profile (`UnsupportedProfile: Unsupported profile p`, the first such `p` in the list) before any row's check; today's gate first ran its alternatives@0 and risk@0 checks (4.2 checks 2 to 5). For an environment, every wrapper but `readings@1` is such a profile, as before. Example: `["alternatives@0", "relational-fol@0", "zzz@0"]` was `alternatives@0 requires norms@0`. Reached by the environment mode and every mode that decodes an environment (`Service.Standalone`), and by the readings route's environment (`Readings.Wire.decodeEnvironment`). | `lean/VE/Compose/Dispatch.lean` `gateOf` | `lean/VE/Compose/Examples.lean` `#guard`s at lines 234 to 238 | SIGNED by standing ruling R2 (DRI-RULINGS.md) |
| 2 | Trust budget: K +0, S +18, untied V +49 (67 lines), recorded with `tools/trust_map.py --allow` in `docs/trust-baseline.json`; per declaration in REPORT.md "Trust". Every new trusted definition has a mutant that a `#guard`, an `example` or a test catches with the proofs stubbed ([`mutants.json`](mutants.json)); the ties-pass row is in manage-agents FOLLOW-UPS.md, "## ar-10a". | `lean/VE/Compose/Dispatch.lean`, `lean/VE/Compose/ProfilesMain.lean` | `mutants.json` | SIGNED by standing ruling R16 (DRI-RULINGS.md) |
