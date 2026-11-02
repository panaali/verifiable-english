# cmp-s2b: user-visible deltas

No answer changes. The rights chain still takes the enumerated route: `routeOf` tests `D.chain != .rights` before
`superposable D`, and `notSuperposable` answers `none` on the rights chain before it reads `sup D`
(lean/VE/Readings/Route.lean), so the new rights cases of `sup D` and the new owners are not on any route.
Off the rights chain no document has a rights content (`chainWF`'s `noRights`) or a `lim`, `cond` or `aimed` key
(`genKeys_decision`). The statement change of `superpose_faithful` (the hypothesis `ht`) changes no answer; the DRI
signed it without a DELTA row (reviews/dri-decisions-20261031-cmp-s2b.md item 1).

| Delta | Detail | Evidence | Ruling |
|---|---|---|---|
| Trust budget | V +46 net over 327bf922a: lean/VE/Readings/Choice.lean +52 (rights cases of `gateContent` and `copyContent`; `rightCopies`, `copyLine`, `copyScope`, `gateLine`, `jointOwner`, `limOwners`, `aimedOwners`, `qLim`; `gateNorm` moved in), lean/VE/Readings/ChoiceFacts.lean -6 (`gateNorm` moved out); K +0, S +0 | `uv run python tools/trust_map.py --check`: PASS with the allowance in docs/trust-baseline.json; every new trusted definition mutated in trust-mutants.json and mutants.json; FOLLOW-UPS.md row "## cmp-s2b" (ties pass) | R16 |
