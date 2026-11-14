# KB-4's measure: the 25 largest modules of the kernel tier

Measured on main `9a3fd7a9f9` (branch `infra/kb-8b`) with `tools/kernel_closure.py --why` (added by kb-8b), for the
architect seat to design KB-4 from. No interpretation is given: the table says what the kernel counts and through
which references. Kernel tier: the paths `route`, `norms`, `softNorms`, `metered` (`tools/kernel-paths.json`;
`quantity` stays a candidate, docs/kernel/kb-8b/CALLS.md).

## How it was measured

- The modules: every module in the `spec_modules` or `wrap_modules` of a kernel path in
  [closure-baseline.json](../closure-baseline.json), 119 modules.
- `kernel_closure.why(registry, <those modules>)` (the function behind `--why`; one run of the Lean half) gives, per
  module and per kernel path part (spec or wrap), the counted definitions with their source ranges and one
  shortest chain. Every per-path, per-part module figure it gives equals the baseline's (the script asserts it).
- A module's **lines** are its distinct counted lines over every kernel part; **spec lines** and **wrap lines** the
  distinct lines over the kernel paths' specs and over their wraps (a line can be in both, so they need not add
  up). The 119 modules' lines add up to 9,552, the baseline's `kernel_lines` (9,552).
- A definition's lines are its source range (`rangeOf`, as the measure counts it). Its **chain** is the one
  shortest chain of references `--why` gives, over every kernel part that counts it (ties: registry order, spec
  first), root first: a listed theorem (whose statement is read) for a spec, the path's entry for a wrap. A chain
  that ends in `<definition>.match_1` (or another auxiliary) reaches the definition through a constant Lean made
  inside its range, such as a matcher that another definition reuses; `rangeOf` charges the whole range of the
  definition for it (the attribution kb-8 described for `decodeUnit.match_1`).
- `kernel_closure.why(registry, <the 125 definitions>)` then gives the chains. The script is at the end.

## Groups

The groups are the task's: acts decoding (`VE.Acts.*`, `VE.Grammar.Table`); profile gate and dispatch
(`VE.Compose.Dispatch`, `VE.Service.Standalone`, `VE.Order.ProfileGate`); wire codecs (`VE.Route.Wire`,
`VE.Route.Decode`, `VE.Route.PyDecoder`, `VE.Norms.Wire`, `VE.Bridge`, `VE.Core.Bridge`, `VE.CertificateWire`,
`VE.Order.Wire`); soft norms (`VE.SoftNorms.*`). Logic and semantics: every other module under
`VE.Order`, `VE.Core`, `VE.Closure`, `VE.Route`, `VE.Norms`, `VE.Definitions`, `VE.Semantics`, `VE.Syntax`, `VE.Tableau`, `VE.TableauChecker`, `VE.TableauClosure`, `VE.Finite`, `VE.Paths`. Other: the rest, which in the kernel tier are `VE.Cardinality.Wire` 9, `VE.ClaimGraph` 103, `VE.Data.Background` 28, `VE.Grammar.Basic` 19, `VE.Grammar.Derives` 47, `VE.Grammar.Reading` 3, `VE.Limits` 20, `VE.NormDefaults.Tree` 65, `VE.NormDefaults.Wire` 54, `VE.Readings.Wire` 5, `VE.Risk.Wire` 32, `VE.Surface` 18, `VE.Time.Budget` 21, `VE.Time.Wire` 3.

Modules named `*Wire` that are not in the task's wire-codec list fall by that rule: `VE.Acts.Wire` (acts decoding, 37), `VE.Cardinality.Wire` (other, 9), `VE.Core.Wire` (logic and semantics, 108), `VE.NormDefaults.Wire` (other, 54), `VE.Readings.Wire` (other, 5), `VE.Risk.Wire` (other, 32), `VE.Route.MeteredWire` (logic and semantics, 46), `VE.SoftNorms.Wire` (soft norms, 80), `VE.Time.Wire` (other, 3).
Not counted by any kernel path: `VE.Order.ProfileGate`.
Wire codecs of the list counted by the kernel but not among the 25: `VE.Route.PyDecoder` 97, `VE.Core.Bridge` 107.

| Group | Modules listed below | Their lines | All kernel modules of the group | Their lines |
|---|---:|---:|---:|---:|
| acts decoding | 5 | 747 | 15 | 1,185 |
| profile gate and dispatch | 2 | 455 | 2 | 455 |
| wire codecs | 6 | 1,372 | 8 | 1,576 |
| logic and semantics | 9 | 2,042 | 68 | 4,507 |
| soft norms | 3 | 997 | 12 | 1,402 |
| other | 0 | 0 | 14 | 427 |
| **total** | **25** | **5,613** | **119** | **9,552** |


## Acts decoding

Listed: 5 of the 25, 747 lines; the group in the whole kernel tier: 15 modules, 1,185 lines.

| Module | Lines | Spec lines | Wrap lines | Paths that count it |
|---|---:|---:|---:|---|
| `VE.Grammar.Table` | 197 | 197 | 197 | norms (spec, wrap), softNorms (spec) |
| `VE.Acts.Grammar` | 159 | 159 | 159 | norms (spec, wrap), softNorms (spec) |
| `VE.Acts.Elaborate` | 137 | 137 | 137 | norms (spec, wrap) |
| `VE.Acts.Meaning` | 130 | 130 | 130 | norms (spec, wrap), softNorms (spec) |
| `VE.Acts.Lexical` | 124 | 124 | 124 | norms (spec, wrap), softNorms (spec), metered (spec, wrap) |

| Module | Definition | Lines | Chain (path, part: root first) |
|---|---|---:|---|
| `VE.Grammar.Table` | `VE.Grammar.ntRowGo` | 17 | norms spec: `VE.Norms.FlaggedSpec.norms_wire_conflict_free` → `VE.Norms.Wire.decodeSource` → `VE.Norms.Wire.decodeNormsEnvironment` → `VE.Norms.Wire.joinedActs` → `VE.Norms.Wire.actsOf` → `VE.Acts.Wire.checkActBy` → `VE.Acts.Wire.joinedActBy` → `VE.Acts.readingsBy` → `VE.Grammar.Prepared.parse` → `VE.Grammar.Prepared.table` → `VE.Grammar.fill` → `VE.Grammar.rowAt` → `VE.Grammar.ntRowGo` |
| `VE.Grammar.Table` | `VE.Grammar.Grammar.prepare` | 15 | norms spec: `VE.Norms.FlaggedSpec.norms_wire_conflict_free` → `VE.Norms.Wire.decodeSource` → `VE.Norms.Wire.decodeNormsEnvironment` → `VE.Norms.Wire.joinedActs` → `VE.Norms.Wire.actsOf` → `VE.Acts.lazyReader` → `VE.Acts.reader` → `VE.Grammar.Grammar.prepare` |
| `VE.Grammar.Table` | `VE.Grammar.Prepared` | 12 | norms spec: `VE.Norms.FlaggedSpec.norms_wire_conflict_free` → `VE.Norms.Wire.decodeSource` → `VE.Norms.Wire.decodeNormsEnvironment` → `VE.Norms.Wire.joinedActs` → `VE.Norms.Wire.actsOf` → `VE.Grammar.Prepared` |
| `VE.Grammar.Table` | `VE.Grammar.sufPosGo` | 12 | norms spec: `VE.Norms.FlaggedSpec.norms_wire_conflict_free` → `VE.Norms.Wire.decodeSource` → `VE.Norms.Wire.decodeNormsEnvironment` → `VE.Norms.Wire.joinedActs` → `VE.Norms.Wire.actsOf` → `VE.Acts.Wire.checkActBy` → `VE.Acts.Wire.joinedActBy` → `VE.Acts.readingsBy` → `VE.Grammar.Prepared.parse` → `VE.Grammar.Prepared.table` → `VE.Grammar.fill` → `VE.Grammar.rowAt` → `VE.Grammar.sufGroups` → `VE.Grammar.sufPosGo` |
| `VE.Grammar.Table` | `VE.Grammar.rowAt` | 11 | norms spec: `VE.Norms.FlaggedSpec.norms_wire_conflict_free` → `VE.Norms.Wire.decodeSource` → `VE.Norms.Wire.decodeNormsEnvironment` → `VE.Norms.Wire.joinedActs` → `VE.Norms.Wire.actsOf` → `VE.Acts.Wire.checkActBy` → `VE.Acts.Wire.joinedActBy` → `VE.Acts.readingsBy` → `VE.Grammar.Prepared.parse` → `VE.Grammar.Prepared.table` → `VE.Grammar.fill` → `VE.Grammar.rowAt` |
| `VE.Acts.Grammar` | `VE.Acts.frameRules` | 45 | norms spec: `VE.Norms.FlaggedSpec.norms_wire_conflict_free` → `VE.Norms.Wire.decodeSource` → `VE.Norms.Wire.decodeNormsEnvironment` → `VE.Norms.Wire.joinedActs` → `VE.Norms.Wire.actsOf` → `VE.Acts.lazyReader` → `VE.Acts.reader` → `VE.Acts.schema` → `VE.Acts.frameRules` |
| `VE.Acts.Grammar` | `VE.Acts.globalRules` | 22 | norms spec: `VE.Norms.FlaggedSpec.norms_wire_conflict_free` → `VE.Norms.Wire.decodeSource` → `VE.Norms.Wire.decodeNormsEnvironment` → `VE.Norms.Wire.joinedActs` → `VE.Norms.Wire.actsOf` → `VE.Acts.lazyReader` → `VE.Acts.reader` → `VE.Acts.schema` → `VE.Acts.globalRules` |
| `VE.Acts.Grammar` | `VE.Acts.NT.rank` | 11 | norms spec: `VE.Norms.FlaggedSpec.norms_wire_conflict_free` → `VE.Norms.Wire.decodeSource` → `VE.Norms.Wire.decodeNormsEnvironment` → `VE.Norms.Wire.joinedActs` → `VE.Norms.Wire.actsOf` → `VE.Acts.lazyReader` → `VE.Acts.reader` → `VE.Acts.build` → `VE.Acts.NT.rank` |
| `VE.Acts.Grammar` | `VE.Acts.NT` | 8 | norms spec: `VE.Norms.FlaggedSpec.norms_wire_conflict_free` → `VE.Norms.Wire.decodeSource` → `VE.Norms.Wire.decodeNormsEnvironment` → `VE.Norms.Wire.joinedActs` → `VE.Norms.Wire.actsOf` → `VE.Acts.RuleS` → `VE.Acts.RuleS.mk` → `VE.Acts.NT` |
| `VE.Acts.Grammar` | `VE.Acts.build` | 8 | norms spec: `VE.Norms.FlaggedSpec.norms_wire_conflict_free` → `VE.Norms.Wire.decodeSource` → `VE.Norms.Wire.decodeNormsEnvironment` → `VE.Norms.Wire.joinedActs` → `VE.Norms.Wire.actsOf` → `VE.Acts.lazyReader` → `VE.Acts.reader` → `VE.Acts.build` |
| `VE.Acts.Elaborate` | `VE.Acts.elaborateMap` | 18 | norms spec: `VE.Acts.Decode.norms_wire_acceptance_elaborated` → `VE.Acts.Decode.flaggedSource` → `VE.Acts.Decode.ElaboratedU` → `VE.Acts.Decode.ElaboratedU.mk` → `VE.Acts.elaborateMap` |
| `VE.Acts.Elaborate` | `VE.Acts.namesOk` | 15 | norms spec: `VE.Acts.Decode.norms_wire_acceptance_elaborated` → `VE.Acts.Decode.flaggedSource` → `VE.Acts.Decode.ElaboratedU` → `VE.Acts.Decode.ElaboratedU.mk` → `VE.Acts.elaborateMap` → `VE.Acts.namesOk` |
| `VE.Acts.Elaborate` | `VE.Acts.readingOf` | 12 | norms spec: `VE.Acts.Decode.norms_wire_acceptance_elaborated` → `VE.Acts.Decode.flaggedSource` → `VE.Acts.Decode.ElaboratedU` → `VE.Acts.Decode.ElaboratedU.mk` → `VE.Acts.elaborateMap` → `VE.Acts.readingOf` |
| `VE.Acts.Elaborate` | `VE.Acts.ruleReading` | 9 | norms spec: `VE.Acts.Decode.norms_wire_acceptance_elaborated` → `VE.Acts.Decode.flaggedSource` → `VE.Acts.Decode.ElaboratedU` → `VE.Acts.Decode.ElaboratedU.mk` → `VE.Acts.elaborateMap` → `VE.Acts.readingOf` → `VE.Acts.ruleReading` |
| `VE.Acts.Elaborate` | `VE.Acts.ActsDoc` | 8 | norms spec: `VE.Acts.Decode.norms_wire_acceptance_elaborated` → `VE.Acts.Decode.flaggedSource` → `VE.Acts.Decode.ElaboratedU` → `VE.Acts.Decode.ElaboratedU.mk` → `VE.Acts.ActsDoc` |
| `VE.Acts.Meaning` | `VE.Acts.applyRule` | 37 | norms spec: `VE.Norms.FlaggedSpec.norms_wire_conflict_free` → `VE.Norms.Wire.decodeSource` → `VE.Norms.Wire.decodeNormsEnvironment` → `VE.Norms.Wire.joinedActs` → `VE.Norms.Wire.actsOf` → `VE.Acts.Wire.checkActBy` → `VE.Acts.Wire.joinedActBy` → `VE.Acts.readingsBy` → `VE.Acts.meaningWith` → `VE.Acts.piecesOf` → `VE.Acts.applyRule` |
| `VE.Acts.Meaning` | `VE.Acts.piecesOf` | 13 | norms spec: `VE.Norms.FlaggedSpec.norms_wire_conflict_free` → `VE.Norms.Wire.decodeSource` → `VE.Norms.Wire.decodeNormsEnvironment` → `VE.Norms.Wire.joinedActs` → `VE.Norms.Wire.actsOf` → `VE.Acts.Wire.checkActBy` → `VE.Acts.Wire.joinedActBy` → `VE.Acts.readingsBy` → `VE.Acts.meaningWith` → `VE.Acts.piecesOf` |
| `VE.Acts.Meaning` | `VE.Acts.atomOk` | 9 | norms spec: `VE.Norms.FlaggedSpec.norms_wire_conflict_free` → `VE.Norms.Wire.decodeSource` → `VE.Norms.Wire.decodeNormsEnvironment` → `VE.Norms.Wire.joinedActs` → `VE.Norms.Wire.actsOf` → `VE.Acts.Wire.checkActBy` → `VE.Acts.Wire.joinedActBy` → `VE.Acts.readingsBy` → `VE.Acts.meaningWith` → `VE.Acts.actOk` → `VE.Acts.atomOk` |
| `VE.Acts.Meaning` | `VE.Acts.Piece` | 7 | norms spec: `VE.Norms.FlaggedSpec.norms_wire_conflict_free` → `VE.Norms.Wire.decodeSource` → `VE.Norms.Wire.decodeNormsEnvironment` → `VE.Norms.Wire.joinedActs` → `VE.Norms.Wire.actsOf` → `VE.Acts.Wire.checkActBy` → `VE.Acts.Wire.joinedActBy` → `VE.Acts.readingsBy` → `VE.Acts.meaningWith` → `VE.Acts.Piece` |
| `VE.Acts.Meaning` | `VE.Acts.coordAct` | 7 | norms spec: `VE.Norms.FlaggedSpec.norms_wire_conflict_free` → `VE.Norms.Wire.decodeSource` → `VE.Norms.Wire.decodeNormsEnvironment` → `VE.Norms.Wire.joinedActs` → `VE.Norms.Wire.actsOf` → `VE.Acts.Wire.checkActBy` → `VE.Acts.Wire.joinedActBy` → `VE.Acts.readingsBy` → `VE.Acts.meaningWith` → `VE.Acts.piecesOf` → `VE.Acts.applyRule` → `VE.Acts.coordAct.match_3` |
| `VE.Acts.Lexical` | `VE.Acts.Lexical.phraseToks` | 22 | norms spec: `VE.Norms.FlaggedSpec.norms_wire_conflict_free` → `VE.Norms.Wire.decodeSource` → `VE.Norms.Wire.decodeNormsEnvironment` → `VE.Norms.Wire.actsFixed` → `VE.Acts.Lexical.decodeFixed` → `VE.Acts.Lexical.phraseToks` |
| `VE.Acts.Lexical` | `VE.Acts.Lexical.checkWith` | 17 | norms spec: `VE.Acts.Decode.norms_wire_certificate_acceptance_elaborated` → `VE.Norms.Flagged.replayEntailmentIn` → `VE.Norms.Wire.canonicalEnvironmentJson` → `VE.Norms.Wire.canonicalShape` → `VE.Acts.Lexical.checkWith` |
| `VE.Acts.Lexical` | `VE.Acts.Lexical.decodeFixed` | 12 | norms spec: `VE.Norms.FlaggedSpec.norms_wire_conflict_free` → `VE.Norms.Wire.decodeSource` → `VE.Norms.Wire.decodeNormsEnvironment` → `VE.Norms.Wire.actsFixed` → `VE.Acts.Lexical.decodeFixed` |
| `VE.Acts.Lexical` | `VE.Acts.Lexical.pieceToks` | 9 | norms spec: `VE.Norms.FlaggedSpec.norms_wire_conflict_free` → `VE.Norms.Wire.decodeSource` → `VE.Norms.Wire.decodeNormsEnvironment` → `VE.Norms.Wire.actsFixed` → `VE.Acts.Lexical.decodeFixed` → `VE.Acts.Lexical.phraseToks` → `VE.Acts.Lexical.rawLex` → `VE.Acts.Lexical.pieceToks` |
| `VE.Acts.Lexical` | `VE.Acts.Lexical.group` | 8 | norms spec: `VE.Acts.Decode.norms_wire_certificate_acceptance_elaborated` → `VE.Norms.Flagged.replayEntailmentIn` → `VE.Norms.Wire.canonicalEnvironmentJson` → `VE.Norms.Wire.canonicalShape` → `VE.Acts.Lexical.checkWith` → `VE.Acts.Lexical.lex` → `VE.Acts.Lexical.group` |

## Profile gate and dispatch

Listed: 2 of the 25, 455 lines; the group in the whole kernel tier: 2 modules, 455 lines.

| Module | Lines | Spec lines | Wrap lines | Paths that count it |
|---|---:|---:|---:|---|
| `VE.Service.Standalone` | 261 | 261 | 261 | metered (spec, wrap) |
| `VE.Compose.Dispatch` | 194 | 194 | 194 | norms (wrap), metered (spec, wrap) |

| Module | Definition | Lines | Chain (path, part: root first) |
|---|---|---:|---|
| `VE.Service.Standalone` | `VE.Service.Standalone.typingReduced` | 37 | metered spec: `VE.Route.MeteredRun.metered_wire_sound` → `VE.Service.Standalone.evaluable` → `VE.Service.Standalone.validated` → `VE.Service.Standalone.typingReduced` |
| `VE.Service.Standalone` | `VE.Service.Standalone.validated` | 36 | metered spec: `VE.Route.MeteredRun.metered_wire_sound` → `VE.Service.Standalone.evaluable` → `VE.Service.Standalone.validated` |
| `VE.Service.Standalone` | `VE.Service.Standalone.riskReduced` | 30 | metered spec: `VE.Route.MeteredRun.metered_wire_sound` → `VE.Service.Standalone.evaluable` → `VE.Service.Standalone.validated` → `VE.Service.Standalone.typingReduced` → `VE.Service.Standalone.riskReduced` |
| `VE.Service.Standalone` | `VE.Service.Standalone.decodeLegacy` | 20 | metered spec: `VE.Route.MeteredRun.metered_wire_sound` → `VE.Service.Standalone.evaluable` → `VE.Service.Standalone.decodeLegacy` |
| `VE.Service.Standalone` | `VE.Service.Standalone.alternativesReduced` | 18 | metered spec: `VE.Route.MeteredRun.metered_wire_sound` → `VE.Service.Standalone.evaluable` → `VE.Service.Standalone.validated` → `VE.Service.Standalone.typingReduced` → `VE.Service.Standalone.alternativesReduced` |
| `VE.Compose.Dispatch` | `VE.Compose.todayGate` | 42 | metered spec: `VE.Route.MeteredRun.metered_wire_sound` → `VE.Service.Standalone.evaluable` → `VE.Compose.decidingEnvironment` → `VE.Compose.gateOf` → `VE.Compose.todayGate.match_1` |
| `VE.Compose.Dispatch` | `VE.Compose.baseRows` | 30 | metered spec: `VE.Route.MeteredRun.metered_wire_sound` → `VE.Service.Standalone.evaluable` → `VE.Compose.decidingEnvironment` → `VE.Compose.profileTable` → `VE.Compose.baseRows` |
| `VE.Compose.Dispatch` | `VE.Compose.decidingEnvironment` | 11 | metered spec: `VE.Route.MeteredRun.metered_wire_sound` → `VE.Service.Standalone.evaluable` → `VE.Compose.decidingEnvironment` |
| `VE.Compose.Dispatch` | `VE.Compose.gateOf` | 9 | metered spec: `VE.Route.MeteredRun.metered_wire_sound` → `VE.Service.Standalone.evaluable` → `VE.Compose.decidingEnvironment` → `VE.Compose.gateOf` |
| `VE.Compose.Dispatch` | `VE.Compose.wrapperRows` | 9 | metered spec: `VE.Route.MeteredRun.metered_wire_sound` → `VE.Service.Standalone.evaluable` → `VE.Compose.decidingEnvironment` → `VE.Compose.profileTable` → `VE.Compose.wrapperRows` |

## Wire codecs

Listed: 6 of the 25, 1,372 lines; the group in the whole kernel tier: 8 modules, 1,576 lines.

| Module | Lines | Spec lines | Wrap lines | Paths that count it |
|---|---:|---:|---:|---|
| `VE.Route.Wire` | 374 | 374 | 191 | route (spec), norms (spec, wrap), softNorms (spec), metered (spec, wrap) |
| `VE.Norms.Wire` | 310 | 310 | 278 | norms (spec, wrap), softNorms (spec), metered (spec, wrap) |
| `VE.Bridge` | 217 | 217 | 159 | route (spec), norms (spec, wrap), softNorms (spec), metered (spec, wrap) |
| `VE.CertificateWire` | 160 | 160 | 0 | route (spec), norms (spec), softNorms (spec) |
| `VE.Order.Wire` | 156 | 156 | 57 | route (spec), metered (spec, wrap) |
| `VE.Route.Decode` | 155 | 155 | 0 | route (spec), metered (spec) |

| Module | Definition | Lines | Chain (path, part: root first) |
|---|---|---:|---|
| `VE.Route.Wire` | `VE.Route.Wire.decodeVocabulary` | 78 | route spec: `VE.Route.RunSound.route_order_certificate` → `VE.Route.Wire.decodeOrderVocabulary` → `VE.Route.Wire.decodeVocabulary.match_1` |
| `VE.Route.Wire` | `VE.Route.Wire.decodeOrderVocabulary` | 31 | route spec: `VE.Route.RunSound.route_order_certificate` → `VE.Route.Wire.decodeOrderVocabulary` |
| `VE.Route.Wire` | `VE.Route.Wire.bodyFault` | 19 | route spec: `VE.Route.RunSound.runCase_dispatch` → `VE.Route.Run.dispatch` → `VE.Core.Layers.decodeLayered` → `VE.Core.Layers.naryEntries` → `VE.Route.Wire.bodyFault` |
| `VE.Route.Wire` | `VE.Route.Wire.decodeModel` | 14 | route spec: `VE.Route.RunSound.route_closure_countermodel` → `VE.Route.WireSound.routeModel` → `VE.Route.Wire.decodeDataModel` → `VE.Route.Wire.decodeModel` |
| `VE.Route.Wire` | `VE.Route.Wire.backgroundCheck` | 13 | route spec: `VE.Route.RunSound.route_closure_countermodel` → `VE.Route.WireSound.routeModel` → `VE.Route.Wire.decodeDataModel` → `VE.Route.Wire.decodeModel` → `VE.Route.Wire.backgroundCheck` |
| `VE.Norms.Wire` | `VE.Norms.Wire.budgetFormula` | 41 | norms spec: `VE.Norms.FlaggedSpec.norms_wire_conflict_free` → `VE.Norms.Wire.decodeSource` → `VE.Norms.Wire.decodeNorm` → `VE.Norms.Wire.budgetFormula` |
| `VE.Norms.Wire` | `VE.Norms.Wire.decodeRegulatedWith` | 37 | norms spec: `VE.Norms.FlaggedSpec.norms_wire_conflict_free` → `VE.Norms.Wire.decodeSource` → `VE.Norms.Wire.decodeNormsEnvironment` → `VE.Norms.Wire.decodeRegulatedShape` → `VE.Norms.Wire.decodeRegulatedWith` |
| `VE.Norms.Wire` | `VE.Norms.Wire.decodeNormsEnvironment` | 36 | norms spec: `VE.Norms.FlaggedSpec.norms_wire_conflict_free` → `VE.Norms.Wire.decodeSource` → `VE.Norms.Wire.decodeNormsEnvironment` |
| `VE.Norms.Wire` | `VE.Norms.Wire.decodeSource` | 29 | norms spec: `VE.Norms.FlaggedSpec.norms_wire_conflict_free` → `VE.Norms.Wire.decodeSource` |
| `VE.Norms.Wire` | `VE.Norms.Wire.canonicalEnvironmentJson` | 23 | norms spec: `VE.Acts.Decode.norms_wire_certificate_acceptance_elaborated` → `VE.Norms.Flagged.replayEntailmentIn` → `VE.Norms.Wire.canonicalEnvironmentJson` |
| `VE.Bridge` | `VE.Bridge.decodeEnvironment` | 42 | metered spec: `VE.Route.MeteredRun.metered_wire_sound` → `VE.Service.Standalone.evaluable` → `VE.Service.Standalone.decodeLegacy` → `VE.Bridge.decodeEnvironment` |
| `VE.Bridge` | `VE.Bridge.decodeModelData` | 31 | softNorms spec: `VE.SoftNorms.Run.soft_wire_selected` → `VE.SoftNorms.Wire.decodeModel` → `VE.Bridge.decodeModelData` |
| `VE.Bridge` | `VE.Bridge.decodeFormula` | 17 | route spec: `VE.Route.RunSound.route_fol_certificate` → `VE.Route.WireSound.folFamily` → `VE.Route.Wire.decodeFormulas` → `VE.Bridge.decodeFormula` |
| `VE.Bridge` | `VE.Bridge.checkVocabularyNames` | 14 | route spec: `VE.Route.RunSound.route_order_certificate` → `VE.Route.Wire.decodeOrderVocabulary` → `VE.Order.Wire.decodeEnvironment` → `VE.Bridge.checkVocabularyNames` |
| `VE.Bridge` | `VE.Bridge.exactFieldsQuoted` | 11 | metered spec: `VE.Route.MeteredRun.metered_wire_sound` → `VE.Service.Standalone.evaluable` → `VE.Service.Standalone.decodeLegacy` → `VE.Bridge.decodeEnvironment` → `VE.Bridge.exactFieldsQuoted` |
| `VE.CertificateWire` | `_private.VE.CertificateWire.0.VE.CertificateWire.shaBlock` | 31 | norms spec: `VE.Acts.Decode.norms_wire_acceptance_elaborated` → `VE.Norms.Run.AdmissionAnswerIn` → `VE.Norms.Run.BindingsMatchSourceAndRegeneration` → `VE.CertificateWire.digest` → `VE.CertificateWire.sha256` → `_private.VE.CertificateWire.0.VE.CertificateWire.shaBlock` |
| `VE.CertificateWire` | `VE.CertificateWire.decodeClosureTrace` | 26 | route spec: `VE.Route.RunSound.route_closure_certificate` → `VE.CertificateWire.decodeClosureCertificate` → `VE.CertificateWire.decodeClosureTrace` |
| `VE.CertificateWire` | `VE.CertificateWire.canonicalWith` | 16 | route spec: `VE.Route.RunSound.route_closure_certificate` → `VE.CertificateWire.decodeClosureCertificate` → `VE.CertificateWire.decodeClosureTrace` → `VE.CertificateWire.canonicalWith.match_5` |
| `VE.CertificateWire` | `VE.CertificateWire.decodeTrace` | 16 | route spec: `VE.Route.RunSound.route_fol_certificate` → `VE.CertificateWire.decodeCertificate` → `VE.CertificateWire.decodeTrace` |
| `VE.CertificateWire` | `VE.CertificateWire.sha256` | 11 | norms spec: `VE.Acts.Decode.norms_wire_acceptance_elaborated` → `VE.Norms.Run.AdmissionAnswerIn` → `VE.Norms.Run.BindingsMatchSourceAndRegeneration` → `VE.CertificateWire.digest` → `VE.CertificateWire.sha256` |
| `VE.Order.Wire` | `VE.Order.Wire.decodeEnvironment` | 50 | route spec: `VE.Route.RunSound.route_order_certificate` → `VE.Route.Wire.decodeOrderVocabulary` → `VE.Order.Wire.decodeEnvironment` |
| `VE.Order.Wire` | `VE.Order.Wire.decodeTrace` | 30 | route spec: `VE.Route.RunSound.route_order_certificate` → `VE.Order.Wire.decodeCertificate` → `VE.Order.Wire.decodeTrace` |
| `VE.Order.Wire` | `VE.Order.Wire.decodeFormula` | 21 | route spec: `VE.Route.RunSound.route_order_certificate` → `VE.Route.WireSound.orderFamily` → `VE.Order.Wire.decodeFormula` |
| `VE.Order.Wire` | `VE.Order.Wire.decodeTerm` | 10 | route spec: `VE.Route.RunSound.route_order_certificate` → `VE.Order.Wire.decodeCertificate` → `VE.Order.Wire.decodeTrace` → `VE.Order.Wire.decodeTerm.match_3` |
| `VE.Order.Wire` | `VE.Order.Wire.decodeInt` | 6 | route spec: `VE.Route.RunSound.route_order_certificate` → `VE.Order.Wire.decodeCertificate` → `VE.Order.Wire.decodeTrace` → `VE.Order.Wire.decodeCut` → `VE.Order.Wire.decodeInt` |
| `VE.Route.Decode` | `VE.Route.Decode.decodeModelData` | 34 | metered spec: `VE.Route.MeteredRun.runWith_sound` → `VE.Route.MeteredRun.CaseModel` → `VE.Core.Layers.completeModel` → `VE.Route.Decode.decodeModelData` |
| `VE.Route.Decode` | `VE.Route.Decode.decodeOrderModel` | 34 | route spec: `VE.Route.RunSound.route_order_countermodel` → `VE.Route.WireSound.orderModel` → `VE.Route.Wire.decodeOrderModel` → `VE.Route.Decode.decodeOrderModel` |
| `VE.Route.Decode` | `VE.Route.Decode.modelLimits` | 12 | route spec: `VE.Route.RunSound.route_order_countermodel` → `VE.Route.WireSound.orderModel` → `VE.Route.Wire.decodeOrderModel` → `VE.Route.Decode.decodeOrderModel` → `VE.Route.Decode.modelLimits` |
| `VE.Route.Decode` | `VE.Route.Decode.validOrderFast` | 11 | route spec: `VE.Route.RunSound.route_order_countermodel` → `VE.Route.WireSound.orderModel` → `VE.Route.Wire.decodeOrderModel` → `VE.Route.Decode.decodeOrderModel` → `VE.Route.Decode.validOrderFast.match_3` |
| `VE.Route.Decode` | `VE.Route.Decode.decodeValue` | 9 | route spec: `VE.Route.RunSound.route_order_countermodel` → `VE.Route.WireSound.orderModel` → `VE.Route.Wire.decodeOrderModel` → `VE.Route.Decode.decodeOrderModel` → `VE.Route.Decode.decodeValue` |

## Logic and semantics

Listed: 9 of the 25, 2,042 lines; the group in the whole kernel tier: 68 modules, 4,507 lines.

| Module | Lines | Spec lines | Wrap lines | Paths that count it |
|---|---:|---:|---:|---|
| `VE.Route.Admission` | 369 | 369 | 0 | route (spec), norms (spec), softNorms (spec) |
| `VE.Norms.Tree` | 273 | 273 | 269 | norms (spec, wrap), softNorms (spec), metered (spec, wrap) |
| `VE.Core.Layers` | 247 | 247 | 133 | route (spec), metered (spec, wrap) |
| `VE.Order.Tableau` | 244 | 244 | 0 | route (spec) |
| `VE.Route.WireSound` | 241 | 241 | 0 | route (spec) |
| `VE.Route.Budget` | 210 | 210 | 0 | route (spec), metered (spec) |
| `VE.Norms.Admission` | 196 | 196 | 0 | norms (spec), softNorms (spec) |
| `VE.Norms.Flagged` | 142 | 142 | 0 | norms (spec) |
| `VE.Definitions.Layer` | 120 | 120 | 42 | route (spec), norms (spec, wrap), softNorms (spec), metered (spec, wrap) |

| Module | Definition | Lines | Chain (path, part: root first) |
|---|---|---:|---|
| `VE.Route.Admission` | `VE.Route.Admission.parseLabelRaw` | 32 | route spec: `VE.Route.RunSound.runCase_dispatch` → `VE.Route.Run.dispatch` → `VE.Route.Admission.parseLabel` → `VE.Route.Admission.parseLabelRaw` |
| `VE.Route.Admission` | `VE.Route.Admission.decodeNode` | 24 | norms spec: `VE.Acts.Decode.norms_wire_acceptance_elaborated` → `VE.Norms.Run.AdmissionAnswerIn` → `VE.Norms.Admission.admitDocumentIn` → `VE.Route.Admission.decodeNode` |
| `VE.Route.Admission` | `VE.Route.Admission.decodeKind` | 23 | norms spec: `VE.Acts.Decode.norms_wire_acceptance_elaborated` → `VE.Norms.Run.AdmissionAnswerIn` → `VE.Norms.Admission.admitDocumentIn` → `VE.Norms.Admission.splitDocument` → `VE.Norms.Admission.splitUnit` → `VE.Route.Admission.decodeKind` |
| `VE.Route.Admission` | `VE.Route.Admission.Kind` | 17 | norms spec: `VE.Acts.Decode.norms_wire_acceptance_elaborated` → `VE.Norms.Run.AdmissionAnswerIn` → `VE.Norms.Admission.admitDocumentIn` → `VE.Route.Admission.renderKind` → `VE.Route.Admission.Kind` |
| `VE.Route.Admission` | `VE.Route.Admission.decodeDoc` | 17 | norms spec: `VE.Acts.Decode.norms_wire_acceptance_elaborated` → `VE.Norms.Run.AdmissionAnswerIn` → `VE.Norms.Admission.admitDocumentIn` → `VE.Route.Admission.decodeDoc` |
| `VE.Norms.Tree` | `VE.Norms.check` | 64 | norms spec: `VE.Norms.FlaggedSpec.norms_wire_conflict_free` → `VE.Norms.Wire.decodeSource` → `VE.Norms.validate` → `VE.Norms.check` |
| `VE.Norms.Tree` | `VE.Norms.actChecks` | 29 | norms spec: `VE.Norms.FlaggedSpec.norms_wire_conflict_free` → `VE.Norms.Wire.decodeSource` → `VE.Norms.Wire.decodeNormsEnvironment` → `VE.Norms.actChecks` |
| `VE.Norms.Tree` | `VE.Norms.typeDiagnostic` | 26 | norms spec: `VE.Norms.FlaggedSpec.norms_wire_conflict_free` → `VE.Norms.Wire.decodeSource` → `VE.Norms.validate` → `VE.Norms.check` → `VE.Norms.typeDiagnostic` |
| `VE.Norms.Tree` | `VE.Norms.semanticCheck` | 15 | norms spec: `VE.Norms.FlaggedSpec.norms_wire_conflict_free` → `VE.Norms.Wire.decodeSource` → `VE.Norms.validate` → `VE.Norms.semanticCheck` |
| `VE.Norms.Tree` | `VE.Norms.Regulated` | 10 | norms spec: `VE.Norms.FlaggedSpec.norms_wire_conflict_free` → `VE.Norms.ConflictFree` → `VE.Norms.Regulated` |
| `VE.Core.Layers` | `VE.Core.Layers.completeModel` | 36 | metered spec: `VE.Route.MeteredRun.runWith_sound` → `VE.Route.MeteredRun.CaseModel` → `VE.Core.Layers.completeModel` |
| `VE.Core.Layers` | `VE.Core.Layers.coreCertificate` | 25 | route spec: `VE.Route.RunSound.runCase_dispatch` → `VE.Route.Run.dispatch` → `VE.Core.Layers.run` → `VE.Core.Layers.coreCertificate` |
| `VE.Core.Layers` | `VE.Core.Layers.naryEntries` | 15 | route spec: `VE.Route.RunSound.runCase_dispatch` → `VE.Route.Run.dispatch` → `VE.Core.Layers.decodeLayered` → `VE.Core.Layers.naryEntries` |
| `VE.Core.Layers` | `VE.Core.Layers.run` | 12 | route spec: `VE.Route.RunSound.runCase_dispatch` → `VE.Route.Run.dispatch` → `VE.Core.Layers.run` |
| `VE.Core.Layers` | `VE.Core.Layers.elaborateNary` | 11 | route spec: `VE.Route.RunSound.runCase_dispatch` → `VE.Route.Run.dispatch` → `VE.Core.Layers.decodeLayered` → `VE.Core.Layers.elaborateNary` |
| `VE.Order.Tableau` | `VE.Order.Tableau.next` | 20 | route spec: `VE.Route.RunSound.route_order_certificate` → `VE.Route.WireSound.orderRunner` → `VE.Route.Checker.order` → `VE.Order.Tableau.checkCertificate` → `VE.Order.Tableau.replay` → `VE.Order.Tableau.next` |
| `VE.Order.Tableau` | `VE.Order.Tableau.constraint` | 18 | route spec: `VE.Route.RunSound.route_order_certificate` → `VE.Route.WireSound.orderRunner` → `VE.Route.Checker.order` → `VE.Order.Tableau.checkCertificate` → `VE.Order.Tableau.replay` → `VE.Order.Tableau.farkasCloses` → `VE.Order.Tableau.comboLin` → `VE.Order.Tableau.constraint.match_1` |
| `VE.Order.Tableau` | `VE.Order.Tableau.replay` | 17 | route spec: `VE.Route.RunSound.route_order_certificate` → `VE.Route.WireSound.orderRunner` → `VE.Route.Checker.order` → `VE.Order.Tableau.checkCertificate` → `VE.Order.Tableau.replay` |
| `VE.Order.Tableau` | `VE.Order.Tableau.Signed.rule` | 13 | route spec: `VE.Route.RunSound.route_order_certificate` → `VE.Route.WireSound.orderRunner` → `VE.Route.Checker.order` → `VE.Order.Tableau.checkCertificate` → `VE.Order.Tableau.replay` → `VE.Order.Tableau.next` → `VE.Order.Tableau.Signed.rule` |
| `VE.Order.Tableau` | `VE.Order.Tableau.addLiterals` | 13 | route spec: `VE.Route.RunSound.route_order_certificate` → `VE.Route.WireSound.orderRunner` → `VE.Route.Checker.order` → `VE.Order.Tableau.checkCertificate` → `VE.Order.Tableau.replay` → `VE.Order.Tableau.farkasCloses` → `VE.Order.Tableau.comboLin` → `VE.Order.Tableau.addLiterals` |
| `VE.Route.WireSound` | `VE.Route.Layer.toClosure` | 25 | route spec: `VE.Route.RunSound.route_closure_certificate` → `VE.Route.WireSound.closureFamily` → `VE.Route.WireSound.closureLayer` → `VE.Route.Layer.toClosure` |
| `VE.Route.WireSound` | `VE.Route.Layer.within` | 22 | route spec: `VE.Route.RunSound.route_fol_certificate` → `VE.Route.WireSound.folFamily` → `VE.Route.WireSound.fullLayer` → `VE.Route.Layer.within` |
| `VE.Route.WireSound` | `VE.Route.WireSound.Family` | 16 | route spec: `VE.Route.RunSound.route_closure_certificate` → `VE.Route.WireSound.Runner.Bound` → `VE.Route.WireSound.Family` |
| `VE.Route.WireSound` | `VE.Route.WireSound.fullLayer` | 16 | route spec: `VE.Route.RunSound.route_fol_certificate` → `VE.Route.WireSound.folFamily` → `VE.Route.WireSound.fullLayer` |
| `VE.Route.WireSound` | `VE.Route.WireSound.orderFamily` | 13 | route spec: `VE.Route.RunSound.route_order_certificate` → `VE.Route.WireSound.orderFamily` |
| `VE.Route.Budget` | `VE.Route.Budget.evalN` | 52 | route spec: `VE.Route.RunSound.runCase_dispatch` → `VE.Route.Run.dispatch` → `VE.Core.Wire.run` → `VE.Route.Budget.refutesN` → `VE.Route.Budget.evalN` |
| `VE.Route.Budget` | `VE.Route.Budget.evalC` | 48 | route spec: `VE.Route.RunSound.runCase_dispatch` → `VE.Route.Run.dispatch` → `VE.Core.Wire.run` → `VE.Route.Budget.refutesN` → `VE.Route.Budget.evalN` → `VE.Route.Budget.evalC.match_3` |
| `VE.Route.Budget` | `VE.Route.Budget.evalF` | 29 | metered spec: `VE.Route.MeteredRun.runWith_sound` → `VE.Route.MeteredRun.CaseModel` → `VE.Core.Layers.completeModel` → `VE.Route.Budget.computeDefinedS` → `VE.Route.Budget.evalF` |
| `VE.Route.Budget` | `VE.Route.Budget.tableWith` | 14 | metered spec: `VE.Route.MeteredRun.runWith_sound` → `VE.Route.MeteredRun.CaseModel` → `VE.Core.Layers.completeModel` → `VE.Route.Budget.computeDefinedWith` → `VE.Route.Budget.tableWith` |
| `VE.Route.Budget` | `VE.Route.Budget.computeDefinedWith` | 12 | metered spec: `VE.Route.MeteredRun.runWith_sound` → `VE.Route.MeteredRun.CaseModel` → `VE.Core.Layers.completeModel` → `VE.Route.Budget.computeDefinedWith` |
| `VE.Norms.Admission` | `VE.Norms.Admission.admitDocumentIn` | 29 | norms spec: `VE.Acts.Decode.norms_wire_acceptance_elaborated` → `VE.Norms.Run.AdmissionAnswerIn` → `VE.Norms.Admission.admitDocumentIn` |
| `VE.Norms.Admission` | `VE.Norms.Admission.SourceDecodedIn` | 23 | norms spec: `VE.Acts.Decode.norms_wire_acceptance_elaborated` → `VE.Norms.Run.AdmissionAnswerIn` → `VE.Norms.Admission.SourceDecodedIn` |
| `VE.Norms.Admission` | `VE.Norms.Admission.Admitted` | 13 | norms spec: `VE.Acts.Decode.norms_wire_acceptance_elaborated` → `VE.Norms.Run.AdmissionAnswerIn` → `VE.Norms.Admission.Admitted` |
| `VE.Norms.Admission` | `VE.Norms.Admission.CertificateBound` | 11 | norms spec: `VE.Acts.Decode.norms_wire_acceptance_elaborated` → `VE.Norms.Run.AdmissionAnswerIn` → `VE.Norms.Run.BindingsMatchSourceAndRegeneration` → `VE.Norms.Admission.CertificatesBound` → `VE.Norms.Admission.CertificateBound` |
| `VE.Norms.Admission` | `VE.Norms.Admission.ReportAdmitted` | 11 | norms spec: `VE.Acts.Decode.norms_wire_acceptance_elaborated` → `VE.Norms.Run.AdmissionAnswerIn` → `VE.Norms.Admission.ReportAdmitted` |
| `VE.Norms.Flagged` | `VE.Norms.Flagged.witnessFrom` | 25 | norms spec: `VE.Norms.FlaggedSpec.runCase_conflictIn` → `VE.Norms.Flagged.replayWitnessIn` → `VE.Norms.Flagged.witnessFrom` |
| `VE.Norms.Flagged` | `VE.Norms.Flagged.decodePackage` | 20 | norms spec: `VE.Norms.FlaggedSpec.runCase_conflictIn` → `VE.Norms.Flagged.replayConflictIn` → `VE.Norms.Flagged.decodePackage` |
| `VE.Norms.Flagged` | `VE.Norms.Flagged.replayEntailmentIn` | 17 | norms spec: `VE.Acts.Decode.norms_wire_certificate_acceptance_elaborated` → `VE.Norms.Flagged.replayEntailmentIn` |
| `VE.Norms.Flagged` | `VE.Norms.Flagged.replayConflictIn` | 11 | norms spec: `VE.Norms.FlaggedSpec.runCase_conflictIn` → `VE.Norms.Flagged.replayConflictIn` |
| `VE.Norms.Flagged` | `VE.Norms.Flagged.regTable` | 9 | norms spec: `VE.Norms.FlaggedSpec.runCase_conflictIn` → `VE.Norms.Flagged.replayConflictIn` → `VE.Norms.Flagged.pyTargets` → `VE.Norms.Flagged.conflictPy` → `VE.Norms.Flagged.regSubst` → `VE.Norms.Flagged.regTable` |
| `VE.Definitions.Layer` | `VE.Definitions.chainLayer` | 24 | route spec: `VE.Route.RunSound.route_fol_certificate` → `VE.Route.WireSound.folFamily` → `VE.Route.WireSound.fullLayer` → `VE.Definitions.chainLayer` |
| `VE.Definitions.Layer` | `VE.Definitions.stepLayer` | 24 | route spec: `VE.Route.RunSound.route_fol_certificate` → `VE.Route.WireSound.folFamily` → `VE.Route.WireSound.fullLayer` → `VE.Definitions.chainLayer` → `VE.Definitions.stepLayer` |
| `VE.Definitions.Layer` | `VE.Definitions.Step` | 13 | route spec: `VE.Route.RunSound.route_closure_certificate` → `VE.Route.Wire.RouteVocabulary` → `VE.Route.Wire.RouteVocabulary.mk` → `VE.Definitions.Chain` → `VE.Definitions.Step` |
| `VE.Definitions.Layer` | `VE.Definitions.ChainLayer` | 10 | route spec: `VE.Route.RunSound.route_fol_certificate` → `VE.Route.WireSound.folFamily` → `VE.Route.WireSound.fullLayer` → `VE.Definitions.ChainLayer` |
| `VE.Definitions.Layer` | `VE.Definitions.Chain` | 6 | route spec: `VE.Route.RunSound.route_closure_certificate` → `VE.Route.Wire.RouteVocabulary` → `VE.Route.Wire.RouteVocabulary.mk` → `VE.Definitions.Chain` |

## Soft norms

Listed: 3 of the 25, 997 lines; the group in the whole kernel tier: 12 modules, 1,402 lines.

| Module | Lines | Spec lines | Wrap lines | Paths that count it |
|---|---:|---:|---:|---|
| `VE.SoftNorms.Soften` | 516 | 516 | 0 | softNorms (spec) |
| `VE.SoftNorms.Phases` | 333 | 333 | 20 | softNorms (spec, wrap), metered (spec, wrap) |
| `VE.SoftNorms.Tree` | 148 | 148 | 0 | softNorms (spec) |

| Module | Definition | Lines | Chain (path, part: root first) |
|---|---|---:|---|
| `VE.SoftNorms.Soften` | `VE.SoftNorms.checkSoft` | 64 | softNorms spec: `VE.SoftNorms.Run.soft_wire_acceptance` → `VE.SoftNorms.Run.SoftAdmissionAnswer` → `VE.SoftNorms.WellFormedSoft` → `VE.SoftNorms.validateSoft` → `VE.SoftNorms.checkSoft` |
| `VE.SoftNorms.Soften` | `VE.SoftNorms.checkW1` | 58 | softNorms spec: `VE.SoftNorms.Run.soft_wire_elaborate` → `VE.SoftNorms.Wire.decodeSoftSource` → `VE.SoftNorms.validateSoftOnce` → `VE.SoftNorms.checkSoftOnce` → `VE.SoftNorms.checkW1` |
| `VE.SoftNorms.Soften` | `VE.SoftNorms.checkSoftRule` | 31 | softNorms spec: `VE.SoftNorms.Run.soft_wire_elaborate` → `VE.SoftNorms.Wire.decodeSoftSource` → `VE.SoftNorms.validateSoftOnce` → `VE.SoftNorms.checkSoftOnce` → `VE.SoftNorms.checkSoftRule` |
| `VE.SoftNorms.Soften` | `VE.SoftNorms.checkSoftEnv` | 27 | softNorms spec: `VE.SoftNorms.Run.soft_wire_elaborate` → `VE.SoftNorms.Wire.decodeSoftSource` → `VE.SoftNorms.validateSoftOnce` → `VE.SoftNorms.checkSoftOnce` → `VE.SoftNorms.checkSoftEnv` |
| `VE.SoftNorms.Soften` | `VE.SoftNorms.softSemanticCheck` | 24 | softNorms spec: `VE.SoftNorms.Run.soft_wire_acceptance` → `VE.SoftNorms.Run.SoftAdmissionAnswer` → `VE.SoftNorms.WellFormedSoft` → `VE.SoftNorms.validateSoft` → `VE.SoftNorms.softSemanticCheck` |
| `VE.SoftNorms.Phases` | `VE.SoftNorms.Phases.declarations` | 71 | softNorms spec: `VE.SoftNorms.Run.soft_wire_elaborate` → `VE.SoftNorms.Wire.decodeSoftSource` → `VE.SoftNorms.Phases.checkSource` → `VE.SoftNorms.Phases.declarations` |
| `VE.SoftNorms.Phases` | `VE.SoftNorms.Phases.ruleFields` | 51 | softNorms spec: `VE.SoftNorms.Run.soft_wire_elaborate` → `VE.SoftNorms.Wire.decodeSoftSource` → `VE.SoftNorms.Phases.checkSource` → `VE.SoftNorms.Phases.ruleFields` |
| `VE.SoftNorms.Phases` | `VE.SoftNorms.Phases.ruleReferences` | 25 | softNorms spec: `VE.SoftNorms.Run.soft_wire_elaborate` → `VE.SoftNorms.Wire.decodeSoftSource` → `VE.SoftNorms.Phases.checkSource` → `VE.SoftNorms.Phases.documentReferences` → `VE.SoftNorms.Phases.ruleReferences` |
| `VE.SoftNorms.Phases` | `VE.SoftNorms.Phases.exceptionFields` | 23 | softNorms spec: `VE.SoftNorms.Run.soft_wire_elaborate` → `VE.SoftNorms.Wire.decodeSoftSource` → `VE.SoftNorms.Phases.checkSource` → `VE.SoftNorms.Phases.ruleFields` → `VE.SoftNorms.Phases.exceptionFields` |
| `VE.SoftNorms.Phases` | `VE.SoftNorms.Phases.envelope` | 18 | softNorms spec: `VE.SoftNorms.Run.soft_wire_elaborate` → `VE.SoftNorms.Wire.decodeSoftSource` → `VE.SoftNorms.Phases.checkSource` → `VE.SoftNorms.Phases.envelope` |
| `VE.SoftNorms.Tree` | `VE.SoftNorms.SoftEnv` | 14 | softNorms spec: `VE.SoftNorms.Run.soft_wire_elaborate` → `VE.SoftNorms.Wire.decodeSoftSource` → `VE.SoftNorms.Wire.SoftEnvironment.mk` → `VE.SoftNorms.SoftEnv` |
| `VE.SoftNorms.Tree` | `VE.SoftNorms.SoftNode` | 11 | softNorms spec: `VE.SoftNorms.Run.soft_wire_selected` → `VE.SoftNorms.soften` → `VE.SoftNorms.SoftNode` |
| `VE.SoftNorms.Tree` | `VE.SoftNorms.belowLevels` | 9 | softNorms spec: `VE.SoftNorms.Run.soft_wire_elaborate` → `VE.SoftNorms.Wire.decodeSoftSource` → `VE.SoftNorms.validateSoftOnce` → `VE.SoftNorms.softSemanticCheckOnce` → `VE.SoftNorms.closureOf` → `VE.SoftNorms.belowLevels` |
| `VE.SoftNorms.Tree` | `VE.SoftNorms.Exception` | 8 | softNorms spec: `VE.SoftNorms.Run.soft_wire_elaborate` → `VE.SoftNorms.Wire.decodeSoftSource` → `VE.SoftNorms.Phases.checkSource` → `VE.SoftNorms.Phases.ruleFields` → `VE.SoftNorms.Exception` |
| `VE.SoftNorms.Tree` | `VE.SoftNorms.Incompatible` | 6 | softNorms spec: `VE.SoftNorms.Run.soft_wire_elaborate` → `VE.SoftNorms.Wire.decodeSoftSource` → `VE.SoftNorms.validateSoftOnce` → `VE.SoftNorms.softSemanticCheckOnce` → `VE.SoftNorms.collidingPairs` → `VE.SoftNorms.Incompatible` |

## Other

Listed: 0 of the 25, 0 lines; the group in the whole kernel tier: 14 modules, 427 lines.

None of the 25 largest modules is in this group.

## The script

`/tmp/kb8b/measure.py`, run as `VE_NATIVE_PREBUILT=1 .venv/bin/python /tmp/kb8b/measure.py` from the worktree (about
a minute); the tables above were printed from its JSON.

```python
"""kb-8b throwaway: the KB-4 module table from tools/kernel_closure.py's why(). Writes /tmp/kb8b/measure.json."""
import json, sys
from pathlib import Path
ROOT = Path("/home/seyran/code/ve-kb-8b")
sys.path.insert(0, str(ROOT / "tools"))
import kernel_closure as kc
registry = json.loads((ROOT / "tools/kernel-paths.json").read_text())
baseline = json.loads((ROOT / "docs/kernel/closure-baseline.json").read_text())
kernel = [p["name"] for p in registry["paths"] if p.get("tier") == "kernel"]
modules = sorted({m for row in baseline["paths"] if row["name"] in kernel
                  for m in list(row["spec_modules"]) + list(row["wrap_modules"])})
found = kc.why(registry, modules)
for row in baseline["paths"]:  # the per-part module figures are the baseline's (same registry, same Lean)
    if row["name"] not in kernel: continue
    for part in ("spec", "wrap"):
        for m, n in row[part + "_modules"].items():
            mine = [r for r in found[m] if r["path"] == row["name"] and r["part"] == part]
            assert len(mine) == 1 and mine[0]["lines"] == n, (row["name"], part, m, n, mine)
out = {}
for m, rows in found.items():
    rng = lambda parts: [(m, d["from"], d["to"]) for r in rows if r["part"] in parts for d in r["definitions"]]
    defs = {}
    for r in rows:
        for d in r["definitions"]:
            defs[d["name"]] = d["lines"]
    out[m] = {"spec": kc.covered(rng({"spec"})), "wrap": kc.covered(rng({"wrap"})), "total": kc.covered(rng({"spec", "wrap"})),
              "paths": sorted({r["path"] for r in rows}, key=kernel.index),
              "parts": [f"{r['path']} {r['part']}" for r in rows],
              "defs": sorted(defs.items(), key=lambda kv: (-kv[1], kv[0]))}
total = sum(v["total"] for v in out.values())
print("modules", len(out), "sum of module totals", total, "baseline kernel_lines", baseline["kernel_lines"])
top = sorted(out, key=lambda m: (-out[m]["total"], m))[:25]
names = [d for m in top for d, _ in out[m]["defs"][:5]]
chains = kc.why(registry, names)
best = {}
for d in names:
    rows = [r for r in chains[d] if r["chain"]]
    rows.sort(key=lambda r: (len(r["chain"]), kernel.index(r["path"]), r["part"]))
    best[d] = {"path": rows[0]["path"], "part": rows[0]["part"], "chain": rows[0]["chain"],
               "counted_by": [f"{r['path']} {r['part']}" for r in chains[d]]}
json.dump({"kernel": kernel, "kernel_lines": baseline["kernel_lines"], "sum_of_modules": total, "modules": out,
           "top": top, "chains": best}, open("/tmp/kb8b/measure.json", "w"), indent=1)
```
