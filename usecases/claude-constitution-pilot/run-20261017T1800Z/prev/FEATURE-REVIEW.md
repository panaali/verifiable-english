# Feature review: what `ve-green-rights-licence-relay` adds over `ve-green-trust-ties-rd9`

Source: the pinned 184,893-byte constitution, unchanged (`../source/SOURCE.md`, SHA-256 `fa10ed48…50dd`). Start: the translation of run `20261016T1800Z` (`prev/`), whose audit found all 30 audited units faithful.

| Merged | What it is | Changes what a constitution unit can say? |
|---|---|---|
| `infra/rights-licence-relay` | Lean's rights route now returns each line instance's narrowing mechanisms with the licence each holds (`Rights/Scope.lean`, new fields in the rights response rows and shape); Python relays them under a binder check (`ve/backends/shape_binding.py`, `ve/rights_route.py`) instead of recomputing them | No: the constitution has no `rights@0` document, and the route says what it said |
| `infra/tarch-store`, `tarch-cutoff`, `tarch-binding` | answer-store byte replay, CI cutoff, shape-binding census (test architecture) | No |

Checked with `git diff ve-green-trust-ties-rd9..HEAD --stat -- ve lean rust conformance`: 15 files, 1,451 insertions and 205 deletions, all in the rights route and its relay (`lean/VE/Rights/Run.lean`, `Scope.lean`, the rights response shape and encoder, generated manifests, `ve/backends/lean_service.py`, `shape_binding.py`, `lean_service_schema/rights.json`, `ve/rights_route.py`). No grammar production, profile or lexicon entry that a norm, guard or reading set of the constitution could use was added. Result: **no unit is newly expressible by a feature** (units upgraded by features: 0; reading sets upgraded by features: 0). The soft chain is not through `ve document check` yet: the soft-chain probe still ends in `UnsupportedProfile: norm-defaults@0 documents are checked through fill`.

## Measurements at this tag (all re-run; every result equals the previous run's)
* **Translation**: `nd.py all` rebuilds it; it differs from the previous run's in the three repaired `meaning` fields only. `ve document check` passes (premises model, superposed route, all 16 choices CONFLICT-FREE); coverage 100% of bytes accounted, residual 50 open terms, 4 unresolved reading sets.
* **Probes**: the unspecified probe, risk, s1, senses, senses_document, discourse and rights probes are byte-identical to the previous run's; the profile-combination probe has the same thirteen rows; the companion probe, the denial and claim-to-be-human conclusion queries (ALL, superposed) and the five `ve ask` questions (no answer) are identical. AT-0p's four kinds: SETTLED no, SETTLED no, UNDECIDED, UNDECIDED for all seven rules.
* **Hard-constraint queries**: the same 12 ALL with certificates and 9 UNKNOWN (the seven "neither" queries by design, plus u0165.s01 knowing and belief), all answered on the first run at the default Rust limit (three in parallel, 22 minutes).
* **Soft chain** (`probe_soft_chain.py`, `evidence/soft-chain-probe.json`): as before: admitted, every pair separated, coverage and render work, both conclusion queries ALL in 16 of 16 choices, 47 open terms instead of 50, `ve document check` fails with the uncaught `UnsupportedProfile`. The unit meanings of the soft form carry no exception term (the unnamed exception is not an open term there).
* **Time** (one run each, load average about 10, not controlled): `ve document check` 25.6 s (56 s), coverage 23.6 s (47 s), `lake build` 16 min 25 s although the copied build was of the identical commit.

## Missing features, ledger tally (`UNFORMALISED`)
norms 669, quantities 119, `other:discourse` 81, causation 76, defaults 50, counting 31, modality/belief 25, attribution 12, time 9, `other:open-list` 1, `other:graded-force` 1 (unchanged). Gaps recorded in earlier runs stay: `other:english-nested-guard` (all seven hard-constraint rules render but do not read back), `other:scope`.
Next, in order of unlock: the soft chain through `ve document check` (native defeasible "should": the three `exception_to_*` terms go); typed modals and belief (know, intend, think "quite likely"); graded quantities; a scope construct for lead-ins, bold labels and narrowing sentences (352 units, 29.9% of the text); an English round trip for nested guards.
