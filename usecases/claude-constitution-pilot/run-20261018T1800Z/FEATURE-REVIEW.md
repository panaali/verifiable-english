# Feature review: what `ve-green-eff-20261018-1` adds over `ve-green-tarch-histdep`

Source: the pinned 184,893-byte constitution, unchanged (`../source/SOURCE.md`, SHA-256 `fa10ed48…50dd`). Start: the translation of run `20261018T0600Z` (`prev/`), whose audit found 25 of 25 verdicts faithful.

| Merged (first-parent order, newest first) | What it is (from its DELTA.md) | Changes what a constitution unit can say? |
|---|---|---|
| infra/eff-20261018-1 | efficiency tooling and a write log | No |
| feature/et-7 | `alternatives@0` accepted together with `norm-defaults@0` (`VE.Compose.todayGate`, `dispatch`, `ve.profiles.checker_family`); alternatives routes answer filled sources | No: the constitution uses no `alternatives@0` profile |
| feature/fsf-r1 | a use case (safety framework): documents and reports | No: no product code |
| infra/speed-abcache | speed tooling | No |
| infra/ties-me-1c, ties-me-1b, ties-me-1a | theorems tying existing definitions; seeded ties | No |
| feature/jt-1 | `judgments@0`: records and admission of judgment terms, the shared scan | No: "reached by no route until JT-2 switches the profile on in the document mode" |
| infra/tarch-manifest-ops | test architecture | No |
| infra/me-1c, me-1b | `VE.Calc` meaning, checker and English lines | No: "Public output: none" |
| feature/et-3 | `lean/VE/Events/*` (events, states, links, calendar premises) | No: "not reachable from any service mode, route, decoder or relay" |
| feature/pk-1s | premise-pack spec, documents only | No |

Checked with `git diff ve-green-tarch-histdep..ve-green-eff-20261018-1 --shortstat -- ve lean rust conformance` (in `metrics.json`, `language_changes_since_previous_tag`) and the DELTA.md files of jt-1, et-3, et-7, me-1b, me-1c and pk-1s. Result: **units upgraded by features: 0; reading sets upgraded by features: 0.**

## Measurements at this tag (all re-run)
* **Build**: `lean/.lake` copied with `cp -a` from `ve-integration` at the identical commit; `lake build` still rebuilt all 997 jobs (25 minutes); the Rust binary rebuilt by `tools/rust_build.py` (42 s) and equal to the pin in `lean/checkers.lock`. The carried translation was rebuilt first by `nd.py all`: cmp-identical to the 06:00Z translation (before any change).
* **Translation**: changed only by the plans below (`apply_plans.py`); `nd.py all` rebuilt it after QT-0p, after the PS-0p builds and for the final document; `ve document check` (final): admitted, premises `model`, superposed route, 32 choices CONFLICT-FREE; coverage 100%, 52 open terms, 22 assumptions.
* **Probes**: risk, s1 (see README), senses, senses_document, discourse, rights, unspecified (the four AT-0p points per rule) and frame are byte-identical to the previous run's; the denial and claim-to-be-human queries are ALL with certificates; the five `ve ask` questions give no answer as before; the companion probe differs (QT-0p, see SUMMARY); the 21 hard-constraint queries give 13 ALL / 8 UNKNOWN (u0165.s01 "knowing" changed from UNKNOWN to ALL).
* **Soft chain** (`probe_soft_chain.py`): unchanged outcome (admitted, both conclusion queries ALL, `ve document check` still raises `UnsupportedProfile`).

## Missing features, ledger tally (`UNFORMALISED`)
norms 669, quantities 119, `other:discourse` 80, causation 76, defaults 50, counting 29, modality/belief 25, attribution 12, time 9, `other:open-list` 1, `other:graded-force` 1 (counting −2 and `other:discourse` −1 against the previous run: the units QT-0p and PS-0p now cover).
