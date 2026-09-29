# Claude constitution pilot

Translation of Anthropic's published constitution into `ve-document@1`, one run per language version.

* `source/` — the pinned text (`claude-constitution.md`, SHA-256 in `SOURCE.md`) and the raw fetch. Never edited.
* `run-20260929T1800Z/` — this run, language at `ve-green-flaky4`.
  * `translation.ve.md` — the main document (every source byte in a unit).
  * `readings/all-strict.ve.md`, `readings/all-default.ve.md` — the same document with every force reading resolved one way;
    they make the elaborated norm of each reading checkable (a norm reading set cannot carry content in the main document).
  * `units.json` — the unit ledger (status, missing feature, readings, open terms); `metrics.json`, `coverage.json`, `check.json`.
  * `rendered.md` — the natural-view rendering (open rules relabelled, reading sets expanded with their English).
  * `SUMMARY.md`, `AUDIT-REPAIR.md`, `FEATURE-REVIEW.md`, `SELF-REVIEW.md`.
  * `prev/` — the previous run's translation and ledger, the only inputs besides `spec.py`.

Reproduce (needs `lake build ve_soft_norms_route` once, about two minutes):

    export PATH=~/.elan/bin:$PATH
    (cd usecases/claude-constitution-pilot/run-20260929T1800Z && uv run --project ../../.. python build.py)
    uv run python usecases/claude-constitution-pilot/run-20260929T1800Z/finish.py
