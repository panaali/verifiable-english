# Run 20261007T1800Z: Claude constitution pilot at `ve-green-readings-defaults`

Read `SUMMARY.md` first, then `FEATURE-REVIEW.md` and `AUDIT-REPAIR.md`. `*-prev-20261006T1800Z.md` are the previous run's.

| File | What it is |
|---|---|
| `translation.ve.md`, `units.json` | the main document and ledger, byte-identical to run 20261006T1800Z (1,132 units, every byte of the 184,893-byte source in exactly one) |
| `readings/` | the strict companion, and the demonstration companions `s1.ve.md` and `all-default.ve.md` (not part of the translation; they complete duties with `deny`); `check-*.json`, `rendered-*.md`, `coverage-s1.json` re-run at this tag (only `check-s1.json` and `rendered-s1.md` differ from the previous run's, in wording) |
| `metrics.json` | bytes accounted, unit counts by status (new units and aggregated to the 299 old boundaries), claimed and audit-verified bytes, open terms, reading sets, missing-feature tally, check verdicts, `s2a`, `readings_defaults_probe`, `lean_decided_share`, `senses_probe`, profile probe |
| `rendered.md`, `rendered-raw.md`, `check.json`, `coverage.json` | the pilot's expanded rendering (reading sets spelled out), the raw `ve document render`, `ve document check` and `coverage` of the main document |
| `probes/` | unspecified, s1, risk, discourse, rights, senses probes (identical to the previous run's), `s2/` (conclusions across and under readings), `lean-decided-share-*.txt` (new), `out-*-now.txt` (this run's console output) |
| `AUDIT-*-received.md` | the audits received; `AUDIT-20261006T1800Z-received.md` (20/20) is the latest |
| `finish.py`, `probe_*.py`, `build.py`, `spec*.py`, `s1*.py`, `finish_0600.py`, `finish_2026100*.py` | scripts; `finish.py` is this run's, the others are earlier runs' kept because they import each other |
| `prev/`, `base/` | the starting point (previous translation, ledger, metrics) |

Reproduce (repository root; `lake build` in `lean/` and `python3 tools/rust_build.py` done):

    export PATH=~/.elan/bin:$PATH VE_NATIVE_PREBUILT=1
    R=usecases/claude-constitution-pilot/run-20261007T1800Z
    for p in unspecified s1 risk discourse rights senses; do uv run python $R/probe_$p.py; done
    uv run python -m ve document check $R/readings/s1.ve.md > $R/readings/check-s1.json    # about 5.3 min
    uv run python -m ve document coverage $R/readings/s1.ve.md > $R/readings/coverage-s1.json
    # probes/s2: ve document readings $R/readings/s1.ve.md --conclusion $R/probes/s2/conclusion-no-denial.json [--under force-u0125-s04-p2:0|1]
    uv run python tools/lean_decided_share.py $R/translation.ve.md > $R/probes/lean-decided-share-main.txt
    uv run python $R/finish.py                  # about 2.5 min
