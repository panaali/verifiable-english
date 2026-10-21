# et-3cb: user-visible delta

Feature item et-3cb (the last two theorems of ET-3 of `docs/spec/events-time-causation-PLAN.md` apart from et-3d,
acting DRI dri-featurefeed, 2026-10-18).

**None.** The modules `lean/VE/Events/*` are still not reachable from any service mode, route, decoder or relay. No
`runMode` case, wire field, diagnostic, verdict, limit or fault order changes, and no Python or Rust file changes. No
approved statement and no `EventsTyped` changes (`evidence/statements.json`: 72 exact, 0 differ). The trust budget
does not grow: `uv run python tools/trust_map.py --check` against the merge base 7c85297ea gives K +0, S +0, untied V
+0 and unclassified +0. The three new definitions (`dayNames`, `firstName`, `datesSituation`) are classed P (proof
helpers of `eventsPremises_satisfiable`), so no R16 allowance is recorded. There are no rows.
