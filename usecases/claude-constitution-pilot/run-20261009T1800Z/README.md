# Run 20261009T1800Z: Claude constitution pilot at `ve-green-rd-3`

Read `SUMMARY.md` first, then `AUDIT-REPAIR.md` and `FEATURE-REVIEW.md`. `*-prev-*.md` are earlier runs'; `AUDIT-20261009T0600Z-received.md` is the audit this run repairs.

| File | What it is |
|---|---|
| `translation.ve.md`, `units.json` | the main document and ledger (1,132 units, every byte of the 184,893-byte source in exactly one). Same statuses as the previous run except u0166.s04.p4 (OPEN -> UNFORMALISED); eight reading sets with Lean-checked content (32 choices, one coupling) |
| `translation-without-content.ve.md` | the same document with the eight sets as pending candidates (output of `repair_20261009T1800Z.py`); input of `nd.py` |
| `prev/` | the previous run's translation, ledger and metrics (the start of this run); `base/` holds the carried inputs of the repair and of the probes |
| `readings/nd-force.ve.md`, `nd-op.ve.md` | slices of the translation (the four "should" sets: 16 choices; the four operator sets: 2 choices) used for conclusion queries; each has `nd-<g>-result.json`, `nd-<g>-check.json`, `coverage-nd-<g>.json`. `nd-all-result.json`, `nd-all-check.json` are the results for the whole translation (`nd.py all`; the document is `translation.ve.md`) |
| `readings/all-strict.ve.md` | carried strict companion (source of the strict content of the four "should" sets), repaired like the translation |
| `metrics.json` | bytes accounted, unit counts by status (new units and aggregated to the 299 old boundaries), claimed and audit-verified bytes, `changed_units`, open terms, reading sets, missing-feature tally, check verdicts, `checked_content_main_chain`, `reading_set_gaps`, `language_changes_since_previous_tag` |
| `rendered.md`, `rendered-raw.md`, `check.json`, `coverage.json` | the rendering, the raw `ve document render`, `check` and `coverage` of the translation |
| `check-baseline.json` | `ve document check` of the unchanged 20261009T0600Z translation at rd-3 (same verdicts as at lf-17, 83 s) |
| `probes/` | the seven carried probes re-run, `probes/nd/` (conclusion queries: the denial query and the "claim to be human" query under each scope) |
| `repair_20261009T1800Z.py`, `nd.py`, `finish_20261009T1800Z.py`, `probe_rights.py` | this run's scripts; the other scripts are earlier runs' kept because they import each other |

Reproduce (repository root; `lake build` in `lean/` and `python3 tools/rust_build.py` done):

    export PATH=~/.elan/bin:$PATH VE_NATIVE_PREBUILT=1
    R=usecases/claude-constitution-pilot/run-20261009T1800Z
    uv run python $R/repair_20261009T1800Z.py            # base/ + prev/ -> translation-without-content.ve.md, units.json, readings/all-strict.ve.md
    for g in force op all; do uv run python $R/nd.py $g; done      # about 5 min; readings/nd-all.ve.md becomes translation.ve.md
    cp $R/readings/nd-all.ve.md $R/translation.ve.md && rm $R/readings/nd-all.ve.md
    for g in force op; do uv run python -m ve document coverage $R/readings/nd-$g.ve.md > $R/readings/coverage-nd-$g.json; done
    uv run python -m ve document coverage $R/translation.ve.md > $R/readings/coverage-nd-all.json
    # probes: s1, rights and discourse read earlier runs' soft companions (copy run-20261008T1800Z/readings/{all-default,s1}.ve.md and base/translation.ve.md in, run, remove)
    for p in unspecified s1 risk discourse rights senses senses_doc; do uv run python $R/probe_$p.py; done
    N=$R/probes/nd   # ve document readings <slice> --conclusion $N/conclusion-no-denial.json [--under force-u0125-s04-p2:0|1]; nd-op with conclusion-no-claim-human.json [--under scope-modal-u0123-s03:0|1]
    uv run python $R/finish_20261009T1800Z.py            # about 3 min
