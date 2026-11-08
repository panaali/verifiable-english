# pe-1 DELTA

No user-visible delta. Nothing calls the new code: no answer, verdict, code, text, path or byte changes. The
`purposes` block is not read by any mode until PE-2. The one row below is the trusted-base growth that R16 asks to
itemise per file.

Measured on the final HEAD with `uv run python tools/trust_map.py --check`: "against a6d0d389a07b: K +0, S +124,
D +121, G +26, tied +134, unclassified +0, trusted +147 … PASS".

| # | File | Trusted lines (class, declarations) | Exercised by | Ruling |
|---|---|---|---|---|
| 1 | `lean/VE/Purposes/WellFormed.lean`, `lean/VE/Purposes/Decl.lean`, `lean/VE/Route/Inert.lean`, `lean/VE/Purposes/Wire.lean` | WellFormed.lean +77: S (`Part`, `Units`, `Units.find?`, `Units.kind?`, `Ref.partId?`, `Link.partIds`, `Link.slots`, `sideOfKind`, `markerAgrees`, `sameUnit`, `sidesAdjacent`, `rivals`, `markersLinked`, `covered`, `markerHonest`, `WellFormed`). Decl.lean +42: S (`Relation`, `Polarity`, `Share`, `Ref`, `Link`, `Block`, `maxLinks`). Inert.lean +5: S (`Kind.inert`). Wire.lean +23: untied D[V] (`wordOf`, `shareOf`, `linksOf`). Tied, so not counted: `check` (C, `check_ok_iff`), `nonfactive`, `shareOk`, `sideAdjacent`, `unstated` (G[V], their `_iff`/`_eq` theorems), `Relation.wire`, `Relation.ofWire?` and the Wire decoders and encoders (D[V], their `_ok`/`_render` theorems); `linkFields`, `linkFieldsOk`, `sideText` are D[R]; the fixtures are T. Total +147 ≤ 150, K +0. | `trust-mutants.json` (`tools/trust_mutants.py --max-mutants 1000 --test lean/VE/Purposes/Examples.lean --allow trust-mutants-allow.json`, exit 0: KILLED 154, INVALID 32, ALLOWED 104, SURVIVOR 0, UNKNOWN 0); the five trusted definitions with no killed trust mutant (`Link.slots`, `Units.kind?`, `Ref.partId?`, `shareOf`, `wordOf`) have a hand-planted mutant each in `mutants.json`, with the #guard that fails | R16 |
