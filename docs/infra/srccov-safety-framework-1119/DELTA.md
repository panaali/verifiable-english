# srccov-safety-framework-1119 DELTA

No user-visible change of VE. This item changes no file under `ve/`, `lean/`, `rust/` or `tools/`
(`git diff --numstat 941208a12d HEAD`, REPORT.md "Files"). VE's diagnostics, fault order, fields, verdicts,
availability and CPU stay as they are on main at 941208a12d. The change is the text of 14 legends in one use case's
vocabulary (`usecases/safety-framework/vocabulary.py`), plus the recorded outputs that hash them, which REPORT.md
lists. In `results.json`, 2 `certificate_sha256` values change and no verdict moves (`git diff 941208a12d HEAD --
usecases/safety-framework/results.json`: 2 lines out, 2 in, both `certificate_sha256`). This follows the precedent of
fsf-repair-f8-disclosure-1119 and fsf-repair-f1-leveldefs-1119. No row needs a standing ruling, and no row is reserved
for the DRI.
