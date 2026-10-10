# Run 20261010T0600Z: Claude constitution pilot at `ve-green-lf-16c`

Read `SUMMARY.md` first, then `AUDIT-REPAIR.md` and `FEATURE-REVIEW.md`. `*-prev-*.md` are earlier runs'; `AUDIT-20261009T1800Z-received.md` is the audit this run repairs.

| File | What it is |
|---|---|
| `translation.ve.md`, `units.json` | the main document and ledger (1,132 units, every byte of the 184,893-byte source in exactly one). Four operator units READINGS -> OPEN; four "should" reading sets with Lean-checked content (16 choices, no coupling) |
| `translation-without-content.ve.md` | the same document with the four sets as pending candidates (output of `repair_20261010T0600Z.py`); input of `nd.py` |
| `prev/` | the previous run's translation, ledger, metrics, rendering, check, probes and docs (the start of this run); `base/` holds the carried inputs of the repair and of the discourse probe |
| `readings/all-strict.ve.md` | carried strict companion (source of the strict content of the four "should" sets); `nd-all-result.json`, `nd-all-check.json`, `coverage-nd-all.json` are the results for the whole translation (`nd.py all`; the document is `translation.ve.md`) |
| `metrics.json` | bytes accounted, unit counts by status (new units and aggregated to the 299 old boundaries), claimed and audit-verified bytes, `changed_units`, open terms, reading sets, missing-feature tally, check verdicts, `checked_content_main_chain`, `reading_set_gaps`, `language_changes_since_previous_tag` |
| `rendered.md`, `rendered-raw.md`, `check.json`, `coverage.json` | the rendering, the raw `ve document render`, `check` and `coverage` of the translation |
| `check-baseline.json` | `ve document check` of the unchanged 20261009T1800Z translation at lf-16c (same verdicts, 148 s) |
| `probes/` | the seven carried probes re-run, `probes/nd/` (conclusion queries: the denial query under each reading, and the "claim to be human" query) |
| `repair_20261010T0600Z.py`, `nd.py`, `finish_20261010T0600Z.py` | this run's scripts; the other scripts are earlier runs' kept because they import each other (`finish_0600.py`, `spec_nd.py`, `build.py`, `spec.py`) |

Reproduce (repository root; `lake build` in `lean/` and `python3 tools/rust_build.py` done):

    export PATH=~/.elan/bin:$PATH VE_NATIVE_PREBUILT=1
    R=usecases/claude-constitution-pilot/run-20261010T0600Z
    uv run python $R/repair_20261010T0600Z.py            # base/ + prev/ -> translation-without-content.ve.md, units.json
    uv run python $R/nd.py all                           # about 2 min; then:
    cp $R/readings/nd-all.ve.md $R/translation.ve.md && rm $R/readings/nd-all.ve.md
    uv run python -m ve document coverage $R/translation.ve.md > $R/readings/coverage-nd-all.json
    # probes: s1 and rights read earlier runs' soft companions (copy run-20261008T1800Z/readings/{all-default,s1}.ve.md in, run, remove)
    for p in unspecified s1 risk discourse rights senses senses_doc; do uv run python $R/probe_$p.py; done
    N=$R/probes/nd   # ve document readings $R/translation.ve.md --conclusion $N/conclusion-no-denial.json [--under force-u0125-s04-p2:0|1]; the same with conclusion-no-claim-human.json
    uv run python $R/finish_20261010T0600Z.py            # about 3 min
