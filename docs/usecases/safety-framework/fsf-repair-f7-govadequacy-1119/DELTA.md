# fsf-repair-f7-govadequacy-1119 DELTA

No user-visible change of VE. This item changes no product code: nothing under `ve/`, `lean/`, `rust/` or `tools/`
changes. VE's diagnostics, fault order, fields, verdicts, availability and CPU stay as they are on main at d8758ce968.
The changes are to three legends of one use case's vocabulary (`usecases/safety-framework/vocabulary.py`:
`mitigates`, `governance_found_acceptable_with_safety_case_where_ccl_reached`, `acceptable`) and to the recorded
outputs that hash it, which REPORT.md lists. No predicate name, argument list, verbalisation, open term or decider
changes, and every verdict in `results.json` is unchanged (only two `certificate_sha256` values move; REPORT.md,
"Regenerated files"). This follows the fsf-r1 and fsf-repair-f5-lowrisk-1119 precedent. No standing ruling is needed,
and no row is reserved for the DRI.
