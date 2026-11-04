# df-5: user-visible delta

Feature item df-5 (the second part of batch DF-5 of `docs/spec/defeasible-PLAN.md`, after df-5a; spec
`docs/spec/defeasible.md` 3.8, 4, 5, 8.6 and 8.8; acting DRI dri-featurefeed, 2026-10-18). Bytes 0.

**What changes for users:** one new kind, `defaults-zone`, in the `norm-defaults` service mode, with its answers.
Every other answer is byte-identical: the 62 `norm-defaults` route cases of the merge base give the same rows from
main's service and from this branch's (`evidence/conservativity.json`, spec 8.8). The refactor of
`lean/VE/Defaults/Zone.lean` (`zoneOfMin`, `forcedOfMin`) changes no value and no statement (DRI 2026-11-04 item 2;
`lean/statements.txt`: 0 removed, 0 changed), so it is no row. DE11's sentence after DE6′ (`defaults_english.fails`) now
reads Lean's words (`ve/defaults_words.json`, review F3); its bytes are unchanged, so it is no row.

**Fault order (R2), within the new kind** (main refuses every `defaults-zone` case): the situation, its decision
tables, the query, then the record's and the observations' sizes (past a bound the answer is `unknown`, and no entry
is read), then each record entry, then each observation, in request order.

| # | Delta | Ruling | Evidence |
| --- | --- | --- | --- |
| D1 | A `defaults-zone` case, refused on main with `UnsupportedProfile: case kind defaults-zone is not available on the norm-defaults route`, is answered: the zone (`byDefault` with its value, `leftTo`, `notSaid`, `noCompletion` with labels, `unknown` with a reason) and, with `byDefault` or `leftTo`, DE10's form, `forced_all` and the completions shown as DE11, DE10f and DE13 rows; `ve.defaults` renders DE10, DE10′, DE10″, DE11, DE10f and DE13. A `weighing@0` document stays refused (`UnsupportedProfile`; spec 5 row 1 until DF-6) | SIGNED by the DRI 2026-11-04 (reviews/dri-decisions-20261104-df-5.md item 1) | `evidence/delta.json`: the 12 recorded zone cases through main's and this branch's `ve_service`, all refused on main with that text, 0 identical; `evidence/conservativity.json`: 62 of 62 identical; tests: `tests/test_defaults_zone.py` (8.6's fixtures, the English, the refusal), `lean/VE/Defaults/ZoneWireExamples.lean` (every 8.6 fixture through `runCaseReported`; spec 5 row 1's text) |
| T1 | Trust budget: **V +139** (K +0, S +0), measured with `uv run python tools/trust_map.py --check` on the final tree against its merge base c3d9ea9380cb (remeasured at review F1): `VE/Defaults/ZoneWire.lean` +92 (D[V] `zoneFieldsOf`, `zoneFields`, `ZoneLine.json`, `exceptedRule`; G[V] `ZoneLine`, `zoneLines`, `zoneCase`, `ZoneReplay`, `ZoneReplay.X`, `maxZoneObservations`, `zoneJoins`), `VE/Defaults/ZoneWordsMain.lean` +9 (G[V] `main`, the words table's generator), `ResponseShape/Schemas/NormDefaults.lean` +36 (G[V] `defaults_zone`, `defaults_zone_line`), `VE/Defaults/Route.lean` +2 (`defaultsKinds`, `defaultsRows`). Tied, not counted: the request decoders `decisionOf`, `outcomeOf`, `tupleIn`, `recordEntry`, `obsEntry`, `replayZoneOn` (`decisionOf_mem`, `outcomeOf_mem`, `tupleIn_typed`, `recordEntry_sound`, `obsEntry_sound`, `replayZoneOn_sound`: each decoded value is the request's), `ZoneReplay.min` (`ZoneReplay.min_ok`: `zoneMin`'s answer), `zoneSizes` (`zoneSizes_record`: `zoneCharge`'s answer), and `ZoneLine.row`, `ZoneLine.kind`, `zoneHeads`, `zoneLineWords` (`zoneWords_complete`: one words row for each row Lean selects; the words' text is checked against spec 4 by `tests/test_defaults_zone.py`, not by a theorem). C (not counted): `zoneOfMin` and `forcedOfMin` (df-5a's C bodies, moved) | SIGNED by standing ruling R16 (DRI-RULINGS.md), df-5, 2026-10-18 | `docs/trust-baseline.json` (allowance V 139); `trust-mutants-final.json` (see REPORT "Trust"); FOLLOW-UPS.md "## df-5" (the ties pass) |
