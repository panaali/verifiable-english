# Feature review: what `ve-green-arch-AR-6` adds over `ve-green-lf-16c`

Source: the pinned 184,893-byte constitution, unchanged (`../source/SOURCE.md`, SHA-256 `fa10ed48…50dd`). Start: the translation of run `20261010T0600Z` (`prev/`). Five first-parent merges since `ve-green-lf-16c`.

| Merged | What it is | Changes what a document can say? |
|---|---|---|
| `question-answering/integrate` (Q1) | `ve ask`: a yes-or-no question is read as one of the document's sentences by the English reader; answering (Q2) is not built | No (questions are not document content) |
| `infra/eff-tests` | work-bound differential fuzzing, gate `--rerun-failed`, run cache | No |
| `readings-defaults/rd4b` (rd-4b) | readings with their own vocabulary (`companion`) through `ve document`: Lean splits the document into components, a companion set is checked by itself, the verdicts are a product; the product route reports `decided_units`; “reading N” is the reading's own sentence in the English | Repackages reading sets; no new meaning |
| `infra/eff-merge` | merge driver and `--resolve` for generated files | No |
| `infra/arch-AR-6` | architecture map work | No |

Result: **no unit changes status because of a feature, and no unit is newly expressible.** The status of every unit is the previous run's (the eleven changes of this run are audit repairs to wording, not statuses). Claimed coverage does not move.

## What the measurement shows
* **Same verdicts.** `ve document check` of the unchanged previous translation at arch-AR-6 (`check-baseline.json`): premises `model`, enumerated plan, 16 choices, conflict-free, field for field the previous run's (54.6 s here). The repaired translation gives the same verdicts (only the document id and admission report id differ: the document's open terms changed).
* **Probes.** The seven carried probes re-run; all seven are byte-identical to the previous run's JSON. The conclusion queries have the same verdicts, routes and evidence; their English is new (rd-4b): an UNKNOWN answer now names the chosen readings' own sentences (“Read sentence 132 as … and sentence 471 as …: VE could not check whether the conclusion follows”).
* **Companion probe (new; `probe_companions.py`, `probes/companion/`).** The four “should” sets re-written as companion sets (same contents, situations and units; each candidate carries the main environment without `readings@1` and the open terms its content names):
  * `ve document check` accepts it (without `source_word`): route `components` (main + four sets), conflict-free, premises `model` in all five components, 2 outcome + 2 selects separations; coverage bytes identical to the translation's.
  * **Lean-decided units: 19 units, 2,602 bytes, 1.41%** (the translation itself: 0.00%, because without companion sets the established route reports no `decided_units`). Caveat: the four sets are each checked by themselves (VE's English says “VE did not check it together with the other sentences”), and a rule checked by itself is conflict-free by construction.
  * **Conclusion queries become decided.** “Claude may not directly deny being Claude” (with `--sentence u0125.s04.p2`): ALL under the strict reading, NONE under the defeasible one (its exception can hold), SOME across readings. The plain route gives UNKNOWN across readings and under the defeasible reading, ALL under the strict. “No operator may give Claude an instruction to claim to be human”: ALL in both. I did not analyse why the plain route cannot decide the two UNKNOWN cases; the contents are the same, only the packaging differs.
  * **Defect found.** With the sets' `source_word` (the span of “should”, which the plain route uses for the English of the two readings) the same document fails: `ve document check`, `coverage` and `render` give `CheckerUnavailable: ReadingsConstruction … KeyError`. Cause: `subdoc` in `ve/readings_components.py` builds the component's document without the `source` key that `Wording.source_word` (`ve/readings_route.py:804`) reads. The tests' companion fixtures carry no `source_word`. The probe drops `source_word`.
  * A conclusion that fits several sentences is refused unless `--sentence <unit>` names one (19 sentences fit the denial query).
* **Not adopted in the translation.** The translation keeps the plain form: companions change no unit's status, lose the `source_word` English and check each set alone. The probe is evidence that the decided share is reachable, not a claim.
* **Question reader (Q1).** `ve ask … --reading` on five questions about the denial, clarification and claim-to-be-human units: none has a reading (“Unknown English phrase 'must not'”, “'each situation'”, “'may give Claude an instruction to …'”). The reader knows only the controlled English of the vocabulary's wordings; answering is Q2, not merged.

## Costs and limits (unchanged unless said)
* A defeasible rule beside norm-defaults@0 is still refused (probe c, byte-identical): the defeasible candidates are the strict rule with an `unless` over an open term the translator names (four `exception_to_*` terms).
* `ve document` now accepts a reading with `companion` (rd-4b), except together with `source_word` (defect above).
* Open terms 33 (two lost a factor).

## Missing features, ledger tally (`UNFORMALISED`)
norms 669, quantities 119, `other:discourse` 81, causation 76, defaults 50, counting 31, modality/belief 25, attribution 12, time 9, `other:open-list` 1, `other:graded-force` 1 (unchanged).
Next, in order of unlock: typed modals and authority (“cannot”, “can”, “may”, “unlocked by”: ability, permission or authority); graded quantities (“serious uplift”, “vast majority”); context-sensitive defeasible obligations beside norm-defaults@0; decided units reported for documents without companion sets (and the `source_word` fix) so the decided share can be read off the translation itself.
