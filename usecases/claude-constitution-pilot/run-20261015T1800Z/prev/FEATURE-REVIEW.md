# Feature review: what `ve-green-lf-14b` adds over `ve-green-repo-map-untracked`

Source: the pinned 184,893-byte constitution, unchanged (`../source/SOURCE.md`, SHA-256 `fa10ed48…50dd`). Start: the translation of run `20261014T1800Z` (`prev/`), whose audit found u0165.s03 unfaithful.

| Merged | What it is | Changes what a document can say? |
|---|---|---|
| `lean-first/b14b` (lf-14b) | non-first-order norm guards on closure, core and order families are decided in Lean (`VE.Norms.Family`, the `family-norms` service); `ve/norms.py` relays them and binds row names and counts. 1,350 corpus records give identical results on the Lean route and on the retained Python route; N-ary core definitions stay for batch 14c | No (where a closure, core or order check runs, not what a rule can say) |
| `infra/ts-B2` | test-speed and gate shadow evidence | No |
| `infra/english-run-root` | the English runner gets a distinct executable root | No |
| `fix/subtick` | sub-tick deadline probe and gate/relay evidence repairs | No |

Checked with `git diff ve-green-repo-map-untracked..ve-green-lf-14b --stat -- ve lean rust conformance`: 20 files (the Lean family decider and its service, wire and response shapes; its relay in `ve/norms.py`; the English runner's root; generated manifests). None is in the grammar, profiles, lexicon or Rust. Result: **no unit is newly expressible by a feature** (units upgraded by features: 0; reading sets upgraded by features: 0).

## What the measurement shows
* **Audit repair of u0165.s03, measured** (`probes/unspecified-probe.json`, `scope_points`): on each companion, the case holding with the *other* candidate's knowing term alone is UNDECIDED, and the other candidate's belief term alone is UNDECIDED; the candidate's own belief term alone is SETTLED no. The two candidates still differ where they should (a cyberweapon that could not cause significant damage, knowingly created: UNDECIDED wide, SETTLED no narrow). Lean separates the two candidates and checks 16 of 16 choices conflict-free.
* **AT-0p shape (carried)**: four probe kinds, seven of seven rules, all as the plan states (see AUDIT-REPAIR.md).
* **Conclusion queries on the hard constraints** (`probes/hard-conclusions-probe.json`, superposed route): see `metrics.json: checked_content_main_chain.conclusion_probes.hard_constraint_queries`. For u0165.s03 the premises name the attitude terms of both candidates so that each candidate's rule fires.
* **Carried probes.** risk, s1, senses, senses_document, discourse and rights are byte-identical to the previous run's. The denial and claim-to-be-human conclusions are ALL as before. The companion probe: 19 decided units (1.41%) as before. `ve ask --reading`: none of the five questions read, as before.
* **Vocabulary change check** (DRI 2026-10-14 15:30Z, 2): see AUDIT-REPAIR.md and `metrics.json: vocabulary_change_check`.
* **Time.** One run each on a machine at load average 25 to 80, not a controlled comparison (`metrics.json: timing_single_runs`).

## Missing features, ledger tally (`UNFORMALISED`)
norms 669, quantities 119, `other:discourse` 81, causation 76, defaults 50, counting 31, modality/belief 25, attribution 12, time 9, `other:open-list` 1, `other:graded-force` 1 (unchanged). Gaps recorded in earlier runs stay: `other:english-nested-guard`, `other:scope`.
Next, in order of unlock: typed modals and belief ("knowingly", "thinks it quite likely", "cannot be unlocked"), still carried by binary named open terms (this run needed four terms for one sentence, because each reading of the relative clause changes what the belief is about: an argument for typed attitudes whose content is a formula, so that a scope reading carries into the belief); graded quantities ("serious uplift", "quite likely"); a scope construct for lead-ins, bold labels and narrowing sentences (352 units, 29.9% of the text); an English round trip for nested guards.
