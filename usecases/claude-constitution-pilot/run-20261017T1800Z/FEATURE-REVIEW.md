# Feature review: what `ve-green-fu-ar2-decoders` adds over `ve-green-rights-licence-relay`

Source: the pinned 184,893-byte constitution, unchanged (`../source/SOURCE.md`, SHA-256 `fa10ed48…50dd`). Start: the translation of run `20261017T0600Z` (`prev/`), whose audit found 24 of 25 units faithful and u0156.s03 unfaithful.

| Merged | What it is | Changes what a constitution unit can say? |
|---|---|---|
| `infra/fu-premise-f9` | a test that a timeout in the lifted choices' searches alone is `CheckerUnavailable` (`tests/test_premise_scale.py`) | No |
| `infra/fu-ar2-decoders` | a DECODERS completeness test (`tests/test_frozen_sources.py`), the widest trusted line at the base (`tools/trust_map.py`, `tools/trust_changes.py`), report and seeded bugs (`docs/fu-ar2-decoders/`) | No |

Checked with `git diff ve-green-rights-licence-relay..HEAD --stat -- ve lean rust conformance`: empty. The whole diff is 6 files (435 insertions, 47 deletions): two tests, two tools, two documents. Result: **no unit is newly expressible by a feature** (units upgraded by features: 0; reading sets upgraded by features: 0). The soft chain is not through `ve document check` yet (`probe_soft_chain.py`: admitted, every pair separated, coverage and render work, both conclusion queries ALL, 48 open terms instead of 51, `ve document check` fails with the uncaught `UnsupportedProfile`).

## Measurements at this tag (all re-run)
* **Build**: `lean/.lake` copied from the checkout at the identical commit (`lake build`: 0.6 s, 957 jobs up to date); the Rust binary rebuilt by `tools/rust_build.py --check` (35 s) and equal to the pin in `lean/checkers.lock`.
* **Translation**: `nd.py all` rebuilds it (cmp-identical to `readings/nd-all.ve.md`); it differs from the previous run's in the reading set of u0156.s03 (four candidates), the frame term, and the record of `illegitimate_absolute_control`. `ve document check` passes (premises model, superposed route, all 32 choices CONFLICT-FREE); coverage 100% of bytes accounted, residual 51 open terms, 4 unresolved reading sets, 9 separations (was 4: u0156.s03 has 6 pairs).
* **Probes**: the unspecified, risk, s1, senses, senses_document, discourse and rights probes are byte-identical to the previous run's; the profile-combination probe has the same thirteen rows; the denial and claim-to-be-human conclusion queries are ALL (superposed); the five `ve ask` questions give no answer as before (only the environment and lexicon ids differ, since the vocabulary has one more predicate); the companion probe differs only where u0156.s03 has four candidates instead of two. New: `probes/frame-probe.json`.
* **Hard-constraint queries**: the same 12 ALL with certificates and 9 UNKNOWN (the seven "neither" queries by design, plus u0165.s01 knowing and belief), all answered on the first run at the default Rust limit.
* **Time** (one run each, load average 20 to 35, not controlled): `ve document check` 51.5 s (25.6 s), coverage 64.7 s (23.6 s); four candidates and 32 choices in place of 16 cost roughly twice as much.

## Missing features, ledger tally (`UNFORMALISED`)
norms 669, quantities 119, `other:discourse` 81, causation 76, defaults 50, counting 31, modality/belief 25, attribution 12, time 9, `other:open-list` 1, `other:graded-force` 1 (unchanged). Gaps recorded in earlier runs stay: `other:english-nested-guard`, `other:scope`.
This run adds a data point for the scope gap: u0156.s03 needed a hand-made frame candidate and a hand-named open term for what a scope construct (a lead-in "Consider a situation where …" governing the sentences after it) would say once. Next, in order of unlock: the soft chain through `ve document check`; typed modals and belief; graded quantities; a scope construct (352 units, 29.9% of the text); an English round trip for nested guards.
