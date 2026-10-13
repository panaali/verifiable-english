# Feature review: what `ve-green-eff-20261011-1` adds over `ve-green-ts-B1`

Source: the pinned 184,893-byte constitution, unchanged (`../source/SOURCE.md`). Start: the translation of run `20261012T1800Z` (`prev/`), whose audit found the seven hard constraints unfaithful.

| Merged | What it is | Changes what a document can say? |
|---|---|---|
| `infra/arch-20261010-1` (AR-1, AR-5a) | audit manifests generated from the compiled environment (`lean/audit.py --write`, `statements.txt`); the evidence toolkit (`tools/evidence`, `tools/batch_evidence.py`); trust-baseline regression repair | No |
| `infra/arch-20261010-2` | tooling merge of the same train | No |
| `infra/arch-AR-9` | `ve/assist/session.py` and `recovery.py` split into six modules; a readings-route relay fix picked earlier is reverted in the batch | No |
| `infra/eff-20261011-1` | `regen_generated.py --resolve` combines concurrent trust-baseline counts | No |

Checked with `git diff ve-green-ts-B1..HEAD --stat -- ve lean rust conformance`: 16 files, namely the generated Lean audit manifests, `lean/audit.py`, one added `example` in `lean/VE/SoftNorms/Status.lean` (a restatement of an existing theorem, no new definition) and the `ve/assist` modules. None is in the grammar, profiles, lexicon, checkers or Rust. Result: **no unit is newly expressible by a feature.**

## What the measurement shows
* **The repair changes answers; the language does not.** `ve document check` of the repaired translation: premises `model`, route `superposed`, 8 of 8 choices CONFLICT-FREE (as before), 39 open terms (33 before: +14 knowing and belief terms, −7 category case atoms, −1 single epistemic term).
* **Hard constraints, asked at one-element situations** (`probes/unspecified-probe.json`, 6 points each): SETTLED no where the knowing alternative holds, where the belief alternative holds (no membership needed: the repair), and where both hold; UNDECIDED where only another category's atom holds and where neither holds. The 21 other points are the previous run's.
* **Conclusion queries** (`probes/hard-conclusions-probe.json`, `probes/nd/hard/`, superposed route): "knowing → not permitted" and "belief → not permitted" are ALL with a certificate for u0165.s02 to s07; "neither → not permitted" is UNKNOWN for all seven (intended: not entailed). For u0165.s01 all three are UNKNOWN: VE's proof search exhausts its budget (6 to 9 minutes each); the same shape of query on the previous translation is also UNKNOWN (10 minutes), so this is a limit of the proof search, not of the repair. One s01 query first failed with CheckerUnavailable (the Rust checker's 5-second limit with four queries in parallel) and was re-run alone; CheckerUnavailable was not used as a verdict.
* **Carried probes.** risk, s1, senses, senses_document, discourse and rights are byte-identical to the previous run's. The denial and claim-to-be-human conclusions are ALL as before. The companion probe: 19 decided units (1.41%) as before; the `source_word` defect remains (`CheckerUnavailable … KeyError`). `ve ask --reading`: none of the five questions read, as before.
* **Time.** One run each, not a controlled comparison: `ve document check` 41.9 s (28.1 s last run; the machine may differ, this worktree had just rebuilt the library).
* **English round trip.** All seven repaired rules read back through VE's English export; a nested guard did not (see AUDIT-REPAIR.md).

## Missing features, ledger tally (`UNFORMALISED`)
norms 669, quantities 119, `other:discourse` 81, causation 76, defaults 50, counting 31, modality/belief 25, attribution 12, time 9, `other:open-list` 1, `other:graded-force` 1 (unchanged).
Next, in order of unlock: typed modals and belief ("knowingly", "thinks it quite likely", "cannot be unlocked"), which this repair again carried with named open terms (14 of them for one list); graded quantities ("serious uplift", "quite likely"); a nested "A and B, or C" guard that reads back in English; defeasible obligations beside norm-defaults@0; decided units reported for documents without companion sets (and the `source_word` fix); a proof search that does not run out on the first of seven identical-shaped rules.
