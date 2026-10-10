# Run 20261010T1800Z: Claude constitution pilot at `ve-green-arch-AR-6`

Read `SUMMARY.md` first, then `AUDIT-REPAIR.md` and `FEATURE-REVIEW.md`. `*-prev-*.md` are earlier runs'; `AUDIT-20261010T0600Z-received.md` is the audit this run repairs. The pinned source is `../source/` (`SOURCE.md` has the SHA-256 and fetch date); it is never edited.

| File | What it is |
|---|---|
| `translation.ve.md`, `units.json` | the main document and ledger (1,132 units, every byte of the 184,893-byte source in exactly one). Four "should" reading sets with Lean-checked content (16 choices, no coupling); the four operator units are single-reading OPEN units. This run changes two open terms' factors and eleven ledger notes (`changed_units`) |
| `translation-without-content.ve.md` | the same document with the four sets as pending candidates (output of `repair_20261010T1800Z.py`); input of `nd.py` |
| `readings/all-strict.ve.md` | carried strict companion (source of the strict content of the four sets, with the same two open-term repairs); `nd-all-result.json`, `nd-all-check.json`, `coverage-nd-all.json` are the results for the whole translation (`nd.py all`; the document is `translation.ve.md`) |
| `metrics.json` | bytes accounted, unit counts by status (new units and aggregated to the 299 old boundaries), claimed and audit-verified bytes, `changed_units`, open terms, reading sets, missing-feature tally, check verdicts, `checked_content_main_chain`, `companion_probe`, `lean_decided_share`, `question_probe`, `reading_set_gaps`, `language_changes_since_previous_tag` |
| `rendered.md`, `rendered-raw.md`, `check.json`, `coverage.json` | the rendering, the raw `ve document render`, `check` and `coverage` of the translation |
| `check-baseline.json` | `ve document check` of the unchanged 20261010T0600Z translation at arch-AR-6 (same verdicts, 55 s) |
| `probes/` | the seven carried probes re-run (byte-identical), `probes/nd/` (conclusion queries on the plain document), `probes/companion/` (the companion probe: the two documents with and without `source_word`, the queries with `--sentence`), `probes/ask/` (five `ve ask --reading` questions) |
| `repair_20261010T1800Z.py`, `nd.py`, `probe_companions.py`, `finish_20261010T1800Z.py` | this run's scripts; the other scripts are earlier runs' kept because they import each other (`finish_0600.py`, `spec_nd.py`, `build.py`, `spec.py`); `base/` holds the carried inputs of the repair and of the discourse probe |

Reproduce (repository root; `lake build` in `lean/` and `python3 tools/rust_build.py` done):

    export PATH=~/.elan/bin:$PATH VE_NATIVE_PREBUILT=1
    R=usecases/claude-constitution-pilot/run-20261010T1800Z
    uv run python $R/repair_20261010T1800Z.py            # base/ + prev/units.json -> translation-without-content.ve.md, readings/all-strict.ve.md, units.json
    uv run python $R/nd.py all                           # about 2 min; then:
    cp $R/readings/nd-all.ve.md $R/translation.ve.md && rm $R/readings/nd-all.ve.md
    uv run python -m ve document coverage $R/translation.ve.md > $R/readings/coverage-nd-all.json
    # probes: s1 and rights read earlier runs' soft companions (copy run-20261008T1800Z/readings/{all-default,s1}.ve.md in, run, remove)
    for p in unspecified s1 risk discourse rights senses senses_doc; do uv run python $R/probe_$p.py; done
    uv run python $R/probe_companions.py                 # about 1.5 min
    N=$R/probes/nd   # ve document readings $R/translation.ve.md --conclusion $N/conclusion-no-denial.json [--under force-u0125-s04-p2:0|1]; the same with conclusion-no-claim-human.json
    # ve ask $R/translation.ve.md "<question>" --reading --json   (probes/ask/)
    uv run python $R/finish_20261010T1800Z.py            # about 2 min
