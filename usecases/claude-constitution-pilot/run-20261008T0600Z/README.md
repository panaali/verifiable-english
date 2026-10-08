# Run 20261008T0600Z: Claude constitution pilot at `ve-green-rd-6a`

Read `SUMMARY.md` first, then `AUDIT-REPAIR.md` (the readings-from-the-words repair) and `FEATURE-REVIEW.md`. `*-prev-*.md` are earlier runs'.

| File | What it is |
|---|---|
| `translation.ve.md`, `units.json` | the main document and ledger (1,132 units, every byte of the 184,893-byte source in exactly one); the previous run's with the repair of `repair.py` (u0052.s01; four open terms removed; justification text on four force sets) |
| `readings/` | the strict companion and the demonstration companions `s1.ve.md`, `all-default.ve.md` (not part of the translation; they complete duties with `deny`); `check-*.json`, `rendered-*.md`, `coverage-s1.json`, `separating-situations.json` re-run at this tag |
| `metrics.json` | bytes accounted, unit counts by status (new units and aggregated to the 299 old boundaries), claimed and audit-verified bytes, open terms, reading sets, missing-feature tally, check verdicts, `s2a`, `senses_document_probe`, `readings_from_the_words_rule` |
| `rendered.md`, `rendered-raw.md`, `check.json`, `coverage.json` | the pilot's expanded rendering, the raw `ve document render`, `check` and `coverage` of the main document |
| `probes/` | unspecified (ported), s1, risk, discourse, rights, senses probes, `senses-document-probe.json` and `senses-documents/` (new), `s2/` (conclusions across and under readings), `lean-decided-share-main.txt`, `out-*-now.txt` |
| `repair.py`, `finish.py`, `probe_*.py`, `build.py`, `spec*.py`, `s1*.py`, `finish_0600.py`, `finish_2026100*.py` | scripts; `repair.py` and `finish.py` are this run's, the others are earlier runs' kept because they import each other |
| `prev/` | the starting point (previous translation, ledger, metrics) |

Reproduce (repository root; `lake build` in `lean/` and `python3 tools/rust_build.py` done; the source is `usecases/claude-constitution-pilot/source/`):

    export PATH=~/.elan/bin:$PATH VE_NATIVE_PREBUILT=1
    R=usecases/claude-constitution-pilot/run-20261008T0600Z
    python3 -I $R/repair.py                       # only on the previous run's files (it asserts that start)
    for p in unspecified s1 risk discourse rights senses senses_doc; do uv run python $R/probe_$p.py; done
    uv run python -m ve document check $R/readings/s1.ve.md > $R/readings/check-s1.json    # about 2.5 min
    uv run python -m ve document coverage $R/readings/s1.ve.md > $R/readings/coverage-s1.json
    # probes/s2: ve document readings $R/readings/s1.ve.md --conclusion $R/probes/s2/conclusion-no-denial.json [--under force-u0125-s04-p2:0|1]
    uv run python tools/lean_decided_share.py $R/translation.ve.md > $R/probes/lean-decided-share-main.txt
    uv run python $R/finish.py                    # about 1 min
