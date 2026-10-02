# Run 20261002T0620Z: Claude constitution pilot at `ve-green-unspecified-uc`

Read `SUMMARY.md` first (9 lines), then `AUDIT-REPAIR.md`, `FEATURE-REVIEW.md`, `SELF-REVIEW.md`.

| File | What it is |
|---|---|
| `translation.ve.md` | the main document (`documents@1`, `norms@0`, `norm-defaults@0`, `relational-fol@0`): the whole 184,893-byte source, every byte in a unit |
| `readings/all-strict.ve.md` | same environment; every reading set resolved to its strict (or permission, narrow-scope) reading, so those rules are elaborated and checked |
| `readings/all-default.ve.md` | `soft-norms@0` document: the defeasible reading of the force-ambiguous units and `u0073.s05` (needs deny completions: `norm-defaults@0` cannot join `soft-norms@0`) |
| `units.json` | the ledger: one entry per unit (1,132) with status CHECKED / LABELLED / OPEN / READINGS / UNFORMALISED, the blocking feature, notes, readings, English |
| `metrics.json` | bytes accounted, unit counts by status (at the new units and aggregated to the 299 older boundaries), audit-verified bytes, open terms, reading sets, missing-feature tally, check verdicts, probes |
| `rendered.md` | the main document in natural English, reading sets expanded, hard constraints annotated with VE's verdicts |
| `check.json`, `coverage.json`, `readings/check-all-*.json` | `ve document check` / `coverage` output |
| `probes/unspecified-probe.json` | VE's statuses (SETTLED / UNDECIDED / CONFLICT) on small situations; `probes/{risk,discourse,rights}-*.json` are carried from the previous run |
| `spec.py`, `spec_nd.py`, `build.py`, `probe_unspecified.py`, `finish.py` | the hand-authored content and the scripts that build and measure it |
| `prev/`, `prev1001/` | the base translation and ledger the build starts from; the previous run's translation, ledger and metrics (for comparison) |

Reproduce (from the repository root, `lake build` done in `lean/`):

    export PATH=~/.elan/bin:$PATH
    uv run python usecases/claude-constitution-pilot/run-20261002T0620Z/build.py
    uv run python usecases/claude-constitution-pilot/run-20261002T0620Z/probe_unspecified.py
    uv run python usecases/claude-constitution-pilot/run-20261002T0620Z/finish.py

`finish.py` asserts that every byte is in exactly one unit, that the ledger and the main document tile the same spans, and that the document coverage
by status equals the ledger's. The source is `../source/claude-constitution.md` (SHA-256 `fa10ed48…50dd`), never edited.
