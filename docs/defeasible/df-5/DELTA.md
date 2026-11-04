# df-5: user-visible delta

Feature item df-5 (the second part of batch DF-5 of `docs/spec/defeasible-PLAN.md`, after df-5a; spec
`docs/spec/defeasible.md` 3.8, 4, 5, 8.6 and 8.8; acting DRI dri-featurefeed, 2026-10-18). Bytes 0.

**What changes for users:** one new kind, `defaults-zone`, in the `norm-defaults` service mode, with its answers.
Every other answer is byte-identical: the 62 `norm-defaults` route cases of the merge base give the same rows from
main's service and from this branch's (`evidence/conservativity.json`, spec 8.8). The refactor of
`lean/VE/Defaults/Zone.lean` (`zoneOfMin`, `forcedOfMin`) changes no value and no statement (DRI 2026-11-04 item 2;
`lean/statements.txt`: 0 removed, 0 changed), so it is no row.

| # | Delta | Ruling | Evidence |
| --- | --- | --- | --- |
| D1 | A `defaults-zone` case, refused on main with `UnsupportedProfile: case kind defaults-zone is not available on the norm-defaults route`, is answered: the zone (`byDefault` with its value, `leftTo`, `notSaid`, `noCompletion` with labels, `unknown` with a reason) and, with `byDefault` or `leftTo`, DE10's form, `forced_all` and the completions shown as DE11, DE10f and DE13 rows; `ve.defaults` renders DE10, DE10′, DE10″, DE11, DE10f and DE13. A `weighing@0` document stays refused (`UnsupportedProfile`; spec 5 row 1 until DF-6) | SIGNED by the DRI 2026-11-04 (reviews/dri-decisions-20261104-df-5.md item 1) | `evidence/delta.json`: the 12 recorded zone cases through main's and this branch's `ve_service`, all refused on main with that text, 0 identical; `evidence/conservativity.json`: 62 of 62 identical; tests: `tests/test_defaults_zone.py` (8.6's fixtures, the English, the refusal), `lean/VE/Defaults/ZoneWireExamples.lean` (every 8.6 fixture through `runCaseReported`; spec 5 row 1's text) |
| T1 | Trust budget: **V +113** (K +0, S +0), measured with `uv run python tools/trust_map.py --check` on the final tree against its merge base c3d9ea9380cb: `VE/Defaults/ZoneWire.lean` +75 (D[V] `zoneFieldsOf`, `zoneFields`, `ZoneLine.json`, `exceptedRule`; G[V] `ZoneLine`, `zoneLines`, `zoneCase`), `ResponseShape/Schemas/NormDefaults.lean` +36 (G[V] `defaults_zone`, `defaults_zone_line`), `VE/Defaults/Route.lean` +2 (`defaultsKinds`, `defaultsRows`). C (not counted): the request decoders and the replay (`decisionOf`, `outcomeOf`, `tupleIn`, `ZoneReplay`, `replayZoneOn`, `maxZoneObservations`), `zoneOfMin` and `forcedOfMin` (df-5a's C bodies, moved) | SIGNED by standing ruling R16 (DRI-RULINGS.md), df-5, 2026-10-18 | `docs/trust-baseline.json` (allowance V 113); `trust-mutants-final.json` (389 killed, 0 survivor, 0 unknown; `trust-mutants-allow.json`); FOLLOW-UPS.md "## df-5" (the ties pass) |
