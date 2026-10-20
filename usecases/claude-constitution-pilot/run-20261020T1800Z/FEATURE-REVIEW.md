# Feature review: what `ve-green-sc-1ac` adds over `ve-green-ap-1a`

Source: the pinned 184,893-byte constitution, unchanged (`../source/SOURCE.md`, SHA-256 `fa10ed48…50dd`). Start: the translation of run `20261020T0600Z` (`prev/`).

| Merged (oldest first) | What it is (from its DELTA.md or report) | Changes what a constitution unit can say? |
|---|---|---|
| feature/qt-b1b | `VE.Scales.{Degrees,Intended,Theorems,Examples}`: the model-construction half of QT-B1 (degree classes, `StrictLinear`, `Fresh`) | No: "reachable from no service mode, route, decoder or relay"; only a trust row (S +9) |
| feature/sc-1ab | `VE.Scope.Effects`: scope's effects on a rule's JSON object | No: "the new definitions reach no caller"; its texts appear in no answer |
| feature/ar-10b | `VE.Service.Registry`: the route registry moved out of `Protocol.lean`; `envelope.json` states the mode list as a `const` | No: the same 37 modes in the same order; no verdict, text, code, path or fault order moves |
| feature/df-1ab | `VE.Defaults.Premises` (`DefaultCoherent`, collision checks); proof helpers in `SoftNorms/RankProof.lean` | No: no service mode, executable, shape, relay, Python or Rust file reaches it |
| infra/speed-trustmut | builder and reviewer tooling (`tools/trust_mutants.py`, `tools/trust_map.py` span rules) | No: nothing under `ve/ lean/ rust/ conformance/` |
| feature/et-3c | `VE.Events.Conservative` (`events_conservative`, `dateName_inj`; fixture T7) | No: the Events modules are reachable from no service mode, route, decoder or relay |
| feature/qt-a1c | `VE.Cardinality.Theorems`: `count_*_agree` and `refutesC_sound` proved | No: trust +0, "no route reaches the new proofs" |
| feature/me-9 | `VE.Calc.Poly`: algebraic identities, the normaliser | No: "Public output: none" |
| infra/eff-20261020-1 | a measurement of the drift check's binary cutoff, stopped by its stop rule | No: changes no code |
| feature/sc-1ac | `VE.Scope.Govern` (`reaches`, `admitBlock`, `govern`) with theorems and fixtures | No: "reach no caller until the document mode (SC-1b)"; `UnsupportedProfile` refusals stand until sc-1ad and sc-3ab |

Checked with `git diff ve-green-ap-1a..ve-green-sc-1ac --shortstat` (213 files; 36 under `ve lean rust conformance`, the Lean ones new modules, proof edits or generated inventories, plus `ve/backends/service_schema.py` and `envelope.json` for ar-10b) and the DELTA/REPORT files named above. Result: **units upgraded by features: 0 (+0 B); reading sets upgraded by features: 0.**

## What the new Lean modules are for (not yet usable)
* `scope@0` (sc-1ab, sc-1ac; the document mode is SC-1b, with sc-1ad and sc-3ab first) is cross-sentence scope as a construct: the governor tally (150 governors, 352 units, 55,294 B, `scope-tally.json`) is what it will act on. This is the top of the "still missing" list.
* `defaults@0` (df-1ab; the wire and kinds are df-1ac) and `calc@0` (me-9) have no document route.
* `acts@0` (ap-1a, opens with ap-1b) and `judgments@0` (jt-1b, opens with JT-2) as before: 17 norm units (2,502 B, `act_workaround_m4`) and 507 units (88,996 B, `judgment_term_units`) wait for them.
**Measured:** each of `scope@0`, `defaults@0`, `calc@0`, `acts@0`, `judgments@0` added to the strict companion's environment is refused by `ve document check` with `UnsupportedProfile: Unsupported profile <name>` (`evidence/new-profile-probe.json`).

## Measurements at this tag (all re-run)
* **Build**: `lean/.lake` and `rust/target` copied with `cp -a` from `ve-integration` at the identical commit (`9b7e6e5c7`); `lake build` completed (1053 jobs, 17 min 6 s: the copy's paths differ, so it rebuilt); the Rust binary equals the pin in `lean/checkers.lock` (`tools/rust_build.py --check`).
* **Translation**: `nd.py all` rebuilt from the carried start document is cmp-identical to the previous run's translation (4 min). `ve document check`: admitted, premises `model`, superposed route, 32 choices CONFLICT-FREE; coverage 100%, 52 open terms, 24 assumptions. `checkpoint.py final`: no fenced unit differs from the start.
* **Probes**: unspecified (the four AT-0p points per rule), risk, s1, senses, senses_document, discourse, rights, frame, the 21 hard-constraint queries (12 ALL, 9 UNKNOWN), companion (after the run id is normalised) and the five `ve ask` questions are byte-identical or equal to the previous run's; the denial, claim-to-be-human and "no fourth type of principal" queries are ALL with certificates (the positive "fourth type" query UNKNOWN as before).
* **Soft chain**: unchanged outcome (`ve document check` raises the same `UnsupportedProfile`; both conclusion queries ALL).

## Missing features, ledger tally (`UNFORMALISED`)
norms 669, quantities 119, `other:discourse` 75, causation 76, defaults 50, counting 29, modality/belief 25, attribution 12, time 9, `other:premise-check-budget` 3, `other:open-list` 1, `other:graded-force` 1.
