# Feature review: what `ve-green-ap-1a` adds over `ve-green-et-3b`

Source: the pinned 184,893-byte constitution, unchanged (`../source/SOURCE.md`, SHA-256 `fa10ed48…50dd`). Start: the translation of run `20261019T1800Z` (`prev/`), whose audit found 31 of 31 verdicts faithful.

| Merged (oldest first) | What it is (from its DELTA.md or report) | Changes what a constitution unit can say? |
|---|---|---|
| infra/eff-20261019-1 | `tools/regen_generated.py` builds and pins `ve_service` before the entries that start it | No: Python tooling only |
| feature/me-5 | `VE.Calc.{Linear,FourierMotzkin,Derive}`: derivations over rational unknowns | No: "Public output: none" (no service mode, route, schema, Python or Rust file) |
| feature/jt-1b | `VE.Judgments.Status`: dependence, unit status and usage map of `judgments@0` | No: reached by no service mode, route or document check before JT-2; **measured**: `judgments@0` in a document is `UnsupportedProfile` |
| feature/et-8 | two harnesses (a use case's and an experiment's), one test file, README text | No: no product code |
| feature/ar-10a | the profile-gate table `VE.Compose.gateOf profileTable`; Python reads `ve/profile_table.json` and its gate mirror (`checker_family`) is deleted | No verdict moves; a list with an unregistered profile is refused for that profile first (fault order and text). Visible only in `probe_risk.py`, which imported the deleted mirror (repaired, see README) |
| infra/arch-20261019-1 (AR-17) | the readings route relays Lean's S2 row (checked for schema and binding) instead of recomputing it | No: 45 report records change one wording in `checked_by.python` |
| feature/pk-1b | norm-defaults layered cases dispatch through a kind table (`kindCase`, proved equal to `layeredCase`) | No: 445 invocations, 0 differences |
| infra/arch-20261019-2 (AR-16a) | `ve/document.py` moved into the package `ve/document/` verbatim | No: 63 of 63 definitions verbatim, 0 differences on nine corpora |
| feature/ap-1a | `VE.Acts.{LexicalBase,Lexical,Compat}` and the profile-aware decoder: lexical acts | No: "Public output: none changes"; `acts@0` has no profile row until ap-1b; **measured**: `acts@0` in a document is `UnsupportedProfile` (`evidence/new-profile-probe.json`) |

Checked with `git diff ve-green-et-3b..ve-green-ap-1a --shortstat` (172 files; 55 under `ve lean rust conformance`) and the `DELTA.md` of ap-1a, AR-16a, AR-17, ar-10a, et-8, jt-1b, me-5, pk-1b and the report of eff-20261019-1. Result: **units upgraded by features: 0 (+0 B); reading sets upgraded by features: 0.**

## What the two new Lean modules are for (not yet usable)
* `acts@0` (ap-1a, then ap-1b opens the profile) is the lexical act phrase: 17 constitution norm units (2,502 B, `act_workaround_m4`) use a pointer, folded or shortened act phrase today.
* `judgments@0` (jt-1b, then JT-2 opens it in the document mode) gives judgment terms a status: 507 units (88,996 B) name a term of class `judgment`.
Neither can be tried before its profile row lands; this run only records that both are refused.

## Measurements at this tag (all re-run)
* **Build**: `lean/.lake` and `rust/target` copied with `cp -a` from `ve-integration` at the identical commit (`b1f7ca7ad`); `lake build` completed (1045 jobs, 31 min 46 s: the copy's paths differ, so it rebuilt); the Rust binary equals the pin in `lean/checkers.lock` (`tools/rust_build.py --check`).
* **Translation**: `nd.py all` rebuilt from the carried start document is cmp-identical to the previous run's translation. `ve document check`: admitted, premises `model`, superposed route, 32 choices CONFLICT-FREE; coverage 100%, 52 open terms, 24 assumptions.
* **Probes**: unspecified (the four AT-0p points per rule), s1, senses, senses_document, discourse, rights, frame, hard-constraint (21 queries: 12 ALL, 9 UNKNOWN) and companion are byte-identical (companion after the run id is normalised); risk differs only in two profile-gate rows (README); the denial, claim-to-be-human and "no fourth type" queries are ALL with certificates; the five `ve ask` questions give no answer as before.
* **Soft chain**: unchanged outcome (`ve document check` raises the same `UnsupportedProfile`; both conclusion queries ALL).

## Missing features, ledger tally (`UNFORMALISED`)
norms 669, quantities 119, `other:discourse` 75, causation 76, defaults 50, counting 29, modality/belief 25, attribution 12, time 9, `other:premise-check-budget` 3, `other:open-list` 1, `other:graded-force` 1.
