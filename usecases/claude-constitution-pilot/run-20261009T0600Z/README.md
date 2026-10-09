# Run 20261009T0600Z: Claude constitution pilot at `ve-green-lf-17`

Read `SUMMARY.md` first, then `AUDIT-REPAIR.md` and `FEATURE-REVIEW.md`. `*-prev-*.md` are earlier runs'; `AUDIT-20261008T1800Z-received.md` is the audit this run repairs.

| File | What it is |
|---|---|
| `translation.ve.md`, `units.json` | the main document and ledger (1,132 units, every byte of the 184,893-byte source in exactly one). Same statuses as the previous run; the four operator reading sets are repaired (AUDIT-REPAIR.md) and all eight reading sets carry Lean-checked content in the document (32 choices, one coupling) |
| `translation-without-content.ve.md` | the same document with the eight sets as pending candidates (output of `repair_20261009.py`); input of `nd.py` and of the S1 probe |
| `prev/` | the previous run's translation, ledger and metrics (the start of this run) |
| `readings/nd-force.ve.md`, `nd-op.ve.md` | slices of the translation (the four "should" sets: 16 choices; the four operator sets: 2 choices) used for conclusion queries; each has `nd-<g>-result.json`, `nd-<g>-check.json`, `coverage-nd-<g>.json`, `rendered-nd-<g>.md`. `nd-all-result.json`, `nd-all-check.json`, `coverage-nd-all.json` are the results for the whole translation (`nd.py all`; the document is `translation.ve.md`) |
| `readings/all-strict.ve.md` | carried strict companion (the source of the strict content of the four "should" sets); not part of the translation. `all-default.ve.md` and `s1.ve.md` are no longer carried: they do not check or render at this tag and held the removed candidates and the `deny` completion (notes in `units.json` that name them are history) |
| `metrics.json` | bytes accounted, unit counts by status (new units and aggregated to the 299 old boundaries), claimed and audit-verified bytes, open terms, reading sets, missing-feature tally, check verdicts, `checked_content_main_chain`, `reading_set_gaps`, `language_changes_since_previous_tag` |
| `rendered.md`, `rendered-raw.md`, `check.json`, `coverage.json` | the rendering (the natural view prints each candidate's content with its label), the raw `ve document render`, `check` and `coverage` of the translation |
| `probes/` | the seven carried probes re-run, `probes/nd/` (conclusion queries: the earlier denial query and the new "claim to be human" query under each scope) |
| `repair_20261009.py`, `nd.py`, `finish_20261009.py` | this run's scripts; the other scripts are earlier runs' kept because they import each other |

Reproduce (repository root; `lake build` in `lean/` and `python3 tools/rust_build.py` done):

    export PATH=~/.elan/bin:$PATH VE_NATIVE_PREBUILT=1
    R=usecases/claude-constitution-pilot/run-20261009T0600Z
    uv run python $R/repair_20261009.py            # prev/ -> translation-without-content.ve.md, units.json
    for g in force op all; do uv run python $R/nd.py $g; done      # about 9 min; readings/nd-all.ve.md becomes translation.ve.md
    cp $R/readings/nd-all.ve.md $R/translation.ve.md && rm $R/readings/nd-all.ve.md
    for g in force op all; do uv run python -m ve document coverage $R/readings/nd-$g.ve.md > $R/readings/coverage-nd-$g.json; done   # nd-all: use translation.ve.md
    for p in unspecified s1 risk discourse rights senses senses_doc; do uv run python $R/probe_$p.py; done
    uv run python -m ve document readings $R/readings/nd-force.ve.md --conclusion $R/probes/nd/conclusion-no-denial.json [--under force-u0125-s04-p2:0|1]
    uv run python -m ve document readings $R/readings/nd-op.ve.md --conclusion $R/probes/nd/conclusion-no-claim-human.json [--under scope-modal-u0123-s03:0|1]
    uv run python $R/finish_20261009.py            # about 13 min
