# Run 20261004T1800Z: Claude constitution pilot at `ve-green-layers2-b2`

Read `SUMMARY.md` first (9 lines), then `AUDIT-REPAIR.md`, `FEATURE-REVIEW.md`, `SELF-REVIEW.md`. The `*-prev-20261004T0600Z.md` and `AUDIT-REPAIR-20261004T0600Z.md` files are the previous run's.

| File | What it is |
|---|---|
| `translation.ve.md` | the main document (`documents@1`, `norms@0`, `norm-defaults@0`, `relational-fol@0`): the whole 184,893-byte source, every byte in a unit; 8 reading sets without content (`readings@1` content cannot join `norm-defaults@0`); every completion is `unspecified` |
| `readings/all-strict.ve.md` | same environment; every reading set resolved to its strict (or permission, narrow-scope) reading, so those rules are elaborated and checked; the probes read this document |
| `readings/s1.ve.md`, `readings/all-default.ve.md` | **demonstrations only, not part of the translation and not counted in any claim**: the soft chain (`soft-norms@0`, plus `readings@1` in `s1.ve.md`) completes duties and the operator permission with `deny`, which the source does not state (audit 20261003T0600Z); kept to show what `readings@1` does at this tag (9 sets, 16 pairs) |
| `units.json` | the ledger: one entry per unit (1,132) with status CHECKED / LABELLED / OPEN / READINGS / UNFORMALISED, the blocking feature, notes, readings, English; `s1_demonstration_only` holds the demonstration's Lean-checked pairs, flagged `claimed: false` |
| `metrics.json` | bytes accounted, unit counts by status (at the new units and aggregated to the 299 older boundaries), audit-verified bytes, open terms, reading sets, missing-feature tally, check verdicts, the `s1` block (demonstration), probes |
| `rendered.md`, `readings/rendered-*.md` | the main document and the companions in natural English (`ve document render`) |
| `check.json`, `coverage.json`, `readings/check-*.json`, `readings/coverage-s1.json` | `ve document check` / `coverage` output |
| `probes/` | `unspecified-probe.json` (34 points), `s1-probe.json`, `risk-probe.json`, `discourse-probe.json`, `rights-reading-probe.json` re-run at this tag |
| `spec.py`, `spec_nd.py`, `build.py`, `s1.py`, `s1_operators.py`, `probe_*.py`, `finish.py` | the hand-authored content and the scripts that build and measure it |
| `prev/`, `prev1001/`, `prev1004/` | the base translation the build starts from; the 20261001T1800Z ledger (audited lineage); the previous run (20261004T0600Z) translation, ledger, metrics, summary and strict companion |
| `AUDIT-*-received.md` | the audits received for earlier runs; `AUDIT-20261004T0600Z-received.md` is the one repaired here |

Reproduce (from the repository root; `lake build` in `lean/` and `python3 tools/rust_build.py` done):

    export PATH=~/.elan/bin:$PATH VE_NATIVE_PREBUILT=1
    R=usecases/claude-constitution-pilot/run-20261004T0600Z
    uv run python $R/build.py
    uv run python $R/probe_unspecified.py
    uv run python $R/s1.py
    uv run python $R/probe_s1.py
    uv run python $R/probe_risk.py; uv run python $R/probe_discourse.py; uv run python $R/probe_rights.py
    uv run python $R/finish.py

`build.py` reproduces the previous run's documents (byte for byte, checked at this tag before any edit) except for `u0123.s01.p1` (one reading with content, new `ops-one` item kind), and the ability candidates of the reading sets of `u0062.s01` and `u0123.s02.p1`. `finish.py` asserts that every byte is in exactly one unit, that the ledger and the main document tile the same spans, that the document coverage by status equals the ledger's, and that the audit-verified bytes are the previous run's plus the two units (`u0263.s04.p2`, `u0073.s05`) and the label unit (`u0001`) the last audit accepted.
The source is `../source/claude-constitution.md` (SHA-256 `fa10ed48…50dd`, copied from the orchestrator's pinned directory), never edited.
