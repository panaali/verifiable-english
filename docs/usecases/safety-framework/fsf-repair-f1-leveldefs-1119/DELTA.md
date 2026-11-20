# fsf-repair-f1-leveldefs-1119 DELTA

No user-visible change of VE. This item changes no product code under `ve/`, `lean/` or `rust/`, and no gate, test
selection or tool logic: the one line under `tools/` is a `tools/gate-optional.json` row that allows the new
pinned-source test's skip on a machine without the stored source, with the same reason as the four FSF rows already
there. VE's diagnostics, fault order, fields, verdicts, availability and CPU stay as they are on main at e53db4e8fc (the rebase base).
The changes are to one use case's vocabulary legend and facts (`usecases/safety-framework/vocabulary.py`, the new
predicate `defined`; `facts.d1.ve`, one fact per level in the `levels-*` blocks) and to the recorded outputs that hash
them, which REPORT.md lists. No verdict in `results.json` changes: `premises` goes from 35 to 42 and two
`certificate_sha256` values move. This follows the fsf-r1 precedent (docs/usecases/safety-framework/fsf-r1/DELTA.md).
No standing ruling is needed, and no row is reserved for the DRI.
