# defs-repair-bluedot-grant-1119 DELTA

No user-visible change of VE. This item changes no product code of VE: nothing under `ve/`, `lean/`, `rust/` or
`tools/` changes, so VE's diagnostics, fault order, fields, verdicts, availability and CPU stay as they are on main
at f5553bc894. The changes are to one use case's legends (six constant descriptions authored in
`usecases/bluedot-grant/semantic_readings.py`) and to the files generated from them (`document.ve.md`,
`causal.ve.md` by the document's `build_document.py`; `conformance/english-lean/corpus-seal.json` by
`conformance.english_lean_seal`). The two documents' `check_document` answers are identical on base and head
apart from the identity digests the legends feed (`document_id`; on causal.ve.md also `report_id` and
`core_report_id`), as `ab-answers.json` records. This follows the fsf-repair-f9-mcca-1119 precedent. No standing
ruling is needed, and no row is reserved for the DRI.
