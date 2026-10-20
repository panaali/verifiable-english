# et-3c: user-visible delta

Feature item et-3c (the third part of ET-3 of `docs/spec/events-time-causation-PLAN.md`, acting DRI dri-featurefeed,
2026-10-18).

**What users see does not change.** The modules `lean/VE/Events/*` are still not reachable from any service mode,
route, decoder or relay. No `runMode` case, wire field, diagnostic, verdict, limit or fault order changes, and no
Python or Rust file changes. No existing Lean source changes except `lean/VE/Events/Examples.lean` (fixture T7 and
its import) and the generated inventories. The one delta is the trust budget.

| # | Delta | Ruling | Evidence |
| --- | --- | --- | --- |
| 1 | Trust budget: **S +10** (K +0, untied V +0), measured with `uv run python tools/trust_map.py --check` on the final tree against its merge base with main, e14d56df9: all in `VE/Events/Conservative.lean`, the one new S definition `oldEnv` (lines 15 to 23 with its docstring, counted as 10 by the tool). `expDays`, `firstDay` and `expansion` are P (proof helpers of `events_conservative`), T7's definitions are T. The check passes with the recorded allowance. | SIGNED by standing ruling R16 (DRI-RULINGS.md): new Lean-owned behaviour, 10 lines, none in K; the one new trusted definition `oldEnv` is broken by four seeded mutants, one per part it filters (links, day predicates, day constants, the day sort), each failing `events_conservative` and a T7 `#guard` (`docs/events-time-causation/et-3c/mutants.json`); the ties pass is asked for in `manage-agents/FOLLOW-UPS.md` ("## et-3c"). The allowance is recorded with `tools/trust_map.py --allow` (S 10 in `docs/trust-baseline.json`, signed "SIGNED by standing ruling R16 (DRI-RULINGS.md), et-3c, 2026-10-18") | `uv run python tools/trust_map.py --check` exit 0; `tests/test_trust_budget.py`, `tests/test_trust_ratchet.py` in the selected run (REPORT.md, Tests) |
