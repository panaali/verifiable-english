# Run 20261008T1800Z: Claude constitution pilot at `ve-green-lf-15b`

Read `SUMMARY.md` first, then `FEATURE-REVIEW.md` and `AUDIT-REPAIR.md`. `*-prev-*.md` are earlier runs'.

| File | What it is |
|---|---|
| `translation.ve.md`, `units.json` | the main document and ledger (1,132 units, every byte of the 184,893-byte source in exactly one). Same as the previous run's except two predicate act wordings (`reword.py`, no apostrophe) and, in the ledger, a note and a `checked_content` pointer on the eight READINGS units. `prev/` holds the previous run's |
| `readings/nd-force.ve.md`, `nd-op.ve.md`, `nd-s01p1.ve.md`, `nd-all.ve.md` | the eight reading sets with Lean-checked content for every candidate, on the main chain (`norm-defaults@0`, completion unspecified); `nd-all` has all eight and is over the 64-choice budget. Each has `nd-<g>-result.json` (what `nd.py` saw), `nd-<g>-check.json`, `coverage-nd-<g>.json`, `rendered-nd-<g>.md`. Measurement documents, not part of the translation |
| `readings/all-strict.ve.md`, `all-default.ve.md` | the strict and the soft-chain companions (reworded); `rendered-all-default.md` is absent: that file does not render at this tag |
| `readings/s1.ve.md`, `check-s1-now.json` | the old soft-chain demonstration companion (`deny` completion); `CheckerUnavailable` at this tag. Its results at `ve-green-rd-6a` are in `readings/at-rd-6a/` and `probes/at-rd-6a/` |
| `metrics.json` | bytes accounted, unit counts by status (new units and aggregated to the 299 old boundaries), claimed and audit-verified bytes, open terms, reading sets, missing-feature tally, check verdicts, `checked_content_main_chain`, `reading_set_gaps` |
| `rendered.md`, `rendered-raw.md`, `check.json`, `coverage.json` | the expanded rendering, the raw `ve document render`, `check` and `coverage` of the main document |
| `probes/` | the seven carried probes (re-run; only the S1 probe's case b changed), `probes/nd/` (conclusion queries on `nd-force`) |
| `nd.py`, `reword.py`, `finish.py` | this run's scripts; the other scripts are earlier runs' kept because they import each other |

Reproduce (repository root; `lake build` in `lean/` and `python3 tools/rust_build.py` done):

    export PATH=~/.elan/bin:$PATH VE_NATIVE_PREBUILT=1
    R=usecases/claude-constitution-pilot/run-20261008T1800Z
    uv run python $R/reword.py                    # only on the previous run's files
    for p in unspecified s1 risk discourse rights senses senses_doc; do uv run python $R/probe_$p.py; done
    for g in force op s01p1 all; do uv run python $R/nd.py $g; done          # about 12 min
    for g in force op s01p1 all; do uv run python -m ve document coverage $R/readings/nd-$g.ve.md > $R/readings/coverage-nd-$g.json; uv run python -m ve document render $R/readings/nd-$g.ve.md > $R/readings/rendered-nd-$g.md; done
    uv run python -m ve document readings $R/readings/nd-force.ve.md --conclusion $R/probes/nd/conclusion-no-denial.json [--under force-u0125-s04-p2:0|1]
    uv run python $R/finish.py                    # about 30 s
