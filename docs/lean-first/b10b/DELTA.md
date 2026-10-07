# Lean-first batch 10b: norm-defaults switch

Base: `7345e3ed`. The trace-fuzzer baseline replay repair was committed first
(`c564a163`), before any switch evidence was used. The Python norm-defaults
implementation is pinned at `9160d326` as a test-only oracle; product admission,
elaboration, report, grounding, residual and identities now read Lean's answers.

## 5.1 gate

| Item | Owner | Evidence |
|---|---|---|
| Full suite on clean HEAD | AGENT | Final gate JSON and status to be filled after the last commit. |
| Conformance A/B | AGENT | `tools/lean_first_diff.py compare`: probe and conformance 58,482 same; norm-defaults profile 2,020 same; readings, discourse, rights and quantity 35,713 same; 294 historical pilots same. No unavailable or unlisted records. Raw recordings and comparator JSON are under `/tmp/lf10b-*`. |
| Differential fuzzer | AGENT | CI sample and baseline replay tests pass. Fourteen date seeds on final HEAD pending. Baseline file is unchanged. |
| Deletion and owner map | AGENT | Below; `tools/relay_lint.py` passes. |
| Latency | AGENT | Same-corpus base/head measurement pending. |
| Wording, order, verdict or availability change | HUMAN (DRI) | None in the completed A/B recordings; no signature required if final recordings remain identical. |
| External check | EXTERNAL | None in this batch. |

## Deletion ledger

| Deleted Python decision | Lean owner |
|---|---|
| `norm_defaults.py`: fill, unspecified predicate selection, guards, generated layers, statuses, conflict, reached, report and residual | `VE.NormDefaults.Wire` and `VE.NormDefaults.Report` through the `norm-defaults` service route. |
| `norm_defaults.py`: environment, fill and document identities | `NormDefaults.Run` elaboration row, checked by the relay container. |
| `norm_defaults_route.py`: Python regeneration comparison and W1 admission checks | `NormDefaults.Run` and `NormDefaults.Admission`; `admit_norm_defaults_document` relays the Lean admission row. |
| `document.py`: gaps and grounding folds | Lean `norm-defaults-report` row. |

The frozen Python oracle is loaded from Git history in `conformance/` for
pre-deletion differential tests. It supplies no product verdict. The existing
soft and rights document wrapper refusal has the same public result on base
and head; those layered routes remain exercised by the frozen oracle and Lean
route tests.

## Build-checklist disposition

| Lines | Owner | Check or scope |
|---|---|---|
| 1-2 | AGENT | Generated wire and route schemas; genuine difffuzz CI and fourteen seeds. |
| 3 | AGENT | Existing text-normalisation and wire fixtures in the full gate. |
| 4-5 | AGENT | Producer response schema, route decoder tests and malformed-input suite. |
| 6-7 | AGENT | Lean statuses and budget/deadline tests in the full gate. |
| 8-9 | AGENT | Existing kind/owner and English tests; this batch changes no English parser. |
| 10 | AGENT | Document and admission callers relay; A/B tests compare public entry points. |
| 11 | AGENT | Lean parses its own source; no new regex language parser. |
| 12 | AGENT | No state-machine or ledger code changed; full gate remains the regression check. |
| 13 | AGENT | Three seeded failures, then restored tests, recorded below. |
| 14-16 | AGENT | Hermetic full gate, Lean-owned identities, registered profile corpus. |
| 17-18 | AGENT | Statement diff and audit; no theorem statement changes. No new spec-stage theorem. |
| 19 | AGENT | No use-case rule or answer key changed; pilot A/B covers historical documents. |
| 20 | AGENT | Evidence numbers verified from JSON by `verify_report.py`. |
| 21 | AGENT / HUMAN / EXTERNAL | Acceptance items above tagged; no DRI or external item needs action when A/B is identical. |
| 22 | AGENT | Final clean HEAD gate, disk check, local commits and this report. |

DRI rulings used: [x] answer 7, pinned frozen oracle
(`tests/test_norm_defaults_differential.py`); [x] answer 9, batch order
(`tests/test_norm_defaults_switch.py`); [x] throughput rule, no growing
difffuzz baseline (`tests/test_difffuzz.py::test_ci_run`). No theorem statement
changed and no wording/order/verdict/availability ruling is sought.

## Seeded bugs

1. Baseline replay answer hash replaced with an empty update in
   `trace_fuzzer.py`; `test_fuzzer_gate_detects_changed_baseline_replay_answer`
   failed. The mutation was removed.
2. Admission relay forced `admitted: false` in `norm_defaults_route.py`;
   `test_document_graph_admits_the_layer_of_fill_u` failed (`False is True`).
   The mutation was removed.
3. Report relay forced `translation: false` in `norm_defaults.py`;
   `test_document_reports_the_leans_grounding_and_gap` failed because
   `UngroundedDefault` disappeared. The mutation was removed. All three
   focused tests then passed on restored code.
