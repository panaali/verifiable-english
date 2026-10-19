# Feature review: what `ve-green-qt-b1` adds over `ve-green-eff-20261018-1`

Source: the pinned 184,893-byte constitution, unchanged (`../source/SOURCE.md`, SHA-256 `fa10ed48…50dd`). Start: the translation of run `20261018T1800Z` (`prev/`), whose audit found 47 of 48 verdicts faithful and rejected one unit.

| Merged (first-parent order, newest first) | What it is (from its DELTA.md or REPORT.md) | Changes what a constitution unit can say? |
|---|---|---|
| feature/qt-b1 | `VE.Scales.*` (scale documents, grades, dimensions), trust +78 | No: "reachable from no service mode, route, decoder or relay" |
| feature/ap-2 | `VE.Acts.Syntax`, `Read`, `GrammarExamples` (act grammar vocabulary, terminals, listing) | No: "Public output: none"; nothing imports the modules but the library root |
| feature/qt-a1b | report of the cardinality spec 3.6 | No: a report and mutants, no product file |
| feature/pk-1 | premise packs for the layered norm-defaults route (`VE.NormDefaults.Packs`) | No: "every answer, array and diagnostic is today's" (452 invocations, 0 differences) |
| feature/qt-a1 | `VE.Cardinality.*` (counting atoms, proportions) | No: "reachable from no service mode, route, decoder or relay" |
| feature/sc-1a | `VE.Layout.List`, `VE.Scope.Examples` (the layout's list runs for scope@0) | No: "No route, service mode or document check imports them" until SC-1b |

Checked with `git diff ve-green-eff-20261018-1..ve-green-qt-b1 --shortstat -- ve lean rust conformance` (38 files, all new Lean modules, generated inventories and `ve/assurance-manifest.json`; no Python or Rust product file; in `metrics.json`, `language_changes_since_previous_tag`) and the DELTA.md files of sc-1a, qt-a1, pk-1, ap-2 and qt-b1. Result: **units upgraded by features: 0; reading sets upgraded by features: 0.** The cardinality and scales modules are the groundwork for the "counting" and "quantities" blockers (29 and 119 units) once a document route reaches them; this run cannot use them.

## Measurements at this tag (all re-run)
* **Build**: `lean/.lake` copied with `cp -a` from `ve-integration` at the identical commit (702ff7429); `lake build` completed (1019 jobs, 19 minutes); the Rust binary rebuilt by `tools/rust_build.py` (26 s) and equal to the pin in `lean/checkers.lock`. The carried translation was rebuilt first by `nd.py all`: cmp-identical to the 18:00Z translation (before any change).
* **Translation**: changed only by the repair of QT-0p's wording and PS-0p's two items (see AUDIT-REPAIR.md); `nd.py all` rebuilt it after the repair, after the PS-0p items and for the final document; `ve document check` (final): admitted, premises `model`, superposed route, 32 choices CONFLICT-FREE; coverage 100%, 53 open terms, 24 assumptions.
* **Probes**: risk, s1 (its input is the 06:00Z document, see README), senses, senses_document, discourse, rights, unspecified (the four AT-0p points per rule) and frame are byte-identical to the previous run's; the denial and claim-to-be-human queries are ALL with certificates; the five `ve ask` questions give no answer as before; the companion probe differs only where the vocabulary and the two new units change it (its main-component premise check is still UNKNOWN); the 21 hard-constraint queries give 12 ALL / 9 UNKNOWN (u0165.s01 "knowing" is UNKNOWN again; it was ALL at 18:00Z and UNKNOWN at 06:00Z: a search-budget effect).
* **Soft chain** (`probe_soft_chain.py`): unchanged outcome (admitted, both conclusion queries ALL, `ve document check` still raises `UnsupportedProfile`).

## Missing features, ledger tally (`UNFORMALISED`)
norms 669, quantities 119, `other:discourse` 78, causation 76, defaults 50, counting 29, modality/belief 25, attribution 12, time 9, `other:open-list` 1, `other:graded-force` 1 (`other:discourse` −2 against the previous run: the two headings PS-0p now covers).
