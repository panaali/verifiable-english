# Run 20261012T0600Z: Claude constitution pilot at `ve-green-devtime-1`

Read `SUMMARY.md` first, then `FEATURE-REVIEW.md` and `AUDIT-REPAIR.md`. `prev/` holds the previous run's (20261011T1800Z) outputs this run starts from; `SUMMARY-prev-20261011T1800Z.md` and `AUDIT-20261011T1800Z-received.md` are its summary and the audit received for it (`SUMMARY-prev-20261010T1800Z.md` and `AUDIT-20261010T1800Z-received.md` are the run before's). The pinned source is `../source/` (`SOURCE.md` has the SHA-256 and fetch date); it is never edited.

| File | What it is |
|---|---|
| `translation.ve.md`, `units.json` | the main document and ledger (1,132 units, every byte of the 184,893-byte source in exactly one), byte-identical to the previous run's. Four "should" reading sets with Lean-checked content (16 choices, no coupling); the four operator units are single-reading OPEN units |
| `translation-without-content.ve.md`, `readings/all-strict.ve.md` | the translation with the four sets as pending candidates (input of `nd.py`), and the strict companion (source of the strict content) |
| `readings/nd-all-result.json`, `nd-all-check.json`, `coverage-nd-all.json` | `nd.py all` at devtime-1: the translation rebuilt (byte-identical), its check, separating situations and coverage; the route is `superposed` (as at the previous tag) |
| `metrics.json` | bytes accounted, unit counts by status (new units and aggregated to the 299 old boundaries), claimed and audit-verified bytes, `changed_units` (empty), open terms, reading sets, missing-feature tally, check verdicts, `checked_content_main_chain` (with `route_change`), `companion_probe`, `lean_decided_share`, `question_probe`, `reading_set_gaps`, `language_changes_since_previous_tag` |
| `rendered.md`, `rendered-raw.md`, `check.json`, `coverage.json` | the rendering, the raw `ve document render`, `check` and `coverage` of the translation (the renderings, coverage and check are identical to the previous run's apart from key order) |
| `probes/` | the seven carried probes re-run (byte-identical), `probes/nd/` (conclusion queries; `superposed` across readings; result files byte-identical to the previous run's), `probes/companion/` (companion probe), `probes/ask/` (five `ve ask --reading` questions with `q*.question.txt`) |
| `finish_20261012T0600Z.py`, `nd.py`, `probe_*.py` | this run's finish script; the other scripts are earlier runs' kept because they import each other (`finish_0600.py`, `spec_nd.py`, `build.py`, `spec.py`); `base/` holds the carried inputs; `*.out` are the probes' console output |

Reproduce (repository root; `lake build` in `lean/` and `python3 tools/rust_build.py` done):

    export PATH=~/.elan/bin:$PATH VE_NATIVE_PREBUILT=1
    R=usecases/claude-constitution-pilot/run-20261012T0600Z
    uv run python $R/nd.py all                           # about 2 min; then:
    cmp $R/readings/nd-all.ve.md $R/translation.ve.md && rm $R/readings/nd-all.ve.md
    uv run python -m ve document coverage $R/translation.ve.md > $R/readings/coverage-nd-all.json
    # probes: s1 and rights read earlier runs' soft companions (copy run-20261008T1800Z/readings/{all-default,s1}.ve.md in, run, remove)
    for p in unspecified s1 risk discourse rights senses senses_doc; do uv run python $R/probe_$p.py; done
    uv run python $R/probe_companions.py                 # about 1.7 min
    N=$R/probes/nd   # ve document readings $R/translation.ve.md --conclusion $N/conclusion-no-denial.json [--under force-u0125-s04-p2:0|1]; the same with conclusion-no-claim-human.json
    # ve ask $R/translation.ve.md "<question>" --reading --json   (probes/ask/)
    uv run python $R/finish_20261012T0600Z.py            # about 2 min
