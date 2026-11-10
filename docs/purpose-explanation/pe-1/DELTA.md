# pe-1 DELTA

No user-visible delta. Nothing calls the new code: no answer, verdict, code, text, path or byte changes. The
`purposes` block is not read by any mode until PE-2. The rows below itemise the trusted-base growth under R16.

Measured for the F1 fix with `python tools/trust_map.py --check`: "against a6d0d389a07b: K +0, S +133,
D +121, G +26, tied +141, unclassified +0, trusted +149 … PASS".

| # | File | Trusted lines (class, declarations) | Exercised by | Ruling |
|---|---|---|---|---|
| 1 | `lean/VE/Purposes/WellFormed.lean`, `lean/VE/Purposes/Decl.lean`, `lean/VE/Route/Inert.lean`, `lean/VE/Purposes/Wire.lean` | WellFormed.lean +77: S (`Part`, `Units`, `Units.find?`, `Units.kind?`, `Ref.partId?`, `Link.partIds`, `Link.slots`, `sideOfKind`, `markerAgrees`, `sameUnit`, `sidesAdjacent`, `rivals`, `markersLinked`, `covered`, `markerHonest`, `WellFormed`). Decl.lean +42: S (`Relation`, `Polarity`, `Share`, `Ref`, `Link`, `Block`, `maxLinks`). Inert.lean +5: S (`Kind.inert`). Wire.lean +23: untied D[V] (`wordOf`, `shareOf`, `linksOf`). Tied, so not counted: `check` (C, `check_ok_iff`), `nonfactive`, `shareOk`, `sideAdjacent`, `unstated` (G[V], their `_iff`/`_eq` theorems), `Relation.wire`, `Relation.ofWire?` and the Wire decoders and encoders (D[V], their `_ok`/`_render` theorems); `linkFields`, `linkFieldsOk`, `sideText` are D[R]; the fixtures are T. Total +147 ≤ 150, K +0. | Current `trust-mutants.json` (`tools/trust_mutants.py --max-mutants 1000 --test lean/VE/Purposes/Examples.lean --allow trust-mutants-allow.json`, exit 0: KILLED 154, INVALID 32, ALLOWED 109, SURVIVOR 0, UNKNOWN 0); the five trusted definitions with no killed trust mutant (`Link.slots`, `Units.kind?`, `Ref.partId?`, `shareOf`, `wordOf`) have a hand-planted mutant each in `mutants.json`, with the #guard that fails | R16 |
| 2 | `lean/VE/Purposes/Decl.lean`, `lean/VE/Purposes/Wire.lean` | F1 restores `NotChecked`: Decl.lean +9 S. `shareOf_render` ties Wire.lean's `shareOf` to its canonical Share wire form, reducing untied D[V] by 7. Cumulative K +0, S +133, untied V +16, trusted +149 ≤ 150. | `VE.Purposes.Examples.notChecked_cases`, its adjacent distinctness `#guard`, and five constructor-removal mutants; the final `trust-mutants.json` records all five as raw UNKNOWN, allowed for their failed elaboration (exit 0); `VE.Purposes.shareOf_render` checks every Share constructor | R16 |
