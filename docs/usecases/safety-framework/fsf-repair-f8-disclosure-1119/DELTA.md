# fsf-repair-f8-disclosure-1119 DELTA

No user-visible change of VE. This item changes no product code: nothing under `ve/`, `lean/`, `rust/` or `tools/`
changes (`git diff --name-only d8758ce968...HEAD`, REPORT.md "Files"). VE's diagnostics, fault order, fields,
verdicts, availability and CPU stay as they are on main at d8758ce968. The changes are three legends in one use case's
vocabulary (`usecases/safety-framework/vocabulary.py`: `shared`, `yearly_review`, `frequent_review`) and the
recorded outputs that hash them, which REPORT.md lists. `results.json` does not change. This follows the fsf-r1 and
fsf-repair-f5-lowrisk-1119 precedent. No row needs a standing ruling, and no row is reserved for the DRI.
