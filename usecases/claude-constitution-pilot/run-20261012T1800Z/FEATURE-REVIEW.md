# Feature review: what `ve-green-ts-B1` adds over `ve-green-devtime-1`

Source: the pinned 184,893-byte constitution, unchanged (`../source/SOURCE.md`). Start: the translation of run `20261012T0600Z` (`prev/`), whose audit found 5 of 20 sampled units unfaithful.

| Merged | What it is | Changes what a document can say? |
|---|---|---|
| `infra/ts-B5` | test-speed B5: run order, `--maxfail`, a tracked quarantine, a gate that never stops early | No |
| `infra/ts-B1` | test-speed B1: manifest, mode schemas and Lean module selection decoupled for test selection; audit events in `ve/assurance.py`; a schema-compile lock in `ve/backends/service_schema.py` | No |

Checked with `git diff ve-green-devtime-1..HEAD --stat -- ve lean rust conformance`: two Python files, neither is in the grammar, profiles, lexicon, Lean or Rust. Result: **no unit is newly expressible by a feature.**

## What the measurement shows
* **The repair changes answers; the language does not.** `ve document check` of the repaired translation: premises `model`, route `superposed`, 8 of 8 choices CONFLICT-FREE (16 of 16 before), 33 open terms (one removed, one added). The denial conclusion ("every instance of Claude: not may directly deny being Claude") is ALL on the superposed route with a certificate and an English line; before it was UNKNOWN across the two readings. The claim-to-be-human conclusion is ALL as before.
* **Hard constraints, asked at one-element situations** (probes/unspecified-probe.json): where the case and the knowledge-or-likelihood condition hold, SETTLED no; where the case holds but the condition does not, UNDECIDED; where the case does not hold, UNDECIDED. Before: SETTLED no wherever the case held.
* **Carried probes.** risk, s1, senses, senses_document, discourse and rights are byte-identical to the previous run's. The companion probe: 19 decided units (1.41%) as before, now with three components plus the main one; the `source_word` defect remains (`CheckerUnavailable … KeyError`). `ve ask --reading`: none of the five questions read, as before.
* **Time.** One run each, not a controlled comparison: `ve document check` 28.4 s (48.9 s last run; the machine may differ, and there are 8 choices instead of 16).
* **Conflicts.** None reported by VE, so none to classify as a source conflict or a translation artefact.

## Missing features, ledger tally (`UNFORMALISED`)
norms 669, quantities 119, `other:discourse` 81, causation 76, defaults 50, counting 31, modality/belief 25, attribution 12, time 9, `other:open-list` 1, `other:graded-force` 1 (unchanged).
Next, in order of unlock: typed modals and belief (“knowingly”, “thinks it quite likely”, “cannot”, “unlocked by”), the first thing this repair had to stand in for with an open term; graded quantities (“serious uplift”, “vast majority”); context-sensitive defeasible obligations beside norm-defaults@0; decided units reported for documents without companion sets (and the `source_word` fix); English for a gated UNKNOWN on the superposed route.
