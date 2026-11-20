# defs-repair-safety-framework-1119 DELTA

No user-visible change of VE. This item changes no product code: nothing under `ve/`, `lean/`, `rust/` or `tools/`
changes (`git diff --name-only 941208a12d...HEAD`, REPORT.md "Files"). VE's diagnostics, fault order, fields,
verdicts, availability and CPU stay as they are on main at 941208a12d.

The item changes 28 legends of one use case's vocabulary (`usecases/safety-framework/vocabulary.py`). No predicate
name, argument list, verbalisation, act, open term or decider changes. It also changes the recorded outputs that hash
those legends, which REPORT.md lists. In `results.json` only two `certificate_sha256` values move
(`/items/N1/goals/cyber` and `/items/N1/goals/harmful_manipulation`). No comparison or verdict path changes: the
REPORT shows the path-only diff, which printed no values. This follows the fsf-r1, fsf-repair-f1, -f6 and -f7
precedent (docs/usecases/safety-framework/fsf-repair-f6-sl2plus-1119/DELTA.md).

No row needs a standing ruling, and no row is reserved for the DRI.
