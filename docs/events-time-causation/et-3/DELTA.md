# et-3: user-visible delta

Feature item et-3 (ET-3 of `docs/spec/events-time-causation-PLAN.md`, acting DRI dri-featurefeed, 2026-10-18).

**What users see does not change.** The new modules `lean/VE/Events/*` are not reachable from any service mode,
route, decoder or relay: no `runMode` case, wire field, diagnostic, verdict, limit or fault order changes, and no
Python or Rust file changes. Every existing environment and its `environment_id` is unchanged (no existing Lean
source changed except the import list `lean/VE.lean` and the generated audit files). The one delta is the trust
budget.

| # | Delta | Ruling | Evidence |
| --- | --- | --- | --- |
| 1 | Trust budget: **S +139** (K +0, V +0), measured with `python3 tools/trust_map.py --check` on the final tree against its merge base with main, 802b8ff9b: `VE/Events/Decl.lean` +64 (EventSort 4, StateSort 5, LinkForm 5, Link 7, EventsEnv 9, dateName 2, dateConst 2, startRole 6, boundRole 6, sig2 2, consecutive 2, regenEnv 4, EventsTyped 10), `VE/Events/Premises.lean` +63 (bin 2, irreflexiveF 1, transitiveF 3, linearF 2, dateFactF 1, adjacentF 2, oneRoleF 4, notBeforeBeginF 4, linkForwardF 8, linkWeakerF 3, weakerPairs 5, calendarLabelled 6, conventionLabelled 8, eventsLabelled 1, orderPremises 1, calendarPremises 1, conventionPremises 1, eventsX 2, Embeds 8), `VE/Events/Completion.lean` +12 (DayExtension 12). The check passes with the recorded allowance. | SIGNED by standing ruling R16 (DRI-RULINGS.md): new Lean-owned behaviour, at most 150 lines, none in K; each definition is exercised by a `#guard` of `lean/VE/Events/Examples.lean` or a theorem that can fail (seeded bugs S1 to S4 in REPORT.md; `Embeds` by `calendar_sat`, `DayExtension` by `dayExtension_transfer`, `EventsTyped` and `regenEnv` by their guards); the ties pass is asked for in `manage-agents/FOLLOW-UPS.md` ("## et-3"). The allowance is recorded with `tools/trust_map.py --allow` (S 139 in `docs/trust-baseline.json`, signed "SIGNED by standing ruling R16 (DRI-RULINGS.md), et-3, 2026-10-18") | `python3 tools/trust_map.py --check` exit 0; `tests/test_trust_budget.py`, `tests/test_trust_ratchet.py` pass (selected run, HEAD 47761ffa) |
