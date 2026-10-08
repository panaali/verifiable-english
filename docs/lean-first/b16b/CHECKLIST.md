# Batch 16b against the build checklist

| # | Line | 16b |
|---|---|---|
| 1 | one contract | Diagnostics come from Lean's mode verbatim; no text is copied into Python. The retained reasons are matched by code (`CheckerUnavailable`, `ResourceLimit`), not by text. |
| 2 | differential fuzz | `tools/difffuzz.py` CI and 14 date seeds at base and head (`evidence/difffuzz.json`); the `document` surface compares the mode with Python's retained path. |
| 3 | normalisation | Unchanged: the mode's reader is 16a's; the fuzz mutants include NBSP, tabs, `\r`, curly quotes and dotted I. |
| 4 | untrusted output | The generated response schema checks shape; `ve.document._bind_document_answer` checks authored unit fields, byte spans, coverage counts and residual totals against the request, and `_lean_document` checks source, document and meaning identities. `test_answers_not_bound_to_the_request_are_unavailable`, `test_identities_and_content_are_leans` and `test_alternatives_coverage_is_bound_to_units_and_counts` mutate those fields. |
| 5 | malformed input | 1,800 fuzz mutants through `check_document` and `render_document` in the A/B: only `VEError` or `CheckerUnavailable` escapes. |
| 6 | three-valued verdicts | An undecided row never becomes a verdict: it takes the retained path; a service failure is raised (`test_a_service_failure_is_never_answered_by_python`). |
| 7 | deadlines | The mode's deadline is the service's (`DEADLINES["document"]`); no new budget. |
| 9 | English | Not applicable (fenced English is a retained reason). |
| 10 | entry points | `check_document`, `load_document`, `coverage`, `render_document` and the CLI all go through `_load`; `test_the_cli_and_the_api_give_the_same_answer`. |
| 11 | no regex of a real language | None added. |
| 13 | tests can fail | Nine seeded faults (`evidence/mutants.json`); planted evidence faults fail `tests/test_b16b_evidence.py`. |
| 14 | hermetic | Tests write under `tmp_path`; the mutant runner uses `tools/nested_pytest`. |
| 16 | lists covered | The retained reasons the tests drive must be rows of DELTA.md; the new tests are in `tools/gate-collection.json`. |
| 17 | spec | `tools/lean_statements.py`: no statement added, removed or changed. |
| 20 | reports from evidence | `report.py` regenerates DELTA.md's block; `tests/test_b16b_evidence.py` checks it and the prose numbers. |
| 21 | AGENT/HUMAN/EXTERNAL | REPORT.md, *Acceptance items*. |
| 22 | hand-off | Full gate at `d1e2e234` in a clean worktree (`evidence/suite.json`); everything committed. |
