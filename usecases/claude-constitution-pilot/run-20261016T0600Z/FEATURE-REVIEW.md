# Feature review: what `ve-green-premise-scale` adds over `ve-green-fix-abbrev`

Source: the pinned 184,893-byte constitution, unchanged (`../source/SOURCE.md`, SHA-256 `fa10ed48…50dd`). Start: the translation of run `20261015T1800Z` (`prev/`), whose audit found all 25 audited units faithful.

| Merged | What it is | Changes what a document can say? |
|---|---|---|
| `infra/premise-scale` (premise-scale) | the premise-consistency check gets Lean's per-sort domain budget (a sort the premises force to hold 3 to 8 distinct things is searched at that size, service mode `search-budget`), a route that takes ground stated facts as their own model, a Rust timeout read as "no witness" (Lean's replay then answers), and a Rust model-search limit scaled by the case's measured cost (at least 5 s) | No (more documents get a Lean-checked answer instead of UNKNOWN; no construct is added) |
| `lean-first/b14c` (lf-14c) | n-ary and mixed-arity `definitions@0` are elaborated by Lean | No (the translation uses no definitions sugar) |
| `fix/x86-cpu-deadline` | a Lean service request is charged its user CPU only | No |
| `infra/arch-AR-2`, `arch-AR-4`, `tarch-b8`, `test-tail` | relay typing of parse diagnostics and graph formulas, test architecture, tail tests | No |

Checked with `git diff ve-green-fix-abbrev..ve-green-premise-scale --stat -- ve lean rust conformance`: 75 files (the Lean `SearchBudget` modules and their response shape, the Rust ground-fact route and scaled limit, the Layers/Preflight/Elaborate changes of lf-14c and the relay typing, process limits, generated manifests). No grammar production, profile or lexicon entry that a norm, guard or reading set of the constitution could use was added. Result: **no unit is newly expressible by a feature** (units upgraded by features: 0; reading sets upgraded by features: 0).

## What the measurement shows
* **The translation's meaning is unchanged**: `nd.py all` at this tag rebuilds the previous translation except for the six admission texts of the three "should" sets (repair below); body, units, vocabulary, graph, contents, meaning ids and situations are identical. `ve document check` passes (premises model, superposed route, all 16 choices CONFLICT-FREE); coverage is 100% of bytes accounted, residual 50 open terms, 4 unresolved reading sets.
* **Unspecified probe**: byte-identical to the previous run's file; the four AT-0p kinds are SETTLED no, SETTLED no, UNDECIDED, UNDECIDED for all seven rules.
* **Conclusion queries on the hard constraints**: the same 12 ALL with certificates and 9 UNKNOWN (the seven "neither" queries by design, plus u0165.s01 knowing and belief). **New at this tag: all 21 answered on their first run at the default Rust limit, at load average 30 to 80** (the previous run: eight CheckerUnavailable at the fixed 5 s limit, two of them still unavailable until a capped run with VE_RUST_TIMEOUT=600). No capped run was needed, so there is no cap or peak resident set to record this time (DRI X2-X4 (3): the default limit was kept).
* **Carried probes**: risk, s1, senses, senses_document, discourse and rights are byte-identical to the previous run's; the denial and claim-to-be-human conclusions are ALL; the companion probe differs only in its document paths; the five `ve ask` questions are still not read (byte-identical answers, `no_answer`).
* **Time**: one run each, machine at load average 30 to 80, not a controlled comparison: `ve document check` 58 s (previous run 60 s), coverage 53 s (47 s). The Lean build of this worktree took 27 minutes (all 943 jobs) although the copied build was of the identical commit.
* **Premise-scale on this document**: the premises were already a Lean-checked model before (the constitution's constants stay one thing per sort), so the search budget raises no sort here; the pilot gains only the first-run answers above.

## Missing features, ledger tally (`UNFORMALISED`)
norms 669, quantities 119, `other:discourse` 81, causation 76, defaults 50, counting 31, modality/belief 25, attribution 12, time 9, `other:open-list` 1, `other:graded-force` 1 (unchanged). Gaps recorded in earlier runs stay: `other:english-nested-guard`, `other:scope`.
Next, in order of unlock: typed modals and belief; graded quantities; a scope construct for lead-ins, bold labels and narrowing sentences (352 units, 29.9% of the text); an English round trip for nested guards.
