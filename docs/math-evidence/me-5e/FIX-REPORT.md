BLOCKED: F1 requires a central registry edit outside this worktree; the workspace approval settings rejected that write. No DRI signature is reserved.
HEAD before this report: `fafd10f02` (main was merged into the worktree during this fix). No push or model call was made.
Change: `FOLLOW-UPS-entry.md` contains the exact R16 ties-pass row for the central registry.
Open: append that row under `## me-5e` in `/home/seyran/code/manage-agents/FOLLOW-UPS.md`, then rerun the supplied F1 probe. This repository cannot make that external write.

## Finding

F1 -> proposed R16 registry row names `Shown.matches`, `Run.row`, `Run.rowJson`, `Check.runShown`, and `Derive.shown`, with the existing outcome, row, and encoder theorems to tie them to -> supplied F1 probe failed before the edit; the same probe passed against a temporary copy of the registry with the proposed row appended, while the central probe remains red -> this report's commit.

The probe cannot become a hermetic repository test: its required target is an external file outside this checkout. A test against the draft alone would not detect the missing central row. The supplied probe is the regression check to run after the protected path becomes writable.

## Validation

- `PATH=~/.elan/bin:$PATH lake build` passed (1,161 jobs). `lean-prep.sh` also ran after the concurrent main merge.
- `python3 lean/audit.py` initially failed because the merged tree's generated declarations were stale. It passed after `tools/regen_generated.py --write` refreshed the Lean inventories (668 sources, 7,433 named theorems). The generator then stopped at `binding-census`: a recorded 10,000-deep JSON request exceeds Python's parse recursion limit. Those unrelated generated edits were reverted; the audit does not pass on this final tree.
- The requested selected run first waited for occupied Mac slots, then failed in the VM fallback because uv's default cache was read-only. A local wrapper rerun with a writable uv cache completed 14 of 401 selected files: 13 passed, and `tests/test_assurance_manifest.py::test_spec_tables_are_generated_from_the_manifest` failed on a stale generated table after the main merge. It was interrupted after the F1 write boundary remained unresolved; no test process was left running. No full suite or release gate ran.
- The three pre-existing main failures listed in `main-known-red.txt` were not changed or targeted.
