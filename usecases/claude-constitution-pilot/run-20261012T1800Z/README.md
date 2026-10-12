# Run 20261012T1800Z: Claude constitution pilot at `ve-green-ts-B1`

Read `SUMMARY.md` first, then `AUDIT-REPAIR.md` and `FEATURE-REVIEW.md`. `prev/` holds the previous run's (20261012T0600Z) ledger, metrics, check, coverage and probe results, which this run starts from and compares with (they are that run's record, not this run's; its translation is `base/translation-without-content.ve.md` plus the sets' content). `AUDIT-20261012T0600Z-received.md` is the audit this run repairs (`AUDIT-20261011T1800Z-received.md` and `AUDIT-20261010T1800Z-received.md` are the two before). The pinned source is `../source/` (`SOURCE.md` has the SHA-256 and fetch date); it is never edited.

| File | What it is |
|---|---|
| `translation.ve.md`, `units.json` | the main document and ledger (1,132 units, every byte of the 184,893-byte source in exactly one). Three "should" reading sets with Lean-checked content (8 choices, no coupling); u0125.s04.p2 is a CHECKED one-reading unit; the seven hard constraints carry the knowledge-or-likelihood open term |
| `translation-without-content.ve.md`, `readings/all-strict.ve.md` | the translation with the three sets as pending candidates (input of `nd.py`), and the strict companion (source of the strict content) |
| `readings/nd-all-result.json`, `nd-all-check.json`, `coverage-nd-all.json` | `nd.py all`: the translation rebuilt (it is `translation.ve.md`), its check, separating situations and coverage |
| `metrics.json` | bytes accounted, unit counts by status (new units and aggregated to the 299 old boundaries), claimed and audit-verified bytes, `changed_units`, open terms, reading sets, missing-feature tally, check verdicts, conclusion probes, `companion_probe`, `lean_decided_share`, `question_probe`, `reading_set_gaps`, `language_changes_since_previous_tag` |
| `rendered.md`, `rendered-raw.md`, `check.json`, `coverage.json` | the rendering (`rendered.md` adds the source words and VE's verdicts under each hard constraint), the raw `ve document render`, `check` and `coverage` |
| `probes/` | the six carried probes (byte-identical to `prev/probes/`), `probes/unspecified-probe.json` (re-run: four points per hard constraint), `probes/nd/` (conclusion queries, `superposed`), `probes/companion/` (companion probe), `probes/ask/` (five `ve ask --reading` questions) |
| `repair_20261012T1800Z.py`, `finish_20261012T1800Z.py`, `nd.py`, `probe_*.py` | this run's scripts; the other scripts are earlier runs' kept because they import each other (`finish_0600.py`, `finish_20261012T0600Z.py`, `spec_nd.py`, `build.py`, `spec.py`); `base/` holds the inputs (the previous run's documents) |

Reproduce (repository root; `lake build` in `lean/` and `python3 tools/rust_build.py` done):

    export PATH=~/.elan/bin:$PATH VE_NATIVE_PREBUILT=1
    R=usecases/claude-constitution-pilot/run-20261012T1800Z
    uv run python $R/repair_20261012T1800Z.py            # base/ -> translation-without-content.ve.md, readings/all-strict.ve.md
    uv run python $R/nd.py all                           # about 1 min
    mv $R/readings/nd-all.ve.md $R/translation.ve.md
    uv run python -m ve document coverage $R/translation.ve.md > $R/readings/coverage-nd-all.json
    # probes: s1 and rights read earlier runs' soft companions (copy run-20261008T1800Z/readings/{all-default,s1}.ve.md in, run, remove);
    # discourse reads base/translation.ve.md, the form it has always started from (the base of run 20261005T0600Z; it is not this run's translation)
    for p in unspecified s1 risk discourse rights senses senses_doc; do uv run python $R/probe_$p.py; done
    uv run python $R/probe_companions.py                 # about 1.5 min
    N=$R/probes/nd   # ve document readings $R/translation.ve.md --conclusion $N/conclusion-no-denial.json  (and conclusion-no-claim-human.json)
    # companion queries: ve document readings $R/probes/companion/translation-companions-without_source_word.ve.md --conclusion ... --sentence u0125.s04.p2 | u0123.s03
    # ve ask $R/translation.ve.md "<question>" --reading --json   (probes/ask/)
    uv run python $R/finish_20261012T1800Z.py            # about 2 min
