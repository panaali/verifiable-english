# Feature review: what `ve-green-fix-abbrev` adds over `ve-green-lf-14b`

Source: the pinned 184,893-byte constitution, unchanged (`../source/SOURCE.md`, SHA-256 `fa10ed48…50dd`). Start: the translation of run `20261015T0600Z` (`prev/`), whose audit found all 29 units faithful.

| Merged | What it is | Changes what a document can say? |
|---|---|---|
| `lean-first/b14a` (lf-14a) | the `definitions@0` sugar (`no`, `every ... that is`, `iff`, `define`) is parsed by Lean; the retained Python reader is deleted; parse responses are typed and diagnostic spans bound | No (the same sugar, read by another owner; the translation uses none of it) |
| `question-answering/q2` (qa-q2) | `ve ask` answers without `--reading` (Lean's checked answer, `no_answer` where no reading exists); Lean-owned `words` mode wording situations, filled gaps and pair sentences | No for documents; it changes how questions are answered and how model situations are worded |
| `fix/abbrev` | test-only repair (git abbreviation length in the RD-8 evidence test) | No |
| `infra/tarch-b1`, `infra/layer-research`, `infra/map-version-notice` | test architecture, heavy-test selection, layer research and map notices | No |

Checked with `git diff ve-green-lf-14b..ve-green-fix-abbrev --stat -- ve lean rust conformance`: 80 files (the Lean `Ask` and `Words` modules, their response shapes and relays, the surface and parse-diagnostic changes, norm-defaults wording moved to Lean, generated manifests). No grammar production, profile or lexicon entry that a norm, guard or reading set of the constitution could use was added. Result: **no unit is newly expressible by a feature** (units upgraded by features: 0; reading sets upgraded by features: 0).

## What the measurement shows
* **The translation is unchanged**: `nd.py all` at this tag rebuilds `translation.ve.md` byte for byte; `ve document check` passes (premises model, superposed route, all 16 choices CONFLICT-FREE); coverage is 100% of bytes accounted, residual 50 open terms, 4 unresolved reading sets.
* **Unspecified probe**: 49 points, byte-identical to the previous run's file; the four AT-0p kinds are SETTLED no, SETTLED no, UNDECIDED, UNDECIDED for all seven rules.
* **Conclusion queries on the hard constraints**: u0165.s02 to s07 knowing and belief are ALL with certificates (12 of 12); u0165.s01 knowing and belief and every "neither" query are UNKNOWN, as before (the "neither" queries are meant not to be entailed).
* **Carried probes**: risk, s1, senses, senses_document, discourse and rights are byte-identical to the previous run's. The denial and claim-to-be-human conclusions are ALL. The companion probe differs only in its document paths.
* **`ve ask`**: none of the five questions is read; the only difference from the previous run is the field `answer`: `not_built` became `no_answer`. Without `--reading` Q2's answer is `no_answer` for all five.
* **Time**: one run each on a machine at load average 30 to 70, not a controlled comparison (`metrics.json: timing_single_runs`). The Lean build of this worktree took about 26 minutes (all 931 jobs) although the copied build was of the identical commit.

## Missing features, ledger tally (`UNFORMALISED`)
norms 669, quantities 119, `other:discourse` 81, causation 76, defaults 50, counting 31, modality/belief 25, attribution 12, time 9, `other:open-list` 1, `other:graded-force` 1 (unchanged). Gaps recorded in earlier runs stay: `other:english-nested-guard`, `other:scope`.
Next, in order of unlock: typed modals and belief; graded quantities; a scope construct for lead-ins, bold labels and narrowing sentences (352 units, 29.9% of the text); an English round trip for nested guards.
