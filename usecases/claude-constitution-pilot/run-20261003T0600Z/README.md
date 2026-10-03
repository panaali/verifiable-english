# Run 20261003T0600Z: Claude constitution pilot at `ve-green-wire-s4`

Read `SUMMARY.md` first (9 lines), then `FEATURE-REVIEW.md`, `AUDIT-REPAIR.md`, `SELF-REVIEW.md`.

| File | What it is |
|---|---|
| `translation.ve.md` | the main document (`documents@1`, `norms@0`, `norm-defaults@0`, `relational-fol@0`): the whole 184,893-byte source, every byte in a unit; 11 reading sets without content (readings@1 content cannot join `norm-defaults@0`) |
| `readings/s1.ve.md` | **new**: the S1 document (`documents@1`, `norms@0`, `soft-norms@0`, `readings@1`, `relational-fol@0`): ten reading sets with content (six "should" pairs, four operator "can" sets), 17 pairs, each with a situation Lean checks when the document loads |
| `readings/all-strict.ve.md` | same environment as the main document; every reading set resolved to its strict (or permission, narrow-scope) reading, so those rules are elaborated and checked |
| `readings/all-default.ve.md` | `soft-norms@0` document: the defeasible reading of the force-ambiguous units and `u0073.s05` (the starting point of `s1.ve.md`) |
| `units.json` | the ledger: one entry per unit (1,132) with status CHECKED / LABELLED / OPEN / READINGS / UNFORMALISED, the blocking feature, notes, readings, English; `s1` and `separating_situation` hold the Lean-checked pairs |
| `metrics.json` | bytes accounted, unit counts by status (at the new units and aggregated to the 299 older boundaries), audit-verified bytes, open terms, reading sets, missing-feature tally, check verdicts, the `s1` block, probes |
| `rendered.md`, `readings/rendered-s1.md` | the main document and the S1 document in natural English (`ve document render`); the S1 file shows each pair with its wording |
| `check.json`, `coverage.json`, `readings/check-*.json`, `readings/coverage-s1.json` | `ve document check` / `coverage` output |
| `probes/s1-probe.json` | what `readings@1` accepts and refuses beside `norm-defaults@0` (three cases, exact messages); `probes/unspecified-probe.json` (30 points); `probes/{risk,discourse,rights}-*.json` re-run at this tag (byte-identical) |
| `spec.py`, `spec_nd.py`, `build.py`, `s1.py`, `s1_operators.py`, `probe_*.py`, `finish.py` | the hand-authored content and the scripts that build and measure it |
| `prev/`, `prev1001/`, `prev1800/` | the base translation the build starts from; the 20261001T1800Z ledger (the audited lineage); the previous run's translation, ledger, metrics and summary |
| `AUDIT-*-received.md` | the audits received for earlier runs; `AUDIT-20261002T1800Z-received.md` is the one repaired here |

Reproduce (from the repository root; `lake build` in `lean/` and `python3 tools/rust_build.py` done):

    export PATH=~/.elan/bin:$PATH VE_NATIVE_PREBUILT=1
    R=usecases/claude-constitution-pilot/run-20261003T0600Z
    uv run python $R/build.py
    uv run python $R/s1.py
    uv run python $R/probe_unspecified.py
    uv run python $R/probe_s1.py
    uv run python $R/probe_risk.py; uv run python $R/probe_discourse.py; uv run python $R/probe_rights.py
    uv run python $R/finish.py

`build.py` reproduces the previous run's three documents byte for byte except for `u0168.s01`. `finish.py` asserts that every byte is in exactly one unit, that the ledger and the main document tile
the same spans, that the document coverage by status equals the ledger's, and that the audit-verified bytes are the previous run's minus the 96 bytes of `u0168.s01`.
The source is `../source/claude-constitution.md` (SHA-256 `fa10ed48…50dd`), never edited.
