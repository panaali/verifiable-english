# et-4: user-visible delta

Feature item et-4 (batch ET-4 of `docs/spec/events-time-causation-PLAN.md`, acting DRI dri-featurefeed, 2026-10-18).

**What users see does not change.** `lean/VE/Events/Wire.lean` and `Chain.lean` are not reachable from any service
mode, route, decoder or relay: no `runMode` case, wire field, diagnostic, verdict, limit or fault order changes, and
no Python or Rust product file changes (the review fix adds one test, `tests/test_events_wire_mutants.py`). PK-1's
`reservedPrefixes` gains the row `("events", "date__")`. Its only readers are `Packs.reserved`, which no route calls, `ownPrefix` in `assemble`, which no route gives an `events` pack, and the new
decoder. The one row is the trust budget.

| # | Delta | Ruling | Evidence |
| --- | --- | --- | --- |
| 1 | Trust budget: **V +120** (K +0, S +0, unclassified +0). Measured with `uv run python tools/trust_map.py --check` on the final tree against the merge base 6d0a10526: `VE/Events/Wire.lean` +120 untied D[V] (`EventsDecoded`, `VocabView`, `vocabView`, `VocabView.args`/`.wording`/`.decided`/`.names`/`.env`, `strAt`, `arrAt`, `decodeEventSort`, `decodeStateSort`, `decodeLinkRaw`, `checkLinks`, `ownedByEvents`, `checkDates`, `decodeEvents`, `eventsPack`). The reject-only checks (`invalid`, `objectAt`, `firstFault`, `repeatOf`, `roleSig`, `checkDay`, `checkRoles`, `checkPremiseSize`) are D[R]. The fixtures in `WireExamples.lean` are T, and `Chain.lean` holds one theorem (P). The check passes with the recorded allowance (`docs/trust-baseline.json`). | SIGNED by standing ruling R16 (DRI-RULINGS.md), et-4, 2026-10-18 | R16's conditions: 120 lines, at most 150; K +0. Every new trusted definition is exercised by a check that can fail. `trust-mutants.json` (a full Mac run on the final Lean tree, 97792c45, exit 0): 199 KILLED, 0 SURVIVOR, 0 UNKNOWN, 36 INVALID, 33 ALLOWED. Its 22 allow entries are 5 equivalent survivors and 17 mutant texts Lean refuses (REPORT.md). The reject-only D[R] checks, which R16 does not count, have their own run (`reject-mutants.json`, exit 0) and `tests/test_events_wire_mutants.py` (review F1). `strAt`, `arrAt` and `eventsPack`, which got no tool mutant, have hand mutants in `mutants.json`, each failing a `#guard`. The ties row is in `manage-agents/FOLLOW-UPS.md` under `## et-4`. |
