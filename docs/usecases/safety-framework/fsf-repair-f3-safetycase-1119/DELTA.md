# fsf-repair-f3-safetycase-1119 DELTA

No user-visible change of VE. This item changes no product code of VE: nothing under `ve/`, `lean/`, `rust/` or
`tools/` changes, so VE's diagnostics, fault order, fields, verdicts, availability and CPU are as on main at
d8758ce968. The change is one use case's vocabulary legend
(`usecases/safety-framework/vocabulary.py`, `governance_found_acceptable_with_safety_case_where_ccl_reached`) plus
the recorded outputs that hash it, which REPORT.md lists. Every verdict in `results.json` is unchanged; only two
`certificate_sha256` values move. This follows the fsf-r1 precedent (docs/usecases/safety-framework/fsf-r1/DELTA.md).
No standing ruling is needed, and no row is reserved for the DRI.
