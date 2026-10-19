# et-3b: user-visible delta

Feature item et-3b (the second half of ET-3 of `docs/spec/events-time-causation-PLAN.md`, acting DRI dri-featurefeed,
2026-10-18).

**What users see does not change.** The modules `lean/VE/Events/*` are still not reachable from any service mode,
route, decoder or relay. No `runMode` case, wire field, diagnostic, verdict, limit or fault order changes, and no
Python or Rust file changes. Every existing environment and its `environment_id` is unchanged: the only existing
sources touched are the import list `lean/VE.lean`, the events files of et-3 and the generated inventories. The one
delta is the trust budget.

| # | Delta | Ruling | Evidence |
| --- | --- | --- | --- |
| 1 | Trust budget: **S +27** (K +0, V +0), measured with `uv run python tools/trust_map.py --check` on the final tree against its merge base with main, e010fb6aa: `VE/Events/Completion.lean` +23 (numOf 3, oldTuple 4, addedDay 2, isDayC 3, completion 9; the other 2 lines are the file's added `open` line and comment), `VE/Events/Premises.lean` +4 (CalendarReading 4). The check passes with the recorded allowance. | SIGNED by standing ruling R16 (DRI-RULINGS.md): new Lean-owned behaviour, at most 150 lines, none in K; every new trusted definition is broken by at least one seeded mutant that fails a named theorem, and for every definition but `completion` also a fixture (`docs/events-time-causation/et-3b/mutants.json`: numOf, oldTuple, addedDay, isDayC, completion twice, CalendarReading); the ties pass is asked for in `manage-agents/FOLLOW-UPS.md` ("## et-3b"). The allowance is recorded with `tools/trust_map.py --allow` (S 27 in `docs/trust-baseline.json`, signed "SIGNED by standing ruling R16 (DRI-RULINGS.md), et-3b, 2026-10-18") | `uv run python tools/trust_map.py --check` exit 0; `tests/test_trust_budget.py`, `tests/test_trust_ratchet.py` in the selected run (REPORT.md, Tests) |
