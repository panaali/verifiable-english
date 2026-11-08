# df-5ab: user-visible delta

Feature item df-5ab (the `forcedAll` group cut from df-5a, `manage-agents/reviews/dri-decisions-20261102-df-5a-size.md`
item 1; spec `docs/spec/defeasible.md` 7.5, 8.6 and 8.9).

**None. Bytes 0.** `lean/VE/Defaults/Zone.lean` gains `forcedAllOf` and three proved theorems, and
`lean/VE/Defaults/ZoneExamples.lean` gains `#guard`s. No service mode, executable, response shape, schema, relay, English,
Python or Rust product code reads them; df-5 is the first reader (DE10f). The trust budget does not grow: K +0, S +0,
V +0 (`uv run python tools/trust_map.py --check`: "against 4e961f0ad503: K +0, S +0, D +0, G +0, tied +0, unclassified
+0, trusted +0" and "PASS"), because `forcedAllOf` is C, checked by `forcedAll_sound`, as df-5a's `defaultZoneOf` is.
The table has no rows.

| # | Delta | Ruling | Evidence |
| --- | --- | --- | --- |
