# UDHR pilot

`source/udhr.md` is the pinned text (SHA-256 and fetch date in `source/SOURCE.md`); it is never edited.
Each `run-<UTC stamp>/` holds one translation:

- `translation.ve.md` — the main document (rights@0 and soft-norms@0), 100% span accounting;
- `readings/` — companion documents for norm reading candidates; `*.ve.md` with `norm-defaults@0` in their profiles leave the completion unspecified;
- `units.json`, `metrics.json`, `witnesses.json`, `rendered.md`, `readings-rendered.md`, `SUMMARY.md`, and (once written by the auditor) `AUDIT.md`;
- `build.py` rebuilds everything from `prev/` (the 2026-09-29 translation) without model calls: run it from a Python with `lark` installed, with `PYTHONPATH` set to the repository root and `PATH=~/.elan/bin:$PATH`.
