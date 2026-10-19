# Feature review: what `ve-green-et-3b` adds over `ve-green-qt-b1`

Source: the pinned 184,893-byte constitution, unchanged (`../source/SOURCE.md`, SHA-256 `fa10ed48…50dd`). Start: the translation of run `20261019T0600Z` (`prev/`), whose audit found 30 of 31 verdicts faithful and rejected one unit (u0032).

| Merged (first-parent order, newest first) | What it is (from its DELTA.md or REPORT.md) | Changes what a constitution unit can say? |
|---|---|---|
| feature/et-3b | `VE.Events.*` completion and calendar reading | No: "not reachable from any service mode, route, decoder or relay"; trust budget only |
| lean-first/b18 (lf-18) | Lean-first batch 18: no setting selects an authority; the Python rows are Lean's answers | No: 100,398 of 100,410 records identical, 12 unavailable on both sides with identical outputs |
| feature/et-7b | `alt-validate` with `norm-defaults@0` and the completion is answered (scenario values for `alternatives@0`) | No: no constitution unit uses the alternatives route |
| feature/sc-3a | scope anchors and labels (`VE.Layout.Anchors`), discourse containment bodies moved | No: discourse answers unchanged on every document; the new parts "reach no caller" until the document mode |
| feature/me-6 | physical dimensions of the calculator (`VE.Calc.Dimension`) | No: "Public output: none" |
| **feature/ps-6r** | four rows of the English idiom table: "{0} is a core value / guideline / mission / nature of {1}" | **Yes**: heading presuppositions of u0013, u0095, u0002, u0235 are writable (below) |
| feature/df-1a | `VE.Defaults.*` (premises of the no-exception defaults) | No: "no service mode, executable, schema, relay, Python or Rust product file reaches it" |
| feature/qt-a2 | `VE.Cardinality.*` typed (`CTerm`, `CFormula`, `Admitted`) | No: reachable from no service mode, route, decoder or relay |
| feature/df-03 | DF-0.3, the defeasible plan's baseline record | No: a report, no product code |

Checked with `git diff ve-green-qt-b1..ve-green-et-3b --shortstat` (311 files; 148 under `ve lean rust conformance`; unlike the last interval these include Python files, from lf-18 and et-7b) and the DELTA.md of df-1a, qt-a2, ps-6r, me-6, sc-3a, et-7b, lf-18 and et-3b. Result: **units upgraded by features: 1 (u0013, +24 B); reading sets upgraded by features: 0.**

## What ps-6r gives, measured (`ps6r_wordings.py`, `evidence/ps6r/wording-lint.json`)
The lint admits all four wordings in this document's environment and changes no existing wording; "Some thing is a core value of claude." parses to exactly `∃x core_value_of(x, claude)` and the rendering parses back to the same formula. Two points of fit: the document's English writes a constant inside a sentence in lower case ("of claude", "of anthropic"; the plan's "Claude" needs an English overlay the document format does not carry), and "the mission of Anthropic" and "Anthropic's guidelines" need `anthropic` as the second argument: it is already a constant of the sort `principal_type` (u0043.s02), so the two predicates take that sort rather than a second Anthropic constant.

## Why one of four (`evidence/ps6r/premise-variants.json`, 21 scratch builds)
With all four, `ve document check` is admitted, 32 choices conflict-free, but the premise check is UNKNOWN (`evidence/ps6r/all-four-document-check.json`). Alone, only u0013 keeps `model`; no pair does; with a predicate renamed to sort first (a measurement only), u0002 fits and u0095, u0235 do not. The cause is in the Rust model search (`rust/ve-profile/src/search.rs`, `advance_subset`): relation subsets are tried by size and then in the order of the used atoms (sorted by predicate name) within 10,000 models; each existential needs one true atom next to `novel_entity(claude)` and `open_problem(x)`. The English was never the obstacle. The DRI has not accepted UNKNOWN for the constitution's premise check, so u0095, u0002 and u0235 are not claimed.

## Measurements at this tag (all re-run)
* **Build**: `lean/.lake` copied with `cp -a` from `ve-integration` at the identical commit (beb5c4630); `lake build` completed (1033 jobs, 35 minutes: the copy's paths differ, so it rebuilt); `tools/rust_build.py` rebuilt the binary (45 s), equal to the pin in `lean/checkers.lock`. The carried translation was rebuilt first by `nd.py all`: cmp-identical to the 06:00Z translation (before any change).
* **Translation**: changed only by `repair_20261019T1800Z.py --only=u0013`; `nd.py all` rebuilt it; `ve document check`: admitted, premises `model`, superposed route, 32 choices CONFLICT-FREE; coverage 100%, 52 open terms, 24 assumptions. The fenced units of the start document (u0245, u0286) parse to the same formulas (`evidence/checkpoint-final.json`, `x3_fences`).
* **Probes**: risk, s1, senses, senses_document, discourse, rights, unspecified (the four AT-0p points per rule) and frame are byte-identical to the previous run's; the denial, claim-to-be-human and "no fourth type of principal" queries are ALL with certificates; the five `ve ask` questions give no answer as before; the companion probe differs only in u0013 taking u0032's place (premise check of its main component still UNKNOWN, 4 units Lean-decided); the 21 hard-constraint queries give 12 ALL / 9 UNKNOWN, every verdict as at the previous run.
* **Soft chain**: unchanged outcome (admitted, both conclusion queries ALL, `ve document check` still raises `UnsupportedProfile`).

## Missing features, ledger tally (`UNFORMALISED`)
norms 669, quantities 119, `other:discourse` 75, causation 76, defaults 50, counting 29, modality/belief 25, attribution 12, time 9, `other:premise-check-budget` 3 (new), `other:open-list` 1, `other:graded-force` 1.
