# fsf-repair-f9-mcca-1119 DELTA

No user-visible change of VE. This item changes no product code: nothing under `ve/`, `lean/`, `rust/` or `tools/`
changes. VE's diagnostics, fault order, fields, verdicts, availability and CPU stay as they are on main at f5553bc894.
The changes are to one use case's two vocabulary legends (`usecases/safety-framework/vocabulary.py`: `assessed`,
`change_assessed`) and to the recorded outputs that hash them (`environment.d1.json`, `coverage.json`,
`tests/data/route-cases.jsonl`, `conformance/english-lean/lexicon-report.json`). `results.json` is unchanged (every
verdict and every hash in it), as REPORT.md records. This follows the fsf-r1 and fsf-repair-f5-lowrisk-1119 precedent.
No standing ruling is needed, and no row is reserved for the DRI.
