# Run 20261005T1800Z: Claude constitution pilot at `ve-green-english-lean-s2`

Read `SUMMARY.md` first (8 lines), then `AUDIT-REPAIR.md` and `FEATURE-REVIEW.md`. `*-prev-20261005T0600Z.md` is the previous run's.

| File | What it is |
|---|---|
| `translation.ve.md` | the main document, unchanged from run 20261005T0600Z (`documents@1`, `norms@0`, `norm-defaults@0`, `relational-fol@0`): the whole 184,893-byte source, every byte in a unit; 9 reading sets without content; every completion `unspecified` |
| `readings/all-strict.ve.md` | the strict companion (reading sets resolved to their strict or narrow-limit reading), unchanged |
| `readings/s1.ve.md`, `readings/all-default.ve.md` | **demonstrations only, not part of the translation and not counted in any claim** (they complete duties with `deny`, which the source does not state). `s1.ve.md` is what composition S2a runs on: its check now carries verdicts across readings (`readings/check-s1.json`, metrics `s2a`) |
| `units.json` | the ledger, 1,132 entries, identical to the previous run's |
| `metrics.json` | bytes accounted, unit counts by status (new and aggregated to the 299 older boundaries), audit-verified bytes, open terms, reading sets, missing-feature tally, check verdicts, the `s2a` block, probes |
| `rendered.md`, `readings/rendered-*.md`, `check.json`, `coverage.json`, `readings/check-*.json`, `readings/coverage-s1.json` | `ve document render` / `check` / `coverage` output at this tag |
| `probes/` | `unspecified-probe.json`, `s1-probe.json` (changed), `risk-probe.json`, `discourse-probe.json`, `rights-reading-probe.json`; `probes/s2/` is new: conclusion queries across and under readings of `u0125.s04.p2` |
| `AUDIT-*-received.md` | the audits received; `AUDIT-20261005T0600Z-received.md` (20/20) is the latest |
| `build.py`, `spec*.py`, `s1.py`, `s1_operators.py`, `probe_*.py`, `finish_0600.py` | the previous run's scripts, kept because the probes and `finish.py` import them (`finish_0600.py` is the previous `finish.py`, not run); `finish.py` is this run's |
| `prev/`, `base/` | the previous run's translation, ledger, metrics and companions (the starting point); the base translation `probe_discourse.py` starts from |

Reproduce (repository root, `lake build` in `lean/` and `python3 tools/rust_build.py` done):

    export PATH=~/.elan/bin:$PATH VE_NATIVE_PREBUILT=1
    R=usecases/claude-constitution-pilot/run-20261005T1800Z
    cp $R/prev/translation.ve.md $R/prev/units.json $R/prev/metrics.json $R/
    uv run python $R/s1.py                      # about 6 min; rebuilds readings/s1.ve.md (byte-identical) and its check
    for p in unspecified s1 risk discourse rights; do uv run python $R/probe_$p.py; done
    # probes/s2: ve document readings $R/readings/s1.ve.md --conclusion $R/probes/s2/conclusion-no-denial.json [--under force-u0125-s04-p2:0|1]
    uv run python $R/finish.py                  # about 17 min

`finish.py` asserts that every byte is in exactly one unit, that the ledger, the main document and the three companions equal the previous run's, that `ve document check` of the main, strict and default documents gives the previous output, and that the audit-verified bytes are the previous run's plus the five units the latest audit accepted.
