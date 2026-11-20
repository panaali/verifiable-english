# fsf-repair-f6-sl2plus-1119 DELTA

No user-visible change of VE. This item changes no product code: nothing under `ve/`, `lean/`, `rust/` or `tools/`
changes. VE's diagnostics, fault order, fields, verdicts, availability and CPU stay as they are on main at f5553bc894
(the synced base; the work started at d8758ce968).
The changes are to one use case's vocabulary legend (`usecases/safety-framework/vocabulary.py`, `recommends`) and to
the recorded outputs that hash it, which REPORT.md lists. Every verdict in `results.json` is unchanged (only two
`certificate_sha256` values move). This follows the fsf-r1 and fsf-repair-f5-lowrisk-1119 precedent
(docs/usecases/safety-framework/fsf-r1/DELTA.md). No standing ruling is needed, and no row is reserved for the DRI.
