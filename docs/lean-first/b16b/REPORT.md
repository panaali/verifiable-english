# Lean-first batch 16b: report

Branch `lean-first/b16b`, base `8350e55f`. DELTA.md has the generated numbers, the deviation, the retained-path
table and the items needing the DRI; LEDGER.md has the decision map. Every number here comes from `evidence/`
and is checked by `tests/test_b16b_evidence.py`.

## What changed

- **Switch.** `load_document`, `check_document`, `coverage` and `render_document` ask Lean's `document` mode first
  for every `ve-document@1` text (`ve/document.py` `_lean_answer`, `_lean_document`; `ve/backends/relay.py`
  `answer`). Lean's rejection is final and verbatim; its acceptance is bound to the request (source, unit ids,
  order, parents, content presence) and the document is built from it, with Lean's statuses, coverage, checked
  content, meaning ids and document and source ids. Python's loader runs only for the mode's `CheckerUnavailable`
  and `ResourceLimit` rows and for texts that are not UTF-8; a failure of the service is raised.
- **Lean.** Unit `content` and `meaning_id` in the row, an `"admit": false` case for `load_document`, and two 16a
  bugs the switch exposed (a `senses` document was rejected; a definitions graph skipped the route's deferral).
- **Gate tooling.** A `document` corpus for `tools/lean_first_diff.py` (every document seed and 1,800 frozen
  fuzzer mutants), since none of the existing corpora had documents the mode owns.

## Lines

See the generated block of DELTA.md: Python under `ve/` has 43 lines deleted and Lean 292 lines added across the
captured commits. **The planned ~900-line deletion is not done** (DELTA.md, *Deviation*): Lean
decides 2 of the 393 pilot documents, so Python's wrapper is still reached by almost every real document, through
profiles 16a's mode refuses. A batch 16c that composes those routes, starting with `null` in the front matter, is
proposed there.

## Gate 5.1

1. **Suite.** `tools/gate.py` at `9003f240` in a clean worktree: passed, 12,647 passed, 90 allowed skips, 0 failed of 12,738 collected; Lean build and audit passed; Rust 37 passed (`evidence/suite.json`). Only this report and its evidence follow that commit.
2. **Corpus A/B.** 0 unlisted differences over all nine corpora; the listed ones are the environment, formula
   and admission decoders' texts and codes, which Lean now supplies for the documents it owns (DF-3 and DF-9,
   batches 12b and 13b), and pilot harness artifacts. This is the signed capture at `9a9a02ce`; the later
   diagnostic corrections are covered by the saved-case regressions in the final gate. No acceptance changed.
3. **Ledger.** LEDGER.md.
4. **Latency.** Within the absolute budgets; the DRI signed the new Lean CPU over the 20% rule on 2026-10-08.

The fuzzer's baseline does not grow (CI 0 new; 14 date seeds, 0 head-only signatures).

## Seeded faults

Nine faults, one per claimed behaviour, applied one at a time by `mutants.py`, each failing its named test, then
restored (the two Lean faults rebuilt and pinned for the run, the original build's hash checked afterwards):
`evidence/mutants.json`.

| Fault | Behaviour | Test that failed |
|---|---|---|
| `rejection_falls_back` | Lean's rejection is final | `test_lean_rejections_are_raised_verbatim` |
| `service_failure_falls_back` | a service failure is never answered by Python | `test_a_service_failure_is_never_answered_by_python` |
| `unbound_answer` | the answer is bound to the request | `test_answers_not_bound_to_the_request_are_unavailable` |
| `python_coverage` | coverage is Lean's | `test_coverage_and_statuses_are_leans` |
| `python_document_id` | identities are Lean's | `test_identities_and_content_are_leans` |
| `load_admits` | `load_document` does not admit the graph | `test_load_does_not_admit_the_graph_and_check_does` |
| `admission_disagreement_kept` | an admission route rejecting what Lean admitted is unavailable | `test_the_admission_route_rejecting_what_lean_admitted_is_unavailable` |
| `lean_senses_guard_removed` | a senses document takes the retained path (Lean) | `test_undecided_answers_take_the_retained_path[a document with senses …]` |
| `lean_admission_bypasses_route` | the graph is admitted through the route's own case (Lean) | `test_definitions_graph_is_deferred_as_the_admission_route_defers_it` |

The evidence test was also checked to fail on planted evidence faults (an unlisted A/B difference, an uncaught
mutant, a changed prose number), each restored.

## Review fix: response binding

Commit `1e1acf48` closes the review's untrusted-answer finding. The receiver now compares every authored unit
field and span, checks coverage byte tables and residual arithmetic, binds alternatives cells to unit IDs and
supports, and verifies source, document and meaning IDs. Genuine Lean rows still provide the checked content,
statuses and report. The response-mutation regressions cover the reported changed span and zero
`accounted_bytes`, as well as nearby count, identity and cell mutations. A forged residual line with a balanced
total is now rejected on both document entry points for plain and alternatives documents.

## Review fix: diagnostic parity and pending paths

Commit `456980eb` preserves Python's frozen-envelope diagnostic when a plain document has an unrecognised
language string. The saved order cases now agree on code and text in `test_signed_order_diagnostics_keep_python_names_and_specificity`;
the field-set regression also covers missing keys and Unicode language mutations. Commit `1648a5f4` records
all 166 signed verdict rows as `path pending lf-12` and runs an xfail-strict check over their 83 distinct cases.

## Acceptance items

- **AGENT, done:** the switch, the Lean changes, the binding checks, the corpus A/B with its signed list, the fuzz
  runs, the latency record, the seeded faults, the full suite in a clean worktree.
- **AGENT, not done:** the planned deletion (blocked, DELTA.md); `tools/relay_lint.py` does not cover
  `ve/document.py`, whose retained path still raises Python's diagnostics.
- **HUMAN (DRI), signed 2026-10-08:** wording and order where names, location and specificity are kept; four
  unavailable pilot records; new Lean CPU; and the deletion's move to 16c. The 166 verdict records are signed
  only as `path pending lf-12`, with a strict xfail for every distinct saved case.
- **EXTERNAL:** none.

Not run: the UDHR readings budget row (no readings change) and the agent-policy and eligibility harnesses (they
check no `ve-document@1` file through `check_document`).
