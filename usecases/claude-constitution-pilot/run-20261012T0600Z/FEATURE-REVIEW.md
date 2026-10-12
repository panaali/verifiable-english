# Feature review: what `ve-green-devtime-1` adds over `ve-green-arch-AR-8`

Source: the pinned 184,893-byte constitution, unchanged (`../source/SOURCE.md`, SHA-256 `fa10ed48…50dd`). Start: the translation of run `20261011T1800Z` (`prev/`), whose audit found all 20 sampled units faithful. Four first-parent merges since `ve-green-arch-AR-8`.

| Merged | What it is | Changes what a document can say? |
|---|---|---|
| `infra/arch-AR-7` | architecture map re-measured, ADR 0001 tests, gate collection | No |
| `lean-first/b16d` (lf-16d) | the Lean `document` mode owns `norm-defaults@0` and `readings@1` documents (content, admission, pending readings, couplings, English fences, norm-defaults coverage); Python binds the typed answer | No (same documents, same answers) |
| `lean-first/b13b` (lf-13b) | typing, parsing, definitions, Background, bundles, norms, admission, graph, readings, premise status and compare default to Lean under every authority; Python FOL/norms admission deleted | No |
| `infra/devtime-1` | `AGENTS.md`, `tools/repo_map.py` (derived map of modes, tests, generators) | No |

Checked by reading the diffs of `ve/parser.py`, `ve/ast.py`, `lean/VE/Service/Document.lean` and the batch reports: the grammar, profiles and lexicon are not extended. Result: **no unit changes status because of a feature, and no unit is newly expressible.** I changed no unit and no product code, so `changed_units` is empty, claimed coverage does not move (2,951 bytes, 1.60%) and no seeded bug was needed (nothing in Lean, Python or Rust was changed).

## What the measurement shows
* **Same answers.** `ve document check` of the unchanged translation equals the previous run's output field for field (premises `model`, route `superposed`, 199 nodes, 69 predicates, 16 of 16 choices CONFLICT-FREE, the same English). `coverage` is identical (same bytes by status, residual 73). `ve document render` is byte-identical. `nd.py all` rebuilt the translation byte for byte from `translation-without-content.ve.md`; the separating situations are the same, found by Lean.
* **Conclusion queries.** Four byte-identical result files: denial across readings UNKNOWN, under the strict reading ALL, under the defeasible reading UNKNOWN, claim-to-be-human ALL, all on the superposed route. The two UNKNOWN answers still carry no English line.
* **Probes.** The seven carried probes re-run, all byte-identical; the companion probe and its four queries give the same result (19 decided units, 1.41%; the `source_word` defect remains: `CheckerUnavailable … KeyError`). `tools/lean_decided_share.py` on the translation itself: 0.00% (no `decided_units`). `ve ask --reading`: none of the five questions read, identical stderr.
* **Time.** One run each, not a controlled comparison (the previous figures come from the previous run's files; the machine may differ): `ve document check` 48.9 s (35 s last run); the readings separation run: load 9.0 s (6.5), check 52.5 s (42.1), separation search 59.9 s (55.2). b13b's own saved latency evidence records about 1.08× on udhr and eligibility.
* **Conflicts.** None reported by VE (CONFLICT-FREE in all 16 choices), so none to classify as a source conflict or a translation artefact.

## Missing features, ledger tally (`UNFORMALISED`)
norms 669, quantities 119, `other:discourse` 81, causation 76, defaults 50, counting 31, modality/belief 25, attribution 12, time 9, `other:open-list` 1, `other:graded-force` 1 (unchanged).
Next, in order of unlock: typed modals and authority (“cannot”, “can”, “may”, “unlocked by”); graded quantities (“serious uplift”, “vast majority”); context-sensitive defeasible obligations beside norm-defaults@0; decided units reported for documents without companion sets (and the `source_word` fix); English for a gated UNKNOWN on the superposed route.
