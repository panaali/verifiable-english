# Feature review: what `ve-green-sc-1ad` adds over `ve-green-sc-1ac`

Source: the pinned 184,893-byte constitution, unchanged (`../source/SOURCE.md`, SHA-256 `fa10ed48…50dd`). Start: the translation of run `20261020T1800Z` (`prev/`).

| Merged (oldest first) | What it is (from its DELTA.md) | Changes what a constitution unit can say? |
|---|---|---|
| feature/ap-1c | `VE.Acts.LexicalProofs` (theorems about the lexical act check) and `check_extends` in `VE.Acts.Compat` | No: "None. The item adds theorems and their lemmas only"; no definition, diagnostic, limit, verdict, field or mode changes; trust +0 |
| feature/me-6b | `VE.Calc.Units` (`ve-units@2`: `UnitDef`, `UnitEnv`, `decodeV2`) | No: "Public output: none"; no service mode, command or route; reached only by the Lean build and `tests/test_calc_units.py` |
| feature/et-3cb | `VE.Events.{Calendar,Conservative}` (`eventsPremises_satisfiable`, `embeddable_complete`) | No: "None"; the Events modules are reachable from no service mode, route, decoder or relay |
| feature/df-1ac | `VE.Defaults.Wire` (the `defaults-elaborate` and `defaults-coherence` kinds) | No: "What users see does not change"; no service mode, executable, schema, relay, Python or Rust file calls them (df-1ad's kind-table row would) |
| feature/sc-1ad | `VE.Scope.{Govern,Theorems}` (the graph step, `governFast`, four theorems) | No: "The changed definitions reach no caller" until the document mode (SC-1b); `govern` answers a precedes or yields governor, its text `ScopeNoEffect` appears in no answer yet |

Checked with `git diff ve-green-sc-1ac..ve-green-sc-1ad --shortstat` (98 files; under `ve/ rust/ conformance/ lean/VE/Service lean/ResponseShape` only `ve/assurance-manifest.json` changes, bookkeeping the manifest tests require) and the five DELTA files named above. Result: **units upgraded by features: 0 (+0 B); reading sets upgraded by features: 0.**

## Measurements at this tag
* **Build**: `lean/.lake` and `rust/target` copied with `cp -a` from `ve-integration` at the identical commit (`68f18dcdc`); `lake build` completed (1058 jobs; the copy's paths differ, so it rebuilt); the Rust binary equals the pin in `lean/checkers.lock` (`tools/rust_build.py --check`).
* **Translation, before any repair**: `nd.py all` on the carried start document rebuilt a translation cmp-identical to the previous run's (4 min 49 s). So the language at this tag reads the same document the same way.
* **New profiles**: each of `scope@0`, `defaults@0`, `calc@0`, `acts@0`, `judgments@0` added to the strict companion's environment is refused by `ve document check` with `UnsupportedProfile` (`evidence/new-profile-probe.json`).
* **After the audit repairs** (`AUDIT-REPAIR.md`): `ve document check` admitted, premises `model`, 2 reading sets, 8 choices, all CONFLICT-FREE; coverage 100%; 49 open terms; probes in `metrics.json`.

## What the new Lean modules are for (not yet usable)
`scope@0` (the 150 governors, 352 units, 55,294 B of `scope-tally.json`) is still the top of the "still missing" list: the graph step and `governFast` are now built, the document mode is next. `defaults@0` has a wire but no route; `calc@0` (units) no route; `acts@0` and `judgments@0` as before (17 norm units with an act workaround, 507 units with a judgment term at the last count; 15 and 506 now, `act_workaround_m4`, `judgment_term_units`).

## Missing features, ledger tally (`UNFORMALISED`)
norms 669, quantities 119, `other:discourse` 76, causation 76, defaults 50, counting 29, modality/belief 25, attribution 12, time 9, `other:premise-check-budget` 3, `other:silence-display` 2 (new: the two demoted units), `other:open-list` 1, `other:graded-force` 1.
