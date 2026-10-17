# Feature review: what `ve-green-trust-ties-rd9` adds over `ve-green-premise-scale`

Source: the pinned 184,893-byte constitution, unchanged (`../source/SOURCE.md`, SHA-256 `fa10ed48…50dd`). Start: the translation of run `20261016T0600Z` (`prev/`), whose audit found all 28 audited units faithful.

| Merged | What it is | Changes what a constitution unit can say? |
|---|---|---|
| `rd-9/integrate` (rd-9) | the soft chain: `readings@1` × `soft-norms@0` × `norm-defaults@0` (unspecified completion). Lean admits such a document, separates its readings on filled sides, checks each choice and the verdicts; per-pair `gaps` on separation lines; `decided_units` without companion sets; R14 candidate wording for conflicts | **Not yet through `ve document check`** (see below). Display: separation lines show the gap sentences their situation reads |
| `lean-first/b16e` (lf-16e) | Lean's `document` mode decides `rights@0` documents (with and without `readings@1`) and `readings@1` documents without `norm-defaults@0` | No: the constitution uses neither shape |
| `infra/trust-ties-rd9`, `fix/relay-mutation-gate` | trust-class ties; a relay mutation gate over every route | No |
| `infra/tarch-contract`, `tarch-leanshare`, `tarch-split`, `tarch-select`, `fix/ci-run-timeout`, `infra/ts-B3` | test architecture, test speed, CI timeouts | No |

Checked with `git diff ve-green-premise-scale..HEAD --stat -- ve lean rust conformance`: 68 files (rd-9's Lean soft-chain modules and response shapes, the readings and rights relays, `ve/document.py`, `ve/softnorms.py`, one 14-line change in `ve/surface/rights.py`). No grammar production, profile or lexicon entry that a norm, guard or reading set of the constitution could use was added. Result: **no unit is newly expressible by a feature** (units upgraded by features: 0; reading sets upgraded by features: 0).

## The soft chain on the constitution (`probe_soft_chain.py`, `evidence/soft-chain-probe.json`)

The native form of the three "should" sets (spec rd-9 plan 5.2, C1 to C4): the defeasible candidate is a default rule with `exception: {decided_by: unstated}` and `unless: []`, the three invented `exception_to_*` open terms are dropped, `soft-norms@0` is added to the profiles, and the situations are searched again.

| Step | Result |
|---|---|
| search for a separating situation per pair | every pair separated, checked by Lean (7 s) |
| load | admitted |
| `ve document coverage` / `render` | work; 47 open terms (50 with the workaround); 4 unresolved sets, 4 separations |
| `ve document readings` denial and claim-to-be-human queries | ALL with certificates in all 16 choices (route enumerated), as with the workaround (ALL, superposed) |
| `ve document check` | **fails**: an uncaught `UnsupportedProfile: norm-defaults@0 documents are checked through fill (ve.norm_defaults)` with a Python traceback, from `ve/document.py` `_report` → `ve/soft_route.py` `admit_soft_document(lower_env, …)` → the `soft-elaborate` service call. Reading the traceback: the claim-graph admission is asked of the Lean soft route with the lower environment `_lower_route(doc)` returns, which still lists norm-defaults@0 (only readings@1 is stripped). Not verified beyond the traceback |

The DRI signature in `docs/readings-defaults/rd9-lean/DELTA.md` makes the soft-completion availability conditional on the full gate on the final head, and `docs/rd-9/integration/FIX-REPORT.md` lists SC-8 (the document relay) as open, which fits. The plan keeps a repair only if `ve document check` passes, so **the translation keeps the workaround**. Two things the probe shows: the unnamed exception is representable with no translator-invented term; and a failing public command is a defect worth reporting (an uncaught error, not a refusal).

## Other measurements at this tag
* **The translation's meaning is unchanged**: `nd.py all` rebuilds the previous translation byte for byte; `ve document check` passes (premises model, superposed route, all 16 choices CONFLICT-FREE); coverage 100% of bytes accounted, residual 50 open terms, 4 unresolved reading sets.
* **Unspecified probe**: byte-identical; AT-0p's four kinds are SETTLED no, SETTLED no, UNDECIDED, UNDECIDED for all seven rules.
* **Carried probes**: risk, senses, senses_document, discourse and rights are byte-identical. The s1 probe differs in point (c) only: adding norm-defaults@0 to the S1 document (which has soft-norms@0) used to be refused by profile ("norm-defaults@0 documents on the soft and rights routes await the Lean route"); now the profile is not refused and the (unre-identified) document fails on its meaning ids. The profile-combination probe shows the same change for soft-norms@0 (now "checked through fill") and rights@0 (now the rights route's own refusal).
* **Separation lines** (SC-A): the lines of u0036.s05 and u0263.s04.p2 show 1 gap sentence each, 15 before (14 about other acts). u0156.s03 and u0165.s03 still say "These two readings differ in a checked situation that VE cannot yet show in words." (before and now).
* **Conclusion queries on the hard constraints**: the same 12 ALL with certificates and 9 UNKNOWN (the seven "neither" queries by design, plus u0165.s01 knowing and belief), all answered on the first run at the default Rust limit (three in parallel, 24 minutes). The denial and claim-to-be-human conclusions are ALL as before; the companion probe's queries are ALL; `ve ask` still reads none of five questions.
* **Time** (one run each, load average 9 to 30, not controlled): `ve document check` 56 s (58 s), coverage 47 s (53 s). The Lean build in this worktree ran all 957 jobs (17 min 50 s) although the copied build was of the identical commit.

## Missing features, ledger tally (`UNFORMALISED`)
norms 669, quantities 119, `other:discourse` 81, causation 76, defaults 50, counting 31, modality/belief 25, attribution 12, time 9, `other:open-list` 1, `other:graded-force` 1 (unchanged). Gaps recorded in earlier runs stay: `other:english-nested-guard` (all seven hard-constraint rules render but do not read back), `other:scope`.
Next, in order of unlock: the soft chain through `ve document check` (native defeasible "should": the `exception_to_*` terms go; the audit of 20261016T0600Z counted about 143 `norms` units that say "should"); typed modals and belief (know, intend, think "quite likely"; the same audit counted about 122 "we want/hope" units); graded quantities; a scope construct for lead-ins, bold labels and narrowing sentences (352 units, 29.9% of the text); an English round trip for nested guards.
